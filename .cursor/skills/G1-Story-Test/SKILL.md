---
name: G1-Story-Test
description: 基于已确认的 Spec 生成 Epic、User Story、Acceptance Criteria 与全面的 Test Cases，覆盖正常、异常、边界、权限、网络、空数据等场景。
---

# G1 — Story-Test Skill

## Purpose

把已通过 G0 的 Spec 拆解为可交付的用户故事（Story）并配套测试用例（Test Cases），用"测试先行"的方式把验收标准前置固化，保证后续开发与验收有据可依。

## Inputs

- `artifacts/specifications/spec.md`（必读，且必须已被人类 APPROVE）

## Outputs

- `artifacts/stories/stories.md`
- `artifacts/testcases/testcases.md`

## Required Artifacts

- 上游：`artifacts/specifications/spec.md`。
- 模板：`.cursor/templates/story-template.md`、`.cursor/templates/testcase-template.md`。

## Process

1. 读取并确认 `spec.md` 已被 APPROVE。
2. 生成 `stories.md`，包含：
   - **Epic**：高层业务目标分组。
   - **User Story**：`作为<角色>，我想要<功能>，以便<价值>`。
   - **Acceptance Criteria**：每个 Story 可验证的验收标准（Given/When/Then）。
3. 生成 `testcases.md`，每条 Story 至少覆盖以下场景类别：
   - 正常流程（Happy Path）
   - 异常流程（错误输入、失败分支）
   - 边界条件（极限值、临界值）
   - 权限问题（未登录、越权、角色差异）
   - 网络问题（超时、断网、重试）
   - 空数据问题（空列表、空字段、首次使用）
4. 用例编号与 Story 建立可追溯映射（如 `TC-001 → US-01`）。
5. 提交 Human Decision Gate，请人类补充遗漏场景。

## Human Decision Gate

```
==================== HUMAN GATE: G1 ====================
阶段产物：artifacts/stories/stories.md, artifacts/testcases/testcases.md
关键决策点：
  - 是否存在遗漏的用户场景需要补充
  - 验收标准是否可度量、可验证
  - 六类测试场景是否均已覆盖
请回复：APPROVE / REJECT（附补充场景）
========================================================
```

## Exit Criteria

- `stories.md` 含 Epic / User Story / Acceptance Criteria。
- `testcases.md` 对每个 Story 覆盖六类场景。
- Story 与 Test Case 双向可追溯。
- 收到人类 `APPROVE`。

## Common Failure Modes

- 只写正常流程，漏掉异常/边界/权限/网络/空数据。
- Acceptance Criteria 不可度量（如"体验好"）。
- Story 粒度过大，无法独立验收。
- 用例与 Story 无追溯关系。

## Example Prompt

```
请加载 G1-Story-Test Skill。
读取 artifacts/specifications/spec.md，
生成 stories.md 与 testcases.md，
确保覆盖正常/异常/边界/权限/网络/空数据六类场景，
完成后提交 G1 Human Gate。
```
