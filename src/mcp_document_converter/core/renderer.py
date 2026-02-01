"""
渲染器基类 - 定义所有文档渲染器的接口
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .ir import DocumentIR


class BaseRenderer(ABC):
    """
    文档渲染器基类
    
    所有渲染器必须继承此类并实现 render 方法。
    渲染器的作用是将统一的中间表示 (DocumentIR)
    转换为特定格式的文档（HTML、PDF、DOCX 等）。
    
    Example:
        ```python
        class HTMLRenderer(BaseRenderer):
            @property
            def output_extension(self) -> str:
                return ".html"
            
            @property
            def format_name(self) -> str:
                return "html"
            
            def render(self, document: DocumentIR, **options) -> str:
                # 实现渲染逻辑
                return "<html>...</html>"
        ```
    """
    
    @property
    @abstractmethod
    def output_extension(self) -> str:
        """
        返回输出文件的扩展名
        
        Returns:
            扩展名，如 ".html", ".pdf"
        """
        pass
    
    @property
    @abstractmethod
    def format_name(self) -> str:
        """
        返回格式名称
        
        Returns:
            格式名称，如 "html", "pdf"
        """
        pass
    
    @property
    def mime_type(self) -> str:
        """
        返回输出的 MIME 类型（可选）
        
        Returns:
            MIME 类型
        """
        return "application/octet-stream"
    
    @property
    def is_binary(self) -> bool:
        """
        返回输出是否为二进制格式
        
        Returns:
            是否为二进制格式
        """
        return False
    
    @abstractmethod
    def render(self, document: DocumentIR, **options: Any) -> Union[str, bytes]:
        """
        将中间表示渲染为目标格式
        
        Args:
            document: 文档的中间表示
            **options: 渲染选项
                - template: 模板名称
                - css: 自定义 CSS
                - preserve_metadata: 是否保留元数据
        
        Returns:
            渲染后的内容（字符串或二进制）
        
        Raises:
            RenderError: 渲染失败时抛出
        """
        pass
    
    def render_to_file(
        self,
        document: DocumentIR,
        output_path: Union[str, Path],
        **options: Any
    ) -> Path:
        """
        将文档渲染并保存到文件
        
        Args:
            document: 文档的中间表示
            output_path: 输出文件路径
            **options: 渲染选项
        
        Returns:
            输出文件路径
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        content = self.render(document, **options)
        
        if self.is_binary:
            output_path.write_bytes(content if isinstance(content, bytes) else content.encode())
        else:
            output_path.write_text(
                content if isinstance(content, str) else content.decode(),
                encoding='utf-8'
            )
        
        return output_path
    
    def get_default_options(self) -> Dict[str, Any]:
        """
        获取默认渲染选项
        
        Returns:
            默认选项字典
        """
        return {
            "preserve_metadata": True,
            "extract_images": True,
        }


class RenderError(Exception):
    """渲染错误"""
    
    def __init__(self, message: str, format_name: Optional[str] = None):
        self.message = message
        self.format_name = format_name
        super().__init__(self.message)
