"""
MCP 服务器 - 提供文档转换的 MCP 工具接口
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    TextContent,
    Tool,
)

from .core.engine import DocumentConverter, ConversionResult
from .registry import get_registry
from .parsers import (
    MarkdownParser,
    HTMLParser,
    DOCXParser,
    PDFParser,
    TextParser,
)
from .renderers import (
    HTMLRenderer,
    MarkdownRenderer,
    DOCXRenderer,
    PDFRenderer,
    TextRenderer,
)


def create_server() -> Server:
    """创建并配置 MCP 服务器"""
    
    # 注册所有解析器和渲染器
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
    
    # 创建转换器
    converter = DocumentConverter(registry)
    
    # 创建 MCP 服务器
    server = Server("mcp-document-converter")
    
    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """列出所有可用的工具"""
        return [
            Tool(
                name="convert_document",
                description="将文档从一种格式转换为另一种格式。支持 Markdown、HTML、DOCX、PDF、Text 等格式之间的相互转换。",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "source_path": {
                            "type": "string",
                            "description": "源文件路径，支持绝对路径或相对路径"
                        },
                        "target_format": {
                            "type": "string",
                            "description": "目标格式",
                            "enum": ["html", "pdf", "markdown", "docx", "text"]
                        },
                        "output_path": {
                            "type": "string",
                            "description": "输出文件路径（可选，默认使用源文件名）"
                        },
                        "source_format": {
                            "type": "string",
                            "description": "源格式（可选，自动检测文件扩展名）",
                            "enum": ["markdown", "html", "docx", "pdf", "text"]
                        },
                        "options": {
                            "type": "object",
                            "description": "转换选项",
                            "properties": {
                                "template": {
                                    "type": "string",
                                    "description": "模板名称"
                                },
                                "css": {
                                    "type": "string",
                                    "description": "自定义 CSS 样式"
                                },
                                "preserve_metadata": {
                                    "type": "boolean",
                                    "description": "是否保留元数据",
                                    "default": True
                                },
                                "extract_images": {
                                    "type": "boolean",
                                    "description": "是否提取图片",
                                    "default": True
                                }
                            }
                        }
                    },
                    "required": ["source_path", "target_format"]
                }
            ),
            Tool(
                name="list_supported_formats",
                description="列出所有支持的文档格式及其转换能力",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="get_conversion_matrix",
                description="获取完整的格式转换矩阵，显示哪些格式可以转换为哪些格式",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="can_convert",
                description="检查是否支持从源格式转换到目标格式",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "source_format": {
                            "type": "string",
                            "description": "源格式",
                            "enum": ["markdown", "html", "docx", "pdf", "text"]
                        },
                        "target_format": {
                            "type": "string",
                            "description": "目标格式",
                            "enum": ["html", "pdf", "markdown", "docx", "text"]
                        }
                    },
                    "required": ["source_format", "target_format"]
                }
            ),
            Tool(
                name="get_format_info",
                description="获取特定格式的详细信息",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "format": {
                            "type": "string",
                            "description": "格式名称",
                            "enum": ["markdown", "html", "docx", "pdf", "text"]
                        }
                    },
                    "required": ["format"]
                }
            ),
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """调用工具"""
        
        if name == "convert_document":
            return await _handle_convert_document(converter, arguments)
        
        elif name == "list_supported_formats":
            return await _handle_list_supported_formats(registry)
        
        elif name == "get_conversion_matrix":
            return await _handle_get_conversion_matrix(converter)
        
        elif name == "can_convert":
            return await _handle_can_convert(converter, arguments)
        
        elif name == "get_format_info":
            return await _handle_get_format_info(registry, arguments)
        
        else:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": f"未知工具: {name}"
                }, ensure_ascii=False, indent=2)
            )]
    
    return server


async def _handle_convert_document(converter: DocumentConverter, arguments: Dict[str, Any]) -> List[TextContent]:
    """处理文档转换请求"""
    source_path = arguments.get("source_path")
    target_format = arguments.get("target_format")
    output_path = arguments.get("output_path")
    source_format = arguments.get("source_format")
    options = arguments.get("options", {})
    
    if not source_path or not target_format:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": "缺少必需参数: source_path 和 target_format"
            }, ensure_ascii=False, indent=2)
        )]
    
    # 执行转换
    result = converter.convert(
        source=source_path,
        target_format=target_format,
        output_path=output_path,
        source_format=source_format,
        options=options
    )
    
    if result.success:
        response = {
            "success": True,
            "message": f"✅ 转换成功！",
            "source_path": source_path,
            "output_path": str(result.output_path) if result.output_path else None,
            "target_format": target_format,
            "metadata": result.metadata
        }
    else:
        response = {
            "success": False,
            "error": result.error_message,
            "source_path": source_path,
            "target_format": target_format
        }
    
    return [TextContent(
        type="text",
        text=json.dumps(response, ensure_ascii=False, indent=2)
    )]


async def _handle_list_supported_formats(registry) -> List[TextContent]:
    """处理列出支持格式请求"""
    formats = registry.list_supported_formats()
    
    # 获取解析器和渲染器的详细信息
    parsers_info = []
    for parser in registry.list_parsers():
        parsers_info.append({
            "format": parser.format_name,
            "extensions": parser.supported_extensions,
            "mime_types": parser.mime_types
        })
    
    renderers_info = []
    for renderer in registry.list_renderers():
        renderers_info.append({
            "format": renderer.format_name,
            "extension": renderer.output_extension,
            "mime_type": renderer.mime_type
        })
    
    response = {
        "parsers": parsers_info,
        "renderers": renderers_info,
        "summary": {
            "total_source_formats": len(parsers_info),
            "total_target_formats": len(renderers_info),
            "possible_conversions": len(parsers_info) * len(renderers_info)
        }
    }
    
    return [TextContent(
        type="text",
        text=json.dumps(response, ensure_ascii=False, indent=2)
    )]


async def _handle_get_conversion_matrix(converter: DocumentConverter) -> List[TextContent]:
    """处理获取转换矩阵请求"""
    matrix = converter.list_supported_conversions()
    
    # 格式化矩阵为表格
    response = {
        "conversion_matrix": matrix,
        "description": "显示每种源格式可以转换到哪些目标格式"
    }
    
    return [TextContent(
        type="text",
        text=json.dumps(response, ensure_ascii=False, indent=2)
    )]


async def _handle_can_convert(converter: DocumentConverter, arguments: Dict[str, Any]) -> List[TextContent]:
    """处理检查转换可行性请求"""
    source_format = arguments.get("source_format")
    target_format = arguments.get("target_format")
    
    if not source_format or not target_format:
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": "缺少必需参数: source_format 和 target_format"
            }, ensure_ascii=False, indent=2)
        )]
    
    can_convert = converter.can_convert(source_format, target_format)
    
    response = {
        "source_format": source_format,
        "target_format": target_format,
        "can_convert": can_convert,
        "message": f"{'✅ 支持' if can_convert else '❌ 不支持'}从 {source_format} 转换到 {target_format}"
    }
    
    return [TextContent(
        type="text",
        text=json.dumps(response, ensure_ascii=False, indent=2)
    )]


async def _handle_get_format_info(registry, arguments: Dict[str, Any]) -> List[TextContent]:
    """处理获取格式信息请求"""
    format_name = arguments.get("format")
    
    if not format_name:
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": "缺少必需参数: format"
            }, ensure_ascii=False, indent=2)
        )]
    
    parser = registry.get_parser(format_name)
    renderer = registry.find_renderer(format_name)
    
    response = {
        "format": format_name,
        "can_parse": parser is not None,
        "can_render": renderer is not None,
    }
    
    if parser:
        response["parser_info"] = {
            "extensions": parser.supported_extensions,
            "mime_types": parser.mime_types
        }
    
    if renderer:
        response["renderer_info"] = {
            "extension": renderer.output_extension,
            "mime_type": renderer.mime_type,
            "is_binary": renderer.is_binary
        }
    
    return [TextContent(
        type="text",
        text=json.dumps(response, ensure_ascii=False, indent=2)
    )]


async def main():
    """主入口函数"""
    server = create_server()
    
    async with stdio_server(server) as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


def main_sync():
    """同步入口函数"""
    import asyncio
    asyncio.run(main())


if __name__ == "__main__":
    main_sync()
