"""
插件注册表 - 管理所有解析器和渲染器
"""

from pathlib import Path
from typing import Dict, List, Optional, Union

from .core.parser import BaseParser
from .core.renderer import BaseRenderer


class ConverterRegistry:
    """
    转换器注册表

    管理所有解析器和渲染器，提供格式查找和自动匹配功能。

    Example:
        ```python
        registry = ConverterRegistry()

        # 注册解析器
        registry.register_parser(MarkdownParser())

        # 注册渲染器
        registry.register_renderer(HTMLRenderer())

        # 查找解析器
        parser = registry.find_parser(".md")

        # 查找渲染器
        renderer = registry.find_renderer("html")
        ```
    """

    def __init__(self):
        self._parsers: Dict[str, BaseParser] = {}  # format_name -> parser
        self._renderers: Dict[str, BaseRenderer] = {}  # format_name -> renderer
        self._extension_to_format: Dict[str, str] = {}  # extension -> format_name

    def register_parser(self, parser: BaseParser) -> None:
        """
        注册解析器

        Args:
            parser: 解析器实例
        """
        self._parsers[parser.format_name] = parser

        # 建立扩展名到格式的映射
        for ext in parser.supported_extensions:
            ext_lower = ext.lower()
            self._extension_to_format[ext_lower] = parser.format_name

    def register_renderer(self, renderer: BaseRenderer) -> None:
        """
        注册渲染器

        Args:
            renderer: 渲染器实例
        """
        self._renderers[renderer.format_name] = renderer

    def find_parser(self, source: Union[str, Path]) -> Optional[BaseParser]:
        """
        根据源文件查找合适的解析器

        Args:
            source: 文件路径或扩展名

        Returns:
            解析器实例，未找到返回 None
        """
        if isinstance(source, Path):
            source = str(source)

        # 提取扩展名
        if "." in source:
            ext = Path(source).suffix.lower()
        else:
            ext = source if source.startswith(".") else f".{source}"
            ext = ext.lower()

        format_name = self._extension_to_format.get(ext)
        if format_name:
            return self._parsers.get(format_name)

        return None

    def find_renderer(self, format_name: str) -> Optional[BaseRenderer]:
        """
        根据格式名称查找渲染器

        Args:
            format_name: 格式名称，如 "html", "pdf"

        Returns:
            渲染器实例，未找到返回 None
        """
        return self._renderers.get(format_name.lower())

    def get_parser(self, format_name: str) -> Optional[BaseParser]:
        """
        根据格式名称获取解析器

        Args:
            format_name: 格式名称

        Returns:
            解析器实例，未找到返回 None
        """
        return self._parsers.get(format_name.lower())

    def list_parsers(self) -> List[BaseParser]:
        """
        列出所有已注册的解析器

        Returns:
            解析器列表
        """
        return list(self._parsers.values())

    def list_renderers(self) -> List[BaseRenderer]:
        """
        列出所有已注册的渲染器

        Returns:
            渲染器列表
        """
        return list(self._renderers.values())

    def list_supported_formats(self) -> Dict[str, List[str]]:
        """
        列出所有支持的格式

        Returns:
            包含解析格式和渲染格式的字典
        """
        return {
            "parsers": list(self._parsers.keys()),
            "renderers": list(self._renderers.keys()),
        }

    def get_conversion_matrix(self) -> Dict[str, List[str]]:
        """
        获取格式转换矩阵

        Returns:
            源格式到目标格式的映射
        """
        matrix = {}
        for parser_name in self._parsers.keys():
            matrix[parser_name] = list(self._renderers.keys())
        return matrix

    def can_convert(self, source_format: str, target_format: str) -> bool:
        """
        检查是否支持从源格式转换到目标格式

        Args:
            source_format: 源格式名称
            target_format: 目标格式名称

        Returns:
            是否支持转换
        """
        has_parser = source_format.lower() in self._parsers
        has_renderer = target_format.lower() in self._renderers
        return has_parser and has_renderer


# 全局注册表实例
_registry: Optional[ConverterRegistry] = None


def get_registry() -> ConverterRegistry:
    """
    获取全局注册表实例

    Returns:
        ConverterRegistry 实例
    """
    global _registry
    if _registry is None:
        _registry = ConverterRegistry()
    return _registry


def register_parser(parser: BaseParser) -> None:
    """注册解析器到全局注册表"""
    get_registry().register_parser(parser)


def register_renderer(renderer: BaseRenderer) -> None:
    """注册渲染器到全局注册表"""
    get_registry().register_renderer(renderer)


def find_parser(source: Union[str, Path]) -> Optional[BaseParser]:
    """在全局注册表中查找解析器"""
    return get_registry().find_parser(source)


def find_renderer(format_name: str) -> Optional[BaseRenderer]:
    """在全局注册表中查找渲染器"""
    return get_registry().find_renderer(format_name)
