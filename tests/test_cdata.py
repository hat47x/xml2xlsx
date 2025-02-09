"""CDATAのテストモジュール"""

import os
import logging
from textwrap import dedent
from pathlib import Path
import pytest
from xml2xlsx.converter import XmlToExcelConverter, ConfigurationError

test_logger = logging.getLogger(__name__)


class TestCdataProcessing:
    """CDATAセクションの処理テスト"""

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """テストの前処理"""
        self.xml_file = tmp_path / "test.xml"
        self.config_file = tmp_path / "config.toml"
        self.output_file = tmp_path / "output.xlsx"

        # テスト用のXMLを作成（CDATAを含む）
        self._create_test_xml()
        self._create_test_config()

    def _create_test_xml(self):
        """テスト用のXMLファイルを作成"""
        xml_content = dedent(
            """
            <?xml version="1.0" encoding="UTF-8"?>
            <root>
                <item>
                    <description><![CDATA[This is a CDATA section with <special> characters]]></description>
                </item>
            </root>
        """
        ).lstrip()
        self.xml_file.write_text(xml_content)

    def _create_test_config(self):
        """テスト用の設定ファイルを作成"""
        config_content = dedent(
            """
            [mapping."root.item"]
            sheet_name = "items"

            [mapping."root.item".columns]
            description = "説明"
        """
        )
        self.config_file.write_text(config_content)

    def test_cdata_content_preservation(self):
        """CDATAの内容が正しく保持されることを確認"""
        converter = XmlToExcelConverter()
        converter.load_config(str(self.config_file))
        converter.convert(str(self.xml_file), str(self.output_file))

        # Excelファイルが生成されていることを確認
        assert self.output_file.exists()

        # 内容の検証（pandas経由で確認）
        import pandas as pd

        df = pd.read_excel(str(self.output_file))
        assert len(df) == 1
        assert df.iloc[0]["説明"] == "This is a CDATA section with <special> characters"

    def test_cdata_multiline_content(self):
        """複数行のCDATAが正しく処理されることを確認"""
        # 複数行のCDATAを含むXMLを作成
        xml_content = dedent(
            """
            <?xml version="1.0" encoding="UTF-8"?>
            <root>
                <item>
                    <description><![CDATA[Line 1
                    Line 2
                    Line 3]]></description>
                </item>
            </root>
        """
        ).lstrip()
        self.xml_file.write_text(xml_content)

        converter = XmlToExcelConverter()
        converter.load_config(str(self.config_file))
        converter.convert(str(self.xml_file), str(self.output_file))

        # 内容の検証
        import pandas as pd

        df = pd.read_excel(str(self.output_file))
        assert len(df) == 1
        assert df.iloc[0]["説明"].count("\n") == 2  # 改行が保持されていることを確認

    def test_cdata_special_characters(self):
        """特殊文字を含むCDATAが正しく処理されることを確認"""
        # 特殊文字を含むCDATAセクションを作成
        xml_content = dedent(
            """
            <?xml version="1.0" encoding="UTF-8"?>
            <root>
                <item>
                    <description><![CDATA[特殊文字: < > & " ' および 日本語]]></description>
                </item>
            </root>
        """
        ).lstrip()
        self.xml_file.write_text(xml_content)

        converter = XmlToExcelConverter()
        converter.load_config(str(self.config_file))
        converter.convert(str(self.xml_file), str(self.output_file))

        # 内容の検証
        import pandas as pd

        df = pd.read_excel(str(self.output_file))
        assert len(df) == 1
        assert df.iloc[0]["説明"] == "特殊文字: < > & \" ' および 日本語"

    def test_cdata_without_config(self):
        """設定ファイルなしでCDATAが正しく処理されることを確認"""
        converter = XmlToExcelConverter()
        with pytest.raises(ConfigurationError) as excinfo:
            converter.convert(str(self.xml_file), str(self.output_file))
        assert "設定ファイルが必要です" == str(excinfo.value)
