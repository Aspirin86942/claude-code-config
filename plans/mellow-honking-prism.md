# 审计日报生成器重构实现计划

## 项目概述
将现有的单文件脚本 (Ai_Daily_Report.py, 450行) 重构为专业的工程化 CLI 工具。

**核心改进**:
1. 配置驱动 (TOML 替代硬编码)
2. 结构化数据 (JSON 存储 + Markdown 渲染)
3. 并行文件处理 (ThreadPoolExecutor)
4. 从 JSON 读取历史 (不再正则解析 Markdown)
5. LLM 强制 JSON 输出 (Pydantic 校验)

---

## 实现步骤

### 阶段 1: 基础设施层

#### 1.1 创建目录结构
```
ai-daily-report/
├── config/
├── data/
│   ├── reports/
│   └── db/
├── src/
│   ├── core/
│   ├── models/
│   ├── services/
│   └── utils/
├── templates/
└── tests/
```

#### 1.2 配置文件 (config/settings.toml)
```toml
[app]
name = "审计日报生成器"
version = "4.0.0"

[paths]
work_dir = "D:\\01- 工作"
data_dir = "data"

[llm]
model_id = "gemini-2.5-flash"
temperature = 0.2
max_tokens = 2048
max_retries = 3

[scanner]
allowed_extensions = [".xlsx", ".xls", ".pptx", ".pdf"]
ignored_patterns = ["~$*", "*.tmp"]
max_workers = 4
excel_max_rows = 50
pdf_max_pages = 5
```

#### 1.3 敏感配置 (config/.secrets.toml)
```toml
[api]
google_api_key = "${GOOGLE_API_KEY}"

[proxy]
http_proxy = "http://127.0.0.1:10808"
https_proxy = "http://127.0.0.1:10808"
```

#### 1.4 依赖文件 (requirements.txt)
```
google-genai>=1.0.0
pydantic>=2.0.0
dynaconf>=3.2.0
rich>=13.0.0
pandas>=2.0.0
openpyxl>=3.1.0
python-pptx>=0.6.0
pdfplumber>=0.10.0
jinja2>=3.1.0
```

---

### 阶段 2: 数据模型层

#### 2.1 src/models/schemas.py
定义 Pydantic 数据模型:
- `WorkItem`: 单项工作记录 (category, content, status, quantitative)
- `RiskItem`: 风险问题记录 (severity, description)
- `DailyReportData`: 日报结构化数据 (date, summary, achievements, risks, plans)
- `FileContext`: 文件扫描结果
- `ScanResult`: 扫描汇总结果

**关键点**: 所有字段包含类型提示和中文 description

---

### 阶段 3: 核心工具层

#### 3.1 src/core/logger.py
- 使用 Python logging 模块
- 配置文件和控制台双输出
- 日志级别: INFO (正常), WARNING (文件解析失败), ERROR (致命错误)

#### 3.2 src/core/config.py
- 使用 dynaconf 加载 settings.toml 和 .secrets.toml
- 支持环境变量覆盖 (如 GOOGLE_API_KEY)
- 单例模式，全局配置访问
- 提供属性: work_dir, llm_config, scanner_config, api_key

#### 3.3 src/utils/text_tools.py
- `truncate_text(text: str, max_chars: int) -> str`: 智能截断
- `estimate_tokens(text: str) -> int`: Token 估算 (简单按字符数/4)

---

### 阶段 4: LLM 交互层

#### 4.1 src/core/llm.py
**核心功能**:
1. 初始化 Google GenAI 客户端 (设置代理)
2. `generate_report()`: 生成日报
   - 使用 `response_mime_type="application/json"` 强制 JSON 输出
   - 传入 Pydantic schema 到 system prompt
   - 实现指数退避重试 (处理 429 错误)
   - 解析 JSON 为 DailyReportData 对象
3. `generate_monthly_summary()`: 生成月度汇总

