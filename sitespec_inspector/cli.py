#!/usr/bin/env python3
"""
命令行接口
"""

import sys
import json
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from typing import List, Optional

from . import Inspector, Config
from .formatters import ConsoleFormatter, JsonFormatter, HtmlFormatter, MarkdownFormatter

console = Console()


def print_banner():
    """打印程序横幅"""
    banner = """
╭──────────────────────────────────────────────────────────────╮
│                                                              │
│   🔍 SiteSpec-Inspector                                      │
│   轻量级网站规范检测工具                                      │
│                                                              │
╰──────────────────────────────────────────────────────────────╯
    """
    console.print(banner, style="cyan")


@click.command()
@click.argument("url")
@click.option("--config", "-c", type=click.Path(exists=True), help="配置文件路径")
@click.option("--output", "-o", type=click.Choice(["console", "json", "html", "markdown"]),
              default="console", help="输出格式")
@click.option("--output-file", "-f", type=click.Path(), help="输出文件路径")
@click.option("--timeout", "-t", default=30, help="请求超时时间(秒)")
@click.option("--no-html", is_flag=True, help="跳过HTML结构检测")
@click.option("--no-seo", is_flag=True, help="跳过SEO检测")
@click.option("--no-a11y", is_flag=True, help="跳过无障碍检测")
@click.option("--no-security", is_flag=True, help="跳过安全检测")
@click.option("--no-perf", is_flag=True, help="跳过性能检测")
@click.option("--no-wellknown", is_flag=True, help="跳过Well-Known URIs检测")
@click.option("--verbose", "-v", is_flag=True, help="显示详细信息")
@click.option("--only-failed", is_flag=True, help="仅显示失败项")
def inspect(url: str, config: Optional[str], output: str, output_file: Optional[str],
            timeout: int, no_html: bool, no_seo: bool, no_a11y: bool,
            no_security: bool, no_perf: bool, no_wellknown: bool,
            verbose: bool, only_failed: bool):
    """
    检测网站规范合规性

    URL: 要检测的网站地址
    """
    print_banner()

    # 加载配置
    if config:
        cfg = Config.from_file(config)
    else:
        cfg = Config()

    # 应用命令行选项
    cfg.timeout = timeout
    cfg.output_format = output
    cfg.verbose = verbose
    cfg.show_passed = not only_failed
    cfg.check_html = not no_html
    cfg.check_seo = not no_seo
    cfg.check_accessibility = not no_a11y
    cfg.check_security = not no_security
    cfg.check_performance = not no_perf
    cfg.check_well_known = not no_wellknown

    # 显示检测配置
    console.print(f"[bold]目标URL:[/bold] {url}")
    console.print(f"[bold]检测模块:[/bold] ", end="")
    modules = []
    if cfg.check_html:
        modules.append("HTML")
    if cfg.check_seo:
        modules.append("SEO")
    if cfg.check_accessibility:
        modules.append("Accessibility")
    if cfg.check_security:
        modules.append("Security")
    if cfg.check_performance:
        modules.append("Performance")
    if cfg.check_well_known:
        modules.append("Well-Known")
    console.print(", ".join(modules))
    console.print()

    # 执行检测
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task("正在检测网站...", total=None)

        inspector = Inspector(cfg)
        report = inspector.inspect(url)

        progress.update(task, completed=True)

    # 格式化输出
    if output == "console":
        formatter = ConsoleFormatter(console)
        output_content = formatter.format(report)
    elif output == "json":
        formatter = JsonFormatter()
        output_content = formatter.format(report)
    elif output == "html":
        formatter = HtmlFormatter()
        output_content = formatter.format(report)
    elif output == "markdown":
        formatter = MarkdownFormatter()
        output_content = formatter.format(report)

    # 输出到文件或控制台
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(output_content)
        console.print(f"\n[green]✓[/green] 报告已保存到: {output_file}")
    elif output != "console":
        console.print(output_content)

    # 返回退出码
    sys.exit(0 if report.error_count == 0 else 1)


@click.command()
@click.option("--output", "-o", type=click.Path(), default="sitespec-config.yaml",
              help="输出文件路径")
def init_config(output: str):
    """生成默认配置文件"""
    default_config = """# SiteSpec-Inspector 配置文件

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

# 输出配置
output_format: "console"
verbose: false
show_passed: true
"""
    with open(output, "w", encoding="utf-8") as f:
        f.write(default_config)
    console.print(f"[green]✓[/green] 配置文件已生成: {output}")


@click.group()
def main():
    """SiteSpec-Inspector - 轻量级网站规范检测工具"""
    pass


main.add_command(inspect)
main.add_command(init_config)

if __name__ == "__main__":
    main()