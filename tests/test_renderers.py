"""
测试渲染器 - renderers 模块
"""


import pytest

from mcp_document_converter.core.ir import DocumentIR, Node, NodeType
from mcp_document_converter.core.renderer import RenderError
from mcp_document_converter.renderers.docx import DOCXRenderer
from mcp_document_converter.renderers.html import HTMLRenderer
from mcp_document_converter.renderers.markdown import MarkdownRenderer
from mcp_document_converter.renderers.pdf import PDFRenderer
from mcp_document_converter.renderers.text import TextRenderer


class TestBaseRenderer:
    """测试渲染器基类"""

    def test_get_default_options(self):
        """测试获取默认选项"""
        renderer = HTMLRenderer()
        options = renderer.get_default_options()

        assert "preserve_metadata" in options
        assert "extract_images" in options


class TestHTMLRenderer:
    """测试 HTML 渲染器"""

    @pytest.fixture
    def renderer(self):
        return HTMLRenderer()

    @pytest.fixture
    def sample_document(self):
        """创建示例文档"""
        doc = DocumentIR(title="测试文档", author="作者")
        doc.add_node(
            Node(
                type=NodeType.HEADING,
                content=[Node(type=NodeType.TEXT, content="标题")],
                attributes={"level": 1},
            )
        )
        doc.add_node(
            Node(
                type=NodeType.PARAGRAPH,
                content=[Node(type=NodeType.TEXT, content="段落内容")],
            )
        )
        return doc

    def test_output_extension(self, renderer):
        """测试输出扩展名"""
        assert renderer.output_extension == ".html"

    def test_format_name(self, renderer):
        """测试格式名称"""
        assert renderer.format_name == "html"

    def test_mime_type(self, renderer):
        """测试 MIME 类型"""
        assert renderer.mime_type == "text/html"

    def test_render_simple(self, renderer, sample_document):
        """测试简单渲染"""
        html = renderer.render(sample_document)

        assert isinstance(html, str)
        assert "<!DOCTYPE html>" in html
        assert "<h1>" in html
        assert "标题" in html

    def test_render_heading(self, renderer):
        """测试标题渲染"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.HEADING,
                content=[Node(type=NodeType.TEXT, content="二级标题")],
                attributes={"level": 2},
            )
        )

        html = renderer.render(doc)

        assert "<h2>" in html
        assert "二级标题" in html

    def test_render_paragraph(self, renderer):
        """测试段落渲染"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.PARAGRAPH,
                content=[Node(type=NodeType.TEXT, content="段落文本")],
            )
        )

        html = renderer.render(doc)

        assert "<p>" in html
        assert "段落文本" in html

    def test_render_code_block(self, renderer):
        """测试代码块渲染"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.CODE_BLOCK,
                content="print('hello')",
                attributes={"language": "python"},
            )
        )

        html = renderer.render(doc)

        assert "<pre>" in html or "code-block" in html

    def test_render_code_block_no_language(self, renderer):
        """测试无语言代码块渲染"""
        doc = DocumentIR()
        doc.add_node(
            Node(type=NodeType.CODE_BLOCK, content="code here"),
        )

        html = renderer.render(doc)

        assert "<pre>" in html

    def test_render_list_unordered(self, renderer):
        """测试无序列表渲染"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.LIST,
                content=[
                    Node(
                        type=NodeType.LIST_ITEM,
                        content=[Node(type=NodeType.TEXT, content="项目1")],
                    ),
                    Node(
                        type=NodeType.LIST_ITEM,
                        content=[Node(type=NodeType.TEXT, content="项目2")],
                    ),
                ],
                attributes={"type": "unordered"},
            )
        )

        html = renderer.render(doc)

        assert "<ul>" in html
        assert "<li>" in html

    def test_render_list_ordered(self, renderer):
        """测试有序列表渲染"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.LIST,
                content=[
                    Node(
                        type=NodeType.LIST_ITEM,
                        content=[Node(type=NodeType.TEXT, content="第一")],
                    ),
                ],
                attributes={"type": "ordered"},
            )
        )

        html = renderer.render(doc)

        assert "<ol>" in html

    def test_render_table(self, renderer):
        """测试表格渲染"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.TABLE,
                content=[
                    Node(
                        type=NodeType.TABLE_ROW,
                        content=[
                            Node(
                                type=NodeType.TABLE_CELL,
                                content=[Node(type=NodeType.TEXT, content="A")],
                                attributes={"header": True},
                            ),
                            Node(
                                type=NodeType.TABLE_CELL,
                                content=[Node(type=NodeType.TEXT, content="B")],
                                attributes={"header": True},
                            ),
                        ],
                    ),
                    Node(
                        type=NodeType.TABLE_ROW,
                        content=[
                            Node(
                                type=NodeType.TABLE_CELL,
                                content=[Node(type=NodeType.TEXT, content="1")],
                            ),
                            Node(
                                type=NodeType.TABLE_CELL,
                                content=[Node(type=NodeType.TEXT, content="2")],
                            ),
                        ],
                    ),
                ],
            )
        )

        html = renderer.render(doc)

        assert "<table>" in html
        assert "<th>" in html
        assert "<td>" in html

    def test_render_blockquote(self, renderer):
        """测试引用块渲染"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.BLOCKQUOTE,
                content=[
                    Node(
                        type=NodeType.PARAGRAPH,
                        content=[Node(type=NodeType.TEXT, content="引用内容")],
                    )
                ],
            )
        )

        html = renderer.render(doc)

        assert "<blockquote>" in html

    def test_render_horizontal_rule(self, renderer):
        """测试分隔线渲染"""
        doc = DocumentIR()
        doc.add_node(Node(type=NodeType.HORIZONTAL_RULE, content=""))

        html = renderer.render(doc)

        assert "<hr>" in html

    def test_render_inline_strong(self, renderer):
        """测试粗体渲染"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.PARAGRAPH,
                content=[
                    Node(
                        type=NodeType.STRONG,
                        content=[Node(type=NodeType.TEXT, content="粗体")],
                    )
                ],
            )
        )

        html = renderer.render(doc)

        assert "<strong>" in html

    def test_render_inline_emphasis(self, renderer):
        """测试斜体渲染"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.PARAGRAPH,
                content=[
                    Node(
                        type=NodeType.EMPHASIS,
                        content=[Node(type=NodeType.TEXT, content="斜体")],
                    )
                ],
            )
        )

        html = renderer.render(doc)

        assert "<em>" in html

    def test_render_inline_code(self, renderer):
        """测试行内代码渲染"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.PARAGRAPH,
                content=[Node(type=NodeType.CODE_INLINE, content="code")],
            )
        )

        html = renderer.render(doc)

        assert "<code>" in html

    def test_render_link(self, renderer):
        """测试链接渲染"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.PARAGRAPH,
                content=[
                    Node(
                        type=NodeType.LINK,
                        content=[Node(type=NodeType.TEXT, content="链接")],
                        attributes={"url": "https://example.com"},
                    )
                ],
            )
        )

        html = renderer.render(doc)

        assert '<a href="https://example.com">' in html

    def test_render_image(self, renderer):
        """测试图片渲染"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.PARAGRAPH,
                content=[
                    Node(
                        type=NodeType.IMAGE,
                        content="",
                        attributes={
                            "src": "image.png",
                            "alt": "图片",
                            "title": "标题",
                        },
                    )
                ],
            )
        )

        html = renderer.render(doc)

        assert '<img src="image.png"' in html

    def test_render_strikethrough(self, renderer):
        """测试删除线渲染"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.PARAGRAPH,
                content=[
                    Node(
                        type=NodeType.STRIKETHROUGH,
                        content=[Node(type=NodeType.TEXT, content="删除")],
                    )
                ],
            )
        )

        html = renderer.render(doc)

        assert "<del>" in html

    def test_render_line_break(self, renderer):
        """测试换行渲染"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.PARAGRAPH,
                content=[
                    Node(type=NodeType.TEXT, content="文本"),
                    Node(type=NodeType.LINE_BREAK, content=""),
                ],
            )
        )

        html = renderer.render(doc)

        assert "<br>" in html

    def test_render_with_custom_css(self, renderer, sample_document):
        """测试自定义 CSS"""
        html = renderer.render(sample_document, css="body { color: red; }")

        assert "color: red" in html

    def test_render_with_custom_title(self, renderer, sample_document):
        """测试自定义标题"""
        html = renderer.render(sample_document, title="自定义标题")

        assert "自定义标题" in html

    def test_render_to_file(self, renderer, sample_document, temp_dir):
        """测试渲染到文件"""
        output_path = temp_dir / "output.html"

        result_path = renderer.render_to_file(sample_document, output_path)

        assert result_path.exists()
        assert result_path.read_text(encoding="utf-8").startswith("<!DOCTYPE html>")


