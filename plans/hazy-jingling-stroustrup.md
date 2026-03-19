# 重构计划: 多模态报告系统 (Daily / Weekly / Monthly)

## Context

当前项目仅支持日报 (Daily) 生成和一个简单的月度汇总 (`--monthly`)。月度汇总无 Pydantic 校验、无 JSON 持久化、无结构化模板。需要将系统扩展为支持日报、周报、月报三种模式，每种模式支持两种数据来源策略 (`db` 聚合 / `scan` 扫描)，并统一使用 JSON 强制输出 + Pydantic 校验。

**设计决策 (已确认)**:
- CLI: 直接迁移到子命令，不保留旧语法
- 存储: 周报/月报同时保存 JSON + Markdown (双轨制)
- 周边界: ISO 标准 Monday-Sunday (`date.fromisocalendar()`)
- Schema: 独立模型 (不使用继承)，复用 `WorkItem` / `RiskItem`
- LLM: 每种报告类型独立方法，提取公共重试逻辑为 `_call_llm_with_json()`

---

## Phase 1: 基础定义 (无依赖)

### 1.1 数据模型 — `src/models/schemas.py`

新增:
- `ReportMode(str, Enum)`: `daily` / `weekly` / `monthly`
- `DataSource(str, Enum)`: `db` / `scan`
- `CategorySummary(BaseModel)`: `category`, `items: List[str]`, `total_count: int`, `completion_rate: Optional[str]`
- `WeeklyReportData(BaseModel)`:
  - `week_label: str` (如 "2026-W05")
  - `date_range: str` (如 "2026-01-27 ~ 2026-02-02")
  - `summary: str`
  - `category_summaries: List[CategorySummary]`
  - `risks: List[RiskItem]`
  - `key_achievements: List[str]`
  - `next_week_plans: List[str]`
  - `missing_days: List[str]` (default_factory=list)
  - `data_source: str`
- `MonthlyReportData(BaseModel)`:
  - `year_month: str`
  - `summary: str`
  - `category_summaries: List[CategorySummary]`
  - `risks: List[RiskItem]`
  - `statistics: Dict[str, str]` (灵活 KV 统计)
  - `key_achievements: List[str]`
  - `next_month_plans: List[str]`
  - `missing_days: List[str]`
  - `data_source: str`

保持不变: `WorkItem`, `RiskItem`, `DailyReportData`, `FileContext`, `ScanResult`

### 1.2 工具函数 — `src/utils/text_tools.py`

新增:
- `parse_week_label(label: str) -> tuple[int, int]`: 解析 "2026-W05" → (2026, 5)，用 `date.fromisocalendar()` 校验
- `get_month_date_range(year_month: str) -> tuple[date, date]`: "2026-02" → (2026-02-01, 2026-02-28)

已有可复用: `truncate_text()`, `estimate_tokens()`

### 1.3 配置 — `config/settings.toml`

新增 `[scanner]` 下:
```toml
summary_excel_max_rows = 10
summary_pdf_max_pages = 2
summary_text_max_chars = 2000
total_max_chars = 50000
```

### 1.4 Prompt 模板 (新建文件)

- `templates/weekly_prompt.md` — 周报 system prompt，占位符: `{schema}`, `{week_label}`, `{reports_summary}`, `{file_context}`, `{missing_days}`, `{data_source}`
- `templates/monthly_prompt.md` — 月报 system prompt，占位符: `{schema}`, `{year_month}`, `{reports_summary}`, `{file_context}`, `{missing_days}`, `{data_source}`

### 1.5 渲染模板 (新建文件)

- `templates/weekly_template.md` — Jinja2 周报模板
- `templates/monthly_template.md` — Jinja2 月报模板

---

## Phase 2: 服务层 (依赖 Phase 1)

### 2.1 文件扫描器 — `src/services/file_scanner.py`

**修改 `scan_today_files()`**: 改为调用新的通用方法

**新增 `scan_files(start_date, end_date, summary_mode=False)`**:
- 签名: `scan_files(self, start_date: date | None = None, end_date: date | None = None, summary_mode: bool = False) -> ScanResult`
- `start_date` 默认昨日, `end_date` 默认今日
- `summary_mode=True` 时: 使用缩减限制 (excel_max_rows=10, pdf_max_pages=2, text_max_chars=2000)
- 新增 `total_max_chars` 全局字符上限，超出时停止添加文件并附注

**重构 `_get_today_modified_files()`** → `_get_files_in_range(start_date, end_date)`:
- `start_dt = datetime.combine(start_date, datetime.min.time())`
- `end_dt = datetime.combine(end_date, datetime.max.time())`
- 过滤: `start_dt <= mtime <= end_dt`

