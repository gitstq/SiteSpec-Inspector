"""
SiteSpec-Inspector 🔍
轻量级网站规范检测工具

自动化检测网站的HTML结构、SEO、Accessibility、Security等Web标准
"""

__version__ = "1.0.0"
__author__ = "gitstq"
__license__ = "MIT"

from .core import Inspector
from .config import Config

__all__ = ["Inspector", "Config"]