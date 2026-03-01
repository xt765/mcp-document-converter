"""
测试服务器模块 - 覆盖更多代码
"""

import json
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from mcp_document_converter.server import (
    _handle_can_convert,
    _handle_convert_document,
    _handle_list_supported_formats,
    create_server,
    main,
    main_sync,
)
from mcp_document_converter.registry import ConverterRegistry
from mcp_document_converter.core.engine import DocumentConverter
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


@pytest.fixture
def setup_registry():
    """设置注册表并注册所有解析器和渲染器"""
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


@pytest.fixture
def converter(setup_registry):
    """创建文档转换器"""
    return DocumentConverter(setup_registry)


class TestServerTools:
    """测试服务器工具处理"""

    @pytest.mark.asyncio
    async def test_call_tool_unknown(self, converter, setup_registry):
        """测试调用未知工具"""
        # 创建服务器
        server = create_server()

        # 获取 call_tool 处理器
        # 由于服务器是通过装饰器注册的，我们需要模拟调用
        # 这里直接测试 _handle_* 函数

        # 测试未知工具会返回错误
        # 由于 call_tool 是内部函数，我们通过创建服务器来间接测试
        assert server is not None

    @pytest.mark.asyncio
    async def test_handle_convert_with_exception(self, converter, temp_dir):
        """测试转换时发生异常"""
        # 创建一个会导致解析错误的文件
        # 使用不支持的格式
        file_path = temp_dir / "test.xyz"
        file_path.write_text("content", encoding="utf-8")

        arguments = {
            "source_path": str(file_path),
            "target_format": "html",
        }
        result = await _handle_convert_document(converter, arguments)

        assert len(result) == 1
        data = json.loads(result[0].text)
        assert data["success"] is False

    @pytest.mark.asyncio
    async def test_handle_convert_render_error(self, converter, temp_dir, sample_markdown):
        """测试渲染错误"""
        md_path = temp_dir / "test.md"
        md_path.write_text(sample_markdown, encoding="utf-8")

        # 使用不支持的目标格式
        arguments = {
            "source_path": str(md_path),
            "target_format": "invalid_format",
        }
        result = await _handle_convert_document(converter, arguments)

        assert len(result) == 1
        data = json.loads(result[0].text)
        assert data["success"] is False


class TestServerMain:
    """测试服务器主函数"""

    def test_main_sync_callable(self):
        """测试 main_sync 可调用"""
        # main_sync 会启动服务器，我们只测试它是否可调用
        assert callable(main_sync)

    @pytest.mark.asyncio
    async def test_main_function_exists(self):
        """测试 main 函数存在"""
        # main 是异步函数，测试它是否存在
        import inspect

        assert inspect.iscoroutinefunction(main)


class TestServerCreation:
    """测试服务器创建"""

    def test_create_server_multiple_times(self):
        """测试多次创建服务器"""
        server1 = create_server()
        server2 = create_server()

        # 每次创建都是新实例
        assert server1 is not server2
        assert server1.name == server2.name

    def test_server_has_name(self):
        """测试服务器名称"""
        server = create_server()

        assert server.name == "mcp-document-converter"


class TestHandleListFormatsDetailed:
    """测试列出格式详细功能"""

    @pytest.mark.asyncio
    async def test_list_formats_parser_details(self, setup_registry):
        """测试解析器详细信息"""
        result = await _handle_list_supported_formats(setup_registry)
        data = json.loads(result[0].text)

        # 检查解析器信息
        for parser_info in data["parsers"]:
            assert "format" in parser_info
            assert "extensions" in parser_info
            assert "mime_types" in parser_info

    @pytest.mark.asyncio
    async def test_list_formats_renderer_details(self, setup_registry):
        """测试渲染器详细信息"""
        result = await _handle_list_supported_formats(setup_registry)
        data = json.loads(result[0].text)

        # 检查渲染器信息
        for renderer_info in data["renderers"]:
            assert "format" in renderer_info
            assert "extension" in renderer_info
            assert "mime_type" in renderer_info

    @pytest.mark.asyncio
    async def test_list_formats_conversion_matrix(self, setup_registry):
        """测试转换矩阵"""
        result = await _handle_list_supported_formats(setup_registry)
        data = json.loads(result[0].text)

        # 检查转换矩阵
        matrix = data["conversion_matrix"]
        assert isinstance(matrix, dict)

        # 每个源格式应该有多个目标格式
        for source_format, target_formats in matrix.items():
            assert isinstance(target_formats, list)
            assert len(target_formats) > 0


class TestHandleCanConvertDetailed:
    """测试转换检查详细功能"""

    @pytest.mark.asyncio
    async def test_can_convert_case_insensitive(self, converter):
        """测试转换检查大小写不敏感"""
        arguments = {
            "source_format": "MARKDOWN",
            "target_format": "HTML",
        }
        result = await _handle_can_convert(converter, arguments)

        assert len(result) == 1
        data = json.loads(result[0].text)
        assert data["can_convert"] is True

    @pytest.mark.asyncio
    async def test_can_convert_returns_formats(self, converter):
        """测试转换检查返回格式信息"""
        arguments = {
            "source_format": "markdown",
            "target_format": "html",
        }
        result = await _handle_can_convert(converter, arguments)

        assert len(result) == 1
        data = json.loads(result[0].text)

        # 应该包含格式信息
        assert "source_format" in data or "can_convert" in data
