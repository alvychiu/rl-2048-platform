---
name: G0-Requirement
description: 将模糊的原始需求转化为正式、可执行的 Spec。识别歧义、缺失信息、边界条件、非目标范围与风险。这是 G0→G4 门控流程的第一道门。
---

# G0 — Requirement Skill

## Purpose

将利益相关者提供的模糊、口语化、不完整的原始需求，转换为一份结构清晰、无歧义、可被工程团队执行的正式规格说明书（Spec）。这是整个交付链路的源头，质量直接决定后续所有阶段。

## Inputs

- `artifacts/requirements/raw-requirement.md`（原始需求，必读）
- 可选：业务背景、相关方访谈记录、现有系统约束

## Outputs

- `artifacts/specifications/spec.md`（正式规格说明书）

## Required Artifacts

- 上游：`artifacts/requirements/raw-requirement.md` 必须存在且非空。
- 下游：本阶段产出 `artifacts/specifications/spec.md`，使用 `.cursor/templates/spec-template.md` 作为结构。

## Process

1. 读取 `artifacts/requirements/raw-requirement.md`，完整理解原始诉求。
2. 套用 `.cursor/templates/spec-template.md` 的结构起草 Spec。
3. 系统性识别并显式列出以下五类问题（缺一不可）：
   - **歧义（Ambiguity）**：含义不清、可多种解读的描述。
   - **缺失信息（Missing Info）**：决策所需但原文未提供的信息。
   - **边界条件（Edge Cases）**：极限值、空值、并发、超时等。
   - **非目标范围（Out of Scope）**：明确本期不做的内容，防止范围蔓延。
   - **风险（Risks）**：技术、业务、合规、依赖等风险及缓解思路。
4. 对每个歧义/缺失项，给出"AI 的合理假设"并标注 `需人类确认`。
5. 输出 Spec 后，提交 Human Decision Gate。

## Human Decision Gate

```
==================== HUMAN GATE: G0 ====================
阶段产物：artifacts/specifications/spec.md
关键决策点：
  - 确认所有"需人类确认"的假设是否成立
  - 确认非目标范围是否正确（防止漏做/多做）
  - 确认已识别风险的可接受性
请回复：APPROVE / REJECT（附原因）
========================================================
```

人类确认 Spec 后，才能进入 G1。

## Exit Criteria

- `spec.md` 已生成且覆盖模板全部章节。
- 歧义、缺失信息、边界条件、非目标范围、风险五项均已显式列出。
- 所有"需人类确认"项已被人类裁决。
- 收到人类 `APPROVE`。

## Common Failure Modes

- 直接把原始需求复制成 Spec，未做歧义识别。
- 遗漏"非目标范围"，导致后续范围蔓延。
- 把假设当成事实，未标注需人类确认。
- 风险只罗列不给缓解方向。
- 越权进入 G1（未拿到 APPROVE）。

## Example Prompt

```
请加载 G0-Requirement Skill。
读取 artifacts/requirements/raw-requirement.md，
按 spec-template 生成 artifacts/specifications/spec.md，
重点识别歧义、缺失信息、边界条件、非目标范围与风险，
完成后向我提交 G0 Human Gate。
```
