使用方法
========

基本的な使用手順
------------

1. 設定ファイルの生成
^^^^^^^^^^^^^^^^^^

XMLファイルから設定ファイルを生成します：

.. code-block:: bash

   xml2xlsx generate-config input.xml -o config.toml

複数のXMLファイルから生成する場合：

.. code-block:: bash

   xml2xlsx generate-config file1.xml file2.xml -o config.toml

2. 設定ファイルの確認と編集
^^^^^^^^^^^^^^^^^^^^

生成された設定ファイルの内容を確認し、必要に応じて編集します：

.. code-block:: toml

   [mapping.root.item]
   sheet_name = "Items"     # シート名を変更
   columns = { 
     "@id" = "ID",         # カラム名をカスタマイズ
     "name" = "商品名"      # 日本語のカラム名も使用可能
   }

3. XMLファイルの変換
^^^^^^^^^^^^^^^^

設定ファイルを使用してXMLファイルを変換します：

.. code-block:: bash

   xml2xlsx convert input.xml -c config.toml -o output.xlsx

コマンドラインオプション
------------------

generate-config
^^^^^^^^^^^^^

.. code-block:: text

   xml2xlsx generate-config [OPTIONS] XML_FILES...

オプション:
   -o, --output FILE  出力する設定ファイルのパス [必須]
   --help            ヘルプメッセージを表示

convert
^^^^^^^

.. code-block:: text

   xml2xlsx convert [OPTIONS] XML_FILE

オプション:
   -c, --config FILE  設定ファイルのパス [必須]
   -o, --output FILE  出力するExcelファイルのパス [必須]
   --help            ヘルプメッセージを表示

設定ファイルの書き方
---------------

基本構造
^^^^^^^

.. code-block:: toml

   [mapping]
   "xml.path" = { sheet_name = "シート名", columns = { ... } }

* ``xml.path``: XMLの要素パス（ドット区切り）
* ``sheet_name``: 出力するExcelのシート名
* ``columns``: 変換ルールを指定する辞書

変換ルールの例
^^^^^^^^^^^

属性の参照:

.. code-block:: toml

   columns = { "@id" = "ID番号" }     # id属性を「ID番号」列に変換

要素の参照:

.. code-block:: toml

   columns = { "name" = "名称" }      # name要素を「名称」列に変換

トラブルシューティング
-----------------

1. シート名の制約

   * シート名は明示的に指定する必要があります
   * Excel仕様の制限に注意してください

2. 変換エラー

   * XMLファイルのパスが正しいか確認
   * 設定ファイルのパスが正しいか確認
   * シート名やカラム名が適切か確認

3. メモリ使用量

   * 大規模なXMLファイルを処理する場合は、十分なメモリを確保してください
   * 必要に応じて分割処理を検討してください