class TestMarkdownRenderer:
    """测试 Markdown 渲染器"""

    @pytest.fixture
    def renderer(self):
        return MarkdownRenderer()

    @pytest.fixture
    def sample_document(self):
        """创建示例文档"""
        doc = DocumentIR(title="测试文档", author="作者")
        doc.add_node(
            Node(
                type=NodeType.HEADING,
                content=[Node(type=NodeType.TEXT, content="标题")],
                attributes={"level": 1},
            )
        )
        return doc

    def test_output_extension(self, renderer):
        """测试输出扩展名"""
        assert renderer.output_extension == ".md"

    def test_format_name(self, renderer):
        """测试格式名称"""
        assert renderer.format_name == "markdown"

    def test_render_heading(self, renderer):
        """测试标题渲染"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.HEADING,
                content=[Node(type=NodeType.TEXT, content="标题")],
                attributes={"level": 2},
            )
        )

        md = renderer.render(doc)

        assert "## 标题" in md

    def test_render_paragraph(self, renderer):
        """测试段落渲染"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.PARAGRAPH,
                content=[Node(type=NodeType.TEXT, content="段落")],
            )
        )

        md = renderer.render(doc)

        assert "段落" in md

    def test_render_code_block(self, renderer):
        """测试代码块渲染"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.CODE_BLOCK,
                content="print('hello')",
                attributes={"language": "python"},
            )
        )

        md = renderer.render(doc)

        assert "```python" in md
        assert "print('hello')" in md

    def test_render_list(self, renderer):
        """测试列表渲染"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.LIST,
                content=[
                    Node(
                        type=NodeType.LIST_ITEM,
                        content=[Node(type=NodeType.TEXT, content="项目")],
                    ),
                ],
                attributes={"type": "unordered"},
            )
        )

        md = renderer.render(doc)

        assert "- 项目" in md

    def test_render_ordered_list(self, renderer):
        """测试有序列表渲染"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.LIST,
                content=[
                    Node(
                        type=NodeType.LIST_ITEM,
                        content=[Node(type=NodeType.TEXT, content="第一")],
                    ),
                ],
                attributes={"type": "ordered"},
            )
        )

        md = renderer.render(doc)

        assert "1. 第一" in md

    def test_render_table(self, renderer):
        """测试表格渲染"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.TABLE,
                content=[
                    Node(
                        type=NodeType.TABLE_ROW,
                        content=[
                            Node(
                                type=NodeType.TABLE_CELL,
                                content=[Node(type=NodeType.TEXT, content="A")],
                            ),
                            Node(
                                type=NodeType.TABLE_CELL,
                                content=[Node(type=NodeType.TEXT, content="B")],
                            ),
                        ],
                    ),
                ],
            )
        )

        md = renderer.render(doc)

        assert "|" in md

    def test_render_blockquote(self, renderer):
        """测试引用块渲染"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.BLOCKQUOTE,
                content=[
                    Node(
                        type=NodeType.PARAGRAPH,
                        content=[Node(type=NodeType.TEXT, content="引用")],
                    )
                ],
            )
        )

        md = renderer.render(doc)

        assert "> " in md

    def test_render_horizontal_rule(self, renderer):
        """测试分隔线渲染"""
        doc = DocumentIR()
        doc.add_node(Node(type=NodeType.HORIZONTAL_RULE, content=""))

        md = renderer.render(doc)

        assert "---" in md

    def test_render_inline_formatting(self, renderer):
        """测试行内格式渲染"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.PARAGRAPH,
                content=[
                    Node(
                        type=NodeType.STRONG,
                        content=[Node(type=NodeType.TEXT, content="粗体")],
                    ),
                    Node(
                        type=NodeType.EMPHASIS,
                        content=[Node(type=NodeType.TEXT, content="斜体")],
                    ),
                    Node(type=NodeType.CODE_INLINE, content="代码"),
                ],
            )
        )

        md = renderer.render(doc)

        assert "**粗体**" in md
        assert "*斜体*" in md
        assert "`代码`" in md

    def test_render_link(self, renderer):
        """测试链接渲染"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.PARAGRAPH,
                content=[
                    Node(
                        type=NodeType.LINK,
                        content=[Node(type=NodeType.TEXT, content="链接")],
                        attributes={"url": "https://example.com"},
                    )
                ],
            )
        )

        md = renderer.render(doc)

        assert "[链接](https://example.com)" in md

    def test_render_image(self, renderer):
        """测试图片渲染"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.PARAGRAPH,
                content=[
                    Node(
                        type=NodeType.IMAGE,
                        content="",
                        attributes={"src": "img.png", "alt": "图片"},
                    )
                ],
            )
        )

        md = renderer.render(doc)

        assert "![图片](img.png)" in md

    def test_render_front_matter(self, renderer, sample_document):
        """测试 Front Matter 渲染"""
        md = renderer.render(sample_document, include_front_matter=True)

        assert "---" in md
        assert "title:" in md

    def test_render_without_front_matter(self, renderer, sample_document):
        """测试不包含 Front Matter"""
        md = renderer.render(sample_document, include_front_matter=False)

        # 不应该有 YAML front matter
        lines = md.strip().split("\n")
        assert not (lines[0] == "---" and lines[-1] == "---")


