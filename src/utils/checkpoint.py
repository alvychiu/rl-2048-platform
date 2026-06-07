"""检查点保存 / 加载（periodic + best）。

- save_checkpoint：保存网络 state_dict + 元数据；目录不存在则创建；
  磁盘满 / 不可写时捕获异常并抛出清晰错误（TC-034）。
- load_checkpoint：加载并校验结构兼容性；文件不存在报清晰错误（TC-033/TC-051）。
"""

from __future__ import annotations

import os
from typing import Any

import torch


def save_checkpoint(
    path: str,
    state_dict: dict[str, Any],
    meta: dict[str, Any] | None = None,
) -> str:
    payload = {"state_dict": state_dict, "meta": meta or {}}
    parent = os.path.dirname(path)
    try:
        if parent:
            os.makedirs(parent, exist_ok=True)
        torch.save(payload, path)
    except (OSError, PermissionError) as e:
        raise OSError(f"无法写入检查点到 {path}: {e}") from e
    return path


def load_checkpoint(path: str, map_location: str = "cpu") -> dict[str, Any]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"checkpoint not found: {path}")
    payload = torch.load(path, map_location=map_location)
    if "state_dict" not in payload:
        raise ValueError(f"invalid checkpoint format (no state_dict): {path}")
    return payload


def load_into_agent(agent, path: str, map_location: str = "cpu") -> dict[str, Any]:
    """把检查点加载进 agent；结构不匹配时抛出清晰错误（TC-033）。"""
    payload = load_checkpoint(path, map_location=map_location)
    try:
        agent.load_state_dict(payload["state_dict"])
    except (RuntimeError, KeyError) as e:
        raise ValueError(
            f"检查点与当前网络结构不匹配: {path} ({e})"
        ) from e
    return payload.get("meta", {})
