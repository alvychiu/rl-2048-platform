# 用户故事 (Stories) — 2048 RL 训练实验平台 MVP

> 阶段：G1 Story-Test ｜ 来源：artifacts/specifications/spec.md（已 APPROVE）｜ 状态：✅ Approved（2026-06-07）
> 角色说明：本项目为单工程师使用的本地 RL 实验工具，主要角色为 **研究者/工程师（User）**。

## Epic 列表
| Epic ID | Epic 名称 | 业务目标 | 关联需求 |
| ------- | --------- | -------- | -------- |
| EP-01   | 2048 游戏环境（Gymnasium） | 从零实现符合标准接口的可训练环境 | FR-1, FR-2, FR-10 |
| EP-02   | DQN 训练与配置管理 | 用 YAML 驱动可复现的 DQN 训练 | FR-3, FR-4 |
| EP-03   | 实验记录（配置/指标/检查点） | 训练全过程自动留痕、可追溯 | FR-5 |
| EP-04   | 可视化与实验对比（TensorBoard） | 查看训练曲线并跨实验对比 | FR-6 |
| EP-05   | 一键启动与可复现 | 5 分钟内拉起训练/评估/可视化 | FR-7 |
| EP-06   | 测试与正确性 | 以测试证明系统正确 | FR-9 |
| EP-07   | 评估与智能性验证 | 量化证明 Agent 变聪明（基线对比） | FR-8, S2 |

---

## EP-01 2048 游戏环境

### Story: US-01 — 2048 棋盘核心逻辑
- **所属 Epic**：EP-01 ｜ **优先级**：P0
- **故事**：作为研究者，我想要一个正确实现 2048 规则（移动/合并/计分/生成/终局）的棋盘内核，以便训练数据可信。
- **验收标准**：
  - **AC-1**：Given 一行 `[2,2,0,0]`，When 向左移动，Then 结果为 `[4,0,0,0]` 且本步得分 +4。
  - **AC-2**：Given 一行 `[2,2,2,2]`，When 向左移动，Then 结果为 `[4,4,0,0]`（一次移动每个方块只合并一次）。
  - **AC-3**：Given 任意有效移动后，When 棋盘有空位，Then 在空位随机生成一个 2(90%) 或 4(10%) 的新方块。
  - **AC-4**：Given 棋盘满且四方向均不可合并，When 判定终局，Then `done/terminated = True`。
  - **AC-5**：Given 固定随机种子，When 重复执行相同动作序列，Then 棋盘演化完全一致（可复现）。
- **关联测试用例**：TC-001 ~ TC-006

### Story: US-02 — Gymnasium 标准接口封装
- **所属 Epic**：EP-01 ｜ **优先级**：P0
- **故事**：作为研究者，我想要环境符合新版 gymnasium 接口（`reset`/`step`/`render`），以便复用标准 RL 工具链。
- **验收标准**：
  - **AC-1**：Given 创建环境，When 调用 `reset(seed=k)`，Then 返回 `(obs, info)`，`obs` 形状符合 `observation_space`。
  - **AC-2**：Given 已 reset，When 调用 `step(action)`，Then 返回 5 元组 `(obs, reward, terminated, truncated, info)`。
  - **AC-3**：Given `action_space`，When 检查，Then 为 `Discrete(4)`（上/下/左/右）。
  - **AC-4**：Given 非法移动（该方向不可动），When `step`，Then 棋盘不变、`info["illegal"]=True`、按设计给惩罚/0 reward。
  - **AC-5**：Given 超过步数上限，When `step`，Then `truncated=True`。
- **关联测试用例**：TC-007 ~ TC-012

### Story: US-03 — 环境渲染
- **所属 Epic**：EP-01 ｜ **优先级**：P1
- **故事**：作为研究者，我想要 `render()` 输出可读的棋盘，以便人工观察对局。
- **验收标准**：
  - **AC-1**：Given 文本渲染模式，When `render()`，Then 输出 4×4 棋盘的可读文本。
  - **AC-2**：Given 空棋盘单元，When 渲染，Then 用统一占位符表示（不报错）。
- **关联测试用例**：TC-013 ~ TC-014

---

## EP-02 DQN 训练与配置管理

### Story: US-04 — YAML 配置管理
- **所属 Epic**：EP-02 ｜ **优先级**：P0
- **故事**：作为研究者，我想要用 YAML 管理全部超参数与实验配置，以便实验可复现、可对比。
- **验收标准**：
  - **AC-1**：Given 一份合法 YAML（含 lr、gamma、batch、buffer、ε 策略、total_steps、seed、device 等），When 加载，Then 配置正确解析为训练参数。
  - **AC-2**：Given 缺少必填项或类型错误的 YAML，When 加载，Then 报出清晰错误并拒绝启动。
  - **AC-3**：Given 提供 quick 与 full 两套配置，When 选择 quick，Then 分钟级跑通训练管线。
- **关联测试用例**：TC-015 ~ TC-018

### Story: US-05 — DQN 训练循环
- **所属 Epic**：EP-02 ｜ **优先级**：P0
- **故事**：作为研究者，我想要可运行的 DQN（经验回放 + 目标网络 + ε-greedy），以便训练出会玩 2048 的 Agent。
- **验收标准**：
  - **AC-1**：Given quick 配置，When 启动训练，Then 训练循环完整跑完且无异常退出。
  - **AC-2**：Given 训练进行中，When 采样，Then 经验回放缓冲区按容量上限滚动、按 batch 采样。
  - **AC-3**：Given 训练进行中，When 到达同步周期，Then 目标网络参数从主网络更新。
  - **AC-4**：Given 设备为 Apple M2，When 指定 `device=cpu` 或 `mps`，Then 均可正常训练（无 CUDA 依赖）。
  - **AC-5**：Given 同一 seed + 同一配置，When 两次训练，Then 关键指标轨迹一致（可复现）。
