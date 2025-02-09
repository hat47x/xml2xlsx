設定ファイル生成
============

.. module:: xml2xlsx.config_generator

XMLファイルを解析して設定ファイルを生成するモジュールです。

関数
----

.. function:: generate_config(input_files: List[str], output_file: str) -> None

   XMLファイルから設定ファイルを生成します。

   :param input_files: 入力XMLファイルのパスのリスト
   :param output_file: 出力する設定ファイルのパス
   :raises FileNotFoundError: 入力ファイルが存在しない場合
   :raises ValueError: シート名が31文字を超えるなど、不正な設定や制限に違反する場合

   複数のXMLファイルを解析し、統合された設定ファイルを生成します。
   生成される設定ファイルは以下の特徴を持ちます：

   * TOML形式
   * XMLパスごとのマッピング定義
   * 属性とテキスト要素の自動検出
   * シート名の自動設定

   使用例:

   .. code-block:: python

      from xml2xlsx import generate_config

      # 単一のXMLファイルから設定を生成
      generate_config(["input.xml"], "config.toml")

      # 複数のXMLファイルから統合設定を生成
      generate_config(["file1.xml", "file2.xml"], "config.toml")

内部関数
-------

.. function:: _analyze_xml_structure(xml_file: str) -> Dict[str, Dict[str, Set[str]]]

   XMLファイルの構造を解析し、属性とテキスト要素を収集します。

   :param xml_file: 解析するXMLファイルのパス
   :return: XMLパスごとの属性と要素の情報を含む辞書

   内部で使用される解析関数です。以下の情報を収集します：

   * XMLパス（要素の階層構造）
   * 各要素の属性
   * テキストコンテンツを持つ子要素

出力される設定ファイル形式
--------------------

生成される設定ファイルは以下の構造を持ちます：

.. code-block:: toml

   [mapping]
   "element_path" = { sheet_name = "sheet_name", columns = { "@attr" = "attr", "elem" = "elem" } }

* ``element_path``: XMLパス（要素の階層を表す）
* ``sheet_name``: 出力Excelのシート名
* ``columns``: 属性（@プレフィックス）と要素のマッピング

例えば、以下のようなXMLファイルの場合：

.. code-block:: xml

   <root>
     <item id="1">
       <name>example</name>
     </item>
   </root>

生成される設定ファイル：

.. code-block:: toml

   [mapping.root.item]
   sheet_name = "root.item"
   columns = { "@id" = "id", "name" = "name" }