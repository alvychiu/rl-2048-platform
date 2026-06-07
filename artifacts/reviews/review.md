# 代码评审 (Review) — 2048 RL 训练实验平台 MVP

> 阶段：G3.5 Review ｜ 评审对象：src/ 变更（T-01~T-19）｜ 状态：Draft（待 Human 决策）
> 日期：2026-06-07 ｜ 评审人：AI（执行）+ 唯一工程师（决策）
> 说明：T-20（调参/训练）尚未完成，本次评审范围为 T-01~T-19 已交付代码。T-20 完成后需做增量评审。

## 评审范围
- 关联 Task：T-01 ~ T-19
- 变更文件：src/env/{board.py, game_2048_env.py, __init__.py}、src/agents/{network.py, dqn.py}、
  src/train/{config.py, replay_buffer.py, train.py}、src/eval/evaluate.py、
  src/utils/{seeding.py, logger.py, checkpoint.py}；配套 tests/、configs/、Makefile、Dockerfile、README.md
- 自动化测试：`pytest` 65 passed

## 风险汇总
| 等级   | 数量 |
| ------ | ---- |
| High   | 1    |
| Medium | 3    |
| Low    | 4    |

> ⚠️ 存在 1 个 High 风险，按规则**禁止进入 G4**，需回 G3 修复（恰好由 T-20 承接）。

---

## 评审发现明细

| 编号 | 维度 | 文件:位置 | 问题描述 | 风险等级 | 修复建议 |
| ---- | ---- | -------- | -------- | -------- | -------- |
| RV-1 | Bug/逻辑 | src/agents/dqn.py `act_greedy`；src/eval/evaluate.py、src/train.py 评估循环 | 贪心策略可反复选择**非法动作**（棋盘不变），episode 不终止而空转至 `truncated`，导致评估表现甚至**低于随机基线**（实测 trained median=4 vs random=128）。直接阻碍达成 S2（max-tile 中位数≥512）。 | **High** | 引入**动作屏蔽（action masking）**：基于 `can_move` 计算各方向合法性，贪心/ε-greedy 时仅在合法动作中选择；或对非法动作给更强惩罚并在选择层过滤。T-20 必须解决。 |
| RV-2 | 安全 | src/utils/checkpoint.py `load_checkpoint` | `torch.load` 未设 `weights_only=True`，加载不可信检查点存在反序列化（pickle）代码执行风险。 | Medium | 改为 `torch.load(path, map_location=..., weights_only=True)`（torch 2.2 支持），仅加载张量。 |
| RV-3 | 可维护性/易用 | src/eval/evaluate.py `--hidden` | 评估需手动传入与训练一致的 `hidden_sizes`，不一致即触发结构不匹配错误，易用性差、易错。 | Medium | 在检查点 meta 中保存网络结构（hidden_sizes 等），评估时自动读取重建，去除手填 `--hidden`。 |
| RV-4 | 边界 | src/utils/logger.py `__init__` | run 目录时间戳精确到秒，`makedirs(exist_ok=False)`；同名配置在同一秒内连续启动两次会 `FileExistsError` 崩溃。 | Medium | 时间戳加毫秒/进程号，或冲突时自动追加序号重试。 |
| RV-5 | 可维护性 | src/train/train.py `evaluate_agent` vs src/eval/evaluate.py `_run_episodes` | 两处“跑 N 局贪心评估”逻辑重复，存在分叉维护风险。 | Low | 抽取公共 `rollout/eval` 工具到 src/eval 或 src/utils，train 与 evaluate 共用。 |
| RV-6 | 性能 | src/env/game_2048_env.py `step` → `is_game_over`→`can_move` | 每个 env.step 额外执行最多 4 次方向移动做终局判定；长训练（数十万步）有常数级开销。 | Low | 可缓存或在 spawn 后仅在棋盘满时判定；当前 4×4 规模影响有限，可暂不优化。 |
| RV-7 | 可复现 | src/agents/dqn.py（MPS 设备） | seed 可复现性单测在 CPU 验证；MPS 上浮点/算子顺序可能导致非严格可复现。 | Low | 文档注明“严格可复现以 CPU 为准”；或对可复现性需求强的实验使用 device=cpu。 |
| RV-8 | 可维护性 | src/train/config.py `_validate` | 依赖 dataclass `f.type` 可能为字符串注解，类型判断用字符串/类型双匹配，较隐晦。 | Low | 可改用 `typing.get_type_hints` 显式解析，增强健壮性与可读性。 |

---

## 维度自检
- [x] Bug（逻辑/错误处理/分支）—— 发现 RV-1（High）。
- [x] 安全（注入/鉴权/越权/敏感信息/依赖漏洞）—— 发现 RV-2；YAML 已用 safe_load（良好）。
- [x] 性能（N+1/循环/内存/IO）—— 发现 RV-6（Low）。
- [x] 可维护性（可读性/重复/命名/耦合）—— 发现 RV-3/RV-5/RV-8。
- [x] 边界情况（空值/并发/超时/极限输入）—— 发现 RV-4；spawn 满盘、未 reset、非法动作等已有处理。

## 亮点（正向确认）
- 模块解耦清晰（env/agents/train/eval/utils），代码只落 `src/`，符合规则。
- 配置用 dataclass 轻量校验、网络用 MLP、移动逻辑旋转复用——无过度设计。
- 测试覆盖到位（65 passed），含训练冒烟与端到端真实跑通。
- 错误处理良好：配置校验、检查点不存在/结构不匹配、设备回退均有清晰报错。

## 结论
- 是否存在 High 风险：**是（RV-1）**。
- 建议：**REJECT，回 G3 修复**。RV-1 由 **T-20** 承接（动作屏蔽 + 调参），建议同时一并修复 RV-2/RV-3/RV-4 三个 Medium。修复后重新跑测试并做增量 Review，再进入 G4。

## Human Gate 记录
- 决策结果：APPROVE / REJECT（待填）
- 决策人 / 日期：
- 备注：
