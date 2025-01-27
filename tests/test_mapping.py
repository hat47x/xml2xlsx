"""カラムマッピング処理のテストモジュール

以下のマッピング機能をテストします：
1. 基本的なカラムマッピング
2. カラム順序の保持
3. 複雑なマッピングパターン
4. エラー処理
"""

import pytest
from xml2xlsx.converter import XmlToExcelConverter
import pandas as pd
from pathlib import Path


def test_basic_column_mapping(tmp_path):
    """基本的なカラムマッピング機能をテスト"""
    xml_content = """
    <root>
        <department>
            <id>D001</id>
            <name>開発部</name>
            <code>DEV</code>
        </department>
    </root>
    """

    config = {
        "mapping": {
            "department": {
                "columns": {"id": "部門ID", "name": "部門名", "code": "部門コード"}
            }
        }
    }

    xml_path = tmp_path / "test.xml"
    output_path = tmp_path / "output.xlsx"
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(xml_content)

    converter = XmlToExcelConverter()
    converter.config = config
    converter.convert(str(xml_path), str(output_path))

    with pd.ExcelFile(output_path) as excel:
        df = pd.read_excel(excel, "department")
        assert list(df.columns) == ["部門ID", "部門名", "部門コード"]
        assert df.iloc[0]["部門ID"] == "D001"
        assert df.iloc[0]["部門名"] == "開発部"
        assert df.iloc[0]["部門コード"] == "DEV"


def test_column_order_preservation(tmp_path):
    """カラム順序の保持機能をテスト"""
    xml_content = """
    <root>
        <department>
            <id>D001</id>
            <name>開発部</name>
            <code>DEV</code>
        </department>
    </root>
    """

    config = {
        "mapping": {
            "department": {
                "columns": {
                    "name": "部門名",  # 意図的に順序を変更
                    "code": "部門コード",
                    "id": "部門ID",
                }
            }
        }
    }

    xml_path = tmp_path / "test.xml"
    output_path = tmp_path / "output.xlsx"
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(xml_content)

    converter = XmlToExcelConverter()
    converter.config = config
    converter.convert(str(xml_path), str(output_path))

    with pd.ExcelFile(output_path) as excel:
        df = pd.read_excel(excel, "department")
        assert list(df.columns) == ["部門名", "部門コード", "部門ID"]


def test_nested_mapping(tmp_path):
    """入れ子構造のマッピング機能をテスト"""
    xml_content = """
    <root>
        <company>
            <id>C001</id>
            <department>
                <id>D001</id>
                <name>開発部</name>
            </department>
        </company>
    </root>
    """

    config = {
        "mapping": {
            "department": {
                "columns": {
                    "id": "部門ID",
                    "name": "部門名",
                    "company.id": "所属会社ID",
                }
            }
        }
    }

    xml_path = tmp_path / "test.xml"
    output_path = tmp_path / "output.xlsx"
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(xml_content)

    converter = XmlToExcelConverter()
    converter.config = config
    converter.convert(str(xml_path), str(output_path))

    with pd.ExcelFile(output_path) as excel:
        df = pd.read_excel(excel, "department")
        assert "所属会社ID" in df.columns
        assert df.iloc[0]["所属会社ID"] == "C001"


