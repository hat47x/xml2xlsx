開発スタイルガイド
==================

プロジェクト構成
----------------

::

   xml2xlsx/                   # プロジェクトルート
   ├── src/                    # ソースコード
   │   └── xml2xlsx/          # メインパッケージ
   │       ├── __init__.py    # パッケージ初期化
   │       ├── cli.py         # コマンドライン処理
   │       ├── converter.py   # 変換ロジック
   │       └── entity.py      # データモデル
   ├── tests/                  # テストコード
   │   ├── test_data/         # テストデータ
   │   │   ├── basic_*.{xml,toml}     # 基本機能テスト
   │   │   ├── cdata_*.{xml,toml}     # CDATA処理テスト
   │   │   └── large_*.{xml,toml}     # 大規模データテスト
   │   ├── test_converter.py  # 変換機能テスト
   │   └── test_performance.py # パフォーマンステスト
   ├── docs/                   # ドキュメント
   │   ├── adr/               # アーキテクチャ決定記録
   │   ├── design.md          # 設計ドキュメント
   │   └── development-style.md # 開発スタイルガイド
   └── pyproject.toml         # プロジェクト設定

コーディング規約
----------------

Pythonコードスタイル
~~~~~~~~~~~~~~~~~~~~

-  PEP 8に準拠
-  型ヒントを積極的に使用（PEP 484）

   -  Union型の代わりにパイプ演算子を使用（Python 3.10+）
   -  match文の活用（Python 3.10+）

-  docstringは必須（Google形式）
-  1行の長さは88文字以内（black準拠）
-  dataclassの活用（データモデル定義）
-  asyncio/awaitの適切な使用

コード品質管理
~~~~~~~~~~~~~~

-  black: コードフォーマット

   .. code:: bash

      # フォーマットの確認
      black --check src/
      # フォーマットの適用
      black src/

-  pflake8: コードスタイルチェック（pyproject.tomlで設定）

   .. code:: bash

      # スタイルチェックの実行
      pflake8 src/

-  型ヒント: 可読性向上のため推奨

命名規則
~~~~~~~~

-  クラス名：UpperCamelCase
-  メソッド名：lowercase_with_underscores
-  定数：UPPERCASE_WITH_UNDERSCORES
-  プライベートメンバー：_prefix
-  型変数：UpperCamelCase_t
-  ジェネリック型：T, U, V

インポート順序
~~~~~~~~~~~~~~

1. 標準ライブラリ
2. サードパーティライブラリ
3. ローカルインポート （各グループ内はアルファベット順）

テスト戦略
----------

テスト手法
~~~~~~~~~~

-  単体テスト

   -  基本変換機能の検証
   -  エッジケースの確認
   -  設定ファイルの解析検証

-  統合テスト

   -  XML→Excel変換の一連の流れ
   -  大規模データ処理

   .. code:: bash

      # パフォーマンステストの実行
      pytest tests/test_performance.py -v

-  テストデータ管理

   -  tests/test_dataディレクトリ配下に配置
   -  実際のユースケースを反映
   -  さまざまなXML構造のカバー

テストカバレッジ
~~~~~~~~~~~~~~~~

-  行カバレッジ90%以上を目標
-  分岐カバレッジ80%以上を目標
-  重要なビジネスロジックは100%を目指す
-  pytest-covでレポート生成

テストデータ
~~~~~~~~~~~~

-  テストデータは\ ``tests/test_data``\ に配置
-  サンプルデータは現実的なケースを想定
-  エッジケースを積極的にテスト
-  データ生成にfactoryパターンを活用

継続的インテグレーション
------------------------

CI/CDパイプライン
~~~~~~~~~~~~~~~~~

-  GitHub Actionsでの自動化

   -  コード品質チェック
   -  テスト実行
   -  ドキュメント生成
   -  パッケージビルド

-  バージョン管理（semantic versioning）
-  自動デプロイ設定

コード品質メトリクス
~~~~~~~~~~~~~~~~~~~~

-  循環的複雑度（10以下）
-  メソッド行数（50行以下）
-  クラス行数（300行以下）
-  依存関係の深さ（3層以下）

品質管理プロセス
----------------

コミット前の確認事項
~~~~~~~~~~~~~~~~~~~~

-  ユニットテストの実行

   .. code:: bash

      pytest tests/

-  コードフォーマットの確認

   .. code:: bash

      black --check src/
      pflake8 src/

-  大規模データでの動作確認

   .. code:: bash

      pytest tests/test_performance.py

.. _継続的インテグレーション-1:

継続的インテグレーション
~~~~~~~~~~~~~~~~~~~~~~~~

-  GitHub Actionsによる自動検証

   -  Python 3.7以上での動作確認
   -  全テストスイートの実行
   -  フォーマットチェック

設定ファイル管理
----------------

TOML設定ファイル
~~~~~~~~~~~~~~~~

-  インデントは2スペース
-  セクション間は1行空ける
-  コメントは日本語で記述
-  環境変数による上書き対応

更新手順
~~~~~~~~

1. テストケースの作成/更新
2. 設定ファイルの修正
3. コンバーターの修正（必要な場合）
4. テストの実行
5. ドキュメントの更新

ドキュメント規約
----------------

アーキテクチャ決定記録（ADR）
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  配置場所：\ ``docs/adr/``\ ディレクトリ

-  ファイル命名規則：\ ``adr-NNN-概要.md``

   ::

      例：
      adr-001-xml-conversion-design-principles.md
      adr-002-column-name-mapping-location.md
      adr-003-configuration-structure-and-data-reference.md

-  必須セクション：

   -  ステータス：以下のいずれかを明記

      -  提案（Proposed）: レビュー待ちの新規提案
      -  承認（Accepted）: レビュー完了し採用された決定
      -  却下（Rejected）: 検討の結果、採用されなかった提案
      -  廃止（Deprecated）: 以前の決定で現在は無効
      -  置換（Superseded）: 新しい決定によって置き換えられた

   -  文脈：決定が必要となった背景
   -  決定：採用する解決策の詳細
   -  代替案：検討した他の選択肢
   -  影響：この決定による影響範囲
   -  備考：補足情報や参考資料

-  更新ルール：

   -  既存のADRは変更不可
   -  決定の変更は新規ADRとして記録
   -  ステータスの変更のみ既存ADRに追記可

エラー処理とロギング
--------------------

エラー設計
~~~~~~~~~~

-  XML解析エラーの詳細な報告
-  設定ファイル検証エラーの明確な説明
-  メモリ不足時の適切なエラーハンドリング

ロギング戦略
~~~~~~~~~~~~

-  ログレベルに応じた出力制御
-  エラー発生時の詳細なコンテキスト記録
-  大規模ファイル処理時の進捗表示

セキュリティ対策
----------------

入力検証
~~~~~~~~

-  XMLファイルの整形式チェック
-  DTD外部実体参照の制限
-  メモリ消費量の監視と制限

依存関係管理
~~~~~~~~~~~~

-  依存パッケージの定期更新
-  既知の脆弱性チェック

パフォーマンス最適化
--------------------

最適化戦略
~~~~~~~~~~

-  プロファイリングの定期実施
-  メモリ使用量の監視
-  CPU使用率の最適化
-  I/O操作の効率化

ベンチマーク
~~~~~~~~~~~~

-  処理速度の定期測定
-  メモリ使用量の推移確認
-  大規模データでのテスト
-  ボトルネックの特定と改善
