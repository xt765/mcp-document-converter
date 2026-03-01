"""
测试中间表示 - core/ir.py
"""

from datetime import datetime

from mcp_document_converter.core.ir import (
    Asset,
    DocumentIR,
    Node,
    NodeType,
    create_code_block,
    create_heading,
    create_link,
    create_paragraph,
)


class TestNodeType:
    """测试 NodeType 枚举"""

    def test_node_type_values(self):
        """测试节点类型值"""
        assert NodeType.DOCUMENT.value == "document"
        assert NodeType.HEADING.value == "heading"
        assert NodeType.PARAGRAPH.value == "paragraph"
        assert NodeType.CODE_BLOCK.value == "code_block"
        assert NodeType.LIST.value == "list"
        assert NodeType.LIST_ITEM.value == "list_item"
        assert NodeType.TABLE.value == "table"
        assert NodeType.TABLE_ROW.value == "table_row"
        assert NodeType.TABLE_CELL.value == "table_cell"
        assert NodeType.BLOCKQUOTE.value == "blockquote"
        assert NodeType.HORIZONTAL_RULE.value == "hr"
        assert NodeType.PAGE_BREAK.value == "page_break"
        assert NodeType.TEXT.value == "text"
        assert NodeType.LINK.value == "link"
        assert NodeType.IMAGE.value == "image"
        assert NodeType.CODE_INLINE.value == "code_inline"
        assert NodeType.EMPHASIS.value == "emphasis"
        assert NodeType.STRONG.value == "strong"
        assert NodeType.STRIKETHROUGH.value == "strike"
        assert NodeType.SUBSCRIPT.value == "sub"
        assert NodeType.SUPERSCRIPT.value == "sup"
        assert NodeType.LINE_BREAK.value == "br"


class TestNode:
    """测试 Node 数据类"""

    def test_node_with_string_content(self):
        """测试字符串内容的节点"""
        node = Node(type=NodeType.TEXT, content="Hello World")

        assert node.type == NodeType.TEXT
        assert node.content == "Hello World"
        assert node.attributes == {}

    def test_node_with_list_content(self):
        """测试列表内容的节点"""
        child = Node(type=NodeType.TEXT, content="child")
        node = Node(type=NodeType.PARAGRAPH, content=[child])

        assert node.type == NodeType.PARAGRAPH
        assert isinstance(node.content, list)
        assert len(node.content) == 1
        assert node.content[0].type == NodeType.TEXT

    def test_node_with_attributes(self):
        """测试带属性的节点"""
        node = Node(
            type=NodeType.HEADING,
            content="Title",
            attributes={"level": 1},
        )

        assert node.attributes == {"level": 1}

    def test_node_post_init_converts_non_node_items(self):
        """测试 __post_init__ 转换非 Node 项"""
        node = Node(type=NodeType.PARAGRAPH, content=["text", "more text"])  # type: ignore[reportArgumentType]

        assert isinstance(node.content, list)
        assert all(isinstance(item, Node) for item in node.content)
        assert node.content[0].content == "text"
        assert node.content[1].content == "more text"

    def test_node_post_init_preserves_node_items(self):
        """测试 __post_init__ 保留 Node 项"""
        child1 = Node(type=NodeType.TEXT, content="text1")
        child2 = Node(type=NodeType.TEXT, content="text2")
        node = Node(type=NodeType.PARAGRAPH, content=[child1, child2])

        assert node.content[0] is child1
        assert node.content[1] is child2


class TestAsset:
    """测试 Asset 数据类"""

    def test_asset_creation(self):
        """测试创建资源"""
        asset = Asset(
            id="img1",
            type="image",
            mime_type="image/png",
            data=b"fake_image_data",
        )

        assert asset.id == "img1"
        assert asset.type == "image"
        assert asset.mime_type == "image/png"
        assert asset.data == b"fake_image_data"
        assert asset.filename is None

    def test_asset_with_filename(self):
        """测试带文件名的资源"""
        asset = Asset(
            id="img1",
            type="image",
            mime_type="image/png",
            data=b"fake_image_data",
            filename="image.png",
        )

        assert asset.filename == "image.png"


