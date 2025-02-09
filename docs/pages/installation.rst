インストール手順
===========

必要要件
-------

* Python 3.10以上
* pip（Pythonパッケージインストーラー）

インストール方法
------------

pipを使用してインストール:

.. code-block:: bash

   pip install xml2xlsx

開発版のインストール
---------------

開発版を使用する場合は、GitHubリポジトリから直接インストールできます：

.. code-block:: bash

   pip install git+https://github.com/hat47x/xml2xlsx.git

依存パッケージ
-----------

xml2xlsxは以下のパッケージに依存しています：

* pandas>=1.5.0: データフレーム処理とExcel出力
* openpyxl>=3.0.0: Excel生成
* toml>=0.10.0: 設定ファイル解析

これらの依存パッケージは、インストール時に自動的にインストールされます。

開発環境のセットアップ
-----------------

開発に参加する場合は、追加の依存パッケージをインストールできます：

.. code-block:: bash

   pip install xml2xlsx[dev]

これにより以下のツールがインストールされます：

* pytest: テスト実行
* black: コードフォーマット
* mypy: 型チェック
* pflake8: コードスタイルチェック
* sphinx: ドキュメント生成