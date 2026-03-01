"""
pytest 配置文件
"""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """临时目录 fixture"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_markdown():
    """示例 Markdown 内容"""
    return """# 测试文档

这是**粗体**和*斜体*文本。

## 代码示例

```python
def hello():
    print("Hello, World!")
```

## 列表示例

- 项目 1
- 项目 2
- 项目 3
"""


@pytest.fixture
def sample_html():
    """示例 HTML 内容"""
    return """<!DOCTYPE html>
<html>
<head><title>测试</title></head>
<body>
<h1>HTML 测试</h1>
<p>这是一个 <strong>测试</strong> 段落。</p>
</body>
</html>
"""


@pytest.fixture
def sample_text():
    """示例纯文本内容"""
    return """测试文档
========

这是第一段文字。

这是第二段文字，包含一些格式。

- 列表项 1
- 列表项 2

代码示例：

    print("Hello")
    print("World")
"""


@pytest.fixture
def sample_document_ir():
    """示例文档 IR"""
    from mcp_document_converter.core.ir import DocumentIR, Node, NodeType

    doc = DocumentIR(title="测试文档", author="测试作者")
    doc.add_node(
        Node(
            type=NodeType.HEADING,
            content=[Node(type=NodeType.TEXT, content="标题一")],
            attributes={"level": 1},
        )
    )
    doc.add_node(
        Node(
            type=NodeType.PARAGRAPH,
            content=[Node(type=NodeType.TEXT, content="这是段落内容。")],
        )
    )
    doc.add_node(
        Node(
            type=NodeType.CODE_BLOCK,
            content="print('hello')",
            attributes={"language": "python"},
        )
    )
    doc.add_node(
        Node(
            type=NodeType.LIST,
            content=[
                Node(
                    type=NodeType.LIST_ITEM,
                    content=[Node(type=NodeType.TEXT, content="项目 1")],
                ),
                Node(
                    type=NodeType.LIST_ITEM,
                    content=[Node(type=NodeType.TEXT, content="项目 2")],
                ),
            ],
            attributes={"type": "unordered"},
        )
    )
    return doc


@pytest.fixture
def setup_full_registry():
    """设置完整注册表"""
    from mcp_document_converter.registry import ConverterRegistry
    from mcp_document_converter.parsers import (
        DOCXParser,
        HTMLParser,
        MarkdownParser,
        PDFParser,
        TextParser,
    )
    from mcp_document_converter.renderers import (
        DOCXRenderer,
        HTMLRenderer,
        MarkdownRenderer,
        PDFRenderer,
        TextRenderer,
    )

    registry = ConverterRegistry()
    registry.register_parser(MarkdownParser())
    registry.register_parser(HTMLParser())
    registry.register_parser(DOCXParser())
    registry.register_parser(PDFParser())
    registry.register_parser(TextParser())
    registry.register_renderer(HTMLRenderer())
    registry.register_renderer(MarkdownRenderer())
    registry.register_renderer(DOCXRenderer())
    registry.register_renderer(PDFRenderer())
    registry.register_renderer(TextRenderer())
    return registry
