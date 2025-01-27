"""パフォーマンステストモジュール

以下の観点でテストを行います：
1. 大規模XMLファイルの処理
2. メモリ使用量の監視
3. 処理時間の計測
"""

import pytest
import time
import psutil
import os
from pathlib import Path
from xml2xlsx.converter import XmlToExcelConverter


def get_memory_usage():
    """現在のプロセスのメモリ使用量をMB単位で返す"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024


def generate_large_xml(size: int) -> str:
    """テスト用の大規模XMLを生成"""
    items = []
    for i in range(size):
        items.append(
            f"""
            <item>
                <id>{i:05d}</id>
                <name>Product {i}</name>
                <price>{i * 100}</price>
                <description>{"Description " * 10}</description>
            </item>
            """
        )
    return f'<root>{"".join(items)}</root>'


@pytest.mark.slow
def test_large_data_processing(tmp_path):
    """大規模データ処理のパフォーマンステスト"""
    # 10,000アイテムのXMLを生成
    size = 10_000
    xml_content = generate_large_xml(size)

    xml_path = tmp_path / "large_test.xml"
    output_path = tmp_path / "large_output.xlsx"

    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(xml_content)

    # メモリ使用量の初期値を記録
    start_memory = get_memory_usage()
    start_time = time.time()

    # 変換を実行
    converter = XmlToExcelConverter()
    converter.convert(str(xml_path), str(output_path))

    # 処理時間とメモリ使用量を計測
    end_time = time.time()
    end_memory = get_memory_usage()

    processing_time = end_time - start_time
    memory_increase = end_memory - start_memory

    # アサーション
    assert (
        processing_time < 60
    ), f"処理に{processing_time}秒かかりました（期待値: 60秒未満）"
    assert (
        memory_increase < 500
    ), f"メモリ使用量が{memory_increase}MB増加しました（期待値: 500MB未満）"
    assert output_path.exists(), "出力ファイルが生成されていません"
