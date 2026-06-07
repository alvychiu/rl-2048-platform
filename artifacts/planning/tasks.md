# 开发任务 (Tasks) — 2048 RL 训练实验平台 MVP

> 阶段：G2 Planning ｜ 来源：spec.md, stories.md（均已 APPROVE）｜ 状态：✅ Approved（2026-06-07）
> 环境：Apple M2（CPU/MPS）、Python 3.10.11、PyTorch(CPU/MPS)、gymnasium、tensorboard
> 状态字段：TODO / DOING / DONE（G3 一次只推进一个 Task）

## 目标目录结构（代码仅写入 src/）
```
src/
├── env/            # 2048 棋盘内核 + Gymnasium 封装
│   ├── board.py
│   └── game_2048_env.py
├── agents/         # DQN 网络与智能体
│   ├── network.py
│   └── dqn.py
├── train/          # 训练循环、回放、配置
│   ├── replay_buffer.py
│   ├── config.py
│   └── train.py
├── eval/           # 评估与基线
│   └── evaluate.py
├── utils/          # 日志/记录/检查点/seed
│   ├── logger.py
│   ├── checkpoint.py
│   └── seeding.py
configs/            # YAML 配置（quick / full）
tests/              # 测试
```
> 说明：`configs/`、`tests/`、`Dockerfile`、`Makefile`、`requirements.txt`、`README.md` 为项目级必要文件；业务代码集中在 `src/`。

---

## 任务总览

| Task ID | 任务名称 | 关联Story | 依赖 | 复杂度 | 风险 | 状态 |
| ------- | -------- | --------- | ---- | ------ | ---- | ---- |
| T-01 | 项目骨架与依赖锁定 | US-09,US-10 | - | S | Low | ✅ DONE |
| T-02 | seed 与工具基础 | US-01,US-05 | T-01 | S | Low | ✅ DONE |
| T-03 | 2048 棋盘内核 | US-01 | T-01 | M | Medium | ✅ DONE |
| T-04 | 棋盘内核单测 | US-01,US-10 | T-03 | S | Low | ✅ DONE |
| T-05 | Gymnasium 环境封装 | US-02 | T-03 | M | Medium | ✅ DONE |
| T-06 | 环境接口单测 | US-02,US-10 | T-05 | S | Low | ✅ DONE |
| T-07 | 文本渲染 render | US-03 | T-05 | S | Low | ✅ DONE |
| T-08 | YAML 配置加载与校验 | US-04 | T-01 | M | Medium | ✅ DONE |
| T-09 | 经验回放缓冲区 | US-05 | T-02 | S | Low | ✅ DONE |
| T-10 | DQN 网络结构 | US-05 | T-02 | S | Low | ✅ DONE |
| T-11 | DQN 智能体(动作/学习/目标网络) | US-05 | T-09,T-10 | M | Medium | ✅ DONE |
| T-12 | 实验记录器(配置快照+TB指标) | US-06 | T-08 | M | Medium | ✅ DONE |
| T-13 | 检查点保存/加载(periodic+best) | US-07 | T-01 | S | Medium | ✅ DONE |
| T-14 | 训练主循环(串联环境/DQN/记录/检查点) | US-05,US-06,US-07 | T-05,T-08,T-11,T-12,T-13 | L | High | ✅ DONE |
| T-15 | 训练冒烟测试 | US-10 | T-14 | S | Medium | ✅ DONE |
| T-16 | 评估脚本与随机基线对比 | US-11 | T-13,T-05 | M | Medium | ✅ DONE |
| T-17 | 一键启动(Makefile/脚本: train/eval/board) | US-09 | T-14,T-16 | S | Low | ✅ DONE |
| T-18 | Dockerfile(arm64) | US-09 | T-17 | M | Medium | ⚠️ DONE(构建待验证) |
| T-19 | README(5分钟复现+开源引用) | US-09 | T-17 | S | Medium | ✅ DONE |
| T-20 | quick/full 配置调参与收敛验证 | US-05,US-11 | T-14,T-16 | L | High | 🔄 DOING(v4调参) |
| T-21 | 2048 GUI（pygame 手动+AI演示） | US-12 | T-05,T-11,T-13 | M | Medium | ✅ DONE |

