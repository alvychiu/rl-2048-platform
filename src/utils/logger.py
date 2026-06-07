"""实验记录器：按 run-id 建独立目录，写配置快照 + TensorBoard 标量。

每次实验目录形如 runs/2026-06-07_11-50_<run_name>/，包含：
- config.snapshot.yaml  配置快照
- events.out.tfevents.* TensorBoard 标量（reward/max_tile/ep_len/loss/eps）
- train.log             文本日志
不同实验目录唯一、互不覆盖（TC-027）。
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any

import yaml
from torch.utils.tensorboard import SummaryWriter


class ExperimentLogger:
    def __init__(self, log_root: str, run_name: str = "", config: dict | None = None):
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        suffix = f"_{run_name}" if run_name else ""
        base = os.path.join(log_root, f"{ts}{suffix}")
        # RV-4：同秒同名冲突时自动追加序号，避免 FileExistsError 崩溃。
        run_dir = base
        n = 2
        while os.path.exists(run_dir):
            run_dir = f"{base}-{n}"
            n += 1
        self.run_dir = run_dir
        os.makedirs(self.run_dir, exist_ok=False)

        self.writer = SummaryWriter(log_dir=self.run_dir)
        self._log_path = os.path.join(self.run_dir, "train.log")

        if config is not None:
            self.save_config(config)

    def save_config(self, config: dict[str, Any]) -> str:
        path = os.path.join(self.run_dir, "config.snapshot.yaml")
        with open(path, "w", encoding="utf-8") as fh:
            yaml.safe_dump(config, fh, sort_keys=True, allow_unicode=True)
        return path

    def log_scalar(self, tag: str, value: float, step: int) -> None:
        self.writer.add_scalar(tag, value, step)

    def log_scalars(self, metrics: dict[str, float], step: int) -> None:
        for tag, value in metrics.items():
            self.writer.add_scalar(tag, value, step)

    def log_text(self, line: str) -> None:
        with open(self._log_path, "a", encoding="utf-8") as fh:
            fh.write(line.rstrip("\n") + "\n")

    def close(self) -> None:
        self.writer.flush()
        self.writer.close()

    def __enter__(self) -> "ExperimentLogger":
        return self

    def __exit__(self, *exc) -> None:
        self.close()
