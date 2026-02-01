"""
解析器基类 - 定义所有文档解析器的接口
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .ir import DocumentIR


class BaseParser(ABC):
    """
    文档解析器基类
    
    所有解析器必须继承此类并实现 parse 方法。
    解析器的作用是将特定格式的文档（Markdown、DOCX、PDF 等）
    转换为统一的中间表示 (DocumentIR)。
    
    Example:
        ```python
        class MarkdownParser(BaseParser):
            @property
            def supported_extensions(self) -> List[str]:
                return [".md", ".markdown"]
            
            def parse(self, source: Union[str, Path], **options) -> DocumentIR:
                # 实现解析逻辑
                return DocumentIR(...)
        ```
    """
    
    @property
    @abstractmethod
    def supported_extensions(self) -> List[str]:
        """
        返回支持的文件扩展名列表
        
        Returns:
            扩展名列表，如 [".md", ".markdown"]
        """
        pass
    
    @property
    @abstractmethod
    def format_name(self) -> str:
        """
        返回格式名称
        
        Returns:
            格式名称，如 "markdown", "docx"
        """
        pass
    
    @property
    def mime_types(self) -> List[str]:
        """
        返回支持的 MIME 类型（可选）
        
        Returns:
            MIME 类型列表
        """
        return []
    
    @abstractmethod
    def parse(self, source: Union[str, Path, bytes], **options: Any) -> DocumentIR:
        """
        将源文档解析为中间表示
        
        Args:
            source: 源文档，可以是文件路径或二进制内容
            **options: 解析选项
        
        Returns:
            DocumentIR: 文档的中间表示
        
        Raises:
            ParseError: 解析失败时抛出
        """
        pass
    
    def can_parse(self, source: Union[str, Path]) -> bool:
        """
        检查是否可以解析给定的源文件
        
        Args:
            source: 文件路径
        
        Returns:
            是否可以解析
        """
        if isinstance(source, (str, Path)):
            path = Path(source)
            return path.suffix.lower() in [ext.lower() for ext in self.supported_extensions]
        return False
    
    def _read_source(self, source: Union[str, Path, bytes]) -> Union[str, bytes]:
        """
        读取源文件内容
        
        Args:
            source: 文件路径或二进制内容
        
        Returns:
            文件内容
        """
        if isinstance(source, (str, Path)):
            path = Path(source)
            if not path.exists():
                raise FileNotFoundError(f"文件不存在: {path}")
            
            # 根据扩展名决定读取方式
            if path.suffix.lower() in ['.pdf', '.docx']:
                return path.read_bytes()
            else:
                return path.read_text(encoding='utf-8')
        
        return source


class ParseError(Exception):
    """解析错误"""
    
    def __init__(self, message: str, source: Optional[str] = None):
        self.message = message
        self.source = source
        super().__init__(self.message)
