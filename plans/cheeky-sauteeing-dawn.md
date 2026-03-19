# WPS Python Migrator Skill 优化计划 - 运用子代理提升效率

## Context

用户需求：在当前 skill 内部**运用子代理 (Sub-agent) 模式**来优化迁移流程，而非将 skill 本身改造成子代理。

**核心问题**：当前 SKILL.md 要求主控 Claude 手动完成所有分析和迁移工作，对于多文件项目效率低下，且无法并行处理独立任务。

---

## 优化方案：在 skill 中内嵌子代理调用策略

### 1. 项目检查阶段 - 使用 Explore 子代理

**当前做法**：
```markdown
- Scan every relevant `.py` file before editing.
- Identify entrypoints, shared utilities, config modules, and persistence layers.
```

**优化后**：
```markdown
## Inspect the project using Explore subagent

For multi-file projects (more than 3 `.py` files) or unfamiliar codebases:

1. **Launch Explore subagent** with prompt:
   > "Explore this Python project to identify: (1) entry scripts and main functions, (2) shared utilities and helpers, (3) config files and external dependencies (HTTP/DB), (4) local file I/O patterns, (5) output targets (worksheets vs data-tables). Return a structured summary with file paths and their roles."

2. **Run scanner in parallel**:
   > `python scripts/scan_incompatible_patterns.py <path>`

3. **Synthesize findings** before planning migration.
```

**收益**：
- Explore 子代理专门用于代码库探索，比主控手动读取更高效
- 支持并行扫描多个文件
- 输出结构化的项目地图

---

### 2. 文档验证阶段 - 使用 Context7 MCP + 子代理

**当前做法**：
```markdown
Use the live WPS Python docs at `https://airsheet.wps.cn/pydocs/introduction/summary.html` as the source of truth.
```

**优化后**：
```markdown
## Verify APIs using Context7 MCP

Before finalizing migration:

1. **For unverified or snapshot-only APIs** (`delete_dbt`, `polars`, `dbt(..., condition=...)`):
   - Launch subagent with prompt:
     > "Query Context7 MCP to verify current WPS support for: [API/library name]. Return official documentation URL, verified parameters, and any breaking changes since 2025."

2. **For third-party libraries** not in the verified subset:
   - Always call Context7 MCP before approving

3. **Mark verification level** in final output:
   - `dedicated_api_doc_verified` - Official API docs exist
   - `summary_example_verified` - Shown in summary only
   - `unverified_or_snapshot_only` - Needs manual confirmation
```

**收益**：
- 避免使用过时文档
- 自动标记未验证假设

---

### 3. 专业审查阶段 - 使用专用 Reviewer 子代理

**当前做法**：
```markdown
Before finishing, verify: [long checklist with 20+ items]
```

**优化后**：
```markdown
## Review using specialized subagents

After migration, activate appropriate reviewers:

| Trigger | Activate |
| :--- | :--- |
| External HTTP calls detected | `security-reviewer` - Check for: secrets, injection, retry logic |
| Database/SQL detected | `database-reviewer` - Check for: N+1, indexes, RLS |
| Python code written | `python-reviewer` - Check for: type hints, vectorization, error handling |
| Complex refactoring | `refactor-cleaner` - Check for: dead code, unused imports |
| Final validation | `e2e-runner` - Run critical flow tests |
```

**收益**：
- 每个 Reviewer 都有专业检查清单
- 避免主控遗漏关键审查点

---

### 4. 复杂任务规划 - 使用 Planner 子代理

**当前做法**：
```markdown
Create a migration plan grouped by reusable rules.
```

**优化后**：
```markdown
## Plan complex migrations using Planner subagent

For multi-file migrations or hybrid (worksheet + data-table) targets:

1. **Launch Planner subagent** with:
   > "Design a migration plan for this WPS migration. Output: (1) Goal/Non-Goals, (2) API Contract (worksheet vs data-table), (3) Commit Plan (independent, reversible steps)"

2. **Execute commits sequentially**, running tests after each
```

**收益**：
- 结构化输出迁移计划
- 明确的 API 契约和回滚策略

---

## 修改后的 SKILL.md 关键段落

### 新增：Agent Subagent Usage Section

在 `Inspect the project first` 之后添加：

```markdown
## Use subagents for efficiency

For projects with more than 3 `.py` files or unclear structure:

1. **Explore** - Launch Explore subagent to map the codebase
2. **Planner** - For complex migrations, design the approach
3. **Reviewers** - Activate specialized reviewers (security, database, python)
4. **Context7 MCP** - Verify unverified APIs against live docs

Single-file migrations may skip subagents and proceed directly.
```

---

## 不需要修改的部分

- `references/` - 参考文档保持不变
- `scripts/scan_incompatible_patterns.py` - 扫描器继续独立运行
- `tests/` - 测试覆盖现有功能
- 核心迁移规则（API 选择、输出形状等）保持不变

---

## 实施检查清单

- [ ] 在 SKILL.md 的 `Inspect the project first` 后添加子代理使用指南
- [ ] 在 `Validate before finishing` 前添加 Reviewer 子代理激活规则
- [ ] 添加 `Use subagents for efficiency` 章节，明确触发条件

---

## 预期收益对比

| 场景 | 当前做法 | 优化后 |
| :--- | :--- | :--- |
| 10 文件项目扫描 | 主控逐个读取 | Explore 子代理并行探索 |
| 未验证 API 检查 | 依赖主控记忆 | Context7 MCP 自动验证 |
| 安全审查 | 手动检查清单 | `security-reviewer` 自动扫描 |
| 复杂迁移规划 | 主控手动设计 | `planner` 输出结构化计划 |
