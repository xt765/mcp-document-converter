"""
MCP Document Converter - 支持多格式文档转换的 MCP 工具

支持格式:
- Markdown (.md, .markdown)
- HTML (.html, .htm)
- DOCX (.docx)
- PDF (.pdf)
- Text (.txt)
"""

__version__ = "0.1.0"
__all__ = ["DocumentConverter", "DocumentIR", "BaseParser", "BaseRenderer"]

from mcp_document_converter.core.engine import DocumentConverter
from mcp_document_converter.core.ir import DocumentIR
from mcp_document_converter.core.parser import BaseParser
from mcp_document_converter.core.renderer import BaseRenderer
