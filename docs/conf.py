# Configuration file for the Sphinx documentation builder.
import os
import sys
sys.path.insert(0, os.path.abspath('../src'))

# Project information
project = 'xml2xlsx'
copyright = '2025'
author = 'hat47x'
version = '0.2.0'
release = '0.2.0'

# General configuration
extensions = [
    'sphinx.ext.autodoc',        # APIドキュメント生成
    'sphinx.ext.napoleon',       # Google形式docstring対応
    'myst_parser',              # Markdown対応
]

# 言語設定
language = 'ja'
locale_dirs = ['locale/']
gettext_compact = False

# テーマ設定
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# 型ヒント表示の設定
autodoc_typehints = 'description'
napoleon_use_param = True
napoleon_use_rtype = True


# MarkdownとreSTの設定
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# マスタードキュメント
master_doc = 'index'

# 出力オプション
html_theme_options = {
    'navigation_depth': 4,
    'titles_only': False,
}

# User-docs specific settings
html_title = 'xml2xlsx ユーザーガイド'
html_short_title = 'User Guide'