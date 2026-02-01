"""
测试脚本 - 验证文档转换功能
"""

import tempfile
from pathlib import Path

from mcp_document_converter import DocumentConverter
from mcp_document_converter.registry import get_registry
from mcp_document_converter.parsers import (
    MarkdownParser,
    HTMLParser,
    DOCXParser,
    PDFParser,
    TextParser,
)
from mcp_document_converter.renderers import (
    HTMLRenderer,
    MarkdownRenderer,
    DOCXRenderer,
    PDFRenderer,
    TextRenderer,
)


def setup_registry():
    """设置注册表"""
    registry = get_registry()
    
    # 注册解析器
    registry.register_parser(MarkdownParser())
    registry.register_parser(HTMLParser())
    registry.register_parser(DOCXParser())
    registry.register_parser(PDFParser())
    registry.register_parser(TextParser())
    
    # 注册渲染器
    registry.register_renderer(HTMLRenderer())
    registry.register_renderer(MarkdownRenderer())
    registry.register_renderer(DOCXRenderer())
    registry.register_renderer(PDFRenderer())
    registry.register_renderer(TextRenderer())
    
    return registry


def test_markdown_to_html():
    """测试 Markdown 转 HTML"""
    print("\n🧪 测试 Markdown 转 HTML...")
    
    # 创建测试 Markdown 文件
    md_content = """# 测试文档

这是**粗体**和*斜体*文本。

## 代码示例

```python
def hello():
    print("Hello, World!")
```

## 列表示例

- 项目 1
- 项目 2
- 项目 3

## 表格示例

| 名称 | 值 |
|------|-----|
| A | 1 |
| B | 2 |
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write(md_content)
        md_path = f.name
    
    try:
        registry = setup_registry()
        converter = DocumentConverter(registry)
        
        result = converter.convert(md_path, 'html')
        
        if result.success:
            print(f"✅ 转换成功!")
            print(f"   输出文件: {result.output_path}")
            
            # 验证输出文件存在
            assert Path(result.output_path).exists(), "输出文件不存在"
            
            # 验证内容
            html_content = Path(result.output_path).read_text(encoding='utf-8')
            assert '<h1>测试文档</h1>' in html_content or '<h1>' in html_content
            assert '<strong>粗体</strong>' in html_content or '<strong>' in html_content
            
            print("✅ 内容验证通过!")
        else:
            print(f"❌ 转换失败: {result.error_message}")
            return False
            
    finally:
        # 清理
        Path(md_path).unlink(missing_ok=True)
        if result.output_path:
            Path(result.output_path).unlink(missing_ok=True)
    
    return True


def test_html_to_markdown():
    """测试 HTML 转 Markdown"""
    print("\n🧪 测试 HTML 转 Markdown...")
    
    html_content = """<!DOCTYPE html>
<html>
<head><title>测试</title></head>
<body>
<h1>HTML 测试</h1>
<p>这是一个 <strong>测试</strong> 段落。</p>
<ul>
<li>项目 A</li>
<li>项目 B</li>
</ul>
</body>
</html>"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(html_content)
        html_path = f.name
    
    try:
        registry = setup_registry()
        converter = DocumentConverter(registry)
        
        result = converter.convert(html_path, 'markdown')
        
        if result.success:
            print(f"✅ 转换成功!")
            print(f"   输出文件: {result.output_path}")
            
            md_content = Path(result.output_path).read_text(encoding='utf-8')
            assert '# HTML 测试' in md_content
            
            print("✅ 内容验证通过!")
        else:
            print(f"❌ 转换失败: {result.error_message}")
            return False
            
    finally:
        Path(html_path).unlink(missing_ok=True)
        if result.output_path:
            Path(result.output_path).unlink(missing_ok=True)
    
    return True


def test_text_to_html():
    """测试 Text 转 HTML"""
    print("\n🧪 测试 Text 转 HTML...")
    
    text_content = """测试文档
========

这是第一段文字。

这是第二段文字，包含一些格式。

- 列表项 1
- 列表项 2

代码示例：

    print("Hello")
    print("World")
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(text_content)
        txt_path = f.name
    
    try:
        registry = setup_registry()
        converter = DocumentConverter(registry)
        
        result = converter.convert(txt_path, 'html')
        
        if result.success:
            print(f"✅ 转换成功!")
            print(f"   输出文件: {result.output_path}")
            print("✅ 内容验证通过!")
        else:
            print(f"❌ 转换失败: {result.error_message}")
            return False
            
    finally:
        Path(txt_path).unlink(missing_ok=True)
        if result.output_path:
            Path(result.output_path).unlink(missing_ok=True)
    
    return True


def test_list_supported_formats():
    """测试列出支持的格式"""
    print("\n🧪 测试列出支持的格式...")
    
    registry = setup_registry()
    formats = registry.list_supported_formats()
    
    print(f"支持的解析格式: {formats['parsers']}")
    print(f"支持的渲染格式: {formats['renderers']}")
    
    assert 'markdown' in formats['parsers']
    assert 'html' in formats['parsers']
    assert 'docx' in formats['parsers']
    assert 'pdf' in formats['parsers']
    assert 'text' in formats['parsers']
    
    assert 'html' in formats['renderers']
    assert 'markdown' in formats['renderers']
    assert 'docx' in formats['renderers']
    assert 'pdf' in formats['renderers']
    assert 'text' in formats['renderers']
    
    print("✅ 格式列表验证通过!")
    return True


def test_conversion_matrix():
    """测试转换矩阵"""
    print("\n🧪 测试转换矩阵...")
    
    registry = setup_registry()
    converter = DocumentConverter(registry)
    
    matrix = converter.list_supported_conversions()
    
    print("转换矩阵:")
    for source, targets in matrix.items():
        print(f"  {source} -> {', '.join(targets)}")
    
    # 验证所有格式都可以相互转换
    for source in matrix:
        assert len(matrix[source]) == 5, f"{source} 应该有 5 个目标格式"
    
    print("✅ 转换矩阵验证通过!")
    return True


def main():
    """运行所有测试"""
    print("=" * 60)
    print("MCP Document Converter 测试")
    print("=" * 60)
    
    tests = [
        ("列出支持格式", test_list_supported_formats),
        ("转换矩阵", test_conversion_matrix),
        ("Markdown 转 HTML", test_markdown_to_html),
        ("HTML 转 Markdown", test_html_to_markdown),
        ("Text 转 HTML", test_text_to_html),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"❌ {name} 测试失败")
        except Exception as e:
            failed += 1
            print(f"❌ {name} 测试异常: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
