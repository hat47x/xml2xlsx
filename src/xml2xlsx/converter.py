"""XMLからExcelへの変換を行うモジュール"""

import logging
from typing import Dict, List, Optional, Tuple, Set
import pandas as pd
import xml.etree.ElementTree as ET
from .entity import EntityContext, Entity
from .exceptions import ConfigurationError

logger = logging.getLogger(__name__)


class XmlToExcelConverter:
    """XMLからExcelへの変換を行うクラス"""

    def __init__(self, config_file: Optional[str] = None):
        """コンバーターの初期化

        Args:
            config_file: 設定ファイルのパス（オプション）
        """
        self.config: Dict = {}
        self.data_frames: Dict[str, pd.DataFrame] = {}
        self.processed_entities: Set[ET.Element] = set()  # 処理済み要素を追跡
        if config_file:
            self.load_config(config_file)

    def load_config(self, config_file: str) -> None:
        """設定ファイルを読み込む

        Args:
            config_file: 設定ファイルのパス

        Raises:
            ConfigurationError: 設定ファイルの読み込みに失敗した場合
        """
        try:
            import toml

            self.config = toml.load(config_file)
            self._validate_config()
        except Exception as e:
            raise ConfigurationError(f"設定ファイルの読み込みに失敗しました: {str(e)}")

    def _validate_config(self) -> None:
        """設定の妥当性を検証"""
        if not isinstance(self.config.get("mapping"), dict):
            raise ConfigurationError("'mapping' セクションが必要です")

        # シート名の長さチェック
        for path, mapping in self.config["mapping"].items():
            if "sheet_name" in mapping:
                sheet_name = mapping["sheet_name"]
                if len(sheet_name) > 31:
                    raise ConfigurationError(f"シート名 '{sheet_name}' がExcelの31文字制限を超えています")

    def convert(self, input_file: str, output_file: str) -> None:
        """XMLファイルをExcelに変換"""
        try:
            if not self.config:
                raise ConfigurationError("設定ファイルが必要です")

            self.data_frames.clear()
            self.processed_entities.clear()  # 処理済み要素をリセット
            tree = ET.parse(input_file)
            root = tree.getroot()
            self._process_root(root)
            self._save_to_excel(output_file)
        except ET.ParseError as e:
            logger.error(f"XMLファイルの解析に失敗しました: {e}")
            raise
        except Exception as e:
            logger.error(f"変換中にエラーが発生しました: {e}")
            raise

    def _find_mapping_config(self, path: str) -> Tuple[Optional[str], Optional[Dict]]:
        """パスに一致するマッピング設定を検索"""
        if not self.config.get("mapping"):
            return None, None

        # 完全一致を優先
        if path in self.config["mapping"]:
            return path, self.config["mapping"][path]

        # 末尾一致を確認
        for config_path, config in self.config["mapping"].items():
            if path.endswith(config_path):
                return config_path, config

        return None, None

    def _process_root(self, root: ET.Element) -> None:
        """ルート要素から処理を開始"""
        context = EntityContext()
        root_entity = context.process_xml_element(root)
        self._process_entity(root_entity, context)

    def _process_entity(self, entity: Entity, context: EntityContext) -> None:
        """エンティティを処理"""
        if entity.element in self.processed_entities:
            return

        # マッピング設定の確認
        config_path, config = self._find_mapping_config(entity.path)

        # コレクションかどうかを判定
        is_collection, child_tag = context.is_collection_element(entity.element)

        if is_collection and child_tag:
            # コレクション要素を処理
            for child in entity.element.findall(child_tag):
                child_entity = context.process_xml_element(child, entity.path, entity)
                row_data = self._extract_data(child_entity)
                if row_data:
                    sheet_name = self._get_sheet_name(child_entity.path)
                    df = pd.DataFrame([row_data])
                    if sheet_name in self.data_frames:
                        self.data_frames[sheet_name] = (
                            pd.concat([self.data_frames[sheet_name], df], ignore_index=True)
                            .dropna(how="all")
                            .reset_index(drop=True)
                        )
                    else:
                        self.data_frames[sheet_name] = df
                self.processed_entities.add(child)

        # 通常の要素の処理
        elif config:
            row_data = self._extract_data(entity)
            if row_data:
                sheet_name = self._get_sheet_name(entity.path)
                df = pd.DataFrame([row_data])
                if sheet_name not in self.data_frames:
                    self.data_frames[sheet_name] = df
                else:
                    self.data_frames[sheet_name] = (
                        pd.concat([self.data_frames[sheet_name], df], ignore_index=True)
                        .dropna(how="all")
                        .reset_index(drop=True)
                    )

        self.processed_entities.add(entity.element)

        # 子要素を処理
        for child in entity.element:
            if isinstance(child.tag, str):
                child_entity = context.process_xml_element(child, entity.path, entity)
                self._process_entity(child_entity, context)

    def _extract_data(self, entity: Entity) -> Optional[Dict]:
        """エンティティからデータを抽出"""
        config_path, mapping_config = self._find_mapping_config(entity.path)
        if not mapping_config or "columns" not in mapping_config:
            return None

        data = {}
        for source, target in mapping_config["columns"].items():
            value = None
            if "." in source:
                # 親要素からの値を取得
                value = self._extract_parent_value(entity, source)
            else:
                # 自身の要素または属性から値を取得
                value = entity.get_value(source)

            if value is not None:
                data[target] = str(value)

        return data if data else None

    def _extract_parent_value(self, entity: Entity, reference: str) -> Optional[str]:
        """親要素からの値を取得"""
        if "." not in reference:
            return None

        first, rest = reference.split(".", 1)
        if not entity.parent:
            return None

        if entity.parent.element.tag == first:
            return entity.parent.get_value(rest)

        # 親の親をたどる
        return self._extract_parent_value(entity.parent, reference)

    def _get_sheet_name(self, path: str) -> str:
        """パスからシート名を取得"""
        config_path, config = self._find_mapping_config(path)

        if config and "sheet_name" in config:
            sheet_name = str(config["sheet_name"])
        else:
            sheet_name = path.split(".")[-1]

        if len(sheet_name) > 31:
            raise ConfigurationError(f"シート名 '{sheet_name}' がExcelの31文字制限を超えています")

        return sheet_name

    def _save_to_excel(self, output_file: str) -> None:
        """データフレームをExcelファイルとして保存"""
        if not self.data_frames:
            raise ConfigurationError("保存するデータがありません")

        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
            for sheet_name, df in self.data_frames.items():
                if df.empty:
                    continue

                # カラム順序を設定から取得
                ordered_columns = self._get_ordered_columns(sheet_name)
                if ordered_columns:
                    ordered_columns = [col for col in ordered_columns if col in df.columns]
                    df = df[ordered_columns]

                df.to_excel(writer, sheet_name=sheet_name, index=False)

    def _get_ordered_columns(self, sheet_name: str) -> List[str]:
        """設定からカラムの順序を取得"""
        for path, config in self.config.get("mapping", {}).items():
            if sheet_name in [config.get("sheet_name"), path.split(".")[-1]]:
                if "columns" in config:
                    return list(config["columns"].values())
        return []
