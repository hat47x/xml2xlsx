アーキテクチャ決定記録（ADR）
=========================

このセクションでは、xml2xlsxの重要な設計決定とその背景を記録しています。

ADRとは
--------

ADR（Architecture Decision Record）は、プロジェクトにおける重要な設計上の決定を記録するためのドキュメントです。
各ADRには以下の情報が含まれます：

* ステータス（提案、承認、却下、廃止など）
* 決定が必要となった背景や文脈
* 検討された選択肢
* 決定内容とその理由
* 影響と結果

ADR一覧
--------

.. toctree::
   :maxdepth: 1
   :numbered:

   adr-001-xml-conversion-design-principles
   adr-002-column-name-mapping-location
   adr-003-configuration-structure-and-data-reference
   adr-004-library-selection-and-implementation
   adr-005-xml-path-and-sheet-name-handling
   adr-006-full-xml-path-and-warnings
   adr-007-sheet-integration-strategy
   adr-008-flexible-element-reference
   adr-009-test-data-cleanup
   adr-010-documentation-tool-selection
   adr-011-documentation-structure-and-format

主要な決定事項
------------

XML変換の基本方針
^^^^^^^^^^^^^^^^^^^

* XML→Excel変換の基本設計（ADR-001）
* 列名マッピングの実装方法（ADR-002）
* 設定構造の設計（ADR-003）

技術選択
^^^^^^^^

* 使用ライブラリの選定（ADR-004）
* XMLパス処理の実装（ADR-005）
* シート名処理の方針（ADR-005）

データ処理方針
^^^^^^^^^^^^

* 完全パスの実装（ADR-006）
* シート統合戦略（ADR-007）
* 要素参照の柔軟性（ADR-008）

ドキュメント管理
^^^^^^^^^^^^^

* ドキュメントツールの選定（ADR-010）
* ドキュメント構造と形式の標準化（ADR-011）

ADRの管理方針
------------

新規ADRの作成
^^^^^^^^^^^^

1. 次のADR番号を割り当て
2. テンプレートを基に作成
3. レビューと承認プロセス
4. マージと公開

ADRの更新
^^^^^^^^^

* 既存のADRは変更せず、新規ADRとして記録
* 古いADRは「置換（Superseded）」として記録

ステータスの種類
^^^^^^^^^^^^^

提案（Proposed）
    レビュー待ちの新規提案

承認（Accepted）
    レビュー完了し採用された決定

却下（Rejected）
    検討の結果、採用されなかった提案

廃止（Deprecated）
    以前の決定で現在は無効

置換（Superseded）
    新しい決定によって置き換えられた