APIリファレンス
=============

xml2xlsxのAPIリファレンスです。

モジュール構成
----------

.. toctree::
   :maxdepth: 2

   converter
   config_generator
   entity
   exceptions

主要コンポーネント
--------------

変換機能
^^^^^^
:class:`xml2xlsx.XmlToExcelConverter`
    XMLファイルをExcelファイルに変換するメインクラス

設定生成
^^^^^^
:func:`xml2xlsx.generate_config`
    XMLファイルから設定ファイルを生成する関数

データモデル
^^^^^^^^^
:class:`xml2xlsx.Entity`
    XML要素を表現するデータモデル

:class:`xml2xlsx.EntityContext`
    変換処理のコンテキスト管理

例外
^^^^
:exc:`xml2xlsx.ConfigurationError`
    設定関連のエラー

使用例
-----

基本的な使用方法:

.. code-block:: python

   from xml2xlsx import XmlToExcelConverter
   from xml2xlsx import generate_config

   # 設定ファイルの生成
   generate_config(["input.xml"], "config.toml")

   # XMLファイルの変換
   converter = XmlToExcelConverter("config.toml")
   converter.convert("input.xml", "output.xlsx")