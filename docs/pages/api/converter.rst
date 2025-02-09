XML変換
=========

.. module:: xml2xlsx.converter

XMLファイルをExcelファイルに変換するためのメインモジュールです。

クラス
----

.. class:: XmlToExcelConverter

   XMLからExcelへの変換を行うクラスです。

   .. method:: __init__(config_file: Optional[str] = None)

      コンバーターを初期化します。

      :param config_file: 設定ファイルのパス（オプション）
      :type config_file: str, optional
      :raises ConfigurationError: 設定ファイルの読み込みに失敗した場合

   .. method:: load_config(config_file: str) -> None

      設定ファイルを読み込みます。

      :param config_file: 設定ファイルのパス
      :type config_file: str
      :raises ConfigurationError: 設定ファイルの読み込みや検証に失敗した場合

   .. method:: convert(input_file: str, output_file: str) -> None

      XMLファイルをExcelに変換します。

      :param input_file: 入力XMLファイルのパス
      :param output_file: 出力Excelファイルのパス
      :raises ConfigurationError: 設定が不適切な場合
      :raises ET.ParseError: XMLファイルの解析に失敗した場合

使用例
-----

基本的な使用方法:

.. code-block:: python

   from xml2xlsx import XmlToExcelConverter

   # 設定ファイルを指定して初期化
   converter = XmlToExcelConverter("config.toml")

   # XMLファイルを変換
   converter.convert("input.xml", "output.xlsx")

設定ファイル形式
------------

TOML形式の設定ファイルで、以下の構造を持ちます：

.. code-block:: toml

   [mapping]
   "xml.path" = { sheet_name = "Sheet1", columns = { "source" = "target" } }

設定の各要素：

* ``xml.path``: XMLのパス（ドット区切りの要素階層）
* ``sheet_name``: 出力するExcelのシート名
* ``columns``: ソースフィールドと出力カラム名のマッピング

  * キー: XMLの要素名または属性名（属性は@プレフィックス）
  * 値: Excelのカラム名

注意事項
-------

1. シート名の制約
   
   * シート名は設定ファイルで明示的に指定する必要があります
   * 名前の長さや文字種の制限はExcelの仕様に準拠します

2. データ変換

   * すべての値は文字列として処理されます
   * CDATA要素は適切に処理されます
   * 重複する要素は自動的に排除されます

3. メモリ管理

   * 処理済み要素は追跡され、重複処理を防止します
   * 必要なカラムのみを抽出して処理します