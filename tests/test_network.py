"""T-10 DQN 网络测试。关联 US-05。"""

import torch

from src.agents.network import QNetwork


def test_forward_output_shape_flat():
    net = QNetwork(input_dim=16, hidden_sizes=(64, 64), num_actions=4)
    x = torch.zeros(8, 16)
    out = net(x)
    assert out.shape == (8, 4)


def test_forward_accepts_board_shape():
    net = QNetwork(input_dim=16, hidden_sizes=(32,), num_actions=4)
    x = torch.zeros(5, 4, 4)
    out = net(x)
    assert out.shape == (5, 4)


def test_param_count_nonzero():
    net = QNetwork()
    n = sum(p.numel() for p in net.parameters())
    assert n > 0


def test_custom_hidden_sizes():
    net = QNetwork(hidden_sizes=(128, 128, 64))
    x = torch.randn(3, 16)
    assert net(x).shape == (3, 4)
