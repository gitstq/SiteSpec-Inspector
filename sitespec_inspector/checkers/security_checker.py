"""
安全检测器
"""

from typing import Dict, Any
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from .base_checker import BaseChecker
from ..models import CheckResult


class SecurityChecker(BaseChecker):
    """安全检测器"""

    def check(self, context: Dict[str, Any]) -> CheckResult:
        """执行安全检测"""
        result = self.create_result("Security")
        headers = context["headers"]
        soup = context["soup"]
        url = context["url"]
        start_time = __import__("time").time()

        # 检查安全响应头
        self._check_security_headers(headers, result)

        # 检查HTTPS
        self._check_https(url, result)

        # 检查混合内容
        self._check_mixed_content(soup, url, result)

        # 检查表单安全
        self._check_form_security(soup, result)

        # 检查Cookie安全（如果可见）
        self._check_cookie_security(context, result)

        # 检查目标属性
        self._check_target_blank(soup, result)

        # 检查内联脚本
        self._check_inline_scripts(soup, result)

        result.duration = __import__("time").time() - start_time
        result.score = self.calculate_score(result)
        return result

    def _check_security_headers(self, headers: Dict[str, str], result: CheckResult):
        """检查安全响应头"""
        headers_lower = {k.lower(): v for k, v in headers.items()}

        # Content-Security-Policy
        if "content-security-policy" not in headers_lower:
            self.add_warning(
                result, "SEC001",
                "缺少Content-Security-Policy头",
                suggestion="添加CSP头以防止XSS攻击",
                reference="https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP"
            )

        # X-Frame-Options
        if "x-frame-options" not in headers_lower:
            self.add_warning(
                result, "SEC002",
                "缺少X-Frame-Options头",
                suggestion="添加X-Frame-Options: DENY或SAMEORIGIN以防止点击劫持",
                reference="https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Frame-Options"
            )

        # X-Content-Type-Options
        if "x-content-type-options" not in headers_lower:
            self.add_warning(
                result, "SEC003",
                "缺少X-Content-Type-Options头",
                suggestion="添加X-Content-Type-Options: nosniff防止MIME类型嗅探",
                reference="https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Content-Type-Options"
            )

        # Referrer-Policy
        if "referrer-policy" not in headers_lower:
            self.add_info(
                result, "SEC004",
                "缺少Referrer-Policy头",
                suggestion="添加Referrer-Policy以控制Referrer信息的发送",
                reference="https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referrer-Policy"
            )

        # Strict-Transport-Security (HSTS)
        if "strict-transport-security" not in headers_lower:
            self.add_info(
                result, "SEC005",
                "缺少Strict-Transport-Security (HSTS)头",
                suggestion="添加HSTS头以强制HTTPS连接",
                reference="https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security"
            )

        # Permissions-Policy
        if "permissions-policy" not in headers_lower:
            self.add_info(
                result, "SEC006",
                "缺少Permissions-Policy头",
                suggestion="添加Permissions-Policy以限制浏览器功能使用",
                reference="https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Permissions-Policy"
            )

        # 收集已配置的头
        security_headers = [
            "content-security-policy",
            "x-frame-options",
            "x-content-type-options",
            "referrer-policy",
            "strict-transport-security",
            "permissions-policy",
            "cross-origin-embedder-policy",
            "cross-origin-opener-policy",
            "cross-origin-resource-policy"
        ]

        configured = [h for h in security_headers if h in headers_lower]
        result.metrics["security_headers_configured"] = len(configured)
        result.metrics["security_headers_total"] = len(security_headers)

    def _check_https(self, url: str, result: CheckResult):
        """检查HTTPS使用"""
        parsed = urlparse(url)
        if parsed.scheme != "https":
            self.add_error(
                result, "SEC007",
                "未使用HTTPS协议",
                suggestion="使用HTTPS加密传输以保护用户数据",
                reference="https://developer.mozilla.org/en-US/docs/Web/Security/Secure_Contexts"
            )

    def _check_mixed_content(self, soup: BeautifulSoup, url: str, result: CheckResult):
        """检查混合内容"""
        parsed = urlparse(url)
        if parsed.scheme != "https":
            return

        # 检查HTTP资源
        http_resources = []

        # 检查图片
        for img in soup.find_all("img", src=True):
            if img["src"].startswith("http://"):
                http_resources.append(("image", img["src"]))

        # 检查脚本
        for script in soup.find_all("script", src=True):
            if script["src"].startswith("http://"):
                http_resources.append(("script", script["src"]))

        # 检查样式表
        for link in soup.find_all("link", rel="stylesheet", href=True):
            if link["href"].startswith("http://"):
                http_resources.append(("stylesheet", link["href"]))

        # 检查iframe
        for iframe in soup.find_all("iframe", src=True):
            if iframe["src"].startswith("http://"):
                http_resources.append(("iframe", iframe["src"]))

        if http_resources:
            self.add_error(
                result, "SEC008",
                f"检测到{len(http_resources)}个HTTP资源（混合内容）",
                suggestion="将所有HTTP资源改为HTTPS，或使用协议相对URL",
                reference="https://developer.mozilla.org/en-US/docs/Web/Security/Mixed_content"
            )

        result.metrics["mixed_content_count"] = len(http_resources)

    def _check_form_security(self, soup: BeautifulSoup, result: CheckResult):
        """检查表单安全"""
        forms = soup.find_all("form")

        insecure_forms = []
        for form in forms:
            action = form.get("action", "")
            # 检查是否提交到HTTP
            if action.startswith("http://"):
                insecure_forms.append(form)
            # 检查密码字段
            password_inputs = form.find_all("input", type="password")
            if password_inputs and not action.startswith("https://"):
                if form not in insecure_forms:
                    insecure_forms.append(form)

        if insecure_forms:
            self.add_error(
                result, "SEC009",
                f"{len(insecure_forms)}个表单可能通过不安全连接提交",
                suggestion="确保所有表单通过HTTPS提交",
                reference="https://developer.mozilla.org/en-US/docs/Web/Security/Secure_Contexts"
            )

        # 检查CSRF保护（简单检测）
        for form in forms:
            if form.find("input", type="password") or form.find("input", type="email"):
                # 检查是否有CSRF token
                hidden_inputs = form.find_all("input", type="hidden")
                csrf_found = any(
                    "csrf" in inp.get("name", "").lower() or
                    "token" in inp.get("name", "").lower()
                    for inp in hidden_inputs
                )
                if not csrf_found:
                    self.add_info(
                        result, "SEC010",
                        "表单可能缺少CSRF保护",
                        suggestion="为表单添加CSRF token以防止跨站请求伪造攻击",
                        reference="https://developer.mozilla.org/en-US/docs/Web/Security/CSRF"
                    )

        result.metrics["forms_count"] = len(forms)

    def _check_cookie_security(self, context: Dict[str, Any], result: CheckResult):
        """检查Cookie安全设置"""
        # 注意：JavaScript无法直接读取HttpOnly cookie
        # 这里只是提供信息
        response = context.get("response")
        if response and hasattr(response, "cookies"):
            cookies = response.cookies
            if cookies:
                result.metrics["cookies_count"] = len(cookies)

    def _check_target_blank(self, soup: BeautifulSoup, result: CheckResult):
        """检查target="_blank"安全性"""
        external_links = soup.find_all("a", target="_blank", href=True)

        missing_rel = []
        for link in external_links:
            rel = link.get("rel", [])
            if isinstance(rel, str):
                rel = rel.split()
            if "noopener" not in rel and "noreferrer" not in rel:
                missing_rel.append(link)

        if missing_rel:
            self.add_warning(
                result, "SEC011",
                f"{len(missing_rel)}个外部链接缺少noopener/noreferrer",
                suggestion="为target=\"_blank\"的链接添加 rel=\"noopener noreferrer\"",
                reference="https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/rel/noopener"
            )

    def _check_inline_scripts(self, soup: BeautifulSoup, result: CheckResult):
        """检查内联脚本"""
        inline_scripts = soup.find_all("script", src=False)

        if inline_scripts:
            # 检查是否有nonce或CSP哈希
            has_nonce = any(script.get("nonce") for script in inline_scripts)

            if not has_nonce:
                self.add_info(
                    result, "SEC012",
                    f"检测到{len(inline_scripts)}个内联脚本",
                    suggestion="考虑使用外部脚本文件，或为内联脚本添加nonce以配合CSP",
                    reference="https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP"
                )

        result.metrics["inline_scripts_count"] = len(inline_scripts)