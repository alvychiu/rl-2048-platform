---
name: G3.5-Review
description: Review 代码，检查 Bug、安全、性能、可维护性与边界情况，按 High/Medium/Low 标注风险。存在 High 风险禁止进入 G4。
---

# G3.5 — Review Skill

## Purpose

对 G3 产出的代码进行系统化评审，发现并分级风险，确保进入验收前代码质量达标。这是发布前的质量闸门：High 风险必须清零。

## Inputs

- `src/` 下的全部代码变更
- `artifacts/specifications/spec.md`、`artifacts/stories/stories.md`、`artifacts/planning/tasks.md`（参考）

## Outputs

- `artifacts/reviews/review.md`

## Required Artifacts

- 上游：G3 已完成（`tasks.md` 中相关 Task 为 DONE）。
- 模板：`.cursor/templates/review-template.md`。

## Process

1. 通读 `src/` 变更，结合 Spec/Story 理解意图。
2. 从以下维度逐项检查并记录发现：
   - **Bug**：逻辑错误、未处理分支、错误处理缺陷。
   - **安全（Security）**：注入、鉴权/越权、敏感信息泄露、依赖漏洞。
   - **性能（Performance）**：N+1、无谓循环、内存/IO 问题。
   - **可维护性（Maintainability）**：可读性、重复、命名、耦合。
   - **边界情况（Edge Cases）**：空值、并发、超时、极限输入。
3. 为每个发现标注风险等级：**High / Medium / Low**，并给出修复建议。
4. 汇总结论：是否存在 High 风险。
5. 提交 Human Decision Gate。

## Human Decision Gate

```
==================== HUMAN GATE: G3.5 ====================
阶段产物：artifacts/reviews/review.md
High 风险数量：<n>
关键决策点：
  - 若存在 High 风险 → 必须打回 G3 修复，禁止进入 G4
  - Medium/Low 风险的处置（修复 or 记录待办）
请回复：APPROVE（无 High，放行 G4） / REJECT（回 G3 修复）
=========================================================
```

## Exit Criteria

- `review.md` 覆盖 Bug/安全/性能/可维护性/边界五维度。
- 每个发现均有风险等级与修复建议。
- **High 风险数量为 0**。
- 收到人类 `APPROVE`。

## Common Failure Modes

- 只看功能不看安全/性能。
- 风险不分级，无法判断能否放行。
- 存在 High 风险却放行进入 G4（严重违规）。
- 发现问题不给修复建议。

## Example Prompt

```
请加载 G3.5-Review Skill。
对 src/ 的变更做 Review，
按 Bug/安全/性能/可维护性/边界检查，
每项标注 High/Medium/Low，生成 artifacts/reviews/review.md，
完成后提交 G3.5 Human Gate（有 High 必须回 G3）。
```