class TestDocumentIR:
    """测试 DocumentIR 数据类"""

    def test_document_ir_creation(self):
        """测试创建文档 IR"""
        doc = DocumentIR()

        assert doc.title is None
        assert doc.author is None
        assert doc.created_at is None
        assert doc.modified_at is None
        assert doc.metadata == {}
        assert doc.content == []
        assert doc.assets == []
        assert doc.styles == {}

    def test_document_ir_with_values(self):
        """测试带值的文档 IR"""
        now = datetime.now()
        doc = DocumentIR(
            title="测试文档",
            author="测试作者",
            created_at=now,
            modified_at=now,
            metadata={"key": "value"},
        )

        assert doc.title == "测试文档"
        assert doc.author == "测试作者"
        assert doc.created_at == now
        assert doc.modified_at == now
        assert doc.metadata == {"key": "value"}

    def test_add_node(self):
        """测试添加节点"""
        doc = DocumentIR()
        node = Node(type=NodeType.PARAGRAPH, content="test")

        doc.add_node(node)

        assert len(doc.content) == 1
        assert doc.content[0] == node

    def test_add_multiple_nodes(self):
        """测试添加多个节点"""
        doc = DocumentIR()
        node1 = Node(type=NodeType.HEADING, content="Title")
        node2 = Node(type=NodeType.PARAGRAPH, content="Content")

        doc.add_node(node1)
        doc.add_node(node2)

        assert len(doc.content) == 2

    def test_add_asset(self):
        """测试添加资源"""
        doc = DocumentIR()
        asset = Asset(
            id="img1",
            type="image",
            mime_type="image/png",
            data=b"data",
        )

        doc.add_asset(asset)

        assert len(doc.assets) == 1
        assert doc.assets[0] == asset

    def test_get_text_content_simple(self):
        """测试获取简单文本内容"""
        doc = DocumentIR()
        doc.add_node(
            Node(type=NodeType.PARAGRAPH, content=[Node(type=NodeType.TEXT, content="Hello")])
        )

        text = doc.get_text_content()

        assert "Hello" in text

    def test_get_text_content_multiple_nodes(self):
        """测试获取多个节点的文本内容"""
        doc = DocumentIR()
        doc.add_node(
            Node(type=NodeType.HEADING, content=[Node(type=NodeType.TEXT, content="Title")])
        )
        doc.add_node(
            Node(type=NodeType.PARAGRAPH, content=[Node(type=NodeType.TEXT, content="Content")])
        )

        text = doc.get_text_content()

        assert "Title" in text
        assert "Content" in text

    def test_get_text_content_nested(self):
        """测试获取嵌套节点的文本内容"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.PARAGRAPH,
                content=[
                    Node(type=NodeType.TEXT, content="Hello "),
                    Node(type=NodeType.STRONG, content=[Node(type=NodeType.TEXT, content="World")]),
                ],
            )
        )

        text = doc.get_text_content()

        assert "Hello World" in text

    def test_get_text_content_empty(self):
        """测试空文档获取文本内容"""
        doc = DocumentIR()

        text = doc.get_text_content()

        assert text == ""

    def test_to_dict(self):
        """测试转换为字典"""
        now = datetime(2024, 1, 1, 12, 0, 0)
        doc = DocumentIR(
            title="测试文档",
            author="作者",
            created_at=now,
            modified_at=now,
            metadata={"key": "value"},
        )
        doc.add_node(
            Node(type=NodeType.PARAGRAPH, content=[Node(type=NodeType.TEXT, content="内容")])
        )
        doc.add_asset(
            Asset(
                id="img1",
                type="image",
                mime_type="image/png",
                data=b"data",
                filename="image.png",
            )
        )

        result = doc.to_dict()

        assert result["title"] == "测试文档"
        assert result["author"] == "作者"
        assert result["created_at"] == now.isoformat()
        assert result["modified_at"] == now.isoformat()
        assert result["metadata"] == {"key": "value"}
        assert len(result["content"]) == 1
        assert len(result["assets"]) == 1
        assert result["assets"][0]["id"] == "img1"
        assert "data" not in result["assets"][0]  # 数据不序列化

    def test_to_dict_node_structure(self):
        """测试节点字典结构"""
        doc = DocumentIR()
        doc.add_node(
            Node(
                type=NodeType.HEADING,
                content=[Node(type=NodeType.TEXT, content="Title")],
                attributes={"level": 1},
            )
        )

        result = doc.to_dict()

        node_dict = result["content"][0]
        assert node_dict["type"] == "heading"
        assert node_dict["attributes"] == {"level": 1}
        assert isinstance(node_dict["content"], list)


class TestConvenienceFunctions:
    """测试便捷函数"""

    def test_create_heading(self):
        """测试创建标题节点"""
        node = create_heading("标题文本", level=2)

        assert node.type == NodeType.HEADING
        assert node.attributes == {"level": 2}
        assert isinstance(node.content, list)
        assert node.content[0].type == NodeType.TEXT
        assert node.content[0].content == "标题文本"

    def test_create_heading_default_level(self):
        """测试创建标题节点默认级别"""
        node = create_heading("标题")

        assert node.attributes == {"level": 1}

    def test_create_paragraph(self):
        """测试创建段落节点"""
        node = create_paragraph("段落文本")

        assert node.type == NodeType.PARAGRAPH
        assert isinstance(node.content, list)
        assert node.content[0].type == NodeType.TEXT
        assert node.content[0].content == "段落文本"

    def test_create_code_block(self):
        """测试创建代码块节点"""
        node = create_code_block("print('hello')", language="python")

        assert node.type == NodeType.CODE_BLOCK
        assert node.content == "print('hello')"
        assert node.attributes == {"language": "python"}

    def test_create_code_block_without_language(self):
        """测试创建不带语言的代码块节点"""
        node = create_code_block("code")

        assert node.type == NodeType.CODE_BLOCK
        assert node.content == "code"
        assert node.attributes == {}

    def test_create_link(self):
        """测试创建链接节点"""
        node = create_link("链接文本", "https://example.com")

        assert node.type == NodeType.LINK
        assert node.attributes == {"url": "https://example.com"}
        assert isinstance(node.content, list)
        assert node.content[0].content == "链接文本"
