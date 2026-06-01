"""
SEO检测器
"""

from typing import Dict, Any
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from .base_checker import BaseChecker
from ..models import CheckResult


class SEOChecker(BaseChecker):
    """SEO检测器"""

    def check(self, context: Dict[str, Any]) -> CheckResult:
        """执行SEO检测"""
        result = self.create_result("SEO")
        soup = context["soup"]
        url = context["url"]
        start_time = __import__("time").time()

        # 检查标题
        self._check_title(soup, result)

        # 检查meta description
        self._check_description(soup, result)

        # 检查canonical链接
        self._check_canonical(soup, url, result)

        # 检查Open Graph标签
        self._check_open_graph(soup, result)

        # 检查Twitter Card
        self._check_twitter_card(soup, result)

        # 检查结构化数据
        self._check_structured_data(soup, result)

        # 检查robots meta
        self._check_robots_meta(soup, result)

        # 检查H1标签
        self._check_h1(soup, result)

        # 检查图片alt属性
        self._check_images(soup, result)

        # 检查内部链接
        self._check_internal_links(soup, result)

        result.duration = __import__("time").time() - start_time
        result.score = self.calculate_score(result)
        return result

    def _check_title(self, soup: BeautifulSoup, result: CheckResult):
        """检查标题优化"""
        title = soup.find("title")
        if title:
            title_text = title.get_text(strip=True)
            if len(title_text) < 30:
                self.add_warning(
                    result, "SEO001",
                    f"标题过短，不利于SEO ({len(title_text)}字符)",
                    suggestion="建议标题长度在30-60个字符之间",
                    reference="https://developers.google.com/search/docs/appearance/title-link"
                )
            elif len(title_text) > 60:
                self.add_warning(
                    result, "SEO002",
                    f"标题过长，可能被截断 ({len(title_text)}字符)",
                    suggestion="建议标题长度控制在60个字符以内"
                )

    def _check_description(self, soup: BeautifulSoup, result: CheckResult):
        """检查meta description"""
        desc_meta = soup.find("meta", attrs={"name": "description"})
        if not desc_meta:
            self.add_error(
                result, "SEO003",
                "缺少meta description",
                suggestion="添加 <meta name=\"description\" content=\"页面描述\">",
                reference="https://developers.google.com/search/docs/appearance/snippet"
            )
        else:
            content = desc_meta.get("content", "")
            if not content:
                self.add_error(
                    result, "SEO004",
                    "meta description为空",
                    suggestion="为description添加有意义的描述文本"
                )
            elif len(content) < 50:
                self.add_warning(
                    result, "SEO005",
                    f"描述过短 ({len(content)}字符)",
                    suggestion="建议描述长度在50-160个字符之间"
                )
            elif len(content) > 160:
                self.add_warning(
                    result, "SEO006",
                    f"描述过长 ({len(content)}字符)",
                    suggestion="建议描述长度控制在160个字符以内"
                )

    def _check_canonical(self, soup: BeautifulSoup, url: str, result: CheckResult):
        """检查canonical链接"""
        canonical = soup.find("link", attrs={"rel": "canonical"})
        if not canonical:
            self.add_warning(
                result, "SEO007",
                "缺少canonical链接",
                suggestion="添加 <link rel=\"canonical\" href=\"...\"> 避免重复内容问题",
                reference="https://developers.google.com/search/docs/crawling-indexing/canonicalization"
            )

    def _check_open_graph(self, soup: BeautifulSoup, result: CheckResult):
        """检查Open Graph标签"""
        og_tags = {
            "og:title": "标题",
            "og:description": "描述",
            "og:image": "图片",
            "og:url": "URL",
            "og:type": "类型",
        }

        missing = []
        for tag, name in og_tags.items():
            if not soup.find("meta", attrs={"property": tag}):
                missing.append(name)

        if missing:
            self.add_warning(
                result, "SEO008",
                f"缺少Open Graph标签: {', '.join(missing)}",
                suggestion="添加Open Graph标签以优化社交媒体分享效果",
                reference="https://ogp.me/"
            )

    def _check_twitter_card(self, soup: BeautifulSoup, result: CheckResult):
        """检查Twitter Card标签"""
        twitter_card = soup.find("meta", attrs={"name": "twitter:card"})
        if not twitter_card:
            self.add_info(
                result, "SEO009",
                "缺少Twitter Card标签",
                suggestion="添加Twitter Card标签以优化Twitter分享效果",
                reference="https://developer.twitter.com/en/docs/twitter-for-websites/cards/overview/abouts-cards"
            )

    def _check_structured_data(self, soup: BeautifulSoup, result: CheckResult):
        """检查结构化数据"""
        json_ld = soup.find_all("script", type="application/ld+json")
        microdata = soup.find_all(attrs={"itemscope": True})

        if not json_ld and not microdata:
            self.add_info(
                result, "SEO010",
                "未检测到结构化数据",
                suggestion="考虑添加Schema.org结构化数据以提升搜索展示效果",
                reference="https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data"
            )
        else:
            result.metrics["structured_data_count"] = len(json_ld) + len(microdata)

    def _check_robots_meta(self, soup: BeautifulSoup, result: CheckResult):
        """检查robots meta标签"""
        robots = soup.find("meta", attrs={"name": "robots"})
        if robots:
            content = robots.get("content", "").lower()
            if "noindex" in content:
                self.add_warning(
                    result, "SEO011",
                    "页面设置了noindex，搜索引擎不会索引此页面",
                    suggestion="如果希望页面被索引，请移除noindex指令"
                )

    def _check_h1(self, soup: BeautifulSoup, result: CheckResult):
        """检查H1标签"""
        h1s = soup.find_all("h1")
        if not h1s:
            self.add_error(
                result, "SEO012",
                "缺少H1标签",
                suggestion="每个页面应该有一个且仅有一个H1标签"
            )
        elif len(h1s) > 1:
            self.add_warning(
                result, "SEO013",
                f"检测到{len(h1s)}个H1标签",
                suggestion="建议每个页面只使用一个H1标签"
            )

    def _check_images(self, soup: BeautifulSoup, result: CheckResult):
        """检查图片alt属性"""
        images = soup.find_all("img")
        missing_alt = [img for img in images if not img.get("alt")]

        if missing_alt:
            self.add_warning(
                result, "SEO014",
                f"{len(missing_alt)}张图片缺少alt属性",
                suggestion="为所有图片添加描述性的alt属性",
                reference="https://developers.google.com/search/docs/appearance/google-images"
            )

        result.metrics["total_images"] = len(images)
        result.metrics["images_without_alt"] = len(missing_alt)

    def _check_internal_links(self, soup: BeautifulSoup, result: CheckResult):
        """检查内部链接"""
        links = soup.find_all("a", href=True)
        internal_links = [a for a in links if not a["href"].startswith(("http", "//", "mailto:", "tel:"))]

        if len(internal_links) < 3:
            self.add_info(
                result, "SEO015",
                f"页面内部链接较少 ({len(internal_links)}个)",
                suggestion="适当增加内部链接有助于搜索引擎发现和索引其他页面"
            )

        result.metrics["internal_links"] = len(internal_links)
        result.metrics["external_links"] = len(links) - len(internal_links)