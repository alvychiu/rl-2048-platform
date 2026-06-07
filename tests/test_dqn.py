"""T-11 DQN 智能体测试。关联 US-05 / TC-022, TC-023。"""

import numpy as np

from src.agents.dqn import DQNAgent
from src.train.replay_buffer import ReplayBuffer


def make_agent(**kw):
    defaults = dict(
        obs_shape=(4, 4),
        hidden_sizes=(32, 32),
        eps_decay_steps=100,
        target_update_interval=5,
        device="cpu",
    )
    defaults.update(kw)
    return DQNAgent(**defaults)


def test_act_returns_valid_action():
    agent = make_agent()
    rng = np.random.default_rng(0)
    obs = np.zeros((4, 4), dtype=np.float32)
    a = agent.act(obs, step=0, rng=rng)
    assert a in {0, 1, 2, 3}


def test_rv1_act_respects_legal_mask_exploration():
    """RV-1: ε=1 探索时也只在合法动作中选择。"""
    agent = make_agent(eps_start=1.0, eps_end=1.0, eps_decay_steps=1)
    rng = np.random.default_rng(0)
    obs = np.zeros((4, 4), dtype=np.float32)
    mask = np.array([False, False, True, False])  # 仅 LEFT 合法
    for _ in range(20):
        assert agent.act(obs, step=0, rng=rng, legal_mask=mask) == 2


def test_rv1_act_greedy_respects_legal_mask():
    """RV-1: 贪心时非法动作被屏蔽，只在合法动作取 argmax。"""
    agent = make_agent()
    obs = np.zeros((4, 4), dtype=np.float32)
    mask = np.array([False, True, False, False])  # 仅 DOWN 合法
    for _ in range(10):
        assert agent.act_greedy(obs, legal_mask=mask) == 1


def test_rv1_no_legal_falls_back():
    """无合法动作（终局）时不崩溃。"""
    agent = make_agent()
    obs = np.zeros((4, 4), dtype=np.float32)
    mask = np.array([False, False, False, False])
    a = agent.act_greedy(obs, legal_mask=mask)
    assert a in {0, 1, 2, 3}


def test_epsilon_decays():
    agent = make_agent(eps_start=1.0, eps_end=0.1, eps_decay_steps=100)
    assert agent.epsilon(0) == 1.0
    assert agent.epsilon(100) == 0.1
    assert 0.1 < agent.epsilon(50) < 1.0


def test_learn_runs_and_returns_loss():
    agent = make_agent()
    buf = ReplayBuffer(capacity=200, obs_shape=(4, 4))
    rng = np.random.default_rng(1)
    for i in range(64):
        buf.push(
            rng.random((4, 4)).astype(np.float32),
            i % 4,
            float(rng.random()),
            rng.random((4, 4)).astype(np.float32),
            bool(i % 7 == 0),
        )
    loss = agent.learn(buf.sample(32, rng=rng))
    assert isinstance(loss, float)
    assert loss >= 0.0


def test_target_sync_changes_params():
    agent = make_agent(target_update_interval=1)
    buf = ReplayBuffer(capacity=200, obs_shape=(4, 4))
    rng = np.random.default_rng(2)
    for i in range(40):
        buf.push(
            rng.random((4, 4)).astype(np.float32),
            i % 4,
            1.0,
            rng.random((4, 4)).astype(np.float32),
            False,
        )
    # 学习一步后 target 应与 q_net 同步
    agent.learn(buf.sample(16, rng=rng))
    for p, t in zip(agent.q_net.parameters(), agent.target_net.parameters()):
        assert np.allclose(p.detach().cpu().numpy(), t.detach().cpu().numpy())


def test_learn_masks_illegal_next_actions():
    """TD 目标仅在 next 合法动作上取 max Q。"""
    agent = make_agent()
    buf = ReplayBuffer(capacity=200, obs_shape=(4, 4))
    rng = np.random.default_rng(3)
    obs = np.zeros((4, 4), dtype=np.float32)
    mask = np.array([False, True, False, False])
    for _ in range(32):
        buf.push(obs, 1, 1.0, obs, False, next_legal_mask=mask)
    loss = agent.learn(buf.sample(16, rng=rng))
    assert isinstance(loss, float)
    assert loss >= 0.0


def test_double_dqn_cnn_learn_runs():
    agent = make_agent(
        network_type="cnn",
        use_dueling=True,
        use_double_dqn=True,
        cnn_channels=(16, 32),
        cnn_fc_size=64,
    )
    buf = ReplayBuffer(capacity=200, obs_shape=(4, 4))
    rng = np.random.default_rng(4)
    for i in range(64):
        buf.push(
            rng.random((4, 4)).astype(np.float32),
            i % 4,
            float(rng.random()),
            rng.random((4, 4)).astype(np.float32),
            bool(i % 7 == 0),
        )
    loss = agent.learn(buf.sample(32, rng=rng))
    assert isinstance(loss, float)
    assert loss >= 0.0


def test_state_dict_roundtrip():
    a1 = make_agent()
    a2 = make_agent()
    a2.load_state_dict(a1.state_dict())
    for p, q in zip(a1.q_net.parameters(), a2.q_net.parameters()):
        assert np.allclose(p.detach().cpu().numpy(), q.detach().cpu().numpy())