> 建议执行顺序（拓扑序）：T-01 → T-02 → T-03 → T-04 → T-05 → T-06 → T-07 → T-08 → T-09 → T-10 → T-11 → T-12 → T-13 → T-14 → T-15 → T-16 → T-17 → T-18 → T-19 → T-20

---

## 任务详情

### T-01 — 项目骨架与依赖锁定
- **关联 Story**：US-09, US-10 ｜ **依赖**：无 ｜ **复杂度**：S ｜ **风险**：Low
- **技术方案**：建立 `src/` 包结构、`configs/`、`tests/`；`requirements.txt` 固定版本（gymnasium、torch CPU/MPS、numpy、tensorboard、pyyaml、pytest）；`pyproject`/`__init__` 使包可导入。
- **DoD**：`pip install -r requirements.txt` 成功；`python -c "import torch,gymnasium"` 通过；目录结构就位。
- **状态**：✅ DONE（2026-06-07）
- **变更文件**：requirements.txt, pyproject.toml, .gitignore, src/__init__.py, src/{env,agents,train,eval,utils}/__init__.py, tests/__init__.py, tests/test_skeleton.py, configs/.gitkeep
- **验证结果**：venv 安装依赖成功；torch 2.2.2 / gymnasium 0.29.1 导入通过；MPS 可用；`pytest` 3 passed。

### T-02 — seed 与工具基础
- **关联 Story**：US-01, US-05 ｜ **依赖**：T-01 ｜ **复杂度**：S ｜ **风险**：Low
- **技术方案**：`utils/seeding.py` 统一设置 random/numpy/torch 种子；提供 device 选择工具（cpu/mps 自动探测）。
- **DoD**：同 seed 下随机序列可复现；device 工具在 M2 返回 mps 或回退 cpu。关联 TC-024, TC-023。
- **状态**：✅ DONE（2026-06-07）
- **变更文件**：src/utils/seeding.py, tests/test_seeding.py
- **验证结果**：pytest 9 passed；seed 对 random/numpy/torch 三者可复现；resolve_device 支持 auto/cpu/mps/cuda 且不可用时优雅回退。

### T-03 — 2048 棋盘内核
- **关联 Story**：US-01 ｜ **依赖**：T-01 ｜ **复杂度**：M ｜ **风险**：Medium
- **技术方案**：`env/board.py` 纯函数式实现：4×4 numpy/list；左/右/上/下移动用"压缩+合并+压缩"统一实现（其余方向用旋转复用）；合并计分；空位生成 2(90%)/4(10%)，注入 RNG 可复现；`can_move`/`is_game_over`。
- **关键取舍**：移动逻辑只实现一个方向 + 旋转复用，避免四份重复代码（非过度设计，是去重）。
- **DoD**：核心函数可被测试覆盖；满足 AC-1~AC-5。关联 TC-001~TC-006。
- **状态**：✅ DONE（2026-06-07）
- **变更文件**：src/env/board.py
- **验证结果**：冒烟测试通过——左移合并 `[2,2,2,2]→[4,4,0,0]`、相邻分别合并 `[4,4,8,8]→[8,16]`、得分正确、非法移动 moved=False、UP/DOWN/RIGHT 方向变换正确、终局判定、spawn 可复现。正式单测见 T-04。

### T-04 — 棋盘内核单测
- **关联 Story**：US-01, US-10 ｜ **依赖**：T-03 ｜ **复杂度**：S ｜ **风险**：Low
- **技术方案**：pytest 覆盖移动/合并(每块只合并一次)/计分/生成/终局/可复现。
- **DoD**：TC-001~TC-006 全绿。
- **状态**：✅ DONE（2026-06-07）｜ **变更文件**：tests/test_board.py｜ **验证**：9 个用例全绿（TC-001~TC-006 + 方向/可复现/终局）。

