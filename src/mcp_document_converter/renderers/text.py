"""
Text 渲染器 - 将中间表示渲染为纯文本
"""

from pathlib import Path
from typing import Any, List, Union

from ..core.ir import DocumentIR, Node, NodeType
from ..core.renderer import BaseRenderer, RenderError


class TextRenderer(BaseRenderer):
    """
    纯文本渲染器
    
    将中间表示渲染为纯文本格式。
    """
    
    @property
    def output_extension(self) -> str:
        return ".txt"
    
    @property
    def format_name(self) -> str:
        return "text"
    
    @property
    def mime_type(self) -> str:
        return "text/plain"
    
    def render(self, document: DocumentIR, **options: Any) -> str:
        """
        将中间表示渲染为纯文本
        
        Args:
            document: 文档的中间表示
            **options: 渲染选项
                - preserve_formatting: 是否保留基本格式（标题下划线等）
                - max_line_length: 最大行长度
        
        Returns:
            纯文本字符串
        """
        try:
            preserve_formatting = options.get('preserve_formatting', True)
            max_line_length = options.get('max_line_length', 80)
            
            parts = []
            
            # 添加标题
            if document.title:
                parts.append(document.title)
                if preserve_formatting:
                    parts.append("=" * len(document.title))
                parts.append("")
            
            # 添加作者信息
            if document.author:
                parts.append(f"作者: {document.author}")
                parts.append("")
            
            # 渲染内容
            content = self._render_nodes(document.content, preserve_formatting, max_line_length)
            parts.append(content)
            
            return '\n'.join(parts)
            
        except Exception as e:
            raise RenderError(f"文本渲染失败: {str(e)}")
    
    def _render_nodes(self, nodes: List[Node], preserve_formatting: bool, max_line_length: int) -> str:
        """渲染节点列表"""
        parts = []
        
        for node in nodes:
            rendered = self._render_node(node, preserve_formatting, max_line_length)
            if rendered:
                parts.append(rendered)
        
        return '\n\n'.join(parts)
    
    def _render_node(self, node: Node, preserve_formatting: bool, max_line_length: int) -> str:
        """渲染单个节点"""
        if node.type == NodeType.HEADING:
            level = node.attributes.get('level', 1)
            content = self._render_inline_content(node)
            
            if preserve_formatting:
                if level == 1:
                    return f"{content}\n{'=' * len(content)}"
                elif level == 2:
                    return f"{content}\n{'-' * len(content)}"
                else:
                    return f"{'#' * level} {content}"
            else:
                return content
        
        elif node.type == NodeType.PARAGRAPH:
            content = self._render_inline_content(node)
            return self._wrap_text(content, max_line_length)
        
        elif node.type == NodeType.CODE_BLOCK:
            code = node.content if isinstance(node.content, str) else ''
            lines = code.split('\n')
            return '\n'.join(['    ' + line for line in lines])
        
        elif node.type == NodeType.LIST:
            return self._render_list(node, 0, preserve_formatting, max_line_length)
        
        elif node.type == NodeType.TABLE:
            return self._render_table(node, max_line_length)
        
        elif node.type == NodeType.BLOCKQUOTE:
            content = self._render_nodes(node.content, preserve_formatting, max_line_length) if isinstance(node.content, list) else ''
            lines = content.split('\n')
            return '\n'.join([f"> {line}" for line in lines])
        
        elif node.type == NodeType.HORIZONTAL_RULE:
            if preserve_formatting:
                return "-" * min(50, max_line_length)
            return ""
        
        elif node.type == NodeType.DOCUMENT:
            return self._render_nodes(node.content, preserve_formatting, max_line_length) if isinstance(node.content, list) else ''
        
        return ""
    
    def _render_list(self, node: Node, indent_level: int, preserve_formatting: bool, max_line_length: int) -> str:
        """渲染列表"""
        list_type = node.attributes.get('type', 'unordered')
        items = node.content if isinstance(node.content, list) else []
        
        lines = []
        indent = "    " * indent_level
        
        for i, item in enumerate(items):
            if not isinstance(item, Node):
                continue
            
            content = self._render_inline_content(item)
            
            if list_type == 'ordered':
                prefix = f"{i + 1}."
            else:
                prefix = "•"
            
            # 包装长行
            wrapped = self._wrap_text(f"{prefix} {content}", max_line_length - len(indent))
            wrapped_lines = wrapped.split('\n')
            
            if wrapped_lines:
                lines.append(indent + wrapped_lines[0])
                for line in wrapped_lines[1:]:
                    lines.append(indent + "    " + line)
        
        return '\n'.join(lines)
    
    def _render_table(self, node: Node, max_line_length: int) -> str:
        """渲染表格为文本"""
        rows = node.content if isinstance(node.content, list) else []
        
        if not rows:
            return ""
        
        # 收集所有单元格内容
        table_data = []
        for row in rows:
            if not isinstance(row, Node) or row.type != NodeType.TABLE_ROW:
                continue
            
            cells = row.content if isinstance(row.content, list) else []
            row_data = []
            
            for cell in cells:
                if not isinstance(cell, Node) or cell.type != NodeType.TABLE_CELL:
                    continue
                content = self._render_inline_content(cell)
                row_data.append(content)
            
            if row_data:
                table_data.append(row_data)
        
        if not table_data:
            return ""
        
        # 计算列宽
        num_cols = max(len(row) for row in table_data)
        col_widths = [0] * num_cols
        
        for row in table_data:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(cell))
        
        # 限制列宽
        max_col_width = max(20, (max_line_length - 3 * num_cols) // num_cols)
        col_widths = [min(w, max_col_width) for w in col_widths]
        
        # 渲染表格
        lines = []
        header_done = False
        
        for row in table_data:
            # 截断或填充单元格
            formatted_cells = []
            for i, cell in enumerate(row):
                width = col_widths[i] if i < len(col_widths) else max_col_width
                if len(cell) > width:
                    cell = cell[:width-3] + "..."
                formatted_cells.append(cell.ljust(width))
            
            # 补充空单元格
            while len(formatted_cells) < num_cols:
                formatted_cells.append("".ljust(col_widths[len(formatted_cells)]))
            
            lines.append(" | ".join(formatted_cells))
            
            # 添加分隔线（表头后）
            if not header_done:
                separator = "-+-".join(["-" * w for w in col_widths[:len(row)]])
                lines.append(separator)
                header_done = True
        
        return '\n'.join(lines)
    
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
                    parts.append(f"*{content}*")
                elif child.type == NodeType.EMPHASIS:
                    content = self._render_inline_content(child)
                    parts.append(f"/{content}/")
                elif child.type == NodeType.CODE_INLINE:
                    code = child.content if isinstance(child.content, str) else ''
                    parts.append(f"`{code}`")
                elif child.type == NodeType.LINK:
                    url = child.attributes.get('url', '')
                    content = self._render_inline_content(child)
                    parts.append(f"{content} ({url})")
                elif child.type == NodeType.IMAGE:
                    alt = child.attributes.get('alt', '')
                    parts.append(f"[图片: {alt}]")
                elif child.type == NodeType.STRIKETHROUGH:
                    content = self._render_inline_content(child)
                    parts.append(f"~{content}~")
                elif child.type == NodeType.LINE_BREAK:
                    parts.append(" ")
                else:
                    parts.append(self._render_inline_content(child))
            else:
                parts.append(str(child))
        
        return ''.join(parts)
    
    def _wrap_text(self, text: str, max_length: int) -> str:
        """包装文本到指定长度"""
        if len(text) <= max_length:
            return text
        
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line) + len(word) + 1 <= max_length:
                if current_line:
                    current_line += " "
                current_line += word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return '\n'.join(lines)
