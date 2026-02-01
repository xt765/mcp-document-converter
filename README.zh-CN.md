# MCP Document Converter

MCP（模型上下文协议）文档转换器 - 支持多格式文档转换的 MCP 工具，让 AI 智能体能够轻松转换各种文档格式。

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP Protocol](https://img.shields.io/badge/MCP-Protocol-green.svg)](https://modelcontextprotocol.io/)

## 功能特性

- **多格式支持**：支持 Markdown、HTML、DOCX、PDF、Text 等 5 种主流文档格式
- **双向转换**：任意格式之间都可以相互转换（5×5=25 种转换组合）
- **MCP 协议**：符合 MCP 标准，可作为 AI 助手（如 Trae IDE）的工具使用
- **插件架构**：易于扩展新的解析器和渲染器
- **代码高亮**：HTML 和 PDF 输出支持语法高亮
- **样式定制**：支持自定义 CSS 样式
- **元数据保留**：转换过程中保留文档标题、作者、创建时间等元数据

## 支持的格式

### 解析格式（输入）

| 格式 | 扩展名 | MIME 类型 | 特性 |
|------|--------|-----------|------|
| Markdown | .md, .markdown, .mdown, .mkd | text/markdown | 支持 YAML Front Matter、GFM 扩展 |
| HTML | .html, .htm | text/html | 支持语义化标签解析 |
| DOCX | .docx | application/vnd.openxmlformats-officedocument.wordprocessingml.document | 支持样式、表格、图片 |
| PDF | .pdf | application/pdf | 支持文本提取和结构识别 |
| Text | .txt, .text | text/plain | 支持自动编码检测和结构识别 |

### 渲染格式（输出）

| 格式 | 扩展名 | MIME 类型 | 特性 |
|------|--------|-----------|------|
| HTML | .html | text/html | 美观的样式、代码高亮、响应式设计 |
| Markdown | .md | text/markdown | 标准 Markdown 格式、YAML Front Matter |
| DOCX | .docx | application/vnd.openxmlformats-officedocument.wordprocessingml.document | Word 文档格式、保留样式 |
| PDF | .pdf | application/pdf | 使用 WeasyPrint 生成、支持分页 |
| Text | .txt | text/plain | 纯文本、保留基本格式 |

## 转换矩阵

| 源格式 \ 目标格式 | HTML | PDF | Markdown | DOCX | Text |
|------------------|:----:|:---:|:--------:|:----:|:----:|
| **Markdown**     |  ✅  |  ✅  |    ✅    |  ✅  |  ✅  |
| **HTML**         |  ✅  |  ✅  |    ✅    |  ✅  |  ✅  |
| **DOCX**         |  ✅  |  ✅  |    ✅    |  ✅  |  ✅  |
| **PDF**          |  ✅  |  ✅  |    ✅    |  ✅  |  ✅  |
| **Text**         |  ✅  |  ✅  |    ✅    |  ✅  |  ✅  |

## 安装

### 前提条件

- Python 3.10 或更高版本
- 支持 MCP 的 AI 工具，如 Trae IDE、Claude Desktop 等

### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/yourusername/mcp-document-converter.git
cd mcp-document-converter

# 安装依赖
pip install -e .
```

## 配置

### 在 Trae IDE 中使用

将以下内容添加到 Trae IDE 的 MCP 配置中：

```json
{
  "mcpServers": {
    "mcp-document-converter": {
      "command": "python",
      "args": ["-m", "mcp_document_converter.server"]
    }
  }
}
```

如果使用 `uvx`：

```json
{
  "mcpServers": {
    "mcp-document-converter": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/yourusername/mcp-document-converter",
        "mcp-document-converter"
      ]
    }
  }
}
```

## 使用方法

### 作为 MCP 工具使用

配置完成后，AI 助手可以直接调用以下工具：

#### 1. convert_document（推荐）

使用统一接口转换任何支持的文档类型。

```python
# Markdown 转 HTML
convert_document(
    source_path="document.md",
    target_format="html"
)

# HTML 转 PDF
convert_document(
    source_path="document.html",
    target_format="pdf"
)

# DOCX 转 Markdown
convert_document(
    source_path="document.docx",
    target_format="markdown"
)

# 带选项的转换
convert_document(
    source_path="document.md",
    target_format="html",
    output_path="output.html",
    options={
        "css": "custom.css",
        "preserve_metadata": True
    }
)
```

#### 2. list_supported_formats

列出所有支持的文档格式。

```python
list_supported_formats()
```

#### 3. get_conversion_matrix

获取完整的格式转换矩阵。

```python
get_conversion_matrix()
```

#### 4. can_convert

检查是否支持从源格式转换到目标格式。

```python
can_convert(source_format="markdown", target_format="pdf")
```

#### 5. get_format_info

获取特定格式的详细信息。

```python
get_format_info(format="markdown")
```

### 作为 Python 库使用

```python
from mcp_document_converter import DocumentConverter
from mcp_document_converter.registry import get_registry
from mcp_document_converter.parsers import MarkdownParser, HTMLParser
from mcp_document_converter.renderers import HTMLRenderer, PDFRenderer

# 注册解析器和渲染器
registry = get_registry()
registry.register_parser(MarkdownParser())
registry.register_parser(HTMLParser())
registry.register_renderer(HTMLRenderer())
registry.register_renderer(PDFRenderer())

# 创建转换器
converter = DocumentConverter(registry)

# 转换文档
result = converter.convert(
    source="input.md",
    target_format="html",
    output_path="output.html"
)

if result.success:
    print(f"✅ 转换成功: {result.output_path}")
else:
    print(f"❌ 转换失败: {result.error_message}")
