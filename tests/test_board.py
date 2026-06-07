"""T-04 棋盘内核单测。关联 US-01 / TC-001~TC-006。"""

import numpy as np

from src.env import board as B


def test_tc001_merge_two_equal_left():
    """TC-001: [2,2,0,0] 左移 -> [4,0,0,0]，得分 +4。"""
    b = np.array([[2, 2, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], dtype=np.int64)
    res, score, moved = B.move(b, B.LEFT)
    assert list(res[0]) == [4, 0, 0, 0]
    assert score == 4
    assert moved is True


def test_tc002_four_equal_merge_once_each():
    """TC-002: [2,2,2,2] 左移 -> [4,4,0,0]，每块只合并一次。"""
    b = np.array([[2, 2, 2, 2], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], dtype=np.int64)
    res, score, _ = B.move(b, B.LEFT)
    assert list(res[0]) == [4, 4, 0, 0]
    assert score == 8


def test_tc003_illegal_move_no_change():
    """TC-003: 无法左移时棋盘不变，moved=False。"""
    b = np.array([[2, 4, 8, 16], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], dtype=np.int64)
    res, score, moved = B.move(b, B.LEFT)
    assert np.array_equal(res, b)
    assert moved is False
    assert score == 0


def test_tc004_adjacent_pairs_merge_separately():
    """TC-004: [2,2,4,4] 左移 -> [4,8,0,0]。"""
    b = np.array([[2, 2, 4, 4], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], dtype=np.int64)
    res, score, _ = B.move(b, B.LEFT)
    assert list(res[0]) == [4, 8, 0, 0]
    assert score == 12


def test_tc005_full_board_with_mergeable_not_over():
    """TC-005: 棋盘满但有相邻同值 -> 非终局。"""
    b = np.array(
        [[2, 2, 4, 8], [16, 32, 64, 128], [2, 4, 8, 16], [32, 64, 128, 256]],
        dtype=np.int64,
    )
    assert B.is_game_over(b) is False


def test_tc006_reset_spawns_handled_by_env():
    """TC-006: 空盘上连续生成两个方块占据两个不同空位。"""
    rng = np.random.default_rng(7)
    b = B.new_board()
    assert B.spawn_tile(b, rng) is True
    assert B.spawn_tile(b, rng) is True
    assert int((b != 0).sum()) == 2
    # 生成值只能是 2 或 4
    assert set(int(v) for v in b[b != 0]).issubset({2, 4})


def test_directions_up_down_right():
    b = np.array([[2, 0, 0, 0], [2, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], dtype=np.int64)
    up, _, _ = B.move(b, B.UP)
    assert up[0, 0] == 4 and up[1, 0] == 0
    down, _, _ = B.move(b, B.DOWN)
    assert down[3, 0] == 4 and down[2, 0] == 0
    b2 = np.array([[0, 0, 2, 2], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], dtype=np.int64)
    right, _, _ = B.move(b2, B.RIGHT)
    assert list(right[0]) == [0, 0, 0, 4]


def test_reproducible_spawn_same_seed():
    rng1 = np.random.default_rng(0)
    rng2 = np.random.default_rng(0)
    b1, b2 = B.new_board(), B.new_board()
    for _ in range(5):
        B.spawn_tile(b1, rng1)
        B.spawn_tile(b2, rng2)
    assert np.array_equal(b1, b2)


def test_game_over_on_full_alternating_board():
    full = np.array(
        [[2, 4, 2, 4], [4, 2, 4, 2], [2, 4, 2, 4], [4, 2, 4, 2]], dtype=np.int64
    )
    assert B.is_game_over(full) is True
    assert B.can_move(full) is False
