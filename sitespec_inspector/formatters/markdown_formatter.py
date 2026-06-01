"""
Markdown报告格式化器
"""

from datetime import datetime
from ..models import InspectionReport, Severity


class MarkdownFormatter:
    """Markdown报告格式化器"""

    def format(self, report: InspectionReport) -> str:
        """格式化报告为Markdown"""
        md = f"""# 🔍 SiteSpec Inspector 检测报告

## 📊 检测总览

| 项目 | 值 |
|------|-----|
| **检测URL** | {report.url} |
| **检测时间** | {datetime.fromtimestamp(report.timestamp).strftime("%Y-%m-%d %H:%M:%S")} |
| **检测耗时** | {report.duration:.2f}秒 |
| **综合评分** | {self._get_score_badge(report.total_score)} |
| **错误数** | {report.error_count} ❌ |
| **警告数** | {report.warning_count} ⚠️ |

---

## 📋 详细检测结果

"""

        # 各模块详情
        for name, result in report.results.items():
            md += self._render_module(name, result)

        # 页脚
        md += f"""
---

*报告生成时间: {datetime.fromtimestamp(report.timestamp).strftime("%Y-%m-%d %H:%M:%S")}*  
*SiteSpec Inspector v1.0.0*
"""

        return md

    def _get_score_badge(self, score: float) -> str:
        """获取评分徽章"""
        if score >= 90:
            return f"🟢 **{score:.1f}**/100 (优秀)"
        elif score >= 70:
            return f"🟡 **{score:.1f}**/100 (良好)"
        else:
            return f"🔴 **{score:.1f}**/100 (需改进)"

    def _render_module(self, name: str, result) -> str:
        """渲染模块详情"""
        score_badge = self._get_score_badge(result.score)

        md = f"""### {name} - {score_badge}

"""

        if not result.issues:
            md += "✅ **所有检查项通过**\n\n"
        else:
            md += "| 级别 | 代码 | 问题 | 建议 |\n"
            md += "|------|------|------|------|\n"

            for issue in result.issues:
                severity_icon = {
                    Severity.ERROR: "🔴 错误",
                    Severity.WARNING: "🟡 警告",
                    Severity.INFO: "🔵 信息",
                }.get(issue.severity, "⚪")

                suggestion = issue.suggestion or "-"
                if issue.reference:
                    suggestion += f" [参考]({issue.reference})"

                # 转义管道符
                message = issue.message.replace("|", "\\|")
                suggestion = suggestion.replace("|", "\\|")

                md += f"| {severity_icon} | `{issue.code}` | {message} | {suggestion} |\n"

            md += "\n"

        # 指标
        if result.metrics:
            md += "**指标统计:**\n\n"
            for key, value in result.metrics.items():
                md += f"- {key}: `{value}`\n"
            md += "\n"

        md += "---\n\n"
        return md