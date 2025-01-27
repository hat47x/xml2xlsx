"""大規模データと複雑な階層構造のテストモジュール

以下の機能をテストします：
1. 複雑な階層関係の処理
2. 大規模データセットの処理
3. 多様なエンティティ間の関係
4. パフォーマンスの検証
"""

import pytest
from xml2xlsx.converter import XmlToExcelConverter
import pandas as pd
from pathlib import Path
import time
import logging

logger = logging.getLogger(__name__)


@pytest.fixture
def test_data_dir():
    """テストデータディレクトリのパスを提供"""
    return Path(__file__).parent / "test_data"


def test_complex_hierarchy(test_data_dir, tmp_path):
    """複雑な階層関係の処理をテスト"""
    xml_path = test_data_dir / "large_sample.xml"
    output_path = tmp_path / "output.xlsx"

    converter = XmlToExcelConverter(str(test_data_dir / "large_config.toml"))

    start_time = time.time()
    converter.convert(str(xml_path), str(output_path))
    processing_time = time.time() - start_time
    logger.info(f"Processing time: {processing_time:.2f} seconds")

    with pd.ExcelFile(output_path) as excel:
        # シートの存在確認
        expected_sheets = [
            "会社マスタ",
            "部門マスタ",
            "プロジェクト",
            "タスク",
            "サブタスク",
            "作業ログ",
            "社員マスタ",
            "スキル",
            "資格",
            "勤怠記録",
            "資産管理",
            "メンテナンス記録",
        ]
        for sheet in expected_sheets:
            assert sheet in excel.sheet_names

        # 会社マスタの検証
        company_df = pd.read_excel(excel, "会社マスタ")
        assert all(
            col in company_df.columns
            for col in ["会社ID", "会社名", "会社コード", "会社区分"]
        )

        # 部門マスタの検証
        department_df = pd.read_excel(excel, "部門マスタ")
        assert all(
            col in department_df.columns
            for col in ["部門ID", "部門名", "部門コード", "所属会社ID"]
        )

        # プロジェクトの検証
        project_df = pd.read_excel(excel, "プロジェクト")
        assert all(
            col in project_df.columns
            for col in [
                "プロジェクトID",
                "プロジェクト名",
                "開始日",
                "終了日",
                "ステータス",
                "優先度",
                "所属会社ID",
                "所属部門ID",
            ]
        )

        # データの整合性確認
        project = project_df.iloc[0]
        company_id = project["所属会社ID"]
        department_id = project["所属部門ID"]

        # 会社の存在確認
        assert any(company_df["会社ID"] == company_id)
        # 部門の存在確認
        assert any(department_df["部門ID"] == department_id)


def test_multiple_references(tmp_path):
    """複数の参照関係を持つデータの処理をテスト"""
    xml_content = """
    <root>
        <company>
            <id>C001</id>
            <name>テスト株式会社</name>
            <department>
                <id>D001</id>
                <name>開発部</name>
                <project>
                    <id>P001</id>
                    <name>プロジェクトA</name>
                    <task>
                        <id>T001</id>
                        <name>タスク1</name>
                        <assigned_to>E001</assigned_to>
                    </task>
                </project>
                <employee>
                    <id>E001</id>
                    <name>山田太郎</name>
                </employee>
            </department>
        </company>
    </root>
    """

    config = {
        "mapping": {
            "task": {
                "columns": {
                    "id": "タスクID",
                    "name": "タスク名",
                    "assigned_to": "担当者ID",
                    "company.id": "所属会社ID",
                    "department.id": "所属部門ID",
                    "project.id": "所属プロジェクトID",
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
        task_df = pd.read_excel(excel, "task")
        task = task_df.iloc[0]

        # 全ての参照が正しく設定されていることを確認
        assert task["タスクID"] == "T001"
        assert task["担当者ID"] == "E001"
        assert task["所属会社ID"] == "C001"
        assert task["所属部門ID"] == "D001"
        assert task["所属プロジェクトID"] == "P001"


def test_large_data_performance(tmp_path):
    """大規模データのパフォーマンスをテスト"""
    # 大規模なXMLを生成
    departments = []
    for i in range(100):  # 100部門
        employees = "\n".join(
            [
                f"""
            <employee>
                <id>E{i:03d}{j:03d}</id>
                <name>社員{i:03d}{j:03d}</name>
                <email>emp{i:03d}{j:03d}@example.com</email>
            </employee>
            """
                for j in range(10)  # 各部門10名の社員
            ]
        )

        departments.append(
            f"""
        <department>
            <id>D{i:03d}</id>
            <name>部門{i:03d}</name>
            {employees}
        </department>
        """
        )

    xml_content = f"""
    <root>
        <company>
            <id>C001</id>
            <name>テスト株式会社</name>
            <departments>
                {''.join(departments)}
            </departments>
        </company>
    </root>
    """

    xml_path = tmp_path / "test.xml"
    output_path = tmp_path / "output.xlsx"
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(xml_content)

    converter = XmlToExcelConverter()

    start_time = time.time()
    converter.convert(str(xml_path), str(output_path))
    processing_time = time.time() - start_time

    logger.info(f"Large data processing time: {processing_time:.2f} seconds")

    # 処理時間の検証（10秒以内を期待）
    assert (
        processing_time < 10.0
    ), f"Processing took too long: {processing_time:.2f} seconds"

    # 結果の検証
    with pd.ExcelFile(output_path) as excel:
        employee_df = pd.read_excel(excel, "employee")
        assert len(employee_df) == 1000  # 100部門 × 10名 = 1000名
        assert "company.id" in employee_df.columns
        assert "department.id" in employee_df.columns
