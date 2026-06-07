"""评估脚本：加载检查点跑 N 局，与随机基线对比，判定 S2 是否达标。

用法：
    python -m src.eval.evaluate --ckpt runs/<id>/best.pt --episodes 100
    python -m src.eval.evaluate --ckpt runs/<id>/best.pt --hidden 256 256

输出训练策略 vs 随机基线的 max_tile / score 统计，并判定
max_tile 中位数是否 >= 512（spec S2）。
"""

from __future__ import annotations

import argparse

import numpy as np

from src.agents.dqn import DQNAgent, agent_kwargs_from_meta
from src.env.game_2048_env import Game2048Env
from src.utils.checkpoint import load_checkpoint, load_into_agent

S2_THRESHOLD = 512


def _run_episodes(policy_fn, episodes: int, max_steps: int, seed: int) -> dict:
    env = Game2048Env(max_steps=max_steps)
    max_tiles, scores = [], []
    for i in range(episodes):
        obs, info = env.reset(seed=seed + i)
        done = False
        while not done:
            action = policy_fn(obs, env, info)
            obs, _, terminated, truncated, info = env.step(action)
            done = terminated or truncated
        max_tiles.append(info["max_tile"])
        scores.append(info["score"])
    return {
        "max_tile_median": float(np.median(max_tiles)),
        "max_tile_mean": float(np.mean(max_tiles)),
        "max_tile_max": int(np.max(max_tiles)),
        "score_mean": float(np.mean(scores)),
        "max_tiles": max_tiles,
    }


def evaluate(
    ckpt: str,
    episodes: int = 100,
    hidden_sizes=None,
    max_steps: int = 5000,
    seed: int = 2024,
    device: str = "cpu",
) -> dict:
    # RV-3：优先从检查点 meta 读取网络结构，避免手填 --hidden 不一致。
    meta = load_checkpoint(ckpt, map_location="cpu").get("meta", {})
    if hidden_sizes is not None:
        meta = {**meta, "hidden_sizes": list(hidden_sizes)}

    agent = DQNAgent(**agent_kwargs_from_meta(meta), device=device)
    load_into_agent(agent, ckpt, map_location="cpu")

    trained = _run_episodes(
        lambda obs, env, info: agent.act_greedy(
            obs, legal_mask=info["legal_action_mask"]
        ),
        episodes,
        max_steps,
        seed,
    )
    rng = np.random.default_rng(seed)
    baseline = _run_episodes(
        lambda obs, env, info: int(rng.integers(env.action_space.n)),
        episodes,
        max_steps,
        seed,
    )

    passed = trained["max_tile_median"] >= S2_THRESHOLD
    return {"trained": trained, "baseline": baseline, "s2_passed": passed}


def _fmt(stats: dict) -> str:
    return (
        f"{stats['max_tile_median']:>16.0f}"
        f"{stats['max_tile_max']:>15d}"
        f"{stats['score_mean']:>14.0f}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="2048 DQN 评估")
    parser.add_argument("--ckpt", required=True, help="检查点路径，如 runs/<id>/best.pt")
    parser.add_argument("--episodes", type=int, default=100)
    parser.add_argument(
        "--hidden",
        type=int,
        nargs="+",
        default=None,
        help="网络隐层；默认从检查点 meta 自动读取（RV-3）",
    )
    parser.add_argument("--max-steps", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=2024)
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()

    result = evaluate(
        ckpt=args.ckpt,
        episodes=args.episodes,
        hidden_sizes=args.hidden,
        max_steps=args.max_steps,
        seed=args.seed,
        device=args.device,
    )

    print(f"[eval] checkpoint = {args.ckpt} | episodes={args.episodes}")
    print("-" * 60)
    print(f"{'Policy':<18}{'max_tile(median)':>16}{'max_tile(max)':>15}{'score(mean)':>14}")
    print(f"{'trained DQN':<18}{_fmt(result['trained'])}")
    print(f"{'random baseline':<18}{_fmt(result['baseline'])}")
    print("-" * 60)
    median = result["trained"]["max_tile_median"]
    status = "✅ PASS" if result["s2_passed"] else "❌ FAIL"
    print(f"[S2] max_tile median {median:.0f} >= {S2_THRESHOLD}  ->  {status}")


if __name__ == "__main__":
    main()
