# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-03-01

### Added

- **CI/CD Workflows**: Added GitHub Actions workflows for automated testing and publishing
  - CI workflow with Ruff, Basedpyright, and Pytest
  - Release workflow for PyPI and MCP Registry publishing
  - Support for Python 3.10-3.14

- **Test Suite**: Comprehensive test coverage increased to 89%
  - 361 test cases covering all core modules
  - Unit tests for parsers, renderers, and converters
  - Integration tests for MCP tools

- **Documentation**: Added comprehensive documentation structure
  - API Reference
  - User Guide
  - Contributing Guide

### Changed

- **Type Checking**: Switched from MyPy to Basedpyright for better type inference
- **Code Formatting**: Replaced Black with Ruff format
- **Dev Dependencies**: Updated development toolchain

### Fixed

- **WeasyPrint Compatibility**: Fixed import handling for Windows environments
- **Type Safety**: Fixed all Basedpyright type errors
- **Code Quality**: Fixed all Ruff linting issues

## [0.1.2] - 2025-02-28

### Added

- **MCP Tools**: Added comprehensive MCP tool interface
  - `convert_document`: Main conversion tool
  - `list_supported_formats`: List all supported formats
  - `get_conversion_matrix`: Get conversion matrix
  - `can_convert`: Check conversion support
  - `get_format_info`: Get format information

- **PDF Support**: Added PDF parsing and rendering capabilities
  - Text extraction from PDF files
  - PDF generation with WeasyPrint
  - Custom template support

### Changed

- **Architecture**: Improved plugin architecture for better extensibility
- **Error Handling**: Enhanced error messages and exception handling

## [0.1.1] - 2025-02-27

### Added

- **DOCX Support**: Added DOCX parsing and rendering
  - Style preservation
  - Table support
  - Image extraction

- **HTML Support**: Added HTML parsing and rendering
  - Semantic tag parsing
  - Code syntax highlighting
  - Custom CSS support

### Fixed

- **Encoding Detection**: Improved auto-encoding detection for text files
- **Metadata Preservation**: Fixed metadata preservation during conversion

## [0.1.0] - 2025-02-25

### Added

- **Initial Release**: First public release of MCP Document Converter
  - Core conversion engine with intermediate representation
  - Markdown parser and renderer
  - HTML renderer
  - Text parser and renderer
  - Plugin architecture for extensibility
  - MCP protocol support for AI assistants

- **Supported Formats**:
  - Input: Markdown, HTML, DOCX, PDF, Text
  - Output: Markdown, HTML, DOCX, PDF, Text

- **Features**:
  - Bidirectional conversion between all formats
  - Metadata preservation
  - Image extraction and embedding
  - Custom styling support
