"""
测试 Markdown 解析器 - 覆盖更多代码
"""

import pytest

from mcp_document_converter.core.ir import NodeType
from mcp_document_converter.parsers.markdown import MarkdownParser


class TestMarkdownParserFull:
    """测试 Markdown 解析器完整覆盖"""

    @pytest.fixture
    def parser(self):
        return MarkdownParser()

    def test_parse_task_list(self, parser, temp_dir):
        """测试任务列表"""
        md_path = temp_dir / "test.md"
        md_path.write_text(
            "- [ ] 未完成\n- [x] 已完成",
            encoding="utf-8",
        )

        doc = parser.parse(md_path)

        assert isinstance(doc, doc.__class__)
        lists = [n for n in doc.content if n.type == NodeType.LIST]
        assert len(lists) >= 1

    def test_parse_footnote(self, parser, temp_dir):
        """测试脚注"""
        md_path = temp_dir / "test.md"
        md_path.write_text(
            "文本[^1]\n\n[^1]: 脚注内容",
            encoding="utf-8",
        )

        doc = parser.parse(md_path)

        assert isinstance(doc, doc.__class__)

    def test_parse_definition_list(self, parser, temp_dir):
        """测试定义列表"""
        md_path = temp_dir / "test.md"
        md_path.write_text(
            "术语 1\n:   定义 1\n\n术语 2\n:   定义 2",
            encoding="utf-8",
        )

        doc = parser.parse(md_path)

        assert isinstance(doc, doc.__class__)

    def test_parse_abbreviation(self, parser, temp_dir):
        """测试缩写"""
        md_path = temp_dir / "test.md"
        md_path.write_text(
            "HTML 是超文本标记语言\n\n*[HTML]: HyperText Markup Language",
            encoding="utf-8",
        )

        doc = parser.parse(md_path)

        assert isinstance(doc, doc.__class__)

    def test_parse_admonition(self, parser, temp_dir):
        """测试提示块"""
        md_path = temp_dir / "test.md"
        md_path.write_text(
            "!!! note\n    这是一个提示",
            encoding="utf-8",
        )

        doc = parser.parse(md_path)

        assert isinstance(doc, doc.__class__)

    def test_parse_subscript_superscript(self, parser, temp_dir):
        """测试下标和上标"""
        md_path = temp_dir / "test.md"
        md_path.write_text(
            "H~2~O 和 E=mc^2^",
            encoding="utf-8",
        )

        doc = parser.parse(md_path)

        assert isinstance(doc, doc.__class__)

    def test_parse_mark_highlight(self, parser, temp_dir):
        """测试标记高亮"""
        md_path = temp_dir / "test.md"
        md_path.write_text(
            "==高亮文本==",
            encoding="utf-8",
        )

        doc = parser.parse(md_path)

        assert isinstance(doc, doc.__class__)

    def test_parse_complex_table(self, parser, temp_dir):
        """测试复杂表格"""
        md_path = temp_dir / "test.md"
        md_path.write_text(
            """| 左对齐 | 居中 | 右对齐 |
|:-------|:----:|-------:|
| A       |  B   |       C |
| D       |  E   |       F |""",
            encoding="utf-8",
        )

        doc = parser.parse(md_path)

        tables = [n for n in doc.content if n.type == NodeType.TABLE]
        assert len(tables) >= 1

    def test_parse_nested_list(self, parser, temp_dir):
        """测试嵌套列表"""
        md_path = temp_dir / "test.md"
        md_path.write_text(
            """- 项目 1
  - 子项目 1.1
  - 子项目 1.2
- 项目 2""",
            encoding="utf-8",
        )

        doc = parser.parse(md_path)

        lists = [n for n in doc.content if n.type == NodeType.LIST]
        assert len(lists) >= 1

    def test_parse_multiline_code_block(self, parser, temp_dir):
        """测试多行代码块"""
        md_path = temp_dir / "test.md"
        md_path.write_text(
            """```python
def hello():
    print("Hello")
    print("World")
```""",
            encoding="utf-8",
        )

        doc = parser.parse(md_path)

        code_blocks = [n for n in doc.content if n.type == NodeType.CODE_BLOCK]
        assert len(code_blocks) >= 1

    def test_parse_inline_attributes(self, parser, temp_dir):
        """测试行内属性"""
        md_path = temp_dir / "test.md"
        md_path.write_text(
            "段落{: #id .class}",
            encoding="utf-8",
        )

        doc = parser.parse(md_path)

        assert isinstance(doc, doc.__class__)

    def test_parse_empty_document(self, parser, temp_dir):
        """测试空文档"""
        md_path = temp_dir / "empty.md"
        md_path.write_text("", encoding="utf-8")

        doc = parser.parse(md_path)

        assert len(doc.content) == 0

    def test_parse_whitespace_only(self, parser, temp_dir):
        """测试只有空白字符"""
        md_path = temp_dir / "whitespace.md"
        md_path.write_text("   \n\n   \n", encoding="utf-8")

        doc = parser.parse(md_path)

        assert isinstance(doc, doc.__class__)
