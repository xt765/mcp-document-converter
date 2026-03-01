"""核心模块 - 中间表示、解析器/渲染器基类、转换引擎"""

from .engine import DocumentConverter
from .ir import Asset, DocumentIR, Node, NodeType
from .parser import BaseParser
from .renderer import BaseRenderer

__all__ = [
    "DocumentIR",
    "Node",
    "NodeType",
    "Asset",
    "BaseParser",
    "BaseRenderer",
    "DocumentConverter",
]
