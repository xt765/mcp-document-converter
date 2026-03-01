"""
转换引擎 - 协调解析器和渲染器完成文档转换
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..registry import ConverterRegistry, get_registry
from .ir import DocumentIR
from .parser import ParseError
from .renderer import RenderError


@dataclass
class ConversionResult:
    """转换结果"""

    success: bool
    output_path: Optional[Path] = None
    content: Optional[Union[str, bytes]] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class DocumentConverter:
    """
    文档转换引擎

    协调解析器和渲染器，完成从任意格式到任意格式的转换。

    Example:
        ```python
        converter = DocumentConverter()

        # 简单转换
        result = converter.convert("input.md", "html")

        # 指定输出路径
        result = converter.convert("input.md", "html", output_path="output.html")

        # 使用选项
        result = converter.convert(
            "input.md",
            "pdf",
            options={"template": "default", "css": "custom.css"}
        )
        ```
    """

    def __init__(self, registry: Optional[ConverterRegistry] = None):
        """
        初始化转换器

        Args:
            registry: 注册表实例，默认使用全局注册表
        """
        self.registry = registry or get_registry()

    def convert(
        self,
        source: Union[str, Path],
        target_format: str,
        output_path: Optional[Union[str, Path]] = None,
        source_format: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> ConversionResult:
        """
        转换文档

        Args:
            source: 源文件路径
            target_format: 目标格式，如 "html", "pdf"
            output_path: 输出文件路径（可选）
            source_format: 源格式（可选，自动检测）
            options: 转换选项

        Returns:
            ConversionResult: 转换结果
        """
        options = options or {}
        source_path = Path(source)

        try:
            # 1. 查找解析器
            if source_format:
                parser = self.registry.get_parser(source_format)
            else:
                parser = self.registry.find_parser(source_path)

            if not parser:
                available = self.registry.list_supported_formats()["parsers"]
                return ConversionResult(
                    success=False,
                    error_message=f"不支持的源格式: {source_path.suffix}. "
                    f"支持的格式: {', '.join(available)}",
                )

            # 2. 查找渲染器
            renderer = self.registry.find_renderer(target_format)
            if not renderer:
                available = self.registry.list_supported_formats()["renderers"]
                return ConversionResult(
                    success=False,
                    error_message=f"不支持的目标格式: {target_format}. "
                    f"支持的格式: {', '.join(available)}",
                )

            # 3. 解析文档
            document = parser.parse(source_path, **options.get("parse_options", {}))

            # 4. 渲染文档
            content = renderer.render(document, **options.get("render_options", {}))

            # 5. 确定输出路径
            if output_path is None:
                output_path = source_path.with_suffix(renderer.output_extension)
            else:
                output_path = Path(output_path)

            # 6. 保存文件
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if renderer.is_binary:
                output_path.write_bytes(content if isinstance(content, bytes) else content.encode())
            else:
                output_path.write_text(
                    content if isinstance(content, str) else content.decode(), encoding="utf-8"
                )

            return ConversionResult(
                success=True,
                output_path=output_path,
                content=content,
                metadata={
                    "source_format": parser.format_name,
                    "target_format": renderer.format_name,
                    "source_path": str(source_path),
                    "output_path": str(output_path),
                },
            )

        except FileNotFoundError as e:
            return ConversionResult(success=False, error_message=f"文件不存在: {e}")
        except ParseError as e:
            return ConversionResult(success=False, error_message=f"解析错误: {e.message}")
        except RenderError as e:
            return ConversionResult(success=False, error_message=f"渲染错误: {e.message}")
        except Exception as e:
            return ConversionResult(success=False, error_message=f"转换失败: {str(e)}")

    def convert_to_ir(
        self, source: Union[str, Path], source_format: Optional[str] = None
    ) -> DocumentIR:
        """
        将文档转换为中间表示

        Args:
            source: 源文件路径
            source_format: 源格式（可选，自动检测）

        Returns:
            DocumentIR: 文档的中间表示

        Raises:
            ValueError: 找不到合适的解析器
            ParseError: 解析失败
        """
        source_path = Path(source)

        # 查找解析器
        if source_format:
            parser = self.registry.get_parser(source_format)
        else:
            parser = self.registry.find_parser(source_path)

        if not parser:
            raise ValueError(f"找不到支持 {source_path.suffix} 格式的解析器")

        return parser.parse(source_path)

    def render_from_ir(
        self,
        document: DocumentIR,
        target_format: str,
        output_path: Optional[Union[str, Path]] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> ConversionResult:
        """
        从中间表示渲染为目标格式

        Args:
            document: 文档的中间表示
            target_format: 目标格式
            output_path: 输出文件路径（可选）
            options: 渲染选项

        Returns:
            ConversionResult: 转换结果
        """
        options = options or {}

        try:
            # 查找渲染器
            renderer = self.registry.find_renderer(target_format)
            if not renderer:
                available = self.registry.list_supported_formats()["renderers"]
                return ConversionResult(
                    success=False,
                    error_message=f"不支持的目标格式: {target_format}. "
                    f"支持的格式: {', '.join(available)}",
                )

            # 渲染文档
            content = renderer.render(document, **options)

            # 保存文件
            if output_path:
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)

                if renderer.is_binary:
                    output_path.write_bytes(
                        content if isinstance(content, bytes) else content.encode()
                    )
                else:
                    output_path.write_text(
                        content if isinstance(content, str) else content.decode(), encoding="utf-8"
                    )

            return ConversionResult(
                success=True,
                output_path=Path(output_path) if output_path else None,
                content=content,
                metadata={
                    "target_format": renderer.format_name,
                    "output_path": str(output_path) if output_path else None,
                },
            )

        except RenderError as e:
            return ConversionResult(success=False, error_message=f"渲染错误: {e.message}")
        except Exception as e:
            return ConversionResult(success=False, error_message=f"渲染失败: {str(e)}")

    def list_supported_conversions(self) -> Dict[str, List[str]]:
        """
        列出所有支持的转换组合

        Returns:
            源格式到目标格式的映射
        """
        return self.registry.get_conversion_matrix()

    def can_convert(self, source_format: str, target_format: str) -> bool:
        """
        检查是否支持转换

        Args:
            source_format: 源格式
            target_format: 目标格式

        Returns:
            是否支持
        """
        return self.registry.can_convert(source_format, target_format)
