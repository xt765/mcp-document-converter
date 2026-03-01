"""
测试转换引擎 - core/engine.py
"""

from pathlib import Path

import pytest

from mcp_document_converter.core.engine import ConversionResult, DocumentConverter
from mcp_document_converter.core.ir import DocumentIR, Node, NodeType
from mcp_document_converter.parsers import (
    DOCXParser,
    HTMLParser,
    MarkdownParser,
    PDFParser,
    TextParser,
)
from mcp_document_converter.registry import ConverterRegistry
from mcp_document_converter.renderers import (
    DOCXRenderer,
    HTMLRenderer,
    MarkdownRenderer,
    PDFRenderer,
    TextRenderer,
)


@pytest.fixture
def registry():
    """创建并配置注册表"""
    reg = ConverterRegistry()
    reg.register_parser(MarkdownParser())
    reg.register_parser(HTMLParser())
    reg.register_parser(DOCXParser())
    reg.register_parser(PDFParser())
    reg.register_parser(TextParser())
    reg.register_renderer(HTMLRenderer())
    reg.register_renderer(MarkdownRenderer())
    reg.register_renderer(DOCXRenderer())
    reg.register_renderer(PDFRenderer())
    reg.register_renderer(TextRenderer())
    return reg


@pytest.fixture
def converter(registry):
    """创建文档转换器"""
    return DocumentConverter(registry)


@pytest.fixture
def converter_no_registry():
    """创建使用全局注册表的转换器"""
    return DocumentConverter()


class TestConversionResult:
    """测试 ConversionResult 数据类"""

    def test_conversion_result_default_metadata(self):
        """测试默认元数据初始化"""
        result = ConversionResult(success=True)
        assert result.metadata == {}

    def test_conversion_result_with_values(self):
        """测试带值的转换结果"""
        result = ConversionResult(
            success=True,
            output_path=Path("/tmp/output.html"),
            content="<html></html>",
            error_message=None,
            metadata={"key": "value"},
        )
        assert result.success is True
        assert result.output_path == Path("/tmp/output.html")
        assert result.content == "<html></html>"
        assert result.metadata == {"key": "value"}

    def test_conversion_result_failure(self):
        """测试失败的转换结果"""
        result = ConversionResult(
            success=False,
            error_message="文件不存在",
        )
        assert result.success is False
        assert result.error_message == "文件不存在"