### T-05 — Gymnasium 环境封装
- **关联 Story**：US-02 ｜ **依赖**：T-03 ｜ **复杂度**：M ｜ **风险**：Medium
- **技术方案**：`env/game_2048_env.py` 继承 `gymnasium.Env`；`action_space=Discrete(4)`；`observation_space` 为 log2 归一化 4×4（Box）；`reset(seed)`→(obs,info)；`step`→5 元组；非法移动 info["illegal"]=True 并给惩罚；步数上限 → truncated。
- **DoD**：满足 AC-1~AC-5；通过 gymnasium API 一致性检查。关联 TC-007~TC-012, TC-046。
- **状态**：✅ DONE（2026-06-07）｜ **变更文件**：src/env/game_2048_env.py, src/env/__init__.py(注册 Game2048-v0)｜ **验证**：见 T-06。

### T-06 — 环境接口单测
- **关联 Story**：US-02, US-10 ｜ **依赖**：T-05 ｜ **复杂度**：S ｜ **风险**：Low
- **技术方案**：pytest 校验 reset/step 返回签名、空间定义、非法动作、truncated、未 reset 报错。
- **DoD**：TC-007~TC-012, TC-046 全绿。
- **状态**：✅ DONE（2026-06-07）｜ **变更文件**：tests/test_env.py｜ **验证**：10 个用例全绿（5 元组、Discrete(4)、归一化观测、非法动作、终局、truncated、未 reset 报错、可复现）。

### T-07 — 文本渲染 render
- **关联 Story**：US-03 ｜ **依赖**：T-05 ｜ **复杂度**：S ｜ **风险**：Low
- **技术方案**：`render(mode="ansi")` 输出对齐的 4×4 文本，空格统一占位。
- **DoD**：TC-013, TC-014 通过。
- **状态**：✅ DONE（2026-06-07）｜ **变更文件**：render 方法在 src/env/game_2048_env.py（render_text），tests/test_render.py｜ **验证**：3 个用例全绿（文本渲染、空盘无数字、无 mode 返回 None）。

### T-08 — YAML 配置加载与校验
- **关联 Story**：US-04 ｜ **依赖**：T-01 ｜ **复杂度**：M ｜ **风险**：Medium
- **技术方案**：`train/config.py` 用 dataclass + pyyaml 加载；做必填项/类型校验，缺失或类型错误抛清晰异常；字段含 lr/gamma/batch/buffer/eps 策略/total_steps/seed/device/save_every/eval_every/log_dir。
- **关键取舍**：用 dataclass 轻量校验，不引入 pydantic 等重依赖（避免过度设计）。
- **DoD**：TC-015~TC-018 通过。
- **状态**：✅ DONE（2026-06-07）｜ **变更文件**：src/train/config.py, configs/quick.yaml, configs/full.yaml, tests/test_config.py｜ **验证**：8 个用例全绿（合法加载、缺必填、类型错误、未知键、范围校验、无读权限、bool 拒绝）。

### T-09 — 经验回放缓冲区
- **关联 Story**：US-05 ｜ **依赖**：T-02 ｜ **复杂度**：S ｜ **风险**：Low
- **技术方案**：`train/replay_buffer.py` 定长环形缓冲，`push`/`sample(batch)`；numpy 存储。
- **DoD**：容量滚动、batch 采样正确；TC-020, TC-021。
- **状态**：✅ DONE（2026-06-07）｜ **变更文件**：src/train/replay_buffer.py, tests/test_replay_buffer.py｜ **验证**：5 个用例全绿（push/len、容量滚动、采样形状、超量报错、可复现采样）。

### T-10 — DQN 网络结构
- **关联 Story**：US-05 ｜ **依赖**：T-02 ｜ **复杂度**：S ｜ **风险**：Low
- **技术方案**：`agents/network.py` 小型 MLP（输入 16 维展平/或简单 CNN，MVP 用 MLP），输出 4 个 Q 值；保持轻量以适配 M2。
- **关键取舍**：MVP 选 MLP 而非复杂 CNN，先验证管线（防过度设计）。
- **DoD**：前向输出形状正确。
- **状态**：✅ DONE（2026-06-07）｜ **变更文件**：src/agents/network.py, tests/test_network.py｜ **验证**：4 个用例全绿（展平输入/棋盘输入输出 (B,4)、参数非空、自定义隐层）。

