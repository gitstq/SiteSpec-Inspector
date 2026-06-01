"""
数据模型定义
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
import json


class Severity(Enum):
    """问题严重程度"""
    ERROR = "error"           # 严重问题
    WARNING = "warning"       # 警告
    INFO = "info"             # 信息提示
    PASSED = "passed"         # 通过


@dataclass
class Issue:
    """检测发现的问题"""
    code: str                          # 问题代码
    message: str                       # 问题描述
    severity: Severity                 # 严重程度
    element: Optional[str] = None      # 相关HTML元素
    line: Optional[int] = None         # 行号
    column: Optional[int] = None       # 列号
    suggestion: Optional[str] = None   # 修复建议
    reference: Optional[str] = None    # 参考链接

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity.value,
            "element": self.element,
            "line": self.line,
            "column": self.column,
            "suggestion": self.suggestion,
            "reference": self.reference,
        }


@dataclass
class CheckResult:
    """单项检测结果"""
    name: str                          # 检测项名称
    passed: bool                       # 是否通过
    score: float                       # 得分 (0-100)
    issues: List[Issue] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    duration: float = 0.0              # 检测耗时

    def add_issue(self, issue: Issue):
        """添加问题"""
        self.issues.append(issue)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "passed": self.passed,
            "score": self.score,
            "issues": [i.to_dict() for i in self.issues],
            "metrics": self.metrics,
            "duration": self.duration,
        }


@dataclass
class InspectionReport:
    """完整检测报告"""
    url: str
    timestamp: float
    config: Dict[str, Any]
    results: Dict[str, CheckResult] = field(default_factory=dict)
    errors: Dict[str, str] = field(default_factory=dict)
    duration: float = 0.0

    def add_result(self, name: str, result: CheckResult):
        """添加检测结果"""
        self.results[name] = result

    def add_error(self, name: str, error: str):
        """添加错误信息"""
        self.errors[name] = error

    @property
    def total_score(self) -> float:
        """计算总得分"""
        if not self.results:
            return 0.0
        scores = [r.score for r in self.results.values()]
        return sum(scores) / len(scores)

    @property
    def total_issues(self) -> int:
        """获取总问题数"""
        return sum(len(r.issues) for r in self.results.values())

    @property
    def error_count(self) -> int:
        """获取错误数量"""
        count = 0
        for result in self.results.values():
            count += sum(1 for i in result.issues if i.severity == Severity.ERROR)
        return count

    @property
    def warning_count(self) -> int:
        """获取警告数量"""
        count = 0
        for result in self.results.values():
            count += sum(1 for i in result.issues if i.severity == Severity.WARNING)
        return count

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "url": self.url,
            "timestamp": self.timestamp,
            "duration": self.duration,
            "config": self.config,
            "total_score": self.total_score,
            "total_issues": self.total_issues,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "results": {k: v.to_dict() for k, v in self.results.items()},
            "errors": self.errors,
        }

    def to_json(self, indent: int = 2) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)