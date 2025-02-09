"""CLIモジュールのテスト"""

from textwrap import dedent
import pytest
from xml2xlsx.cli import main
from xml2xlsx import __version__


def test_help_command(capsys):
    """ヘルプコマンドのテスト"""
    with pytest.raises(SystemExit) as e:
        main(["--help"])
    assert e.value.code == 0
    captured = capsys.readouterr()
    assert "利用可能なコマンド" in captured.out
    assert "convert" in captured.out
    assert "generate" in captured.out


def test_version_command(capsys):
    """バージョン表示のテスト"""
    with pytest.raises(SystemExit) as e:
        main(["--version"])
    assert e.value.code == 0
    captured = capsys.readouterr()
    assert __version__ in captured.out


def test_missing_command(capsys):
    """コマンドが指定されていない場合のテスト"""
    with pytest.raises(SystemExit) as e:
        main([])
    assert e.value.code == 2
    captured = capsys.readouterr()
    assert "コマンドが指定されていません" in captured.err


def test_convert_missing_args(capsys):
    """convert コマンドの必須引数漏れのテスト"""
    with pytest.raises(SystemExit) as e:
        main(["convert"])
    assert e.value.code == 2
    captured = capsys.readouterr()
    assert "--input" in captured.err


def test_generate_missing_args(capsys):
    """generate コマンドの必須引数漏れのテスト"""
    with pytest.raises(SystemExit) as e:
        main(["generate"])
    assert e.value.code == 2
    captured = capsys.readouterr()
    assert "--input" in captured.err


def test_convert_with_missing_files(tmp_path):
    """存在しないファイルを指定した場合のテスト"""
    input_file = tmp_path / "not_exists.xml"
    config_file = tmp_path / "not_exists.toml"
    output_file = tmp_path / "output.xlsx"

    result = main(["convert", "-i", str(input_file), "-c", str(config_file), "-o", str(output_file)])
    assert result == 1


def test_convert_xml_to_excel(tmp_path, capsys):
    """XMLからExcelへの変換テスト"""
    xml_content = dedent(
        """
        <?xml version="1.0" encoding="UTF-8"?>
        <orders>
            <order id="1">
                <order_date>2024-02-01</order_date>
                <customer_name>山田太郎</customer_name>
                <total_amount>10000</total_amount>
                <order_items>
                    <order_item>
                        <product_name>商品A</product_name>
                        <quantity>2</quantity>
                        <unit_price>1000</unit_price>
                    </order_item>
                    <order_item>
                        <product_name>商品B</product_name>
                        <quantity>1</quantity>
                        <unit_price>8000</unit_price>
                    </order_item>
                </order_items>
            </order>
        </orders>
        """
    ).lstrip()

    config_content = dedent(
        """
        [mapping."orders.order"]
        sheet_name = "注文一覧"

        [mapping."orders.order".columns]
        "@id" = "注文番号"
        "order_date" = "注文日"
        "customer_name" = "顧客名"
        "total_amount" = "合計金額"

        [mapping."orders.order.order_items.order_item"]
        sheet_name = "注文明細"

        [mapping."orders.order.order_items.order_item".columns]
        "product_name" = "商品名"
        "quantity" = "数量"
        "unit_price" = "単価"
        "order.@id" = "注文番号"
    """
    )

    xml_path = tmp_path / "test.xml"
    config_path = tmp_path / "config.toml"
    output_path = tmp_path / "output.xlsx"

    xml_path.write_text(xml_content)
    config_path.write_text(config_content)

    result = main(["convert", "-i", str(xml_path), "-c", str(config_path), "-o", str(output_path)])
    assert result == 0
    assert output_path.exists()
    captured = capsys.readouterr()
    assert "変換が完了しました" in captured.err


def test_convert_with_invalid_xml(tmp_path, capsys):
    """不正なXMLファイルの処理テスト"""
    invalid_xml = tmp_path / "invalid.xml"
    config_file = tmp_path / "config.toml"
    output_file = tmp_path / "output.xlsx"

    invalid_xml.write_text("This is not XML")
    config_content = dedent(
        """
        [mapping."root"]
        sheet_name = "test"

        [mapping."root".columns]
        text = "テキスト"
    """
    )
    config_file.write_text(config_content)

    result = main(["convert", "-i", str(invalid_xml), "-c", str(config_file), "-o", str(output_file)])
    assert result == 1
    captured = capsys.readouterr()
    assert "エラー" in captured.err


def test_invalid_sheet_name_error(tmp_path, capsys):
    """シート名エラーのテスト"""
    xml_content = dedent(
        """
        <?xml version="1.0" encoding="UTF-8"?>
        <root>
            <data>
                <text>テストデータ</text>
            </data>
        </root>
        """
    ).lstrip()
    xml_path = tmp_path / "test.xml"
    xml_path.write_text(xml_content)

    # 31文字超過のテスト
    config_content = dedent(
        """
        [mapping."root.data"]
        sheet_name = "this_is_a_very_long_sheet_name_that_exceeds_31_characters"

        [mapping."root.data".columns]
        text = "テキスト"
    """
    )
    config_path = tmp_path / "config1.toml"
    config_path.write_text(config_content)
    result = main(["convert", "-i", str(xml_path), "-c", str(config_path), "-o", str(tmp_path / "out1.xlsx")])
    assert result == 1
    captured = capsys.readouterr()
    assert "31文字制限を超えています" in captured.err


def test_japanese_error_messages(tmp_path, capsys):
    """日本語エラーメッセージのテスト"""
    # 1. 存在しないファイル
    result = main(["convert", "-i", "存在しない.xml", "-c", str(tmp_path / "config.toml"), "-o", "出力.xlsx"])
    assert result == 1
    captured = capsys.readouterr()
    assert "見つかりません" in captured.err

    # 2. 不正なXML
    xml_path = tmp_path / "invalid.xml"
    config_path = tmp_path / "config.toml"
    xml_path.write_text("不正なXML")

    config_content = dedent(
        """
        [mapping."root"]
        sheet_name = "テスト"

        [mapping."root".columns]
        "#text" = "データ"
    """
    )
    config_path.write_text(config_content)

    result = main(["convert", "-i", str(xml_path), "-c", str(config_path), "-o", str(tmp_path / "output.xlsx")])
    assert result == 1
    captured = capsys.readouterr()
    assert "エラー" in captured.err
