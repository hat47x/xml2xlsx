テストガイド
==========

このガイドでは、xml2xlsxのテスト手法とベストプラクティスを説明します。

テスト構成
--------

プロジェクトのテストは以下のカテゴリで構成されています：

1. 単体テスト
^^^^^^^^^

個々のコンポーネントの機能テスト：

* コンバーター機能
* 設定生成機能
* エンティティ処理

2. 結合テスト
^^^^^^^^^

複数のコンポーネントを組み合わせたテスト：

* XML→Excel変換の一連の流れ
* 設定ファイルの生成と使用
* エラー処理の連携

3. パフォーマンステスト
^^^^^^^^^^^^^^^

大規模データでの動作確認：

* メモリ使用量
* 処理速度
* リソース効率

テストの実行方法
-----------

基本的なテスト実行::

    pytest

カバレッジレポート付きで実行::

    pytest --cov=xml2xlsx tests/

特定のテストのみ実行::

    pytest tests/test_converter.py

テストの作成ガイドライン
----------------

1. テストケースの命名
^^^^^^^^^^^^^^^

* テストファイル: ``test_機能名.py``
* テスト関数: ``test_テスト内容()``

例::

    # test_converter.py
    def test_basic_conversion():
        ...

    def test_cdata_handling():
        ...

2. テストデータの配置
^^^^^^^^^^^^^

* ``tests/test_data/`` ディレクトリを使用
* 意図が分かる名前を付ける
* ファイルサイズはできるだけ小さく

例::

    tests/test_data/
    ├── basic_input.xml
    ├── cdata_sample.xml
    └── large_dataset.xml

3. フィクスチャの活用
^^^^^^^^^^^^^

共通のセットアップコードはフィクスチャとして定義::

    @pytest.fixture
    def sample_xml():
        return """
        <root>
            <item id="1">
                <name>テスト商品</name>
            </item>
        </root>
        """

4. アサーションの書き方
^^^^^^^^^^^^^

明確で具体的なアサーション::

    def test_conversion_result(sample_xml):
        converter = XmlToExcelConverter()
        result = converter.convert(sample_xml)
        
        assert "商品" in result.sheet_names
        assert result.get_sheet("商品").shape[0] > 0

テストデータの作成
------------

1. 基本テストデータ
^^^^^^^^^^^^^

* シンプルなXML構造
* 最小限の要素と属性
* 典型的なユースケース

2. エッジケース
^^^^^^^^^^^

* 空の要素
* 特殊文字
* 長いテキスト
* 非ASCII文字

3. エラーケース
^^^^^^^^^^^

* 不正なXML
* 不正な設定
* リソース制限

CI/CDでのテスト
-----------

GitHub Actionsでの自動テスト::

    name: Tests
    on: [push, pull_request]
    
    jobs:
      test:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v3
          - name: Set up Python
            uses: actions/setup-python@v4
            with:
              python-version: '3.10'
          - name: Install dependencies
            run: pip install -e .[dev]
          - name: Run tests
            run: pytest --cov=xml2xlsx tests/

テストカバレッジの目標
--------------

* コードカバレッジ: 90%以上
* 分岐カバレッジ: 80%以上
* 重要なビジネスロジック: 100%

カバレッジレポートの生成::

    pytest --cov=xml2xlsx --cov-report=html tests/

トラブルシューティング
---------------

1. テストが失敗する場合
   * テストデータの確認
   * 環境変数の確認
   * 依存関係の確認

2. カバレッジが低い場合
   * 未テストのコードパスの特定
   * テストケースの追加
   * エッジケースの考慮