"""
SEO检测器测试
"""

import pytest
from bs4 import BeautifulSoup

from sitespec_inspector.checkers.seo_checker import SEOChecker
from sitespec_inspector.config import Config


class TestSEOChecker:
    """SEO检测器测试类"""

    @pytest.fixture
    def checker(self):
        return SEOChecker(Config())

    def test_missing_description(self, checker):
        """测试缺少meta description"""
        html = "<html><head><title>Test</title></head><body></body></html>"
        soup = BeautifulSoup(html, "lxml")

        result = checker.create_result("test")
        checker._check_description(soup, result)

        assert any(i.code == "SEO003" for i in result.issues)

    def test_missing_canonical(self, checker):
        """测试缺少canonical链接"""
        html = "<html><head><title>Test</title></head><body></body></html>"
        soup = BeautifulSoup(html, "lxml")

        result = checker.create_result("test")
        checker._check_canonical(soup, "https://example.com", result)

        assert any(i.code == "SEO007" for i in result.issues)

    def test_missing_h1(self, checker):
        """测试缺少H1标签"""
        html = "<html><head><title>Test</title></head><body></body></html>"
        soup = BeautifulSoup(html, "lxml")

        result = checker.create_result("test")
        checker._check_h1(soup, result)

        assert any(i.code == "SEO012" for i in result.issues)

    def test_multiple_h1(self, checker):
        """测试多个H1标签"""
        html = "<html><head><title>Test</title></head><body><h1>Title 1</h1><h1>Title 2</h1></body></html>"
        soup = BeautifulSoup(html, "lxml")

        result = checker.create_result("test")
        checker._check_h1(soup, result)

        assert any(i.code == "SEO013" for i in result.issues)

    def test_images_without_alt(self, checker):
        """测试图片缺少alt属性"""
        html = '<html><head><title>Test</title></head><body><img src="test.jpg"><img src="test2.jpg" alt=""></body></html>'
        soup = BeautifulSoup(html, "lxml")

        result = checker.create_result("test")
        checker._check_images(soup, result)

        assert any(i.code == "SEO014" for i in result.issues)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])