"""T-16 评估脚本测试。关联 US-11 / TC-048~TC-051。"""

import pytest

from src.agents.dqn import DQNAgent
from src.eval.evaluate import evaluate
from src.utils.checkpoint import save_checkpoint


def _make_ckpt(tmp_path, hidden=(32, 32)):
    agent = DQNAgent(obs_shape=(4, 4), hidden_sizes=hidden, device="cpu")
    path = str(tmp_path / "best.pt")
    save_checkpoint(path, agent.state_dict(), meta={"step": 1})
    return path


def test_tc048_eval_outputs_stats(tmp_path):
    ckpt = _make_ckpt(tmp_path)
    result = evaluate(ckpt, episodes=3, hidden_sizes=(32, 32), max_steps=200)
    for key in ("max_tile_median", "max_tile_mean", "max_tile_max", "score_mean"):
        assert key in result["trained"]
    assert "s2_passed" in result


def test_tc049_baseline_present(tmp_path):
    ckpt = _make_ckpt(tmp_path)
    result = evaluate(ckpt, episodes=3, hidden_sizes=(32, 32), max_steps=200)
    assert result["baseline"]["max_tile_median"] > 0


def test_tc050_single_episode_no_error(tmp_path):
    ckpt = _make_ckpt(tmp_path)
    result = evaluate(ckpt, episodes=1, hidden_sizes=(32, 32), max_steps=200)
    assert result["trained"]["max_tile_max"] >= 2


def test_tc051_missing_checkpoint_raises():
    with pytest.raises(FileNotFoundError):
        evaluate("nope/missing.pt", episodes=1, hidden_sizes=(32, 32))
