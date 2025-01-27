# ADR 002: カラム名マッピングの設定場所変更

## ステータス
実装完了 2025-01-25
- XmlToExcelConverterクラスの_get_column_mappingメソッドで実装
- 新しい設定構造でのマッピング処理を実装
- テストケースで動作確認済み

## Context
カラム名の日本語マッピングについて、設定ファイルの構造をより論理的に整理する必要がありました。

## Decision
- カラム名マッピングをトップレベルの`column_names`からエンティティ定義内の`column_names`に移動
- 例：`[entities.order.column_names]`として各エンティティ内で定義

## Benefits
- エンティティに関連する設定を1箇所にまとめることで、設定ファイルの見通しが改善
- エンティティごとの独立性が向上し、メンテナンス性が向上
- エンティティ単位での設定の追加・変更・削除が容易に

## 実装例
```toml
[entities.order]
sheet_name = "注文"
primary_keys = "order_id"

[entities.order.column_names]
"order_id" = "注文番号"
"customer_name" = "顧客名"