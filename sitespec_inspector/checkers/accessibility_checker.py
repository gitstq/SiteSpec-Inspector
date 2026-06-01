"""
无障碍(Accessibility)检测器
基于WCAG 2.1标准
"""

from typing import Dict, Any
from bs4 import BeautifulSoup
import re

from .base_checker import BaseChecker
from ..models import CheckResult


class AccessibilityChecker(BaseChecker):
    """无障碍检测器"""

    def check(self, context: Dict[str, Any]) -> CheckResult:
        """执行无障碍检测"""
        result = self.create_result("Accessibility")
        soup = context["soup"]
        start_time = __import__("time").time()

        # 检查语言属性
        self._check_language(soup, result)

        # 检查标题层级
        self._check_heading_structure(soup, result)

        # 检查图片alt属性
        self._check_image_alts(soup, result)

        # 检查表单标签
        self._check_form_labels(soup, result)

        # 检查链接文本
        self._check_link_text(soup, result)

        # 检查跳过链接
        self._check_skip_links(soup, result)

        # 检查ARIA使用
        self._check_aria_usage(soup, result)

        # 检查对比度提示
        self._check_contrast_hints(soup, result)

        # 检查键盘可访问性
        self._check_keyboard_accessibility(soup, result)

        result.duration = __import__("time").time() - start_time
        result.score = self.calculate_score(result)
        return result

    def _check_language(self, soup: BeautifulSoup, result: CheckResult):
        """检查语言属性"""
        html = soup.find("html")
        if html and not html.get("lang"):
            self.add_error(
                result, "A11Y001",
                "<html>标签缺少lang属性",
                suggestion="添加lang属性以告知辅助技术页面语言，如 <html lang=\"zh-CN\">",
                reference="https://www.w3.org/WAI/WCAG21/Understanding/language-of-page.html"
            )

    def _check_heading_structure(self, soup: BeautifulSoup, result: CheckResult):
        """检查标题层级结构"""
        headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])

        if not headings:
            self.add_error(
                result, "A11Y002",
                "页面缺少标题层级",
                suggestion="添加适当的标题(h1-h6)来组织内容结构"
            )
            return

        # 检查层级跳跃
        prev_level = 0
        for h in headings:
            level = int(h.name[1])
            if level > prev_level + 1:
                self.add_warning(
                    result, "A11Y003",
                    f"标题层级跳跃: 从h{prev_level}跳到h{level}",
                    suggestion="标题层级应该按顺序使用，不要跳跃",
                    element=str(h)[:100]
                )
            prev_level = level

        # 检查多个H1
        h1s = [h for h in headings if h.name == "h1"]
        if len(h1s) > 1:
            self.add_warning(
                result, "A11Y004",
                f"页面包含{len(h1s)}个H1标题",
                suggestion="建议每个页面只使用一个H1标题作为页面主标题"
            )

        result.metrics["headings_count"] = len(headings)

    def _check_image_alts(self, soup: BeautifulSoup, result: CheckResult):
        """检查图片alt属性"""
        images = soup.find_all("img")

        decorative_without_alt = 0
        informative_without_alt = 0

        for img in images:
            alt = img.get("alt")
            # 检查是否有role="presentation"或aria-hidden="true"
            is_decorative = img.get("role") == "presentation" or img.get("aria-hidden") == "true"

            if alt is None and not is_decorative:
                # 尝试判断是否为装饰性图片
                src = img.get("src", "").lower()
                if any(x in src for x in ["icon", "decoration", "spacer", "blank"]):
                    decorative_without_alt += 1
                else:
                    informative_without_alt += 1

        if informative_without_alt > 0:
            self.add_error(
                result, "A11Y005",
                f"{informative_without_alt}张信息性图片缺少alt属性",
                suggestion="为所有信息性图片添加描述性的alt属性",
                reference="https://www.w3.org/WAI/WCAG21/Understanding/non-text-content.html"
            )

        if decorative_without_alt > 0:
            self.add_info(
                result, "A11Y006",
                f"{decorative_without_alt}张图片可能为装饰性图片但未标记",
                suggestion="装饰性图片应使用 alt=\"\" 或 role=\"presentation\""
            )

        result.metrics["images_total"] = len(images)
        result.metrics["images_missing_alt"] = informative_without_alt

    def _check_form_labels(self, soup: BeautifulSoup, result: CheckResult):
        """检查表单标签"""
        inputs = soup.find_all(["input", "select", "textarea"])

        missing_labels = []
        for inp in inputs:
            # 跳过隐藏、提交、按钮类型的input
            input_type = inp.get("type", "").lower()
            if input_type in ["hidden", "submit", "button", "image", "reset"]:
                continue

            # 检查是否有label
            input_id = inp.get("id")
            input_name = inp.get("name")

            has_label = False
            if input_id:
                label = soup.find("label", attrs={"for": input_id})
                if label:
                    has_label = True

            # 检查aria-label或aria-labelledby
            if not has_label and (inp.get("aria-label") or inp.get("aria-labelledby")):
                has_label = True

            # 检查placeholder是否作为唯一标签
            if not has_label and inp.get("placeholder") and not input_id:
                self.add_warning(
                    result, "A11Y007",
                    "使用placeholder作为唯一标签",
                    suggestion="placeholder不应替代label，请添加适当的<label>标签",
                    element=str(inp)[:100]
                )
                continue

            if not has_label:
                missing_labels.append(inp)

        if missing_labels:
            self.add_error(
                result, "A11Y008",
                f"{len(missing_labels)}个表单字段缺少标签",
                suggestion="为所有表单字段添加<label>标签或aria-label属性",
                reference="https://www.w3.org/WAI/WCAG21/Understanding/info-and-relationships.html"
            )

    def _check_link_text(self, soup: BeautifulSoup, result: CheckResult):
        """检查链接文本"""
        links = soup.find_all("a", href=True)

        vague_texts = ["点击这里", "了解更多", "查看详情", "点击", "这里", "更多",
                       "click here", "read more", "learn more", "details", "link"]

        vague_links = []
        for link in links:
            text = link.get_text(strip=True).lower()
            if text in vague_texts or len(text) < 3:
                vague_links.append(link)

        if vague_links:
            self.add_warning(
                result, "A11Y009",
                f"{len(vague_links)}个链接文本不够描述性",
                suggestion="使用描述性的链接文本，避免\"点击这里\"等模糊表述",
                reference="https://www.w3.org/WAI/WCAG21/Understanding/link-purpose-in-context.html"
            )

    def _check_skip_links(self, soup: BeautifulSoup, result: CheckResult):
        """检查跳过导航链接"""
        skip_links = soup.find_all("a", href=re.compile(r"^#"))
        has_skip_link = any("skip" in link.get_text(strip=True).lower() or
                           "main" in link.get("href", "") for link in skip_links)

        # 检查是否有main元素或role="main"
        main_content = soup.find("main") or soup.find(attrs={"role": "main"})

        if not has_skip_link and main_content:
            self.add_info(
                result, "A11Y010",
                "未检测到跳过导航链接",
                suggestion="添加\"跳转到主内容\"链接以方便键盘用户",
                reference="https://www.w3.org/WAI/WCAG21/Understanding/bypass-blocks.html"
            )

    def _check_aria_usage(self, soup: BeautifulSoup, result: CheckResult):
        """检查ARIA使用"""
        # 检查无效的ARIA角色
        valid_roles = [
            "alert", "alertdialog", "application", "article", "banner", "button",
            "cell", "checkbox", "columnheader", "combobox", "complementary",
            "contentinfo", "definition", "dialog", "directory", "document",
            "feed", "figure", "form", "grid", "gridcell", "group", "heading",
            "img", "link", "list", "listbox", "listitem", "log", "main",
            "marquee", "math", "menu", "menubar", "menuitem", "menuitemcheckbox",
            "menuitemradio", "navigation", "none", "note", "option", "presentation",
            "progressbar", "radio", "radiogroup", "region", "row", "rowgroup",
            "rowheader", "scrollbar", "search", "searchbox", "separator",
            "slider", "spinbutton", "status", "switch", "tab", "table", "tablist",
            "tabpanel", "term", "textbox", "timer", "toolbar", "tooltip", "tree",
            "treegrid", "treeitem"
        ]

        elements_with_role = soup.find_all(attrs={"role": True})
        invalid_roles = []

        for elem in elements_with_role:
            role = elem.get("role", "").lower()
            if role not in valid_roles:
                invalid_roles.append((elem, role))

        if invalid_roles:
            self.add_warning(
                result, "A11Y011",
                f"检测到{len(invalid_roles)}个无效的ARIA角色",
                suggestion="使用有效的ARIA角色值",
                reference="https://www.w3.org/TR/wai-aria-1.1/#role_definitions"
            )

    def _check_contrast_hints(self, soup: BeautifulSoup, result: CheckResult):
        """检查对比度相关提示"""
        # 检查是否有浅色文字在浅色背景上的情况（简单检测）
        inline_styles = soup.find_all(style=True)

        low_contrast_hints = 0
        for elem in inline_styles:
            style = elem.get("style", "").lower()
            # 简单检测：如果同时有color和background-color且颜色相近
            if "color:" in style and "background" in style:
                low_contrast_hints += 1

        if low_contrast_hints > 0:
            self.add_info(
                result, "A11Y012",
                f"检测到{low_contrast_hints}个内联样式可能包含颜色设置",
                suggestion="确保文字与背景对比度符合WCAG标准（正常文字4.5:1，大文字3:1）",
                reference="https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html"
            )

    def _check_keyboard_accessibility(self, soup: BeautifulSoup, result: CheckResult):
        """检查键盘可访问性"""
        # 检查tabindex
        negative_tabindex = soup.find_all(attrs={"tabindex": lambda x: x and int(x) < 0})

        if negative_tabindex:
            self.add_info(
                result, "A11Y013",
                f"检测到{len(negative_tabindex)}个元素使用负值tabindex",
                suggestion="负值tabindex会将元素从Tab顺序中移除，确保这是有意为之"
            )

        # 检查可点击的非交互元素
        clickable_divs = soup.find_all("div", onclick=True)
        clickable_spans = soup.find_all("span", onclick=True)

        if clickable_divs or clickable_spans:
            total = len(clickable_divs) + len(clickable_spans)
            self.add_warning(
                result, "A11Y014",
                f"检测到{total}个非交互元素绑定了点击事件",
                suggestion="使用<button>或<a>标签代替div/span，或添加适当的ARIA角色和键盘事件处理",
                reference="https://www.w3.org/WAI/WCAG21/Understanding/keyboard.html"
            )