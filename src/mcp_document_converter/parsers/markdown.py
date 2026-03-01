"""
Markdown 解析器 - 将 Markdown 解析为中间表示
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional, Union

import markdown
import yaml
from bs4 import BeautifulSoup, Tag

from ..core.ir import DocumentIR, Node, NodeType
from ..core.parser import BaseParser, ParseError


class MarkdownParser(BaseParser):
    """
    Markdown 文档解析器

    支持标准 Markdown 和 GFM (GitHub Flavored Markdown) 扩展。
    支持 YAML Front Matter 元数据。
    """

    @property
    def supported_extensions(self) -> List[str]:
        return [".md", ".markdown", ".mdown", ".mkd"]

    @property
    def format_name(self) -> str:
        return "markdown"

    @property
    def mime_types(self) -> List[str]:
        return ["text/markdown", "text/x-markdown"]

    def parse(self, source: Union[str, Path, bytes], **options: Any) -> DocumentIR:
        """
        解析 Markdown 文档

        Args:
            source: Markdown 文件路径或内容
            **options: 解析选项
                - extensions: Markdown 扩展列表
                - extract_metadata: 是否提取 YAML Front Matter

        Returns:
            DocumentIR: 文档的中间表示
        """
        try:
            # 读取内容
            content = self._read_source(source)
            if isinstance(content, bytes):
                content = content.decode("utf-8")

            # 提取 YAML Front Matter
            metadata = {}
            extract_metadata = options.get("extract_metadata", True)

            if extract_metadata:
                content, metadata = self._extract_front_matter(content)

            # 配置 Markdown 扩展
            default_extensions = [
                "fenced_code",  # 代码块
                "tables",  # 表格
                "toc",  # 目录
                "nl2br",  # 换行转 <br>
            ]
            extensions = options.get("extensions", default_extensions)

            # 转换为 HTML
            md = markdown.Markdown(extensions=extensions)
            html_content = md.convert(content)

            # 解析 HTML 为 IR
            document = self._html_to_ir(html_content)

            # 设置元数据
            document.metadata = metadata
            document.title = metadata.get("title")
            document.author = metadata.get("author")

            # 解析日期
            if "date" in metadata:
                document.created_at = self._parse_date(metadata["date"])
            if "modified" in metadata:
                document.modified_at = self._parse_date(metadata["modified"])

            # 如果没有标题，从第一个 h1 提取
            if not document.title:
                for node in document.content:
                    if node.type == NodeType.HEADING and node.attributes.get("level") == 1:
                        document.title = self._extract_text(node)
                        break

            return document

        except Exception as e:
            raise ParseError(f"Markdown 解析失败: {str(e)}")

    def _extract_front_matter(self, content: str) -> tuple:
        """
        提取 YAML Front Matter

        Args:
            content: Markdown 内容

        Returns:
            (content_without_front_matter, metadata_dict)
        """
        pattern = r"^---\s*\n(.*?)\n---\s*\n"
        match = re.match(pattern, content, re.DOTALL)

        if match:
            front_matter = match.group(1)
            remaining_content = content[match.end() :]
            try:
                metadata = yaml.safe_load(front_matter) or {}
                return remaining_content, metadata
            except yaml.YAMLError:
                pass

        return content, {}

    def _html_to_ir(self, html: str) -> DocumentIR:
        """
        将 HTML 转换为中间表示

        Args:
            html: HTML 内容

        Returns:
            DocumentIR
        """
        soup = BeautifulSoup(html, "html.parser")
        document = DocumentIR()

        # 解析所有顶级元素
        for element in soup.find_all(recursive=False):
            node = self._parse_element(element)
            if node:
                document.add_node(node)

        return document

    def _parse_element(self, element: Tag) -> Optional[Node]:
        """
        解析单个 HTML 元素为 IR 节点

        Args:
            element: BeautifulSoup 元素

        Returns:
            Node 或 None
        """
        tag_name = element.name

        if tag_name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            level = int(tag_name[1])
            return Node(
                type=NodeType.HEADING,
                content=self._parse_inline_content(element),
                attributes={"level": level},
            )

        elif tag_name == "p":
            return Node(type=NodeType.PARAGRAPH, content=self._parse_inline_content(element))

        elif tag_name == "pre":
            # 代码块
            code = element.find("code")
            if code:
                language = None
                classes = code.get("class", [])
                for cls in classes:
                    if cls.startswith("language-"):
                        language = cls[9:]
                        break

                return Node(
                    type=NodeType.CODE_BLOCK,
                    content=code.get_text(),
                    attributes={"language": language} if language else {},
                )
            else:
                return Node(type=NodeType.CODE_BLOCK, content=element.get_text())

        elif tag_name in ["ul", "ol"]:
            list_type = "unordered" if tag_name == "ul" else "ordered"
            items = []
            for li in element.find_all("li", recursive=False):
                items.append(Node(type=NodeType.LIST_ITEM, content=self._parse_inline_content(li)))

            return Node(type=NodeType.LIST, content=items, attributes={"type": list_type})

        elif tag_name == "table":
            return self._parse_table(element)

        elif tag_name == "blockquote":
            content = []
            for child in element.find_all(recursive=False):
                node = self._parse_element(child)
                if node:
                    content.append(node)

            return Node(type=NodeType.BLOCKQUOTE, content=content)

        elif tag_name == "hr":
            return Node(type=NodeType.HORIZONTAL_RULE, content="")

        elif tag_name == "div":
            # 递归解析 div 内容
            content = []
            for child in element.find_all(recursive=False):
                node = self._parse_element(child)
                if node:
                    content.append(node)
            return Node(type=NodeType.DOCUMENT, content=content) if content else None

        return None

    def _parse_inline_content(self, element: Tag) -> List[Node]:
        """
        解析行内内容

        Args:
            element: 包含行内元素的标签

        Returns:
            节点列表
        """
        nodes = []

        for content in element.contents:
            if isinstance(content, str):
                text = content.strip()
                if text:
                    nodes.append(Node(type=NodeType.TEXT, content=text))
            elif content.name == "br":
                nodes.append(Node(type=NodeType.LINE_BREAK, content=""))
            elif content.name == "strong" or content.name == "b":
                nodes.append(
                    Node(type=NodeType.STRONG, content=self._parse_inline_content(content))
                )
            elif content.name == "em" or content.name == "i":
                nodes.append(
                    Node(type=NodeType.EMPHASIS, content=self._parse_inline_content(content))
                )
            elif content.name == "code":
                nodes.append(Node(type=NodeType.CODE_INLINE, content=content.get_text()))
            elif content.name == "a":
                nodes.append(
                    Node(
                        type=NodeType.LINK,
                        content=self._parse_inline_content(content),
                        attributes={"url": content.get("href", "")},
                    )
                )
            elif content.name == "img":
                nodes.append(
                    Node(
                        type=NodeType.IMAGE,
                        content="",
                        attributes={
                            "src": content.get("src", ""),
                            "alt": content.get("alt", ""),
                            "title": content.get("title", ""),
                        },
                    )
                )
            elif content.name == "del" or content.name == "s":
                nodes.append(
                    Node(type=NodeType.STRIKETHROUGH, content=self._parse_inline_content(content))
                )
            elif content.name:
                # 其他标签，递归解析
                nodes.extend(self._parse_inline_content(content))

        return nodes

    def _parse_table(self, element: Tag) -> Node:
        """解析表格"""
        rows = []

        # 解析表头
        thead = element.find("thead")
        if thead:
            for tr in thead.find_all("tr"):
                cells = []
                for th in tr.find_all(["th", "td"]):
                    cells.append(
                        Node(
                            type=NodeType.TABLE_CELL,
                            content=self._parse_inline_content(th),
                            attributes={"header": True},
                        )
                    )
                if cells:
                    rows.append(Node(type=NodeType.TABLE_ROW, content=cells))

        # 解析表体
        tbody = element.find("tbody")
        if tbody:
            for tr in tbody.find_all("tr"):
                cells = []
                for td in tr.find_all("td"):
                    cells.append(
                        Node(type=NodeType.TABLE_CELL, content=self._parse_inline_content(td))
                    )
                if cells:
                    rows.append(Node(type=NodeType.TABLE_ROW, content=cells))

        # 如果没有 thead/tbody，直接解析 tr
        if not thead and not tbody:
            is_first_row = True
            for tr in element.find_all("tr"):
                cells = []
                for cell in tr.find_all(["th", "td"]):
                    cells.append(
                        Node(
                            type=NodeType.TABLE_CELL,
                            content=self._parse_inline_content(cell),
                            attributes={"header": is_first_row} if is_first_row else {},
                        )
                    )
                if cells:
                    rows.append(Node(type=NodeType.TABLE_ROW, content=cells))
                is_first_row = False

        return Node(type=NodeType.TABLE, content=rows)

    def _extract_text(self, node: Node) -> str:
        """从节点中提取纯文本"""
        if isinstance(node.content, str):
            return node.content
        elif isinstance(node.content, list):
            return "".join(self._extract_text(child) for child in node.content)
        return ""

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """解析日期字符串"""
        formats = [
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M:%S",
            "%d/%m/%Y",
            "%m/%d/%Y",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None
