#!/usr/bin/env python3
"""
SiteSpec-Inspector - 网站规范检测工具
Setup配置
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sitespec-inspector",
    version="1.0.0",
    author="gitstq",
    author_email="",
    description="🔍 轻量级网站规范检测工具 - 自动化检测HTML、SEO、Accessibility、Security等Web标准",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gitstq/sitespec-inspector",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "beautifulsoup4>=4.11.0",
        "lxml>=4.9.0",
        "colorama>=0.4.6",
        "pyyaml>=6.0",
        "click>=8.0.0",
        "rich>=13.0.0",
        "validators>=0.20.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "sitespec=sitespec_inspector.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)