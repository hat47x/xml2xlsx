import unittest
from pathlib import Path
import pandas as pd
import os
from xml2xlsx import XmlToExcelConverter


class TestCdataProcessing(unittest.TestCase):
    def setUp(self):
        """テストの前準備"""
        self.test_data_dir = Path(__file__).parent / "test_data"
        self.config_file = str(self.test_data_dir / "cdata_config.toml")
        self.xml_file = str(self.test_data_dir / "cdata_sample.xml")
        self.output_file = str(self.test_data_dir / "cdata_output.xlsx")

    def tearDown(self):
        """テスト後のクリーンアップ"""
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

    def test_cdata_content_preservation(self):
        """CDATAセクションの内容が正しく保持されることを確認"""
        converter = XmlToExcelConverter(self.config_file)
        converter.convert(self.xml_file, self.output_file)

        # 出力ファイルの存在確認
        self.assertTrue(os.path.exists(self.output_file))

        # Excelファイルの内容確認
        with pd.ExcelFile(self.output_file) as excel:
            # シートの存在確認
            self.assertIn("注文", excel.sheet_names)

            # データの確認
            orders_df = pd.read_excel(excel, "注文")

            # 1件目の注文のCDATAコンテンツを確認
            first_order = orders_df.iloc[0]
            self.assertEqual(first_order["メモ"], "特別な記号を含むメモ: <>&\"'")
            self.assertEqual(
                first_order["説明"],
                "複数行の説明\n改行を含む内容\nタグのような文字列: <tag>値</tag>",
            )

            # 2件目の注文のCDATAコンテンツを確認
            second_order = orders_df.iloc[1]
            self.assertEqual(second_order["メモ"], "HTML形式のメモ: <b>重要</b>")
            self.assertTrue(
                "SQL文を含む説明:\nSELECT * FROM orders WHERE id = 'ORD002'"
                in second_order["説明"]
            )

    def test_cdata_special_characters(self):
        """CDATAセクション内の特殊文字が正しく処理されることを確認"""
        converter = XmlToExcelConverter(self.config_file)
        converter.convert(self.xml_file, self.output_file)

        with pd.ExcelFile(self.output_file) as excel:
            orders_df = pd.read_excel(excel, "注文")

            # 特殊文字を含むデータの確認
            first_order = orders_df.iloc[0]
            self.assertIn("<>&\"'", first_order["メモ"])
            self.assertIn("<tag>値</tag>", first_order["説明"])

    def test_cdata_multiline_content(self):
        """CDATAセクション内の複数行コンテンツが正しく処理されることを確認"""
        converter = XmlToExcelConverter(self.config_file)
        converter.convert(self.xml_file, self.output_file)

        with pd.ExcelFile(self.output_file) as excel:
            orders_df = pd.read_excel(excel, "注文")

            # 複数行データの確認
            first_order = orders_df.iloc[0]
            description_lines = first_order["説明"].split("\n")
            self.assertEqual(len(description_lines), 3)
            self.assertEqual(description_lines[0], "複数行の説明")
            self.assertEqual(description_lines[1], "改行を含む内容")

    def test_cdata_without_config(self):
        """設定ファイルなしでCDATAが正しく処理されることを確認"""
        # 設定ファイルを指定せずにコンバーターを初期化
        converter = XmlToExcelConverter()
        converter.convert(self.xml_file, self.output_file)

        # 出力ファイルの存在確認
        self.assertTrue(os.path.exists(self.output_file))

        # Excelファイルの内容確認
        with pd.ExcelFile(self.output_file) as excel:
            # シートの存在確認
            self.assertIn("order", excel.sheet_names)

            # データの確認
            orders_df = pd.read_excel(excel, "order")

            # データが正しく取り込まれていることを確認
            self.assertEqual(len(orders_df), 2)  # 2件のデータ

            # カラムの確認
            expected_columns = {"id", "customer_name", "notes", "description"}
            self.assertTrue(all(col in orders_df.columns for col in expected_columns))

            # CDATAの内容が正しく保持されていることを確認
            first_order = orders_df.iloc[0]
            self.assertEqual(first_order["notes"], "特別な記号を含むメモ: <>&\"'")
            self.assertIn("複数行の説明", first_order["description"])
            self.assertIn("<tag>値</tag>", first_order["description"])

            # 2件目のデータも確認
            second_order = orders_df.iloc[1]
            self.assertEqual(second_order["notes"], "HTML形式のメモ: <b>重要</b>")
            self.assertIn("SQL文を含む説明", second_order["description"])


if __name__ == "__main__":
    unittest.main()
