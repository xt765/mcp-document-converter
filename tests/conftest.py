"""
pytest 配置文件
"""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """临时目录 fixture"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_markdown():
    """示例 Markdown 内容"""
    return """# 测试文档

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
"""


@pytest.fixture
def sample_html():
    """示例 HTML 内容"""
    return """<!DOCTYPE html>
<html>
<head><title>测试</title></head>
<body>
<h1>HTML 测试</h1>
<p>这是一个 <strong>测试</strong> 段落。</p>
</body>
</html>
"""
