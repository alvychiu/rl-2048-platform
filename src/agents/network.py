"""DQN Q 网络：MLP / CNN，可选 Dueling 头。

- MLP：MVP 基线，展平 4×4 观测。
- CNN：保留棋盘空间结构，利于角落/蛇形策略学习（v6）。
- Dueling：V(s) + A(s,a) 分解，减 Q 值过估计。
"""

from __future__ import annotations

from typing import Sequence

import torch
import torch.nn as nn


class QNetwork(nn.Module):
    """标准 MLP Q 网络。"""

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
        if x.dim() > 2:
            x = x.reshape(x.shape[0], -1)
        return self.net(x)


def _to_board_batch(x: torch.Tensor) -> torch.Tensor:
    """统一为 (B, 1, 4, 4)。"""
    if x.dim() == 2:
        return x.view(x.shape[0], 1, 4, 4)
    if x.dim() == 3:
        return x.unsqueeze(1)
    return x


class CNNQNetwork(nn.Module):
    """轻量 CNN Q 网络，输入 4×4 棋盘。"""

    def __init__(
        self,
        conv_channels: Sequence[int] = (32, 64),
        fc_size: int = 128,
        num_actions: int = 4,
    ) -> None:
        super().__init__()
        c1, c2 = int(conv_channels[0]), int(conv_channels[1])
        self.features = nn.Sequential(
            nn.Conv2d(1, c1, kernel_size=2, stride=1),
            nn.ReLU(),
            nn.Conv2d(c1, c2, kernel_size=2, stride=1),
            nn.ReLU(),
        )
        flat = c2 * 2 * 2
        self.head = nn.Sequential(nn.Linear(flat, fc_size), nn.ReLU())
        self.q_out = nn.Linear(fc_size, num_actions)
        self.num_actions = num_actions

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = _to_board_batch(x)
        feat = self.features(x).view(x.shape[0], -1)
        return self.q_out(self.head(feat))


class DuelingCNNQNetwork(nn.Module):
    """Dueling CNN：共享卷积特征 + 独立 V / A 流。"""

    def __init__(
        self,
        conv_channels: Sequence[int] = (32, 64),
        fc_size: int = 128,
        num_actions: int = 4,
    ) -> None:
        super().__init__()
        c1, c2 = int(conv_channels[0]), int(conv_channels[1])
        self.features = nn.Sequential(
            nn.Conv2d(1, c1, kernel_size=2, stride=1),
            nn.ReLU(),
            nn.Conv2d(c1, c2, kernel_size=2, stride=1),
            nn.ReLU(),
        )
        flat = c2 * 2 * 2
        self.fc = nn.Sequential(nn.Linear(flat, fc_size), nn.ReLU())
        self.value_stream = nn.Linear(fc_size, 1)
        self.advantage_stream = nn.Linear(fc_size, num_actions)
        self.num_actions = num_actions

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = _to_board_batch(x)
        feat = self.features(x).view(x.shape[0], -1)
        feat = self.fc(feat)
        v = self.value_stream(feat)
        a = self.advantage_stream(feat)
        return v + a - a.mean(dim=1, keepdim=True)


def build_q_network(
    *,
    network_type: str = "mlp",
    obs_shape: tuple[int, ...] = (4, 4),
    hidden_sizes: Sequence[int] = (256, 256),
    conv_channels: Sequence[int] = (32, 64),
    cnn_fc_size: int = 128,
    num_actions: int = 4,
    use_dueling: bool = False,
) -> nn.Module:
    """按配置构造 Q 网络。"""
    if network_type == "cnn":
        if use_dueling:
            return DuelingCNNQNetwork(conv_channels, cnn_fc_size, num_actions)
        return CNNQNetwork(conv_channels, cnn_fc_size, num_actions)
    if network_type == "mlp":
        if use_dueling:
            raise ValueError("dueling MLP not implemented; use network_type=cnn")
        input_dim = int(torch.tensor(obs_shape).prod().item())
        return QNetwork(input_dim, hidden_sizes, num_actions)
    raise ValueError(f"unknown network_type: {network_type!r}")
