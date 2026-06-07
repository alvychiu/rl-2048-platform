"""结构奖励启发式单测。"""

import numpy as np

from src.env import board as B


def test_max_tile_in_corner_true():
    board = np.array(
        [[512, 64, 8, 2], [32, 16, 4, 0], [8, 4, 2, 0], [2, 0, 0, 0]],
        dtype=np.int64,
    )
    assert B.max_tile_in_corner(board) is True


def test_max_tile_in_corner_false():
    board = np.array(
        [[64, 512, 8, 2], [32, 16, 4, 0], [8, 4, 2, 0], [2, 0, 0, 0]],
        dtype=np.int64,
    )
    assert B.max_tile_in_corner(board) is False


def test_structure_score_higher_for_corner_layout():
    corner = np.array(
        [[256, 64, 16, 4], [32, 8, 4, 2], [8, 4, 2, 0], [4, 2, 0, 0]],
        dtype=np.int64,
    )
    scattered = np.array(
        [[64, 128, 32, 16], [8, 256, 4, 2], [4, 2, 8, 0], [2, 0, 4, 0]],
        dtype=np.int64,
    )
    assert B.structure_score(corner) > B.structure_score(scattered)


def test_corner_log_scale_disabled_uses_binary_corner():
    board = np.array(
        [[512, 64, 16, 4], [32, 8, 4, 2], [8, 4, 2, 0], [4, 2, 0, 0]],
        dtype=np.int64,
    )
    with_log = B.structure_score(
        board,
        corner_weight=1.0,
        monotonicity_weight=0.0,
        smoothness_weight=0.0,
        corner_log_scale=True,
    )
    no_log = B.structure_score(
        board,
        corner_weight=1.0,
        monotonicity_weight=0.0,
        smoothness_weight=0.0,
        corner_log_scale=False,
    )
    assert no_log == 1.0
    assert with_log < no_log


def test_corner_min_tile_suppresses_early_bonus():
    board = np.array(
        [[64, 32, 16, 8], [32, 16, 8, 4], [16, 8, 4, 2], [8, 4, 2, 0]],
        dtype=np.int64,
    )
    low = B.structure_score(board, corner_min_tile=0, corner_log_scale=False)
    high = B.structure_score(board, corner_min_tile=128, corner_log_scale=False)
    assert low > high


def test_env_structure_reward_on_improving_layout():
    from src.env.game_2048_env import Game2048Env

    env = Game2048Env(
        merge_reward_scale=0.0,
        reward_structure_coef=1.0,
        reward_structure_corner=2.0,
    )
    env.reset(seed=0)
    # 构造：大 tile 在角上，左移可维持/改善结构
    env._board = np.array(
        [[0, 128, 64, 32], [0, 16, 8, 4], [0, 8, 4, 2], [0, 2, 0, 0]],
        dtype=np.int64,
    )
    env._prev_max_tile = 128
    _, reward, _, _, info = env.step(2)  # LEFT：合法移动且 max 仍在角落
    assert info["illegal"] is False
    assert reward != 0.0
