"""XMLからExcelへの変換ツールのセットアップスクリプト。"""

from setuptools import setup, find_packages

setup(
    name="xml2xlsx",
    version="0.1.0",
    description="Convert XML files to XLSX",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pandas>=1.5.0",
        "openpyxl>=3.0.0",
        "toml>=0.10.0",
    ],
    entry_points={
        "console_scripts": [
            "xml2xlsx=xml2xlsx.cli:main",
        ],
    },
    python_requires=">=3.7",
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "flake8>=4.0.0",
            "black>=22.0.0",
            "mypy>=1.0.0",
            "pandas-stubs>=2.0.0",  # pandasの型定義
            "psutil>=5.8.0",        # パフォーマンス監視用
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Text Processing :: Markup :: XML",
        "Topic :: Office/Business",
    ],
)