**迁移来源**: Ai_Daily_Report.py L305-366

---

### 阶段 5: 业务服务层

#### 5.1 src/services/file_scanner.py
**核心功能**:
1. `scan_today_files() -> ScanResult`: 扫描今日修改的文件
   - 使用 `ThreadPoolExecutor` 并行处理 (max_workers=4)
   - 数据完整性校验: 记录 total/success/error 数量
2. `_extract_content(file_path) -> FileContext`: 分发到具体解析器
3. `_parse_excel(file_path) -> str`:
   - 使用 pandas 读取所有 Sheet
   - 矢量化过滤空行 (dropna)
   - 限制行数 (excel_max_rows)
   - 转换为 Markdown 表格
4. `_parse_pdf(file_path) -> str`: 使用 pdfplumber，限制页数
5. `_parse_pptx(file_path) -> str`: 使用 python-pptx 提取文本

**迁移来源**: Ai_Daily_Report.py L39-116

#### 5.2 src/services/history_mgr.py
**核心功能**:
1. `save_report(report: DailyReportData) -> Path`:
   - 序列化为 JSON 存入 `data/db/YYYY-MM-DD.json`
2. `get_yesterday_plan(target_date) -> List[str]`:
   - 读取昨日 JSON 文件的 `plans` 字段
   - **不再使用正则表达式解析 Markdown**
3. `get_month_reports(year_month) -> List[DailyReportData]`:
   - 读取指定月份所有 JSON 文件

**迁移来源**: Ai_Daily_Report.py L143-190 (替代正则解析逻辑)

#### 5.3 src/services/report_gen.py
**核心功能**:
1. 初始化 Jinja2 环境 (加载 templates/)
2. `render_markdown(report: DailyReportData) -> str`:
   - 使用 Jinja2 模板渲染 Markdown
3. `save_markdown(content, report_date, output_dir) -> Path`:
   - 保存到 `data/reports/YYYY-MM/YYYY-MM-DD.md`

**迁移来源**: Ai_Daily_Report.py L118-140

---

### 阶段 6: 模板文件

#### 6.1 templates/system_prompt.md
```markdown
你是专业的内审专员 AI 助手。根据用户口述、文件证据和昨日计划生成审计日报。

## 输出要求
1. 严格 JSON 格式 (符合 DailyReportData schema)
2. 数据勾稽 (将文件中的具体指标融入 achievements)
3. 昨日对照 (评估昨日计划完成情况)
4. 风险识别 (标注严重程度: 高/中/低)
5. 风格: 客观、精炼、量化、专业

## JSON Schema
{schema}

## 输入数据
【用户口述】
{user_input}

【昨日计划】
{yesterday_plan}

【今日文件证据】
{file_context}
```

#### 6.2 templates/report_template.md (Jinja2)
包含以下部分:
- 标题 (日期)
- 今日工作概述
- 昨日计划完成情况 (可选)
- 今日完成工作 (循环 achievements)
- 风险与问题 (循环 risks)
- 明日工作计划 (循环 plans)

---

### 阶段 7: 主程序入口

#### 7.1 main.py
**业务流程**:
1. 初始化 (Config, Logger, Console)
2. 解析命令行参数 (argparse):
   - `-i/--input`: 直接指定工作内容
   - `--monthly YYYY-MM`: 生成月度汇总
   - `--list`: 列出已有日报
   - `--no-save`: 不保存日报
3. 初始化服务 (Scanner, HistoryManager, ReportGenerator, LLMClient)
4. 执行业务逻辑:
   - **日报生成**:
     1. 并行扫描文件 (显示进度条)
     2. 读取昨日计划 (从 JSON)
     3. 获取用户输入 (CLI 交互或 -i 参数)
     4. LLM 生成报告 (JSON 格式)
     5. 保存 JSON (data/db/)
     6. 渲染 Markdown (data/reports/)
     7. 预览 (rich.Markdown)
   - **月度汇总**: 读取月份所有 JSON，调用 LLM 生成汇总
   - **列表日报**: 列出 data/db/ 下所有日报

