# ADR 004: ライブラリ選択と実装知見

## ステータス
実装完了 2025-01-25
- すべてのライブラリ機能が実装済み
- パフォーマンス最適化を完了
- エラー処理の改善も実施済み

## Context
XMLからExcelへの変換において、以下のライブラリを使用：
- xml.etree.ElementTree：XML解析
- pandas：データフレーム処理
- toml：設定ファイル読み込み

これらのライブラリ使用時に様々な制約と課題に直面し、それぞれに対する解決策を見出しました。

## Decision

### ElementTree
1. 親要素参照の制限への対応
```python
def _build_parent_map(self, root: ET.Element) -> Dict[ET.Element, ET.Element]:
    return {child: parent for parent in root.iter() for child in parent}
```

2. XPath機能の制限への対応
```python
def _find_parent_element(self, element: ET.Element, parent_name: str) -> Optional[ET.Element]:
    current = element
    parent_map = self._build_parent_map(element.getroottree().getroot())
    while current in parent_map:
        current = parent_map[current]
        if current.tag == parent_name:
            return current
    return None
```

### pandas
1. データフレーム最適化
```python
columns = []
key_fields = entity_config.get('key_field', [])
for key_field in key_fields:
    if key_field in df.columns:
        columns.append(key_field)
```

2. カラム名日本語化の最適化
```python
if 'columns' in entity_config:
    column_mapping = entity_config['columns']
    renamed_columns = [column_mapping.get(col, col) for col in df.columns]
    df.columns = renamed_columns
```

### TOML
1. 設定ファイル形式として選択した理由：
- 人間が読み書きしやすい
- コメントが書ける
- 階層構造が表現しやすい
- データ型が明確

2. 辞書の順序保持の活用
```toml
[mapping.department.columns]
id = "部門ID"          # 1番目
name = "部門名"        # 2番目
company.id = "所属会社ID" # 3番目
```

## Lessons Learned
1. 親子関係の表現
- 失敗：特殊記法（$parent）の導入検討
- 教訓：既存概念（エンティティ名.フィールド名）の活用

2. 設定ファイル構造
- 失敗：設定の分散化
- 教訓：関連設定の一箇所への集約

3. データ変換パイプライン
- 失敗：一括変換アプローチ
- 教訓：抽出→変換→出力の段階的処理

## Consequences
- コードの保守性向上
- エラー処理の改善
- パフォーマンスの最適化

## Notes
- ElementTreeの代替としてlxmlの検討を完了（現時点では不要と判断）
- 大規模データセット用の最適化を実装済み
- 設定ファイルのバリデーション強化を完了