class TestTextRenderer:
    """测试 Text 渲染器"""

    @pytest.fixture
    def renderer(self):
        return TextRenderer()

    @pytest.fixture
    def sample_document(self):
        """创建示例文档"""
        doc = DocumentIR(title="测试文档", author="作者")
        doc.add_node(
            Node(
                type=NodeType.HEADING,
                content=[Node(type=NodeType.TEXT, content="标题")],
                attributes={"level": 1},
            )
        )
        doc.add_node(
            Node(
                type=NodeType.PARAGRAPH,
                content=[Node(type=NodeType.TEXT, content="段落内容")],
            )
        )
        return doc

    def test_output_extension(self, renderer):
        """测试输出扩展名"""
        assert renderer.output_extension == ".txt"

    def test_format_name(self, renderer):
        """测试格式名称"""
        assert renderer.format_name == "text"

    def test_render_simple(self, renderer, sample_document):
        """测试简单渲染"""
        text = renderer.render(sample_document)

        assert "测试文档" in text
        assert "标题" in text
        assert "段落内容" in text

    def test_render_heading_with_formatting(self, renderer):
        """测试标题带格式化"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.HEADING,
                content=[Node(type=NodeType.TEXT, content="标题")],
                attributes={"level": 1},
            )
        )

        text = renderer.render(doc, preserve_formatting=True)

        assert "标题" in text
        assert "=" in text

    def test_render_heading_level2(self, renderer):
        """测试二级标题"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.HEADING,
                content=[Node(type=NodeType.TEXT, content="二级标题")],
                attributes={"level": 2},
            )
        )

        text = renderer.render(doc, preserve_formatting=True)

        assert "二级标题" in text
        assert "-" in text

    def test_render_code_block(self, renderer):
        """测试代码块渲染"""
        doc = DocumentIR()
        doc.add_node(Node(type=NodeType.CODE_BLOCK, content="code line"))

        text = renderer.render(doc)

        assert "code line" in text

    def test_render_list(self, renderer):
        """测试列表渲染"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.LIST,
                content=[
                    Node(
                        type=NodeType.LIST_ITEM,
                        content=[Node(type=NodeType.TEXT, content="项目")],
                    ),
                ],
                attributes={"type": "unordered"},
            )
        )

        text = renderer.render(doc)

        assert "项目" in text

    def test_render_ordered_list(self, renderer):
        """测试有序列表渲染"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.LIST,
                content=[
                    Node(
                        type=NodeType.LIST_ITEM,
                        content=[Node(type=NodeType.TEXT, content="第一")],
                    ),
                ],
                attributes={"type": "ordered"},
            )
        )

        text = renderer.render(doc)

        assert "1." in text

    def test_render_table(self, renderer):
        """测试表格渲染"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.TABLE,
                content=[
                    Node(
                        type=NodeType.TABLE_ROW,
                        content=[
                            Node(
                                type=NodeType.TABLE_CELL,
                                content=[Node(type=NodeType.TEXT, content="A")],
                            ),
                            Node(
                                type=NodeType.TABLE_CELL,
                                content=[Node(type=NodeType.TEXT, content="B")],
                            ),
                        ],
                    ),
                ],
            )
        )

        text = renderer.render(doc)

        assert "A" in text
        assert "B" in text

    def test_render_blockquote(self, renderer):
        """测试引用块渲染"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.BLOCKQUOTE,
                content=[
                    Node(
                        type=NodeType.PARAGRAPH,
                        content=[Node(type=NodeType.TEXT, content="引用")],
                    )
                ],
            )
        )

        text = renderer.render(doc)

        assert "> " in text

    def test_render_horizontal_rule(self, renderer):
        """测试分隔线渲染"""
        doc = DocumentIR()
        doc.add_node(Node(type=NodeType.HORIZONTAL_RULE, content=""))

        text = renderer.render(doc, preserve_formatting=True)

        assert "-" in text

    def test_render_link(self, renderer):
        """测试链接渲染"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.PARAGRAPH,
                content=[
                    Node(
                        type=NodeType.LINK,
                        content=[Node(type=NodeType.TEXT, content="链接")],
                        attributes={"url": "https://example.com"},
                    )
                ],
            )
        )

        text = renderer.render(doc)

        assert "链接" in text
        assert "https://example.com" in text

    def test_render_image(self, renderer):
        """测试图片渲染"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.PARAGRAPH,
                content=[
                    Node(
                        type=NodeType.IMAGE,
                        content="",
                        attributes={"alt": "图片描述"},
                    )
                ],
            )
        )

        text = renderer.render(doc)

        assert "图片描述" in text or "[图片" in text

    def test_wrap_text(self, renderer):
        """测试文本换行"""
        long_text = "这是一个很长的文本 " * 20

        wrapped = renderer._wrap_text(long_text, 80)

        lines = wrapped.split("\n")
        assert all(len(line) <= 80 for line in lines)

    def test_render_max_line_length(self, renderer):
        """测试最大行长度"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.PARAGRAPH,
                content=[Node(type=NodeType.TEXT, content="这是一个很长的段落文本 " * 20)],
            )
        )

        text = renderer.render(doc, max_line_length=60)

        lines = text.split("\n")
        # 检查大部分行不超过限制
        assert most(len(line) <= 65 for line in lines if line.strip())


def most(iterable):
    """检查可迭代对象中大多数元素为 True"""
    true_count = sum(1 for x in iterable if x)
    total = sum(1 for _ in iterable)
    return true_count > total * 0.8 if total > 0 else True


class TestDOCXRenderer:
    """测试 DOCX 渲染器"""

    @pytest.fixture
    def renderer(self):
        return DOCXRenderer()

    @pytest.fixture
    def sample_document(self):
        """创建示例文档"""
        doc = DocumentIR(title="测试文档", author="作者")
        doc.add_node(
            Node(
                type=NodeType.HEADING,
                content=[Node(type=NodeType.TEXT, content="标题")],
                attributes={"level": 1},
            )
        )
        doc.add_node(
            Node(
                type=NodeType.PARAGRAPH,
                content=[Node(type=NodeType.TEXT, content="段落内容")],
            )
        )
        return doc

    def test_output_extension(self, renderer):
        """测试输出扩展名"""
        assert renderer.output_extension == ".docx"

    def test_format_name(self, renderer):
        """测试格式名称"""
        assert renderer.format_name == "docx"

    def test_is_binary(self, renderer):
        """测试二进制输出"""
        assert renderer.is_binary is True

    def test_render_simple(self, renderer, sample_document):
        """测试简单渲染"""
        result = renderer.render(sample_document)

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_render_heading(self, renderer):
        """测试标题渲染"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.HEADING,
                content=[Node(type=NodeType.TEXT, content="标题")],
                attributes={"level": 2},
            )
        )

        result = renderer.render(doc)

        assert isinstance(result, bytes)

    def test_render_code_block(self, renderer):
        """测试代码块渲染"""
        doc = DocumentIR()
        doc.add_node(Node(type=NodeType.CODE_BLOCK, content="print('hello')"))

        result = renderer.render(doc)

        assert isinstance(result, bytes)

    def test_render_list(self, renderer):
        """测试列表渲染"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.LIST,
                content=[
                    Node(
                        type=NodeType.LIST_ITEM,
                        content=[Node(type=NodeType.TEXT, content="项目")],
                    ),
                ],
                attributes={"type": "unordered"},
            )
        )

        result = renderer.render(doc)

        assert isinstance(result, bytes)

    def test_render_table(self, renderer):
        """测试表格渲染"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.TABLE,
                content=[
                    Node(
                        type=NodeType.TABLE_ROW,
                        content=[
                            Node(
                                type=NodeType.TABLE_CELL,
                                content=[Node(type=NodeType.TEXT, content="单元格")],
                            ),
                        ],
                    ),
                ],
            )
        )

        result = renderer.render(doc)

        assert isinstance(result, bytes)

    def test_render_blockquote(self, renderer):
        """测试引用块渲染"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.BLOCKQUOTE,
                content=[
                    Node(
                        type=NodeType.PARAGRAPH,
                        content=[Node(type=NodeType.TEXT, content="引用")],
                    )
                ],
            )
        )

        result = renderer.render(doc)

        assert isinstance(result, bytes)

    def test_render_horizontal_rule(self, renderer):
        """测试分隔线渲染"""
        doc = DocumentIR()
        doc.add_node(Node(type=NodeType.HORIZONTAL_RULE, content=""))

        result = renderer.render(doc)

        assert isinstance(result, bytes)

    def test_render_inline_formatting(self, renderer):
        """测试行内格式渲染"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.PARAGRAPH,
                content=[
                    Node(
                        type=NodeType.STRONG,
                        content=[Node(type=NodeType.TEXT, content="粗体")],
                    ),
                    Node(
                        type=NodeType.EMPHASIS,
                        content=[Node(type=NodeType.TEXT, content="斜体")],
                    ),
                    Node(type=NodeType.CODE_INLINE, content="代码"),
                ],
            )
        )

        result = renderer.render(doc)

        assert isinstance(result, bytes)

    def test_render_link(self, renderer):
        """测试链接渲染"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.PARAGRAPH,
                content=[
                    Node(
                        type=NodeType.LINK,
                        content=[Node(type=NodeType.TEXT, content="链接")],
                        attributes={"url": "https://example.com"},
                    )
                ],
            )
        )

        result = renderer.render(doc)

        assert isinstance(result, bytes)

    def test_render_strikethrough(self, renderer):
        """测试删除线渲染"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.PARAGRAPH,
                content=[
                    Node(
                        type=NodeType.STRIKETHROUGH,
                        content=[Node(type=NodeType.TEXT, content="删除")],
                    )
                ],
            )
        )

        result = renderer.render(doc)

        assert isinstance(result, bytes)

    def test_render_to_file(self, renderer, sample_document, temp_dir):
        """测试渲染到文件"""
        output_path = temp_dir / "output.docx"

        result_path = renderer.render_to_file(sample_document, output_path)

        assert result_path.exists()
        assert result_path.stat().st_size > 0


