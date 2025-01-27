import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)


class Entity:
    """XMLエンティティを表現するクラス"""

    def __init__(self, element: ET.Element, config: Optional[Dict] = None):
        """
        Parameters:
            element: XMLの要素
            config: エンティティの設定（オプション）
        """
        self.element = element
        self.config = config
        self.tag = element.tag
        self._data: Dict[str, str] = {}
        self._parent_refs: Dict[str, str] = {}
        self._sibling_refs: Dict[str, str] = {}

        # 基本データを抽出
        self._extract_data()

    def _extract_data(self) -> None:
        """要素からデータを抽出"""
        # ID要素を特別に処理
        id_elem = self.element.find("id")
        if id_elem is not None and id_elem.text:
            self._data["id"] = id_elem.text.strip()

        # 子要素からデータを抽出
        for child in self.element:
            if isinstance(child.tag, str) and child.text and child != id_elem:
                self._data[child.tag] = child.text.strip()

        # 属性を処理
        for name, value in self.element.attrib.items():
            self._data[f"@{name}"] = value

        logger.debug(f"Extracted data for {self.tag}: {self._data}")

    @property
    def id(self) -> Optional[str]:
        """エンティティのID"""
        return self._data.get("id")

    def add_parent_ref(self, parent_tag: str, ref_data: Dict[str, str]) -> None:
        """親エンティティの参照を追加"""
        for field, value in ref_data.items():
            ref_key = f"{parent_tag}.{field}"
            self._parent_refs[ref_key] = value
            logger.debug(f"Added parent reference for {self.tag}: {ref_key}={value}")

    def add_sibling_ref(self, sibling_type: str, ref_data: Dict[str, str]) -> None:
        """兄弟エンティティの参照を追加"""
        for key, value in ref_data.items():
            ref_key = f"{sibling_type}.{key}"
            self._sibling_refs[ref_key] = value
            logger.debug(f"Added sibling reference for {self.tag}: {ref_key}={value}")

    @property
    def data(self) -> Dict[str, str]:
        """エンティティの全データ（親参照と兄弟参照を含む）"""
        result = self._data.copy()
        result.update(self._parent_refs)
        result.update(self._sibling_refs)
        return result


