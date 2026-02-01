"""核心模块 - 中间表示、解析器/渲染器基类、转换引擎"""

from .ir import DocumentIR, Node, NodeType, Asset
from .parser import BaseParser
from .renderer import BaseRenderer
from .engine import DocumentConverter

__all__ = [
    "DocumentIR",
    "Node",
    "NodeType",
    "Asset",
    "BaseParser",
    "BaseRenderer",
    "DocumentConverter",
]
