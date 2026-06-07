"""经验回放缓冲区（定长环形，numpy 预分配）。

存储六元组 (obs, action, reward, next_obs, done, next_legal_mask)。容量满后滚动覆盖最旧样本
（TC-020）。采样数量超过当前样本数时报错，由调用方在 len>=batch 后再采样
（TC-021 的保护在智能体层）。
"""

from __future__ import annotations

import numpy as np


class ReplayBuffer:
    def __init__(self, capacity: int, obs_shape: tuple[int, ...]) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be > 0")
        self.capacity = int(capacity)
        self.obs_shape = tuple(obs_shape)

        self._obs = np.zeros((self.capacity, *self.obs_shape), dtype=np.float32)
        self._next_obs = np.zeros((self.capacity, *self.obs_shape), dtype=np.float32)
        self._actions = np.zeros((self.capacity,), dtype=np.int64)
        self._rewards = np.zeros((self.capacity,), dtype=np.float32)
        self._dones = np.zeros((self.capacity,), dtype=np.float32)
        self._next_legal_masks = np.ones((self.capacity, 4), dtype=np.bool_)

        self._pos = 0
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def push(
        self,
        obs: np.ndarray,
        action: int,
        reward: float,
        next_obs: np.ndarray,
        done: bool,
        next_legal_mask: np.ndarray | None = None,
    ) -> None:
        i = self._pos
        self._obs[i] = obs
        self._next_obs[i] = next_obs
        self._actions[i] = int(action)
        self._rewards[i] = float(reward)
        self._dones[i] = 1.0 if done else 0.0
        if next_legal_mask is None:
            self._next_legal_masks[i] = True
        else:
            self._next_legal_masks[i] = np.asarray(next_legal_mask, dtype=np.bool_)
        self._pos = (self._pos + 1) % self.capacity
        self._size = min(self._size + 1, self.capacity)

    def sample(
        self, batch_size: int, rng: np.random.Generator | None = None
    ) -> tuple[
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
    ]:
        if batch_size > self._size:
            raise ValueError(
                f"cannot sample {batch_size} from buffer of size {self._size}"
            )
        rng = rng or np.random.default_rng()
        idx = rng.integers(0, self._size, size=batch_size)
        return (
            self._obs[idx],
            self._actions[idx],
            self._rewards[idx],
            self._next_obs[idx],
            self._dones[idx],
            self._next_legal_masks[idx],
        )
