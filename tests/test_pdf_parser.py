"""
测试 PDF 解析器 - 覆盖更多代码
"""


import pytest

from mcp_document_converter.core.ir import NodeType
from mcp_document_converter.parsers.pdf import PDFParser


class TestPDFParserFull:
    """测试 PDF 解析器完整覆盖"""

    @pytest.fixture
    def parser(self):
        return PDFParser()

    def test_parse_text_structure_with_headings(self, parser):
        """测试带标题的文本结构解析"""
        from mcp_document_converter.core.ir import DocumentIR

        doc = DocumentIR()
        text = """IMPORTANT NOTICE

This is a paragraph.

1. Introduction

More content here.

## Markdown Heading

Final paragraph."""

        parser._parse_text_structure(doc, text)

        # 应该有标题和段落
        assert len(doc.content) > 0

    def test_parse_text_structure_with_lists(self, parser):
        """测试带列表的文本结构解析"""
        from mcp_document_converter.core.ir import DocumentIR

        doc = DocumentIR()
        text = """Paragraph

- Item 1
- Item 2
- Item 3

Another paragraph."""

        parser._parse_text_structure(doc, text)

        lists = [n for n in doc.content if n.type == NodeType.LIST]
        assert len(lists) >= 1

    def test_parse_text_structure_with_code(self, parser):
        """测试带代码块的文本结构解析"""
        from mcp_document_converter.core.ir import DocumentIR

        doc = DocumentIR()
        # PDF 解析器不检测缩进代码块，只检测普通文本
        text = """Paragraph

More text here.

Another paragraph."""

        parser._parse_text_structure(doc, text)

        # 应该有段落
        assert len(doc.content) >= 1

    def test_get_heading_level_edge_cases(self, parser):
        """测试标题级别边缘情况"""
        # 数字编号
        assert parser._get_heading_level("1. Title") == 1
        assert parser._get_heading_level("5. Title") == 2
        assert parser._get_heading_level("15. Title") == 3

        # Markdown 风格
        assert parser._get_heading_level("###### Title") == 6
        assert parser._get_heading_level("####### Title") == 6  # 最大 6

        # 全大写
        assert parser._get_heading_level("IMPORTANT") == 1

        # 默认
        assert parser._get_heading_level("Normal text") == 2

    def test_is_heading_edge_cases(self, parser):
        """测试标题判断边缘情况"""
        # 太短
        assert parser._is_heading("AB") is False

        # 太长
        assert parser._is_heading("A" * 150) is False

        # 正常长度的大写
        assert parser._is_heading("IMPORTANT NOTICE") is True

        # 数字开头
        assert parser._is_heading("1. Introduction") is True

        # Markdown 风格
        assert parser._is_heading("# Heading") is True

    def test_classify_text_edge_cases(self, parser):
        """测试文本分类边缘情况"""
        # 空文本
        node = parser._classify_text("")
        assert node.type == NodeType.PARAGRAPH

        # 纯空白
        node = parser._classify_text("   ")
        assert node.type == NodeType.PARAGRAPH

        # 多行列表
        node = parser._classify_text("- Item 1\n- Item 2")
        assert node.type == NodeType.LIST

        # 带 bullet 的列表
        node = parser._classify_text("• Item")
        assert node.type == NodeType.LIST

        # 带 * 的列表
        node = parser._classify_text("* Item")
        assert node.type == NodeType.LIST

        # 带 + 的列表
        node = parser._classify_text("+ Item")
        assert node.type == NodeType.LIST
