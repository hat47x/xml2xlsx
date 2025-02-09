設定ファイルの作成
==============

このガイドでは、xml2xlsxの設定ファイルの詳細な作成方法を説明します。

設定ファイルの基本
-------------

設定ファイルはTOML形式で記述され、以下の要素で構成されます：

1. マッピング定義
2. シート名の指定
3. カラム名の設定

基本構造
^^^^^^

.. code-block:: toml

    [mapping.要素パス]
    sheet_name = "シート名"
    columns = { 
        "XMLの要素名" = "Excelのカラム名"
    }

要素の指定方法
----------

1. 属性の参照
^^^^^^^^^^

属性は ``@`` プレフィックスで指定します：

.. code-block:: toml

    [mapping.products.item]
    sheet_name = "商品リスト"
    columns = {
        "@id" = "商品ID",       # id属性
        "@code" = "商品コード"  # code属性
    }

2. 要素の参照
^^^^^^^^^

要素は直接名前で指定します：

.. code-block:: toml

    [mapping.products.item]
    sheet_name = "商品リスト"
    columns = {
        "name" = "商品名",    # name要素
        "price" = "価格"      # price要素
    }

設定例
----

1. シンプルな変換
^^^^^^^^^^^^^

.. code-block:: xml

    <products>
        <item id="1">
            <name>商品A</name>
            <price>1000</price>
        </item>
    </products>

対応する設定：

.. code-block:: toml

    [mapping.products.item]
    sheet_name = "商品リスト"
    columns = {
        "@id" = "商品ID",
        "name" = "商品名",
        "price" = "価格"
    }

2. 複数シートの出力
^^^^^^^^^^^^^

.. code-block:: xml

    <company>
        <departments>
            <dept id="1">
                <name>営業部</name>
            </dept>
        </departments>
        <employees>
            <employee id="1">
                <name>山田太郎</name>
            </employee>
        </employees>
    </company>

対応する設定：

.. code-block:: toml

    [mapping.company.departments.dept]
    sheet_name = "部門一覧"
    columns = {
        "@id" = "部門ID",
        "name" = "部門名"
    }

    [mapping.company.employees.employee]
    sheet_name = "従業員一覧"
    columns = {
        "@id" = "社員ID",
        "name" = "氏名"
    }

制約事項
------

1. シート名
^^^^^^^^

* 31文字以内
* 使用可能文字: 
    * 英数字
    * ひらがな
    * カタカナ
    * 漢字
    * 一部の記号（スペース、アンダースコア等）

2. カラム名
^^^^^^^^

* 重複不可
* 空白文字は使用可能

よくある問題と解決方法
---------------

1. シート名が長すぎる場合
^^^^^^^^^^^^^^^^^^^

エラーメッセージ:
    ``シート名 'xxxxx' がExcelの31文字制限を超えています``

解決方法:
    より短いシート名を設定する

2. 要素が見つからない場合
^^^^^^^^^^^^^^^^^^

エラーメッセージ:
    ``指定された要素 'xxxxx' が見つかりません``

解決方法:
    * XMLファイルの構造を確認
    * 要素パスが正しいか確認

次のステップ
---------

* :doc:`advanced` で高度なマッピング設定を学習
* :doc:`../api/index` でAPIリファレンスを確認