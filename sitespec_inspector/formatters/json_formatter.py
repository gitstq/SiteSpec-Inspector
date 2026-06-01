"""
JSON格式化器
"""

import json
from ..models import InspectionReport


class JsonFormatter:
    """JSON输出格式化器"""

    def format(self, report: InspectionReport, indent: int = 2) -> str:
        """格式化报告为JSON"""
        return report.to_json(indent=indent)