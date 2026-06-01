"""
HTML检测器测试
"""

import pytest
from bs4 import BeautifulSoup

from sitespec_inspector.checkers.html_checker import HTMLChecker
from sitespec_inspector.config import Config
from sitespec_inspector.models import CheckResult


class TestHTMLChecker:
    """HTML检测器测试类"""

    @pytest.fixture
    def checker(self):
        return HTMLChecker(Config())

    def test_missing_doctype(self, checker):
        """测试缺少DOCTYPE"""
        html = "<html><head><title>Test</title></head><body></body></html>"
        soup = BeautifulSoup(html, "lxml")

        result = checker.create_result("test")
        checker._check_doctype(soup, result)

        assert any(i.code == "HTML001" for i in result.issues)

    def test_missing_title(self, checker):
        """测试缺少标题"""
        html = "<!DOCTYPE html><html><head></head><body></body></html>"
        soup = BeautifulSoup(html, "lxml")

        result = checker.create_result("test")
        checker._check_title(soup, result)

        assert any(i.code == "HTML010" for i in result.issues)

    def test_title_too_short(self, checker):
        """测试标题过短"""
        html = "<!DOCTYPE html><html><head><title>Hi</title></head><body></body></html>"
        soup = BeautifulSoup(html, "lxml")

        result = checker.create_result("test")
        checker._check_title(soup, result)

        assert any(i.code == "HTML012" for i in result.issues)

    def test_missing_viewport(self, checker):
        """测试缺少viewport"""
        html = "<!DOCTYPE html><html><head><title>Test Title</title></head><body></body></html>"
        soup = BeautifulSoup(html, "lxml")

        result = checker.create_result("test")
        checker._check_viewport(soup, result)

        assert any(i.code == "HTML008" for i in result.issues)

    def test_valid_html(self, checker):
        """测试有效的HTML"""
        html = """<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>This is a Valid Title for Testing</title>
        </head>
        <body></body>
        </html>"""
        soup = BeautifulSoup(html, "lxml")

        result = checker.create_result("test")
        checker._check_doctype(soup, result)
        checker._check_title(soup, result)
        checker._check_viewport(soup, result)
        checker._check_language(soup, result)
        checker._check_charset(soup, result)

        # 应该没有错误
        assert not any(i.severity.value == "error" for i in result.issues)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])