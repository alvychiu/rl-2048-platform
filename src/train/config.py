"""训练配置：从 YAML 加载并做轻量校验（dataclass，不引入重依赖）。

校验策略（满足 TC-015~TC-018）：
- 必填字段缺失 -> 抛 KeyError/ValueError 并指明字段。
- 字段类型错误（如 lr="abc"） -> 抛 TypeError/ValueError 并指明字段。
- 文件不存在 / 无读权限 -> open() 自然抛 FileNotFoundError / PermissionError。
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Any

import yaml

# 必填字段：缺失即拒绝启动。
REQUIRED_FIELDS = ("total_steps",)


@dataclass
class Config:
    # 环境
    max_steps: int = 5000
    illegal_penalty: float = -1.0
    merge_reward_scale: float = 1.0
    reward_empty_coef: float = 0.0
    reward_new_max_bonus: float = 0.0
    reward_milestones: dict[int, float] = field(default_factory=dict)
    reward_structure_coef: float = 0.0
    reward_structure_corner: float = 2.0
    reward_structure_monotonicity: float = 0.3
    reward_structure_smoothness: float = 0.05
    reward_structure_corner_log_scale: bool = True
    reward_structure_corner_min_tile: int = 0
    reward_high_tile_coef: float = 0.0
    reward_high_tile_min: int = 256
    reward_snake_coef: float = 0.0
    reward_snake_corner: str = "bottom-left"
    reward_snake_ratio: float = 0.7
    discouraged_action: int = -1
    discouraged_action_penalty: float = 0.0

    # 训练总量
    total_steps: int = 20000
    learning_starts: int = 1000
    train_freq: int = 4
    target_update_interval: int = 1000

    # DQN 超参
    lr: float = 1e-3
    gamma: float = 0.99
    batch_size: int = 128
    buffer_size: int = 50000
    hidden_sizes: list[int] = field(default_factory=lambda: [256, 256])
    grad_clip_max_norm: float = 0.0

    # ε-greedy 探索
    eps_start: float = 1.0
    eps_end: float = 0.05
    eps_decay_steps: int = 10000

    # 记录 / 评估 / 检查点
    log_dir: str = "runs"
    save_every: int = 5000
    eval_every: int = 5000
    eval_episodes: int = 20

    # 运行
    seed: int = 42
    device: str = "auto"
    run_name: str = ""

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        for f in fields(self):
            value = getattr(self, f.name)
            expected = f.type
            if f.name == "hidden_sizes":
                if not isinstance(value, list) or not all(
                    isinstance(x, int) for x in value
                ):
                    raise TypeError("config field 'hidden_sizes' must be list[int]")
                continue
            if f.name in (
                "reward_structure_corner_log_scale",
            ):
                if not isinstance(value, bool):
                    raise TypeError(f"config field '{f.name}' must be bool")
                continue
            if f.name == "reward_milestones":
                if not isinstance(value, dict):
                    raise TypeError(
                        "config field 'reward_milestones' must be dict[int, float]"
                    )
                normalized: dict[int, float] = {}
                for k, v in value.items():
                    if isinstance(k, bool) or not isinstance(k, int):
                        raise TypeError(
                            "config field 'reward_milestones' keys must be int"
                        )
                    if isinstance(v, bool) or not isinstance(v, (int, float)):
                        raise TypeError(
                            "config field 'reward_milestones' values must be float"
                        )
                    normalized[int(k)] = float(v)
                setattr(self, f.name, normalized)
                continue
            # 解析注解（dataclass 下 f.type 可能是字符串）
            if expected in ("int", int):
                if isinstance(value, bool) or not isinstance(value, int):
                    raise TypeError(
                        f"config field '{f.name}' must be int, got {value!r}"
                    )
            elif expected in ("float", float):
                # 允许 int 自动提升为 float
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    raise TypeError(
                        f"config field '{f.name}' must be float, got {value!r}"
                    )
                setattr(self, f.name, float(value))
            elif expected in ("str", str):
                if not isinstance(value, str):
                    raise TypeError(
                        f"config field '{f.name}' must be str, got {value!r}"
                    )

        # 取值范围校验
        if self.total_steps <= 0:
            raise ValueError("total_steps must be > 0")
        if not (0.0 <= self.gamma <= 1.0):
            raise ValueError("gamma must be in [0, 1]")
        if self.lr <= 0:
            raise ValueError("lr must be > 0")
        if self.batch_size <= 0:
            raise ValueError("batch_size must be > 0")
        if self.device not in ("auto", "cpu", "mps", "cuda"):
            raise ValueError(
                f"device must be one of auto/cpu/mps/cuda, got {self.device!r}"
            )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Config":
        if data is None:
            data = {}
        known = {f.name for f in fields(cls)}
        unknown = set(data) - known
        if unknown:
            raise ValueError(f"unknown config keys: {sorted(unknown)}")
        for req in REQUIRED_FIELDS:
            if req not in data:
                raise ValueError(f"missing required config field: '{req}'")
        return cls(**data)

    @classmethod
    def from_yaml(cls, path: str) -> "Config":
        with open(path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        return cls.from_dict(data or {})

    def to_dict(self) -> dict[str, Any]:
        return {f.name: getattr(self, f.name) for f in fields(self)}
