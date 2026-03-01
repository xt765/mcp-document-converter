"""
测试服务器入口点和其他未覆盖代码
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio


class TestServerEntryPoint:
    """测试服务器入口点"""

    def test_main_sync_function(self):
        """测试 main_sync 函数存在且可调用"""
        from mcp_document_converter.server import main_sync

        assert callable(main_sync)

    @pytest.mark.asyncio
    async def test_main_function(self):
        """测试 main 异步函数"""
        from mcp_document_converter.server import main

        # main 是异步函数
        assert asyncio.iscoroutinefunction(main)


class TestModuleImports:
    """测试模块导入"""

    def test_import_main_module(self):
        """测试导入主模块"""
        import mcp_document_converter

        assert hasattr(mcp_document_converter, "DocumentConverter")

    def test_import_core_module(self):
        """测试导入核心模块"""
        from mcp_document_converter.core import DocumentIR, Node, NodeType
        from mcp_document_converter.core.parser import BaseParser, ParseError
        from mcp_document_converter.core.renderer import BaseRenderer, RenderError

        assert NodeType.HEADING is not None
        assert NodeType.PARAGRAPH is not None

    def test_import_parsers_module(self):
        """测试导入解析器模块"""
        from mcp_document_converter.parsers import (
            MarkdownParser,
            HTMLParser,
            DOCXParser,
            PDFParser,
            TextParser,
        )

        assert MarkdownParser is not None
        assert HTMLParser is not None

    def test_import_renderers_module(self):
        """测试导入渲染器模块"""
        from mcp_document_converter.renderers import (
            MarkdownRenderer,
            HTMLRenderer,
            DOCXRenderer,
            PDFRenderer,
            TextRenderer,
        )

        assert MarkdownRenderer is not None
        assert HTMLRenderer is not None


class TestNodeTypeValues:
    """测试 NodeType 枚举值"""

    def test_all_node_types_exist(self):
        """测试所有节点类型存在"""
        from mcp_document_converter.core.ir import NodeType

        # 块级元素
        assert hasattr(NodeType, "DOCUMENT")
        assert hasattr(NodeType, "HEADING")
        assert hasattr(NodeType, "PARAGRAPH")
        assert hasattr(NodeType, "CODE_BLOCK")
        assert hasattr(NodeType, "LIST")
        assert hasattr(NodeType, "LIST_ITEM")
        assert hasattr(NodeType, "TABLE")
        assert hasattr(NodeType, "TABLE_ROW")
        assert hasattr(NodeType, "TABLE_CELL")
        assert hasattr(NodeType, "BLOCKQUOTE")
        assert hasattr(NodeType, "HORIZONTAL_RULE")
        assert hasattr(NodeType, "PAGE_BREAK")

        # 行内元素
        assert hasattr(NodeType, "TEXT")
        assert hasattr(NodeType, "LINK")
        assert hasattr(NodeType, "IMAGE")
        assert hasattr(NodeType, "CODE_INLINE")
        assert hasattr(NodeType, "EMPHASIS")
        assert hasattr(NodeType, "STRONG")
        assert hasattr(NodeType, "STRIKETHROUGH")
        assert hasattr(NodeType, "SUBSCRIPT")
        assert hasattr(NodeType, "SUPERSCRIPT")
        assert hasattr(NodeType, "LINE_BREAK")


class TestRegistryFunctions:
    """测试注册表函数"""

    def test_get_registry_returns_registry(self):
        """测试 get_registry 返回注册表"""
        from mcp_document_converter.registry import get_registry, ConverterRegistry

        # 清除全局注册表
        import mcp_document_converter.registry as reg_module
        reg_module._registry = None

        registry = get_registry()

        assert isinstance(registry, ConverterRegistry)

        # 清理
        reg_module._registry = None

    def test_register_parser_function(self):
        """测试 register_parser 函数"""
        from mcp_document_converter.registry import register_parser, get_registry
        from mcp_document_converter.parsers import MarkdownParser
        import mcp_document_converter.registry as reg_module

        reg_module._registry = None

        parser = MarkdownParser()
        register_parser(parser)

        registry = get_registry()
        assert registry.get_parser("markdown") is parser

        # 清理
        reg_module._registry = None

    def test_register_renderer_function(self):
        """测试 register_renderer 函数"""
        from mcp_document_converter.registry import register_renderer, get_registry
        from mcp_document_converter.renderers import HTMLRenderer
        import mcp_document_converter.registry as reg_module

        reg_module._registry = None

        renderer = HTMLRenderer()
        register_renderer(renderer)

        registry = get_registry()
        assert registry.find_renderer("html") is renderer

        # 清理
        reg_module._registry = None
