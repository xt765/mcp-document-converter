"""
测试注册表 - registry.py
"""

from pathlib import Path

import pytest

from mcp_document_converter.parsers import (
    DOCXParser,
    HTMLParser,
    MarkdownParser,
    PDFParser,
    TextParser,
)
from mcp_document_converter.registry import (
    ConverterRegistry,
    find_parser,
    find_renderer,
    get_registry,
    register_parser,
    register_renderer,
)
from mcp_document_converter.renderers import (
    DOCXRenderer,
    HTMLRenderer,
    MarkdownRenderer,
    PDFRenderer,
    TextRenderer,
)


class TestConverterRegistry:
    """测试转换器注册表"""

    @pytest.fixture
    def registry(self):
        """创建空注册表"""
        return ConverterRegistry()

    @pytest.fixture
    def populated_registry(self):
        """创建已填充的注册表"""
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

    def test_init(self, registry):
        """测试初始化"""
        assert registry._parsers == {}
        assert registry._renderers == {}
        assert registry._extension_to_format == {}

    def test_register_parser(self, registry):
        """测试注册解析器"""
        parser = MarkdownParser()
        registry.register_parser(parser)

        assert "markdown" in registry._parsers
        assert ".md" in registry._extension_to_format
        assert ".markdown" in registry._extension_to_format

    def test_register_renderer(self, registry):
        """测试注册渲染器"""
        renderer = HTMLRenderer()
        registry.register_renderer(renderer)

        assert "html" in registry._renderers

    def test_find_parser_by_extension(self, populated_registry):
        """测试通过扩展名查找解析器"""
        parser = populated_registry.find_parser("test.md")
        assert parser is not None
        assert parser.format_name == "markdown"

    def test_find_parser_by_path(self, populated_registry):
        """测试通过路径查找解析器"""
        parser = populated_registry.find_parser(Path("test.html"))
        assert parser is not None
        assert parser.format_name == "html"

    def test_find_parser_by_format(self, populated_registry):
        """测试通过格式名查找解析器"""
        parser = populated_registry.find_parser("docx")
        assert parser is not None
        assert parser.format_name == "docx"

    def test_find_parser_not_found(self, registry):
        """测试找不到解析器"""
        parser = registry.find_parser(".xyz")
        assert parser is None

    def test_find_renderer(self, populated_registry):
        """测试查找渲染器"""
        renderer = populated_registry.find_renderer("html")
        assert renderer is not None
        assert renderer.format_name == "html"

    def test_find_renderer_case_insensitive(self, populated_registry):
        """测试渲染器查找大小写不敏感"""
        renderer = populated_registry.find_renderer("HTML")
        assert renderer is not None

        renderer = populated_registry.find_renderer("Markdown")
        assert renderer is not None

    def test_find_renderer_not_found(self, registry):
        """测试找不到渲染器"""
        renderer = registry.find_renderer("invalid")
        assert renderer is None

    def test_get_parser(self, populated_registry):
        """测试获取解析器"""
        parser = populated_registry.get_parser("markdown")
        assert parser is not None
        assert parser.format_name == "markdown"

    def test_get_parser_case_insensitive(self, populated_registry):
        """测试获取解析器大小写不敏感"""
        parser = populated_registry.get_parser("MARKDOWN")
        assert parser is not None

    def test_get_parser_not_found(self, registry):
        """测试获取不存在的解析器"""
        parser = registry.get_parser("invalid")
        assert parser is None

    def test_list_parsers(self, populated_registry):
        """测试列出解析器"""
        parsers = populated_registry.list_parsers()

        assert len(parsers) == 5
        formats = [p.format_name for p in parsers]
        assert "markdown" in formats
        assert "html" in formats
        assert "docx" in formats
        assert "pdf" in formats
        assert "text" in formats

    def test_list_renderers(self, populated_registry):
        """测试列出渲染器"""
        renderers = populated_registry.list_renderers()

        assert len(renderers) == 5
        formats = [r.format_name for r in renderers]
        assert "html" in formats
        assert "markdown" in formats
        assert "docx" in formats
        assert "pdf" in formats
        assert "text" in formats

    def test_list_supported_formats(self, populated_registry):
        """测试列出支持的格式"""
        formats = populated_registry.list_supported_formats()

        assert "parsers" in formats
        assert "renderers" in formats
        assert len(formats["parsers"]) == 5
        assert len(formats["renderers"]) == 5

    def test_get_conversion_matrix(self, populated_registry):
        """测试获取转换矩阵"""
        matrix = populated_registry.get_conversion_matrix()

        assert isinstance(matrix, dict)
        assert "markdown" in matrix
        assert "html" in matrix["markdown"]
        assert "pdf" in matrix["markdown"]
        assert "docx" in matrix["markdown"]
        assert "text" in matrix["markdown"]

    def test_can_convert_supported(self, populated_registry):
        """测试支持的转换检查"""
        assert populated_registry.can_convert("markdown", "html") is True
        assert populated_registry.can_convert("html", "markdown") is True
        assert populated_registry.can_convert("text", "pdf") is True

    def test_can_convert_unsupported_source(self, populated_registry):
        """测试不支持的源格式"""
        assert populated_registry.can_convert("invalid", "html") is False

    def test_can_convert_unsupported_target(self, populated_registry):
        """测试不支持的目标格式"""
        assert populated_registry.can_convert("markdown", "invalid") is False

    def test_can_convert_case_insensitive(self, populated_registry):
        """测试转换检查大小写不敏感"""
        assert populated_registry.can_convert("MARKDOWN", "HTML") is True
        assert populated_registry.can_convert("Markdown", "Pdf") is True

    def test_multiple_parsers_same_format(self, registry):
        """测试同一格式注册多个解析器（后注册的覆盖）"""
        parser1 = MarkdownParser()
        parser2 = MarkdownParser()

        registry.register_parser(parser1)
        registry.register_parser(parser2)

        # 后注册的应该覆盖
        assert registry.get_parser("markdown") is parser2

    def test_multiple_renderers_same_format(self, registry):
        """测试同一格式注册多个渲染器"""
        renderer1 = HTMLRenderer()
        renderer2 = HTMLRenderer()

        registry.register_renderer(renderer1)
        registry.register_renderer(renderer2)

        assert registry.find_renderer("html") is renderer2


