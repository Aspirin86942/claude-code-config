# WPS Report Spider 功能增强计划

## Context

用户请求三项功能增强，源于实际运行体验：
1. **secCode 前导零丢失**：股票代码如 "000563" 在 WPS 中显示为 "563"，影响数据准确性
2. **结果表缺少筛选**：159 行数据无法快速按列过滤，需要手动添加筛选器
3. **整格标红过于突兀**：当前整个单元格填充橙色背景，希望仅标红关键词文字

## Implementation Plan

### Feature 1: secCode 文本格式（保留前导零）

**问题**：`write_outputs_to_wps()` 第 2958-2959 行虽已转换 `astype("string")`，但 WPS 仍可能将纯数字字符串推断为数值。

**实现**：
1. 在 `write_outputs_to_wps()` 写入结果后，立即调用新函数 `apply_secCode_text_format()`
2. 该函数遍历 secCode 列所有单元格，设置 `.NumberFormat = "@"`（WPS 文本格式代码）

**关键代码**（新增函数，约第 2335 行后）：
```python
def apply_secCode_text_format(sheet_name: str, row_count: int) -> None:
    worksheet = get_worksheet(sheet_name)
    if worksheet is None:
        return

    # 获取 secCode 列索引（第 3 列，从 1 开始）
    # 根据 export_cols 定义，secCode 是第 3 个导出列
    secCode_col_index = 3

    for row_num in range(2, row_count + 2):
        cell = worksheet.Cells(row_num, secCode_col_index)
        cell.NumberFormat = "@"  # Excel/WPS 文本格式
```

**调用点**（第 2964 行后）：
```python
write_sheet_df(export_df, RESULT_SHEET)
apply_secCode_text_format(RESULT_SHEET, len(export_df))  # 新增调用
```

---

### Feature 2: 结果表自动筛选器

**实现**：
1. 新增函数 `apply_header_auto_filter()`
2. 对标题行（第 1 行）启用 `AutoFilter`

**关键代码**（新增函数，约第 2355 行后）：
```python
def apply_header_auto_filter(sheet_name: str, column_count: int) -> None:
    worksheet = get_worksheet(sheet_name)
    if worksheet is None or column_count == 0:
        return

    # 计算最后一列的字母（如第 33 列 = AG）
    last_col_letter = xl.Columns(column_count).Address.split('$')[1]
    header_range = worksheet.Range(f"A1:{last_col_letter}1")
    header_range.AutoFilter = True
```

**调用点**（第 2964 行后）：
```python
write_sheet_df(export_df, RESULT_SHEET)
apply_header_auto_filter(RESULT_SHEET, len(export_df.columns))  # 新增调用
```

---

### Feature 3: 仅高亮关键词文本（标红 + 背景）

**当前行为**：`apply_keyword_highlight()` 第 2327-2328 行对整个单元格应用字体和背景色。

**新行为**：使用 `Characters()` 方法定位关键词子字符串，仅对该部分应用红色字体 + 浅色背景。

**修改函数**：`apply_keyword_highlight()`（第 2279-2333 行）

**关键改动**：
```python
# 原代码（整格高亮）
if hit_flag:
    cell.ClearFormats()
    cell.Font.Color = font_color
    cell.Interior.Color = fill_color

# 新代码（部分文本高亮）
if hit_flag and cell_text:
    cell.ClearFormats()  # 先清除整格格式

    # 查找所有匹配关键词
    matches = list(keyword_pattern.finditer(cell_text))
    for match in matches:
        start_pos = match.start() + 1  # Characters 从 1 开始
        length = match.end() - match.start()

        try:
            char_obj = cell.Characters(start_pos, length)
            char_obj.Font.Color = font_color
            char_obj.Font.Interior.Color = fill_color  # 仅背景填充关键词
        except (AttributeError, IndexError):
            # WPS 不支持 Characters，降级为整格高亮
            cell.Font.Color = font_color
            cell.Interior.Color = fill_color
            break
```

**降级策略**：捕获 `AttributeError` 或 `IndexError`，回退到整格高亮，确保兼容性。

---

## Critical Files

| 文件 | 行号范围 | 修改内容 |
|------|----------|----------|
| `wps_report_spider.py` | 2335-2355 | 新增 `apply_secCode_text_format()` |
| `wps_report_spider.py` | 2355-2375 | 新增 `apply_header_auto_filter()` |
| `wps_report_spider.py` | 2279-2333 | 修改 `apply_keyword_highlight()` |
| `wps_report_spider.py` | 2964-2970 | 增加三个新函数调用 |

---

## Verification

### 测试步骤
1. **本地语法检查**：`python -m py_compile wps_report_spider.py`
2. **现有测试**：`pytest tests/ -v`（确保无回归）
3. **WPS 实测**：
   - 运行脚本，检查 result 表：
     - secCode 列显示 "000563" 而非 "563"
     - 标题行有筛选下拉箭头
     - 关键词（如"激光"）文字红色 + 浅橙色背景，非关键词不变色

### 验收标准
- [ ] secCode 列公式 `=ISTEXT(A2)` 返回 TRUE
- [ ] 可点击筛选器按条件过滤
- [ ] 关键词高亮不影响相邻文字

---

## 实施顺序 - 多子代理并行

三项功能相互独立，可并行实施：

| 子代理 | 功能 | 关键文件/行号 |
|--------|------|----------|
| Agent 1 | Feature 1: secCode 文本格式 | 新增 `apply_secCode_text_format()` (2335 行后)，修改调用点 (2964 行后) |
| Agent 2 | Feature 2: AutoFilter | 新增 `apply_header_auto_filter()` (2355 行后)，修改调用点 (2964 行后) |
| Agent 3 | Feature 3: 部分高亮 | 修改 `apply_keyword_highlight()` (2279-2333 行) |

实施完成后：
1. 运行语法检查：`python -m py_compile wps_report_spider.py`
2. 运行现有测试：`pytest tests/ -v`
3. WPS 实测验证
