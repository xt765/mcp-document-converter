"""
PDF 解析器 - 将 PDF 解析为中间表示
"""

import re
from pathlib import Path
from typing import Any, List, Union

from PyPDF2 import PdfReader

from ..core.ir import DocumentIR, Node, NodeType
from ..core.parser import BaseParser, ParseError


class PDFParser(BaseParser):
    """
    PDF 文档解析器

    将 PDF 文件解析为中间表示。
    """

    @property
    def supported_extensions(self) -> List[str]:
        return [".pdf"]

    @property
    def format_name(self) -> str:
        return "pdf"

    @property
    def mime_types(self) -> List[str]:
        return ["application/pdf"]

    def parse(self, source: Union[str, Path, bytes], **options: Any) -> DocumentIR:
        """
        解析 PDF 文档

        Args:
            source: PDF 文件路径或二进制内容
            **options: 解析选项

        Returns:
            DocumentIR: 文档的中间表示
        """
        try:
            # 读取 PDF
            if isinstance(source, (str, Path)):
                reader = PdfReader(str(source))
            else:
                from io import BytesIO

                reader = PdfReader(BytesIO(source))

            document = DocumentIR()

            # 提取元数据
            if reader.metadata:
                metadata = reader.metadata
                document.title = getattr(metadata, "title", None)
                document.author = getattr(metadata, "author", None)
                if getattr(metadata, "creation_date", None):
                    document.created_at = metadata.creation_date
                if getattr(metadata, "modification_date", None):
                    document.modified_at = metadata.modification_date

                document.metadata = {
                    "subject": getattr(metadata, "subject", None),
                    "creator": getattr(metadata, "creator", None),
                    "producer": getattr(metadata, "producer", None),
                    "page_count": len(reader.pages),
                }

            # 提取文本内容
            all_text = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    all_text.append(text)

            full_text = "\n\n".join(all_text)

            # 解析文本结构
            self._parse_text_structure(document, full_text)

            return document

        except Exception as e:
            raise ParseError(f"PDF 解析失败: {str(e)}")

    def _parse_text_structure(self, document: DocumentIR, text: str) -> None:
        """
        解析文本结构

        尝试识别标题、段落等结构
        """
        lines = text.split("\n")
        current_paragraph = []

        for line in lines:
            line = line.strip()
            if not line:
                # 空行，结束当前段落
                if current_paragraph:
                    paragraph_text = " ".join(current_paragraph)
                    node = self._classify_text(paragraph_text)
                    document.add_node(node)
                    current_paragraph = []
                continue

            # 检查是否为标题特征
            if self._is_heading(line):
                if current_paragraph:
                    paragraph_text = " ".join(current_paragraph)
                    node = self._classify_text(paragraph_text)
                    document.add_node(node)
                    current_paragraph = []

                level = self._get_heading_level(line)
                document.add_node(
                    Node(
                        type=NodeType.HEADING,
                        content=[Node(type=NodeType.TEXT, content=line.strip("#").strip())],
                        attributes={"level": level},
                    )
                )
            else:
                current_paragraph.append(line)

        # 处理最后一段
        if current_paragraph:
            paragraph_text = " ".join(current_paragraph)
            node = self._classify_text(paragraph_text)
            document.add_node(node)

    def _is_heading(self, line: str) -> bool:
        """判断是否为标题"""
        # 全大写且较短
        if line.isupper() and len(line) < 100 and len(line) > 3:
            return True

        # 以数字开头（如 "1. Introduction"）
        if re.match(r"^\d+[.\s]", line) and len(line) < 100:
            return True

        # 以 # 开头（Markdown 风格，可能来自转换的 PDF）
        if line.startswith("#"):
            return True

        return False

    def _get_heading_level(self, line: str) -> int:
        """获取标题级别"""
        # Markdown 风格
        if line.startswith("#"):
            match = re.match(r"^(#+)", line)
            if match:
                return min(len(match.group(1)), 6)

        # 数字编号风格
        match = re.match(r"^(\d+)[.\s]", line)
        if match:
            num = int(match.group(1))
            if num == 1:
                return 1
            elif num < 10:
                return 2
            else:
                return 3

        # 全大写作为一级标题
        if line.isupper():
            return 1

        return 2

    def _classify_text(self, text: str) -> Node:
        """对文本进行分类"""
        text = text.strip()

        # 检查是否为列表
        if re.match(r"^[\*\-\+•]\s", text):
            items = text.split("\n")
            list_items = []
            for item in items:
                item = re.sub(r"^[\*\-\+•]\s*", "", item).strip()
                if item:
                    list_items.append(
                        Node(
                            type=NodeType.LIST_ITEM,
                            content=[Node(type=NodeType.TEXT, content=item)],
                        )
                    )
            if list_items:
                return Node(
                    type=NodeType.LIST, content=list_items, attributes={"type": "unordered"}
                )

        # 检查是否为代码块（缩进或等宽字体特征）
        if text.startswith("    ") or text.startswith("\t"):
            return Node(type=NodeType.CODE_BLOCK, content=text.strip())

        # 普通段落
        return Node(type=NodeType.PARAGRAPH, content=[Node(type=NodeType.TEXT, content=text)])