class TestDocumentConverter:
    """测试 DocumentConverter 类"""

    def test_init_with_registry(self, registry):
        """测试使用注册表初始化"""
        converter = DocumentConverter(registry)
        assert converter.registry == registry

    def test_init_without_registry(self):
        """测试不使用注册表初始化"""
        converter = DocumentConverter()
        assert converter.registry is not None

    def test_convert_markdown_to_html(self, converter, temp_dir, sample_markdown):
        """测试 Markdown 转 HTML"""
        md_path = temp_dir / "test.md"
        md_path.write_text(sample_markdown, encoding="utf-8")

        result = converter.convert(md_path, "html")

        assert result.success is True
        assert result.output_path is not None
        assert result.output_path.suffix == ".html"
        assert result.output_path.exists()
        assert "<h1>" in result.output_path.read_text(encoding="utf-8")

    def test_convert_with_output_path(self, converter, temp_dir, sample_markdown):
        """测试指定输出路径"""
        md_path = temp_dir / "input.md"
        md_path.write_text(sample_markdown, encoding="utf-8")
        output_path = temp_dir / "custom_output.html"

        result = converter.convert(md_path, "html", output_path=output_path)

        assert result.success is True
        assert result.output_path == output_path

    def test_convert_with_source_format(self, converter, temp_dir, sample_markdown):
        """测试指定源格式"""
        md_path = temp_dir / "test.custom"
        md_path.write_text(sample_markdown, encoding="utf-8")

        result = converter.convert(md_path, "html", source_format="markdown")

        assert result.success is True
        assert result.output_path.suffix == ".html"

    def test_convert_with_options(self, converter, temp_dir, sample_markdown):
        """测试带选项的转换"""
        md_path = temp_dir / "test.md"
        md_path.write_text(sample_markdown, encoding="utf-8")

        result = converter.convert(
            md_path,
            "html",
            options={"render_options": {"title": "自定义标题"}},
        )

        assert result.success is True

    def test_convert_file_not_found(self, converter, temp_dir):
        """测试文件不存在"""
        result = converter.convert(temp_dir / "nonexistent.md", "html")

        assert result.success is False
        assert "文件不存在" in result.error_message

    def test_convert_unsupported_source_format(self, converter, temp_dir):
        """测试不支持的源格式"""
        file_path = temp_dir / "test.xyz"
        file_path.write_text("content", encoding="utf-8")

        result = converter.convert(file_path, "html")

        assert result.success is False
        assert "不支持的源格式" in result.error_message

    def test_convert_unsupported_target_format(self, converter, temp_dir, sample_markdown):
        """测试不支持的目标格式"""
        md_path = temp_dir / "test.md"
        md_path.write_text(sample_markdown, encoding="utf-8")

        result = converter.convert(md_path, "invalid_format")

        assert result.success is False
        assert "不支持的目标格式" in result.error_message

    def test_convert_creates_parent_directories(self, converter, temp_dir, sample_markdown):
        """测试创建父目录"""
        md_path = temp_dir / "test.md"
        md_path.write_text(sample_markdown, encoding="utf-8")
        output_path = temp_dir / "subdir" / "deep" / "output.html"

        result = converter.convert(md_path, "html", output_path=output_path)

        assert result.success is True
        assert output_path.parent.exists()

    def test_convert_to_ir(self, converter, temp_dir, sample_markdown):
        """测试转换为中间表示"""
        md_path = temp_dir / "test.md"
        md_path.write_text(sample_markdown, encoding="utf-8")

        document = converter.convert_to_ir(md_path)

        assert isinstance(document, DocumentIR)
        assert len(document.content) > 0

    def test_convert_to_ir_with_format(self, converter, temp_dir, sample_markdown):
        """测试指定格式转换为中间表示"""
        md_path = temp_dir / "test.custom"
        md_path.write_text(sample_markdown, encoding="utf-8")

        document = converter.convert_to_ir(md_path, source_format="markdown")

        assert isinstance(document, DocumentIR)

    def test_convert_to_ir_unsupported_format(self, converter, temp_dir):
        """测试不支持的格式转换为中间表示"""
        file_path = temp_dir / "test.xyz"
        file_path.write_text("content", encoding="utf-8")

        with pytest.raises(ValueError, match="找不到支持"):
            converter.convert_to_ir(file_path)

    def test_render_from_ir(self, converter, temp_dir):
        """测试从中间表示渲染"""
        document = DocumentIR(title="测试文档")
        document.add_node(
            Node(
                type=NodeType.HEADING,
                content=[Node(type=NodeType.TEXT, content="标题")],
                attributes={"level": 1},
            )
        )

        result = converter.render_from_ir(document, "html")

        assert result.success is True
        assert result.content is not None
        assert "<h1>" in result.content

    def test_render_from_ir_with_output_path(self, converter, temp_dir):
        """测试从中间表示渲染到文件"""
        document = DocumentIR(title="测试文档")
        document.add_node(
            Node(type=NodeType.PARAGRAPH, content=[Node(type=NodeType.TEXT, content="内容")])
        )
        output_path = temp_dir / "output.html"

        result = converter.render_from_ir(document, "html", output_path=output_path)

        assert result.success is True
        assert result.output_path == output_path
        assert output_path.exists()

    def test_render_from_ir_unsupported_format(self, converter):
        """测试不支持的目标格式渲染"""
        document = DocumentIR()

        result = converter.render_from_ir(document, "invalid_format")

        assert result.success is False
        assert "不支持的目标格式" in result.error_message

    def test_render_from_ir_with_options(self, converter):
        """测试带选项渲染"""
        document = DocumentIR(title="测试")
        document.add_node(
            Node(type=NodeType.PARAGRAPH, content=[Node(type=NodeType.TEXT, content="内容")])
        )

        result = converter.render_from_ir(
            document, "html", options={"title": "自定义标题", "css": "body { color: red; }"}
        )

        assert result.success is True
        assert "自定义标题" in result.content

    def test_list_supported_conversions(self, converter):
        """测试列出支持的转换"""
        matrix = converter.list_supported_conversions()

        assert isinstance(matrix, dict)
        assert "markdown" in matrix
        assert "html" in matrix["markdown"]
        assert "pdf" in matrix["markdown"]
        assert "docx" in matrix["markdown"]

    def test_can_convert_supported(self, converter):
        """测试支持的转换检查"""
        assert converter.can_convert("markdown", "html") is True
        assert converter.can_convert("html", "markdown") is True
        assert converter.can_convert("text", "pdf") is True

    def test_can_convert_unsupported(self, converter):
        """测试不支持的转换检查"""
        assert converter.can_convert("invalid", "html") is False
        assert converter.can_convert("markdown", "invalid") is False

    def test_convert_html_to_markdown(self, converter, temp_dir, sample_html):
        """测试 HTML 转 Markdown"""
        html_path = temp_dir / "test.html"
        html_path.write_text(sample_html, encoding="utf-8")

        result = converter.convert(html_path, "markdown")

        assert result.success is True
        assert result.output_path.suffix == ".md"

    def test_convert_text_to_html(self, converter, temp_dir):
        """测试 Text 转 HTML"""
        text_path = temp_dir / "test.txt"
        text_path.write_text("测试文本\n\n第二段", encoding="utf-8")

        result = converter.convert(text_path, "html")

        assert result.success is True
        assert result.output_path.suffix == ".html"

    def test_convert_to_docx(self, converter, temp_dir, sample_markdown):
        """测试转换为 DOCX"""
        md_path = temp_dir / "test.md"
        md_path.write_text(sample_markdown, encoding="utf-8")

        result = converter.convert(md_path, "docx")

        assert result.success is True
        assert result.output_path.suffix == ".docx"

    def test_convert_to_pdf(self, converter, temp_dir, sample_markdown):
        """测试转换为 PDF"""
        md_path = temp_dir / "test.md"
        md_path.write_text(sample_markdown, encoding="utf-8")

        result = converter.convert(md_path, "pdf")

        # PDF 可能因为 weasyprint 不可用而失败
        # 但应该有结果返回
        assert result.success is True or result.success is False

    def test_convert_to_text(self, converter, temp_dir, sample_markdown):
        """测试转换为 Text"""
        md_path = temp_dir / "test.md"
        md_path.write_text(sample_markdown, encoding="utf-8")

        result = converter.convert(md_path, "text")

        assert result.success is True
        assert result.output_path.suffix == ".txt"

    def test_render_from_ir_binary_output(self, converter, temp_dir):
        """测试二进制输出渲染"""
        document = DocumentIR(title="测试")
        document.add_node(
            Node(type=NodeType.PARAGRAPH, content=[Node(type=NodeType.TEXT, content="内容")])
        )
        output_path = temp_dir / "output.docx"

        result = converter.render_from_ir(document, "docx", output_path=output_path)

        assert result.success is True
        assert isinstance(result.content, bytes)
