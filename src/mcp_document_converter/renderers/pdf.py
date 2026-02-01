"""
PDF 渲染器 - 将中间表示渲染为 PDF
"""

from pathlib import Path
from typing import Any, List, Union

from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

from ..core.ir import DocumentIR, Node, NodeType
from ..core.renderer import BaseRenderer, RenderError


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
