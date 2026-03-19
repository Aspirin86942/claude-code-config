# .gitignore Plan - Claude Code Sync Configuration

## Context
用户需要在两台电脑之间同步 Claude Code 配置目录 (`C:\Users\chenzixuan\.claude`)，需要一个 `.gitignore` 文件来排除不适合跨设备同步的文件（缓存、日志、会话数据等）。

## Implementation

### Critical Files Created
- `C:\Users\chenzixuan\.claude\.gitignore` - 新建

### Sync Strategy

**✅ 同步 (核心配置):**
- `CLAUDE.md` - 用户核心指令
- `settings.json` - 权限/环境配置
- `config.json` - 基础配置
- `skills/` - 自定义技能
- `agents/` - Agent 定义
- `ide/`, `plugins/`, `projects/`, `tasks/`, `todos/` - 配置数据

**❌ 不同步 (排除项):**
- 缓存：`cache/`, `paste-cache/`, `stats-cache.json`
- 日志/调试：`debug/`, `telemetry/`, `statsig/`
- 会话数据：`history.jsonl`, `sessions/`, `shell-snapshots/`, `file-history/`
- 备份/下载：`backups/`, `downloads/`

## Verification
1. 运行 `git status` 查看被忽略的文件
2. 确认核心配置文件未被忽略
3. 确认缓存/日志文件已被忽略