### T-11 — DQN 智能体
- **关联 Story**：US-05 ｜ **依赖**：T-09, T-10 ｜ **复杂度**：M ｜ **风险**：Medium
- **技术方案**：`agents/dqn.py`：ε-greedy 选动作、从回放采样计算 TD loss、目标网络周期同步、优化器步进；device 适配 cpu/mps。
- **DoD**：单步 learn 不报错、loss 可下降；TC-022, TC-023。
- **状态**：✅ DONE（2026-06-07）｜ **变更文件**：src/agents/dqn.py, tests/test_dqn.py｜ **验证**：5 用例全绿（合法动作、ε 衰减、learn 返回 loss、目标网络同步、state_dict 往返）。

### T-12 — 实验记录器
- **关联 Story**：US-06 ｜ **依赖**：T-08 ｜ **复杂度**：M ｜ **风险**：Medium
- **技术方案**：`utils/logger.py`：按 run-id(时间戳) 建实验目录；写配置快照(yaml/json)；用 `torch.utils.tensorboard.SummaryWriter` 记录 reward/max-tile/ep_len/loss/eps。
- **DoD**：TC-025~TC-027, TC-029；目录唯一不覆盖。
- **状态**：✅ DONE（2026-06-07）｜ **变更文件**：src/utils/logger.py, tests/test_logger_checkpoint.py｜ **验证**：配置快照、TB 标量、run 目录唯一性用例全绿。

### T-13 — 检查点保存/加载
- **关联 Story**：US-07 ｜ **依赖**：T-01 ｜ **复杂度**：S ｜ **风险**：Medium
- **技术方案**：`utils/checkpoint.py`：保存网络 state_dict + 元数据；periodic + best；加载时校验结构；目录不可写/磁盘满时捕获异常并提示。
- **DoD**：TC-030~TC-034。
- **状态**：✅ DONE（2026-06-07）｜ **变更文件**：src/utils/checkpoint.py, tests/test_logger_checkpoint.py｜ **验证**：保存/加载、往返、结构不匹配报错、文件不存在报错用例全绿。

### T-14 — 训练主循环
- **关联 Story**：US-05, US-06, US-07 ｜ **依赖**：T-05,T-08,T-11,T-12,T-13 ｜ **复杂度**：L ｜ **风险**：**High**
- **技术方案**：`train/train.py`：读配置→建环境/Agent/Logger→交互采样→存回放→学习→周期评估→记录→存检查点；支持 quick/full；CLI 入口 `python -m src.train.train --config configs/quick.yaml`。
- **风险点**：串联多模块，最易出集成 bug；先用 quick 跑通管线再追效果。
- **DoD**：TC-019, TC-024；quick 配置完整跑通。
- **状态**：✅ DONE（2026-06-07）｜ **变更文件**：src/train/train.py｜ **验证**：`python -m src.train.train --config configs/quick.yaml` 端到端跑通——device=mps，44s，14 episodes，产出 config 快照 + ckpt_1000/2000/3000 + best.pt + tfevents + train.log。

### T-15 — 训练冒烟测试
- **关联 Story**：US-10 ｜ **依赖**：T-14 ｜ **复杂度**：S ｜ **风险**：Medium
- **技术方案**：pytest 用极小 total_steps 跑通 train→记录→检查点；断言产物存在。
- **DoD**：TC-045 通过。
- **状态**：✅ DONE（2026-06-07）｜ **变更文件**：tests/test_train_smoke.py｜ **验证**：极小步数(200)冒烟跑通 train→记录→检查点，断言 run 目录/配置快照/ckpt/best/tfevents 均存在。全套 61 passed。

