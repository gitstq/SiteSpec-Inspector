"""
基础检测器类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import time

from ..models import CheckResult, Issue, Severity
from ..config import Config


class BaseChecker(ABC):
    """检测器基类"""

    def __init__(self, config: Config):
        self.config = config

    @abstractmethod
    def check(self, context: Dict[str, Any]) -> CheckResult:
        """
        执行检测

        Args:
            context: 检测上下文，包含url, response, soup, headers等

        Returns:
            CheckResult: 检测结果
        """
        pass

    def create_result(self, name: str) -> CheckResult:
        """创建检测结果对象"""
        return CheckResult(name=name, passed=True, score=100.0)

    def add_error(self, result: CheckResult, code: str, message: str,
                  element: str = None, suggestion: str = None, reference: str = None):
        """添加错误级别问题"""
        issue = Issue(
            code=code,
            message=message,
            severity=Severity.ERROR,
            element=element,
            suggestion=suggestion,
            reference=reference
        )
        result.add_issue(issue)
        result.passed = False

    def add_warning(self, result: CheckResult, code: str, message: str,
                    element: str = None, suggestion: str = None, reference: str = None):
        """添加警告级别问题"""
        issue = Issue(
            code=code,
            message=message,
            severity=Severity.WARNING,
            element=element,
            suggestion=suggestion,
            reference=reference
        )
        result.add_issue(issue)

    def add_info(self, result: CheckResult, code: str, message: str,
                 element: str = None, suggestion: str = None):
        """添加信息级别问题"""
        issue = Issue(
            code=code,
            message=message,
            severity=Severity.INFO,
            element=element,
            suggestion=suggestion
        )
        result.add_issue(issue)

    def calculate_score(self, result: CheckResult, max_score: float = 100.0) -> float:
        """
        计算得分
        错误扣10分，警告扣3分
        """
        errors = sum(1 for i in result.issues if i.severity == Severity.ERROR)
        warnings = sum(1 for i in result.issues if i.severity == Severity.WARNING)

        score = max_score - (errors * 10) - (warnings * 3)
        return max(0.0, score)