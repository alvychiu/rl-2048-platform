"""训练主循环：串联环境 / DQN / 回放 / 记录 / 检查点。

用法：
    python -m src.train.train --config configs/quick.yaml

流程（High 风险集成点，先用 quick 配置跑通管线再追效果）：
  读配置 → set_seed → 建环境/Agent/Buffer/Logger → 采样交互 → 学习
  → 周期记录指标 / 评估 / 保存 periodic+best 检查点 → 输出总结。
"""

from __future__ import annotations

import argparse
import os
import time

import numpy as np

from src.agents.dqn import DQNAgent
from src.env.game_2048_env import Game2048Env
from src.train.config import Config
from src.train.replay_buffer import ReplayBuffer
from src.utils.checkpoint import save_checkpoint
from src.utils.logger import ExperimentLogger
from src.utils.seeding import set_global_seed


def evaluate_agent(agent: DQNAgent, cfg: Config, episodes: int, seed: int) -> dict:
    """贪心评估若干局，返回 max_tile / score 统计。"""
    env = Game2048Env(
        max_steps=cfg.max_steps,
        illegal_penalty=cfg.illegal_penalty,
        merge_reward_scale=cfg.merge_reward_scale,
        reward_empty_coef=cfg.reward_empty_coef,
        reward_new_max_bonus=cfg.reward_new_max_bonus,
        reward_milestones=cfg.reward_milestones,
        reward_structure_coef=cfg.reward_structure_coef,
        reward_structure_corner=cfg.reward_structure_corner,
        reward_structure_monotonicity=cfg.reward_structure_monotonicity,
        reward_structure_smoothness=cfg.reward_structure_smoothness,
        reward_structure_corner_log_scale=cfg.reward_structure_corner_log_scale,
        reward_structure_corner_min_tile=cfg.reward_structure_corner_min_tile,
        reward_high_tile_coef=cfg.reward_high_tile_coef,
        reward_high_tile_min=cfg.reward_high_tile_min,
    )
    max_tiles, scores = [], []
    for i in range(episodes):
        obs, info = env.reset(seed=seed + i)
        done = False
        while not done:
            action = agent.act_greedy(obs, legal_mask=info["legal_action_mask"])
            obs, _, terminated, truncated, info = env.step(action)
            done = terminated or truncated
        max_tiles.append(info["max_tile"])
        scores.append(info["score"])
    return {
        "max_tile_median": float(np.median(max_tiles)),
        "max_tile_mean": float(np.mean(max_tiles)),
        "max_tile_max": int(np.max(max_tiles)),
        "score_mean": float(np.mean(scores)),
    }


