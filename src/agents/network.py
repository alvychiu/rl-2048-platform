"""DQN 的 Q 网络（轻量 MLP，适配 Apple M2）。

MVP 选用 MLP 而非复杂 CNN：先验证训练管线可行性（避免过度设计）。
输入为展平的 4×4 观测（16 维），输出 4 个动作的 Q 值。
"""

from __future__ import annotations

from typing import Sequence

import torch
import torch.nn as nn


class QNetwork(nn.Module):
    def __init__(
        self,
        input_dim: int = 16,
        hidden_sizes: Sequence[int] = (256, 256),
        num_actions: int = 4,
    ) -> None:
        super().__init__()
        layers: list[nn.Module] = []
        last = input_dim
        for h in hidden_sizes:
            layers.append(nn.Linear(last, h))
            layers.append(nn.ReLU())
            last = h
        layers.append(nn.Linear(last, num_actions))
        self.net = nn.Sequential(*layers)
        self.input_dim = input_dim
        self.num_actions = num_actions

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # 接受 (B,4,4) 或 (B,16)，统一展平为 (B, input_dim)
        if x.dim() > 2:
            x = x.reshape(x.shape[0], -1)
        return self.net(x)
