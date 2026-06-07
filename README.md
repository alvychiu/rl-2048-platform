# 2048 RL 训练实验平台（MVP）

用 **2048 游戏**作为训练场景的强化学习实验平台：从零实现的 Gymnasium 环境 + DQN 算法 + TensorBoard 可视化 + 一键启动 + 测试。

> 运行环境：**Apple M2 (ARM64, macOS)**，**Python 3.10.11**，PyTorch 走 CPU/MPS（无 CUDA）。

---

## 快速开始（5 分钟内可复现）

### 1. 安装依赖
```bash
make install
# 等价于：python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

### 2. 训练（quick 配置，分钟级验证管线）
```bash
make train
# 等价于：.venv/bin/python -m src.train.train --config configs/quick.yaml
```
输出示例：
```
[cfg ] device=mps | seed=42 | run=runs/2026-06-07_12-16-35_quick
[done] episodes=14 best_median=4.0 elapsed=44.0s
```

### 3. 查看训练曲线（TensorBoard）
```bash
make board          # 打开 http://localhost:6006
# 端口占用时：make board PORT=6007
```

### 4. 评估 + 随机基线对比（判定智能性 S2）
```bash
make eval CKPT=runs/<your-run-id>/best.pt HIDDEN="128 128"
```
> `HIDDEN` 必须与训练配置的 `hidden_sizes` 一致（quick=128 128，full=256 256）。

### 5. 运行测试
```bash
make test           # pytest，约 60+ 用例
```

### 追求效果（达标 max-tile 中位数 ≥ 512）
```bash
make train CONFIG=configs/full.yaml   # 300k 步，M2 上约数十分钟~2 小时
```

---

## 目录结构
```
src/
├── env/      2048 棋盘内核 (board.py) + Gymnasium 封装 (game_2048_env.py)
├── agents/   DQN 网络 (network.py) + 智能体 (dqn.py)
├── train/    配置 (config.py) + 回放 (replay_buffer.py) + 训练主循环 (train.py)
├── eval/     评估 + 随机基线 (evaluate.py)
└── utils/    seed/device (seeding.py) + 记录器 (logger.py) + 检查点 (checkpoint.py)
configs/      quick.yaml / full.yaml
tests/        单测 + 训练冒烟测试
runs/         实验产物（自动生成：配置快照/曲线/检查点/日志）
```

## 设计要点
- **环境**：从零实现 2048（移动/合并/计分/生成/终局），符合新版 **gymnasium** 接口（`reset`/`step`/`render`，`step` 返回 5 元组）；观测为 log2 归一化 4×4；`action_space=Discrete(4)`；非法移动给惩罚并在 `info["illegal"]` 标注。
- **算法**：DQN（经验回放 + 目标网络 + ε-greedy 线性衰减），超参由 YAML 管理。
- **实验记录**：每次训练生成唯一 `runs/<时间戳>_<name>/` 目录，含配置快照、TensorBoard 指标（reward/max_tile/loss/eps/eval）、周期检查点与 best 检查点。
- **可复现**：统一 seed（random/numpy/torch）+ gymnasium 注入 RNG。

## Docker（arm64）
```bash
docker build -t rl-2048 .
docker run --rm -v "$PWD/runs:/app/runs" rl-2048   # 容器内用 CPU 跑 quick 训练
```

---

## 研发流程（G0 → G4 门控体系）
本项目遵循 **AI 执行、Human 决策** 的门控研发流程，全过程文档位于 `artifacts/`：

| Gate | 产物 |
| ---- | ---- |
| G0 需求 | `artifacts/specifications/spec.md` |
| G1 故事/用例 | `artifacts/stories/stories.md`、`artifacts/testcases/testcases.md` |
| G2 任务规划 | `artifacts/planning/tasks.md` |
| G2.5 原型 | `artifacts/prototype/prototype.md` |
| G3 开发 | `src/`（一次一个 Task，逐 Task 验证） |
| G3.5 评审 | `artifacts/reviews/review.md` |
| G4 验收 | `artifacts/acceptance/acceptance.md` |

门控规则与各阶段 Skill 见 `.cursor/`（`rules/`、`skills/`、`templates/`）。

## 开源引用来源
本项目从零实现 2048 环境与 DQN，未直接复制第三方代码。使用的开源库：
- [Gymnasium](https://github.com/Farama-Foundation/Gymnasium)（环境接口规范，标准 RL API）
- [PyTorch](https://github.com/pytorch/pytorch)（深度学习框架，DQN 网络与训练）
- [TensorBoard](https://github.com/tensorflow/tensorboard)（训练可视化）
- NumPy / PyYAML / pytest（数值计算 / 配置解析 / 测试）

2048 游戏规则参考公开通用规则（4×4 棋盘，相同方块合并，2 占 90% / 4 占 10%）。