def train(cfg: Config) -> dict:
    set_global_seed(cfg.seed)
    rng = np.random.default_rng(cfg.seed)

    env = Game2048Env(
        max_steps=cfg.max_steps,
        illegal_penalty=cfg.illegal_penalty,
        merge_reward_scale=cfg.merge_reward_scale,
        reward_empty_coef=cfg.reward_empty_coef,
        reward_new_max_bonus=cfg.reward_new_max_bonus,
        reward_milestones=cfg.reward_milestones,
        reward_structure_coef=cfg.reward_structure_coef,
        reward_structure_corner=cfg.reward_structure_corner,
        reward_structure_monotonicity=cfg.reward_structure_monotonicity,
        reward_structure_smoothness=cfg.reward_structure_smoothness,
        reward_structure_corner_log_scale=cfg.reward_structure_corner_log_scale,
        reward_structure_corner_min_tile=cfg.reward_structure_corner_min_tile,
        reward_high_tile_coef=cfg.reward_high_tile_coef,
        reward_high_tile_min=cfg.reward_high_tile_min,
    )
    agent = DQNAgent(
        obs_shape=(4, 4),
        num_actions=4,
        hidden_sizes=tuple(cfg.hidden_sizes),
        lr=cfg.lr,
        gamma=cfg.gamma,
        eps_start=cfg.eps_start,
        eps_end=cfg.eps_end,
        eps_decay_steps=cfg.eps_decay_steps,
        target_update_interval=cfg.target_update_interval,
        grad_clip_max_norm=cfg.grad_clip_max_norm,
        device=cfg.device,
    )
    buffer = ReplayBuffer(capacity=cfg.buffer_size, obs_shape=(4, 4))
    logger = ExperimentLogger(cfg.log_dir, run_name=cfg.run_name, config=cfg.to_dict())

    print(f"[cfg ] device={agent.device} | seed={cfg.seed} | run={logger.run_dir}")
    logger.log_text(f"device={agent.device} seed={cfg.seed} total_steps={cfg.total_steps}")

    obs, info = env.reset(seed=cfg.seed)
    ep_reward, ep_len, ep_count = 0.0, 0, 0
    best_median = -1.0
    last_loss = 0.0
    t0 = time.time()

    for step in range(1, cfg.total_steps + 1):
        action = agent.act(obs, step, rng, legal_mask=info["legal_action_mask"])
        next_obs, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        buffer.push(
            obs,
            action,
            reward,
            next_obs,
            terminated,
            info["legal_action_mask"],
        )
        obs = next_obs
        ep_reward += reward
        ep_len += 1

        if (
            step >= cfg.learning_starts
            and step % cfg.train_freq == 0
            and len(buffer) >= cfg.batch_size
        ):
            last_loss = agent.learn(buffer.sample(cfg.batch_size, rng=rng))

        if done:
            ep_count += 1
            logger.log_scalars(
                {
                    "train/episode_reward": ep_reward,
                    "train/episode_len": ep_len,
                    "train/max_tile": info["max_tile"],
                    "train/score": info["score"],
                    "train/epsilon": agent.epsilon(step),
                    "train/loss": last_loss,
                },
                step=step,
            )
            if ep_count % 20 == 0:
                print(
                    f"step {step:>7} | ep {ep_count:>5} | reward {ep_reward:7.1f} "
                    f"| max_tile {info['max_tile']:>5} | loss {last_loss:.3f} "
                    f"| eps {agent.epsilon(step):.3f}"
                )
            obs, info = env.reset()
            ep_reward, ep_len = 0.0, 0

        if step % cfg.save_every == 0:
            path = os.path.join(logger.run_dir, f"ckpt_{step}.pt")
            save_checkpoint(
                path,
                agent.state_dict(),
                meta={"step": step, "hidden_sizes": list(cfg.hidden_sizes)},
            )
            logger.log_text(f"[ckpt] saved {path}")

        if step % cfg.eval_every == 0:
            stats = evaluate_agent(agent, cfg, cfg.eval_episodes, seed=cfg.seed + 9999)
            logger.log_scalars(
                {
                    "eval/max_tile_median": stats["max_tile_median"],
                    "eval/max_tile_mean": stats["max_tile_mean"],
                    "eval/score_mean": stats["score_mean"],
                },
                step=step,
            )
            if stats["max_tile_median"] > best_median:
                best_median = stats["max_tile_median"]
                best_path = os.path.join(logger.run_dir, "best.pt")
                save_checkpoint(
                    best_path,
                    agent.state_dict(),
                    meta={
                        "step": step,
                        "hidden_sizes": list(cfg.hidden_sizes),
                        **stats,
                    },
                )
                logger.log_text(
                    f"[best] step={step} median={best_median} -> {best_path}"
                )

    elapsed = time.time() - t0
    summary = {
        "run_dir": logger.run_dir,
        "episodes": ep_count,
        "best_eval_median": best_median,
        "elapsed_sec": round(elapsed, 1),
    }
    logger.log_text(f"[done] {summary}")
    logger.close()
    print(f"[done] episodes={ep_count} best_median={best_median} elapsed={elapsed:.1f}s")
    print(f"[done] logs -> {logger.run_dir}")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="2048 DQN 训练")
    parser.add_argument(
        "--config", default="configs/quick.yaml", help="YAML 配置文件路径"
    )
    args = parser.parse_args()
    cfg = Config.from_yaml(args.config)
    train(cfg)


if __name__ == "__main__":
    main()
