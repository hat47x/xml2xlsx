xml2xlsx 開発者ドキュメント
=========================

このドキュメントは、xml2xlsxの開発に参加する方々向けの技術情報を提供します。
ユーザー向けのドキュメントは ``docs/`` ディレクトリにあります。

クイックスタート
-------------

1. 開発環境のセットアップ::

    git clone https://github.com/hat47x/xml2xlsx.git
    cd xml2xlsx
    pip install -e .[dev]

2. テストの実行::

    pytest

3. ドキュメントのビルド::

    cd dev-docs
    make html

目次
----

.. toctree::
   :maxdepth: 2
   :caption: アーキテクチャ

   architecture/index

.. toctree::
   :maxdepth: 2
   :caption: 開発ガイド

   guides/development-style
   guides/testing
   guides/test-specification

.. toctree::
   :maxdepth: 2
   :caption: 設計決定記録

   adr/index

開発プロセス
-----------

コード品質
^^^^^^^^^^

- black: コードフォーマット
- mypy: 型チェック
- pflake8: コードスタイルチェック

実行方法::

    # フォーマットチェック
    black --check src tests

    # 型チェック
    mypy src

    # スタイルチェック
    pflake8 src tests

テスト
^^^^^^

* pytest使用
* カバレッジ90%以上
* 大規模データのテスト含む

実行方法::

    # 全テスト実行
    pytest

    # カバレッジレポート付き
    pytest --cov=xml2xlsx tests/

    # パフォーマンステスト
    pytest tests/test_performance.py

ドキュメント
^^^^^^^^^^

* reStructuredText形式
* Sphinx使用
* 日本語対応

ビルド方法::

    cd dev-docs
    make html

ディレクトリ構造
-------------

.. code-block:: text

    xml2xlsx/
    ├── src/                    # ソースコード
    │   └── xml2xlsx/          # メインパッケージ
    ├── tests/                  # テストコード
    │   └── test_data/         # テストデータ
    ├── docs/                   # ユーザードキュメント
    │   ├── usage/             # 使用方法
    │   └── api/               # API参照
    └── dev-docs/              # 開発者ドキュメント
        ├── architecture/      # 設計文書
        ├── guides/           # 開発ガイド
        └── adr/             # 設計決定記録

コントリビューション
----------------

1. コーディング規約
   * PEP 8に準拠
   * 型ヒントを積極的に使用
   * docstringは必須（Google形式）

2. テスト
   * 新機能には必ずテストを追加
   * カバレッジ90%以上を維持

3. ドキュメント
   * 機能変更時はドキュメントも更新
   * ADRによる設計決定の記録

検索
----

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`