### T-16 — 评估脚本与随机基线
- **关联 Story**：US-11 ｜ **依赖**：T-13, T-05 ｜ **复杂度**：M ｜ **风险**：Medium
- **技术方案**：`eval/evaluate.py`：加载检查点跑 N 局，统计 max-tile/score 分布(中位数/均值/最大)；提供随机策略基线；检查点不存在报清晰错误。
- **DoD**：TC-048~TC-051。
- **状态**：✅ DONE（2026-06-07）｜ **变更文件**：src/eval/evaluate.py, tests/test_evaluate.py｜ **验证**：4 用例全绿；真实 quick best.pt 评估正常输出（trained vs random 对比表 + S2 判定）。注：quick 欠训练模型 median=4 未达标属预期，效果由 T-20 达成。

### T-17 — 一键启动
- **关联 Story**：US-09 ｜ **依赖**：T-14, T-16 ｜ **复杂度**：S ｜ **风险**：Low
- **技术方案**：`Makefile`/脚本提供 `train`/`eval`/`board`(tensorboard --logdir) 目标；端口占用提示。
- **DoD**：TC-040, TC-035~TC-038。
- **状态**：✅ DONE（2026-06-07）｜ **变更文件**：Makefile｜ **验证**：提供 install/train/eval/board/test/clean 目标；train/eval/test 经实际命令验证可用；board 调用 tensorboard。

### T-18 — Dockerfile(arm64)
- **关联 Story**：US-09 ｜ **依赖**：T-17 ｜ **复杂度**：M ｜ **风险**：Medium
- **技术方案**：基于 arm64 兼容 python:3.10-slim；装依赖；默认入口跑 quick 训练。
- **DoD**：TC-042, TC-043（构建并跑通 quick）。
- **状态**：⚠️ DONE-代码（2026-06-07）｜ **变更文件**：Dockerfile（python:3.10-slim arm64 兼容，装依赖+拷贝代码，默认跑 quick）｜ **待验证**：本机未安装 docker，`docker build`/`docker run`（TC-042/043）无法执行，留待 G4 验收或有 docker 环境时确认。容器内 device=auto 自动解析为 cpu。

### T-19 — README
- **关联 Story**：US-09 ｜ **依赖**：T-17 ｜ **复杂度**：S ｜ **风险**：Medium
- **技术方案**：5 分钟复现步骤(安装→train→board→eval)；标注开源引用来源（gymnasium、PyTorch 等）；说明 M2/MPS。
- **DoD**：TC-039, TC-041；按步骤可复现。
- **状态**：✅ DONE（2026-06-07）｜ **变更文件**：README.md（重写为项目运行说明）｜ **内容**：5 分钟复现步骤(install→train→board→eval→test)、目录结构、设计要点、Docker 用法、G0-G4 流程指引、开源引用来源(gymnasium/PyTorch/TensorBoard 等)、M2/MPS 说明。

### T-20 — quick/full 配置调参与收敛验证
- **关联 Story**：US-05, US-11 ｜ **依赖**：T-14, T-16 ｜ **复杂度**：L ｜ **风险**：**High**
- **技术方案**：调 reward 设计/网络/ε 衰减/学习率；quick 验证管线，full 追求 max-tile 中位数≥512；记录基线对比。
- **风险点**：收敛不确定性最高；预留多轮调参，必要时调整 reward 塑形(A-7)。
- **DoD**：S2 达标（max-tile 中位数≥512）或给出充分的趋势证据 + 复盘。关联 TC-048。
- **状态**：⚠️ DONE — v2 调参 + full_v2 600k 训练完成，S2 仍未达标（2026-06-07）
- **v1 训练结果**：`runs/2026-06-07_13-57-22_full`，250k 步，best_median=256；正式评估 median=128, max=512，**S2 FAIL**。
- **v2 代码改动**：
  - `merge_reward_scale` 合并得分缩放（默认 1.0，v2 用 0.05）
  - `reward_milestones` 里程碑奖励（128/256/512/1024）
  - DQN `learn()` TD 目标对 next 合法动作做 masking
  - replay buffer 存储 `next_legal_mask`
