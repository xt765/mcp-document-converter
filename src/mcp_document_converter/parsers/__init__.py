"""解析器模块 - 将各种格式解析为中间表示"""

from .docx import DOCXParser
from .html import HTMLParser
from .markdown import MarkdownParser
from .pdf import PDFParser
from .text import TextParser

__all__ = [
    "MarkdownParser",
    "HTMLParser",
    "DOCXParser",
    "PDFParser",
    "TextParser",
]
