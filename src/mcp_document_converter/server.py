"""
MCP Server - Provides MCP tool interface for document conversion
"""

import json
from typing import Any, Dict, List

from mcp.server import Server
from mcp.types import (
    TextContent,
    Tool,
)

from .core.engine import DocumentConverter
from .parsers import (
    DOCXParser,
    HTMLParser,
    MarkdownParser,
    PDFParser,
    TextParser,
)
from .registry import get_registry
from .renderers import (
    DOCXRenderer,
    HTMLRenderer,
    MarkdownRenderer,
    PDFRenderer,
    TextRenderer,
)


def create_server() -> Server:
    """Create and configure MCP server"""

    # Register all parsers and renderers
    registry = get_registry()

    # Register parsers
    registry.register_parser(MarkdownParser())
    registry.register_parser(HTMLParser())
    registry.register_parser(DOCXParser())
    registry.register_parser(PDFParser())
    registry.register_parser(TextParser())

    # Register renderers
    registry.register_renderer(HTMLRenderer())
    registry.register_renderer(MarkdownRenderer())
    registry.register_renderer(DOCXRenderer())
    registry.register_renderer(PDFRenderer())
    registry.register_renderer(TextRenderer())

    # Create converter
    converter = DocumentConverter(registry)

    # Create MCP server
    server = Server("mcp-document-converter")

    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """List all available tools"""
        return [
            Tool(
                name="convert_document",
                description="Convert a document from one format to another. Supports conversion between Markdown, HTML, DOCX, PDF, and Text formats.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "source_path": {
                            "type": "string",
                            "description": "Source file path, supports absolute or relative paths",
                        },
                        "target_format": {
                            "type": "string",
                            "description": "Target format",
                            "enum": ["html", "pdf", "markdown", "docx", "text"],
                        },
                        "output_path": {
                            "type": "string",
                            "description": "Output file path (optional, defaults to source filename)",
                        },
                        "source_format": {
                            "type": "string",
                            "description": "Source format (optional, auto-detected from file extension)",
                            "enum": ["markdown", "html", "docx", "pdf", "text"],
                        },
                        "options": {
                            "type": "object",
                            "description": "Conversion options",
                            "properties": {
                                "template": {"type": "string", "description": "Template name"},
                                "css": {"type": "string", "description": "Custom CSS styles"},
                                "preserve_metadata": {
                                    "type": "boolean",
                                    "description": "Whether to preserve metadata",
                                    "default": True,
                                },
                                "extract_images": {
                                    "type": "boolean",
                                    "description": "Whether to extract images",
                                    "default": True,
                                },
                            },
                        },
                    },
                    "required": ["source_path", "target_format"],
                },
            ),
            Tool(
                name="list_supported_formats",
                description="List all supported document formats and their conversion capabilities",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="can_convert",
                description="Check if conversion from source format to target format is supported",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "source_format": {
                            "type": "string",
                            "description": "Source format",
                            "enum": ["markdown", "html", "docx", "pdf", "text"],
                        },
                        "target_format": {
                            "type": "string",
                            "description": "Target format",
                            "enum": ["html", "pdf", "markdown", "docx", "text"],
                        },
                    },
                    "required": ["source_format", "target_format"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Call tool"""

        if name == "convert_document":
            return await _handle_convert_document(converter, arguments)

        elif name == "list_supported_formats":
            return await _handle_list_supported_formats(registry)

        elif name == "can_convert":
            return await _handle_can_convert(converter, arguments)

        else:
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {"error": f"Unknown tool: {name}"}, ensure_ascii=False, indent=2
                    ),
                )
            ]

    return server


async def _handle_convert_document(
    converter: DocumentConverter, arguments: Dict[str, Any]
) -> List[TextContent]:
    """Handle document conversion request"""
    source_path = arguments.get("source_path")
    target_format = arguments.get("target_format")
    output_path = arguments.get("output_path")
    source_format = arguments.get("source_format")
    options = arguments.get("options", {})

    if not source_path or not target_format:
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "success": False,
                        "error": "Missing required parameters: source_path and target_format",
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
            )
        ]

    # Execute conversion
    result = converter.convert(
        source=source_path,
        target_format=target_format,
        output_path=output_path,
        source_format=source_format,
        options=options,
    )

    if result.success:
        response = {
            "success": True,
            "message": "Conversion successful!",
            "source_path": source_path,
            "output_path": str(result.output_path) if result.output_path else None,
            "target_format": target_format,
            "metadata": result.metadata,
        }
    else:
        response = {
            "success": False,
            "error": result.error_message,
            "source_path": source_path,
            "target_format": target_format,
        }

    return [TextContent(type="text", text=json.dumps(response, ensure_ascii=False, indent=2))]


async def _handle_list_supported_formats(registry) -> List[TextContent]:
    """Handle list supported formats request"""
    registry.list_supported_formats()

    # Get detailed information of parsers and renderers
    parsers_info = []
    for parser in registry.list_parsers():
        parsers_info.append(
            {
                "format": parser.format_name,
                "extensions": parser.supported_extensions,
                "mime_types": parser.mime_types,
            }
        )

    renderers_info = []
    for renderer in registry.list_renderers():
        renderers_info.append(
            {
                "format": renderer.format_name,
                "extension": renderer.output_extension,
                "mime_type": renderer.mime_type,
            }
        )

    # Get conversion matrix
    from .core.engine import DocumentConverter

    temp_converter = DocumentConverter(registry)
    matrix = temp_converter.list_supported_conversions()

    response = {
        "parsers": parsers_info,
        "renderers": renderers_info,
        "conversion_matrix": matrix,
        "summary": {
            "total_source_formats": len(parsers_info),
            "total_target_formats": len(renderers_info),
            "possible_conversions": len(parsers_info) * len(renderers_info),
        },
    }

    return [TextContent(type="text", text=json.dumps(response, ensure_ascii=False, indent=2))]


async def _handle_can_convert(
    converter: DocumentConverter, arguments: Dict[str, Any]
) -> List[TextContent]:
    """Handle check conversion feasibility request"""
    source_format = arguments.get("source_format")
    target_format = arguments.get("target_format")

    if not source_format or not target_format:
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {"error": "Missing required parameters: source_format and target_format"},
                    ensure_ascii=False,
                    indent=2,
                ),
            )
        ]

    can_convert = converter.can_convert(source_format, target_format)

    response = {
        "source_format": source_format,
        "target_format": target_format,
        "can_convert": can_convert,
        "message": f"{'Supported' if can_convert else 'Not supported'}: {source_format} to {target_format}",
    }

    return [TextContent(type="text", text=json.dumps(response, ensure_ascii=False, indent=2))]


async def main():
    """Main entry function"""
    server = create_server()

    # Use new MCP API
    from mcp.server.stdio import stdio_server as mcp_stdio_server

    async with mcp_stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main_sync():
    """Synchronous entry function"""
    import asyncio

    asyncio.run(main())


if __name__ == "__main__":
    main_sync()
