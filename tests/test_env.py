"""T-06 环境接口单测。关联 US-02 / TC-007~TC-012, TC-046。"""

import numpy as np
import pytest
from gymnasium import spaces

from src.env.game_2048_env import Game2048Env


def make_env(**kw):
    return Game2048Env(**kw)


def test_tc007_reset_returns_obs_info():
    env = make_env()
    obs, info = env.reset(seed=42)
    assert obs.shape == (4, 4)
    assert obs.dtype == np.float32
    assert isinstance(info, dict)
    assert "score" in info and "max_tile" in info


def test_tc008_step_returns_five_tuple():
    env = make_env()
    env.reset(seed=42)
    out = env.step(2)  # LEFT
    assert len(out) == 5
    obs, reward, terminated, truncated, info = out
    assert obs.shape == (4, 4)
    assert isinstance(reward, float)
    assert isinstance(terminated, bool)
    assert isinstance(truncated, bool)
    assert isinstance(info, dict)


def test_action_space_is_discrete_4():
    env = make_env()
    assert isinstance(env.action_space, spaces.Discrete)
    assert env.action_space.n == 4


def test_observation_space_box_normalized():
    env = make_env()
    obs, _ = env.reset(seed=1)
    assert isinstance(env.observation_space, spaces.Box)
    assert obs.min() >= 0.0 and obs.max() <= 1.0


def test_tc009_invalid_action_raises():
    env = make_env()
    env.reset(seed=0)
    with pytest.raises((ValueError, AssertionError)):
        env.step(9)


def test_tc010_terminated_when_no_move():
    env = make_env()
    env.reset(seed=0)
    # 直接构造终局棋盘
    env._board = np.array(
        [[2, 4, 2, 4], [4, 2, 4, 2], [2, 4, 2, 4], [4, 2, 4, 2]], dtype=np.int64
    )
    # 任意一步后应判定 terminated（此盘任何方向都不可动 -> illegal，但终局判定为真）
    _, _, terminated, _, _ = env.step(2)
    assert terminated is True


def test_tc011_truncated_on_step_limit():
    env = make_env(max_steps=3)
    env.reset(seed=0)
    truncated = False
    for _ in range(3):
        _, _, terminated, truncated, _ = env.step(env.action_space.sample())
        if terminated:
            break
    assert truncated is True or terminated is True


def test_tc012_step_before_reset_raises():
    env = make_env()
    with pytest.raises(RuntimeError):
        env.step(0)


def test_legal_action_mask_in_info_and_method():
    env = make_env()
    _, info = env.reset(seed=0)
    assert "legal_action_mask" in info
    assert info["legal_action_mask"].shape == (4,)
    # 仅左侧不可动的棋盘
    env._board = np.array(
        [[2, 4, 8, 16], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], dtype=np.int64
    )
    mask = env.legal_action_mask()
    assert mask[2] == False  # LEFT 非法


def test_illegal_move_marked_in_info():
    env = make_env()
    env.reset(seed=0)
    env._board = np.array(
        [[2, 4, 8, 16], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], dtype=np.int64
    )
    # 该盘向左不可动 -> illegal
    _, reward, _, _, info = env.step(2)
    assert info["illegal"] is True
    assert reward == env.illegal_penalty


def test_tc046_reproducible_with_seed():
    env1, env2 = make_env(), make_env()
    o1, _ = env1.reset(seed=123)
    o2, _ = env2.reset(seed=123)
    assert np.array_equal(o1, o2)
    for a in [0, 1, 2, 3, 0, 1]:
        s1 = env1.step(a)
        s2 = env2.step(a)
        assert np.array_equal(s1[0], s2[0])
        assert s1[1] == s2[1]
