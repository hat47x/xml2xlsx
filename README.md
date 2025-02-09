xml2xlsx

XMLファイルをXLSX形式に変換するPythonツールです。階層化されたXMLの要素からエンティティと項目を識別し、エンティティをExcelシート、項目を列にマッピングします。

## ドキュメント

- [基本設計書](docs/basic-design.md): システムの全体設計と要件定義
- [詳細設計書](docs/detailed-design.md): 実装仕様と技術的な詳細
- [開発スタイルガイド](docs/development-style.md): コーディング規約
- [テスト仕様書](docs/test-specification.md): テスト方針と手順

## 環境構築

### 前提条件
- Python 3.10以上

### インストール
```bash
# 開発版としてインストール
pip install -e .

# 開発用パッケージを含めてインストール
pip install -e ".[dev]"
```

### 依存パッケージ
主要なパッケージ：
- pandas: データフレーム操作とExcel出力
- toml: 設定ファイルの解析
- openpyxl: Excelファイル操作

開発用パッケージ：
- pytest: テストフレームワーク
- pyproject-flake8: コード品質チェック
- black: コードフォーマッター
- mypy: 型チェック
- tox: 複数バージョンでのテスト実行

## 使用方法

### コマンドライン

基本的な使用方法：
```bash
# 設定ファイルを使用する場合
xml2xlsx convert -i input.xml -c config.toml -o output.xlsx

# 設定ファイルの自動生成
xml2xlsx generate -i input.xml -o config.toml
```

オプション：
- `-i, --input`: 入力XMLファイルのパス（未指定時は標準入力から読み込み）
- `-c, --config`: TOML設定ファイルのパス（省略可）
- `-o, --output`: 出力ファイルのパス（未指定時は標準出力に出力）
- `-f, --force`: 既存の出力ファイルを上書き
- `-q, --quiet`: 進捗メッセージを表示しない
- `-v, --version`: バージョン情報を表示

標準入出力を使用した例：
```bash
# パイプラインでの使用
cat input.xml | xml2xlsx convert -c config.toml > output.xlsx

# 入力ファイル指定、標準出力
xml2xlsx convert -i input.xml -c config.toml > output.xlsx

# 標準入力、出力ファイル指定
cat input.xml | xml2xlsx convert -c config.toml -o output.xlsx
```

注意：
- 標準出力を使用する場合、進捗メッセージは標準エラー出力に出力されます
- 大きなファイルを処理する場合はファイル指定を推奨です
- シート名は31文字以内である必要があります（Excel仕様による制限）
- 同一要素の重複は自動的に排除されます
- エラーメッセージは日本語で出力されます

### 設定ファイル形式

設定ファイル（TOML）には以下の項目を指定します：

```toml
# 注文一覧のマッピング
[mapping."root.orders.order"]
sheet_name = "注文一覧"

[mapping."root.orders.order".columns]
"@id" = "注文ID"               # 属性の参照は@を付ける
"order_date" = "注文日"        # 要素の参照は直接指定
"customer.name" = "顧客名"     # 子要素は.で連結して参照

# 注文詳細のマッピング（親要素の参照あり）
[mapping."root.orders.order.items.item"]
sheet_name = "注文詳細"

[mapping."root.orders.order.items.item".columns]
"@id" = "明細ID"
"product_name" = "商品名"
"quantity" = "数量"
"order.@id" = "注文ID"         # 親要素の属性を参照
"order.order_date" = "注文日"  # 親要素の要素を参照
```

親要素の情報参照：
- `order.@id`: 親要素の属性を参照
- `order.order_date`: 親要素の要素を参照
- `order.customer.name`: 親要素の子要素を参照

重要な制約事項：
1. シート名の制限
   - 最大31文字（Excel仕様）
   - シート名の重複は不可

2. データの重複
   - 同一要素の重複は自動的に排除
   - 親子関係は維持

3. メモリ使用
   - 大規模ファイル処理時はメモリ使用量に注意
   - 必要に応じて分割処理を推奨

詳細な設定例や XMLファイル例については、[基本設計書](docs/basic-design.md)を参照してください。

## 開発

### テストの実行

単一バージョンでのテスト：
```bash
# 全テストを実行
pytest

# カバレッジレポートの生成
pytest --cov=xml2excel tests/

# 特定のテストファイルの実行
pytest tests/test_converter.py
```

複数バージョンでのテスト（tox使用）：
```bash
# すべてのPythonバージョンでテスト
tox

# 特定のバージョンでテスト
tox -e py39

# 並列実行
tox -p auto

# テスト環境の再作成
tox --recreate
```

toxによるテスト実行では以下のチェックが行われます：

1. コードフォーマット（black）
2. コード品質チェック（pflake8）
3. 型チェック（mypy）
4. ユニットテスト（pytest）

対応Pythonバージョン：
- Python 3.10
- Python 3.11
- Python 3.12
- Python 3.13

テストの詳細な仕様については、[テスト仕様書](docs/test-specification.md)を参照してください。

## トラブルシューティング

### よくある問題

1. シート名に関するエラー：
```
エラー: シート名 'very_long_sheet_name_exceeding_limit' が31文字を超えています
→ 設定ファイルで31文字以内のシート名を指定してください
```

2. メモリ使用量の問題：
```
エラー: メモリ不足が発生しました
→ 入力ファイルを分割するか、より大きなメモリを確保してください
```

3. XMLファイルのエラー：
```
エラー: XMLファイルの解析に失敗しました
→ XMLファイルの形式を確認してください
```

その他の一般的な問題：
```bash
# インストールに失敗する場合
pip install --no-cache-dir -e .

# 依存関係の問題
pip uninstall xml2xlsx
pip install -e .

# toxでのテストに失敗する場合
tox --recreate
```

## ライセンス

MIT License