**`scan_today_files()` 改为薄封装**: 调用 `scan_files()` 保持向后兼容

### 2.2 历史管理器 — `src/services/history_mgr.py`

**新增方法**:
- `get_reports_in_range(start_date: date, end_date: date) -> tuple[List[DailyReportData], List[str]]`
  - 遍历范围内工作日 (weekday < 5)
  - 返回 `(reports, missing_dates)` — 缺失日报不抛异常
- `get_week_reports(year: int, week: int) -> tuple[List[DailyReportData], List[str]]`
  - 用 `date.fromisocalendar(year, week, 1/7)` 计算边界
  - 调用 `get_reports_in_range()`
- `save_weekly_report(report: WeeklyReportData) -> Path`
  - 保存到 `data/db/weekly/YYYY-Wnn.json`
- `save_monthly_report(report: MonthlyReportData) -> Path`
  - 保存到 `data/db/monthly/YYYY-MM.json`

保持不变: `save_report()`, `get_yesterday_plan()`, `get_month_reports()`, `list_all_reports()`

### 2.3 报告生成器 — `src/services/report_gen.py`

**新增方法**:
- `render_weekly_markdown(report: WeeklyReportData) -> str`: 加载 `weekly_template.md`
- `render_monthly_markdown(report: MonthlyReportData) -> str`: 加载 `monthly_template.md`
- `save_weekly_markdown(content: str, year: int, week: int) -> Path`: 保存到 `data/reports/weekly/YYYY-Wnn.md`
- `save_monthly_markdown(content: str, year_month: str) -> Path`: 保存到 `data/reports/monthly/YYYY-MM.md`

保持不变: `render_markdown()`, `save_markdown()`

---

## Phase 3: LLM 层 (依赖 Phase 2)

### 3.1 LLM 客户端 — `src/core/llm.py`

**重构**:
- `__init__()`: 加载所有 prompt 模板 (`system_prompt.md`, `weekly_prompt.md`, `monthly_prompt.md`) 到 `self.prompt_templates: dict[str, str]`
- 提取 `generate_report()` 中 lines 69-109 的重试逻辑为 `_call_llm_with_json(prompt: str, response_model: type[BaseModel]) -> BaseModel`
- `generate_report()` 改为调用 `_call_llm_with_json()`

**新增**:
- `generate_weekly_report(reports, file_context, year, week, missing_days, data_source) -> WeeklyReportData`
- `generate_monthly_report(reports, file_context, year_month, missing_days, data_source) -> MonthlyReportData`
- `_summarize_reports(reports: List[DailyReportData]) -> str`: 将日报列表压缩为摘要文本 (每份 ~200 字)

**删除**: `generate_monthly_summary()` (被 `generate_monthly_report()` 替代)

---

## Phase 4: CLI 入口 (依赖 Phase 3)

### 4.1 主程序 — `main.py`

**完全重写 `parse_args()`** → `build_parser()`:

```
python main.py daily [-i "内容"] [--no-save] [--date YYYY-MM-DD]
python main.py weekly [YYYY-Wnn] --source db|scan [-i "补充"] [--no-save]
python main.py monthly [YYYY-MM] --source db|scan [-i "补充"] [--no-save]
python main.py list
```

- `daily`: 默认子命令，新增 `--date` 参数支持指定日期
- `weekly`: 位置参数为 ISO 周标签 (可选, 默认本周)，`--source` 必选
- `monthly`: 位置参数为年月 (可选, 默认本月)，`--source` 必选
- `list`: 列出已有日报

**保留/重构**:
- `generate_daily_report()`: 基本不变，改用 `scan_files()` 替代 `scan_today_files()`
- `get_user_input()`: 不变

**新增**:
- `generate_weekly_report_cmd(week, source, user_input, no_save)`:
  1. 解析周标签 → year, week_num → monday, sunday
  2. source=db: `history_mgr.get_week_reports()` 获取日报 + 缺失天数
  3. source=scan: `scanner.scan_files(monday, sunday, summary_mode=True)` 获取文件上下文
  4. 调用 `llm_client.generate_weekly_report()`
  5. 渲染 + 保存 JSON 和 Markdown
- `generate_monthly_report_cmd(month, source, user_input, no_save)`:
  - 同上模式，用 `get_month_date_range()` 获取边界

**删除**: `generate_monthly_summary()` (旧月度汇总函数)

