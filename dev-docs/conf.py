# Configuration file for the Sphinx documentation builder (Developer Documentation).
import os
import sys
sys.path.insert(0, os.path.abspath('../src'))

# Project information
project = 'xml2xlsx Developer Documentation'
copyright = '2025, hat47x'
author = 'hat47x'
version = '0.2.0'
release = '0.2.0'

# General configuration
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.graphviz',
    'sphinx.ext.intersphinx',
    'sphinxcontrib.mermaid'  # mermaid図表のサポート
]

# 言語設定
language = 'ja'
locale_dirs = ['locale/']
gettext_compact = False

# テーマ設定
html_theme = 'sphinx_rtd_theme'
html_static_path = []  # 警告を抑制するため空リストに変更

# 型ヒント表示の設定
autodoc_typehints = 'description'
napoleon_use_param = True
napoleon_use_rtype = True

# インタースフィンクス設定
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
}

# Mermaid設定
mermaid_version = '10.6.1'  # 特定のバージョンを指定
mermaid_init_js = 'https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js'
mermaid_params = []  # 空のリストとして設定

# GraphViz設定
graphviz_output_format = 'svg'

# 出力オプション
html_theme_options = {
    'navigation_depth': 4,
    'titles_only': False,
    'style_nav_header_background': '#2980B9',
    'collapse_navigation': False,
    'sticky_navigation': True,
}

# 除外パターン
exclude_patterns = [
    '_build',
    'Thumbs.db',
    '.DS_Store',
    'README.md'
]

# ソースファイル設定
source_suffix = '.rst'
master_doc = 'index'

# サイドバーのカスタマイズ
html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
        'relations.html',
        'searchbox.html',
    ]
}

# reST設定
rst_prolog = '''
.. |project| replace:: xml2xlsx
'''

# セクションの文字装飾
rst_epilog = '''
.. |h1| raw:: html

   <hr style="border-top: 3px double #8c8b8b">

.. |h2| raw:: html

   <hr style="border-top: 1px solid #8c8b8b">

.. highlight:: none
'''

# TOML用のハイライト設定
from pygments.lexer import RegexLexer, bygroups
from pygments.token import *

class SimpleTOMLLexer(RegexLexer):
    name = 'TOML'
    aliases = ['toml']
    filenames = ['*.toml']

    tokens = {
        'root': [
            (r'[^\S\n]+', Text),
            (r'#.*?$', Comment.Single),
            (r'"[^"]*"', String),
            (r'=', Operator),
            (r'\{|\}|\[|\]', Punctuation),
            (r'[^=\s\[\]{}#"]+', Name),
            (r'\n', Text),
        ]
    }

def setup(app):
    from sphinx.highlighting import lexers
    lexers['toml'] = SimpleTOMLLexer()