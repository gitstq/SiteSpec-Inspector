"""
控制台格式化器
"""

from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich import box
from datetime import datetime

from ..models import InspectionReport, Severity


class ConsoleFormatter:
    """控制台输出格式化器"""

    def __init__(self, console):
        self.console = console

    def format(self, report: InspectionReport) -> str:
        """格式化报告为控制台输出"""
        # 总览面板
        self._print_summary(report)

        # 各模块详情
        for name, result in report.results.items():
            self._print_module_result(name, result)

        # 错误信息
        if report.errors:
            self._print_errors(report.errors)

        return ""

    def _print_summary(self, report: InspectionReport):
        """打印总览"""
        # 计算评分颜色
        score = report.total_score
        if score >= 90:
            score_color = "green"
            score_emoji = "🟢"
        elif score >= 70:
            score_color = "yellow"
            score_emoji = "🟡"
        else:
            score_color = "red"
            score_emoji = "🔴"

        # 创建总览表格
        summary_table = Table(show_header=False, box=box.SIMPLE)
        summary_table.add_column("Item", style="cyan")
        summary_table.add_column("Value", style="white")

        summary_table.add_row("检测URL", report.url)
        summary_table.add_row("检测时间", datetime.fromtimestamp(report.timestamp).strftime("%Y-%m-%d %H:%M:%S"))
        summary_table.add_row("检测耗时", f"{report.duration:.2f}秒")
        summary_table.add_row("综合评分", f"[{score_color}]{score_emoji} {score:.1f}/100[/{score_color}]")
        summary_table.add_row("问题统计", f"❌ {report.error_count} 个错误  |  ⚠️ {report.warning_count} 个警告")

        self.console.print(Panel(summary_table, title="[bold]📊 检测总览[/bold]", border_style="blue"))
        self.console.print()

    def _print_module_result(self, name: str, result):
        """打印模块结果"""
        # 计算评分颜色
        score = result.score
        if score >= 90:
            score_style = "green"
            icon = "✅"
        elif score >= 70:
            score_style = "yellow"
            icon = "⚠️"
        else:
            score_style = "red"
            icon = "❌"

        # 模块标题
        title = f"{icon} {name} - 得分: [{score_style}]{score:.1f}[/{score_style}]"

        # 如果没有问题，简化显示
        if not result.issues:
            self.console.print(f"[green]✓[/green] {name}: 所有检查项通过 (得分: 100.0)")
            return

        # 创建问题表格
        table = Table(box=box.SIMPLE)
        table.add_column("级别", width=6)
        table.add_column("代码", width=10)
        table.add_column("问题描述", min_width=40)
        table.add_column("建议", min_width=30)

        for issue in result.issues:
            severity_icon = {
                Severity.ERROR: "🔴",
                Severity.WARNING: "🟡",
                Severity.INFO: "🔵",
                Severity.PASSED: "🟢"
            }.get(issue.severity, "⚪")

            severity_style = {
                Severity.ERROR: "red",
                Severity.WARNING: "yellow",
                Severity.INFO: "blue",
                Severity.PASSED: "green"
            }.get(issue.severity, "white")

            suggestion = issue.suggestion or ""
            if issue.reference:
                suggestion += f"\n[dim]参考: {issue.reference}[/dim]"

            table.add_row(
                f"[{severity_style}]{severity_icon}[/{severity_style}]",
                issue.code,
                issue.message,
                suggestion
            )

        self.console.print(Panel(table, title=f"[bold]{title}[/bold]", border_style="blue"))
        self.console.print()

    def _print_errors(self, errors: dict):
        """打印错误信息"""
        self.console.print("[bold red]检测错误:[/bold red]")
        for module, error in errors.items():
            self.console.print(f"  ❌ {module}: {error}")
        self.console.print()