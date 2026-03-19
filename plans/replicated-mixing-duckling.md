# 计划：FileScanner 新增文件类型支持

## 需求分析

当前支持：`.xlsx`, `.xls`, `.pptx`, `.pdf`

建议新增：
| 类型 | 用途 | 实现复杂度 | 依赖 |
|------|------|-----------|------|
| `.txt` | 纯文本笔记 | 低 | 无 |
| `.md` | Markdown 文档 | 低 | 无 |
| `.docx` | Word 文档 | 中 | `python-docx` |

## 实现方案

### 修改文件

1. **`src/services/file_scanner.py`** - 添加解析方法
2. **`config/settings.toml`** - 添加扩展名
3. **`requirements.txt`** - 添加 `python-docx`

### 代码变更

#### 1. `_extract_content()` 添加分发 (约 L128)

```python
elif file_type in ['.txt', '.md']:
    content = self._parse_text(file_path)
elif file_type == '.docx':
    content = self._parse_docx(file_path)
```

#### 2. 新增 `_parse_text()` 方法

```python
def _parse_text(self, file_path: Path) -> str:
    """解析纯文本文件"""
    return file_path.read_text(encoding='utf-8')
```

#### 3. 新增 `_parse_docx()` 方法

```python
def _parse_docx(self, file_path: Path) -> str:
    """解析 Word 文档"""
    from docx import Document
    doc = Document(file_path)
    return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
```

#### 4. `config/settings.toml` 更新

```toml
allowed_extensions = [".xlsx", ".xls", ".pptx", ".pdf", ".txt", ".md", ".docx"]
```

#### 5. `requirements.txt` 添加

```
python-docx>=1.1.0
```

## 验证步骤

1. `pip install python-docx`
2. 在工作目录放置测试文件 (.txt, .md, .docx)
3. 运行 `python main.py` 确认文件被扫描
4. 检查生成的日报是否包含新文件内容
