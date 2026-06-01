"""
配置管理模块
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import yaml
import json


@dataclass
class Config:
    """检测配置类"""

    # 基础配置
    timeout: int = 30
    follow_redirects: bool = True
    verify_ssl: bool = True
    user_agent: str = "SiteSpec-Inspector/1.0.0"

    # 检测模块开关
    check_html: bool = True
    check_seo: bool = True
    check_accessibility: bool = True
    check_security: bool = True
    check_performance: bool = True
    check_well_known: bool = True

    # 阈值配置
    min_title_length: int = 10
    max_title_length: int = 60
    min_description_length: int = 50
    max_description_length: int = 160
    max_image_size_kb: int = 500
    max_page_size_kb: int = 2048

    # 输出配置
    output_format: str = "console"  # console, json, html, markdown
    verbose: bool = False
    show_passed: bool = True

    # 自定义规则
    custom_rules: Dict = field(default_factory=dict)

    @classmethod
    def from_file(cls, filepath: str) -> "Config":
        """从配置文件加载"""
        with open(filepath, "r", encoding="utf-8") as f:
            if filepath.endswith(".yaml") or filepath.endswith(".yml"):
                data = yaml.safe_load(f)
            else:
                data = json.load(f)
        return cls(**data)

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "timeout": self.timeout,
            "follow_redirects": self.follow_redirects,
            "verify_ssl": self.verify_ssl,
            "user_agent": self.user_agent,
            "check_html": self.check_html,
            "check_seo": self.check_seo,
            "check_accessibility": self.check_accessibility,
            "check_security": self.check_security,
            "check_performance": self.check_performance,
            "check_well_known": self.check_well_known,
            "min_title_length": self.min_title_length,
            "max_title_length": self.max_title_length,
            "min_description_length": self.min_description_length,
            "max_description_length": self.max_description_length,
            "max_image_size_kb": self.max_image_size_kb,
            "max_page_size_kb": self.max_page_size_kb,
            "output_format": self.output_format,
            "verbose": self.verbose,
            "show_passed": self.show_passed,
        }