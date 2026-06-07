# 工作流速查表 (Workflow Cheatsheet)

AI Driven Delivery System — G0→G4 门控研发体系快速参考。

## 一图流

```
G0 ─► G1 ─► G2 ─► G2.5 ─► G3 ─► G3.5 ─► G4
需求   故事   规划   原型     开发   评审    验收
 │     │     │     │       │     │      │
APPROVE 才能进入下一个 Gate（Human 决策）
```

## 各 Gate 速记

| Gate  | 做什么            | 读取                                   | 产出                          | 放行条件                    |
| ----- | ----------------- | -------------------------------------- | ----------------------------- | --------------------------- |
| G0    | 需求→Spec         | raw-requirement.md                     | spec.md                       | Spec 被确认                 |
| G1    | Spec→故事+用例    | spec.md                                | stories.md, testcases.md      | 六类场景覆盖、补全场景      |
| G2    | 故事→任务         | spec.md, stories.md                    | tasks.md                      | 无过度设计                  |
| G2.5  | 低保真原型        | spec.md, stories.md                    | prototype.md                  | 产品方向正确                |
| G3    | 实现任务(一次一个)| spec.md, stories.md, tasks.md          | src/ + 更新 tasks.md          | 每个 Task 完成并验证        |
| G3.5  | Review            | src/                                   | review.md                     | High 风险 = 0               |
| G4    | 验收              | testcases.md, review.md                | acceptance.md, release-notes  | 全部用例通过                |

## 启动命令（对 AI 说）

- 「加载 G0-Requirement Skill，开始处理需求」
- 「加载 G1-Story-Test Skill，生成故事与用例」
- 「加载 G2-Planning Skill，拆解任务」
- 「加载 G2.5-Prototype Skill，出低保真原型」
- 「加载 G3-Development Skill，实现下一个 Task（仅一个）」
- 「加载 G3.5-Review Skill，评审 src 变更」
- 「加载 G4-Acceptance Skill，按用例验收」

## 铁律（Top Rules）

1. 禁止跳过任何 Gate。
2. 进入阶段前先读上阶段产物。
3. 文档只进 `artifacts/`，代码只进 `src/`。
4. G3 一次只做一个 Task。
5. High 风险不得发布；用例未全通过不得发布。

## Human 回复关键词

- `APPROVE` — 放行下一阶段
- `REJECT` — 打回（附原因）
- `CONTINUE` — G3 继续下一个 Task
- `RELEASE` — G4 批准发布
