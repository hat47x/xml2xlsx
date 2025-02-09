開発者ガイド
==========

このセクションでは、xml2xlsxの開発に参加する方向けの情報を提供します。

.. toctree::
   :maxdepth: 2

   setup
   testing
   style_guide

開発環境のセットアップ
----------------

1. リポジトリのクローン:

.. code-block:: bash

   git clone https://github.com/hat47x/xml2xlsx.git
   cd xml2xlsx

2. 開発用依存パッケージのインストール:

.. code-block:: bash

   pip install -e .[dev]

コード品質管理
----------

以下のツールを使用してコード品質を維持します：

* black: コードフォーマット
* mypy: 型チェック
* pflake8: コードスタイルチェック

実行方法：

.. code-block:: bash

   # フォーマットチェック
   black --check src tests

   # 型チェック
   mypy src

   # スタイルチェック
   pflake8 src tests

テスト
----

pytestを使用してテストを実行します：

.. code-block:: bash

   # 全テストの実行
   pytest

   # カバレッジレポート付きで実行
   pytest --cov=xml2xlsx tests/

   # 特定のテストのみ実行
   pytest tests/test_converter.py

既存のテストケース：

* test_converter.py: 基本的な変換機能のテスト
* test_config_generation.py: 設定ファイル生成のテスト
* test_cdata.py: CDATA処理のテスト
* test_performance.py: パフォーマンステスト

ドキュメント生成
------------

Sphinxを使用してドキュメントを生成します：

.. code-block:: bash

   cd docs
   make html

生成されたドキュメントは ``docs/_build/html`` に出力されます。