**`main()` 分发**: 使用 `match args.subcommand` (Python 3.10+)

### 4.2 辅助函数 — `main.py` 内

- `build_file_context(scan_result: ScanResult) -> str`: 从 `generate_daily_report()` 中提取文件上下文拼接逻辑，供日报/周报/月报复用

---

## Phase 5: 配置检查 + 测试

### 5.1 `check_config.py`

新增模板文件存在性检查: `weekly_prompt.md`, `monthly_prompt.md`, `weekly_template.md`, `monthly_template.md`

### 5.2 测试

- `tests/test_schemas.py` (新建): 测试 `WeeklyReportData`, `MonthlyReportData`, `CategorySummary` 的 Pydantic 校验
- `tests/test_text_tools.py` (新建): 测试 `parse_week_label()`, `get_month_date_range()`
- `tests/test_file_scanner.py` (修改): 新增 `scan_files(start_date, end_date)` 和 `summary_mode` 测试
- `tests/test_history_mgr.py` (修改): 新增 `get_reports_in_range()`, `get_week_reports()` 测试，验证缺失日期检测
- `tests/test_report_gen.py` (修改): 新增 `render_weekly_markdown()`, `render_monthly_markdown()` 测试

---

## 涉及文件清单

| 文件 | 操作 |
|------|------|
| `src/models/schemas.py` | 修改 (新增 5 个类/枚举) |
| `src/utils/text_tools.py` | 修改 (新增 2 个函数) |
| `config/settings.toml` | 修改 (新增 4 个配置项) |
| `templates/weekly_prompt.md` | **新建** |
| `templates/monthly_prompt.md` | **新建** |
| `templates/weekly_template.md` | **新建** |
| `templates/monthly_template.md` | **新建** |
| `src/services/file_scanner.py` | 修改 (date range + summary_mode) |
| `src/services/history_mgr.py` | 修改 (新增 4 个方法) |
| `src/services/report_gen.py` | 修改 (新增 4 个方法) |
| `src/core/llm.py` | 修改 (重构 + 新增 4 个方法, 删除 1 个旧方法) |
| `main.py` | 重写 (子命令 CLI + 新 handler) |
| `check_config.py` | 修改 (模板检查) |
| `tests/test_schemas.py` | **新建** |
| `tests/test_text_tools.py` | **新建** |
| `tests/test_file_scanner.py` | 修改 |
| `tests/test_history_mgr.py` | 修改 |
| `tests/test_report_gen.py` | 修改 |
| `CLAUDE.md` | 修改 (更新 Commands / Architecture / Project Structure) |

---

## 风险缓解

| 风险 | 措施 |
|------|------|
| Monthly + scan 超出 Gemini 上下文窗口 | `summary_mode` 缩减限制 + `total_max_chars=50000` 全局上限 |
| ISO week 跨年 (2025-W01 含 2024-12-29) | `date.fromisocalendar()` 自动处理 |
| 无效周标签 `2026-W53` | `parse_week_label()` 中 `date.fromisocalendar()` 抛 ValueError |
| Aggregation 模式缺失日报 | `get_reports_in_range()` 返回 `missing_dates`，写入报告而非抛异常 |
| LLM 未返回 `missing_days` 字段 | Schema 中 `default_factory=list`，缺失不影响校验 |

---

## Phase 6: 更新项目文档

### 6.1 `CLAUDE.md`

更新以下章节:
- **Commands**: 新增 `daily`/`weekly`/`monthly`/`list` 子命令用法，删除旧 `--monthly`/`--list` 语法
- **Architecture**: 补充周报/月报数据流
- **Project Structure**: 补充新增的模板文件和测试文件
- **Key Patterns**: 补充 `summary_mode` 和 `total_max_chars` 的 token 控制策略
- **Modifying LLM Output**: 更新为三种报告类型的修改指南

---

## 验证方式

```bash
# 1. 单元测试
pytest tests/ -v

# 2. 日报 (功能回归)
python main.py daily -i "测试日报生成"
python main.py daily --no-save -i "预览模式"

# 3. 周报
python main.py weekly --source db                    # 聚合本周日报
python main.py weekly 2026-W05 --source scan -i "本周总结"  # 扫描文件

# 4. 月报
python main.py monthly --source db                   # 聚合本月日报
python main.py monthly 2026-01 --source scan -i "本月总结"  # 扫描文件

# 5. 列表
python main.py list

# 6. 检查输出文件
ls data/db/weekly/          # JSON 持久化
ls data/db/monthly/
ls data/reports/weekly/     # Markdown
ls data/reports/monthly/
```
