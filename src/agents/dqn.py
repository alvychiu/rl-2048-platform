"""DQN 智能体：ε-greedy 选动作 + TD 目标 + 目标网络周期同步。

设计：
- 主网络 q_net 与目标网络 target_net；target 周期性硬拷贝主网络参数。
- act：以线性衰减的 ε 做探索，否则取 argmax Q。
- learn：从回放采样，计算 TD loss = MSE(Q(s,a), r + γ·maxQ_target(s')·(1-done))。
- device 由 utils.resolve_device 解析（Apple M2 用 cpu/mps，无 CUDA）。
"""

from __future__ import annotations

import copy

import numpy as np
import torch
import torch.nn as nn

from src.agents.network import QNetwork
from src.utils.seeding import resolve_device


class DQNAgent:
    def __init__(
        self,
        obs_shape: tuple[int, ...] = (4, 4),
        num_actions: int = 4,
        hidden_sizes=(256, 256),
        lr: float = 1e-3,
        gamma: float = 0.99,
        eps_start: float = 1.0,
        eps_end: float = 0.05,
        eps_decay_steps: int = 10000,
        target_update_interval: int = 1000,
        device: str = "auto",
    ) -> None:
        self.device = resolve_device(device)
        self.num_actions = num_actions
        self.gamma = float(gamma)
        self.eps_start = float(eps_start)
        self.eps_end = float(eps_end)
        self.eps_decay_steps = int(eps_decay_steps)
        self.target_update_interval = int(target_update_interval)

        input_dim = int(np.prod(obs_shape))
        self.q_net = QNetwork(input_dim, hidden_sizes, num_actions).to(self.device)
        self.target_net = copy.deepcopy(self.q_net).to(self.device)
        self.target_net.eval()

        self.optimizer = torch.optim.Adam(self.q_net.parameters(), lr=lr)
        self.loss_fn = nn.MSELoss()

        self._learn_steps = 0

    def epsilon(self, step: int) -> float:
        """线性衰减的探索率。"""
        if step >= self.eps_decay_steps:
            return self.eps_end
        frac = step / max(1, self.eps_decay_steps)
        return self.eps_start + frac * (self.eps_end - self.eps_start)

    def _legal_indices(self, legal_mask) -> list[int]:
        if legal_mask is None:
            return list(range(self.num_actions))
        idx = [i for i, ok in enumerate(np.asarray(legal_mask).tolist()) if ok]
        # 无合法动作（终局）时退回全集，避免空选择崩溃。
        return idx if idx else list(range(self.num_actions))

    @torch.no_grad()
    def act(
        self,
        obs: np.ndarray,
        step: int,
        rng: np.random.Generator,
        legal_mask=None,
    ) -> int:
        """ε-greedy 选动作；提供 legal_mask 时仅在合法动作中选择（RV-1）。"""
        legal = self._legal_indices(legal_mask)
        eps = self.epsilon(step)
        if rng.random() < eps:
            return int(legal[rng.integers(len(legal))])
        return self._greedy_among(obs, legal)

    @torch.no_grad()
    def act_greedy(self, obs: np.ndarray, legal_mask=None) -> int:
        """纯贪心（评估用）；提供 legal_mask 时仅在合法动作中取 argmax（RV-1）。"""
        return self._greedy_among(obs, self._legal_indices(legal_mask))

    @torch.no_grad()
    def _greedy_among(self, obs: np.ndarray, legal: list[int]) -> int:
        obs_t = torch.as_tensor(obs, dtype=torch.float32, device=self.device).unsqueeze(0)
        q = self.q_net(obs_t).squeeze(0)
        # 把非法动作的 Q 置为 -inf，再取 argmax
        mask = torch.full_like(q, float("-inf"))
        legal_t = torch.tensor(legal, dtype=torch.int64, device=self.device)
        mask[legal_t] = q[legal_t]
        return int(torch.argmax(mask).item())

    def learn(self, batch) -> float:
        """一次梯度更新，返回 loss 标量。"""
        obs, actions, rewards, next_obs, dones, next_legal_masks = batch
        obs_t = torch.as_tensor(obs, dtype=torch.float32, device=self.device)
        next_t = torch.as_tensor(next_obs, dtype=torch.float32, device=self.device)
        act_t = torch.as_tensor(actions, dtype=torch.int64, device=self.device)
        rew_t = torch.as_tensor(rewards, dtype=torch.float32, device=self.device)
        done_t = torch.as_tensor(dones, dtype=torch.float32, device=self.device)

        q_values = self.q_net(obs_t).gather(1, act_t.unsqueeze(1)).squeeze(1)
        with torch.no_grad():
            next_q_all = self.target_net(next_t)
            legal_t = torch.as_tensor(
                next_legal_masks, dtype=torch.bool, device=self.device
            )
            next_q_all = next_q_all.masked_fill(~legal_t, float("-inf"))
            next_q = next_q_all.max(dim=1).values
            next_q = torch.where(
                torch.isinf(next_q), torch.zeros_like(next_q), next_q
            )
            target = rew_t + self.gamma * next_q * (1.0 - done_t)

        loss = self.loss_fn(q_values, target)
        self.optimizer.zero_grad()
        loss.backward()
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