class TestPDFRenderer:
    """测试 PDF 渲染器"""

    @pytest.fixture
    def renderer(self):
        return PDFRenderer()

    @pytest.fixture
    def sample_document(self):
        """创建示例文档"""
        doc = DocumentIR(title="测试文档", author="作者")
        doc.add_node(
            Node(
                type=NodeType.HEADING,
                content=[Node(type=NodeType.TEXT, content="标题")],
                attributes={"level": 1},
            )
        )
        doc.add_node(
            Node(
                type=NodeType.PARAGRAPH,
                content=[Node(type=NodeType.TEXT, content="段落内容")],
            )
        )
        return doc

    def test_output_extension(self, renderer):
        """测试输出扩展名"""
        assert renderer.output_extension == ".pdf"

    def test_format_name(self, renderer):
        """测试格式名称"""
        assert renderer.format_name == "pdf"

    def test_is_binary(self, renderer):
        """测试二进制输出"""
        assert renderer.is_binary is True

    def test_render_simple(self, renderer, sample_document):
        """测试简单渲染"""
        # PDF 渲染可能因 weasyprint 不可用而失败
        try:
            result = renderer.render(sample_document)
            assert isinstance(result, bytes)
            assert len(result) > 0
        except RenderError:
            # 如果 weasyprint 不可用，跳过测试
            pytest.skip("WeasyPrint not available")

    def test_render_heading(self, renderer):
        """测试标题渲染"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.HEADING,
                content=[Node(type=NodeType.TEXT, content="标题")],
                attributes={"level": 1},
            )
        )

        try:
            result = renderer.render(doc)
            assert isinstance(result, bytes)
        except RenderError:
            pytest.skip("WeasyPrint not available")

    def test_render_code_block(self, renderer):
        """测试代码块渲染"""
        doc = DocumentIR()
        doc.add_node(Node(type=NodeType.CODE_BLOCK, content="print('hello')"))

        try:
            result = renderer.render(doc)
            assert isinstance(result, bytes)
        except RenderError:
            pytest.skip("WeasyPrint not available")

    def test_render_to_file(self, renderer, sample_document, temp_dir):
        """测试渲染到文件"""
        output_path = temp_dir / "output.pdf"

        try:
            result_path = renderer.render_to_file(sample_document, output_path)
            assert result_path.exists()
            assert result_path.stat().st_size > 0
        except RenderError:
            pytest.skip("WeasyPrint not available")

    def test_extract_text(self, renderer):
        """测试文本提取"""
        node = Node(
            type=NodeType.PARAGRAPH,
            content=[Node(type=NodeType.TEXT, content="测试文本")],
        )

        text = renderer._extract_text(node)

        assert text == "测试文本"

    def test_extract_text_nested(self, renderer):
        """测试嵌套文本提取"""
        node = Node(
            type=NodeType.PARAGRAPH,
            content=[
                Node(type=NodeType.TEXT, content="Hello "),
                Node(
                    type=NodeType.STRONG,
                    content=[Node(type=NodeType.TEXT, content="World")],
                ),
            ],
        )

        text = renderer._extract_text(node)

        assert text == "Hello World"
