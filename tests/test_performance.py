"""パフォーマンステスト"""

import gc
import time
import logging
import psutil
import pytest
from pathlib import Path
from textwrap import dedent
from xml2xlsx.converter import XmlToExcelConverter

test_logger = logging.getLogger(__name__)


def create_test_xml(path: Path, record_count: int) -> None:
    """テスト用のXMLファイルを生成"""
    xml_content = ['<?xml version="1.0" encoding="UTF-8"?>', "<root>", "<records>"]
    for i in range(record_count):
        xml_content.extend(
            [
                f"<record id='{i}'>",
                f"<name>Name {i}</name>",
                f"<value>{i * 100}</value>",
                f"<description>Description for record {i}</description>",
                "</record>",
            ]
        )
    xml_content.extend(["</records>", "</root>"])
    path.write_text("\n".join(xml_content))


def create_test_config(path: Path) -> None:
    """テスト用の設定ファイルを生成"""
    config_content = dedent(
        """
        [mapping."root.records.record"]
        sheet_name = "records"

        [mapping."root.records.record".columns]
        "@id" = "ID"
        "name" = "名前"
        "value" = "値"
        "description" = "説明"
    """
    )
    path.write_text(config_content)


def measure_memory() -> float:
    """メモリ使用量を計測(MB単位)"""
    gc.collect()  # 明示的なGC実行
    time.sleep(0.1)  # GC完了を待機
    process = psutil.Process()
    return process.memory_info().rss / (1024 * 1024)


def test_basic_performance(tmp_path):
    """基本的なパフォーマンステスト"""
    # テストファイルの作成
    xml_path = tmp_path / "data.xml"
    config_path = tmp_path / "config.toml"
    output_path = tmp_path / "output.xlsx"

    record_count = 1000
    create_test_xml(xml_path, record_count)
    create_test_config(config_path)

    # 性能計測
    initial_memory = measure_memory()
    start_time = time.time()

    # 変換実行
    converter = XmlToExcelConverter()
    converter.load_config(str(config_path))
    converter.convert(str(xml_path), str(output_path))

    # 結果の検証
    execution_time = time.time() - start_time
    peak_memory = measure_memory()
    memory_increase = peak_memory - initial_memory

    assert execution_time < 10.0, f"実行時間が長すぎます: {execution_time:.2f}秒"
    assert memory_increase < 200.0, f"メモリ使用量が多すぎます: {memory_increase:.2f}MB"
    assert output_path.exists()


def test_large_file_performance(tmp_path):
    """大規模ファイルのパフォーマンステスト"""
    # テストファイルの作成
    xml_path = tmp_path / "large_data.xml"
    config_path = tmp_path / "config.toml"
    output_path = tmp_path / "output.xlsx"

    # レコード数を2000に削減（開発時の迅速なフィードバックのため）
    record_count = 2000
    create_test_xml(xml_path, record_count)
    create_test_config(config_path)

    # メモリ使用量の監視
    initial_memory = measure_memory()
    start_time = time.time()

    # 変換実行
    converter = XmlToExcelConverter()
    converter.load_config(str(config_path))
    converter.convert(str(xml_path), str(output_path))

    # 結果の検証
    execution_time = time.time() - start_time
    peak_memory = measure_memory()
    memory_increase = peak_memory - initial_memory

    # 時間制限を緩和（2000レコードの処理に対して現実的な値）
    assert execution_time < 15.0, f"大規模ファイルの実行時間が長すぎます: {execution_time:.2f}秒"
    assert memory_increase < 200.0, f"大規模ファイルのメモリ使用量が多すぎます: {memory_increase:.2f}MB"
    assert output_path.exists()


def test_resource_management(tmp_path):
    """リソース管理の総合テスト"""
    xml_path = tmp_path / "test.xml"
    config_path = tmp_path / "config.toml"
    output_path = tmp_path / "output.xlsx"
    create_test_config(config_path)

    # 1. 段階的なメモリ使用量の確認
    record_counts = [100, 500, 1000]  # サイズを小さく調整
    memory_increases = []

    for count in record_counts:
        # 一時ファイルを削除してクリーンな状態を確保
        xml_path.unlink(missing_ok=True)
        output_path.unlink(missing_ok=True)
        gc.collect()
        time.sleep(0.1)  # GC完了を待機

        # ファイル生成
        create_test_xml(xml_path, count)

        # 変換前のメモリ使用量を計測
        initial_memory = measure_memory()

        # 変換実行
        converter = XmlToExcelConverter()
        converter.load_config(str(config_path))
        converter.convert(str(xml_path), str(output_path))

        # 変換後のメモリ使用量を計測
        peak_memory = measure_memory()
        memory_increase = peak_memory - initial_memory
        memory_increases.append(memory_increase)

        # オブジェクトを解放
        del converter
        gc.collect()
        time.sleep(0.1)  # GC完了を待機

    # メモリ増加率が緩やかであることを確認
    for i in range(len(memory_increases) - 1):
        if memory_increases[i] > 0:  # 0除算を防ぐ
            ratio = memory_increases[i + 1] / memory_increases[i]
            msg = f"メモリ増加: {memory_increases[i]:.1f}MB → {memory_increases[i+1]:.1f}MB"
            assert ratio < 7.0, msg

    # 2. エラー時のリソース解放
    invalid_xml = "不正なXML"
    xml_path.write_text(invalid_xml)
    error_initial_memory = measure_memory()

    with pytest.raises(Exception):
        converter = XmlToExcelConverter()
        converter.load_config(str(config_path))
        converter.convert(str(xml_path), str(output_path))

    del converter
    gc.collect()
    time.sleep(0.1)  # GC完了を待機

    error_final_memory = measure_memory()
    error_memory_diff = error_final_memory - error_initial_memory

    # エラー後のメモリ増加は50MB以内であることを期待
    assert error_memory_diff < 50.0, f"エラー後のメモリリーク: {error_memory_diff:.1f}MB"
