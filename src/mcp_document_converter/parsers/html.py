"""
HTML 解析器 - 将 HTML 解析为中间表示
"""

from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional, Union

from bs4 import BeautifulSoup, Tag

from ..core.ir import DocumentIR, Node, NodeType
from ..core.parser import BaseParser, ParseError


class HTMLParser(BaseParser):
    """
    HTML 文档解析器
    
    将 HTML 文档解析为中间表示。
    """
    
    @property
    def supported_extensions(self) -> List[str]:
        return [".html", ".htm"]
    
    @property
    def format_name(self) -> str:
        return "html"
    
    @property
    def mime_types(self) -> List[str]:
        return ["text/html", "application/xhtml+xml"]
    
    def parse(self, source: Union[str, Path, bytes], **options: Any) -> DocumentIR:
        """
        解析 HTML 文档
        
        Args:
            source: HTML 文件路径或内容
            **options: 解析选项
        
        Returns:
            DocumentIR: 文档的中间表示
        """
        try:
            # 读取内容
            content = self._read_source(source)
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            
            # 解析 HTML
            soup = BeautifulSoup(content, 'html.parser')
            
            document = DocumentIR()
            
            # 提取标题
            title_tag = soup.find('title')
            if title_tag:
                document.title = title_tag.get_text(strip=True)
            
            # 提取元数据
            meta_tags = soup.find_all('meta')
            for meta in meta_tags:
                name = meta.get('name', '').lower()
                content_val = meta.get('content', '')
                if name and content_val:
                    document.metadata[name] = content_val
            
            # 提取作者
            if 'author' in document.metadata:
                document.author = document.metadata['author']
            
            # 查找主要内容区域
            body = soup.find('body')
            if body:
                # 尝试找到主要内容
                main_content = (
                    body.find('main') or
                    body.find('article') or
                    body.find('div', class_='content') or
                    body.find('div', class_='container') or
                    body
                )
                
                # 解析内容
                for element in main_content.find_all(recursive=False):
                    node = self._parse_element(element)
                    if node:
                        document.add_node(node)
            
            return document
            
        except Exception as e:
            raise ParseError(f"HTML 解析失败: {str(e)}")
    
    def _parse_element(self, element: Tag) -> Optional[Node]:
        """解析 HTML 元素为 IR 节点"""
        tag_name = element.name
        
        if not tag_name:
            return None
        
        if tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(tag_name[1])
            return Node(
                type=NodeType.HEADING,
                content=self._parse_inline_content(element),
                attributes={"level": level}
            )
        
        elif tag_name == 'p':
            return Node(
                type=NodeType.PARAGRAPH,
                content=self._parse_inline_content(element)
            )
        
        elif tag_name == 'pre':
            code = element.find('code')
            if code:
                return Node(
                    type=NodeType.CODE_BLOCK,
                    content=code.get_text()
                )
            else:
                return Node(
                    type=NodeType.CODE_BLOCK,
                    content=element.get_text()
                )
        
        elif tag_name in ['ul', 'ol']:
            list_type = 'unordered' if tag_name == 'ul' else 'ordered'
            items = []
            for li in element.find_all('li', recursive=False):
                items.append(Node(
                    type=NodeType.LIST_ITEM,
                    content=self._parse_inline_content(li)
                ))
            
            return Node(
                type=NodeType.LIST,
                content=items,
                attributes={"type": list_type}
            )
        
        elif tag_name == 'table':
            return self._parse_table(element)
        
        elif tag_name == 'blockquote':
            content = []
            for child in element.find_all(recursive=False):
                node = self._parse_element(child)
                if node:
                    content.append(node)
            
            return Node(
                type=NodeType.BLOCKQUOTE,
                content=content
            )
        
        elif tag_name == 'hr':
            return Node(
                type=NodeType.HORIZONTAL_RULE,
                content=""
            )
        
        elif tag_name in ['div', 'section', 'article', 'main']:
            # 递归解析容器
            content = []
            for child in element.find_all(recursive=False):
                node = self._parse_element(child)
                if node:
                    content.append(node)
            return Node(type=NodeType.DOCUMENT, content=content) if content else None
        
        return None
    
    def _parse_inline_content(self, element: Tag) -> List[Node]:
        """解析行内内容"""
        nodes = []
        
        for content in element.contents:
            if isinstance(content, str):
                text = content.strip()
                if text:
                    nodes.append(Node(type=NodeType.TEXT, content=text))
            elif content.name == 'br':
                nodes.append(Node(type=NodeType.LINE_BREAK, content=""))
            elif content.name in ['strong', 'b']:
                nodes.append(Node(
                    type=NodeType.STRONG,
                    content=self._parse_inline_content(content)
                ))
            elif content.name in ['em', 'i']:
                nodes.append(Node(
                    type=NodeType.EMPHASIS,
                    content=self._parse_inline_content(content)
                ))
            elif content.name == 'code':
                nodes.append(Node(
                    type=NodeType.CODE_INLINE,
                    content=content.get_text()
                ))
            elif content.name == 'a':
                nodes.append(Node(
                    type=NodeType.LINK,
                    content=self._parse_inline_content(content),
                    attributes={"url": content.get('href', '')}
                ))
            elif content.name == 'img':
                nodes.append(Node(
                    type=NodeType.IMAGE,
                    content="",
                    attributes={
                        "src": content.get('src', ''),
                        "alt": content.get('alt', ''),
                        "title": content.get('title', '')
                    }
                ))
            elif content.name:
                nodes.extend(self._parse_inline_content(content))
        
        return nodes
    
    def _parse_table(self, element: Tag) -> Node:
        """解析表格"""
        rows = []
        
        thead = element.find('thead')
        if thead:
            for tr in thead.find_all('tr'):
                cells = []
                for th in tr.find_all(['th', 'td']):
                    cells.append(Node(
                        type=NodeType.TABLE_CELL,
                        content=self._parse_inline_content(th),
                        attributes={"header": True}
                    ))
                if cells:
                    rows.append(Node(type=NodeType.TABLE_ROW, content=cells))
        
        tbody = element.find('tbody')
        if tbody:
            for tr in tbody.find_all('tr'):
                cells = []
                for td in tr.find_all('td'):
                    cells.append(Node(
                        type=NodeType.TABLE_CELL,
                        content=self._parse_inline_content(td)
                    ))
                if cells:
                    rows.append(Node(type=NodeType.TABLE_ROW, content=cells))
        
        if not thead and not tbody:
            is_first_row = True
            for tr in element.find_all('tr'):
                cells = []
                for cell in tr.find_all(['th', 'td']):
                    cells.append(Node(
                        type=NodeType.TABLE_CELL,
                        content=self._parse_inline_content(cell),
                        attributes={"header": is_first_row} if is_first_row else {}
                    ))
                if cells:
                    rows.append(Node(type=NodeType.TABLE_ROW, content=cells))
                is_first_row = False
        
        return Node(type=NodeType.TABLE, content=rows)
