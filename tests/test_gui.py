"""T-21 GUI 测试。关联 US-12 / FR-11。"""

import pytest

pygame = pytest.importorskip("pygame")

from src.env import board as B
from src.gui.renderer import key_to_action, tile_colors, window_size


def test_key_to_action_arrows_and_wasd():
    pygame.init()
    assert key_to_action(pygame.K_UP) == B.UP
    assert key_to_action(pygame.K_w) == B.UP
    assert key_to_action(pygame.K_DOWN) == B.DOWN
    assert key_to_action(pygame.K_s) == B.DOWN
    assert key_to_action(pygame.K_LEFT) == B.LEFT
    assert key_to_action(pygame.K_a) == B.LEFT
    assert key_to_action(pygame.K_RIGHT) == B.RIGHT
    assert key_to_action(pygame.K_d) == B.RIGHT
    assert key_to_action(pygame.K_ESCAPE) is None


def test_tile_colors_known_and_large():
    bg, fg = tile_colors(2)
    assert isinstance(bg, tuple) and len(bg) == 3
    bg2, _ = tile_colors(4096)
    assert bg2 == tile_colors(2048)[0]


def test_window_size_positive():
    w, h = window_size()
    assert w > 400 and h > 400


def test_play_module_parses_args():
    from src.gui import play as play_mod

    assert hasattr(play_mod, "main")
    assert hasattr(play_mod, "run_manual")
    assert hasattr(play_mod, "run_ai_demo")
