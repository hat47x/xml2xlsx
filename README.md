# xml2xlsx

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
xml2xlsx -i input.xml -c config.toml -o output.xlsx

# 設定ファイルなしで自動変換（シンプルなXMLの場合）
xml2xlsx -i input.xml -o output.xlsx
```

オプション：
- `-i, --input`: 入力XMLファイルのパス（未指定時は標準入力から読み込み）
- `-c, --config`: TOML設定ファイルのパス（省略可）
- `-o, --output`: 出力XLSXファイルのパス（未指定時は標準出力に出力）
- `-f, --force`: 既存の出力ファイルを上書き
- `-q, --quiet`: 進捗メッセージを表示しない
- `-v, --version`: バージョン情報を表示

標準入出力を使用した例：
```bash
# パイプラインでの使用
cat input.xml | xml2xlsx -c config.toml > output.xlsx

# 入力ファイル指定、標準出力
xml2xlsx -i input.xml -c config.toml > output.xlsx

# 標準入力、出力ファイル指定
cat input.xml | xml2xlsx -c config.toml -o output.xlsx
```

注意：
- 標準出力を使用する場合、進捗メッセージは標準エラー出力に出力されます
- 大きなファイルを処理する場合はファイル指定を推奨です

### 設定ファイル形式

設定ファイル（TOML）には以下の項目を指定します：

- `sheet_name`: Excelシート名（必須）
- `primary_keys`: エンティティの一意キー（必須）
- `parent_key`: 親エンティティとの関連キー（ルートエンティティの場合は省略可）
- `column_order`: 取得する項目とその出力順序（省略可）

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
   - srcとtestsディレクトリの全Pythonファイルをチェック
   - フォーマットの不一致があればエラー

2. コード品質チェック（pflake8）
   - PEP 8スタイルガイドへの準拠
   - 複雑度やコード行数の制限チェック

3. 型チェック（mypy）
   - 静的型チェックによるエラー検出
   - 未定義の型や型の不一致を報告

4. ユニットテスト（pytest）
   - すべてのテストケースを実行
   - カバレッジレポートを生成（xml2xlsxパッケージ）

対応Pythonバージョン：
- Python 3.10
- Python 3.11
- Python 3.12
- Python 3.13

各バージョンで個別の仮想環境が作成され、依存パッケージのインストールからテストまでが独立して実行されます。

テストの詳細な仕様については、[テスト仕様書](docs/test-specification.md)を参照してください。

### Visual Studio Codeでの開発

プロジェクトにはVSCode用の設定が含まれています：

1. F5キーで直接デバッグ実行が可能
2. テストの実行と結果の確認が容易
3. 設定済みのデバッグ構成
4. Mermaid図の表示機能

#### 必須拡張機能

設計書に含まれるMermaid図を表示するには、以下の拡張機能をインストールしてください：

```bash
code --install-extension bierner.markdown-mermaid
```

または、VS Code内で以下の手順で拡張機能をインストール：
1. 拡張機能パネルを開く（Ctrl+Shift+X）
2. 検索欄に「Markdown Preview Mermaid Support」と入力
3. 「インストール」をクリック

## トラブルシューティング

### よくある問題

1. インストールに失敗する場合：
```bash
# キャッシュを使わずに再インストール
pip install --no-cache-dir -e .
```

2. 依存関係の問題：
```bash
# 依存関係をクリーンアップして再インストール
pip uninstall xml2xlsx
pip install -e .
```

3. toxでのテストに失敗する場合：
```bash
# toxの環境をクリーンアップして再実行
tox --recreate

# 特定のPythonバージョンで失敗する場合
# そのバージョンのみを対象に再実行
tox -e py310 --recreate

# テスト中にメモリエラーが発生する場合
# 並列実行を無効化して再実行
tox --recreate -p 0
```

## ライセンス

MIT License