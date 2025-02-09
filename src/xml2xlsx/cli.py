"""コマンドラインインターフェース"""

import sys
import argparse
import logging
from pathlib import Path
from . import __version__
from .converter import XmlToExcelConverter
from .config_generator import generate_config
from .exceptions import ConfigurationError

logger = logging.getLogger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """コマンドラインパーサーを作成"""
    parser = argparse.ArgumentParser(
        description="XMLファイルをExcelファイルに変換します。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="利用可能なコマンド")

    # convertコマンド
    convert_parser = subparsers.add_parser("convert", help="XMLをExcelに変換")
    convert_parser.add_argument("-i", "--input", help="入力XMLファイル")
    convert_parser.add_argument("-c", "--config", help="設定ファイル")
    convert_parser.add_argument("-o", "--output", help="出力Excelファイル")

    # generateコマンド
    generate_parser = subparsers.add_parser("generate", help="設定ファイルを生成")
    generate_parser.add_argument("-i", "--input", help="入力XMLファイル")
    generate_parser.add_argument("-o", "--output", help="出力設定ファイル")

    return parser


def convert_command(args: argparse.Namespace) -> int:
    """変換コマンドの実行"""
    try:
        # 入力ファイルの存在確認
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"入力ファイルが見つかりません: {args.input}", file=sys.stderr)
            return 1

        # 設定ファイルの存在確認
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"設定ファイルが見つかりません: {args.config}", file=sys.stderr)
            return 1

        # 変換の実行
        converter = XmlToExcelConverter()
        converter.load_config(str(config_path))
        converter.convert(str(input_path), args.output)
        print("変換が完了しました", file=sys.stderr)
        return 0

    except ConfigurationError as e:
        print(f"エラー: {str(e)}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {str(e)}", file=sys.stderr)
        return 1


def generate_command(args: argparse.Namespace) -> int:
    """設定ファイル生成コマンドの実行"""
    try:
        # 入力ファイルの存在確認
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"入力ファイルが見つかりません: {args.input}", file=sys.stderr)
            return 1

        # 設定ファイルの生成
        generate_config([str(input_path)], args.output)
        print("設定ファイルを生成しました", file=sys.stderr)
        return 0

    except Exception as e:
        print(f"予期せぬエラーが発生しました: {str(e)}", file=sys.stderr)
        return 1


def main(args: list[str] | None = None) -> int:
    """メインエントリーポイント"""
    if args is None:
        args = sys.argv[1:]

    parser = create_parser()
    parsed_args = parser.parse_args(args)

    if not parsed_args.command:
        print(parser.format_usage(), file=sys.stderr)
        print("エラー: コマンドが指定されていません", file=sys.stderr)
        sys.exit(2)

    if parsed_args.command == "convert":
        if not all([parsed_args.input, parsed_args.config, parsed_args.output]):
            parser.error("convert コマンドには --input, --config, --output が必要です")
        return convert_command(parsed_args)

    if parsed_args.command == "generate":
        if not all([parsed_args.input, parsed_args.output]):
            parser.error("generate コマンドには --input, --output が必要です")
        return generate_command(parsed_args)

    return 0
