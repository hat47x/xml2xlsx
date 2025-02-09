"""設定ファイル生成機能のテスト"""

import tempfile
import warnings
from pathlib import Path
import pytest
from xml2xlsx.config_generator import generate_config


def test_generate_config_basic():
    """基本的な設定ファイル生成のテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        xml_content = """
        <root>
            <item>
                <id>1</id>
                <name>Test</name>
            </item>
        </root>
        """
        xml_path = Path(tmpdir) / "test.xml"
        xml_path.write_text(xml_content)
        config_path = Path(tmpdir) / "config.toml"

        generate_config(input_files=[str(xml_path)], output_file=str(config_path))
        assert config_path.exists()
        content = config_path.read_text()
        assert "mapping" in content
        assert "item" in content
        assert "id" in content
        assert "name" in content


def test_generate_config_multiple_sources():
    """複数のXMLファイルからの設定生成をテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        xml1_content = """
        <root>
            <item>
                <id>1</id>
            </item>
        </root>
        """
        xml2_content = """
        <root>
            <item>
                <name>Test</name>
            </item>
        </root>
        """
        xml1_path = Path(tmpdir) / "test1.xml"
        xml2_path = Path(tmpdir) / "test2.xml"
        xml1_path.write_text(xml1_content)
        xml2_path.write_text(xml2_content)
        config_path = Path(tmpdir) / "config.toml"

        generate_config(
            input_files=[str(xml1_path), str(xml2_path)],
            output_file=str(config_path),
        )
        content = config_path.read_text()
        assert "id" in content
        assert "name" in content


def test_generate_config_nested_paths():
    """異なるパスのエンティティ生成をテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        xml_content = """
        <orders>
            <domestic>
                <order>
                    <order_id>D001</order_id>
                </order>
            </domestic>
            <overseas>
                <order>
                    <order_id>O001</order_id>
                </order>
            </overseas>
        </orders>
        """
        xml_path = Path(tmpdir) / "test.xml"
        xml_path.write_text(xml_content)
        config_path = Path(tmpdir) / "config.toml"

        generate_config(input_files=[str(xml_path)], output_file=str(config_path))
        content = config_path.read_text()
        assert "domestic.order" in content
        assert "overseas.order" in content


def test_generate_config_invalid_xml():
    """不正なXMLファイルの処理をテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        xml_path = Path(tmpdir) / "invalid.xml"
        xml_path.write_text("This is not XML")
        config_path = Path(tmpdir) / "config.toml"

        with pytest.raises(Exception):
            generate_config(input_files=[str(xml_path)], output_file=str(config_path))


def test_generate_config_missing_file():
    """存在しないファイルの処理をテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        xml_path = Path(tmpdir) / "missing.xml"
        config_path = Path(tmpdir) / "config.toml"

        with pytest.raises(FileNotFoundError):
            generate_config(input_files=[str(xml_path)], output_file=str(config_path))


def test_generate_config_empty_file():
    """空のXMLファイルの処理をテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        xml_content = "<root></root>"
        xml_path = Path(tmpdir) / "empty.xml"
        xml_path.write_text(xml_content)
        config_path = Path(tmpdir) / "config.toml"

        generate_config(input_files=[str(xml_path)], output_file=str(config_path))
        assert config_path.exists()
        content = config_path.read_text()
        assert "mapping" in content


def test_generate_config_type_mismatch():
    """型の不一致の処理をテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        xml_content = """
        <root>
            <item>
                <id>1</id>
                <value>text</value>
            </item>
            <item>
                <id>2</id>
                <value>123</value>
            </item>
        </root>
        """
        xml_path = Path(tmpdir) / "test.xml"
        xml_path.write_text(xml_content)
        config_path = Path(tmpdir) / "config.toml"

        generate_config(input_files=[str(xml_path)], output_file=str(config_path))
        content = config_path.read_text()
        assert "value" in content


def test_generate_config_long_sheet_name():
    """長いシート名のテスト（エラーの確認）"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 長いパスを持つXMLの作成
        xml_content = """
        <very>
            <long>
                <path>
                    <that>
                        <exceeds>
                            <excel>
                                <sheet>
                                    <name>
                                        <limit>
                                            <test>value</test>
                                        </limit>
                                    </name>
                                </sheet>
                            </excel>
                        </exceeds>
                    </that>
                </path>
            </long>
        </very>
        """
        xml_path = Path(tmpdir) / "test.xml"
        xml_path.write_text(xml_content)
        config_path = Path(tmpdir) / "config.toml"

        with pytest.raises(ValueError) as exc_info:
            generate_config(input_files=[str(xml_path)], output_file=str(config_path))
        assert "シート名が長すぎます" in str(exc_info.value)
