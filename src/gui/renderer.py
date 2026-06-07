"""pygame 棋盘渲染与输入映射（可单测，不依赖窗口循环）。"""

from __future__ import annotations

import pygame

from src.env import board as B

# 经典 2048 风格配色：(背景色, 文字色)
_TILE_COLORS: dict[int, tuple[tuple[int, int, int], tuple[int, int, int]]] = {
    0: ((205, 193, 180), (119, 110, 101)),
    2: ((238, 228, 218), (119, 110, 101)),
    4: ((237, 224, 200), (119, 110, 101)),
    8: ((242, 177, 121), (249, 246, 242)),
    16: ((245, 149, 99), (249, 246, 242)),
    32: ((246, 124, 95), (249, 246, 242)),
    64: ((246, 94, 59), (249, 246, 242)),
    128: ((237, 207, 114), (249, 246, 242)),
    256: ((237, 204, 97), (249, 246, 242)),
    512: ((237, 200, 80), (249, 246, 242)),
    1024: ((237, 197, 63), (249, 246, 242)),
    2048: ((237, 194, 46), (249, 246, 242)),
}

WINDOW_BG = (250, 248, 239)
GRID_BG = (187, 173, 160)
HEADER_BG = (250, 248, 239)
TITLE_COLOR = (119, 110, 101)
SCORE_BG = (187, 173, 160)
SCORE_FG = (255, 255, 255)
SCORE_LABEL = (238, 228, 218)

CELL_SIZE = 100
CELL_GAP = 10
GRID_SIZE = B.SIZE
PADDING = 20
HEADER_H = 100

# macOS / 跨平台：优先选用支持中文的系统字体，避免 pygame 默认 arial 显示 □□□□
_CJK_FONT_CANDIDATES = (
    "PingFang SC",
    "PingFangSC-Regular",
    "STHeiti Light",
    "STHeiti",
    "Hiragino Sans GB",
    "Arial Unicode MS",
    "Microsoft YaHei",
    "Noto Sans CJK SC",
    "WenQuanYi Micro Hei",
)

_font_cache: dict[tuple[int, bool], pygame.font.Font] = {}


def _font_supports_cjk(font: pygame.font.Font) -> bool:
    """粗略检测字体是否能渲染中文（非空、非全空白）。"""
    try:
        surf = font.render("中文", True, (0, 0, 0))
        return surf.get_width() > 10
    except Exception:
        return False


def get_ui_font(size: int, bold: bool = False) -> pygame.font.Font:
    """获取可显示中文的 UI 字体（带缓存）。"""
    key = (size, bold)
    if key in _font_cache:
        return _font_cache[key]
    for name in _CJK_FONT_CANDIDATES:
        try:
            f = pygame.font.SysFont(name, size, bold=bold)
            if _font_supports_cjk(f):
                _font_cache[key] = f
                return f
        except Exception:
            continue
    f = pygame.font.SysFont(None, size, bold=bold)
    _font_cache[key] = f
    return f


def window_size() -> tuple[int, int]:
    w = PADDING * 2 + GRID_SIZE * CELL_SIZE + (GRID_SIZE - 1) * CELL_GAP
    h = HEADER_H + PADDING * 2 + GRID_SIZE * CELL_SIZE + (GRID_SIZE - 1) * CELL_GAP
    return w, h


def tile_colors(value: int) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    if value in _TILE_COLORS:
        return _TILE_COLORS[value]
    # 更大数值沿用 2048 配色
    return _TILE_COLORS[2048]


def key_to_action(key: int) -> int | None:
    """将 pygame 按键映射为环境动作；无法识别返回 None。"""
    mapping = {
        pygame.K_UP: B.UP,
        pygame.K_w: B.UP,
        pygame.K_DOWN: B.DOWN,
        pygame.K_s: B.DOWN,
        pygame.K_LEFT: B.LEFT,
        pygame.K_a: B.LEFT,
        pygame.K_RIGHT: B.RIGHT,
        pygame.K_d: B.RIGHT,
    }
    return mapping.get(key)


def draw_board(
    surface: pygame.Surface,
    board,
    score: int,
    title: str = "2048",
    subtitle: str = "方向键/WASD 移动 | R 重开 | ESC 退出",
) -> None:
    surface.fill(WINDOW_BG)
    font_title = get_ui_font(42, bold=True)
    font_small = get_ui_font(18)
    font_score = get_ui_font(22, bold=True)
    # 方块数字用西文字体即可
    font_cell = pygame.font.SysFont("arial", 36, bold=True)
    font_cell_sm = pygame.font.SysFont("arial", 28, bold=True)

    surface.blit(font_title.render(title, True, TITLE_COLOR), (PADDING, 18))
    surface.blit(font_small.render(subtitle, True, TITLE_COLOR), (PADDING, 68))

    score_w, score_h = 110, 56
    score_x = surface.get_width() - PADDING - score_w
    pygame.draw.rect(surface, SCORE_BG, (score_x, 20, score_w, score_h), border_radius=6)
    surface.blit(
        font_small.render("SCORE", True, SCORE_LABEL),
        (score_x + 12, 26),
    )
    surface.blit(
        font_score.render(str(score), True, SCORE_FG),
        (score_x + 12, 46),
    )

    grid_x = PADDING
    grid_y = HEADER_H + PADDING
    grid_w = GRID_SIZE * CELL_SIZE + (GRID_SIZE - 1) * CELL_GAP
    pygame.draw.rect(surface, GRID_BG, (grid_x, grid_y, grid_w, grid_w), border_radius=8)

    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            val = int(board[r, c])
            bg, fg = tile_colors(val)
            x = grid_x + c * (CELL_SIZE + CELL_GAP) + CELL_GAP
            y = grid_y + r * (CELL_SIZE + CELL_GAP) + CELL_GAP
            pygame.draw.rect(surface, bg, (x, y, CELL_SIZE, CELL_SIZE), border_radius=6)
            if val:
                text = str(val)
                f = font_cell if val < 1000 else font_cell_sm
                txt = f.render(text, True, fg)
                surface.blit(
                    txt,
                    txt.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2)),
                )


def draw_overlay(surface: pygame.Surface, message: str) -> None:
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((255, 255, 255, 160))
    surface.blit(overlay, (0, 0))
    font = get_ui_font(40, bold=True)
    txt = font.render(message, True, (60, 58, 50))
    surface.blit(txt, txt.get_rect(center=surface.get_rect().center))
