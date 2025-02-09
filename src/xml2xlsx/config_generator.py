"""設定ファイルの生成を行うモジュール"""

import logging
from pathlib import Path
from typing import Dict, List, Set
import xml.etree.ElementTree as ET
import toml

logger = logging.getLogger(__name__)


def _analyze_xml_structure(xml_file: str) -> Dict[str, Dict[str, Set[str]]]:
    """XMLファイルの構造を解析"""
    logger.info(f"入力XMLファイルの解析: {xml_file}")
    tree = ET.parse(xml_file)
    root = tree.getroot()
    entities: Dict[str, Dict[str, Set[str]]] = {}

    def process_element(element: ET.Element, parent_path: str = "") -> None:
        current_path = f"{parent_path}.{element.tag}" if parent_path else element.tag
        if current_path not in entities:
            entities[current_path] = {"attributes": set(), "elements": set()}

        # 属性を記録
        for attr in element.attrib:
            entities[current_path]["attributes"].add(attr)

        # テキストコンテンツを持つ子要素を記録
        for child in element:
            if isinstance(child.tag, str):
                process_element(child, current_path)
                if child.text and child.text.strip():
                    entities[current_path]["elements"].add(child.tag)

    process_element(root)
    return entities


def generate_config(input_files: List[str], output_file: str) -> None:
    """設定ファイルを生成する

    Args:
        input_files: 入力XMLファイルのリスト
        output_file: 出力する設定ファイルのパス

    Raises:
        FileNotFoundError: 入力ファイルが存在しない場合
        ValueError: 不正な設定や制限に違反する場合
    """
    logger.info(f"設定ファイル生成を開始: {output_file}")
    if not input_files:
        raise ValueError("入力XMLファイルが指定されていません")

    # XMLファイルの解析
    all_entities = []
    for xml_file in input_files:
        if not Path(xml_file).exists():
            raise FileNotFoundError(f"入力XMLファイル '{xml_file}' が見つかりません")
        entities = _analyze_xml_structure(xml_file)
        all_entities.append(entities)

    # 設定のマージ
    merged: Dict[str, Dict[str, Set[str]]] = {}
    for entities in all_entities:
        for path, definition in entities.items():
            if path not in merged:
                merged[path] = {"attributes": set(), "elements": set()}
            merged[path]["attributes"].update(definition["attributes"])
            merged[path]["elements"].update(definition["elements"])

    # 設定ファイルの生成
    config: Dict[str, Dict] = {"mapping": {}}
    for path, definition in merged.items():
        # シート名の長さチェック
        if len(path) > 31:
            raise ValueError(f"シート名が長すぎます: {path}")

        columns: Dict[str, str] = {}
        # 属性のマッピング
        for attr in sorted(definition["attributes"]):
            columns[f"@{attr}"] = attr

        # 要素のマッピング
        for elem in sorted(definition["elements"]):
            columns[elem] = elem

        config["mapping"][path] = {"sheet_name": path, "columns": columns}

    # 設定ファイルの保存
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        toml.dump(config, f)

    logger.info(f"設定ファイルを生成しました: {output_file}")
