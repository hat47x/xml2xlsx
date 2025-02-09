ADR-010: ドキュメント生成ツールの選定
=====================================

ステータス
----------

提案（Proposed）

文脈
----

プロジェクトの成長に伴い、コードベースのドキュメント管理が重要になっています。現状のコードベースは以下の特徴を持ちます：

-  Google形式のdocstring
-  日本語によるドキュメント
-  型アノテーションの積極的な使用
-  高い品質基準（循環的複雑度、行数制限など）
-  CI/CDパイプラインでの自動化要件

決定
----

以下の理由から、\ **Sphinx + sphinx-autodoc + MyST-Parser**
の組み合わせを採用することを提案します。

主要コンポーネント
~~~~~~~~~~~~~~~~~~

1. **Sphinx**

   -  豊富な拡張機能エコシステム
   -  PDF/HTML/ePub等の多様な出力形式
   -  国際化（i18n）サポート

2. **sphinx-autodoc**

   -  Pythonコードからの自動ドキュメント生成
   -  型アノテーションの適切な表示
   -  docstringの解析と整形

3. **MyST-Parser**

   -  Markdownとrestructuredtextの統合
   -  既存のMarkdownドキュメントとの互換性
   -  ADRドキュメントの容易な統合

設定例
~~~~~~

.. code:: python

   # conf.py
   extensions = [
       'sphinx.ext.autodoc',
       'sphinx.ext.napoleon',  # Googleスタイルdocstring対応
       'sphinx.ext.viewcode',  # ソースコードへのリンク
       'sphinx.ext.intersphinx',  # 外部ドキュメントへのリンク
       'myst_parser',  # Markdown対応
   ]

   # 日本語サポート
   language = 'ja'
   locale_dirs = ['locale/']
   gettext_compact = False

   # 型アノテーション表示の設定
   autodoc_typehints = 'description'
   napoleon_use_param = True

CI/CD統合
~~~~~~~~~

.. code:: yaml

   # .github/workflows/docs.yml
   name: Documentation

   on:
     push:
       branches: [ main ]
     pull_request:
       branches: [ main ]

   jobs:
     docs:
       runs-on: ubuntu-latest
       steps:
       - uses: actions/checkout@v3
       - uses: actions/setup-python@v4
         with:
           python-version: '3.10'
       
       - name: Install dependencies
         run: |
           pip install sphinx sphinx-autodoc myst-parser

       - name: Build docs
         run: |
           sphinx-build -b html docs/ docs/_build/html

       - name: Deploy to GitHub Pages
         if: github.ref == 'refs/heads/main'
         uses: peaceiris/actions-gh-pages@v3
         with:
           github_token: ${{ secrets.GITHUB_TOKEN }}
           publish_dir: docs/_build/html

代替案
------

1. MkDocs + mkdocstrings
~~~~~~~~~~~~~~~~~~~~~~~~

-  利点:

   -  Markdownネイティブ
   -  シンプルな設定

-  欠点:

   -  拡張性がSphinxより限定的
   -  日本語サポートが不完全

2. pdoc
~~~~~~~

-  利点:

   -  最小限の設定で動作
   -  モダンなデフォルトテーマ

-  欠点:

   -  カスタマイズ性が低い
   -  大規模プロジェクトでの機能不足

3. pydoc
~~~~~~~~

-  利点:

   -  標準ライブラリ
   -  追加依存関係なし

-  欠点:

   -  機能が限定的
   -  モダンな機能なし

影響
----

肯定的な影響
~~~~~~~~~~~~

1. ドキュメントの品質向上

   -  型情報の適切な表示
   -  コードとドキュメントの一貫性確保
   -  自動生成による保守性向上

2. 開発効率の向上

   -  IDE統合によるドキュメント参照の容易さ
   -  CI/CDによる自動更新
   -  既存Markdownファイルの再利用

3. プロジェクトの持続可能性向上

   -  学習曲線の緩和
   -  コミュニティサポートの活用
   -  将来の拡張性確保

課題と対策
~~~~~~~~~~

1. 学習コスト

   -  チーム向けドキュメント作成ガイドラインの整備
   -  サンプルドキュメントの提供

2. 移行作業

   -  段階的な導入計画の策定
   -  既存ドキュメントの変換自動化

備考
----

実装計画
~~~~~~~~

1. 初期設定（1日）

   -  Sphinx環境の構築
   -  基本設定ファイルの作成

2. テンプレート整備（2日）

   -  ドキュメントテンプレートの作成
   -  スタイルガイドの整備

3. CI/CD構築（1日）

   -  GitHub Actions設定
   -  自動デプロイフロー確立

4. 既存ドキュメント移行（3日）

   -  ADRドキュメントの変換
   -  コードドキュメントの生成

参考資料
~~~~~~~~

-  `Sphinxドキュメント <https://www.sphinx-doc.org/ja/master/>`__
-  `MyST-Parser Documentation <https://myst-parser.readthedocs.io/>`__
-  `Google
   Pythonスタイルガイド <https://google.github.io/styleguide/pyguide.html>`__
