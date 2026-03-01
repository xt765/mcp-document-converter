"""
Text 解析器 - 将纯文本解析为中间表示
"""

import re
from pathlib import Path
from typing import Any, List, Union

import chardet

from ..core.ir import DocumentIR, Node, NodeType
from ..core.parser import BaseParser, ParseError


class TextParser(BaseParser):
    """
    纯文本文档解析器

    将 .txt 文件解析为中间表示。
    支持自动检测编码。
    """

    @property
    def supported_extensions(self) -> List[str]:
        return [".txt", ".text"]

    @property
    def format_name(self) -> str:
        return "text"

    @property
    def mime_types(self) -> List[str]:
        return ["text/plain"]

    def parse(self, source: Union[str, Path, bytes], **options: Any) -> DocumentIR:
        """
        解析纯文本文档

        Args:
            source: 文本文件路径或内容
            **options: 解析选项
                - encoding: 指定编码（默认自动检测）
                - detect_structure: 是否尝试检测结构（标题、列表等）

        Returns:
            DocumentIR: 文档的中间表示
        """
        try:
            # 读取内容
            if isinstance(source, (str, Path)):
                path = Path(source)
                content_bytes = path.read_bytes()
            else:
                content_bytes = source

            # 检测或获取编码
            encoding = options.get("encoding")
            if not encoding and isinstance(content_bytes, bytes):
                detected = chardet.detect(content_bytes)
                encoding = detected.get("encoding", "utf-8") or "utf-8"

            # 解码内容
            if isinstance(content_bytes, bytes):
                content = content_bytes.decode(encoding, errors="replace")
            else:
                content = content_bytes

            document = DocumentIR()

            # 是否检测结构
            detect_structure = options.get("detect_structure", True)

            if detect_structure:
                self._parse_with_structure(document, content)
            else:
                # 简单解析为段落
                paragraphs = content.split("\n\n")
                for para in paragraphs:
                    para = para.strip()
                    if para:
                        document.add_node(
                            Node(
                                type=NodeType.PARAGRAPH,
                                content=[Node(type=NodeType.TEXT, content=para)],
                            )
                        )

            return document

        except Exception as e:
            raise ParseError(f"文本解析失败: {str(e)}")

    def _parse_with_structure(self, document: DocumentIR, text: str) -> None:
        """
        尝试检测并解析文本结构

        识别：
        - 标题（全大写、下划线、编号等）
        - 列表
        - 代码块（缩进）
        - 引用（> 开头）
        - 分隔线
        """
        lines = text.split("\n")
        i = 0

        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            if not stripped:
                i += 1
                continue

            # 检查分隔线
            if re.match(r"^[\*\-=]{3,}$", stripped):
                document.add_node(Node(type=NodeType.HORIZONTAL_RULE, content=""))
                i += 1
                continue

            # 检查标题（下划线风格）
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if re.match(r"^=+$", next_line) and len(next_line) >= len(stripped):
                    document.add_node(
                        Node(
                            type=NodeType.HEADING,
                            content=[Node(type=NodeType.TEXT, content=stripped)],
                            attributes={"level": 1},
                        )
                    )
                    i += 2
                    continue
                elif re.match(r"^-+$", next_line) and len(next_line) >= len(stripped):
                    document.add_node(
                        Node(
                            type=NodeType.HEADING,
                            content=[Node(type=NodeType.TEXT, content=stripped)],
                            attributes={"level": 2},
                        )
                    )
                    i += 2
                    continue

            # 检查标题（Markdown 风格）
            heading_match = re.match(r"^(#{1,6})\s+(.+)$", stripped)
            if heading_match:
                level = len(heading_match.group(1))
                title = heading_match.group(2)
                document.add_node(
                    Node(
                        type=NodeType.HEADING,
                        content=[Node(type=NodeType.TEXT, content=title)],
                        attributes={"level": level},
                    )
                )
                i += 1
                continue

            # 检查标题（全大写且较短）
            if stripped.isupper() and len(stripped) < 100 and len(stripped) > 3:
                document.add_node(
                    Node(
                        type=NodeType.HEADING,
                        content=[Node(type=NodeType.TEXT, content=stripped)],
                        attributes={"level": 2},
                    )
                )
                i += 1
                continue

            # 检查标题（编号风格）
            if re.match(r"^\d+[.\s]", stripped) and len(stripped) < 100:
                level = self._get_numbered_heading_level(stripped)
                document.add_node(
                    Node(
                        type=NodeType.HEADING,
                        content=[Node(type=NodeType.TEXT, content=stripped)],
                        attributes={"level": level},
                    )
                )
                i += 1
                continue

            # 检查引用
            if stripped.startswith(">"):
                quote_lines = []
                while i < len(lines) and lines[i].strip().startswith(">"):
                    quote_lines.append(lines[i].strip()[1:].strip())
                    i += 1

                quote_text = " ".join(quote_lines)
                document.add_node(
                    Node(
                        type=NodeType.BLOCKQUOTE,
                        content=[
                            Node(
                                type=NodeType.PARAGRAPH,
                                content=[Node(type=NodeType.TEXT, content=quote_text)],
                            )
                        ],
                    )
                )
                continue

            # 检查代码块（缩进）
            if line.startswith("    ") or line.startswith("\t"):
                code_lines = []
                while i < len(lines) and (
                    lines[i].startswith("    ") or lines[i].startswith("\t") or not lines[i].strip()
                ):
                    if lines[i].strip():
                        code_lines.append(lines[i].strip())
                    i += 1

                if code_lines:
                    document.add_node(Node(type=NodeType.CODE_BLOCK, content="\n".join(code_lines)))
                continue

            # 检查列表
            list_match = re.match(r"^([\*\-\+•]|\d+[.\)])\s+(.+)$", stripped)
            if list_match:
                list_type = "ordered" if list_match.group(1)[0].isdigit() else "unordered"
                items = []

                while i < len(lines):
                    line_stripped = lines[i].strip()
                    if not line_stripped:
                        i += 1
                        continue

                    item_match = re.match(r"^([\*\-\+•]|\d+[.\)])\s+(.+)$", line_stripped)
                    if item_match:
                        items.append(
                            Node(
                                type=NodeType.LIST_ITEM,
                                content=[Node(type=NodeType.TEXT, content=item_match.group(2))],
                            )
                        )
                        i += 1
                    elif line_stripped and not lines[i].startswith("    "):
                        break
                    else:
                        i += 1

                if items:
                    document.add_node(
                        Node(type=NodeType.LIST, content=items, attributes={"type": list_type})
                    )
                continue

            # 普通段落
            paragraph_lines = []
            while i < len(lines):
                line_stripped = lines[i].strip()
                if not line_stripped:
                    break
                # 如果遇到特殊结构，结束段落
                if (
                    re.match(r"^[\*\-=]{3,}$", line_stripped)
                    or re.match(r"^(#{1,6})\s+", line_stripped)
                    or line_stripped.startswith(">")
                    or re.match(r"^([\*\-\+•]|\d+[.\)])\s+", line_stripped)
                    or lines[i].startswith("    ")
                    or lines[i].startswith("\t")
                ):
                    break
                paragraph_lines.append(line_stripped)
                i += 1

            if paragraph_lines:
                paragraph_text = " ".join(paragraph_lines)
                document.add_node(
                    Node(
                        type=NodeType.PARAGRAPH,
                        content=[Node(type=NodeType.TEXT, content=paragraph_text)],
                    )
                )

    def _get_numbered_heading_level(self, line: str) -> int:
        """根据编号获取标题级别"""
        match = re.match(r"^(\d+)[.\s]", line)
        if match:
            num = int(match.group(1))
            if num == 1:
                return 1
            elif num < 10:
                return 2
            else:
                return 3
        return 2
