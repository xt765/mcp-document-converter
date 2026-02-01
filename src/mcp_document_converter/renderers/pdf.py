"""
PDF 渲染器 - 将中间表示渲染为 PDF
"""

from pathlib import Path
from typing import Any, List, Union, Optional

from ..core.ir import DocumentIR, Node, NodeType
from ..core.renderer import BaseRenderer, RenderError

# 尝试导入 WeasyPrint，如果失败则标记为不可用
try:
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False


class PDFRenderer(BaseRenderer):
    """
    PDF 文档渲染器
    
    将中间表示渲染为 PDF 格式。
    使用 WeasyPrint 将 HTML 转换为 PDF。
    """
    
    @property
    def output_extension(self) -> str:
        return ".pdf"
    
    @property
    def format_name(self) -> str:
        return "pdf"
    
    @property
    def mime_type(self) -> str:
        return "application/pdf"
    
    @property
    def is_binary(self) -> bool:
        return True
    
    def render(self, document: DocumentIR, **options: Any) -> bytes:
        """
        将中间表示渲染为 PDF
        
        Args:
            document: 文档的中间表示
            **options: 渲染选项
                - css: 自定义 CSS
                - page_size: 页面大小（默认 A4）
                - margin: 页边距
        
        Returns:
            PDF 二进制数据
        """
        if not WEASYPRINT_AVAILABLE:
            # 如果 WeasyPrint 不可用，返回一个包含错误信息的简单 PDF
            # 使用 reportlab 作为备选方案
            try:
                return self._render_with_reportlab(document, **options)
            except ImportError:
                raise RenderError(
                    "PDF 渲染需要 WeasyPrint 或 ReportLab 库。\n"
                    "在 Windows 上安装 WeasyPrint 需要先安装 GTK 库。\n"
                    "请访问: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows"
                )
        
        try:
            # 首先渲染为 HTML
            from .html import HTMLRenderer
            html_renderer = HTMLRenderer()
            html_content = html_renderer.render(document, **options)
            
            # 添加 PDF 专用 CSS
            pdf_css = self._get_pdf_css(options)
            
            # 合并 CSS
            custom_css = options.get('css', '')
            full_css = pdf_css + custom_css
            
            # 使用 WeasyPrint 转换为 PDF
            font_config = FontConfiguration()
            html_doc = HTML(string=html_content)
            css_doc = CSS(string=full_css, font_config=font_config)
            
            pdf_bytes = html_doc.write_pdf(stylesheets=[css_doc], font_config=font_config)
            
            return pdf_bytes
            
        except Exception as e:
            raise RenderError(f"PDF 渲染失败: {str(e)}")
    
    def _render_with_reportlab(self, document: DocumentIR, **options: Any) -> bytes:
        """
        使用 ReportLab 作为备选方案渲染 PDF
        
        当 WeasyPrint 不可用时使用。功能较简单，但无需 GTK 依赖。
        """
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            from io import BytesIO
            
            # 创建 PDF 缓冲区
            buffer = BytesIO()
            
            # 创建文档
            page_size = options.get('page_size', 'A4')
            margin = options.get('margin', 2)
            
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=margin * inch,
                leftMargin=margin * inch,
                topMargin=margin * inch,
                bottomMargin=margin * inch
            )
            
            # 获取样式
            styles = getSampleStyleSheet()
            story = []
            
            # 添加标题
            if document.title:
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=24,
                    spaceAfter=30,
                )
                story.append(Paragraph(document.title, title_style))
                story.append(Spacer(1, 0.2 * inch))
            
            # 添加作者信息
            if document.author:
                author_style = ParagraphStyle(
                    'AuthorStyle',
                    parent=styles['Normal'],
                    fontSize=10,
                    textColor='gray',
                    spaceAfter=20,
                )
                story.append(Paragraph(f"Author: {document.author}", author_style))
                story.append(Spacer(1, 0.2 * inch))
            
            # 确保 inch 已导入
            from reportlab.lib.units import inch
            
            # 渲染内容
            for node in document.content:
                self._render_node_to_reportlab(node, story, styles)
            
            # 构建 PDF
            doc.build(story)
            
            # 获取 PDF 数据
            pdf_data = buffer.getvalue()
            buffer.close()
            
            return pdf_data
            
        except Exception as e:
            raise RenderError(f"ReportLab PDF 渲染失败: {str(e)}")
    
    def _render_node_to_reportlab(self, node, story, styles):
        """将节点渲染为 ReportLab 元素"""
        from reportlab.platypus import Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
        from reportlab.lib.units import inch
        
        if node.type.name == 'HEADING':
            level = node.attributes.get('level', 1)
            text = self._extract_text(node)
            
            style_name = f'Heading{min(level, 3)}'
            if style_name in styles:
                style = styles[style_name]
            else:
                style = styles['Heading1']
            
            story.append(Paragraph(text, style))
            story.append(Spacer(1, 0.1 * inch))
            
        elif node.type.name == 'PARAGRAPH':
            text = self._extract_text(node)
            if text.strip():
                story.append(Paragraph(text, styles['Normal']))
                story.append(Spacer(1, 0.1 * inch))
                
        elif node.type.name == 'CODE_BLOCK':
            code = node.content if isinstance(node.content, str) else ''
            # 使用等宽字体样式
            code_style = ParagraphStyle(
                'CodeStyle',
                parent=styles['Code'],
                fontName='Courier',
                fontSize=9,
                leftIndent=20,
            )
            # 转义 HTML 特殊字符
            code_escaped = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            for line in code_escaped.split('\n'):
                story.append(Paragraph(line, code_style))
            story.append(Spacer(1, 0.1 * inch))
            
        elif node.type.name == 'HORIZONTAL_RULE':
            story.append(Spacer(1, 0.2 * inch))
            
        elif node.type.name == 'PAGE_BREAK':
            story.append(PageBreak())
    
    def _extract_text(self, node) -> str:
        """从节点中提取纯文本"""
        if isinstance(node.content, str):
            return node.content
        
        if not isinstance(node.content, list):
            return ""
        
        parts = []
        for child in node.content:
            if hasattr(child, 'type'):
                parts.append(self._extract_text(child))
            else:
                parts.append(str(child))
        
        return ''.join(parts)
    
    def _get_pdf_css(self, options: dict) -> str:
        """获取 PDF 专用 CSS"""
        page_size = options.get('page_size', 'A4')
        margin = options.get('margin', '2cm')
        
        return f'''
        @page {{
            size: {page_size};
            margin: {margin};
            
            @top-center {{
                content: string(doctitle);
                font-size: 9pt;
                color: #666;
            }}
            
            @bottom-center {{
                content: counter(page);
                font-size: 9pt;
            }}
        }}
        
        h1 {{
            string-set: doctitle content();
        }}
        
        /* PDF 优化 */
        body {{
            background: white !important;
            padding: 0 !important;
        }}
        
        .container {{
            box-shadow: none !important;
            max-width: 100% !important;
            padding: 0 !important;
        }}
        
        /* 分页控制 */
        h1, h2, h3 {{
            page-break-after: avoid;
        }}
        
        pre, table, figure, img {{
            page-break-inside: avoid;
        }}
        
        /* 打印链接 */
        a {{
            color: #3498db;
            text-decoration: none;
        }}
        
        a[href]::after {{
            content: " (" attr(href) ")";
            font-size: 0.8em;
            color: #666;
        }}
        '''
