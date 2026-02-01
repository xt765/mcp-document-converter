"""
HTML 渲染器 - 将中间表示渲染为 HTML
"""

from html import escape
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer

from ..core.ir import DocumentIR, Node, NodeType
from ..core.renderer import BaseRenderer, RenderError


class HTMLRenderer(BaseRenderer):
    """
    HTML 文档渲染器
    
    将中间表示渲染为 HTML 文档。
    支持代码高亮和自定义 CSS。
    """
    
    @property
    def output_extension(self) -> str:
        return ".html"
    
    @property
    def format_name(self) -> str:
        return "html"
    
    @property
    def mime_type(self) -> str:
        return "text/html"
    
    def render(self, document: DocumentIR, **options: Any) -> str:
        """
        将中间表示渲染为 HTML
        
        Args:
            document: 文档的中间表示
            **options: 渲染选项
                - template: 模板名称
                - css: 自定义 CSS
                - title: 文档标题
                - include_toc: 是否包含目录
        
        Returns:
            HTML 字符串
        """
        try:
            # 渲染内容
            body_content = self._render_nodes(document.content)
            
            # 获取标题
            title = options.get('title', document.title) or "Document"
            
            # 获取 CSS
            css = options.get('css', self._get_default_css())
            
            # 构建完整 HTML
            html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape(str(title))}</title>
    <style>
{css}
    </style>
</head>
<body>
    <div class="container">
{body_content}
    </div>
</body>
</html>'''
            
            return html
            
        except Exception as e:
            raise RenderError(f"HTML 渲染失败: {str(e)}")
    
    def _render_nodes(self, nodes: List[Node], level: int = 0) -> str:
        """渲染节点列表"""
        parts = []
        indent = "    " * (level + 2)
        
        for node in nodes:
            rendered = self._render_node(node, level + 2)
            if rendered:
                parts.append(indent + rendered)
        
        return '\n'.join(parts)
    
    def _render_node(self, node: Node, level: int = 0) -> str:
        """渲染单个节点"""
        if node.type == NodeType.HEADING:
            level_attr = node.attributes.get('level', 1)
            content = self._render_inline_content(node)
            return f"<h{level_attr}>{content}</h{level_attr}>"
        
        elif node.type == NodeType.PARAGRAPH:
            content = self._render_inline_content(node)
            if content:
                return f"<p>{content}</p>"
            return ""
        
        elif node.type == NodeType.CODE_BLOCK:
            language = node.attributes.get('language', '')
            code = node.content if isinstance(node.content, str) else ''
            
            if language:
                try:
                    lexer = get_lexer_by_name(language)
                    highlighted = highlight(code, lexer, HtmlFormatter())
                    return f'<div class="code-block">{highlighted}</div>'
                except:
                    pass
            
            escaped_code = escape(code)
            return f"<pre><code>{escaped_code}</code></pre>"
        
        elif node.type == NodeType.LIST:
            list_type = node.attributes.get('type', 'unordered')
            items = node.content if isinstance(node.content, list) else []
            
            item_html = []
            for item in items:
                if isinstance(item, Node):
                    content = self._render_inline_content(item)
                    item_html.append(f"<li>{content}</li>")
            
            tag = "ol" if list_type == 'ordered' else "ul"
            items_str = '\n'.join(['        ' + item for item in item_html])
            return f"<{tag}>\n{items_str}\n    </{tag}>"
        
        elif node.type == NodeType.TABLE:
            return self._render_table(node)
        
        elif node.type == NodeType.BLOCKQUOTE:
            content = self._render_nodes(node.content, level) if isinstance(node.content, list) else ''
            return f"<blockquote>\n{content}\n    </blockquote>"
        
        elif node.type == NodeType.HORIZONTAL_RULE:
            return "<hr>"
        
        elif node.type == NodeType.DOCUMENT:
            content = self._render_nodes(node.content, level) if isinstance(node.content, list) else ''
            return content
        
        return ""
    
    def _render_inline_content(self, node: Node) -> str:
        """渲染行内内容"""
        if isinstance(node.content, str):
            return escape(node.content)
        
        if not isinstance(node.content, list):
            return ""
        
        parts = []
        for child in node.content:
            if isinstance(child, Node):
                if child.type == NodeType.TEXT:
                    parts.append(escape(str(child.content)))
                elif child.type == NodeType.STRONG:
                    content = self._render_inline_content(child)
                    parts.append(f"<strong>{content}</strong>")
                elif child.type == NodeType.EMPHASIS:
                    content = self._render_inline_content(child)
                    parts.append(f"<em>{content}</em>")
                elif child.type == NodeType.CODE_INLINE:
                    code = child.content if isinstance(child.content, str) else ''
                    parts.append(f"<code>{escape(code)}</code>")
                elif child.type == NodeType.LINK:
                    url = child.attributes.get('url', '#')
                    content = self._render_inline_content(child)
                    parts.append(f'<a href="{escape(url)}">{content}</a>')
                elif child.type == NodeType.IMAGE:
                    src = child.attributes.get('src', '')
                    alt = child.attributes.get('alt', '')
                    title = child.attributes.get('title', '')
                    title_attr = f' title="{escape(title)}"' if title else ''
                    parts.append(f'<img src="{escape(src)}" alt="{escape(alt)}"{title_attr}>')
                elif child.type == NodeType.STRIKETHROUGH:
                    content = self._render_inline_content(child)
                    parts.append(f"<del>{content}</del>")
                elif child.type == NodeType.LINE_BREAK:
                    parts.append("<br>")
                else:
                    parts.append(self._render_inline_content(child))
            else:
                parts.append(escape(str(child)))
        
        return ''.join(parts)
    
    def _render_table(self, node: Node) -> str:
        """渲染表格"""
        rows = node.content if isinstance(node.content, list) else []
        
        if not rows:
            return ""
        
        html_parts = ["<table>"]
        
        for row in rows:
            if not isinstance(row, Node) or row.type != NodeType.TABLE_ROW:
                continue
            
            html_parts.append("    <tr>")
            cells = row.content if isinstance(row.content, list) else []
            
            for cell in cells:
                if not isinstance(cell, Node) or cell.type != NodeType.TABLE_CELL:
                    continue
                
                is_header = cell.attributes.get('header', False)
                tag = 'th' if is_header else 'td'
                content = self._render_inline_content(cell)
                html_parts.append(f"        <{tag}>{content}</{tag}>")
            
            html_parts.append("    </tr>")
        
        html_parts.append("</table>")
        return '\n'.join(html_parts)
    
    def _get_default_css(self) -> str:
        """获取默认 CSS 样式（包含 Pygments 代码高亮样式）"""
        # Pygments 默认样式（monokai 主题）
        pygments_css = '''/* Pygments 代码高亮样式 (Monokai 主题) */
