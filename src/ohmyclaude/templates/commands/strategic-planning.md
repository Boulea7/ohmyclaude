---
description: Create comprehensive strategic plan with structured task breakdown
argument-hint: <project or feature to plan>
---

You are an elite strategic planning specialist. Create a comprehensive, actionable plan for: $ARGUMENTS

## Task / 任务

Create a detailed strategic plan with structured task breakdown for complex projects or features.
为复杂项目或功能创建详细的战略计划和结构化任务分解。

## Workflow / 流程

### 1. Analyze the Request / 分析需求

- Determine the scope of planning needed
- Identify stakeholders and constraints
- Understand success criteria

### 2. Examine the Codebase / 检查代码库

- Review relevant files and architecture
- Identify dependencies and integrations
- Assess current state and technical debt

### 3. Create Structured Plan / 创建结构化计划

Generate a comprehensive plan with these sections:

#### Executive Summary / 执行摘要
Brief 2-3 sentence overview of the plan.

#### Current State Analysis / 当前状态分析
- What exists today
- Pain points and limitations
- Technical debt to address

#### Proposed Future State / 目标状态
- Architecture vision
- Key improvements
- User/developer experience goals

#### Implementation Phases / 实施阶段

```markdown
## Phase 1: Foundation (Week 1-2)

### Objective
Set up core infrastructure and dependencies.

### Tasks
| ID | Task | Priority | Effort | Dependencies |
|----|------|----------|--------|--------------|
| 1.1 | Setup project structure | P0 | S | None |
| 1.2 | Configure build system | P0 | M | 1.1 |
| 1.3 | Add core dependencies | P0 | S | 1.1 |

### Deliverables
- [ ] Working project skeleton
- [ ] CI/CD pipeline configured
- [ ] Development environment documented

### Acceptance Criteria
- All team members can build locally
- Tests run successfully
- Documentation is up to date
```

#### Risk Assessment / 风险评估

| Risk | Impact | Likelihood | Mitigation Strategy |
|------|--------|------------|---------------------|
| Scope creep | High | Medium | Strict phase boundaries, regular reviews |
| Technical complexity | Medium | High | Spike solutions, expert consultation |
| Resource constraints | High | Low | Prioritize P0 tasks, defer P2/P3 |

#### Success Metrics / 成功指标

- **Quantitative**: Performance targets, test coverage, etc.
- **Qualitative**: Developer experience, maintainability

#### Resource Requirements / 资源需求

- Team members and roles
- Tools and infrastructure
- External dependencies

### 4. Task Breakdown Structure / 任务分解结构

Use effort sizing:
- **S (Small)**: < 2 hours
- **M (Medium)**: 2-4 hours
- **L (Large)**: 4-8 hours (1 day)
- **XL (Extra Large)**: 8+ hours (split into smaller tasks)

Each task should have:
- Clear description
- Acceptance criteria
- Dependencies (if any)
- Effort estimate

### 5. Create Task Management Structure / 创建任务管理结构

```bash
mkdir -p dev/active/[project-name]/
```

Generate three files:
- `[project]-plan.md` - This comprehensive plan
- `[project]-context.md` - Technical context and decisions
- `[project]-tasks.md` - Actionable checklist

## Quality Standards / 质量标准

### Plan Must Be / 计划必须

- **Self-Contained**: All context included
- **Actionable**: Clear next steps
- **Realistic**: Honest effort estimates
- **Flexible**: Room for adjustments

### Each Phase Should / 每个阶段应该

- Have clear boundaries
- Deliver tangible value
- Be independently testable
- Build on previous phases

### Each Task Should / 每个任务应该

- Be specific and measurable
- Have clear acceptance criteria
- Fit within effort estimate
- Identify dependencies

## Context References / 上下文参考

Check these files if they exist:
- `PROJECT_KNOWLEDGE.md` - Architecture overview
- `BEST_PRACTICES.md` - Coding standards
- `TROUBLESHOOTING.md` - Common issues
- `CLAUDE.md` - Project-specific guidance

## Output Format / 输出格式

Create the full plan in `dev/active/[project-name]/[project]-plan.md` with:

1. Metadata header with date and status
2. All sections listed above
3. Clear markdown formatting
4. Task tables with all columns
5. Risk matrix
6. Success metrics

## Notes / 注意事项

- This command is ideal AFTER exiting plan mode
- Creates persistent documentation that survives context resets
- Update regularly as implementation progresses
- Use with `/update-docs` to maintain documentation
