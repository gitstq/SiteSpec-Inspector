"""
HTML报告格式化器
"""

from datetime import datetime
from ..models import InspectionReport, Severity


class HtmlFormatter:
    """HTML报告格式化器"""

    def format(self, report: InspectionReport) -> str:
        """格式化报告为HTML"""
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SiteSpec Inspector 检测报告 - {report.url}</title>
    <style>
        :root {{
            --color-bg: #f5f5f5;
            --color-card: #ffffff;
            --color-text: #333333;
            --color-primary: #2196F3;
            --color-success: #4CAF50;
            --color-warning: #FF9800;
            --color-error: #f44336;
            --color-info: #2196F3;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: var(--color-bg);
            color: var(--color-text);
            line-height: 1.6;
            padding: 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 12px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header .url {{ opacity: 0.9; font-size: 1.1em; }}
        .score-card {{
            background: var(--color-card);
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .score-circle {{
            width: 150px;
            height: 150px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
            font-size: 2.5em;
            font-weight: bold;
            color: white;
        }}
        .score-high {{ background: var(--color-success); }}
        .score-medium {{ background: var(--color-warning); }}
        .score-low {{ background: var(--color-error); }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .stat-item {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
        }}
        .stat-value {{ font-size: 2em; font-weight: bold; color: var(--color-primary); }}
        .stat-label {{ color: #666; margin-top: 5px; }}
        .module {{
            background: var(--color-card);
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .module-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #eee;
        }}
        .module-title {{ font-size: 1.5em; font-weight: bold; }}
        .module-score {{
            padding: 8px 20px;
            border-radius: 20px;
            color: white;
            font-weight: bold;
        }}
        .issue {{
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            border-left: 4px solid;
        }}
        .issue-error {{ background: #ffebee; border-color: var(--color-error); }}
        .issue-warning {{ background: #fff3e0; border-color: var(--color-warning); }}
        .issue-info {{ background: #e3f2fd; border-color: var(--color-info); }}
        .issue-code {{
            display: inline-block;
            padding: 2px 8px;
            background: rgba(0,0,0,0.1);
            border-radius: 4px;
            font-family: monospace;
            font-size: 0.9em;
            margin-bottom: 5px;
        }}
        .issue-message {{ font-weight: 500; margin-bottom: 5px; }}
        .issue-suggestion {{ color: #666; font-size: 0.95em; }}
        .issue-reference {{ margin-top: 5px; }}
        .issue-reference a {{ color: var(--color-primary); }}
        .footer {{
            text-align: center;
            padding: 30px;
            color: #666;
            margin-top: 30px;
        }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #eee;
        }}
        .metric {{ text-align: center; }}
        .metric-value {{ font-size: 1.5em; font-weight: bold; color: var(--color-primary); }}
        .metric-label {{ font-size: 0.85em; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 SiteSpec Inspector</h1>
            <div class="url">{report.url}</div>
        </div>

        <div class="score-card">
            <div class="score-circle {self._get_score_class(report.total_score)}">
                {report.total_score:.0f}
            </div>
            <h2>综合评分</h2>
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-value">{report.error_count}</div>
                    <div class="stat-label">错误</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{report.warning_count}</div>
                    <div class="stat-label">警告</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{len(report.results)}</div>
                    <div class="stat-label">检测模块</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{report.duration:.1f}s</div>
                    <div class="stat-label">检测耗时</div>
                </div>
            </div>
        </div>

        {self._render_modules(report)}

        <div class="footer">
            <p>生成时间: {datetime.fromtimestamp(report.timestamp).strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p>SiteSpec Inspector v1.0.0</p>
        </div>
    </div>
</body>
</html>"""
        return html

    def _get_score_class(self, score: float) -> str:
        """获取评分对应的CSS类"""
        if score >= 90:
            return "score-high"
        elif score >= 70:
            return "score-medium"
        else:
            return "score-low"

    def _render_modules(self, report: InspectionReport) -> str:
        """渲染模块详情"""
        modules_html = ""
        for name, result in report.results.items():
            issues_html = ""
            for issue in result.issues:
                issue_class = {
                    Severity.ERROR: "issue-error",
                    Severity.WARNING: "issue-warning",
                    Severity.INFO: "issue-info",
                }.get(issue.severity, "issue-info")

                reference_html = ""
                if issue.reference:
                    reference_html = f'<div class="issue-reference">参考: <a href="{issue.reference}" target="_blank">{issue.reference}</a></div>'

                suggestion_html = ""
                if issue.suggestion:
                    suggestion_html = f'<div class="issue-suggestion">💡 {issue.suggestion}</div>'

                issues_html += f"""
                <div class="issue {issue_class}">
                    <div class="issue-code">{issue.code}</div>
                    <div class="issue-message">{issue.message}</div>
                    {suggestion_html}
                    {reference_html}
                </div>
                """

            if not issues_html:
                issues_html = '<p style="color: #4CAF50;">✅ 所有检查项通过</p>'

            # 渲染指标
            metrics_html = ""
            if result.metrics:
                metrics_html = '<div class="metrics">'
                for key, value in result.metrics.items():
                    metrics_html += f"""
                    <div class="metric">
                        <div class="metric-value">{value}</div>
                        <div class="metric-label">{key}</div>
                    </div>
                    """
                metrics_html += '</div>'

            modules_html += f"""
            <div class="module">
                <div class="module-header">
                    <div class="module-title">{name}</div>
                    <div class="module-score {self._get_score_class(result.score)}">{result.score:.0f}</div>
                </div>
                {issues_html}
                {metrics_html}
            </div>
            """

        return modules_html