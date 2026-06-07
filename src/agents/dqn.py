"""DQN 智能体：ε-greedy + TD 目标 + 目标网络周期同步。

v6 扩展：可选 Double DQN + Dueling CNN。
"""

from __future__ import annotations

import copy
from typing import Any

import numpy as np
import torch
import torch.nn as nn

from src.agents.network import build_q_network
from src.utils.seeding import resolve_device


def agent_kwargs_from_meta(meta: dict[str, Any]) -> dict[str, Any]:
    """从检查点 meta 还原 Agent 构造参数。"""
    return {
        "obs_shape": (4, 4),
        "hidden_sizes": tuple(meta.get("hidden_sizes", (256, 256))),
        "network_type": meta.get("network_type", "mlp"),
        "cnn_channels": tuple(meta.get("cnn_channels", (32, 64))),
        "cnn_fc_size": int(meta.get("cnn_fc_size", 128)),
        "use_dueling": bool(meta.get("use_dueling", False)),
        "use_double_dqn": bool(meta.get("use_double_dqn", False)),
    }


def checkpoint_meta(agent: "DQNAgent", extra: dict[str, Any] | None = None) -> dict[str, Any]:
    """生成写入检查点的网络 meta。"""
    meta = {
        "hidden_sizes": list(agent.hidden_sizes),
        "network_type": agent.network_type,
        "cnn_channels": list(agent.cnn_channels),
        "cnn_fc_size": agent.cnn_fc_size,
        "use_dueling": agent.use_dueling,
        "use_double_dqn": agent.use_double_dqn,
    }
    if extra:
        meta.update(extra)
    return meta