- **v2 配置**：`configs/full_v2_smoke.yaml`（50k）、`configs/full_v2.yaml`（600k）
- **烟雾结果** `runs/2026-06-07_14-43-32_full_v2_smoke`：50k 步，108s，418 ep；best_median=128；训练中出现 max_tile=256；正式评估 median=64, max=512。**阶段1未过线（median>192）**，但 max 达 512 有信号。
- **人类决策**：✅ RUN_FULL（2026-06-07）
- **full_v2 训练结果** `runs/2026-06-07_14-48-35_full_v2`：600k 步，MPS，1333s（~22min），4880 ep；step 550k 更新 best_median=**256**；训练末期单局 max_tile=256。
- **正式评估(100局)**：trained median=**128**, max=**512**, score_mean=2206；random median=128；**S2 FAIL**；**1024 未出现**。
- **v2 复盘**：较 v1 训练期 best_median 持平(256)，长训练未带来评估 median 提升；偶发 512 依旧。
- **v3 结构奖励**（2026-06-07）：`board.structure_score`（角落锚定+单调性+平滑度），`reward_structure_coef` 按结构分增量塑形；配置 `full_v3.yaml` / `full_v3_smoke.yaml`。
- **full_v3 训练结果** `runs/2026-06-07_15-27-39_full_v3`：600k 步，1427s；best_median=128（退步）；正式评估 median=128, max=512，**S2 FAIL**。
- **v4 配置**（2026-06-07）：`full_v4.yaml`（800k）— 快 exploitation(eps→0.01@160k)、强推512(里程碑60+high_tile)、弱化corner(log关闭+min128+权重0.25)、稳定训练(lr↓/batch↑/grad_clip)、后期空间(gamma0.998/max_steps15k)。
- **人类决策**：✅ 启动 full_v4 训练（2026-06-07）
- **full_v4 训练结果** `runs/2026-06-07_16-06-54_full_v4`：800k 步，2292s，5731 ep；best_median=128（仍未提升）。
- **v5 蛇形策略**（2026-06-07）：将「角落+蛇形+方向纪律」人工策略编码进奖励——
  - `board.snake_gradient_score`：固定左下角，蛇形几何递减权重势能（主导塑形项）
  - 方向纪律：`discouraged_action=0(UP)` + `discouraged_action_penalty`，抑制误触向上打乱布局
  - 配置 `full_v5.yaml`（800k）/ `full_v5_smoke.yaml`（50k）
  - 烟雾 `runs/2026-06-07_16-57-24_full_v5_smoke`：50k 步，192s，单局频繁到 256；启动 full_v5 完整训练。

### T-21 — 2048 GUI（pygame 手动游玩 + AI 演示）
- **关联 Story**：US-12 ｜ **依赖**：T-05, T-11, T-13 ｜ **复杂度**：M ｜ **风险**：Medium
- **技术方案**：`src/gui/` 用 pygame 渲染棋盘；`key_to_action` 映射方向键/WASD；`make play` 手动模式；`make play CKPT=...` 加载检查点 AI 演示（动作屏蔽）；经典配色无复杂动画。
- **DoD**：TC-052~057；`make play` 可启动；README 已更新。
- **状态**：✅ DONE（2026-06-07）
- **变更文件**：src/gui/{renderer.py,play.py}, requirements.txt(pygame), Makefile(play), tests/test_gui.py, README.md
- **验证结果**：74 passed；`make play` / `make play CKPT=...` 入口就绪。

---

## 过度设计自检
- [x] 未引入当前不需要的抽象：环境/算法直接面向 2048+DQN，未做"通用算法插件框架"。
- [x] 未为假想需求预留扩展点：不实现多算法注册表、不做分布式接口（属非目标范围）。
- [x] 遵循 YAGNI/KISS：网络用 MLP、配置用 dataclass、可视化复用 TensorBoard、移动逻辑旋转复用。
- [x] 第二种算法(PPO)、GUI 渲染、训练 resume 均**不在本期**，列为未来增强。

## 关键风险（High）跟踪
- **T-14 集成**：分步串联 + quick 冒烟先行降低集成风险。
- **T-20 收敛**：reward 设计 + obs 归一化 + 多轮调参，先小规模验证。

## Human Gate 记录
- 是否存在过度设计：否（人类确认）
- 决策结果：✅ **APPROVE**
- 决策人 / 日期：唯一工程师 / 2026-06-07
