"""T-09 经验回放缓冲区测试。关联 US-05 / TC-020, TC-021。"""

import numpy as np
import pytest

from src.train.replay_buffer import ReplayBuffer


def _obs(v):
    return np.full((4, 4), v, dtype=np.float32)


def test_push_and_len():
    buf = ReplayBuffer(capacity=10, obs_shape=(4, 4))
    assert len(buf) == 0
    buf.push(_obs(0), 1, 1.0, _obs(1), False)
    assert len(buf) == 1


def test_tc020_capacity_rolling():
    buf = ReplayBuffer(capacity=3, obs_shape=(4, 4))
    for i in range(5):
        buf.push(_obs(i), i % 4, float(i), _obs(i + 1), False)
    assert len(buf) == 3  # 不超过容量


def test_sample_shapes():
    buf = ReplayBuffer(capacity=100, obs_shape=(4, 4))
    for i in range(50):
        buf.push(_obs(i), i % 4, float(i), _obs(i + 1), i % 2 == 0)
    obs, act, rew, nobs, done, legal = buf.sample(16, rng=np.random.default_rng(0))
    assert obs.shape == (16, 4, 4)
    assert act.shape == (16,)
    assert rew.shape == (16,)
    assert nobs.shape == (16, 4, 4)
    assert done.shape == (16,)
    assert legal.shape == (16, 4)


def test_push_stores_next_legal_mask():
    buf = ReplayBuffer(capacity=10, obs_shape=(4, 4))
    mask = np.array([True, False, True, False])
    buf.push(_obs(0), 0, 0.0, _obs(1), False, next_legal_mask=mask)
    _, _, _, _, _, legal = buf.sample(1, rng=np.random.default_rng(0))
    assert np.array_equal(legal[0], mask)


def test_tc021_sample_more_than_size_raises():
    buf = ReplayBuffer(capacity=10, obs_shape=(4, 4))
    buf.push(_obs(0), 0, 0.0, _obs(1), False)
    with pytest.raises(ValueError):
        buf.sample(5)


def test_sample_reproducible_with_rng():
    buf = ReplayBuffer(capacity=100, obs_shape=(4, 4))
    for i in range(50):
        buf.push(_obs(i), i % 4, float(i), _obs(i + 1), False)
    s1 = buf.sample(8, rng=np.random.default_rng(7))
    s2 = buf.sample(8, rng=np.random.default_rng(7))
    assert np.array_equal(s1[1], s2[1])
