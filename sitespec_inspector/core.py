"""
核心检测引擎
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
import time

from .config import Config
from .checkers.html_checker import HTMLChecker
from .checkers.seo_checker import SEOChecker
from .checkers.accessibility_checker import AccessibilityChecker
from .checkers.security_checker import SecurityChecker
from .checkers.performance_checker import PerformanceChecker
from .checkers.wellknown_checker import WellKnownChecker
from .models import CheckResult, InspectionReport


class Inspector:
    """网站规范检测器"""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.config.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
        })

        # 初始化检测器
        self.checkers = {}
        if self.config.check_html:
            self.checkers["html"] = HTMLChecker(self.config)
        if self.config.check_seo:
            self.checkers["seo"] = SEOChecker(self.config)
        if self.config.check_accessibility:
            self.checkers["accessibility"] = AccessibilityChecker(self.config)
        if self.config.check_security:
            self.checkers["security"] = SecurityChecker(self.config)
        if self.config.check_performance:
            self.checkers["performance"] = PerformanceChecker(self.config)
        if self.config.check_well_known:
            self.checkers["well_known"] = WellKnownChecker(self.config)

    def inspect(self, url: str) -> InspectionReport:
        """
        执行完整的网站检测

        Args:
            url: 要检测的网站URL

        Returns:
            InspectionReport: 检测报告
        """
        start_time = time.time()

        # 确保URL格式正确
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        report = InspectionReport(
            url=url,
            timestamp=start_time,
            config=self.config.to_dict()
        )

        try:
            # 获取页面内容
            response = self.session.get(
                url,
                timeout=self.config.timeout,
                allow_redirects=self.config.follow_redirects,
                verify=self.config.verify_ssl
            )
            response.raise_for_status()

            # 解析HTML
            soup = BeautifulSoup(response.content, "lxml")

            # 存储上下文
            context = {
                "url": url,
                "response": response,
                "soup": soup,
                "headers": response.headers,
                "content": response.content,
                "elapsed": response.elapsed.total_seconds(),
            }

            # 执行各项检测
            for name, checker in self.checkers.items():
                try:
                    result = checker.check(context)
                    report.add_result(name, result)
                except Exception as e:
                    report.add_error(name, str(e))

        except requests.exceptions.RequestException as e:
            report.add_error("network", f"请求失败: {str(e)}")
        except Exception as e:
            report.add_error("general", f"检测失败: {str(e)}")

        report.duration = time.time() - start_time
        return report

    def inspect_multiple(self, urls: List[str]) -> List[InspectionReport]:
        """批量检测多个URL"""
        reports = []
        for url in urls:
            report = self.inspect(url)
            reports.append(report)
        return reports