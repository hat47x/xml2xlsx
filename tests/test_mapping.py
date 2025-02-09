"""マッピング機能のテスト"""

from textwrap import dedent
import pytest
import pandas as pd
from xml2xlsx.converter import XmlToExcelConverter


def test_basic_column_mapping(tmp_path):
    """基本的なカラムマッピング機能をテスト"""
    xml_content = dedent(
        """
        <root>
            <item>
                <code>001</code>
                <name>Item 1</name>
            </item>
        </root>
    """
    )

    config = {"mapping": {"root.item": {"columns": {"code": "商品コード", "name": "商品名"}}}}

    xml_path = tmp_path / "test.xml"
    output_path = tmp_path / "output.xlsx"
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(xml_content)

    converter = XmlToExcelConverter()
    converter.config = config
    converter.convert(str(xml_path), str(output_path))

    with pd.ExcelFile(output_path) as excel:
        df = pd.read_excel(excel, "item", dtype=str)
        assert list(df.columns) == ["商品コード", "商品名"]
        assert df.iloc[0]["商品コード"] == "001"
        assert df.iloc[0]["商品名"] == "Item 1"


def test_nested_mapping(tmp_path):
    """ネストされた要素のマッピング機能をテスト"""
    xml_content = dedent(
        """
        <root>
            <order>
                <header>
                    <code>O001</code>
                    <date>2024-01-01</date>
                </header>
                <details>
                    <item>
                        <code>001</code>
                        <quantity>2</quantity>
                    </item>
                </details>
            </order>
        </root>
    """
    )

    config = {
        "mapping": {
            "root.order.details.item": {
                "sheet_name": "items",
                "columns": {"code": "商品コード", "quantity": "数量"},
            },
            "root.order.header": {
                "sheet_name": "headers",
                "columns": {"code": "注文番号", "date": "注文日"},
            },
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
        items_df = pd.read_excel(excel, "items", dtype=str)
        assert list(items_df.columns) == ["商品コード", "数量"]
        assert items_df.iloc[0]["商品コード"] == "001"

        header_df = pd.read_excel(excel, "headers", dtype=str)
        assert list(header_df.columns) == ["注文番号", "注文日"]
        assert header_df.iloc[0]["注文番号"] == "O001"


def test_parent_reference_mapping(tmp_path):
    """親要素への参照をマッピングするテスト"""
    xml_content = dedent(
        """
        <root>
            <organization name="Org1">
                <department name="Dev1">
                    <employee name="Emp1"/>
                </department>
            </organization>
        </root>
    """
    )

    config = {
        "mapping": {
            "root.organization.department.employee": {
                "sheet_name": "employees",
                "columns": {
                    "@name": "社員名",
                    "department.@name": "部門名",
                    "organization.@name": "組織名",
                },
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
        df = pd.read_excel(excel, "employees", dtype=str)
        assert list(df.columns) == ["社員名", "部門名", "組織名"]
        assert df.iloc[0]["社員名"] == "Emp1"
        assert df.iloc[0]["部門名"] == "Dev1"
        assert df.iloc[0]["組織名"] == "Org1"


def test_attribute_mapping(tmp_path):
    """属性のマッピング機能をテスト"""
    xml_content = dedent(
        """
        <root>
            <item code="001" type="normal">
                <name>Item 1</name>
            </item>
        </root>
    """
    )

    config = {
        "mapping": {
            "root.item": {
                "sheet_name": "items",
                "columns": {
                    "@code": "商品コード",
                    "@type": "種別",
                    "name": "商品名",
                },
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
        df = pd.read_excel(excel, "items", dtype=str)
        assert list(df.columns) == ["商品コード", "種別", "商品名"]
        assert df.iloc[0]["商品コード"] == "001"
        assert df.iloc[0]["種別"] == "normal"
        assert df.iloc[0]["商品名"] == "Item 1"


def test_multiple_parent_references(tmp_path):
    """複数の親要素への参照をテスト"""
    xml_content = dedent(
        """
        <root>
            <company code="C001">
                <department code="D001">
                    <project code="P001">
                        <task name="Task1"/>
                    </project>
                </department>
            </company>
        </root>
    """
    )

    config = {
        "mapping": {
            "root.company.department.project.task": {
                "sheet_name": "tasks",
                "columns": {
                    "@name": "タスク名",
                    "project.@code": "プロジェクトコード",
                    "department.@code": "部門コード",
                    "company.@code": "会社コード",
                },
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
        df = pd.read_excel(excel, "tasks", dtype=str)
        assert list(df.columns) == [
            "タスク名",
            "プロジェクトコード",
            "部門コード",
            "会社コード",
        ]
        assert df.iloc[0]["タスク名"] == "Task1"
        assert df.iloc[0]["プロジェクトコード"] == "P001"
        assert df.iloc[0]["部門コード"] == "D001"
        assert df.iloc[0]["会社コード"] == "C001"


def test_custom_sheet_names(tmp_path):
    """カスタムシート名の設定をテスト"""
    xml_content = dedent(
        """
        <root>
            <item>
                <code>001</code>
                <name>Item 1</name>
            </item>
        </root>
    """
    )

    config = {
        "mapping": {
            "root.item": {
                "sheet_name": "商品マスタ",
                "columns": {"code": "商品コード", "name": "商品名"},
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
        assert "商品マスタ" in excel.sheet_names
        df = pd.read_excel(excel, "商品マスタ", dtype=str)
        assert list(df.columns) == ["商品コード", "商品名"]
        assert df.iloc[0]["商品コード"] == "001"
        assert df.iloc[0]["商品名"] == "Item 1"
