"""
HTML结构检测器
"""

from typing import Dict, Any
from bs4 import BeautifulSoup

from .base_checker import BaseChecker
from ..models import CheckResult


class HTMLChecker(BaseChecker):
    """HTML结构检测器"""

    def check(self, context: Dict[str, Any]) -> CheckResult:
        """执行HTML检测"""
        result = self.create_result("HTML Structure")
        soup = context["soup"]
        start_time = __import__("time").time()

        # 检查DOCTYPE
        self._check_doctype(soup, result)

        # 检查基本结构
        self._check_basic_structure(soup, result)

        # 检查meta标签
        self._check_meta_tags(soup, result)

        # 检查语言属性
        self._check_language(soup, result)

        # 检查字符编码
        self._check_charset(soup, result)

        # 检查视口设置
        self._check_viewport(soup, result)

        # 检查标题
        self._check_title(soup, result)

        # 收集指标
        result.metrics = {
            "total_elements": len(soup.find_all()),
            "headings_count": len(soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])),
            "images_count": len(soup.find_all("img")),
            "links_count": len(soup.find_all("a")),
            "scripts_count": len(soup.find_all("script")),
            "styles_count": len(soup.find_all("style")) + len(soup.find_all(rel="stylesheet")),
        }

        result.duration = __import__("time").time() - start_time
        result.score = self.calculate_score(result)
        return result

    def _check_doctype(self, soup: BeautifulSoup, result: CheckResult):
        """检查DOCTYPE声明"""
        # BeautifulSoup会自动处理DOCTYPE
        doctype = soup.contents[0] if soup.contents else None
        if not doctype or not isinstance(doctype, str) or "!doctype" not in doctype.lower():
            self.add_error(
                result, "HTML001",
                "缺少DOCTYPE声明",
                suggestion="在文档第一行添加 <!DOCTYPE html>",
                reference="https://html.spec.whatwg.org/multipage/syntax.html#the-doctype"
            )

    def _check_basic_structure(self, soup: BeautifulSoup, result: CheckResult):
        """检查基本HTML结构"""
        html = soup.find("html")
        if not html:
            self.add_error(
                result, "HTML002",
                "缺少<html>标签",
                suggestion="确保文档包含<html>根元素"
            )

        head = soup.find("head")
        if not head:
            self.add_error(
                result, "HTML003",
                "缺少<head>标签",
                suggestion="在<html>内添加<head>元素"
            )

        body = soup.find("body")
        if not body:
            self.add_error(
                result, "HTML004",
                "缺少<body>标签",
                suggestion="在<html>内添加<body>元素"
            )

    def _check_meta_tags(self, soup: BeautifulSoup, result: CheckResult):
        """检查meta标签"""
        # 检查charset
        charset_meta = soup.find("meta", charset=True)
        if not charset_meta:
            self.add_warning(
                result, "HTML005",
                "缺少charset meta标签",
                suggestion="添加 <meta charset=\"UTF-8\">",
                reference="https://html.spec.whatwg.org/multipage/semantics.html#charset"
            )

    def _check_language(self, soup: BeautifulSoup, result: CheckResult):
        """检查语言属性"""
        html = soup.find("html")
        if html and not html.get("lang"):
            self.add_warning(
                result, "HTML006",
                "<html>标签缺少lang属性",
                suggestion="添加lang属性，如 <html lang=\"zh-CN\"> 或 <html lang=\"en\">",
                reference="https://www.w3.org/TR/WCAG20-TECHS/H57.html"
            )

    def _check_charset(self, soup: BeautifulSoup, result: CheckResult):
        """检查字符编码"""
        charset_meta = soup.find("meta", charset=True)
        if charset_meta:
            charset = charset_meta.get("charset", "").upper()
            if charset not in ["UTF-8", "UTF8"]:
                self.add_warning(
                    result, "HTML007",
                    f"推荐使用UTF-8编码，当前为: {charset}",
                    suggestion="将charset设置为UTF-8"
                )

    def _check_viewport(self, soup: BeautifulSoup, result: CheckResult):
        """检查视口设置"""
        viewport_meta = soup.find("meta", attrs={"name": "viewport"})
        if not viewport_meta:
            self.add_warning(
                result, "HTML008",
                "缺少viewport meta标签",
                suggestion="添加 <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">",
                reference="https://developer.mozilla.org/en-US/docs/Web/HTML/Viewport_meta_tag"
            )
        else:
            content = viewport_meta.get("content", "")
            if "width=device-width" not in content:
                self.add_warning(
                    result, "HTML009",
                    "viewport设置不完整",
                    suggestion="确保包含 width=device-width"
                )

    def _check_title(self, soup: BeautifulSoup, result: CheckResult):
        """检查标题"""
        title = soup.find("title")
        if not title:
            self.add_error(
                result, "HTML010",
                "缺少<title>标签",
                suggestion="在<head>中添加<title>标签"
            )
        else:
            title_text = title.get_text(strip=True)
            if not title_text:
                self.add_error(
                    result, "HTML011",
                    "<title>标签为空",
                    suggestion="为<title>添加有意义的文本"
                )
            elif len(title_text) < self.config.min_title_length:
                self.add_warning(
                    result, "HTML012",
                    f"标题过短 ({len(title_text)}字符)",
                    suggestion=f"标题建议至少{self.config.min_title_length}个字符"
                )
            elif len(title_text) > self.config.max_title_length:
                self.add_warning(
                    result, "HTML013",
                    f"标题过长 ({len(title_text)}字符)",
                    suggestion=f"标题建议不超过{self.config.max_title_length}个字符"
                )