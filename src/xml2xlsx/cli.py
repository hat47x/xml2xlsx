"""Command-line interface for xml2xlsx"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional
from xml2xlsx.converter import XmlToExcelConverter
from xml2xlsx import __version__


def create_parser() -> argparse.ArgumentParser:
    """
    コマンドライン引数のパーサーを作成

    Returns:
        ArgumentParser: 設定済みの引数パーサー
    """
    parser = argparse.ArgumentParser(
        description="XMLファイルをExcelに変換します。エンティティと項目の関係はTOML設定ファイルで定義します。"
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        help="入力XMLファイルのパス（未指定時は標準入力から読み込み）",
    )
    parser.add_argument(
        "-c", "--config", type=str, required=True, help="TOML設定ファイルのパス"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="出力Excelファイルのパス（未指定時は標準出力に出力）",
    )
    parser.add_argument(
        "-f", "--force", action="store_true", help="既存の出力ファイルを上書き"
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="進捗メッセージを表示しない"
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"xml2xlsx {__version__}"
    )
    return parser


def validate_args(args: argparse.Namespace) -> Optional[str]:
    """
    コマンドライン引数を検証

    Args:
        args: パース済みの引数

    Returns:
        エラーメッセージ（問題がない場合はNone）
    """
    # 入力XMLファイルの存在確認（ファイル指定時のみ）
    if args.input and not Path(args.input).exists():
        return f"入力XMLファイル '{args.input}' が見つかりません"

    # 設定ファイルの存在確認
    if not Path(args.config).exists():
        return f"設定ファイル '{args.config}' が見つかりません"

    # 出力ファイルの存在確認（ファイル指定時かつ--forceが指定されていない場合）
    if args.output and Path(args.output).exists() and not args.force:
        return f"出力ファイル '{args.output}' は既に存在します。上書きする場合は --force オプションを指定してください"

    return None


def main(argv: Optional[List[str]] = None) -> int:
    """
    メインの実行関数

    Args:
        argv: コマンドライン引数のリスト（Noneの場合はsys.argvを使用）

    Returns:
        終了コード（0:成功、1:エラー）
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    # 引数の検証
    error = validate_args(args)
    if error:
        print(f"エラー: {error}", file=sys.stderr)
        return 1

    try:
        # 入力の準備
        xml_input: str | bytes
        input_desc = "標準入力"
        if args.input:
            with open(args.input, "rb") as f:
                xml_input = f.read()
            input_desc = f"'{args.input}'"
        else:
            xml_input = sys.stdin.buffer.read()

        # 変換の実行
        converter = XmlToExcelConverter(args.config)

        if args.output:
            # ファイル出力の場合
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            converter.convert(xml_input, args.output)
            if not args.quiet:
                print(
                    f"{input_desc} を '{args.output}' に変換しました", file=sys.stderr
                )
        else:
            # 標準出力の場合
            excel_data = converter.convert(xml_input)
            if excel_data:
                sys.stdout.buffer.write(excel_data)
                if not args.quiet:
                    print(f"{input_desc} をExcelに変換しました", file=sys.stderr)

        return 0

    except Exception as e:
        print(f"エラー: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    main()
