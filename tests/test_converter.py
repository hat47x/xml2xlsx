"""基本機能のテストモジュール

以下の基本機能をテストします：
1. 単純なXML変換
2. 複数シート出力
3. カスタムシート名
4. 基本的なマッピング
"""

import pytest
from xml2xlsx.converter import XmlToExcelConverter
import pandas as pd
from pathlib import Path
import xml.etree.ElementTree as ET


def test_simple_xml_conversion(tmp_path):
    """単純なXMLからExcelへの基本的な変換をテスト"""
    xml_content = """
    <root>
        <item>
            <id>001</id>
            <name>Test Item</name>
            <price>1000</price>
        </item>
    </root>
    """

    # XMLを一時ファイルに保存
    xml_path = tmp_path / "test.xml"
    output_path = tmp_path / "output.xlsx"
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(xml_content)

    # 変換を実行
    converter = XmlToExcelConverter()
    converter.convert(str(xml_path), str(output_path))

    # 結果を検証（文字列として読み込み）
    with pd.ExcelFile(output_path) as excel:
        df = pd.read_excel(excel, "item", dtype=str)
        assert "id" in df.columns
        assert "name" in df.columns
        assert "price" in df.columns

        first_row = df.iloc[0]
        assert first_row["id"] == "001"
        assert first_row["name"] == "Test Item"
        assert first_row["price"] == "1000"


def test_multi_sheet_output(tmp_path):
    """複数エンティティの処理と複数シート出力をテスト"""
    xml_content = """
    <root>
        <company>
            <id>C001</id>
            <name>Test Company</name>
            <departments>
                <department>
                    <id>D001</id>
                    <name>Development</name>
                </department>
            </departments>
        </company>
    </root>
    """

    # XMLを一時ファイルに保存
    xml_path = tmp_path / "test.xml"
    output_path = tmp_path / "output.xlsx"
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(xml_content)

    # 変換を実行
    converter = XmlToExcelConverter()
    converter.convert(str(xml_path), str(output_path))

    # 結果を検証
    with pd.ExcelFile(output_path) as excel:
        # シートの存在確認
        assert "company" in excel.sheet_names
        assert "department" in excel.sheet_names

        # 会社データの確認（文字列として読み込み）
        company_df = pd.read_excel(excel, "company", dtype=str)
        assert "id" in company_df.columns
        assert company_df.iloc[0]["id"] == "C001"

        # 部門データの確認
        department_df = pd.read_excel(excel, "department", dtype=str)
        assert "id" in department_df.columns
        assert department_df.iloc[0]["id"] == "D001"
        assert "company.id" in department_df.columns
        assert department_df.iloc[0]["company.id"] == "C001"


def test_custom_sheet_names(tmp_path):
    """カスタムシート名の設定と適用をテスト"""
    xml_content = """
    <root>
        <company>
            <id>C001</id>
            <name>Test Company</name>
        </company>
    </root>
    """

    config = {
        "mapping": {
            "company": {
                "sheet_name": "会社マスタ",
                "columns": {"id": "会社ID", "name": "会社名"},
            }
        }
    }

    # XMLを一時ファイルに保存
    xml_path = tmp_path / "test.xml"
    output_path = tmp_path / "output.xlsx"
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(xml_content)

    # 変換を実行
    converter = XmlToExcelConverter()
    converter.config = config
    converter.convert(str(xml_path), str(output_path))

    # 結果を検証
    with pd.ExcelFile(output_path) as excel:
        assert "会社マスタ" in excel.sheet_names

        # データを文字列として読み込み
        df = pd.read_excel(excel, "会社マスタ", dtype=str)
        assert "会社ID" in df.columns
        assert "会社名" in df.columns
        assert df.iloc[0]["会社ID"] == "C001"


def test_basic_mapping(tmp_path):
    """基本的なカラムマッピング機能をテスト"""
    xml_content = """
    <root>
        <item>
            <id>001</id>
            <name>Test Item</name>
            <price>1000</price>
        </item>
    </root>
    """

    config = {
        "mapping": {
            "item": {"columns": {"id": "商品ID", "name": "商品名", "price": "価格"}}
        }
    }

    # XMLを一時ファイルに保存
    xml_path = tmp_path / "test.xml"
    output_path = tmp_path / "output.xlsx"
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(xml_content)

    # 変換を実行
    converter = XmlToExcelConverter()
    converter.config = config
    converter.convert(str(xml_path), str(output_path))

    # 結果を検証（文字列として読み込み）
    with pd.ExcelFile(output_path) as excel:
        df = pd.read_excel(excel, "item", dtype=str)
        assert "商品ID" in df.columns
        assert "商品名" in df.columns
        assert "価格" in df.columns

        first_row = df.iloc[0]
        assert first_row["商品ID"] == "001"
        assert first_row["商品名"] == "Test Item"
        assert first_row["価格"] == "1000"
