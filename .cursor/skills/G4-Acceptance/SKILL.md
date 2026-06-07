---
name: G4-Acceptance
description: 依据 testcases 执行验收，记录测试项/步骤/预期/实际/是否通过。全部通过才能发布。
---

# G4 — Acceptance Skill

## Purpose

依据 G1 固化的测试用例，对已通过 Review 的实现进行端到端验收，逐条记录执行结果，作为是否发布的最终依据。

## Inputs

- `artifacts/testcases/testcases.md`（验收前必读）
- `artifacts/reviews/review.md`（必须已 APPROVE 且无 High 风险）
- `src/` 实现

## Outputs

- `artifacts/acceptance/acceptance.md`
- 通过后：`artifacts/release/release-notes.md`

## Required Artifacts

- 上游：`testcases.md`、`review.md`（无 High 风险）。
- 模板：`.cursor/templates/acceptance-template.md`。

## Process

1. 确认 G3.5 已 APPROVE 且 `review.md` 中 High 风险为 0（否则不得开始验收）。
2. 读取 `testcases.md`，逐条执行验收，记录为表格：
   | 测试项 | 步骤 | 预期结果 | 实际结果 | 是否通过 |
3. 对未通过项，记录失败详情并打回 G3 修复。
4. 全部通过后，编写 `release/release-notes.md`（变更摘要、影响范围、回滚方案）。
5. 提交 Human Decision Gate。

## Human Decision Gate

```
==================== HUMAN GATE: G4 ====================
阶段产物：artifacts/acceptance/acceptance.md
通过率：<pass>/<total>
关键决策点：
  - 是否全部用例通过（未全通过禁止发布）
  - 是否批准发布并生成 release-notes
请回复：RELEASE（全部通过，发布） / REJECT（回 G3 修复）
========================================================
```

## Exit Criteria

- 每条 Test Case 均有"实际结果"与"是否通过"。
- **全部用例通过**。
- `release-notes.md` 已生成。
- 收到人类 `RELEASE`。

## Common Failure Modes

- 在存在 High 风险时开始验收。
- 只记录"通过"不记录实际结果与步骤。
- 部分用例失败仍发布（严重违规）。
- 未生成 release-notes 就宣布完成。

## Example Prompt

```
请加载 G4-Acceptance Skill。
确认 review.md 无 High 风险后，
读取 testcases.md 逐条验收，
生成 artifacts/acceptance/acceptance.md（测试项/步骤/预期/实际/是否通过），
全部通过则生成 release-notes，提交 G4 Human Gate。
```
