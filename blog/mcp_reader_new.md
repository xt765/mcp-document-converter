# 我开发了一个 MCP 文档读取工具，让 AI 轻松提取多格式文档内容

> **GitHub**: [https://github.com/xt765/mcp_documents_reader](https://github.com/xt765/mcp_documents_reader)  
> **Gitee（国内镜像）**: [https://gitee.com/xt765/mcp_documents_reader](https://gitee.com/xt765/mcp_documents_reader)

大家好，我是玄同765（xt765）。作为一名大语言模型开发工程师，我在日常工作中经常遇到这样的困扰：**如何让 AI 智能体直接读取各种格式的文档？**

比如，项目文档有 DOCX、PDF、Excel 多种格式，每次都要手动复制粘贴纯文本到智能体；Excel 文件有多个工作表，要逐个复制内容，效率极低；大 PDF/DOCX 文件复制到智能体时，格式混乱还容易卡死。

这让我萌生了一个想法：**开发一个能让 AI 直接调用、支持多格式文档读取的 MCP 工具**。

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
| **办公文档** | DOCX | Microsoft Word 格式，办公必备 |
| **办公文档** | Excel (XLSX/XLS) | 支持多工作表，数据处理利器 |
| **技术文档** | PDF | 通用文档格式，适合打印和分享 |
| **文本文件** | TXT | 纯文本，最通用的格式 |

无需切换多个工具，一个 `mcp_documents_reader` 就能搞定所有主流文档格式的纯文本提取。

### 2. 统一调用接口

不管是哪种格式，都可以通过同一个接口调用，智能体无需区分格式，降低使用成本。

### 3. 大文件优化

针对大体积文档（如 100MB+ 的 PDF、10 万行+ 的 Excel），工具会自动分段读取，避免内存溢出，保证运行流畅。

### 4. 双仓库支持

提供 GitHub+Gitee 双仓库，国内用户可通过 Gitee 快速克隆和安装，解决网络访问慢的问题。

## 如何快速使用？

### 前置依赖

* **Trae IDE 版本**：≥v1.2.0（支持 MCP 协议）
* **Python 环境**：≥3.8
* **uv 包管理器**（推荐）

### 安装方式

#### 方式 1：uvx 一键启动（推荐，无需克隆仓库）

```bash
# GitHub源
uvx --from git+https://github.com/xt765/mcp_documents_reader mcp_documents_reader

# 国内用户推荐Gitee源
uvx --from git+https://gitee.com/xt765/mcp_documents_reader mcp_documents_reader
```

启动成功后，工具默认运行在 `http://localhost:8080/mcp`。

#### 方式 2：本地克隆安装

```bash
# GitHub克隆
git clone https://github.com/xt765/mcp_documents_reader.git

# 国内用户推荐Gitee克隆
git clone https://gitee.com/xt765/mcp_documents_reader.git

cd mcp_documents_reader
# 安装依赖
pip install python-docx PyPDF2 openpyxl
# 启动工具
python mcp_documents_reader.py
```

### 在 Trae IDE 中配置

将以下内容添加到 Trae IDE 的 MCP 配置中：

**Github源：**

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

**Gitee源：**

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

### 环境变量配置

可通过环境变量指定文档存储目录（默认：`./documents`）：

```bash
# macOS/Linux
export DOCUMENT_DIRECTORY="/path/to/your/documents"

# Windows（PowerShell）
$env:DOCUMENT_DIRECTORY="C:\path\to\your\documents"
```

## 实际使用示例

### 示例 1：统一接口调用（推荐）

无需指定格式，工具自动识别文档类型并提取纯文本：

```
帮我读取本地的《2024年销售数据.xlsx》，提取所有文本内容并总结核心信息。
```

**工具执行说明**：Excel 文件会合并所有工作表的纯文本内容，返回给智能体进行总结。

### 示例 2：单独格式接口调用

如果需要明确指定格式，可调用对应接口：

```
帮我用read_pdf工具读取本地的《技术架构手册.pdf》，提取文本后分析核心组件。
```

### 示例 3：各格式提取说明

| 格式  | 提取逻辑说明               |
| ----- | -------------------------- |
| Excel | 合并所有工作表的纯文本内容 |
| DOCX  | 提取文档所有段落的纯文本   |
| PDF   | 提取所有页面的纯文本内容   |
| TXT   | 直接返回文件纯文本         |

## 实际应用场景

这个工具在我的日常工作中已经帮了大忙：

### 场景 1：Excel 销售数据快速总结

**智能体指令**：

```
帮我读取本地的《2024年销售数据.xlsx》，提取文本后总结各地区的销售总额情况。
```

**预期输出**：

```
### 2024年销售数据总结
1. 华东区销售总额为1250.8万元，占比35%；
2. 华南区销售总额为980.5万元，占比27%；
3. 华北区销售总额为760.2万元，占比21%；
4. 西南区销售总额为520.1万元，占比14%；
5. 西北区销售总额为110.4万元，占比3%。
```

### 场景 2：DOCX 需求文档快速梳理

**智能体指令**：

```
帮我读取本地的《项目需求文档.docx》，提取文本后总结核心功能模块。
```

**预期输出**：

```
### 项目核心功能模块总结
项目包含三大核心模块：
1. 用户管理模块：支持用户注册、登录、信息修改、密码找回；
2. 订单管理模块：支持订单创建、支付、查询、取消；
3. 支付管理模块：支持微信支付、支付宝支付、银行卡支付三种方式。
```

### 场景 3：PDF 技术手册快速提取

**智能体指令**：

```
帮我读取本地的《技术架构手册.pdf》，提取文本后列出微服务核心组件。
```

**预期输出**：

```
### 微服务核心组件列表
1. API网关
2. 用户服务
3. 订单服务
4. 库存服务
5. 配置中心
6. 日志中心
```

## 当前限制与未来规划

### 当前功能限制

目前工具处于轻量版阶段，暂不支持以下功能：

* 保留 Excel 表格结构、多工作表单独提取、单元格格式识别
* 保留 DOCX 标题层级、段落格式
* 提取 PDF 页码范围、表格结构
* 多模态内容（如图片、公式）识别

### 未来规划

后续版本将逐步开发以下功能：

- [ ] 支持 Excel 表格结构提取、多工作表单独读取
- [ ] 支持 DOCX 标题层级、段落格式保留
- [ ] 支持 PDF 页码范围选择、表格结构提取
- [ ] 支持 PPT 格式文本提取
- [ ] 优化大文件读取性能，支持断点续读

## 邀请你一起参与

mcp_documents_reader 是一个开源项目，我非常欢迎社区贡献：

- **提交 Issue**: 如果你发现了 Bug 或有功能建议
- **提交 PR**: 贡献代码，修复问题或添加新功能
- **分享使用经验**: 帮助改进文档和示例

**项目地址**：
- GitHub: [https://github.com/xt765/mcp_documents_reader](https://github.com/xt765/mcp_documents_reader)
- Gitee（国内镜像）: [https://gitee.com/xt765/mcp_documents_reader](https://gitee.com/xt765/mcp_documents_reader)

## 写在最后

开发 mcp_documents_reader 的初衷很简单：**让 AI 智能体能轻松处理各种格式的文档**。

在 AI 时代，我们不应该被文档格式所束缚。无论是开发者、数据分析师还是办公人员，只要需要让 AI 读取文档内容，这个工具都能为你节省大量时间和精力。

如果你也觉得这个工具有用，请在 GitHub 上给我一个 ⭐️ Star，这是对我最大的鼓励！

**立即体验**:
- [GitHub](https://github.com/xt765/mcp_documents_reader)
- [Gitee（国内镜像）](https://gitee.com/xt765/mcp_documents_reader)

---

*我是玄同765（xt765），一个热爱开源和 AI 的开发者。欢迎与我交流！*
