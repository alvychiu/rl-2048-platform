"""2048 GUI 入口：手动游玩 + 可选 AI 演示。

用法：
    python -m src.gui.play
    python -m src.gui.play --ckpt runs/<id>/best.pt
    make play
    make play CKPT=runs/<id>/best.pt
"""

from __future__ import annotations

import argparse
import os
import sys
import time

import numpy as np
import pygame

from src.agents.dqn import DQNAgent
from src.env import board as B
from src.env.game_2048_env import Game2048Env
from src.gui.renderer import draw_board, draw_overlay, key_to_action, window_size
from src.utils.checkpoint import load_checkpoint, load_into_agent


def _check_display() -> None:
    if sys.platform.startswith("linux") and not os.environ.get("DISPLAY"):
        raise RuntimeError("无图形显示环境（DISPLAY 未设置），无法启动 GUI")


def run_manual(env: Game2048Env, fps: int = 30) -> None:
    pygame.init()
    _check_display()
    screen = pygame.display.set_mode(window_size())
    pygame.display.set_caption("2048 — 手动模式")
    clock = pygame.time.Clock()
    obs, info = env.reset()
    game_over = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
                if event.key == pygame.K_r:
                    obs, info = env.reset()
                    game_over = False
                    continue
                if not game_over:
                    action = key_to_action(event.key)
                    if action is not None:
                        obs, _, terminated, truncated, info = env.step(action)
                        game_over = terminated or truncated

        draw_board(screen, info["board"], info["score"], subtitle="手动模式 | R 重开 | ESC 退出")
        if game_over:
            draw_overlay(screen, "游戏结束！")
        pygame.display.flip()
        clock.tick(fps)


def run_ai_demo(
    env: Game2048Env,
    agent: DQNAgent,
    fps: int = 8,
    step_delay: float = 0.15,
) -> None:
    pygame.init()
    _check_display()
    screen = pygame.display.set_mode(window_size())
    pygame.display.set_caption("2048 — AI 演示")
    clock = pygame.time.Clock()
    obs, info = env.reset()
    game_over = False
    last_step = 0.0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                return

        now = time.time()
        if not game_over and now - last_step >= step_delay:
            action = agent.act_greedy(obs, legal_mask=info["legal_action_mask"])
            obs, _, terminated, truncated, info = env.step(action)
            game_over = terminated or truncated
            last_step = now
            if game_over:
                time.sleep(0.8)
                obs, info = env.reset()
                game_over = False

        draw_board(
            screen,
            info["board"],
            info["score"],
            title="2048 AI",
            subtitle="AI 自动演示 | ESC 退出",
        )
        pygame.display.flip()
        clock.tick(fps)


def main() -> None:
    parser = argparse.ArgumentParser(description="2048 GUI（pygame）")
    parser.add_argument("--ckpt", default=None, help="检查点路径，提供则进入 AI 演示模式")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()

    env = Game2048Env(render_mode="human")

    if args.ckpt:
        meta = load_checkpoint(args.ckpt, map_location="cpu").get("meta", {})
        hidden = tuple(meta.get("hidden_sizes", (256, 256)))
        agent = DQNAgent(obs_shape=(4, 4), hidden_sizes=hidden, device=args.device)
        load_into_agent(agent, args.ckpt, map_location="cpu")
        env.reset(seed=args.seed)
        run_ai_demo(env, agent, fps=min(args.fps, 12))
    else:
        env.reset(seed=args.seed)
        run_manual(env, fps=args.fps)


if __name__ == "__main__":
    main()
