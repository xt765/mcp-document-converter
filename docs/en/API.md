# API Reference

## Table of Contents

- [Core Classes](#core-classes)
  - [DocumentIR](#documentir)
  - [Node](#node)
  - [NodeType](#nodetype)
  - [Asset](#asset)
- [Conversion Engine](#conversion-engine)
  - [DocumentConverter](#documentconverter)
  - [ConversionResult](#conversionresult)
- [Registry](#registry)
  - [ConverterRegistry](#converterregistry)
- [Parsers](#parsers)
  - [BaseParser](#baseparser)
  - [MarkdownParser](#markdownparser)
  - [HTMLParser](#htmlparser)
  - [DOCXParser](#docxparser)
  - [PDFParser](#pdfparser)
  - [TextParser](#textparser)
- [Renderers](#renderers)
  - [BaseRenderer](#baserenderer)
  - [HTMLRenderer](#htmlrenderer)
  - [PDFRenderer](#pdfrenderer)
  - [MarkdownRenderer](#markdownrenderer)
  - [DOCXRenderer](#docxrenderer)
  - [TextRenderer](#textrenderer)
- [MCP Tools](#mcp-tools)
  - [convert_document](#convert_document)
  - [list_supported_formats](#list_supported_formats)
  - [get_conversion_matrix](#get_conversion_matrix)
  - [can_convert](#can_convert)
  - [get_format_info](#get_format_info)

---

## Core Classes

### DocumentIR

The intermediate representation for all document formats.

```python
from mcp_document_converter.core.ir import DocumentIR, Node, NodeType

document = DocumentIR(
    title="My Document",
    author="Author Name",
    metadata={"key": "value"}
)

# Add content nodes
document.add_node(Node(
    type=NodeType.PARAGRAPH,
    content=[Node(type=NodeType.TEXT, content="Hello World")]
))
```

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `title` | `Optional[str]` | Document title |
| `author` | `Optional[str]` | Document author |
| `created_at` | `Optional[datetime]` | Creation timestamp |
| `modified_at` | `Optional[datetime]` | Modification timestamp |
| `metadata` | `Dict[str, Any]` | Additional metadata |
| `content` | `List[Node]` | Document content tree |
| `assets` | `List[Asset]` | Embedded resources |
| `styles` | `Dict[str, Any]` | Style information |

**Methods:**

| Method | Description |
|--------|-------------|
| `add_node(node)` | Add a node to document content |
| `add_asset(asset)` | Add an asset to document |
| `get_text_content()` | Extract plain text content |
| `to_dict()` | Convert to dictionary for serialization |

---

### Node

Document tree node.

```python
from mcp_document_converter.core.ir import Node, NodeType

# Create a heading
heading = Node(
    type=NodeType.HEADING,
    content=[Node(type=NodeType.TEXT, content="Title")],
    attributes={"level": 1}
)

# Create a paragraph with formatting
paragraph = Node(
    type=NodeType.PARAGRAPH,
    content=[
        Node(type=NodeType.TEXT, content="Normal text "),
        Node(type=NodeType.STRONG, content=[Node(type=NodeType.TEXT, content="bold")]),
    ]
)
```

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `type` | `NodeType` | Node type |
| `content` | `Union[str, List[Node]]` | Text content or child nodes |
| `attributes` | `Dict[str, Any]` | Node attributes |

---

### NodeType

Enumeration of document node types.

**Block Elements:**

| Type | Description |
|------|-------------|
| `DOCUMENT` | Document root node |
| `HEADING` | Heading (h1-h6) |
| `PARAGRAPH` | Paragraph |
| `CODE_BLOCK` | Code block |
| `LIST` | Ordered/unordered list |
| `LIST_ITEM` | List item |
| `TABLE` | Table |
| `TABLE_ROW` | Table row |
| `TABLE_CELL` | Table cell |
| `BLOCKQUOTE` | Blockquote |
| `HORIZONTAL_RULE` | Horizontal rule |
| `PAGE_BREAK` | Page break |

**Inline Elements:**

| Type | Description |
|------|-------------|
| `TEXT` | Plain text |
| `LINK` | Hyperlink |
| `IMAGE` | Image |
| `CODE_INLINE` | Inline code |
| `EMPHASIS` | Italic |
| `STRONG` | Bold |
| `STRIKETHROUGH` | Strikethrough |
| `SUBSCRIPT` | Subscript |
| `SUPERSCRIPT` | Superscript |
| `LINE_BREAK` | Line break |

---

### Asset

Document resource (images, attachments, etc.).

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

## Conversion Engine

### DocumentConverter

The main conversion engine that coordinates parsers and renderers.

```python
from mcp_document_converter import DocumentConverter

converter = DocumentConverter()

# Simple conversion
result = converter.convert("input.md", "html")

# With output path
result = converter.convert("input.md", "html", output_path="output.html")

# With options
result = converter.convert(
    "input.md",
    "pdf",
    options={"template": "default", "css": "custom.css"}
)

if result.success:
    print(f"Converted: {result.output_path}")
else:
    print(f"Error: {result.error_message}")
```

**Methods:**

| Method | Description |
|--------|-------------|
| `convert(source, target_format, ...)` | Convert document |
| `convert_to_ir(source, ...)` | Convert to intermediate representation |
| `render_from_ir(document, target_format, ...)` | Render from intermediate representation |
| `list_supported_conversions()` | List all supported conversions |
| `can_convert(source_format, target_format)` | Check if conversion is supported |

---

### ConversionResult

Result of a conversion operation.

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `success` | `bool` | Whether conversion succeeded |
| `output_path` | `Optional[Path]` | Output file path |
| `content` | `Optional[Union[str, bytes]]` | Output content |
| `error_message` | `Optional[str]` | Error message if failed |
| `metadata` | `Dict[str, Any]` | Conversion metadata |

---

## Registry

### ConverterRegistry

Manages all parsers and renderers.

```python
from mcp_document_converter.registry import get_registry, ConverterRegistry
from mcp_document_converter.parsers import MarkdownParser
from mcp_document_converter.renderers import HTMLRenderer

# Use global registry
registry = get_registry()
registry.register_parser(MarkdownParser())
registry.register_renderer(HTMLRenderer())

# Or create custom registry
custom_registry = ConverterRegistry()
```

**Methods:**

| Method | Description |
|--------|-------------|
| `register_parser(parser)` | Register a parser |
| `register_renderer(renderer)` | Register a renderer |
| `find_parser(source)` | Find parser by file path/extension |
| `find_renderer(format_name)` | Find renderer by format name |
| `get_parser(format_name)` | Get parser by format name |
| `list_parsers()` | List all registered parsers |
| `list_renderers()` | List all registered renderers |
| `list_supported_formats()` | List all supported formats |
| `get_conversion_matrix()` | Get format conversion matrix |
| `can_convert(source_format, target_format)` | Check if conversion is supported |

---

## Parsers

### BaseParser

Abstract base class for all parsers.

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
        # Implementation
        pass
```

---

### MarkdownParser

Parses Markdown files to DocumentIR.

**Supported Extensions:** `.md`, `.markdown`, `.mdown`, `.mkd`

**Features:**
- YAML Front Matter
- GFM extensions
- Code blocks with syntax highlighting
- Tables
- Task lists

---

### HTMLParser

Parses HTML files to DocumentIR.

**Supported Extensions:** `.html`, `.htm`

**Features:**
- Semantic tag parsing
- Style extraction
- Image extraction

---

### DOCXParser

Parses DOCX files to DocumentIR.

**Supported Extensions:** `.docx`

**Features:**
- Style preservation
- Table support
- Image extraction

---

### PDFParser

Parses PDF files to DocumentIR.

**Supported Extensions:** `.pdf`

**Features:**
- Text extraction
- Structure recognition
- Table extraction

---

### TextParser

Parses plain text files to DocumentIR.

**Supported Extensions:** `.txt`, `.text`

**Features:**
- Auto encoding detection
- Paragraph recognition

---

## Renderers

### BaseRenderer

Abstract base class for all renderers.

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
        # Implementation
        pass
```

---

### HTMLRenderer

Renders DocumentIR to HTML.

**Features:**
- Beautiful styling
- Code syntax highlighting
- Responsive design
- Custom CSS support

---

### PDFRenderer

Renders DocumentIR to PDF.

**Features:**
- WeasyPrint backend
- Custom templates
- Font embedding
- Image support

---

### MarkdownRenderer

Renders DocumentIR to Markdown.

**Features:**
- Standard Markdown format
- YAML Front Matter
- GFM extensions

---

### DOCXRenderer

Renders DocumentIR to DOCX.

**Features:**
- Style preservation
- Table support
- Image embedding

---

### TextRenderer

Renders DocumentIR to plain text.

**Features:**
- Basic formatting preservation
- Encoding support

---

## MCP Tools

### convert_document

Convert a document from one format to another.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `source_path` | string | Yes | Source file path |
| `target_format` | string | Yes | Target format (`html`, `pdf`, `markdown`, `docx`, `text`) |
| `output_path` | string | No | Output file path |
| `source_format` | string | No | Source format (auto-detected if not provided) |
| `options` | object | No | Additional options |

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `template` | string | - | Template name |
| `css` | string | - | Custom CSS styles |
| `preserve_metadata` | boolean | true | Preserve metadata |
| `extract_images` | boolean | true | Extract images |

---

### list_supported_formats

List all supported document formats.

**Returns:** Object with `parsers` and `renderers` arrays.

---

### get_conversion_matrix

Get the complete format conversion matrix.

**Returns:** Object mapping source formats to target formats.

---

### can_convert

Check if conversion is supported.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `source_format` | string | Yes | Source format |
| `target_format` | string | Yes | Target format |

**Returns:** Boolean

---

### get_format_info

Get detailed information about a format.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `format` | string | Yes | Format name |

**Returns:** Object with format details
