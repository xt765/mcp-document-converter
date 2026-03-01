# API 参考

## 目录

- [核心类](#核心类)
  - [DocumentIR](#documentir)
  - [Node](#node)
  - [NodeType](#nodetype)
  - [Asset](#asset)
- [转换引擎](#转换引擎)
  - [DocumentConverter](#documentconverter)
  - [ConversionResult](#conversionresult)
- [注册表](#注册表)
  - [ConverterRegistry](#converterregistry)
- [解析器](#解析器)
  - [BaseParser](#baseparser)
  - [MarkdownParser](#markdownparser)
  - [HTMLParser](#htmlparser)
  - [DOCXParser](#docxparser)
  - [PDFParser](#pdfparser)
  - [TextParser](#textparser)
- [渲染器](#渲染器)
  - [BaseRenderer](#baserenderer)
  - [HTMLRenderer](#htmlrenderer)
  - [PDFRenderer](#pdfrenderer)
  - [MarkdownRenderer](#markdownrenderer)
  - [DOCXRenderer](#docxrenderer)
  - [TextRenderer](#textrenderer)
- [MCP 工具](#mcp-工具)
  - [convert_document](#convert_document)
  - [list_supported_formats](#list_supported_formats)
  - [get_conversion_matrix](#get_conversion_matrix)
  - [can_convert](#can_convert)
  - [get_format_info](#get_format_info)

---

## 核心类

### DocumentIR

所有文档格式的中间表示。

```python
from mcp_document_converter.core.ir import DocumentIR, Node, NodeType

document = DocumentIR(
    title="我的文档",
    author="作者名称",
    metadata={"key": "value"}
)

# 添加内容节点
document.add_node(Node(
    type=NodeType.PARAGRAPH,
    content=[Node(type=NodeType.TEXT, content="你好世界")]
))
```

**属性：**

| 属性 | 类型 | 描述 |
|------|------|------|
| `title` | `Optional[str]` | 文档标题 |
| `author` | `Optional[str]` | 文档作者 |
| `created_at` | `Optional[datetime]` | 创建时间 |
| `modified_at` | `Optional[datetime]` | 修改时间 |
| `metadata` | `Dict[str, Any]` | 额外元数据 |
| `content` | `List[Node]` | 文档内容树 |
| `assets` | `List[Asset]` | 嵌入资源 |
| `styles` | `Dict[str, Any]` | 样式信息 |

**方法：**

| 方法 | 描述 |
|------|------|
| `add_node(node)` | 添加节点到文档内容 |
| `add_asset(asset)` | 添加资源到文档 |
| `get_text_content()` | 提取纯文本内容 |
| `to_dict()` | 转换为字典用于序列化 |

---

### Node

文档树节点。

```python
from mcp_document_converter.core.ir import Node, NodeType

# 创建标题
heading = Node(
    type=NodeType.HEADING,
    content=[Node(type=NodeType.TEXT, content="标题")],
    attributes={"level": 1}
)

# 创建带格式的段落
paragraph = Node(
    type=NodeType.PARAGRAPH,
    content=[
        Node(type=NodeType.TEXT, content="普通文本 "),
        Node(type=NodeType.STRONG, content=[Node(type=NodeType.TEXT, content="粗体")]),
    ]
)
```

**属性：**

| 属性 | 类型 | 描述 |
|------|------|------|
| `type` | `NodeType` | 节点类型 |
| `content` | `Union[str, List[Node]]` | 文本内容或子节点 |
| `attributes` | `Dict[str, Any]` | 节点属性 |

---

### NodeType

文档节点类型枚举。

**块级元素：**

| 类型 | 描述 |
|------|------|
| `DOCUMENT` | 文档根节点 |
| `HEADING` | 标题 (h1-h6) |
| `PARAGRAPH` | 段落 |
| `CODE_BLOCK` | 代码块 |
| `LIST` | 有序/无序列表 |
| `LIST_ITEM` | 列表项 |
| `TABLE` | 表格 |
| `TABLE_ROW` | 表格行 |
| `TABLE_CELL` | 表格单元格 |
| `BLOCKQUOTE` | 引用块 |
| `HORIZONTAL_RULE` | 分隔线 |
| `PAGE_BREAK` | 分页符 |

**行内元素：**

| 类型 | 描述 |
|------|------|
| `TEXT` | 纯文本 |
| `LINK` | 超链接 |
| `IMAGE` | 图片 |
| `CODE_INLINE` | 行内代码 |
| `EMPHASIS` | 斜体 |
| `STRONG` | 粗体 |
| `STRIKETHROUGH` | 删除线 |
| `SUBSCRIPT` | 下标 |
| `SUPERSCRIPT` | 上标 |
| `LINE_BREAK` | 换行 |

---

### Asset

文档资源（图片、附件等）。

```python
from mcp_document_converter.core.ir import Asset

asset = Asset(
    id="img_001",
    type="image",
    mime_type="image/png",
    data=b"...",
    filename="image.png"
)
```

---

## 转换引擎

### DocumentConverter

协调解析器和渲染器的主转换引擎。

```python
from mcp_document_converter import DocumentConverter

converter = DocumentConverter()

# 简单转换
result = converter.convert("input.md", "html")

# 指定输出路径
result = converter.convert("input.md", "html", output_path="output.html")

# 使用选项
result = converter.convert(
    "input.md",
    "pdf",
    options={"template": "default", "css": "custom.css"}
)

if result.success:
    print(f"已转换: {result.output_path}")
else:
    print(f"错误: {result.error_message}")
```

**方法：**

| 方法 | 描述 |
|------|------|
| `convert(source, target_format, ...)` | 转换文档 |
| `convert_to_ir(source, ...)` | 转换为中间表示 |
| `render_from_ir(document, target_format, ...)` | 从中间表示渲染 |
| `list_supported_conversions()` | 列出所有支持的转换 |
| `can_convert(source_format, target_format)` | 检查是否支持转换 |

---

### ConversionResult

转换操作结果。

**属性：**

| 属性 | 类型 | 描述 |
|------|------|------|
| `success` | `bool` | 转换是否成功 |
| `output_path` | `Optional[Path]` | 输出文件路径 |
| `content` | `Optional[Union[str, bytes]]` | 输出内容 |
| `error_message` | `Optional[str]` | 错误信息 |
| `metadata` | `Dict[str, Any]` | 转换元数据 |

---

## 注册表

### ConverterRegistry

管理所有解析器和渲染器。

```python
from mcp_document_converter.registry import get_registry, ConverterRegistry
from mcp_document_converter.parsers import MarkdownParser
from mcp_document_converter.renderers import HTMLRenderer

# 使用全局注册表
registry = get_registry()
registry.register_parser(MarkdownParser())
registry.register_renderer(HTMLRenderer())

# 或创建自定义注册表
custom_registry = ConverterRegistry()
```

**方法：**

| 方法 | 描述 |
|------|------|
| `register_parser(parser)` | 注册解析器 |
| `register_renderer(renderer)` | 注册渲染器 |
| `find_parser(source)` | 根据文件路径/扩展名查找解析器 |
| `find_renderer(format_name)` | 根据格式名称查找渲染器 |
| `get_parser(format_name)` | 根据格式名称获取解析器 |
| `list_parsers()` | 列出所有已注册的解析器 |
| `list_renderers()` | 列出所有已注册的渲染器 |
| `list_supported_formats()` | 列出所有支持的格式 |
| `get_conversion_matrix()` | 获取格式转换矩阵 |
| `can_convert(source_format, target_format)` | 检查是否支持转换 |

---

## 解析器

### BaseParser

所有解析器的抽象基类。

```python
from mcp_document_converter.core.parser import BaseParser

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
    
    def parse(self, source, **options) -> DocumentIR:
        # 实现解析逻辑
        pass
```

---

### MarkdownParser

将 Markdown 文件解析为 DocumentIR。

**支持扩展名：** `.md`, `.markdown`, `.mdown`, `.mkd`

**特性：**
- YAML Front Matter
- GFM 扩展
- 带语法高亮的代码块
- 表格
- 任务列表

---

### HTMLParser

将 HTML 文件解析为 DocumentIR。

**支持扩展名：** `.html`, `.htm`

**特性：**
- 语义标签解析
- 样式提取
- 图片提取

---

### DOCXParser

将 DOCX 文件解析为 DocumentIR。

**支持扩展名：** `.docx`

**特性：**
- 样式保留
- 表格支持
- 图片提取

---

### PDFParser

将 PDF 文件解析为 DocumentIR。

**支持扩展名：** `.pdf`

**特性：**
- 文本提取
- 结构识别
- 表格提取

---

### TextParser

将纯文本文件解析为 DocumentIR。

**支持扩展名：** `.txt`, `.text`

**特性：**
- 自动编码检测
- 段落识别

---

## 渲染器

### BaseRenderer

所有渲染器的抽象基类。

```python
from mcp_document_converter.core.renderer import BaseRenderer

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
    
    def render(self, document, **options) -> str:
        # 实现渲染逻辑
        pass
```

---

### HTMLRenderer

将 DocumentIR 渲染为 HTML。

**特性：**
- 美观样式
- 代码语法高亮
- 响应式设计
- 自定义 CSS 支持

---

### PDFRenderer

将 DocumentIR 渲染为 PDF。

**特性：**
- WeasyPrint 后端
- 自定义模板
- 字体嵌入
- 图片支持

---

### MarkdownRenderer

将 DocumentIR 渲染为 Markdown。

**特性：**
- 标准 Markdown 格式
- YAML Front Matter
- GFM 扩展

---

### DOCXRenderer

将 DocumentIR 渲染为 DOCX。

**特性：**
- 样式保留
- 表格支持
- 图片嵌入

---

### TextRenderer

将 DocumentIR 渲染为纯文本。

**特性：**
- 基本格式保留
- 编码支持

---

## MCP 工具

### convert_document

将文档从一种格式转换为另一种格式。

**参数：**

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `source_path` | string | 是 | 源文件路径 |
| `target_format` | string | 是 | 目标格式 (`html`, `pdf`, `markdown`, `docx`, `text`) |
| `output_path` | string | 否 | 输出文件路径 |
| `source_format` | string | 否 | 源格式（未提供时自动检测） |
| `options` | object | 否 | 额外选项 |

**选项：**

| 选项 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `template` | string | - | 模板名称 |
| `css` | string | - | 自定义 CSS 样式 |
| `preserve_metadata` | boolean | true | 保留元数据 |
| `extract_images` | boolean | true | 提取图片 |

---

### list_supported_formats

列出所有支持的文档格式。

**返回：** 包含 `parsers` 和 `renderers` 数组的对象。

---

### get_conversion_matrix

获取完整的格式转换矩阵。

**返回：** 源格式到目标格式的映射对象。

---

### can_convert

检查是否支持转换。

**参数：**

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `source_format` | string | 是 | 源格式 |
| `target_format` | string | 是 | 目标格式 |

**返回：** 布尔值

---

### get_format_info

获取格式的详细信息。

**参数：**

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `format` | string | 是 | 格式名称 |

**返回：** 格式详情对象
