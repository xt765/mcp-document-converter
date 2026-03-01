# 更新日志

本项目的所有重要变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [0.2.0] - 2025-03-01

### 新增

- **CI/CD 工作流**：添加 GitHub Actions 工作流用于自动化测试和发布
  - CI 工作流：Ruff、Basedpyright、Pytest
  - Release 工作流：发布到 PyPI 和 MCP Registry
  - 支持 Python 3.10-3.14

- **测试套件**：测试覆盖率提升至 89%
  - 361 个测试用例覆盖所有核心模块
  - 解析器、渲染器、转换器的单元测试
  - MCP 工具的集成测试

- **文档**：添加完整的文档结构
  - API 参考
  - 用户指南
  - 贡献指南

### 变更

- **类型检查**：从 MyPy 切换到 Basedpyright，获得更好的类型推断
- **代码格式化**：用 Ruff format 替代 Black
- **开发依赖**：更新开发工具链

### 修复

- **WeasyPrint 兼容性**：修复 Windows 环境下的导入处理
- **类型安全**：修复所有 Basedpyright 类型错误
- **代码质量**：修复所有 Ruff 代码检查问题

## [0.1.2] - 2025-02-28

### 新增

- **MCP 工具**：添加完整的 MCP 工具接口
  - `convert_document`：主转换工具
  - `list_supported_formats`：列出所有支持的格式
  - `get_conversion_matrix`：获取转换矩阵
  - `can_convert`：检查转换支持
  - `get_format_info`：获取格式信息

- **PDF 支持**：添加 PDF 解析和渲染功能
  - 从 PDF 文件提取文本
  - 使用 WeasyPrint 生成 PDF
  - 支持自定义模板

### 变更

- **架构**：改进插件架构，提高可扩展性
- **错误处理**：增强错误消息和异常处理

## [0.1.1] - 2025-02-27

### 新增

- **DOCX 支持**：添加 DOCX 解析和渲染
  - 样式保留
  - 表格支持
  - 图片提取

- **HTML 支持**：添加 HTML 解析和渲染
  - 语义标签解析
  - 代码语法高亮
  - 自定义 CSS 支持

### 修复

- **编码检测**：改进文本文件的自动编码检测
- **元数据保留**：修复转换过程中的元数据保留问题

## [0.1.0] - 2025-02-25

### 新增

- **首次发布**：MCP Document Converter 首次公开发布
  - 带中间表示的核心转换引擎
  - Markdown 解析器和渲染器
  - HTML 渲染器
  - Text 解析器和渲染器
  - 可扩展的插件架构
  - 支持 AI 助手的 MCP 协议

- **支持的格式**：
  - 输入：Markdown、HTML、DOCX、PDF、Text
  - 输出：Markdown、HTML、DOCX、PDF、Text

- **功能特性**：
  - 所有格式间的双向转换
  - 元数据保留
  - 图片提取和嵌入
  - 自定义样式支持
