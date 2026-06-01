"""
性能检测器
"""

from typing import Dict, Any
from bs4 import BeautifulSoup
import re

from .base_checker import BaseChecker
from ..models import CheckResult


class PerformanceChecker(BaseChecker):
    """性能检测器"""

    def check(self, context: Dict[str, Any]) -> CheckResult:
        """执行性能检测"""
        result = self.create_result("Performance")
        soup = context["soup"]
        headers = context["headers"]
        content = context["content"]
        elapsed = context["elapsed"]
        start_time = __import__("time").time()

        # 检查页面大小
        self._check_page_size(content, result)

        # 检查响应时间
        self._check_response_time(elapsed, result)

        # 检查资源加载
        self._check_resources(soup, result)

        # 检查图片优化
        self._check_image_optimization(soup, result)

        # 检查缓存头
        self._check_caching_headers(headers, result)

        # 检查压缩
        self._check_compression(headers, result)

        # 检查渲染阻塞资源
        self._check_render_blocking(soup, result)

        # 检查Gzip/Brotli
        self._check_content_encoding(headers, result)

        result.duration = __import__("time").time() - start_time
        result.score = self.calculate_score(result)
        return result

    def _check_page_size(self, content: bytes, result: CheckResult):
        """检查页面大小"""
        size_kb = len(content) / 1024

        result.metrics["page_size_kb"] = round(size_kb, 2)

        if size_kb > 2048:
            self.add_error(
                result, "PERF001",
                f"页面过大 ({size_kb:.1f} KB)",
                suggestion="优化页面大小，建议控制在2MB以内",
                reference="https://developer.mozilla.org/en-US/docs/Web/Performance/How_browsers_work"
            )
        elif size_kb > 1024:
            self.add_warning(
                result, "PERF002",
                f"页面较大 ({size_kb:.1f} KB)",
                suggestion="考虑优化图片、压缩资源以减少页面大小"
            )

    def _check_response_time(self, elapsed: float, result: CheckResult):
        """检查响应时间"""
        result.metrics["response_time_ms"] = round(elapsed * 1000, 2)

        if elapsed > 3:
            self.add_error(
                result, "PERF003",
                f"响应时间过长 ({elapsed:.2f}秒)",
                suggestion="优化服务器响应时间，建议控制在3秒以内"
            )
        elif elapsed > 1:
            self.add_warning(
                result, "PERF004",
                f"响应时间较慢 ({elapsed:.2f}秒)",
                suggestion="考虑优化服务器性能或CDN配置"
            )

    def _check_resources(self, soup: BeautifulSoup, result: CheckResult):
        """检查资源数量"""
        scripts = soup.find_all("script", src=True)
        stylesheets = soup.find_all("link", rel="stylesheet")
        images = soup.find_all("img")
        iframes = soup.find_all("iframe")

        result.metrics["external_scripts"] = len(scripts)
        result.metrics["stylesheets"] = len(stylesheets)
        result.metrics["images"] = len(images)
        result.metrics["iframes"] = len(iframes)

        # 检查过多外部脚本
        if len(scripts) > 15:
            self.add_warning(
                result, "PERF005",
                f"外部脚本数量较多 ({len(scripts)}个)",
                suggestion="考虑合并脚本文件或使用异步加载"
            )

        # 检查过多样式表
        if len(stylesheets) > 5:
            self.add_warning(
                result, "PERF006",
                f"样式表数量较多 ({len(stylesheets)}个)",
                suggestion="考虑合并CSS文件"
            )

        # 检查iframe使用
        if len(iframes) > 0:
            self.add_info(
                result, "PERF007",
                f"检测到{len(iframes)}个iframe",
                suggestion="iframe可能影响页面性能，考虑使用其他方案"
            )

    def _check_image_optimization(self, soup: BeautifulSoup, result: CheckResult):
        """检查图片优化"""
        images = soup.find_all("img")

        issues = []
        for img in images:
            # 检查尺寸属性
            if not img.get("width") or not img.get("height"):
                issues.append(("missing_dimensions", img))

            # 检查loading属性
            if not img.get("loading"):
                issues.append(("missing_lazy_loading", img))

            # 检查现代格式
            src = img.get("src", "").lower()
            if src and not any(src.endswith(ext) for ext in [".webp", "avif"]):
                issues.append(("not_modern_format", img))

        if issues:
            missing_dims = sum(1 for i, _ in issues if i == "missing_dimensions")
            missing_lazy = sum(1 for i, _ in issues if i == "missing_lazy_loading")

            if missing_dims > 0:
                self.add_warning(
                    result, "PERF008",
                    f"{missing_dims}张图片缺少width/height属性",
                    suggestion="添加图片尺寸属性以防止布局偏移(CLS)",
                    reference="https://web.dev/cls/"
                )

            if missing_lazy > 5:
                self.add_info(
                    result, "PERF009",
                    f"{missing_lazy}张图片可以添加懒加载",
                    suggestion="为视口外图片添加 loading=\"lazy\" 属性",
                    reference="https://web.dev/lazy-loading-images/"
                )

    def _check_caching_headers(self, headers: Dict[str, str], result: CheckResult):
        """检查缓存头"""
        headers_lower = {k.lower(): v for k, v in headers.items()}

        cache_control = headers_lower.get("cache-control", "")
        expires = headers_lower.get("expires")
        etag = headers_lower.get("etag")
        last_modified = headers_lower.get("last-modified")

        if not cache_control and not expires:
            self.add_warning(
                result, "PERF010",
                "缺少缓存控制头",
                suggestion="添加Cache-Control或Expires头以启用浏览器缓存",
                reference="https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching"
            )
        elif "no-cache" in cache_control or "no-store" in cache_control:
            self.add_info(
                result, "PERF011",
                "页面禁用了缓存",
                suggestion="静态资源应该启用缓存以提高性能"
            )

        if not etag and not last_modified:
            self.add_info(
                result, "PERF012",
                "缺少ETag或Last-Modified头",
                suggestion="添加验证头以支持条件请求"
            )

    def _check_compression(self, headers: Dict[str, str], result: CheckResult):
        """检查压缩"""
        headers_lower = {k.lower(): v for k, v in headers.items()}

        content_encoding = headers_lower.get("content-encoding", "")

        if not content_encoding:
            self.add_warning(
                result, "PERF013",
                "未启用内容压缩",
                suggestion="启用Gzip或Brotli压缩以减少传输大小",
                reference="https://developer.mozilla.org/en-US/docs/Web/HTTP/Compression"
            )

    def _check_render_blocking(self, soup: BeautifulSoup, result: CheckResult):
        """检查渲染阻塞资源"""
        # 检查head中的阻塞资源
        head = soup.find("head")
        if head:
            # 检查没有async/defer的脚本
            blocking_scripts = head.find_all(
                "script",
                src=True,
                async=False,
                defer=False
            )

            if len(blocking_scripts) > 3:
                self.add_warning(
                    result, "PERF014",
                    f"head中有{len(blocking_scripts)}个可能阻塞渲染的脚本",
                    suggestion="将脚本移到body底部或添加async/defer属性",
                    reference="https://web.dev/render-blocking-resources/"
                )

            # 检查外部样式表
            stylesheets = head.find_all("link", rel="stylesheet")
            if len(stylesheets) > 3:
                self.add_info(
                    result, "PERF015",
                    f"检测到{len(stylesheets)}个外部样式表",
                    suggestion="考虑内联关键CSS或合并样式表"
                )

    def _check_content_encoding(self, headers: Dict[str, str], result: CheckResult):
        """检查内容编码"""
        headers_lower = {k.lower(): v for k, v in headers.items()}

        encoding = headers_lower.get("content-encoding", "").lower()

        if encoding:
            if "br" in encoding:
                result.metrics["compression"] = "brotli"
            elif "gzip" in encoding:
                result.metrics["compression"] = "gzip"
            else:
                result.metrics["compression"] = encoding
        else:
            result.metrics["compression"] = "none"