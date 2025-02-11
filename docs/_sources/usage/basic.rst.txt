基本的な使い方
============

このガイドでは、xml2xlsxの基本的な使用方法を説明します。

インストール
---------

pipを使用してインストール::

    pip install xml2xlsx

基本的な使用手順
------------

1. 設定ファイルの生成
^^^^^^^^^^^^^^^^^

最初に、XMLファイルから設定ファイルを生成します::

    xml2xlsx generate-config input.xml -o config.toml

このコマンドは、XMLファイルを解析して適切な設定ファイルを生成します。

2. 設定ファイルの確認
^^^^^^^^^^^^^^^

生成された設定ファイルの内容を確認します::

    [mapping.root.item]
    sheet_name = "商品リスト"
    columns = {
        "@id" = "商品ID",
        "name" = "商品名",
        "price" = "価格"
    }

必要に応じて、シート名やカラム名を編集できます。

3. XMLファイルの変換
^^^^^^^^^^^^^^^

設定ファイルを使用してXMLファイルを変換::

    xml2xlsx convert input.xml -c config.toml -o output.xlsx

コマンドラインオプション
------------------

generate-config
^^^^^^^^^^^^^

::

    xml2xlsx generate-config [OPTIONS] XML_FILES...

オプション:
  -o, --output FILE  出力する設定ファイルのパス [必須]
  --help            ヘルプメッセージを表示

convert
^^^^^^^

::

    xml2xlsx convert [OPTIONS] XML_FILE

オプション:
  -c, --config FILE  設定ファイルのパス [必須]
  -o, --output FILE  出力するExcelファイルのパス [必須]
  --help            ヘルプメッセージを表示

実行例
----

シンプルなXMLファイルの変換
^^^^^^^^^^^^^^^^^^^^^

input.xml::

    <?xml version="1.0" encoding="UTF-8"?>
    <products>
        <product id="1">
            <name>商品A</name>
            <price>1000</price>
        </product>
        <product id="2">
            <name>商品B</name>
            <price>2000</price>
        </product>
    </products>

設定ファイル（config.toml）::

    [mapping.products.product]
    sheet_name = "商品リスト"
    columns = {
        "@id" = "商品ID",
        "name" = "商品名",
        "price" = "価格"
    }

変換の実行::

    xml2xlsx convert input.xml -c config.toml -o output.xlsx

この結果、以下のような形式のExcelファイルが生成されます：

============  ========  ====
商品ID       商品名    価格
============  ========  ====
1            商品A     1000
2            商品B     2000
============  ========  ====

トラブルシューティング
---------------

よくある問題と解決方法：

1. 設定ファイル生成エラー
   * XMLファイルが整形式であることを確認
   * ファイルパスが正しいことを確認

2. 変換エラー
   * 設定ファイルのパスが正しいか確認
   * XMLファイルのパスが正しいか確認
   * シート名が31文字以内か確認

次のステップ
---------

* :doc:`config` で設定ファイルの詳細を確認
* :doc:`advanced` で高度な使用方法を学習