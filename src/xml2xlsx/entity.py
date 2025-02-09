"""XML"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple, Set


class Entity:
    """XMLエンティティを表現するクラス"""

    def __init__(self, element: ET.Element, path: str, parent: Optional["Entity"] = None):
        """
        Args:
            element: XMLエレメント
            path: エンティティのパス
            parent: 親エンティティ
        """
        self.element = element
        self.path = path
        self.parent = parent
        self._columns: Set[str] = set()
        self._values: Dict[str, str] = {}
        self._inherited_values: Dict[str, str] = {}
        self._initialize()

    def _initialize(self) -> None:
        """初期化処理"""
        # 自身の値を初期化
        self._initialize_values()
        # 親からの継承値を初期化
        self._inherit_values()

    def _initialize_values(self) -> None:
        """自身の値を初期化"""
        # テキストコンテンツ
        if self.element.text and self.element.text.strip():
            self._values[self.element.tag] = self.element.text.strip()
            self._columns.add(self.element.tag)

        # 属性値
        for attr_name, attr_value in self.element.attrib.items():
            attr_key = f"@{attr_name}"
            self._values[attr_key] = attr_value
            self._columns.add(attr_key)

        # 子要素のテキストコンテンツと属性
        for child in self.element:
            if isinstance(child.tag, str):
                if child.text and child.text.strip():
                    self._values[child.tag] = child.text.strip()
                    self._columns.add(child.tag)
                for attr_name, attr_value in child.attrib.items():
                    key = f"{child.tag}.@{attr_name}"
                    self._values[key] = attr_value
                    self._columns.add(key)

    def _inherit_values(self) -> None:
        """親からの値を継承"""
        if not self.parent:
            return

        # 親の値を継承（属性とテキスト）
        parent_prefix = self.parent.element.tag
        # 親自身の属性を継承
        for attr_name, attr_value in self.parent.element.attrib.items():
            inherited_key = f"{parent_prefix}.@{attr_name}"
            self._inherited_values[inherited_key] = attr_value
            self._columns.add(inherited_key)

        # 親が持つ値も継承
        for key, value in self.parent._values.items():
            inherited_key = f"{parent_prefix}.{key}"
            self._inherited_values[inherited_key] = value
            self._columns.add(inherited_key)

        # 親の継承値も引き継ぐ
        if self.parent.parent:
            grandparent_prefix = self.parent.parent.element.tag
            for key, value in self.parent._inherited_values.items():
                if key.startswith(f"{grandparent_prefix}."):
                    inherited_key = f"{parent_prefix}.{key}"
                    self._inherited_values[inherited_key] = value
                    self._columns.add(inherited_key)

    def get_columns(self) -> List[str]:
        """利用可能なカラムのリストを取得"""
        return sorted(list(self._columns))

    def get_value(self, key: str) -> Optional[str]:
        """値を取得"""
        # 自身の値をチェック
        if key in self._values:
            return self._values[key]

        # 継承値をチェック
        if key in self._inherited_values:
            return self._inherited_values[key]

        # 親要素への参照をチェック
        if self.parent and "." in key:
            prefix, rest = key.split(".", 1)
            if prefix == self.parent.element.tag:
                return self.parent.get_value(rest)

        return None


class EntityContext:
    """エンティティのコンテキスト管理クラス"""

    def __init__(self) -> None:
        self._current_path: str = ""
        self._current_parent: Optional[Entity] = None

    def process_xml_element(
        self, element: ET.Element, parent_path: str = "", parent: Optional[Entity] = None
    ) -> Entity:
        """XMLエレメントを処理してエンティティを作成"""
        # 現在のコンテキストを保存
        prev_path = self._current_path
        prev_parent = self._current_parent

        try:
            # 現在のエンティティのコンテキストを設定
            current_path = f"{parent_path}.{element.tag}" if parent_path else element.tag
            self._current_path = current_path
            self._current_parent = parent

            # エンティティを作成
            current_entity = Entity(element, current_path, parent)

            # 子要素を処理
            for child in element:
                if isinstance(child.tag, str):
                    self.process_xml_element(child, current_path, current_entity)

            return current_entity
        finally:
            # コンテキストを復元
            self._current_path = prev_path
            self._current_parent = prev_parent

    def is_collection_element(self, element: ET.Element) -> Tuple[bool, Optional[str]]:
        """コレクション要素かどうかを判定"""
        child_tags = [child.tag for child in element if isinstance(child.tag, str)]
        if not child_tags:
            return False, None

        # タグの出現回数をカウント
        tag_counts: Dict[str, int] = {}
        content_children = 0
        for tag in child_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
            # テキストコンテンツを持つ子要素をカウント
            child = element.find(tag)
            if child is not None:
                # 子要素自身のテキストまたは孫要素のテキストをチェック
                has_content = bool(child.text and child.text.strip())
                if not has_content:
                    for grandchild in child:
                        if grandchild.text and grandchild.text.strip():
                            has_content = True
                            break
                if has_content:
                    content_children += 1

        # テキストコンテンツを持つ要素が一つもない場合も処理継続
        if content_children == 0:
            # コレクションではないが、処理は継続
            return False, None

        # 複数回出現するタグを探す
        for tag, count in tag_counts.items():
            if count > 1:
                # そのタグを持つ要素が有効なコンテンツを持っているか確認
                children = element.findall(tag)
                valid_children = 0
                for child in children:
                    if child.text and child.text.strip():
                        valid_children += 1
                        continue
                    for grandchild in child:
                        if grandchild.text and grandchild.text.strip():
                            valid_children += 1
                            break
                if valid_children > 1:
                    return True, tag

        return False, None
