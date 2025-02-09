xml2xlsx ユーザーガイド
==================

XMLファイルをExcelファイルに変換するツール
---------------------------------

xml2xlsxは、XMLファイルを簡単にExcelファイルに変換できるツールです。

クイックスタート
-----------

1. インストール::

    pip install xml2xlsx

2. 設定ファイルの生成::

    xml2xlsx generate-config input.xml -o config.toml

3. XMLファイルの変換::

    xml2xlsx convert input.xml -c config.toml -o output.xlsx

目次
----

.. toctree::
   :maxdepth: 2
   :caption: 基本ガイド

   usage/basic
   usage/config
   usage/advanced

.. toctree::
   :maxdepth: 1
   :caption: リファレンス

   api/index

特徴
----

* シンプルなコマンドラインインターフェース
* 設定ファイルの自動生成機能
* 柔軟なカラムマッピング
* CDATA要素のサポート

システム要件
---------

* Python 3.10以上
* 対応OS: Linux, macOS, Windows

サポート
------

問題が発生した場合は、以下の手順で解決を試みてください：

1. :doc:`usage/basic` の確認
2. :doc:`usage/config` の設定例を参照
3. GitHubのイシュートラッカーで報告

更新履歴
------

最新バージョン: 0.2.0

* XMLパスの完全サポート
* 設定ファイル生成機能の改善
* エラーメッセージの日本語対応

検索
----

* :ref:`search`