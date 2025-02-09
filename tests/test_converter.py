"""Converterのテストモジュール"""

from textwrap import dedent
import pytest
import pandas as pd
from xml2xlsx.converter import XmlToExcelConverter, ConfigurationError


def test_simple_xml_conversion(tmp_path):
    """基本的なXML変換のテスト"""
    xml_content = dedent(
        """
        <root>
            <item>
                <name>Test Item</name>
                <price>100</price>
            </item>
        </root>
    """
    ).lstrip()

    config_content = dedent(
        """
        [mapping."root.item"]
        sheet_name = "商品"

        [mapping."root.item".columns]
        name = "商品名"
        price = "価格"
    """
    )

    xml_path = tmp_path / "test.xml"
    config_path = tmp_path / "config.toml"
    output_path = tmp_path / "output.xlsx"

    xml_path.write_text(xml_content)
    config_path.write_text(config_content)

    converter = XmlToExcelConverter()
    converter.load_config(str(config_path))
    converter.convert(str(xml_path), str(output_path))

    assert output_path.exists()
    df = pd.read_excel(output_path, sheet_name="商品", dtype=str)
    assert df.iloc[0]["商品名"] == "Test Item"
    assert df.iloc[0]["価格"] == "100"


def test_configuration_required(tmp_path):
    """設定が必要なことをテスト"""
    xml_content = dedent(
        """
        <root>
            <item>
                <name>Test Item</name>
            </item>
        </root>
    """
    ).lstrip()

    xml_path = tmp_path / "test.xml"
    output_path = tmp_path / "output.xlsx"
    xml_path.write_text(xml_content)

    converter = XmlToExcelConverter()
    with pytest.raises(ConfigurationError) as excinfo:
        converter.convert(str(xml_path), str(output_path))
    assert "設定ファイルが必要です" == str(excinfo.value)


def test_multi_sheet_output(tmp_path):
    """複数シートの出力テスト"""
    xml_content = dedent(
        """
        <root>
            <categories>
                <category>
                    <name>Category 1</name>
                    <products>
                        <product>
                            <name>Product 1</name>
                            <price>100</price>
                        </product>
                    </products>
                </category>
            </categories>
        </root>
    """
    ).lstrip()

    config_content = dedent(
        """
        [mapping."root.categories.category"]
        sheet_name = "カテゴリ"

        [mapping."root.categories.category".columns]
        name = "カテゴリ名"

        [mapping."root.categories.category.products.product"]
        sheet_name = "商品"

        [mapping."root.categories.category.products.product".columns]
        name = "商品名"
        price = "価格"
        "category.name" = "カテゴリ名"
    """
    )

    xml_path = tmp_path / "test.xml"
    config_path = tmp_path / "config.toml"
    output_path = tmp_path / "output.xlsx"

    xml_path.write_text(xml_content)
    config_path.write_text(config_content)

    converter = XmlToExcelConverter()
    converter.load_config(str(config_path))
    converter.convert(str(xml_path), str(output_path))

    with pd.ExcelFile(output_path) as excel:
        assert "カテゴリ" in excel.sheet_names
        assert "商品" in excel.sheet_names


def test_data_preserve_order(tmp_path):
    """データの順序が保持されることを確認するテスト"""
    xml_content = dedent(
        """
        <?xml version="1.0" encoding="UTF-8"?>
        <root>
            <items>
                <item id="1">
                    <name>商品A</name>
                    <price>1000</price>
                    <category>電化製品</category>
                </item>
                <item id="2">
                    <name>商品A</name>
                    <price>1000</price>
                    <category>電化製品</category>
                </item>
                <item id="3">
                    <name>商品B</name>
                    <price>2000</price>
                    <category>家具</category>
                </item>
                <item id="3">
                    <name>商品B</name>
                    <price>2000</price>
                    <category>家具</category>
                </item>
            </items>
        </root>
    """
    ).lstrip()

    config_content = dedent(
        """
        [mapping."root.items.item"]
        sheet_name = "商品一覧"

        [mapping."root.items.item".columns]
        "@id" = "商品ID"
        name = "商品名"
        price = "価格"
        category = "カテゴリ"
    """
    )

    xml_path = tmp_path / "test.xml"
    config_path = tmp_path / "config.toml"
    output_path = tmp_path / "output.xlsx"

    xml_path.write_text(xml_content)
    config_path.write_text(config_content)

    converter = XmlToExcelConverter()
    converter.load_config(str(config_path))
    converter.convert(str(xml_path), str(output_path))

    df = pd.read_excel(output_path, sheet_name="商品一覧", dtype=str)

    # データ数が正しく、順序が保持されていることを確認
    assert len(df) == 4, "XMLの要素数と一致していません"
    assert df["商品ID"].tolist() == ["1", "2", "3", "3"], "データの順序が保持されていません"
    assert df["商品名"].tolist() == ["商品A", "商品A", "商品B", "商品B"]
    assert df["カテゴリ"].tolist() == ["電化製品", "電化製品", "家具", "家具"]


def test_custom_sheet_names(tmp_path):
    """カスタムシート名のテスト"""
    xml_content = dedent(
        """
        <root>
            <data>
                <value>Test</value>
            </data>
        </root>
    """
    ).lstrip()

    config_content = dedent(
        """
        [mapping."root.data"]
        sheet_name = "カスタムシート"

        [mapping."root.data".columns]
        value = "値"
    """
    )

    xml_path = tmp_path / "test.xml"
    config_path = tmp_path / "config.toml"
    output_path = tmp_path / "output.xlsx"

    xml_path.write_text(xml_content)
    config_path.write_text(config_content)

    converter = XmlToExcelConverter()
    converter.load_config(str(config_path))
    converter.convert(str(xml_path), str(output_path))

    with pd.ExcelFile(output_path) as excel:
        assert "カスタムシート" in excel.sheet_names
