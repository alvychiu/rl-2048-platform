---
name: G3-Development
description: 实施开发任务。一次只允许完成一个 Task，完成后更新 tasks.md 状态，并输出变更文件列表与测试方法。代码只能写入 src。
---

# G3 — Development Skill

## Purpose

按照 `tasks.md` 逐个实现开发任务，严格执行"一次一个 Task"的纪律，保证每次变更小而可控、可追溯、可回滚，并即时更新任务状态。

## Inputs

- `artifacts/specifications/spec.md`（开发前必读）
- `artifacts/stories/stories.md`（开发前必读）
- `artifacts/planning/tasks.md`（开发前必读）
- `artifacts/prototype/prototype.md`（参考）

## Outputs

- `src/` 下的代码变更（**只能写入 src 及必要项目配置文件**）
- 更新后的 `artifacts/planning/tasks.md`（任务状态）
- 每次提交的变更文件列表与测试方法

## Required Artifacts

- 上游：`spec.md`、`stories.md`、`tasks.md` 必须存在且已 APPROVE。
- 代码产物位置：仅限 `src/`。

## Process

1. 开发前读取 `spec.md`、`stories.md`、`tasks.md`（强制）。
2. 从 `tasks.md` 选取**一个**状态为 `TODO` 且依赖已满足的 Task，将其置为 `DOING`。
3. 仅实现该 Task，代码写入 `src/`。
4. 完成后：
   - 将该 Task 状态更新为 `DONE`。
   - 输出**变更文件列表**（路径 + 变更说明）。
   - 输出**测试方法**（如何验证该 Task，关联对应 Test Case 编号）。
5. **禁止一次实现多个 Task**。完成一个后停下，等待人类指示是否继续下一个。
6. 全部 Task 完成后，进入 G3.5 Review。

## Human Decision Gate

```
==================== HUMAN GATE: G3 (per task) ====================
完成 Task：<Task ID / 名称>
变更文件列表：<...>
测试方法：<...>
请回复：CONTINUE（下一 Task） / STOP / REWORK（附原因）
==================================================================
```

全部 Task 完成后须人类确认方可进入 G3.5。

## Exit Criteria

- 所选 Task 已实现并通过其测试方法。
- `tasks.md` 状态已更新为 DONE。
- 变更文件列表与测试方法已输出。
- 代码仅写入 `src/`。

## Common Failure Modes

- **一次实现多个 Task**（严重违规）。
- 忘记更新 `tasks.md` 状态。
- 代码写入 `src/` 以外目录。
- 未输出变更文件列表/测试方法。
- 跳过开发前必读文档。

## Example Prompt

```
请加载 G3-Development Skill。
读取 spec.md / stories.md / tasks.md，
从 tasks.md 选取一个 TODO 任务实现（仅一个），
代码写入 src/，完成后更新 tasks.md 状态，
输出变更文件列表与测试方法，然后停下等我指示。
```
