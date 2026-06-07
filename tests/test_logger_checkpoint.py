"""T-12/T-13 测试：记录器与检查点。关联 TC-025~027, TC-030~034, TC-051。"""

import os

import pytest

from src.agents.dqn import DQNAgent
from src.utils.checkpoint import load_checkpoint, load_into_agent, save_checkpoint
from src.utils.logger import ExperimentLogger


def test_tc025_logger_writes_config_snapshot(tmp_path):
    cfg = {"total_steps": 100, "lr": 0.001}
    logger = ExperimentLogger(str(tmp_path), run_name="quick", config=cfg)
    snap = os.path.join(logger.run_dir, "config.snapshot.yaml")
    assert os.path.exists(snap)
    logger.close()


def test_tc026_log_scalars(tmp_path):
    logger = ExperimentLogger(str(tmp_path), run_name="m")
    logger.log_scalars({"reward": 1.0, "max_tile": 64, "loss": 0.2}, step=1)
    logger.close()
    # tfevents 文件应存在
    files = os.listdir(logger.run_dir)
    assert any(f.startswith("events.out.tfevents") for f in files)


def test_tc027_unique_run_dirs(tmp_path):
    import time

    l1 = ExperimentLogger(str(tmp_path), run_name="x")
    time.sleep(1.1)  # 时间戳精确到秒，确保不同
    l2 = ExperimentLogger(str(tmp_path), run_name="x")
    assert l1.run_dir != l2.run_dir
    l1.close()
    l2.close()


def _agent():
    return DQNAgent(obs_shape=(4, 4), hidden_sizes=(16,), device="cpu")


def test_tc030_save_and_load_checkpoint(tmp_path):
    agent = _agent()
    path = str(tmp_path / "ckpt.pt")
    save_checkpoint(path, agent.state_dict(), meta={"step": 100})
    assert os.path.exists(path)
    payload = load_checkpoint(path)
    assert payload["meta"]["step"] == 100


def test_tc032_load_into_agent_roundtrip(tmp_path):
    a1 = _agent()
    path = str(tmp_path / "best.pt")
    save_checkpoint(path, a1.state_dict(), meta={"max_tile": 256})
    a2 = _agent()
    meta = load_into_agent(a2, path)
    assert meta["max_tile"] == 256


def test_tc033_structure_mismatch_raises(tmp_path):
    a1 = DQNAgent(obs_shape=(4, 4), hidden_sizes=(64,), device="cpu")
    path = str(tmp_path / "c.pt")
    save_checkpoint(path, a1.state_dict())
    a2 = DQNAgent(obs_shape=(4, 4), hidden_sizes=(256, 256), device="cpu")
    with pytest.raises(ValueError):
        load_into_agent(a2, path)


def test_tc051_missing_checkpoint_raises():
    with pytest.raises(FileNotFoundError):
        load_checkpoint("does/not/exist.pt")
