"""
测试 MCP Server - 服务端工具接口测试
"""

import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from mcp_document_converter.server import (
    _handle_can_convert,
    _handle_convert_document,
    _handle_list_supported_formats,
    create_server,
)
from mcp_document_converter.registry import ConverterRegistry, get_registry
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


class TestCreateServer:
    """测试 create_server 函数"""

    def test_create_server_returns_server(self):
        """测试创建服务器返回 Server 实例"""
        server = create_server()
        assert server is not None
        assert server.name == "mcp-document-converter"

    def test_server_is_callable(self):
        """测试服务器可调用"""
        server = create_server()
        assert callable(server.run)


class TestHandleConvertDocument:
    """测试文档转换处理"""

    @pytest.mark.asyncio
    async def test_convert_missing_source_path(self, converter):
        """测试缺少源文件路径"""
        arguments = {"target_format": "html"}
        result = await _handle_convert_document(converter, arguments)

        assert len(result) == 1
        data = json.loads(result[0].text)
        assert data["success"] is False
        assert "Missing required parameters" in data["error"]

    @pytest.mark.asyncio
    async def test_convert_missing_target_format(self, converter):
        """测试缺少目标格式"""
        arguments = {"source_path": "test.md"}
        result = await _handle_convert_document(converter, arguments)

        assert len(result) == 1
        data = json.loads(result[0].text)
        assert data["success"] is False
        assert "Missing required parameters" in data["error"]

    @pytest.mark.asyncio
    async def test_convert_file_not_found(self, converter, temp_dir):
        """测试文件不存在"""
        arguments = {
            "source_path": str(temp_dir / "nonexistent.md"),
            "target_format": "html",
        }
        result = await _handle_convert_document(converter, arguments)

        assert len(result) == 1
        data = json.loads(result[0].text)
        assert data["success"] is False
        assert "文件不存在" in data["error"]

    @pytest.mark.asyncio
    async def test_convert_success(self, converter, temp_dir, sample_markdown):
        """测试成功转换"""
        # 创建测试文件
        md_path = temp_dir / "test.md"
        md_path.write_text(sample_markdown, encoding="utf-8")

        arguments = {
            "source_path": str(md_path),
            "target_format": "html",
        }
        result = await _handle_convert_document(converter, arguments)

        assert len(result) == 1
        data = json.loads(result[0].text)
        assert data["success"] is True
        assert "output_path" in data
        assert data["target_format"] == "html"

    @pytest.mark.asyncio
    async def test_convert_with_output_path(self, converter, temp_dir, sample_markdown):
        """测试指定输出路径"""
        md_path = temp_dir / "input.md"
        md_path.write_text(sample_markdown, encoding="utf-8")
        output_path = temp_dir / "output.html"

        arguments = {
            "source_path": str(md_path),
            "target_format": "html",
            "output_path": str(output_path),
        }
        result = await _handle_convert_document(converter, arguments)

        assert len(result) == 1
        data = json.loads(result[0].text)
        assert data["success"] is True
        assert Path(data["output_path"]) == output_path

    @pytest.mark.asyncio
    async def test_convert_with_source_format(self, converter, temp_dir, sample_markdown):
        """测试指定源格式"""
        md_path = temp_dir / "test.custom"
        md_path.write_text(sample_markdown, encoding="utf-8")

        arguments = {
            "source_path": str(md_path),
            "target_format": "html",
            "source_format": "markdown",
        }
        result = await _handle_convert_document(converter, arguments)

        assert len(result) == 1
        data = json.loads(result[0].text)
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_convert_unsupported_format(self, converter, temp_dir):
        """测试不支持的格式"""
        file_path = temp_dir / "test.xyz"
        file_path.write_text("test content", encoding="utf-8")

        arguments = {
            "source_path": str(file_path),
            "target_format": "invalid_format",
        }
        result = await _handle_convert_document(converter, arguments)

        assert len(result) == 1
        data = json.loads(result[0].text)
        assert data["success"] is False


class TestHandleListSupportedFormats:
    """测试列出支持格式"""

    @pytest.mark.asyncio
    async def test_list_formats_returns_data(self, setup_registry):
        """测试返回格式列表"""
        result = await _handle_list_supported_formats(setup_registry)

        assert len(result) == 1
        data = json.loads(result[0].text)

        assert "parsers" in data
        assert "renderers" in data
        assert "conversion_matrix" in data
        assert "summary" in data

    @pytest.mark.asyncio
    async def test_list_formats_contains_expected(self, setup_registry):
        """测试包含预期格式"""
        result = await _handle_list_supported_formats(setup_registry)
        data = json.loads(result[0].text)

        parser_formats = [p["format"] for p in data["parsers"]]
        renderer_formats = [r["format"] for r in data["renderers"]]

        assert "markdown" in parser_formats
        assert "html" in parser_formats
        assert "docx" in parser_formats
        assert "pdf" in parser_formats
        assert "text" in parser_formats

        assert "html" in renderer_formats
        assert "markdown" in renderer_formats
        assert "docx" in renderer_formats
        assert "pdf" in renderer_formats
        assert "text" in renderer_formats

    @pytest.mark.asyncio
    async def test_list_formats_summary(self, setup_registry):
        """测试格式摘要"""
        result = await _handle_list_supported_formats(setup_registry)
        data = json.loads(result[0].text)

        summary = data["summary"]
        assert summary["total_source_formats"] == 5
        assert summary["total_target_formats"] == 5
        assert summary["possible_conversions"] == 25


class TestHandleCanConvert:
    """测试检查转换可行性"""

    @pytest.mark.asyncio
    async def test_can_convert_missing_source_format(self, converter):
        """测试缺少源格式"""
        arguments = {"target_format": "html"}
        result = await _handle_can_convert(converter, arguments)

        assert len(result) == 1
        data = json.loads(result[0].text)
        assert "error" in data

    @pytest.mark.asyncio
    async def test_can_convert_missing_target_format(self, converter):
        """测试缺少目标格式"""
        arguments = {"source_format": "markdown"}
        result = await _handle_can_convert(converter, arguments)

        assert len(result) == 1
        data = json.loads(result[0].text)
        assert "error" in data

    @pytest.mark.asyncio
    async def test_can_convert_supported(self, converter):
        """测试支持的转换"""
        arguments = {
            "source_format": "markdown",
            "target_format": "html",
        }
        result = await _handle_can_convert(converter, arguments)

        assert len(result) == 1
        data = json.loads(result[0].text)
        assert data["can_convert"] is True
        assert "Supported" in data["message"]

    @pytest.mark.asyncio
    async def test_can_convert_unsupported_source(self, converter):
        """测试不支持的源格式"""
        arguments = {
            "source_format": "invalid",
            "target_format": "html",
        }
        result = await _handle_can_convert(converter, arguments)

        assert len(result) == 1
        data = json.loads(result[0].text)
        assert data["can_convert"] is False

    @pytest.mark.asyncio
    async def test_can_convert_unsupported_target(self, converter):
        """测试不支持的目标格式"""
        arguments = {
            "source_format": "markdown",
            "target_format": "invalid",
        }
        result = await _handle_can_convert(converter, arguments)

        assert len(result) == 1
        data = json.loads(result[0].text)
        assert data["can_convert"] is False
