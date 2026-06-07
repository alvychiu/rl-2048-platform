---
name: G2-Planning
description: 将 User Story 拆解为可执行的 Task，标注依赖、复杂度、风险等级与技术方案，并防止过度设计。
---

# G2 — Planning Skill

## Purpose

把已确认的 Story 拆解为颗粒度合适、可独立交付的开发任务（Task），明确依赖关系、复杂度、风险等级与技术方案，为 G3 单任务开发提供精确的执行清单，同时主动规避过度设计。

## Inputs

- `artifacts/specifications/spec.md`（必读）
- `artifacts/stories/stories.md`（必读，已 APPROVE）

## Outputs

- `artifacts/planning/tasks.md`

## Required Artifacts

- 上游：`spec.md`、`stories.md`。
- 模板：`.cursor/templates/task-template.md`。

## Process

1. 读取 `spec.md` 与 `stories.md`。
2. 将每个 Story 拆为若干 Task，每个 Task 必须包含：
   - **任务（Task）**：清晰、可独立完成的工作项。
   - **依赖（Dependencies）**：前置 Task 或外部依赖。
   - **复杂度（Complexity）**：S / M / L 或故事点。
   - **风险等级（Risk）**：High / Medium / Low。
   - **技术方案（Approach）**：实现思路、涉及模块、关键取舍。
3. 为每个 Task 标注状态字段：`TODO / DOING / DONE`（初始为 TODO）。
4. 建立 Task → Story 的追溯关系。
5. 审视拆解结果，剔除过度设计（不必要的抽象、超前的扩展点、YAGNI 违例）。
6. 提交 Human Decision Gate，请人类确认不存在过度设计。

## Human Decision Gate

```
==================== HUMAN GATE: G2 ====================
阶段产物：artifacts/planning/tasks.md
关键决策点：
  - 是否存在过度设计（不必要的抽象/超前扩展）
  - 依赖与执行顺序是否合理
  - 高风险 Task 的技术方案是否可接受
请回复：APPROVE / REJECT（附原因）
========================================================
```

## Exit Criteria

- 每个 Task 含任务、依赖、复杂度、风险等级、技术方案五要素。
- Task 与 Story 可追溯，且每个 Task 可独立交付。
- 人类已确认无过度设计。
- 收到人类 `APPROVE`。

## Common Failure Modes

- Task 粒度过大，无法在 G3 单任务完成。
- 缺少依赖标注，导致执行顺序混乱。
- 过度设计：为假想需求引入复杂抽象。
- 风险等级缺失或随意标注。

## Example Prompt

```
请加载 G2-Planning Skill。
读取 spec.md 与 stories.md，
生成 artifacts/planning/tasks.md，
每个 Task 标注依赖、复杂度、风险等级、技术方案，
完成后提交 G2 Human Gate 确认无过度设计。
```