class DQNAgent:
    def __init__(
        self,
        obs_shape: tuple[int, ...] = (4, 4),
        num_actions: int = 4,
        hidden_sizes=(256, 256),
        network_type: str = "mlp",
        cnn_channels=(32, 64),
        cnn_fc_size: int = 128,
        use_dueling: bool = False,
        use_double_dqn: bool = False,
        lr: float = 1e-3,
        gamma: float = 0.99,
        eps_start: float = 1.0,
        eps_end: float = 0.05,
        eps_decay_steps: int = 10000,
        target_update_interval: int = 1000,
        grad_clip_max_norm: float = 0.0,
        device: str = "auto",
    ) -> None:
        self.device = resolve_device(device)
        self.num_actions = num_actions
        self.gamma = float(gamma)
        self.eps_start = float(eps_start)
        self.eps_end = float(eps_end)
        self.eps_decay_steps = int(eps_decay_steps)
        self.target_update_interval = int(target_update_interval)
        self.grad_clip_max_norm = float(grad_clip_max_norm)
        self.hidden_sizes = tuple(hidden_sizes)
        self.network_type = str(network_type)
        self.cnn_channels = tuple(cnn_channels)
        self.cnn_fc_size = int(cnn_fc_size)
        self.use_dueling = bool(use_dueling)
        self.use_double_dqn = bool(use_double_dqn)

        self.q_net = build_q_network(
            network_type=self.network_type,
            obs_shape=obs_shape,
            hidden_sizes=self.hidden_sizes,
            conv_channels=self.cnn_channels,
            cnn_fc_size=self.cnn_fc_size,
            num_actions=num_actions,
            use_dueling=self.use_dueling,
        ).to(self.device)
        self.target_net = copy.deepcopy(self.q_net).to(self.device)
        self.target_net.eval()

        self.optimizer = torch.optim.Adam(self.q_net.parameters(), lr=lr)
        self.loss_fn = nn.MSELoss()

        self._learn_steps = 0

    @classmethod
    def from_checkpoint_meta(
        cls, meta: dict[str, Any], device: str = "cpu", **overrides
    ) -> "DQNAgent":
        kw = agent_kwargs_from_meta(meta)
        kw.update(overrides)
        return cls(device=device, **kw)

    def epsilon(self, step: int) -> float:
        if step >= self.eps_decay_steps:
            return self.eps_end
        frac = step / max(1, self.eps_decay_steps)
        return self.eps_start + frac * (self.eps_end - self.eps_start)

    def _legal_indices(self, legal_mask) -> list[int]:
        if legal_mask is None:
            return list(range(self.num_actions))
        idx = [i for i, ok in enumerate(np.asarray(legal_mask).tolist()) if ok]
        return idx if idx else list(range(self.num_actions))

    @torch.no_grad()
    def act(
        self,
        obs: np.ndarray,
        step: int,
        rng: np.random.Generator,
        legal_mask=None,
    ) -> int:
        legal = self._legal_indices(legal_mask)
        eps = self.epsilon(step)
        if rng.random() < eps:
            return int(legal[rng.integers(len(legal))])
        return self._greedy_among(obs, legal)

    @torch.no_grad()
    def act_greedy(self, obs: np.ndarray, legal_mask=None) -> int:
        return self._greedy_among(obs, self._legal_indices(legal_mask))

    @torch.no_grad()
    def _greedy_among(self, obs: np.ndarray, legal: list[int]) -> int:
        obs_t = torch.as_tensor(obs, dtype=torch.float32, device=self.device).unsqueeze(0)
        q = self.q_net(obs_t).squeeze(0)
        mask = torch.full_like(q, float("-inf"))
        legal_t = torch.tensor(legal, dtype=torch.int64, device=self.device)
        mask[legal_t] = q[legal_t]
        return int(torch.argmax(mask).item())

    def _masked_max_q(
        self, q_all: torch.Tensor, legal_t: torch.Tensor
    ) -> torch.Tensor:
        masked = q_all.masked_fill(~legal_t, float("-inf"))
        max_q = masked.max(dim=1).values
        return torch.where(torch.isinf(max_q), torch.zeros_like(max_q), max_q)

    def learn(self, batch) -> float:
        obs, actions, rewards, next_obs, dones, next_legal_masks = batch
        obs_t = torch.as_tensor(obs, dtype=torch.float32, device=self.device)
        next_t = torch.as_tensor(next_obs, dtype=torch.float32, device=self.device)
        act_t = torch.as_tensor(actions, dtype=torch.int64, device=self.device)
        rew_t = torch.as_tensor(rewards, dtype=torch.float32, device=self.device)
        done_t = torch.as_tensor(dones, dtype=torch.float32, device=self.device)

        q_values = self.q_net(obs_t).gather(1, act_t.unsqueeze(1)).squeeze(1)
        with torch.no_grad():
            legal_t = torch.as_tensor(
                next_legal_masks, dtype=torch.bool, device=self.device
            )
            if self.use_double_dqn:
                online_next = self.q_net(next_t).masked_fill(~legal_t, float("-inf"))
                best_act = online_next.argmax(dim=1, keepdim=True)
                target_next = self.target_net(next_t).gather(1, best_act).squeeze(1)
                next_q = torch.where(
                    torch.isinf(target_next), torch.zeros_like(target_next), target_next
                )
            else:
                next_q = self._masked_max_q(self.target_net(next_t), legal_t)
            target = rew_t + self.gamma * next_q * (1.0 - done_t)

        loss = self.loss_fn(q_values, target)
        self.optimizer.zero_grad()
        loss.backward()
        if self.grad_clip_max_norm > 0:
            nn.utils.clip_grad_norm_(
                self.q_net.parameters(), self.grad_clip_max_norm
            )
        self.optimizer.step()

        self._learn_steps += 1
        if self._learn_steps % self.target_update_interval == 0:
            self.sync_target()
        return float(loss.item())

    def sync_target(self) -> None:
        self.target_net.load_state_dict(self.q_net.state_dict())

    def state_dict(self) -> dict:
        return self.q_net.state_dict()

    def load_state_dict(self, sd: dict) -> None:
        self.q_net.load_state_dict(sd)
        self.sync_target()
