"""
中间表示 (Intermediate Representation) - 所有文档格式的统一抽象
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class NodeType(Enum):
    """文档节点类型"""

    # 块级元素
    DOCUMENT = "document"  # 文档根节点
    HEADING = "heading"  # 标题 (h1-h6)
    PARAGRAPH = "paragraph"  # 段落
    CODE_BLOCK = "code_block"  # 代码块
    LIST = "list"  # 列表 (有序/无序)
    LIST_ITEM = "list_item"  # 列表项
    TABLE = "table"  # 表格
    TABLE_ROW = "table_row"  # 表格行
    TABLE_CELL = "table_cell"  # 表格单元格
    BLOCKQUOTE = "blockquote"  # 引用块
    HORIZONTAL_RULE = "hr"  # 分隔线
    PAGE_BREAK = "page_break"  # 分页符

    # 行内元素
    TEXT = "text"  # 纯文本
    LINK = "link"  # 超链接
    IMAGE = "image"  # 图片
    CODE_INLINE = "code_inline"  # 行内代码
    EMPHASIS = "emphasis"  # 斜体
    STRONG = "strong"  # 粗体
    STRIKETHROUGH = "strike"  # 删除线
    SUBSCRIPT = "sub"  # 下标
    SUPERSCRIPT = "sup"  # 上标
    LINE_BREAK = "br"  # 换行


@dataclass
class Node:
    """
    文档树节点

    Attributes:
        type: 节点类型
        content: 节点内容（文本或子节点列表）
        attributes: 节点属性（如 heading level, link url 等）
    """

    type: NodeType
    content: Union[str, List["Node"]]
    attributes: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """确保 content 类型正确"""
        if isinstance(self.content, list):
            # 确保所有子元素都是 Node 类型
            self.content = [
                item
                if isinstance(item, Node)
                else Node(type=NodeType.TEXT, content=str(item), attributes={})
                for item in self.content
            ]


@dataclass
class Asset:
    """
    文档资源（图片、附件等）

    Attributes:
        id: 资源唯一标识
        type: 资源类型 (image, attachment, etc.)
        mime_type: MIME 类型
        data: 二进制数据
        filename: 文件名
    """

    id: str
    type: str
    mime_type: str
    data: bytes
    filename: Optional[str] = None


@dataclass
class DocumentIR:
    """
    文档中间表示 - 所有格式的统一抽象

    这是整个转换系统的核心数据结构，所有解析器都将文档解析为此格式，
    所有渲染器都从此格式渲染为目标格式。

    Attributes:
        title: 文档标题
        author: 作者
        created_at: 创建时间
        modified_at: 修改时间
        metadata: 元数据字典
        content: 文档内容树（根节点）
        assets: 资源列表（图片、附件等）
        styles: 样式信息
    """

    title: Optional[str] = None
    author: Optional[str] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    content: List[Node] = field(default_factory=list)
    assets: List[Asset] = field(default_factory=list)
    styles: Dict[str, Any] = field(default_factory=dict)

    def add_node(self, node: Node) -> None:
        """添加节点到文档内容"""
        self.content.append(node)

    def add_asset(self, asset: Asset) -> None:
        """添加资源到文档"""
        self.assets.append(asset)

    def get_text_content(self) -> str:
        """提取纯文本内容（用于 Text 渲染）"""
        texts = []

        def extract_text(node: Union[Node, str]) -> str:
            if isinstance(node, str):
                return node
            if isinstance(node, Node):
                if isinstance(node.content, str):
                    return node.content
                elif isinstance(node.content, list):
                    return "".join(extract_text(child) for child in node.content)
            return ""

        for node in self.content:
            text = extract_text(node)
            if text.strip():
                texts.append(text)

        return "\n\n".join(texts)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（用于 JSON 序列化）"""

        def node_to_dict(node: Node) -> Dict[str, Any]:
            content = (
                node.content
                if isinstance(node.content, str)
                else [node_to_dict(child) for child in node.content]
            )
            return {
                "type": node.type.value,
                "content": content,
                "attributes": node.attributes,
            }

        return {
            "title": self.title,
            "author": self.author,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "modified_at": self.modified_at.isoformat() if self.modified_at else None,
            "metadata": self.metadata,
            "content": [node_to_dict(node) for node in self.content],
            "assets": [
                {
                    "id": asset.id,
                    "type": asset.type,
                    "mime_type": asset.mime_type,
                    "filename": asset.filename,
                }
                for asset in self.assets
            ],
            "styles": self.styles,
        }


# 便捷函数
def create_heading(text: str, level: int = 1) -> Node:
    """创建标题节点"""
    return Node(
        type=NodeType.HEADING,
        content=[Node(type=NodeType.TEXT, content=text)],
        attributes={"level": level},
    )


def create_paragraph(text: str) -> Node:
    """创建段落节点"""
    return Node(type=NodeType.PARAGRAPH, content=[Node(type=NodeType.TEXT, content=text)])


def create_code_block(code: str, language: Optional[str] = None) -> Node:
    """创建代码块节点"""
    return Node(
        type=NodeType.CODE_BLOCK,
        content=code,
        attributes={"language": language} if language else {},
    )


def create_link(text: str, url: str) -> Node:
    """创建链接节点"""
    return Node(
        type=NodeType.LINK,
        content=[Node(type=NodeType.TEXT, content=text)],
        attributes={"url": url},
    )
