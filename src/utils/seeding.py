"""统一的随机种子与计算设备工具。

- `set_global_seed` 同时设定 Python `random`、NumPy 与 PyTorch 的种子，
  保证训练/环境演化在相同 seed 下可复现（满足 spec S1/可复现 与 TC-024）。
- `resolve_device` 在 Apple M2 上优先选用 MPS，否则回退 CPU；显式请求
  `cuda` 但不可用时优雅回退（满足 TC-022/TC-023）。
"""

from __future__ import annotations

import random

import numpy as np
import torch


def set_global_seed(seed: int) -> None:
    """设置全局随机种子（random / numpy / torch）。

    Args:
        seed: 非负整数种子。
    """
    if seed < 0:
        raise ValueError(f"seed must be non-negative, got {seed}")
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def resolve_device(requested: str = "auto") -> torch.device:
    """解析计算设备，处理 Apple M2 (MPS) 与不可用设备的回退。

    Args:
        requested: "auto" | "cpu" | "mps" | "cuda"。
            - auto：MPS 可用则用 MPS，否则 CPU。
            - mps/cuda：不可用时打印告警并回退 CPU。

    Returns:
        torch.device 实例。
    """
    requested = (requested or "auto").lower()

    if requested == "cpu":
        return torch.device("cpu")

    mps_ok = torch.backends.mps.is_available()
    cuda_ok = torch.cuda.is_available()

    if requested == "auto":
        if mps_ok:
            return torch.device("mps")
        if cuda_ok:
            return torch.device("cuda")
        return torch.device("cpu")

    if requested == "mps":
        if mps_ok:
            return torch.device("mps")
        print("[warn] MPS unavailable, falling back to cpu")
        return torch.device("cpu")

    if requested == "cuda":
        if cuda_ok:
            return torch.device("cuda")
        print("[warn] CUDA unavailable, falling back to cpu")
        return torch.device("cpu")

    raise ValueError(
        f"unknown device '{requested}', expected one of: auto, cpu, mps, cuda"
    )
