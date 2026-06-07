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


def test_snake_weight_matrix_normalized_and_corner_max():
    w = B.snake_weight_matrix("bottom-left", ratio=0.7)
    assert w.shape == (4, 4)
    assert abs(w.sum() - 1.0) < 1e-9
    # 左下角(3,0)为蛇形起点，应为最大权重
    assert w[3, 0] == w.max()


def test_snake_weight_matrix_other_corner():
    w = B.snake_weight_matrix("bottom-right", ratio=0.7)
    assert w[3, 3] == w.max()


def test_snake_order_is_full_permutation():
    order = B._snake_order("bottom-left")
    assert len(order) == 16
    assert len(set(order)) == 16


def test_snake_gradient_prefers_corner_descending():
    aligned = np.array(
        [[2, 4, 8, 16], [128, 64, 32, 16], [256, 128, 64, 32], [512, 256, 128, 64]],
        dtype=np.int64,
    )
    scattered = np.array(
        [[512, 0, 0, 2], [0, 0, 256, 0], [0, 128, 0, 0], [0, 0, 0, 64]],
        dtype=np.int64,
    )
    assert B.snake_gradient_score(aligned) > B.snake_gradient_score(scattered)


def test_discouraged_action_penalty_applied():
    from src.env.game_2048_env import Game2048Env

    env = Game2048Env(
        merge_reward_scale=0.0,
        discouraged_action=0,
        discouraged_action_penalty=-0.5,
    )
    env.reset(seed=0)
    env._board = np.array(
        [[0, 0, 0, 0], [0, 0, 0, 0], [2, 0, 0, 0], [4, 0, 0, 0]], dtype=np.int64
    )
    _, reward, _, _, info = env.step(0)  # UP（合法且被惩罚）
    assert info["illegal"] is False
    assert reward <= -0.5


def test_snake_reward_changes_reward():
    from src.env.game_2048_env import Game2048Env

    env = Game2048Env(merge_reward_scale=0.0, reward_snake_coef=4.0)
    env.reset(seed=1)
    env._board = np.array(
        [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 4, 2], [0, 0, 0, 0]], dtype=np.int64
    )
    _, reward, _, _, info = env.step(1)  # DOWN，向底部聚拢
    assert info["illegal"] is False
    assert reward != 0.0


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
