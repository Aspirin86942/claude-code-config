# WPS Python Migrator - Codex to Claude Code 适配计划

## Context

**背景**：用户有一个为 Codex 设计的 WPS Python Migrator skill 包，需要适配到 Claude Code 平台。

**原始架构**：
- 入口：`SKILL.md`（Codex skill 元数据 + 工作流定义）
- 事实源：`references/official_capabilities.yml`（机器可读能力清单）
- 扫描工具：`scripts/scan_incompatible_patterns.py`（40 条规则，10 个分类）
- 示例：`example/wps 版本脚本.py`（WPS 原生模式库）
- 测试：`tests/test_scan_incompatible_patterns.py`, `tests/test_skill_docs.py`

**目标**：保留核心知识资产，调整技能触发和 Agent 路由以适配 Claude Code。

---

## 核心发现

### 可直接复用（100%）
| 文件/目录 | 说明 |
|-----------|------|
| `references/` | 所有知识文档（能力清单、平台指南、检查清单） |
| `scripts/scan_incompatible_patterns.py` | 扫描工具完全独立 |
| `tests/` | 所有测试用例 |
| `example/wps 版本脚本.py` | 辅助函数模式库 |
| `environment.yml` | Conda 环境配置 |

### 需要修改（~20%）
| 文件 | 修改内容 |
|------|----------|
| `SKILL.md` | 移除 Codex 元数据头部（YAML frontmatter），替换"Codex"术语为"Claude Code"或"the assistant" |
| `CLAUDE.md` | 已在会话中创建，需确认是否保留 |

### 需要新增
| 文件 | 说明 |
|------|------|
| （可选）`.claude/skills/wps-migrator.md` | 如果 Claude Code 支持 skill 发现机制 |

---

## 适配方案

### 方案 A：轻量适配（推荐）

**修改范围**：仅修改 `SKILL.md` 的术语和元数据

**步骤**：
1. 移除 YAML frontmatter（`---` 包裹的元数据）
2. 全局替换：
   - "Codex skill" → "Claude Code skill"
   - "Codex" → "the assistant" 或 "Claude"
   - "skill-authoring task" → 删除或改为 "skill maintenance"
3. 更新工作流描述中的工具调用说明

**优点**：
- 最小改动，保留原始设计意图
- 风险低，可快速验证
- 所有领域知识保持不变

**缺点**：
- 依赖用户 claudeMd 中的 Agent 路由系统
- 需要确认技能如何被触发

---

### 方案 B：深度集成

**修改范围**：修改 `SKILL.md` + 在用户 claudeMd 中添加 Agent 路由

**步骤**：
1. 执行方案 A 的所有修改
2. 在用户 claudeMd 的 "Agent 调度路由矩阵" 中添加：
   ```markdown
   | **WPS 迁移/代码适配** | `wps-migrator` | 1. 调用 `scan_incompatible_patterns.py` 扫描风险<br>2. 应用 `official_capabilities.yml` 规则<br>3. 参考 `example/` 模式输出 WPS 原生代码 |
   ```
3. （可选）创建 `skills/wps-migrator.md` 作为技能快捷入口

**触发条件建议**：
- 用户提到 "WPS", "KDocs", "金山文档"
- 用户提到 "迁移" + "Python"
- 用户上传 Python 项目并提到云端执行

**优点**：
- 与现有 Agent 系统无缝集成
- 触发条件明确
- 用户已有 claudeMd Agent 路由矩阵，符合其工作流

**缺点**：
- 需要修改用户全局配置（不在本仓库范围内）

---

## 推荐方案

**采用方案 A（轻量适配）**

**理由**：
1. 用户已有全局 `CLAUDE.md`（~200 行）定义了完整的 Agent 路由矩阵
2. 仓库级适配应保持最小侵入性
3. 技能触发可通过用户全局配置控制，无需在本仓库重复定义
4. 核心资产（扫描规则、知识文档、测试）完全保留

**修改文件清单**：
1. `SKILL.md` - 移除 YAML frontmatter，替换术语（约 10-15 处）

**验证步骤**：
1. 运行测试：`conda run -n test python -m pytest -q`
2. 运行扫描器验证：`conda run -n test python scripts/scan_incompatible_patterns.py .`
3. 语法检查：`conda run -n test python -m compileall scripts`

---

## 关键文件路径

| 文件 | 用途 |
|------|------|
| `SKILL.md` | 主要修改目标 |
| `references/official_capabilities.yml` | 核心事实源，无需修改 |
| `scripts/scan_incompatible_patterns.py` | 核心工具，无需修改 |
| `tests/test_skill_docs.py` | 可能需要添加测试验证 SKILL.md 不包含 Codex 术语 |

---

## 风险与缓解

| 风险 | 缓解措施 |
|------|----------|
| 修改后技能触发失效 | 依赖用户全局 claudeMd 配置，不在本仓库控制范围内 |
| 术语替换遗漏 | 使用 grep 全局搜索 "Codex" 确认清理完成 |
| 测试失败 | 运行现有测试套件验证 |

---

## 待确认问题

1. 用户是否希望保留 YAML frontmatter 作为某种文档元数据？
2. 是否需要为 Claude Code 创建独立的 skill 入口文件？
3. 用户的 claudeMd Agent 路由是否已包含 WPS 迁移触发条件？