.highlight .hll { background-color: #49483e }
.highlight  { background: #272822; color: #f8f8f2 }
.highlight .c { color: #75715e } /* Comment */
.highlight .err { color: #960050; background-color: #1e0010 } /* Error */
.highlight .k { color: #66d9ef } /* Keyword */
.highlight .l { color: #ae81ff } /* Literal */
.highlight .n { color: #f8f8f2 } /* Name */
.highlight .o { color: #f92672 } /* Operator */
.highlight .p { color: #f8f8f2 } /* Punctuation */
.highlight .ch { color: #75715e } /* Comment.Hashbang */
.highlight .cm { color: #75715e } /* Comment.Multiline */
.highlight .cp { color: #75715e } /* Comment.Preproc */
.highlight .cpf { color: #75715e } /* Comment.PreprocFile */
.highlight .c1 { color: #75715e } /* Comment.Single */
.highlight .cs { color: #75715e } /* Comment.Special */
.highlight .gd { color: #f92672 } /* Generic.Deleted */
.highlight .ge { font-style: italic } /* Generic.Emph */
.highlight .gi { color: #a6e22e } /* Generic.Inserted */
.highlight .gs { font-weight: bold } /* Generic.Strong */
.highlight .gu { color: #75715e } /* Generic.Subheading */
.highlight .kc { color: #66d9ef } /* Keyword.Constant */
.highlight .kd { color: #66d9ef } /* Keyword.Declaration */
.highlight .kn { color: #f92672 } /* Keyword.Namespace */
.highlight .kp { color: #66d9ef } /* Keyword.Pseudo */
.highlight .kr { color: #66d9ef } /* Keyword.Reserved */
.highlight .kt { color: #66d9ef } /* Keyword.Type */
.highlight .ld { color: #e6db74 } /* Literal.Date */
.highlight .m { color: #ae81ff } /* Literal.Number */
.highlight .s { color: #e6db74 } /* Literal.String */
.highlight .na { color: #a6e22e } /* Name.Attribute */
.highlight .nb { color: #f8f8f2 } /* Name.Builtin */
.highlight .nc { color: #a6e22e } /* Name.Class */
.highlight .no { color: #66d9ef } /* Name.Constant */
.highlight .nd { color: #a6e22e } /* Name.Decorator */
.highlight .ni { color: #f8f8f2 } /* Name.Entity */
.highlight .ne { color: #a6e22e } /* Name.Exception */
.highlight .nf { color: #a6e22e } /* Name.Function */
.highlight .nl { color: #f8f8f2 } /* Name.Label */
.highlight .nn { color: #f8f8f2 } /* Name.Namespace */
.highlight .nx { color: #a6e22e } /* Name.Other */
.highlight .py { color: #f8f8f2 } /* Name.Property */
.highlight .nt { color: #f92672 } /* Name.Tag */
.highlight .nv { color: #f8f8f2 } /* Name.Variable */
.highlight .ow { color: #f92672 } /* Operator.Word */
.highlight .w { color: #f8f8f2 } /* Text.Whitespace */
.highlight .mb { color: #ae81ff } /* Literal.Number.Bin */
.highlight .mf { color: #ae81ff } /* Literal.Number.Float */
.highlight .mh { color: #ae81ff } /* Literal.Number.Hex */
.highlight .mi { color: #ae81ff } /* Literal.Number.Integer */
.highlight .mo { color: #ae81ff } /* Literal.Number.Oct */
.highlight .sa { color: #e6db74 } /* Literal.String.Affix */
.highlight .sb { color: #e6db74 } /* Literal.String.Backtick */
.highlight .sc { color: #e6db74 } /* Literal.String.Char */
.highlight .dl { color: #e6db74 } /* Literal.String.Delimiter */
.highlight .sd { color: #e6db74 } /* Literal.String.Doc */
.highlight .s2 { color: #e6db74 } /* Literal.String.Double */
.highlight .se { color: #ae81ff } /* Literal.String.Escape */
.highlight .sh { color: #e6db74 } /* Literal.String.Heredoc */
.highlight .si { color: #e6db74 } /* Literal.String.Interpol */
.highlight .sx { color: #e6db74 } /* Literal.String.Other */
.highlight .sr { color: #e6db74 } /* Literal.String.Regex */
.highlight .s1 { color: #e6db74 } /* Literal.String.Single */
.highlight .ss { color: #e6db74 } /* Literal.String.Symbol */
.highlight .bp { color: #f8f8f2 } /* Name.Builtin.Pseudo */
.highlight .fm { color: #a6e22e } /* Name.Function.Magic */
.highlight .vc { color: #f8f8f2 } /* Name.Variable.Class */
.highlight .vg { color: #f8f8f2 } /* Name.Variable.Global */
.highlight .vi { color: #f8f8f2 } /* Name.Variable.Instance */
.highlight .vm { color: #f8f8f2 } /* Name.Variable.Magic */
.highlight .il { color: #ae81ff } /* Literal.Number.Integer.Long */

/* 基础样式 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    line-height: 1.8;
    color: #333;
    background-color: #f5f5f5;
    padding: 20px;
}

.container {
    max-width: 900px;
    margin: 0 auto;
    background: white;
    padding: 40px;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

/* 标题样式 */
h1 {
    font-size: 2.2em;
    color: #2c3e50;
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 3px solid #3498db;
}

h2 {
    font-size: 1.8em;
    color: #34495e;
    margin-top: 30px;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 2px solid #ecf0f1;
}

h3 {
    font-size: 1.4em;
    color: #34495e;
    margin-top: 25px;
    margin-bottom: 12px;
}

h4 {
    font-size: 1.2em;
    color: #555;
    margin-top: 20px;
    margin-bottom: 10px;
}

/* 段落和文本 */
p {
    margin-bottom: 15px;
    text-align: justify;
}

strong {
    color: #2c3e50;
    font-weight: 600;
}

em {
    color: #666;
}

/* 链接 */
a {
    color: #3498db;
    text-decoration: none;
    transition: color 0.3s;
}

a:hover {
    color: #2980b9;
    text-decoration: underline;
}

/* 代码块 */
pre {
    background: #2d2d2d;
    color: #f8f8f2;
    padding: 20px;
    border-radius: 6px;
    overflow-x: auto;
    margin: 20px 0;
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 14px;
    line-height: 1.5;
}

code {
    background: #f4f4f4;
    color: #c7254e;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 0.9em;
}

pre code {
    background: transparent;
    color: #f8f8f2;
    padding: 0;
}

/* 行内代码 */
p code, li code {
    background: #f8f8f8;
    border: 1px solid #e0e0e0;
}

/* 表格 */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    background: white;
}

th, td {
    padding: 12px 15px;
    text-align: left;
    border: 1px solid #ddd;
}

th {
    background: #3498db;
    color: white;
    font-weight: 600;
}

tr:nth-child(even) {
    background: #f8f9fa;
}

tr:hover {
    background: #e8f4f8;
}

/* 列表 */
ul, ol {
    margin: 15px 0;
    padding-left: 30px;
}

li {
    margin-bottom: 8px;
}

/* 引用块 */
blockquote {
    border-left: 4px solid #3498db;
    padding: 15px 20px;
    margin: 20px 0;
    background: #f8f9fa;
    font-style: italic;
    color: #555;
}

/* 分隔线 */
hr {
    border: none;
    height: 2px;
    background: linear-gradient(to right, #3498db, #2ecc71);
    margin: 30px 0;
}

/* 图片 */
img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 20px auto;
    border-radius: 6px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* 代码高亮 */
.code-block .highlight {
    background: transparent;
}

.code-block .highlight pre {
    margin: 0;
}

/* 打印样式 */
@media print {
    body {
        background: white;
        padding: 0;
    }
    
    .container {
        box-shadow: none;
        max-width: 100%;
    }
}

/* 响应式 */
@media (max-width: 768px) {
    body {
        padding: 10px;
    }
    
    .container {
        padding: 20px;
    }
    
    h1 {
        font-size: 1.8em;
    }
    
    h2 {
        font-size: 1.5em;
    }
    
    pre {
        padding: 15px;
        font-size: 13px;
    }
}'''