**迁移来源**: Ai_Daily_Report.py L193-219 (用户输入), L368-450 (主流程)

---

## 关键文件路径

**原始代码**:
- `D:\03- Program\01- common\01- ai daily report\Ai_Daily_Report.py`

**新建文件** (按创建顺序):
1. `config/settings.toml`
2. `config/.secrets.toml`
3. `requirements.txt`
4. `src/models/schemas.py`
5. `src/core/logger.py`
6. `src/core/config.py`
7. `src/utils/text_tools.py`
8. `src/core/llm.py`
9. `src/services/file_scanner.py`
10. `src/services/history_mgr.py`
11. `src/services/report_gen.py`
12. `templates/system_prompt.md`
13. `templates/report_template.md`
14. `main.py`

---

## 数据流转

```
用户输入 ──┐
           ├──> LLM Client ──> DailyReportData (JSON)
文件扫描 ──┤                        │
           │                        ├──> HistoryManager.save_report()
昨日计划 ──┘                        │    └──> data/db/YYYY-MM-DD.json
                                    │
                                    └──> ReportGenerator.render_markdown()
                                         └──> data/reports/YYYY-MM/YYYY-MM-DD.md
```

---

## 验证方法

### 1. 单元测试
```bash
pytest tests/test_file_scanner.py  # 测试文件解析和并行扫描
pytest tests/test_history_mgr.py   # 测试 JSON 存储与读取
pytest tests/test_report_gen.py    # 测试 Jinja2 渲染
```

### 2. 集成测试
```bash
# 生成日报 (交互模式)
python main.py

# 生成日报 (命令行模式)
python main.py -i "今日完成XX审计，发现YY问题"

# 生成月度汇总
python main.py --monthly 2026-01

# 列出已有日报
python main.py --list
```

### 3. 数据完整性校验
- 检查 `data/db/YYYY-MM-DD.json` 是否存在且格式正确
- 检查 `data/reports/YYYY-MM/YYYY-MM-DD.md` 是否存在且可读
- 验证次日能从 JSON 读取昨日计划 (不再依赖正则)
- 验证文件扫描的 success_count + error_count == total_files

### 4. 性能验证
- 对比重构前后文件扫描时间 (应显著减少，因为并行处理)
- 验证大文件 (50+ Sheet Excel) 不会导致 Token 超限

---

## 技术决策

| 决策点 | 方案 | 理由 |
|---|---|---|
| 配置管理 | dynaconf + TOML | 支持环境变量覆盖 |
| 数据模型 | Pydantic | 强类型校验 + JSON 序列化 |
| 并行处理 | ThreadPoolExecutor | I/O 密集型，线程池足够 |
| 模板引擎 | Jinja2 | 标准方案，易维护 |
| CLI 框架 | argparse + rich | 保持原接口 + 美化输出 |
| 历史存储 | JSON + Markdown 双重存储 | 程序可靠读取 + 人类可读 |
| LLM 输出 | 强制 JSON Mode | 避免正则解析不稳定 |

---

## 注意事项

1. **配置迁移**: 将 Ai_Daily_Report.py L16-30 的硬编码值移至 settings.toml
2. **API Key 安全**: .secrets.toml 必须加入 .gitignore
3. **类型提示**: 所有函数必须包含类型提示 (符合 CLAUDE.md 要求)
4. **中文注释**: 关键业务逻辑包含中文注释
5. **错误处理**: 文件解析失败不能静默，必须记录到 logger 和 ScanResult.error_count
6. **数据完整性**: 每个数据处理环节包含校验 (行数勾稽、空值率检测)
7. **pandas 矢量化**: Excel 处理必须使用 pandas，严禁 for 循环
8. **金额计算**: 如涉及金额计算，使用 decimal 库 (当前版本未涉及)
