<div align="center">

# 🔍 SiteSpec-Inspector

**轻量级网站规范检测工具**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)

[English](#english) | [简体中文](#简体中文) | [繁體中文](#繁體中文)

</div>

---

<a name="简体中文"></a>
## 🎉 项目介绍

SiteSpec-Inspector 是一款轻量级网站规范检测工具，帮助开发者和网站管理员快速检测网站的 **HTML结构**、**SEO优化**、**无障碍访问(Accessibility)**、**安全性(Security)**、**性能(Performance)** 以及 **Well-Known URIs** 等Web标准合规性。

### ✨ 灵感来源

本项目灵感来源于 [specification.website](https://github.com/jdevalk/specification.website) - 一个优秀的网站规范文档项目。与其不同，SiteSpec-Inspector 专注于**自动化检测**，将规范转化为可执行的工具，帮助开发者快速发现并修复网站问题。

### 🎯 核心价值

- 🚀 **快速检测** - 一键检测网站多项规范指标
- 📊 **全面报告** - 生成详细的检测报告，包含问题定位与修复建议
- 🔧 **易于集成** - 支持CLI命令行，可集成到CI/CD流程
- 🌍 **多格式输出** - 支持Console、JSON、HTML、Markdown多种输出格式

---

## ✨ 核心特性

| 检测模块 | 描述 | 检测项 |
|---------|------|--------|
| 🏗️ **HTML结构** | 检测HTML文档结构合规性 | DOCTYPE、meta标签、标题、语言属性、视口设置 |
| 🔍 **SEO优化** | 检测搜索引擎优化相关标签 | Title、Description、Canonical、Open Graph、结构化数据 |
| ♿ **无障碍访问** | 基于WCAG 2.1标准检测 | 图片alt属性、表单标签、标题层级、ARIA使用 |
| 🔒 **安全性** | 检测安全响应头和配置 | CSP、HSTS、X-Frame-Options、HTTPS、混合内容 |
| ⚡ **性能** | 检测页面性能指标 | 页面大小、响应时间、资源数量、缓存策略 |
| 📋 **Well-Known** | 检测标准定义的文件 | robots.txt、security.txt、sitemap.xml、favicon.ico |

### 🌟 差异化亮点

- **智能评分系统** - 综合评分机制，直观展示网站健康度
- **详细修复建议** - 每个问题都附带具体的修复建议和参考链接
- **模块化设计** - 可灵活启用/禁用特定检测模块
- **轻量高效** - 零依赖（除Python标准库外），执行速度快

---

## 🚀 快速开始

### 环境要求

- **Python**: 3.8 或更高版本
- **操作系统**: Windows、macOS、Linux

### 安装

#### 方式一：通过 pip 安装（推荐）

```bash
pip install sitespec-inspector
```

#### 方式二：从源码安装

```bash
git clone https://github.com/gitstq/SiteSpec-Inspector.git
cd SiteSpec-Inspector
pip install -e .
```

### 基本使用

#### 检测单个网站

```bash
# 基础检测
sitespec inspect https://example.com

# 生成HTML报告
sitespec inspect https://example.com --output html --output-file report.html

# 仅显示失败项
sitespec inspect https://example.com --only-failed

# 跳过特定检测模块
sitespec inspect https://example.com --no-perf --no-wellknown
```

#### 生成配置文件

```bash
sitespec init-config --output sitespec-config.yaml
```

---

## 📖 详细使用指南

### 命令行参数

```
Usage: sitespec inspect [OPTIONS] URL

Arguments:
  URL    要检测的网站地址

Options:
  -c, --config PATH          配置文件路径
  -o, --output [console|json|html|markdown]  输出格式
  -f, --output-file PATH     输出文件路径
  -t, --timeout INTEGER      请求超时时间(秒) [default: 30]
  --no-html                  跳过HTML结构检测
  --no-seo                   跳过SEO检测
  --no-a11y                  跳过无障碍检测
  --no-security              跳过安全检测
  --no-perf                  跳过性能检测
  --no-wellknown             跳过Well-Known URIs检测
  -v, --verbose              显示详细信息
  --only-failed              仅显示失败项
  --help                     显示帮助信息
```

### 配置文件示例

```yaml
# SiteSpec-Inspector 配置文件

# 基础配置
timeout: 30
follow_redirects: true
verify_ssl: true
user_agent: "SiteSpec-Inspector/1.0.0"

# 检测模块开关
check_html: true
check_seo: true
check_accessibility: true
check_security: true
check_performance: true
check_well_known: true

# 阈值配置
min_title_length: 10
max_title_length: 60
min_description_length: 50
max_description_length: 160
max_image_size_kb: 500
max_page_size_kb: 2048
```

### 典型使用场景

#### 场景1：开发阶段本地测试

```bash
# 检测本地开发服务器
sitespec inspect http://localhost:3000 --verbose
```

#### 场景2：CI/CD集成

```yaml
# .github/workflows/sitespec.yml
name: SiteSpec Check
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install SiteSpec
        run: pip install sitespec-inspector
      - name: Run SiteSpec
        run: sitespec inspect https://your-site.com --output json --only-failed
```

#### 场景3：生成专业报告

```bash
# 生成HTML报告用于分享
sitespec inspect https://example.com --output html --output-file report.html

# 生成Markdown报告用于文档
sitespec inspect https://example.com --output markdown --output-file report.md
```

---

## 💡 设计思路与迭代规划

### 设计理念

1. **简单易用** - 一条命令即可完成检测
2. **全面覆盖** - 涵盖网站规范的各个维度
3. **可扩展性** - 模块化架构，易于添加新的检测规则
4. **开发者友好** - 详细的错误信息和修复建议

### 技术选型

- **Python 3.8+** - 主流编程语言，生态丰富
- **BeautifulSoup4** - HTML解析，灵活高效
- **Click** - CLI框架，命令行体验优秀
- **Rich** - 终端输出美化，提升用户体验

### 后续功能迭代计划

- [ ] 支持批量检测多个URL
- [ ] 添加更多SEO检测规则（如Core Web Vitals）
- [ ] 支持自定义检测规则
- [ ] 添加历史记录和趋势分析
- [ ] 支持导出为PDF报告
- [ ] 添加API服务模式

### 社区贡献方向

- 提交新的检测规则
- 完善多语言支持
- 分享使用案例
- 报告Bug和功能建议

---

## 📦 打包与部署指南

### 本地开发

```bash
# 克隆仓库
git clone https://github.com/gitstq/SiteSpec-Inspector.git
cd SiteSpec-Inspector

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
black sitespec_inspector
```

### 发布到PyPI

```bash
# 构建包
python -m build

# 上传到PyPI
python -m twine upload dist/*
```

---

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 提交PR

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: 添加某个特性'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 提交规范

- `feat:` 新功能
- `fix:` 修复问题
- `docs:` 文档更新
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建/工具相关

---

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

---

<a name="english"></a>
## 🎉 Introduction (English)

SiteSpec-Inspector is a lightweight website specification inspection tool that helps developers and site administrators quickly detect **HTML structure**, **SEO optimization**, **Accessibility**, **Security**, **Performance**, and **Well-Known URIs** compliance.

### ✨ Key Features

- 🚀 **Fast Inspection** - One-click detection of multiple website specification metrics
- 📊 **Comprehensive Reports** - Detailed inspection reports with problem location and fix suggestions
- 🔧 **Easy Integration** - CLI support, integrable into CI/CD workflows
- 🌍 **Multiple Output Formats** - Console, JSON, HTML, Markdown

### 🚀 Quick Start

```bash
# Install
pip install sitespec-inspector

# Basic inspection
sitespec inspect https://example.com

# Generate HTML report
sitespec inspect https://example.com --output html --output-file report.html
```

---

<a name="繁體中文"></a>
## 🎉 專案介紹 (繁體中文)

SiteSpec-Inspector 是一款輕量級網站規範檢測工具，幫助開發者和網站管理員快速檢測網站的 **HTML結構**、**SEO優化**、**無障礙訪問**、**安全性**、**效能** 以及 **Well-Known URIs** 等Web標準合規性。

### 🚀 快速開始

```bash
# 安裝
pip install sitespec-inspector

# 基礎檢測
sitespec inspect https://example.com

# 生成HTML報告
sitespec inspect https://example.com --output html --output-file report.html
```

---

<div align="center">

**Made with ❤️ by gitstq**

[⭐ Star us on GitHub](https://github.com/gitstq/SiteSpec-Inspector) | [🐛 Report Bug](https://github.com/gitstq/SiteSpec-Inspector/issues)

</div>