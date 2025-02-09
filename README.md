xml2xlsx
====

XMLファイルをXLSX形式に変換するPythonツールです。階層化されたXMLの要素からエンティティと項目を識別し、エンティティをExcelシート、項目を列にマッピングします。

## ドキュメント

詳細なドキュメントは以下で公開しています：

- [ユーザーガイド](https://hat47x.github.io/xml2xlsx/docs/): インストール方法、基本的な使い方、設定ファイルの作成方法などを説明しています
- [開発者ガイド](https://hat47x.github.io/xml2xlsx/dev-docs/): アーキテクチャ設計、開発プロセス、テスト仕様などの技術文書を提供しています

※ドキュメントはGitHub Pagesでホストされています。上記リンクで閲覧できない場合は、GitHubリポジトリの「gh-pages」ブランチの`docs`および`dev-docs`ディレクトリをご確認ください。

## クイックスタート

### 前提条件
- Python 3.10以上

### インストール
```bash
pip install xml2xlsx
```

### 基本的な使用方法
```bash
# 設定ファイルを使用してXMLをExcelに変換
xml2xlsx convert -i input.xml -c config.toml -o output.xlsx

# 設定ファイルの自動生成
xml2xlsx generate -i input.xml -o config.toml
```

より詳細な使用方法や設定例については、[ユーザーガイド](https://hat47x.github.io/xml2xlsx/docs/)を参照してください。

## 開発用インストール

```bash
# 開発版としてインストール
pip install -e .

# 開発用パッケージを含めてインストール
pip install -e ".[dev]"
```

開発プロセス、アーキテクチャ、テスト仕様などの詳細は[開発者ガイド](https://hat47x.github.io/xml2xlsx/dev-docs/)を参照してください。

## ライセンス

MIT License