- **关联测试用例**：TC-019 ~ TC-024

---

## EP-03 实验记录

### Story: US-06 — 实验配置与指标记录
- **所属 Epic**：EP-03 ｜ **优先级**：P0
- **故事**：作为研究者，我想要训练自动记录配置快照与训练指标，以便复盘与对比。
- **验收标准**：
  - **AC-1**：Given 启动一次实验，When 训练开始，Then 在独立实验目录写入完整配置快照。
  - **AC-2**：Given 训练进行中，When 周期性记录，Then 至少记录 reward 曲线，并含 max-tile、episode 长度、loss、ε。
  - **AC-3**：Given 多次实验，When 查看目录，Then 每次实验有唯一命名（时间戳/run-id），互不覆盖。
- **关联测试用例**：TC-025 ~ TC-029

### Story: US-07 — 模型检查点
- **所属 Epic**：EP-03 ｜ **优先级**：P0
- **故事**：作为研究者，我想要训练自动保存检查点，以便评估与恢复。
- **验收标准**：
  - **AC-1**：Given 训练达到保存周期，When 保存，Then 在实验目录生成检查点文件。
  - **AC-2**：Given 出现更优评估指标，When 保存，Then 额外保留 best 检查点。
  - **AC-3**：Given 一个检查点，When 评估脚本加载，Then 能复原网络并推理。
- **关联测试用例**：TC-030 ~ TC-034

---

## EP-04 可视化与实验对比

### Story: US-08 — TensorBoard 训练曲线与对比
- **所属 Epic**：EP-04 ｜ **优先级**：P0
- **故事**：作为研究者，我想要在 TensorBoard 查看训练曲线并对比多实验，以便判断哪组超参更好。
- **验收标准**：
  - **AC-1**：Given 一次训练产生日志，When 启动 TensorBoard 指向日志根目录，Then 可看到 reward 等标量曲线。
  - **AC-2**：Given 多次实验日志，When 在 TensorBoard 查看，Then 多条曲线可叠加对比（按 run 区分）。
  - **AC-3**：Given 日志根目录为空，When 启动 TensorBoard，Then 优雅显示空态而非崩溃。
- **关联测试用例**：TC-035 ~ TC-038

---

## EP-05 一键启动与可复现

### Story: US-09 — 一键启动与 5 分钟复现
- **所属 Epic**：EP-05 ｜ **优先级**：P0
- **故事**：作为研究者，我想要按 README 一键启动训练/评估/可视化，以便 5 分钟内复现。
- **验收标准**：
  - **AC-1**：Given 干净环境，When 按 README 安装依赖（固定版本），Then 安装成功且 ≤5 分钟可开始训练。
  - **AC-2**：Given 提供脚本/Makefile，When 执行 `train`/`eval`/`board` 命令，Then 分别启动训练/评估/可视化。
  - **AC-3**：Given 提供 arm64 兼容 Dockerfile，When 构建并运行，Then 容器内可跑通 quick 训练。
- **关联测试用例**：TC-039 ~ TC-043

---

## EP-06 测试与正确性

### Story: US-10 — 自动化测试套件
- **所属 Epic**：EP-06 ｜ **优先级**：P0
- **故事**：作为研究者，我想要一套自动化测试，以便证明系统（尤其环境逻辑）正确。
- **验收标准**：
  - **AC-1**：Given 测试套件，When 运行，Then 覆盖移动/合并/计分/生成/终局/接口一致性，全部通过。
  - **AC-2**：Given 训练链路，When 运行冒烟测试，Then 用极小步数跑通 train→记录→检查点而不报错。
  - **AC-3**：Given 一条命令，When 执行测试，Then 输出通过/失败汇总。
- **关联测试用例**：TC-044 ~ TC-047

---

## EP-07 评估与智能性验证

### Story: US-11 — 评估脚本与基线对比
- **所属 Epic**：EP-07 ｜ **优先级**：P1
- **故事**：作为研究者，我想要评估脚本对比"训练后 Agent vs 随机基线"，以便量化证明 Agent 变聪明（S2）。
- **验收标准**：
  - **AC-1**：Given 一个检查点，When 运行评估 N 局，Then 输出 max-tile / score 的分布统计（中位数、均值、最大）。
  - **AC-2**：Given 随机策略基线，When 同样评估 N 局，Then 输出可对比统计。
  - **AC-3**：Given full 训练后的 Agent，When 评估，Then **max-tile 中位数 ≥ 512** 视为达标（S2）。
- **关联测试用例**：TC-048 ~ TC-051

---

## 追溯矩阵 (Story ↔ Spec FR)
| Story | 对应需求(FR) |
| ----- | ------------ |
| US-01 | FR-1 |
| US-02 | FR-2 |
| US-03 | FR-10 |
| US-04 | FR-4 |
| US-05 | FR-3 |
| US-06 | FR-5 |
| US-07 | FR-5 |
| US-08 | FR-6 |
| US-09 | FR-7 |
| US-10 | FR-9 |
| US-11 | FR-8 |

## Human Gate 记录
- 补充场景：无（人类确认当前 Story 覆盖充分）
- 决策结果：✅ **APPROVE**
- 决策人 / 日期：唯一工程师 / 2026-06-07
