# 用户指南

## 目录

- [快速开始](#快速开始)
- [MCP 配置](#mcp-配置)
  - [Trae IDE](#trae-ide)
  - [Claude Desktop](#claude-desktop)
  - [Cherry Studio](#cherry-studio)
- [作为 Python 库使用](#作为-python-库使用)
- [转换选项](#转换选项)
- [常见问题](#常见问题)

---

## 快速开始

### 安装

```bash
pip install mcp-document-converter
```

### 基本使用

```python
from mcp_document_converter import DocumentConverter

converter = DocumentConverter()

# Markdown 转 HTML
result = converter.convert("document.md", "html")
print(f"输出: {result.output_path}")

# HTML 转 PDF
result = converter.convert("document.html", "pdf")

# DOCX 转 Markdown
result = converter.convert("document.docx", "markdown")
```

---

## MCP 配置

### Trae IDE

添加到 MCP 配置文件：

```json
{
  "mcpServers": {
    "mcp-document-converter": {
      "command": "uvx",
      "args": ["mcp-document-converter"]
    }
  }
}
```

### Claude Desktop

```json
{
  "mcpServers": {
    "mcp-document-converter": {
      "command": "uvx",
      "args": ["mcp-document-converter"]
    }
  }
}
```

### Cherry Studio

![Cherry Studio 配置](../images/1770102311686.png)

![Cherry Studio 使用](../images/1770102446855.png)

---

## 作为 Python 库使用

### 基本转换

```python
from mcp_document_converter import DocumentConverter

converter = DocumentConverter()
result = converter.convert("input.md", "html")

if result.success:
    print(f"已转换到: {result.output_path}")
    print(f"内容: {result.content[:100]}...")
else:
    print(f"错误: {result.error_message}")
```

### 自定义注册表

```python
from mcp_document_converter import DocumentConverter
from mcp_document_converter.registry import ConverterRegistry
from mcp_document_converter.parsers import MarkdownParser, HTMLParser
from mcp_document_converter.renderers import HTMLRenderer, PDFRenderer

# 创建自定义注册表
registry = ConverterRegistry()
registry.register_parser(MarkdownParser())
registry.register_parser(HTMLParser())
registry.register_renderer(HTMLRenderer())
registry.register_renderer(PDFRenderer())

# 使用自定义注册表
converter = DocumentConverter(registry)
```

### 操作 DocumentIR

```python
from mcp_document_converter import DocumentConverter

converter = DocumentConverter()

# 解析为中间表示
document = converter.convert_to_ir("input.md")

# 修改文档
document.title = "新标题"
document.metadata["custom_field"] = "value"

# 渲染为多种格式
converter.render_from_ir(document, "html", output_path="output.html")
converter.render_from_ir(document, "pdf", output_path="output.pdf")
```

### 批量转换

```python
from pathlib import Path
from mcp_document_converter import DocumentConverter

converter = DocumentConverter()

# 转换目录下所有 Markdown 文件
for md_file in Path("docs").glob("*.md"):
    result = converter.convert(md_file, "html")
    print(f"已转换 {md_file} -> {result.output_path}")
```

---

## 转换选项

### HTML 选项

```python
result = converter.convert(
    "input.md",
    "html",
    options={
        "css": "body { font-family: Arial; }",
        "template": "default",
        "preserve_metadata": True,
        "extract_images": True
    }
)
```

### PDF 选项

```python
result = converter.convert(
    "input.md",
    "pdf",
    options={
        "template": "default",
        "css": "@page { size: A4; }",
        "preserve_metadata": True
    }
)
```

### Markdown 选项

```python
result = converter.convert(
    "input.html",
    "markdown",
    options={
        "preserve_metadata": True,
        "code_style": "fenced"
    }
)
```

---

## 常见问题

### Q: 支持哪些格式？

**A:** 转换器支持 5 种格式：
- **输入：** Markdown、HTML、DOCX、PDF、Text
- **输出：** Markdown、HTML、DOCX、PDF、Text

### Q: 如何处理转换错误？

```python
result = converter.convert("input.md", "html")

if not result.success:
    print(f"错误: {result.error_message}")
    # 处理错误
```

### Q: 可以扩展自定义解析器/渲染器吗？

**A:** 可以！创建继承自 `BaseParser` 或 `BaseRenderer` 的类：

```python
from mcp_document_converter.core.parser import BaseParser
from mcp_document_converter.core.ir import DocumentIR

class MyParser(BaseParser):
    @property
    def supported_extensions(self):
        return [".myext"]
    
    @property
    def format_name(self):
        return "myformat"
    
    def parse(self, source, **options):
        # 你的解析逻辑
        return DocumentIR(title="我的文档")

# 注册
from mcp_document_converter.registry import get_registry
get_registry().register_parser(MyParser())
```

### Q: 在 Windows 上能正常工作吗？

**A:** 是的，转换器支持 Windows、macOS 和 Linux。对于使用 WeasyPrint 的 PDF 渲染，在 Windows 上可能需要安装 GTK 依赖。

### Q: 转换时如何保留图片？

**A:** 图片会自动提取和保留。使用 `extract_images` 选项：

```python
result = converter.convert(
    "input.docx",
    "html",
    options={"extract_images": True}
)
```

### Q: 可以不保存文件直接获取内容吗？

**A:** 可以，`ConversionResult.content` 包含输出内容：

```python
result = converter.convert("input.md", "html")

if result.success:
    html_content = result.content
    # 直接使用内容，无需保存
```
