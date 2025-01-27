"""XMLToExcelConverterの大規模データ処理テスト。"""

import pytest
import pandas as pd
from pathlib import Path
import xml.etree.ElementTree as ET

from xml2xlsx.converter import XmlToExcelConverter


@pytest.fixture
def test_data_dir() -> Path:
    """テストデータディレクトリのパスを返す。"""
    return Path(__file__).parent / "test_data"


@pytest.fixture
def converter(test_data_dir: Path) -> XmlToExcelConverter:
    """テスト用のコンバーターインスタンスを作成。"""
    config_path = test_data_dir / "large_config.toml"
    return XmlToExcelConverter(str(config_path))


def test_large_hierarchy_processing(
    converter: XmlToExcelConverter, test_data_dir: Path, tmp_path: Path
):
    """深い階層構造の処理をテスト。"""
    xml_path = test_data_dir / "large_sample.xml"
    output_path = tmp_path / "large_output.xlsx"

    # XMLファイルを変換
    converter.convert(str(xml_path), str(output_path))

    # 出力ファイルが作成されていることを確認
    assert output_path.exists()

    # Excelファイルを読み込んで検証
    with pd.ExcelFile(output_path) as excel:
        # 各シートの存在確認
        sheets = excel.sheet_names
        assert "会社マスタ" in sheets
        assert "部門マスタ" in sheets
        assert "プロジェクト" in sheets
        assert "タスク" in sheets
        assert "サブタスク" in sheets
        assert "作業ログ" in sheets
        assert "社員マスタ" in sheets
        assert "スキル" in sheets
        assert "資格" in sheets
        assert "勤怠記録" in sheets
        assert "資産管理" in sheets
        assert "メンテナンス記録" in sheets

        # データの検証例
        company_df = pd.read_excel(excel, "会社マスタ")
        assert "会社ID" in company_df.columns
        assert "会社名" in company_df.columns
        assert "会社コード" in company_df.columns
        assert "会社区分" in company_df.columns

        department_df = pd.read_excel(excel, "部門マスタ")
        assert "部門ID" in department_df.columns
        assert "部門名" in department_df.columns
        assert "所属会社ID" in department_df.columns
        assert "部門コード" in department_df.columns

        # 他のシートについても同様に検証を追加
        # 例: プロジェクトシートの検証
        project_df = pd.read_excel(excel, "プロジェクト")
        assert "プロジェクトID" in project_df.columns
        assert "プロジェクト名" in project_df.columns
        assert "開始日" in project_df.columns
        assert "終了日" in project_df.columns
        assert "ステータス" in project_df.columns
        assert "優先度" in project_df.columns
        assert "所属部門ID" in project_df.columns


def test_many_entities_processing(converter: XmlToExcelConverter, tmp_path: Path):
    """多数のエンティティを含むXMLの処理をテスト。"""
    # テストデータ生成
    root = ET.Element("root")
    companies = ET.SubElement(root, "companies")

    company_count = 10
    for i in range(company_count):
        company = ET.SubElement(companies, "company")
        company.set("code", f"C{i:03d}")
        company.set("type", "corporation")

        id_elem = ET.SubElement(company, "id")
        id_elem.text = f"COMP{i:03d}"
        name_elem = ET.SubElement(company, "name")
        name_elem.text = f"テスト株式会社{i:03d}"

        departments = ET.SubElement(company, "departments")
        for j in range(2):  # 各社2部門
            department = ET.SubElement(departments, "department")
            department.set("code", f"D{i:03d}{j:02d}")

            id_elem = ET.SubElement(department, "id")
            id_elem.text = f"DEPT{i:03d}{j:02d}"
            name_elem = ET.SubElement(department, "name")
            name_elem.text = f"部門{j:02d}"

    # テスト用XMLファイルを作成
    test_xml_path = tmp_path / "test_many_entities.xml"
    tree = ET.ElementTree(root)
    tree.write(str(test_xml_path), encoding="UTF-8", xml_declaration=True)

    # 変換を実行
    output_path = tmp_path / "test_many_entities_output.xlsx"
    converter.convert(str(test_xml_path), str(output_path))

    # 結果を検証
    with pd.ExcelFile(output_path) as excel:
        company_df = pd.read_excel(excel, "会社マスタ")
        department_df = pd.read_excel(excel, "部門マスタ")

        assert len(company_df) == company_count
        assert len(department_df) == company_count * 2


def test_element_and_attribute_handling(
    converter: XmlToExcelConverter, test_data_dir: Path, tmp_path: Path
):
    """XML要素と属性の処理を検証。"""
    xml_path = test_data_dir / "large_sample.xml"
    output_path = tmp_path / "attribute_test_output.xlsx"

    converter.convert(str(xml_path), str(output_path))

    with pd.ExcelFile(output_path) as excel:
        # プロジェクトシートの検証
        project_df = pd.read_excel(excel, "プロジェクト")
        # 要素から変換されたカラム
        assert "プロジェクトID" in project_df.columns
        assert "プロジェクト名" in project_df.columns
        assert "開始日" in project_df.columns
        assert "終了日" in project_df.columns
        # 属性から変換されたカラム
        assert "ステータス" in project_df.columns
        assert "優先度" in project_df.columns

        # タスクシートの検証
        task_df = pd.read_excel(excel, "タスク")
        assert len(task_df) > 0
        # 属性値の検証
        status_column = "タスクステータス"  # 設定ファイルでのマッピング名
        assert "in_progress" in task_df[status_column].values


if __name__ == "__main__":
    pytest.main([__file__])
