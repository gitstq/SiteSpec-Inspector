"""
检测器模块
"""

from .base_checker import BaseChecker
from .html_checker import HTMLChecker
from .seo_checker import SEOChecker
from .accessibility_checker import AccessibilityChecker
from .security_checker import SecurityChecker
from .performance_checker import PerformanceChecker
from .wellknown_checker import WellKnownChecker

__all__ = [
    "BaseChecker",
    "HTMLChecker",
    "SEOChecker",
    "AccessibilityChecker",
    "SecurityChecker",
    "PerformanceChecker",
    "WellKnownChecker",
]