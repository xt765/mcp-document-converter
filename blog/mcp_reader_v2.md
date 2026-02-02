# 我开发了一个 MCP 文档读取工具，让 AI 轻松搞定多格式文档

> **GitHub**: [https://github.com/xt765/mcp_documents_reader](https://github.com/xt765/mcp_documents_reader)  
> **Gitee（国内镜像）**: [https://gitee.com/xt765/mcp_documents_reader](https://gitee.com/xt765/mcp_documents_reader)

大家好，我是玄同765（xt765）。作为一名大语言模型开发工程师，我每天都在和 AI 智能体打交道。但在使用过程中，我发现了一个让人头疼的问题：**如何让 AI 直接读取不同格式的文档？**

比如，项目文档有 DOCX、PDF、Excel 多种格式，每次都要手动复制粘贴纯文本到智能体；Excel 文件有多个工作表，要逐个复制内容，效率极低；大 PDF/DOCX 文件复制到智能体时，格式混乱还容易卡死；国内访问 GitHub 慢，想找个国内镜像仓库都没有。

这让我萌生了一个想法：**开发一个能让 AI 直接读取多格式文档的 MCP 工具**。

于是，**mcp_documents_reader** 诞生了。

## 为什么选择 MCP 协议？

在开发这个工具之前，我深入研究了 Anthropic 在 2024 年 11 月推出的 **MCP (Model Context Protocol，模型上下文协议)**。

MCP 的设计理念让我眼前一亮：它就像 USB 接口统一了各种外设连接一样，旨在用一套标准协议打通所有 AI 工具与外部系统的连接。简单来说，MCP 就是 AI 世界的"通用语言"。

任何支持 MCP 的 AI 助手（如 Trae IDE、Claude Desktop 等），都可以通过统一的接口调用外部工具的能力。这正是我想要的！

## 我设计的核心功能

### 1. 多格式统一支持

我选定了最常用的文档格式，覆盖绝大多数办公场景：

| 格式类型 | 支持格式 | 特点 |
|---------|---------|------|
| **办公文档** | DOCX、Excel (XLSX/XLS) | 支持多工作表合并读取 |
| **技术文档** | PDF、TXT | 支持大文件分段读取 |

无需切换多个工具，一个 `mcp_documents_reader` 就能搞定所有主流文档格式的纯文本提取。

### 2. 统一调用接口

不管是哪种格式，都可以通过同一个接口调用：

```python
# 统一接口，自动识别格式
read_document(file_path="report.xlsx")

# 或指定格式接口
read_excel(file_path="data.xlsx")
read_docx(file_path="document.docx")
read_pdf(file_path="manual.pdf")
```

智能体无需区分格式，降低使用成本。

### 3. 大文件优化

针对大体积文档（如 100MB+ 的 PDF、10 万行+ 的 Excel），工具会自动分段读取，避免内存溢出，保证运行流畅。

### 4. 双仓库支持

提供 GitHub+Gitee 双仓库，国内用户可通过 Gitee 快速克隆和安装：

- GitHub：[https://github.com/xt765/mcp_documents_reader](https://github.com/xt765/mcp_documents_reader)
- Gitee：[https://gitee.com/xt765/mcp_documents_reader](https://gitee.com/xt765/mcp_documents_reader)

## 快速开始

### 前置依赖

- **Trae IDE 版本**：≥v1.2.0（支持 MCP 协议）
- **Python 环境**：≥3.8
- **uv 包管理器**（推荐）

### 安装

#### 方式 1：uvx 一键启动（推荐）

```bash
# GitHub 源
uvx --from git+https://github.com/xt765/mcp_documents_reader mcp_documents_reader

# 国内用户推荐 Gitee 源
uvx --from git+https://gitee.com/xt765/mcp_documents_reader mcp_documents_reader
```

启动成功后，工具默认运行在 `http://localhost:8080/mcp`。

#### 方式 2：本地克隆安装

```bash
# GitHub 克隆
git clone https://github.com/xt765/mcp_documents_reader.git

# 国内用户推荐 Gitee 克隆
git clone https://gitee.com/xt765/mcp_documents_reader.git

cd mcp_documents_reader
# 安装依赖
pip install python-docx PyPDF2 openpyxl
# 启动工具
python mcp_documents_reader.py
```

### 在 Trae IDE 中配置

将以下内容添加到 Trae IDE 的 MCP 配置中：

**GitHub 源：**

```json
{
    "mcpServers": {
        "mcp-document-reader": {
            "command": "uvx",
            "args": [
                "--from",
                "git+https://github.com/xt765/mcp_documents_reader",
                "mcp_documents_reader"
            ]
        }
    }
}
```

**Gitee 源：**

```json
{
    "mcpServers": {
        "mcp-document-reader": {
            "command": "uvx",
            "args": [
                "--from",
                "git+https://gitee.com/xt765/mcp_documents_reader",
                "mcp_documents_reader"
            ]
        }
    }
}
```

配置完成后，AI 助手就可以直接调用文档读取工具了！

### 环境变量配置

可通过环境变量指定文档存储目录（默认：`./documents`）：

```bash
# macOS/Linux
export DOCUMENT_DIRECTORY="/path/to/your/documents"

# Windows（PowerShell）
$env:DOCUMENT_DIRECTORY="C:\path\to\your\documents"
```

## 实际使用示例
