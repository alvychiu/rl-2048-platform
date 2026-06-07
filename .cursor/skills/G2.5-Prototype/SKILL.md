---
name: G2.5-Prototype
description: 生成低保真原型，描述页面、导航与交互流程，在投入开发前确认产品方向正确。
---

# G2.5 — Prototype Skill

## Purpose

在正式开发前，用低保真原型（文字 + ASCII/线框描述）快速呈现页面结构、导航关系与关键交互流程，让人类以最低成本验证"产品方向是否正确"，避免方向性返工。

## Inputs

- `artifacts/specifications/spec.md`（必读）
- `artifacts/stories/stories.md`（必读）
- `artifacts/planning/tasks.md`（参考）

## Outputs

- `artifacts/prototype/prototype.md`

## Required Artifacts

- 上游：`spec.md`、`stories.md`、`tasks.md`。
- 模板：`.cursor/templates/prototype-template.md`。

## Process

1. 读取 `spec.md`、`stories.md`，理解用户旅程。
2. 套用 `prototype-template.md`，输出：
   - **页面（Pages/Screens）**：每个页面的目的与核心元素（用线框/ASCII 描述）。
   - **导航（Navigation）**：页面间跳转关系与入口。
   - **交互流程（Interaction Flow）**：关键操作的步骤流（含异常/空态提示）。
3. 标注关键交互的状态：默认态、加载态、空态、错误态。
4. 明确这是低保真原型，仅验证方向，不涉及视觉细节。
5. 提交 Human Decision Gate，请人类确认产品方向。

## Human Decision Gate

```
==================== HUMAN GATE: G2.5 ====================
阶段产物：artifacts/prototype/prototype.md
关键决策点：
  - 产品方向（信息架构/主流程）是否正确
  - 页面与导航是否符合用户预期
  - 是否需要调整流程后再进入开发
请回复：APPROVE / REJECT（附调整意见）
=========================================================
```

## Exit Criteria

- `prototype.md` 含页面、导航、交互流程三部分。
- 关键页面标注了默认/加载/空/错误态。
- 人类已确认产品方向正确。
- 收到人类 `APPROVE`。

## Common Failure Modes

- 直接进入高保真/视觉细节，违背低保真目标。
- 只画页面不画导航与流程。
- 忽略空态与错误态。
- 未与 Story 对齐，原型覆盖不全。

## Example Prompt

```
请加载 G2.5-Prototype Skill。
读取 spec.md 与 stories.md，
生成 artifacts/prototype/prototype.md（页面+导航+交互流程，低保真），
完成后提交 G2.5 Human Gate 确认产品方向。
```