class EntityContext:
    """エンティティ間の関係を管理するクラス"""

    def __init__(self, root: ET.Element, config: Optional[Dict] = None):
        """
        Parameters:
            root: XMLのルート要素
            config: 設定データ（オプション）
        """
        self.root = root
        self.config = config or {}
        self.entities: Dict[str, List[Entity]] = {}
        self._entity_map: Dict[str, Entity] = {}  # ID→エンティティのマップ
        self._parent_chain: Dict[ET.Element, List[ET.Element]] = {}  # 要素の親チェーン

        # 親子関係のマップを構築
        self._build_parent_chains(root)
        # エンティティを処理
        self._process_element(root)
        # 兄弟関係の参照を処理
        self._process_sibling_references()

    def _build_parent_chains(
        self, element: ET.Element, parents: Optional[List[ET.Element]] = None
    ) -> None:
        """要素の親チェーンを構築（ルート要素を除外）"""
        parents = parents or []

        # ルート要素とcompanies要素は親チェーンから除外
        if element != self.root and element.tag != "companies":
            parents = parents + [element]

        # 親チェーンを保存（ルート要素以外の場合）
        if element != self.root:
            self._parent_chain[element] = parents[:-1]  # 自身を除外

        # 子要素を処理
        for child in element:
            if isinstance(child.tag, str):
                self._build_parent_chains(child, parents)

    def _should_process_as_entity(self, element: ET.Element) -> bool:
        """要素をエンティティとして扱うべきかを判定"""
        # 設定がある場合はそれに従う
        if self.config.get("mapping", {}).get(element.tag):
            return True

        # 特定のタグは除外
        if element.tag in ["companies"]:
            return False

        # 属性があればエンティティとして扱う
        if element.attrib:
            return True

        # id要素があればエンティティとして扱う
        id_elem = element.find("id")
        if id_elem is not None and id_elem.text:
            return True

        # 子要素があればエンティティとして扱う
        for child in element:
            if isinstance(child.tag, str) and child.tag != "id":
                if child.text or child.attrib:
                    return True

        # テキストコンテンツがあればエンティティとして扱う
        if element.text and element.text.strip():
            return True

        return False

    def _has_meaningful_content(self, element: ET.Element) -> bool:
        """要素が意味のあるコンテンツを持つかを判定"""
        # 属性があれば有意
        if element.attrib:
            return True

        # id要素があれば有意
        id_elem = element.find("id")
        if id_elem is not None and id_elem.text:
            return True

        # テキストコンテンツがあれば有意
        if element.text and element.text.strip():
            return True

        # 子要素があれば有意
        for child in element:
            if isinstance(child.tag, str):
                if child.tag != "id":  # id以外の子要素
                    if child.text or child.attrib or list(child):
                        return True

        return False

    def _is_valid_collection_child(
        self, element: ET.Element, child: ET.Element
    ) -> bool:
        """子要素がコレクションの有効なメンバーかを判定"""
        # IDを持つ要素は有効
        id_elem = child.find("id")
        if id_elem is not None and id_elem.text:
            return True

        # タグ名の関係をチェック（複数形→単数形）
        if element.tag.endswith("s"):
            expected_child = element.tag[:-1]
            if child.tag == expected_child and self._has_meaningful_content(child):
                return True

        return False

    def is_collection_element(self, element: ET.Element) -> Tuple[bool, Optional[str]]:
        """要素がコレクション（同じタグの子要素の集まり）かどうかを判定

        Returns:
            (is_collection, child_tag): コレクションかどうかと、子要素のタグ
        """
        # 子要素を集計
        child_tags: Dict[str, int] = {}
        valid_children: Dict[str, int] = {}  # 有効な子要素のカウント

        for child in element:
            if isinstance(child.tag, str):
                child_tags[child.tag] = child_tags.get(child.tag, 0) + 1
                if self._is_valid_collection_child(element, child):
                    valid_children[child.tag] = valid_children.get(child.tag, 0) + 1

        # 有効な子要素がない場合
        if not valid_children:
            return False, None

        # 単一のタグのみを持つ場合の処理
        if len(child_tags) == 1:
            tag, count = next(iter(child_tags.items()))
            valid_count = valid_children.get(tag, 0)

            # 有効な子要素が複数ある場合、または
            # 単一の要素でもIDを持つ場合はコレクション
            if valid_count > 1 or (valid_count == 1 and element.tag.endswith("s")):
                return True, tag

        return False, None

    def _extract_element_data(self, element: ET.Element) -> Dict[str, str]:
        """要素からすべてのデータを抽出"""
        data = {}

        # ID要素を特別に処理
        id_elem = element.find("id")
        if id_elem is not None and id_elem.text:
            data["id"] = id_elem.text.strip()

        # その他の子要素を処理
        for child in element:
            if isinstance(child.tag, str) and child.text and child != id_elem:
                data[child.tag] = child.text.strip()

        # 属性を処理
        for name, value in element.attrib.items():
            data[f"@{name}"] = value

        return data

    def _process_element(self, element: ET.Element) -> None:
        """要素を再帰的に処理"""
        if isinstance(element.tag, str):
            # エンティティとして処理
            if self._should_process_as_entity(element):
                entity = Entity(
                    element, self.config.get("mapping", {}).get(element.tag)
                )

                # エンティティをIDでマップに登録
                if entity.id:
                    self._entity_map[entity.id] = entity

                # タグでリストに登録
                if element.tag not in self.entities:
                    self.entities[element.tag] = []
                self.entities[element.tag].append(entity)

                # 親要素の参照を追加
                for parent in self._parent_chain.get(element, []):
                    if self._should_process_as_entity(parent):
                        parent_data = self._extract_element_data(parent)
                        entity.add_parent_ref(parent.tag, parent_data)

            # 子要素を処理
            for child in element:
                self._process_element(child)

    def _get_entity_id(self, element: ET.Element) -> Optional[str]:
        """要素のIDを取得"""
        id_elem = element.find("id")
        return id_elem.text.strip() if id_elem is not None and id_elem.text else None

    def _process_sibling_references(self) -> None:
        """兄弟要素間の参照を処理"""
        for entity_type, entities in self.entities.items():
            mapping = self.config.get("mapping", {}).get(entity_type, {})
            columns = mapping.get("columns", {})

            # 参照が必要なカラムを特定
            ref_columns = {
                k: v for k, v in columns.items() if "." in k and not k.startswith("@")
            }

            for entity in entities:
                for ref_key, _ in ref_columns.items():
                    parts = ref_key.split(".")
                    if len(parts) == 2:
                        ref_type, ref_field = parts
                        # 親参照として既に処理されているものはスキップ
                        if ref_key not in entity._parent_refs:
                            # manager_idなどの参照フィールドを探す
                            ref_id = (
                                entity._data.get("manager_id")
                                if ref_type == "employee"
                                else None
                            )
                            if ref_id and ref_type in self.entities:
                                # 参照先のエンティティを検索
                                for ref_entity in self.entities[ref_type]:
                                    if ref_entity.id == ref_id:
                                        # 参照データを追加
                                        ref_data = {
                                            field: ref_entity._data.get(field, "")
                                            for field in [ref_field]
                                            if field in ref_entity._data
                                        }
                                        entity.add_sibling_ref(ref_type, ref_data)
                                        break

    def get_entity_data(self, entity_type: str) -> List[Dict[str, str]]:
        """指定したタイプのエンティティのデータを取得"""
        entities = self.entities.get(entity_type, [])
        mapping = self.config.get("mapping", {}).get(entity_type, {})
        columns = mapping.get("columns")

        result = []
        for entity in entities:
            data = entity.data
            if columns:
                # OrderedDictを使用してカラム順序を保持
                mapped_data = OrderedDict()
                # columnsの定義順でデータを格納
                for source_key in columns.keys():
                    target_key = columns[source_key]
                    if source_key in data:
                        mapped_data[target_key] = data[source_key]
                        logger.debug(
                            f"Mapped {entity_type}.{source_key} ="
                            f" {data[source_key]} -> {target_key}"
                        )
                data = mapped_data

            if data:  # 空でないデータのみを追加
                result.append(data)

        logger.debug(f"Retrieved {len(result)} records for {entity_type}")
        return result
