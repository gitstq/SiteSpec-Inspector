"""
Well-Known URIs检测器
检测RFC 5785定义的well-known locations
"""

from typing import Dict, Any
import requests
from urllib.parse import urljoin

from .base_checker import BaseChecker
from ..models import CheckResult


class WellKnownChecker(BaseChecker):
    """Well-Known URIs检测器"""

    # Well-Known URI列表
    WELL_KNOWN_URIS = {
        "/security.txt": {
            "description": "安全联系信息",
            "rfc": "RFC 9116",
            "importance": "high",
            "reference": "https://www.rfc-editor.org/rfc/rfc9116.html"
        },
        "/robots.txt": {
            "description": "搜索引擎爬虫规则",
            "rfc": "de-facto standard",
            "importance": "high",
            "reference": "https://www.robotstxt.org/"
        },
        "/humans.txt": {
            "description": "网站作者信息",
            "rfc": "Community standard",
            "importance": "low",
            "reference": "http://humanstxt.org/"
        },
        "/.well-known/security.txt": {
            "description": "安全联系信息(标准路径)",
            "rfc": "RFC 9116",
            "importance": "high",
            "reference": "https://www.rfc-editor.org/rfc/rfc9116.html"
        },
        "/.well-known/change-password": {
            "description": "密码更改页面",
            "rfc": "WICG",
            "importance": "medium",
            "reference": "https://wicg.github.io/change-password-url/"
        },
        "/.well-known/openid-configuration": {
            "description": "OpenID Connect配置",
            "rfc": "OpenID Connect",
            "importance": "medium",
            "reference": "https://openid.net/specs/openid-connect-discovery-1_0.html"
        },
        "/sitemap.xml": {
            "description": "站点地图",
            "rfc": "sitemaps.org",
            "importance": "high",
            "reference": "https://www.sitemaps.org/"
        },
        "/favicon.ico": {
            "description": "网站图标",
            "rfc": "de-facto standard",
            "importance": "medium",
            "reference": "https://html.spec.whatwg.org/multipage/links.html#rel-icon"
        },
        "/manifest.json": {
            "description": "Web应用清单",
            "rfc": "W3C",
            "importance": "medium",
            "reference": "https://w3c.github.io/manifest/"
        },
        "/.well-known/assetlinks.json": {
            "description": "数字资产链接",
            "rfc": "Google",
            "importance": "low",
            "reference": "https://developers.google.com/digital-asset-links/v1/getting-started"
        },
        "/.well-known/apple-app-site-association": {
            "description": "iOS通用链接",
            "rfc": "Apple",
            "importance": "low",
            "reference": "https://developer.apple.com/documentation/xcode/supporting-associated-domains"
        },
        "/.well-known/gpc.json": {
            "description": "全球隐私控制",
            "rfc": "Global Privacy Control",
            "importance": "low",
            "reference": "https://globalprivacycontrol.org/"
        },
        "/ads.txt": {
            "description": "授权数字卖家",
            "rfc": "IAB Tech Lab",
            "importance": "low",
            "reference": "https://iabtechlab.com/ads-txt/"
        },
        "/.well-known/dnt-policy.txt": {
            "description": "Do Not Track政策",
            "rfc": "EFF",
            "importance": "low",
            "reference": "https://www.eff.org/dnt-policy"
        },
    }

    def __init__(self, config):
        super().__init__(config)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": config.user_agent,
            "Accept": "*/*",
        })
        self.session.timeout = config.timeout

    def check(self, context: Dict[str, Any]) -> CheckResult:
        """执行Well-Known URIs检测"""
        result = self.create_result("Well-Known URIs")
        url = context["url"]
        start_time = __import__("time").time()

        found_count = 0
        missing_important = []

        for path, info in self.WELL_KNOWN_URIS.items():
            full_url = urljoin(url, path)
            exists = self._check_uri(full_url)

            if exists:
                found_count += 1
                result.metrics[path] = "found"
            else:
                result.metrics[path] = "missing"
                if info["importance"] == "high":
                    missing_important.append((path, info))

        # 报告缺失的重要文件
        for path, info in missing_important:
            if path == "/robots.txt":
                self.add_warning(
                    result, "WK001",
                    f"缺少 {path} - {info['description']}",
                    suggestion="创建robots.txt文件以指导搜索引擎爬虫",
                    reference=info["reference"]
                )
            elif path in ["/security.txt", "/.well-known/security.txt"]:
                self.add_warning(
                    result, "WK002",
                    f"缺少 {path} - {info['description']}",
                    suggestion="创建security.txt文件以提供安全联系信息",
                    reference=info["reference"]
                )
            elif path == "/sitemap.xml":
                self.add_info(
                    result, "WK003",
                    f"缺少 {path} - {info['description']}",
                    suggestion="创建sitemap.xml以帮助搜索引擎索引",
                    reference=info["reference"]
                )

        result.metrics["found_count"] = found_count
        result.metrics["total_count"] = len(self.WELL_KNOWN_URIS)

        result.duration = __import__("time").time() - start_time
        result.score = self.calculate_score(result)
        return result

    def _check_uri(self, url: str) -> bool:
        """检查URI是否存在"""
        try:
            response = self.session.head(url, allow_redirects=True, verify=self.config.verify_ssl)
            # 2xx状态码表示存在
            return 200 <= response.status_code < 300
        except requests.exceptions.RequestException:
            return False