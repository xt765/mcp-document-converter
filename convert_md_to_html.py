#!/usr/bin/env python3
"""
Markdown 转 HTML 转换器
支持代码高亮、表格样式等
"""

import markdown
from markdown.extensions import fenced_code, tables, toc
import os

def convert_md_to_html(md_file_path, output_html_path=None):
    """
    将 Markdown 文件转换为 HTML
    
    Args:
        md_file_path: Markdown 文件路径
        output_html_path: 输出 HTML 文件路径，默认为同名 .html 文件
    """
    
    # 如果未指定输出路径，使用同名 .html 文件
    if output_html_path is None:
        output_html_path = os.path.splitext(md_file_path)[0] + '.html'
    
    # 读取 Markdown 文件
    with open(md_file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # 配置 Markdown 扩展
    md = markdown.Markdown(extensions=[
        'fenced_code',      # 代码块支持
        'tables',           # 表格支持
        'toc',              # 目录支持
        'nl2br',            # 换行转 <br>
    ])
    
    # 转换 Markdown 为 HTML
    html_body = md.convert(md_content)
    
    # 构建完整的 HTML 文档
    html_template = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{os.path.basename(md_file_path).replace('.md', '')}</title>
    <style>
        /* 基础样式 */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.8;
            color: #333;
            background-color: #f5f5f5;
            padding: 20px;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        /* 标题样式 */
        h1 {{
            font-size: 2.2em;
            color: #2c3e50;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 3px solid #3498db;
        }}
        
        h2 {{
            font-size: 1.8em;
            color: #34495e;
            margin-top: 30px;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #ecf0f1;
        }}
        
        h3 {{
            font-size: 1.4em;
            color: #34495e;
            margin-top: 25px;
            margin-bottom: 12px;
        }}
        
        h4 {{
            font-size: 1.2em;
            color: #555;
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        
        /* 段落和文本 */
        p {{
            margin-bottom: 15px;
            text-align: justify;
        }}
        
        strong {{
            color: #2c3e50;
            font-weight: 600;
        }}
        
        em {{
            color: #666;
        }}
        
        /* 链接 */
        a {{
            color: #3498db;
            text-decoration: none;
            transition: color 0.3s;
        }}
        
        a:hover {{
            color: #2980b9;
            text-decoration: underline;
        }}
        
        /* 代码块 */
        pre {{
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 20px;
            border-radius: 6px;
            overflow-x: auto;
            margin: 20px 0;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.5;
        }}
        
        code {{
            background: #f4f4f4;
            color: #c7254e;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
        }}
        
        pre code {{
            background: transparent;
            color: #f8f8f2;
            padding: 0;
        }}
        
        /* 行内代码 */
        p code, li code {{
            background: #f8f8f8;
            border: 1px solid #e0e0e0;
        }}
        
        /* 表格 */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
        }}
        
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border: 1px solid #ddd;
        }}
        
        th {{
            background: #3498db;
            color: white;
            font-weight: 600;
        }}
        
        tr:nth-child(even) {{
            background: #f8f9fa;
        }}
        
        tr:hover {{
            background: #e8f4f8;
        }}
        
        /* 列表 */
        ul, ol {{
            margin: 15px 0;
            padding-left: 30px;
        }}
        
        li {{
            margin-bottom: 8px;
        }}
        
        /* 引用块 */
        blockquote {{
            border-left: 4px solid #3498db;
            padding: 15px 20px;
            margin: 20px 0;
            background: #f8f9fa;
            font-style: italic;
            color: #555;
        }}
        
        /* 分隔线 */
        hr {{
            border: none;
            height: 2px;
            background: linear-gradient(to right, #3498db, #2ecc71);
            margin: 30px 0;
        }}
        
        /* 图片 */
        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 20px auto;
            border-radius: 6px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        /* 目录 */
        .toc {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            margin: 20px 0;
            border: 1px solid #e0e0e0;
        }}
        
        .toc ul {{
            list-style: none;
            padding-left: 0;
        }}
        
        .toc li {{
            margin: 5px 0;
        }}
        
        .toc a {{
            color: #3498db;
        }}
        
        /* 打印样式 */
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            
            .container {{
                box-shadow: none;
                max-width: 100%;
            }}
        }}
        
        /* 响应式 */
        @media (max-width: 768px) {{
            body {{
                padding: 10px;
            }}
            
            .container {{
                padding: 20px;
            }}
            
            h1 {{
                font-size: 1.8em;
            }}
            
            h2 {{
                font-size: 1.5em;
            }}
            
            pre {{
                padding: 15px;
                font-size: 13px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
{html_body}
    </div>
</body>
</html>'''
    
    # 写入 HTML 文件
    with open(output_html_path, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print(f"✅ 转换成功！")
    print(f"   输入文件: {md_file_path}")
    print(f"   输出文件: {output_html_path}")
    
    return output_html_path


if __name__ == "__main__":
    import sys
    
    # 转换 TRAE 8 大智能体博客
    md_files = [
        r"d:\TraeProjects\langchain_code_comment\bolg\TRAE_8_Custom_Agents_Final.md",
        r"d:\TraeProjects\langchain_code_comment\bolg\LangChain_v1.0_Middleware_Guide.md",
        r"d:\TraeProjects\langchain_code_comment\bolg\TRAE_AI_Ecosystem_Technical_Blog.md",
    ]
    
    for md_file in md_files:
        if os.path.exists(md_file):
            try:
                convert_md_to_html(md_file)
                print()
            except Exception as e:
                print(f"❌ 转换失败 {md_file}: {e}\n")
        else:
            print(f"⚠️ 文件不存在: {md_file}\n")