class TestGlobalRegistry:
    """测试全局注册表函数"""

    def test_get_registry_singleton(self):
        """测试获取全局注册表单例"""
        registry1 = get_registry()
        registry2 = get_registry()

        assert registry1 is registry2

    def test_register_parser_global(self):
        """测试全局注册解析器"""
        # 清空全局注册表
        from mcp_document_converter import registry as reg_module

        reg_module._registry = None

        parser = MarkdownParser()
        register_parser(parser)

        registry = get_registry()
        assert registry.get_parser("markdown") is parser

        # 清理
        reg_module._registry = None

    def test_register_renderer_global(self):
        """测试全局注册渲染器"""
        from mcp_document_converter import registry as reg_module

        reg_module._registry = None

        renderer = HTMLRenderer()
        register_renderer(renderer)

        registry = get_registry()
        assert registry.find_renderer("html") is renderer

        # 清理
        reg_module._registry = None

    def test_find_parser_global(self):
        """测试全局查找解析器"""
        from mcp_document_converter import registry as reg_module

        reg_module._registry = None

        register_parser(MarkdownParser())

        parser = find_parser("test.md")
        assert parser is not None
        assert parser.format_name == "markdown"

        # 清理
        reg_module._registry = None

    def test_find_renderer_global(self):
        """测试全局查找渲染器"""
        from mcp_document_converter import registry as reg_module

        reg_module._registry = None

        register_renderer(HTMLRenderer())

        renderer = find_renderer("html")
        assert renderer is not None
        assert renderer.format_name == "html"

        # 清理
        reg_module._registry = None
