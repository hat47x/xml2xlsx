import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Union

import pandas as pd
import toml

from .entity import EntityContext

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class XmlToExcelConverter:
    """XMLからExcelへの変換を行うクラス"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Parameters:
            config_path: TOML設定ファイルのパス
        """
        self.config = (
            {"mapping": {}} if config_path is None else self._load_config(config_path)
        )

    def _load_config(self, config_path: str) -> dict:
        """TOML設定ファイルを読み込む"""
        config = toml.load(config_path)
        return {
            "mapping": self._flatten_mapping(
                config.get("entities", config.get("mapping", {}))
            )
        }

    def _flatten_mapping(self, mapping: Dict) -> Dict:
        """設定のマッピングをフラット化"""
        flattened = {}
        for entity_type, entity_config in mapping.items():
            flattened[entity_type] = {
                "sheet_name": entity_config.get("sheet_name", entity_type),
                "columns": self._flatten_columns(entity_config.get("columns", {})),
            }
            # primary_keysのみをサポート
            if "primary_keys" in entity_config:
                flattened[entity_type]["primary_keys"] = entity_config["primary_keys"]
            else:
                logger.error(f"'primary_keys' is required in config for {entity_type}")
                raise ValueError(
                    f"Missing required 'primary_keys' in config for {entity_type}"
                )
            logger.debug(
                f"Flattened config for {entity_type}: {flattened[entity_type]}"
            )
        return flattened

    def _flatten_columns(self, columns: Dict, prefix: str = "") -> Dict[str, str]:
        """カラムマッピングをフラット化"""
        flattened = {}
        for key, value in columns.items():
            if isinstance(value, dict):
                # 入れ子構造を処理（例: company: {id: '所属会社ID'}）
                nested = self._flatten_columns(value, f"{key}.")
                flattened.update(nested)
            else:
                full_key = f"{prefix}{key}"
                flattened[full_key] = value
                logger.debug(f"Mapped column {full_key} -> {value}")
        return flattened

    def _get_column_mapping(
        self, entity_type: str, data_columns: List[str]
    ) -> Dict[str, str]:
        """エンティティタイプに対するカラムマッピングを取得"""
        mapping = self.config["mapping"].get(entity_type, {})
        columns = mapping.get("columns", {})

        # マッピング設定がない場合は、データのカラムをそのまま使用
        if not columns:
            return {col: col for col in data_columns}

        # マッピング設定に従ってカラムを変換
        result = {}
        for source, target in columns.items():
            if source in data_columns:
                result[source] = target
                logger.debug(f"Mapped column {source} -> {target} for {entity_type}")

        return result

    def _create_dataframe(
        self, data_list: List[Dict[str, str]], entity_type: str
    ) -> pd.DataFrame:
        """エンティティデータからDataFrameを作成"""
        if not data_list:
            return pd.DataFrame()

        # データフレームを作成（すべての値を文字列として扱う）
        df = pd.DataFrame(data_list).astype(str)
        logger.debug(
            f"Created initial DataFrame for {entity_type}"
            f" with columns: {df.columns.tolist()}"
        )

        # カラムのマッピングと順序付け
        column_mapping = self._get_column_mapping(entity_type, df.columns.tolist())

        # マッピングに含まれるカラムのみを抽出し、順序を維持
        columns = [col for col in column_mapping.keys() if col in df.columns]
        if columns:
            try:
                df = df[columns]
                logger.debug(f"Reordered columns for {entity_type}: {columns}")
            except KeyError as e:
                logger.warning(f"Column reordering failed for {entity_type}: {e}")

        # カラム名を変換
        df = df.rename(columns=column_mapping)
        logger.debug(f"Final columns for {entity_type}: {df.columns.tolist()}")

        return df

    def convert(
        self,
        xml_input: Union[str, Path, bytes],
        output_path: Union[str, Path, None] = None,
    ) -> Union[bytes, None]:
        """XMLをExcelに変換"""
        # XMLを解析
        if isinstance(xml_input, (str, Path)):
            if str(xml_input).startswith("<?xml"):
                root = ET.fromstring(str(xml_input))
            else:
                tree = ET.parse(str(xml_input))
                root = tree.getroot()
        elif isinstance(xml_input, bytes):
            root = ET.fromstring(xml_input)
        else:
            raise ValueError("Unsupported input type")

        # エンティティを抽出
        context = EntityContext(root, self.config)
        logger.debug(f"Found entities: {list(context.entities.keys())}")

        if not context.entities:
            raise ValueError("No valid data found for any entity")

        # 設定がない場合は自動生成
        if not self.config["mapping"]:
            for tag, entities in context.entities.items():
                if entities:
                    first_data = entities[0].data
                    self.config["mapping"][tag] = {
                        "sheet_name": tag,
                        "columns": {field: field for field in first_data.keys()},
                    }
                    logger.debug(
                        f"Generated config for {tag}: {self.config['mapping'][tag]}"
                    )

        # Excelファイルに出力
        excel_buffer = pd.ExcelWriter(
            output_path if output_path else "output.xlsx", engine="openpyxl"
        )

        for entity_type, entity_config in self.config["mapping"].items():
            # エンティティのデータを取得
            data_list = context.get_entity_data(entity_type)
            if not data_list:
                logger.debug(f"No data found for {entity_type}")
                continue

            sheet_name = entity_config.get("sheet_name", entity_type)
            logger.debug(f"Processing sheet {sheet_name}")

            # データフレームを作成
            df = self._create_dataframe(data_list, entity_type)
            if df.empty:
                logger.warning(f"Empty DataFrame for {entity_type}")
                continue

            # シートを作成
            df.to_excel(excel_buffer, sheet_name=sheet_name, index=False)
            logger.debug(f"Created sheet {sheet_name}")

        excel_buffer.close()
        if output_path is None:
            with open("output.xlsx", "rb") as f:
                return f.read()
        return None
