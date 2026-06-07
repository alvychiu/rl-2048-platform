"""T-07 文本渲染测试。关联 US-03 / TC-013, TC-014。"""

import numpy as np

from src.env.game_2048_env import Game2048Env


def test_tc013_render_text_readable():
    env = Game2048Env(render_mode="ansi")
    env.reset(seed=0)
    env._board = np.array(
        [[2, 0, 4, 0], [0, 16, 8, 2], [4, 32, 128, 16], [0, 2, 4, 256]],
        dtype=np.int64,
    )
    text = env.render()
    assert isinstance(text, str)
    # 包含若干已知数值
    for token in ["256", "128", "32", "16"]:
        assert token in text
    # 4 行棋盘 + 分隔线，至少 9 行结构 + score
    assert text.count("\n") >= 8
    assert "score:" in text


def test_tc014_empty_cells_no_error():
    env = Game2048Env(render_mode="ansi")
    env.reset(seed=0)
    env._board = np.zeros((4, 4), dtype=np.int64)
    text = env.render()
    assert isinstance(text, str)
    # 空盘不应出现任何数字方块（除 score 行外）
    board_part = text.split("score:")[0]
    assert not any(ch.isdigit() for ch in board_part)


def test_render_none_when_no_mode():
    env = Game2048Env(render_mode=None)
    env.reset(seed=0)
    assert env.render() is None
