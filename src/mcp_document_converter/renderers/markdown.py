"""
Markdown 渲染器 - 将中间表示渲染为 Markdown
"""

from typing import Any, List

from ..core.ir import DocumentIR, Node, NodeType
from ..core.renderer import BaseRenderer, RenderError


class MarkdownRenderer(BaseRenderer):
    """
    Markdown 文档渲染器

    将中间表示渲染为 Markdown 格式。
    """

    @property
    def output_extension(self) -> str:
        return ".md"

    @property
    def format_name(self) -> str:
        return "markdown"

    @property
    def mime_type(self) -> str:
        return "text/markdown"

    def render(self, document: DocumentIR, **options: Any) -> str:
        """
        将中间表示渲染为 Markdown

        Args:
            document: 文档的中间表示
            **options: 渲染选项
                - include_front_matter: 是否包含 YAML Front Matter

        Returns:
            Markdown 字符串
        """
        try:
            parts = []

            # 添加 YAML Front Matter
            include_front_matter = options.get("include_front_matter", True)
            if include_front_matter and (document.title or document.author or document.metadata):
                front_matter = self._generate_front_matter(document)
                if front_matter:
                    parts.append(front_matter)
                    parts.append("")

            # 渲染内容
            content = self._render_nodes(document.content)
            parts.append(content)

            return "\n\n".join(parts)

        except Exception as e:
            raise RenderError(f"Markdown 渲染失败: {str(e)}")

    def _generate_front_matter(self, document: DocumentIR) -> str:
        """生成 YAML Front Matter"""
        lines = ["---"]

        if document.title:
            lines.append(f"title: {document.title}")
        if document.author:
            lines.append(f"author: {document.author}")

        # 添加其他元数据
        for key, value in document.metadata.items():
            if value and key not in ["title", "author"]:
                if isinstance(value, str):
                    lines.append(f"{key}: {value}")
                else:
                    lines.append(f"{key}: {value}")

        lines.append("---")
        return "\n".join(lines)

    def _render_nodes(self, nodes: List[Node]) -> str:
        """渲染节点列表"""
        parts = []

        for node in nodes:
            rendered = self._render_node(node)
            if rendered:
                parts.append(rendered)

        return "\n\n".join(parts)

    def _render_node(self, node: Node) -> str:
        """渲染单个节点"""
        if node.type == NodeType.HEADING:
            level = node.attributes.get("level", 1)
            content = self._render_inline_content(node)
            return f"{'#' * level} {content}"

        elif node.type == NodeType.PARAGRAPH:
            content = self._render_inline_content(node)
            return content

        elif node.type == NodeType.CODE_BLOCK:
            language = node.attributes.get("language", "")
            code = node.content if isinstance(node.content, str) else ""
            return f"```{language}\n{code}\n```"

        elif node.type == NodeType.LIST:
            return self._render_list(node)

        elif node.type == NodeType.TABLE:
            return self._render_table(node)

        elif node.type == NodeType.BLOCKQUOTE:
            content = self._render_nodes(node.content) if isinstance(node.content, list) else ""
            lines = content.split("\n")
            quoted_lines = [f"> {line}" for line in lines if line]
            return "\n".join(quoted_lines)

        elif node.type == NodeType.HORIZONTAL_RULE:
            return "---"

        elif node.type == NodeType.DOCUMENT:
            return self._render_nodes(node.content) if isinstance(node.content, list) else ""

        return ""

    def _render_list(self, node: Node, indent: str = "") -> str:
        """渲染列表"""
        list_type = node.attributes.get("type", "unordered")
        items = node.content if isinstance(node.content, list) else []

        lines = []
        for i, item in enumerate(items):
            if not isinstance(item, Node):
                continue

            content = self._render_inline_content(item)

            if list_type == "ordered":
                prefix = f"{i + 1}."
            else:
                prefix = "-"

            lines.append(f"{indent}{prefix} {content}")

        return "\n".join(lines)

    def _render_table(self, node: Node) -> str:
        """渲染表格"""
        rows = node.content if isinstance(node.content, list) else []

        if not rows:
            return ""

        lines = []
        header_done = False

        for row in rows:
            if not isinstance(row, Node) or row.type != NodeType.TABLE_ROW:
                continue

            cells = row.content if isinstance(row.content, list) else []
            cell_contents = []

            for cell in cells:
                if not isinstance(cell, Node) or cell.type != NodeType.TABLE_CELL:
                    continue
                content = self._render_inline_content(cell)
                cell_contents.append(content)

            if cell_contents:
                lines.append("| " + " | ".join(cell_contents) + " |")

                # 添加分隔行（表头后）
                if not header_done:
                    separator = "|" + "|".join([" --- " for _ in cell_contents]) + "|"
                    lines.append(separator)
                    header_done = True

        return "\n".join(lines)

    def _render_inline_content(self, node: Node) -> str:
        """渲染行内内容"""
        if isinstance(node.content, str):
            return node.content

        if not isinstance(node.content, list):
            return ""

        parts = []
        for child in node.content:
            if isinstance(child, Node):
                if child.type == NodeType.TEXT:
                    parts.append(str(child.content))
                elif child.type == NodeType.STRONG:
                    content = self._render_inline_content(child)
                    parts.append(f"**{content}**")
                elif child.type == NodeType.EMPHASIS:
                    content = self._render_inline_content(child)
                    parts.append(f"*{content}*")
                elif child.type == NodeType.CODE_INLINE:
                    code = child.content if isinstance(child.content, str) else ""
                    parts.append(f"`{code}`")
                elif child.type == NodeType.LINK:
                    url = child.attributes.get("url", "")
                    content = self._render_inline_content(child)
                    parts.append(f"[{content}]({url})")
                elif child.type == NodeType.IMAGE:
                    src = child.attributes.get("src", "")
                    alt = child.attributes.get("alt", "")
                    title = child.attributes.get("title", "")
                    if title:
                        parts.append(f'![{alt}]({src} "{title}")')
                    else:
                        parts.append(f"![{alt}]({src})")
                elif child.type == NodeType.STRIKETHROUGH:
                    content = self._render_inline_content(child)
                    parts.append(f"~~{content}~~")
                elif child.type == NodeType.LINE_BREAK:
                    parts.append("\n")
                else:
                    parts.append(self._render_inline_content(child))
            else:
                parts.append(str(child))

        return "".join(parts)
