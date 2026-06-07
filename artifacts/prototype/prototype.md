# 低保真原型 (Prototype) — 2048 RL 训练实验平台 MVP

> 阶段：G2.5 Prototype ｜ 来源：spec.md, stories.md, tasks.md（均已 APPROVE）｜ 状态：✅ Approved（2026-06-07）
> 说明：本系统是**命令行工具 + TensorBoard 可视化**，无传统 GUI。原型的"页面"指：CLI 命令界面、终端输出界面、TensorBoard 面板。低保真，仅验证产品方向，不涉及视觉细节。

## 1. 页面清单 (Pages / Screens)
| 页面ID | 页面名称 | 形态 | 目的 | 关联Story |
| ------ | -------- | ---- | ---- | --------- |
| P-01 | 训练命令界面 | CLI | 启动并实时输出训练进度 | US-04,US-05,US-06 |
| P-02 | 实验产物目录 | 文件系统 | 配置快照/日志/检查点的归档结构 | US-06,US-07 |
| P-03 | TensorBoard 面板 | Web(本地) | 查看训练曲线、跨实验对比 | US-08 |
| P-04 | 评估命令界面 | CLI | 评估检查点 + 随机基线对比 | US-11 |
| P-05 | 棋盘渲染 | 终端文本 | 人工观察单局对弈 | US-03 |
| P-06 | 一键入口(Make/脚本) | CLI | train/eval/board 统一入口 | US-09 |

---

## 2. 页面线框 (Wireframes)

### P-06 — 一键入口（用户的第一接触点）
```
$ make help
┌──────────────────────────────────────────────┐
│ 2048 RL 训练实验平台                            │
├──────────────────────────────────────────────┤
│ make install   安装依赖 (固定版本)             │
│ make train     训练 (默认 configs/quick.yaml)  │
│ make train CONFIG=configs/full.yaml            │
│ make board     启动 TensorBoard (localhost:6006)│
│ make eval CKPT=runs/<id>/best.pt               │
│ make test      运行测试套件                     │
└──────────────────────────────────────────────┘
```

### P-01 — 训练命令界面
```
$ make train CONFIG=configs/quick.yaml
[cfg ] loaded configs/quick.yaml | device=mps | seed=42
[run ] runs/2026-06-07_11-50_quick/
[init] env=2048-v0  agent=DQN(MLP)  buffer=10000
─────────────────────────────────────────────────
step   1000 | ep  37 | reward  84.0 | max_tile  64 | loss 0.21 | eps 0.62
step   2000 | ep  71 | reward 132.0 | max_tile 128 | loss 0.14 | eps 0.41
...
[ckpt] saved runs/.../ckpt_5000.pt
[best] new best (eval max_tile median=256) -> best.pt
─────────────────────────────────────────────────
[done] total_steps=20000 | elapsed 7m12s | logs -> runs/2026-06-07_11-50_quick/
```
- 状态：
  - **默认态**：逐行打印 step 指标。
  - **加载态**：`[cfg]/[init]` 初始化提示。
  - **错误态**：配置非法 → `[error] config: 'lr' must be float, got 'abc'` 并退出（非 0）。
  - **空/边界态**：device=cuda 不可用 → `[warn] CUDA unavailable, falling back to cpu`。

### P-02 — 实验产物目录
```
runs/
└── 2026-06-07_11-50_quick/
    ├── config.snapshot.yaml     # 配置快照
    ├── events.out.tfevents...   # TensorBoard 指标
    ├── ckpt_5000.pt             # 周期检查点
    ├── ckpt_10000.pt
    ├── best.pt                  # 最优检查点
    └── train.log               # 文本日志
```
- 状态：每次实验唯一目录（时间戳+配置名），互不覆盖；0 步退出不产生损坏文件。

### P-03 — TensorBoard 面板
```
$ make board
TensorBoard on http://localhost:6006

┌─ SCALARS ───────────────────────────────────────┐
│  reward/episode        max_tile/episode          │
│   ╭─────────╮            ╭─────────╮             │
│   │   ╱╲ ╱╲ │            │     ╱──  │             │
│   │  ╱  ╲╱  │            │   ╱╱     │             │
│   ╰─────────╯            ╰─────────╯             │
│  loss                   epsilon (decay)          │
│                                                   │
│  Runs:  ☑ 11-50_quick   ☑ 14-20_full  (叠加对比) │
└───────────────────────────────────────────────────┘
```
- 状态：
  - **空态**：日志根目录为空 → TB 显示 "No dashboards are active"，不崩溃。
  - **错误态**：端口 6006 被占用 → 提示换端口 `make board PORT=6007`。

### P-04 — 评估命令界面
```
$ make eval CKPT=runs/2026-06-07_14-20_full/best.pt
[eval] checkpoint = .../best.pt | episodes=100
─────────────────────────────────────────────────
Policy        max_tile(median)  max_tile(max)  score(mean)
trained DQN        512              2048           14820
random baseline     64               256             980
─────────────────────────────────────────────────
[S2] max_tile median 512 >= 512  ->  ✅ PASS
```
- 状态：错误态 → 检查点不存在 `[error] checkpoint not found: ...`。

### P-05 — 棋盘渲染（文本）
```
+------+------+------+------+
|    2 |      |    4 |      |
+------+------+------+------+
|      |   16 |    8 |    2 |
+------+------+------+------+
|    4 |   32 |  128 |   16 |
+------+------+------+------+
|      |    2 |    4 |  256 |
+------+------+------+------+
score: 1832
```
- 状态：空格统一占位（留空），不报错。

---

## 3. 导航关系 (Navigation)
```
                       [P-06 一键入口 make]
                ┌────────────┼─────────────┐
                ▼            ▼              ▼
        [P-01 训练]     [P-04 评估]     [P-03 TensorBoard]
              │              │
              ▼              ▼
        [P-02 产物目录] ◄────┘   (eval 读取 P-02 中的 best.pt)
              │
              └──► [P-03 TensorBoard 读取 runs/ 日志]

[P-05 棋盘渲染] 由训练/评估内部调用 render() 触发（调试观察用）
```

## 4. 交互流程 (Interaction Flow)

### 流程 A：训练一个实验（主流程）
1. 用户 `make train CONFIG=configs/quick.yaml`
2. 系统加载并**校验配置**（失败 → 错误态退出）
3. 创建唯一 run 目录、写配置快照（目录不可写 → 报权限错误）
4. 循环：环境交互 → 存回放 → 学习 → 周期记录指标/保存检查点
5. 结束打印总结，日志落到 `runs/<id>/`

### 流程 B：查看与对比训练
1. 用户 `make board`
2. TB 指向 `runs/` 根目录（空 → 空态）
3. 浏览器查看 reward/max_tile/loss/eps 曲线，勾选多个 run 叠加对比

### 流程 C：评估与达标判定
1. 用户 `make eval CKPT=runs/<id>/best.pt`（不存在 → 错误态）
2. 跑 N 局，统计训练策略 vs 随机基线
3. 输出 max_tile 中位数，判定 S2 是否 PASS（≥512）

## 产品方向要点（请重点确认）
- **交互形态 = CLI + TensorBoard**（无自研 GUI），符合 MVP 与单机定位。
- **核心用户旅程 = train → board(看曲线) → eval(验达标)**，三命令闭环。
- **实验以 run 目录为单位**自包含（配置+日志+检查点），便于对比与复现。

## Human Gate 记录
- 产品方向是否正确：是（人类确认 CLI + TensorBoard 形态与三命令闭环）
- 调整意见：无
- 决策结果：✅ **APPROVE**
- 决策人 / 日期：唯一工程师 / 2026-06-07
