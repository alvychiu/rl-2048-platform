"""T-15 训练冒烟测试：极小步数跑通 train→记录→检查点。关联 TC-045。"""

import os

from src.train.config import Config
from src.train.train import train


def test_tc045_training_smoke(tmp_path):
    cfg = Config.from_dict(
        {
            "total_steps": 200,
            "learning_starts": 20,
            "train_freq": 4,
            "target_update_interval": 20,
            "batch_size": 16,
            "buffer_size": 500,
            "hidden_sizes": [32, 32],
            "eps_decay_steps": 100,
            "save_every": 100,
            "eval_every": 100,
            "eval_episodes": 2,
            "max_steps": 200,
            "log_dir": str(tmp_path),
            "device": "cpu",
            "run_name": "smoke",
        }
    )
    summary = train(cfg)

    run_dir = summary["run_dir"]
    assert os.path.isdir(run_dir)
    # 配置快照
    assert os.path.exists(os.path.join(run_dir, "config.snapshot.yaml"))
    # 周期检查点 + best
    assert os.path.exists(os.path.join(run_dir, "ckpt_100.pt"))
    assert os.path.exists(os.path.join(run_dir, "best.pt"))
    # TensorBoard 事件
    assert any(f.startswith("events.out.tfevents") for f in os.listdir(run_dir))
    assert summary["episodes"] >= 1