def test_multilevel_hierarchy_mapping(tmp_path):
    """複数階層の親子関係マッピング機能をテスト"""
    xml_content = """
    <root>
        <organization>
            <id>O001</id>
            <name>組織1</name>
            <company>
                <id>C001</id>
                <name>会社1</name>
                <department>
                    <id>D001</id>
                    <name>開発部</name>
                </department>
            </company>
        </organization>
    </root>
    """

    config = {
        "mapping": {
            "department": {
                "columns": {
                    "id": "部門ID",
                    "name": "部門名",
                    "company.id": "所属会社ID",
                    "company.name": "所属会社名",
                    "organization.id": "組織ID",
                    "organization.name": "組織名",
                }
            }
        }
    }

    xml_path = tmp_path / "test.xml"
    output_path = tmp_path / "output.xlsx"
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(xml_content)

    converter = XmlToExcelConverter()
    converter.config = config
    converter.convert(str(xml_path), str(output_path))

    with pd.ExcelFile(output_path) as excel:
        df = pd.read_excel(excel, "department")
        assert list(df.columns) == [
            "部門ID",
            "部門名",
            "所属会社ID",
            "所属会社名",
            "組織ID",
            "組織名",
        ]
        assert df.iloc[0]["部門ID"] == "D001"
        assert df.iloc[0]["所属会社ID"] == "C001"
        assert df.iloc[0]["組織ID"] == "O001"
        assert df.iloc[0]["所属会社名"] == "会社1"
        assert df.iloc[0]["組織名"] == "組織1"


def test_partial_mapping(tmp_path):
    """部分的なマッピング機能をテスト"""
    xml_content = """
    <root>
        <department>
            <id>D001</id>
            <name>開発部</name>
            <code>DEV</code>
            <location>東京</location>
        </department>
    </root>
    """

    config = {
        "mapping": {"department": {"columns": {"id": "部門ID", "name": "部門名"}}}
    }

    xml_path = tmp_path / "test.xml"
    output_path = tmp_path / "output.xlsx"
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(xml_content)

    converter = XmlToExcelConverter()
    converter.config = config
    converter.convert(str(xml_path), str(output_path))

    with pd.ExcelFile(output_path) as excel:
        df = pd.read_excel(excel, "department")
        assert list(df.columns) == ["部門ID", "部門名"]
        assert "code" not in df.columns
        assert "location" not in df.columns


def test_attribute_mapping(tmp_path):
    """属性のマッピング機能をテスト"""
    xml_content = """
    <root>
        <department code="DEV" type="development">
            <id>D001</id>
            <name>開発部</name>
        </department>
    </root>
    """

    config = {
        "mapping": {
            "department": {
                "columns": {
                    "id": "部門ID",
                    "name": "部門名",
                    "@code": "部門コード",
                    "@type": "部門種別",
                }
            }
        }
    }

    xml_path = tmp_path / "test.xml"
    output_path = tmp_path / "output.xlsx"
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(xml_content)

    converter = XmlToExcelConverter()
    converter.config = config
    converter.convert(str(xml_path), str(output_path))

    with pd.ExcelFile(output_path) as excel:
        df = pd.read_excel(excel, "department")
        assert "部門コード" in df.columns
        assert "部門種別" in df.columns
        assert df.iloc[0]["部門コード"] == "DEV"
        assert df.iloc[0]["部門種別"] == "development"


def test_sibling_reference_mapping(tmp_path):
    """兄弟要素間の参照マッピング機能をテスト"""
    xml_content = """
    <root>
        <company>
            <id>C001</id>
            <departments>
                <department>
                    <id>D001</id>
                    <name>開発部</name>
                    <manager_id>E001</manager_id>
                </department>
                <employee>
                    <id>E001</id>
                    <name>山田太郎</name>
                    <department_id>D001</department_id>
                </employee>
            </departments>
        </company>
    </root>
    """

    config = {
        "mapping": {
            "department": {
                "columns": {
                    "id": "部門ID",
                    "name": "部門名",
                    "manager_id": "部門長ID",
                    "employee.name": "部門長名",
                }
            }
        }
    }

    xml_path = tmp_path / "test.xml"
    output_path = tmp_path / "output.xlsx"
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(xml_content)

    converter = XmlToExcelConverter()
    converter.config = config
    converter.convert(str(xml_path), str(output_path))

    with pd.ExcelFile(output_path) as excel:
        df = pd.read_excel(excel, "department")
        assert list(df.columns) == ["部門ID", "部門名", "部門長ID", "部門長名"]
        assert df.iloc[0]["部門長名"] == "山田太郎"
