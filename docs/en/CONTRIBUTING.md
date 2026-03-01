# Contributing Guide

Thank you for your interest in contributing to MCP Document Converter!

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Standards](#code-standards)
- [Commit Guidelines](#commit-guidelines)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)

---

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/xt765/mcp-document-converter.git
   cd mcp-document-converter
   ```
3. Create a branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

---

## Development Setup

### Prerequisites

- Python 3.10+
- uv (recommended) or pip

### Installation

```bash
# Create virtual environment
uv venv .venv --python 3.13

# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS

# Install dependencies
uv sync --all-extras
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test
pytest tests/test_engine.py -v
```

### Code Quality

```bash
# Lint check
ruff check src tests

# Format check
ruff format --check src tests

# Type check
basedpyright src
```

---

## Code Standards

### Style Guide

- Follow PEP 8 conventions
- Use Ruff for formatting and linting
- Maximum line length: 100 characters
- Use type hints for all public functions

### Documentation

- Add docstrings to all public modules, classes, and functions
- Use Google-style docstrings:

```python
def convert(source: str, target_format: str) -> ConversionResult:
    """
    Convert a document to the target format.

    Args:
        source: Path to the source file.
        target_format: Target format name.

    Returns:
        ConversionResult with success status and output.

    Raises:
        FileNotFoundError: If source file does not exist.
    """
```

### Code Comments

- Use Chinese comments for code explanations
- Add file-level, class-level, and function-level comments
- Comment complex logic sections

---

## Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Code style changes |
| `refactor` | Code refactoring |
| `test` | Adding/updating tests |
| `chore` | Build/config changes |

### Examples

```
feat(parser): add RST parser support

fix(pdf): fix image extraction on Windows

docs(api): update API reference for v0.2.0

test(engine): add edge case tests for conversion
```

---

## Testing

### Test Requirements

- All new features must have tests
- Bug fixes must include regression tests
- Maintain test coverage above 80%

### Test Structure

```
tests/
├── conftest.py           # Shared fixtures
├── test_engine.py        # Engine tests
├── test_parsers.py       # Parser tests
├── test_renderers.py     # Renderer tests
└── test_server.py        # MCP server tests
```

### Writing Tests

```python
import pytest
from mcp_document_converter import DocumentConverter

class TestDocumentConverter:
    """Test DocumentConverter class."""

    def test_convert_markdown_to_html(self, temp_dir):
        """Test Markdown to HTML conversion."""
        # Create test file
        md_file = temp_dir / "test.md"
        md_file.write_text("# Test\n\nHello World")

        # Convert
        converter = DocumentConverter()
        result = converter.convert(md_file, "html")

        # Assert
        assert result.success
        assert result.output_path.suffix == ".html"
```

---

## Pull Request Process

1. **Update Documentation**: Update relevant documentation for your changes
2. **Add Tests**: Include tests for new features or bug fixes
3. **Run Quality Checks**: Ensure all checks pass
   ```bash
   ruff check src tests
   ruff format --check src tests
   basedpyright src
   pytest --cov
   ```
4. **Create PR**: Open a pull request with a clear description

### PR Checklist

- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] Type checking passes
- [ ] Linting passes

---

## Questions?

Feel free to open an issue for any questions or discussions!