```

## 工具接口详情

### convert_document

将文档从一种格式转换为另一种格式。

**参数：**

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| `source_path` | string | ✅ | 源文件路径，支持绝对路径或相对路径 |
| `target_format` | string | ✅ | 目标格式：`html`、`pdf`、`markdown`、`docx`、`text` |
| `output_path` | string | ❌ | 输出文件路径（可选，默认使用源文件名） |
| `source_format` | string | ❌ | 源格式（可选，自动检测文件扩展名） |
| `options` | object | ❌ | 转换选项 |

**options 选项：**

| 选项名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `template` | string | - | 模板名称 |
| `css` | string | - | 自定义 CSS 样式 |
| `preserve_metadata` | boolean | true | 是否保留元数据 |
| `extract_images` | boolean | true | 是否提取图片 |

**示例：**

```json
{
  "source_path": "/path/to/document.md",
  "target_format": "html",
  "output_path": "/path/to/output.html",
  "options": {
    "css": "body { font-family: Arial; }",
    "preserve_metadata": true
  }
}
```

## 架构设计

```
┌─────────────────────────────────────────────────────────────────┐
│                    MCP Document Converter                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Parsers (解析器)                    Renderers (渲染器)         │
│   ┌─────────────┐                    ┌─────────────┐            │
│   │ Markdown    │ ────────────────→  │ HTML        │            │
│   │ DOCX        │ ────────────────→  │ PDF         │            │
│   │ HTML        │ ────────────────→  │ Markdown    │            │
│   │ PDF         │ ────────────────→  │ DOCX        │            │
│   │ Text        │ ────────────────→  │ Text        │            │
│   └─────────────┘                    └─────────────┘            │
│          ↓                                    ↓                 │
│   ┌─────────────────────────────────────────────────────┐       │
│   │         统一中间表示 (Intermediate Representation)   │       │
│   │  - Document Tree (文档树)                           │       │
│   │  - Metadata (元数据)                                │       │
│   │  - Assets (图片、附件等资源)                         │       │
│   └─────────────────────────────────────────────────────┘       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 核心组件

1. **DocumentIR（中间表示）**：所有文档的统一抽象，包含文档树、元数据、资源等
2. **BaseParser（解析器基类）**：定义了解析器的接口，将各种格式解析为 DocumentIR
3. **BaseRenderer（渲染器基类）**：定义了渲染器的接口，将 DocumentIR 渲染为各种格式
4. **ConverterRegistry（注册表）**：管理所有解析器和渲染器，提供格式查找和自动匹配
5. **DocumentConverter（转换引擎）**：协调解析器和渲染器完成文档转换

## 扩展开发

### 添加新的解析器

```python
from typing import List, Union
from pathlib import Path
from mcp_document_converter.core.parser import BaseParser
from mcp_document_converter.core.ir import DocumentIR, Node, NodeType

class MyParser(BaseParser):
    @property
    def supported_extensions(self) -> List[str]:
        return [".myext"]
    
    @property
    def format_name(self) -> str:
        return "myformat"
    
    @property
    def mime_types(self) -> List[str]:
        return ["application/x-myformat"]
    
    def parse(self, source: Union[str, Path, bytes], **options) -> DocumentIR:
        # 读取源文件
        content = self._read_source(source)
        
        # 解析为 DocumentIR
        document = DocumentIR()
        document.title = "My Document"
        
        # 添加内容节点
        document.add_node(Node(
            type=NodeType.PARAGRAPH,
            content=[Node(type=NodeType.TEXT, content="Hello World")]
        ))
        
        return document
```

### 添加新的渲染器

```python
from typing import Any
from mcp_document_converter.core.renderer import BaseRenderer
from mcp_document_converter.core.ir import DocumentIR

class MyRenderer(BaseRenderer):
    @property
    def output_extension(self) -> str:
        return ".myext"
    
    @property
    def format_name(self) -> str:
        return "myformat"
    
    @property
    def mime_type(self) -> str:
        return "application/x-myformat"
    
    def render(self, document: DocumentIR, **options: Any) -> str:
        # 将 DocumentIR 渲染为目标格式
        parts = []
        
        if document.title:
            parts.append(f"# {document.title}")
        
        for node in document.content:
            # 渲染每个节点
            pass
        
        return "\n".join(parts)
```

### 注册扩展

```python
from mcp_document_converter.registry import get_registry

# 注册新的解析器和渲染器
registry = get_registry()
registry.register_parser(MyParser())
registry.register_renderer(MyRenderer())
```

## 测试

```bash
# 运行所有测试
python tests/test_conversion.py

# 运行特定测试
python tests/test_conversion.py::test_markdown_to_html
```

## 环境变量

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| `MCP_CONVERTER_LOG_LEVEL` | 日志级别 | `INFO` |
| `MCP_CONVERTER_TEMP_DIR` | 临时文件目录 | 系统临时目录 |

## 依赖

### 核心依赖
- `mcp` >= 1.0.0 - MCP 协议实现
- `pydantic` >= 2.0.0 - 数据验证

### 解析器依赖
- `markdown` >= 3.5.0 - Markdown 解析
- `beautifulsoup4` >= 4.12.0 - HTML 解析
- `python-docx` >= 1.1.0 - DOCX 解析
- `PyPDF2` >= 3.0.0 - PDF 解析
- `chardet` >= 5.0.0 - 编码检测
- `pyyaml` >= 6.0.0 - YAML 解析

### 渲染器依赖
- `weasyprint` >= 60.0 - PDF 渲染
- `pygments` >= 2.17.0 - 代码高亮
- `jinja2` >= 3.1.0 - 模板引擎

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 相关项目

- [MCP Document Reader](https://github.com/xt765/mcp_documents_reader) - MCP 文档阅读器，支持读取多种文档格式
- [Model Context Protocol](https://modelcontextprotocol.io/) - 模型上下文协议官方文档
