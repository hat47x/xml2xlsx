"""CLIインターフェースのテスト。"""

import pytest
from pathlib import Path

from xml2xlsx import __version__
from xml2xlsx.cli import main, create_parser, validate_args


@pytest.fixture
def test_data_dir() -> Path:
    """テストデータディレクトリのパスを返す。"""
    return Path(__file__).parent / "test_data"


def test_parser_required_args():
    """必須引数のパース処理をテスト。"""
    parser = create_parser()
    # ショートオプション
    args = parser.parse_args(
        ["-i", "input.xml", "-c", "config.toml", "-o", "output.xlsx"]
    )
    assert args.input == "input.xml"
    assert args.config == "config.toml"
    assert args.output == "output.xlsx"
    assert not args.force
    assert not args.quiet

    # ロングオプション
    args = parser.parse_args(
        ["--input", "input.xml", "--config", "config.toml", "--output", "output.xlsx"]
    )
    assert args.input == "input.xml"
    assert args.config == "config.toml"
    assert args.output == "output.xlsx"


def test_parser_missing_required_args():
    """必須引数が不足している場合のテスト。"""
    parser = create_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["-i", "input.xml"])  # configとoutputが不足
    with pytest.raises(SystemExit):
        parser.parse_args(
            ["--input", "input.xml", "--output", "output.xlsx"]
        )  # configが不足


def test_parser_optional_args():
    """オプション引数の組み合わせをテスト。"""
    parser = create_parser()
    # forceオプション（ショート）
    args = parser.parse_args(
        ["-i", "input.xml", "-c", "config.toml", "-o", "output.xlsx", "-f"]
    )
    assert args.force

    # forceオプション（ロング）
    args = parser.parse_args(
        [
            "--input",
            "input.xml",
            "--config",
            "config.toml",
            "--output",
            "output.xlsx",
            "--force",
        ]
    )
    assert args.force

    # quietオプション
    args = parser.parse_args(
        [
            "--input",
            "input.xml",
            "--config",
            "config.toml",
            "--output",
            "output.xlsx",
            "--quiet",
        ]
    )
    assert args.quiet

    # 全オプション
    args = parser.parse_args(
        [
            "--input",
            "input.xml",
            "--config",
            "config.toml",
            "--output",
            "output.xlsx",
            "--force",
            "--quiet",
        ]
    )
    assert args.force
    assert args.quiet


def test_parser_version(capsys):
    """バージョン情報の出力をテスト。"""
    parser = create_parser()
    # ショートオプション
    with pytest.raises(SystemExit) as excinfo:
        parser.parse_args(["-v"])
    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    assert __version__ in captured.out

    # ロングオプション
    with pytest.raises(SystemExit) as excinfo:
        parser.parse_args(["--version"])
    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    assert __version__ in captured.out


def test_parser_help(capsys):
    """ヘルプメッセージの出力をテスト。"""
    parser = create_parser()
    # ショートオプション
    with pytest.raises(SystemExit) as excinfo:
        parser.parse_args(["-h"])
    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    help_out = captured.out
    assert "usage:" in help_out
    assert "--input" in help_out
    assert "--config" in help_out
    assert "--output" in help_out
    assert "--force" in help_out
    assert "--quiet" in help_out

    # ロングオプション
    with pytest.raises(SystemExit) as excinfo:
        parser.parse_args(["--help"])
    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    assert captured.out == help_out  # 同じヘルプメッセージ


def test_validate_args_missing_input(tmp_path):
    """存在しない入力ファイルの検証をテスト。"""
    args = create_parser().parse_args(
        [
            "--input",
            "nonexistent.xml",
            "--config",
            "config.toml",
            "--output",
            "output.xlsx",
        ]
    )
    error = validate_args(args)
    assert error is not None
    assert "入力XMLファイル" in error
    assert "見つかりません" in error


def test_validate_args_missing_config(test_data_dir, tmp_path):
    """存在しない設定ファイルの検証をテスト。"""
    args = create_parser().parse_args(
        [
            "--input",
            str(test_data_dir / "basic_sample.xml"),
            "--config",
            "nonexistent.toml",
            "--output",
            "output.xlsx",
        ]
    )
    error = validate_args(args)
    assert error is not None
    assert "設定ファイル" in error
    assert "見つかりません" in error


def test_validate_args_existing_output(test_data_dir, tmp_path):
    """既存の出力ファイルの検証をテスト。"""
    # 出力ファイルを作成
    output_path = tmp_path / "existing.xlsx"
    output_path.touch()

    args = create_parser().parse_args(
        [
            "--input",
            str(test_data_dir / "basic_sample.xml"),
            "--config",
            str(test_data_dir / "basic_config.toml"),
            "--output",
            str(output_path),
        ]
    )
    error = validate_args(args)
    assert error is not None
    assert "既に存在します" in error
    assert "--force" in error


def test_validate_args_force_overwrite(test_data_dir, tmp_path):
    """--forceオプションでの上書き検証をテスト。"""
    # 出力ファイルを作成
    output_path = tmp_path / "existing.xlsx"
    output_path.touch()

    args = create_parser().parse_args(
        [
            "--input",
            str(test_data_dir / "basic_sample.xml"),
            "--config",
            str(test_data_dir / "basic_config.toml"),
            "--output",
            str(output_path),
            "--force",
        ]
    )
    error = validate_args(args)
    assert error is None


def test_main_successful_execution(test_data_dir: Path, tmp_path: Path, capsys):
    """正常系の実行をテスト。"""
    xml_path = test_data_dir / "basic_sample.xml"
    config_path = test_data_dir / "basic_config.toml"
    output_path = tmp_path / "output.xlsx"

    # 通常実行
    result = main(
        [
            "--input",
            str(xml_path),
            "--config",
            str(config_path),
            "--output",
            str(output_path),
        ]
    )
    assert result == 0
    assert output_path.exists()
    captured = capsys.readouterr()
    assert str(xml_path) in (captured.out + captured.err)
    assert str(output_path) in (captured.out + captured.err)

    # quietオプション付きの実行
    output_path.unlink()  # 前の出力を削除
    result = main(
        [
            "--input",
            str(xml_path),
            "--config",
            str(config_path),
            "--output",
            str(output_path),
            "--quiet",
        ]
    )
    assert result == 0
    assert output_path.exists()
    captured = capsys.readouterr()
    assert not captured.out  # 出力メッセージなし


def test_main_error_handling(capsys, tmp_path):
    """エラー処理のテスト。"""
    # 不正なXMLファイル
    invalid_xml = tmp_path / "invalid.xml"
    invalid_xml.write_text("This is not XML")

    result = main(
        [
            "--input",
            str(invalid_xml),
            "--config",
            "config.toml",
            "--output",
            "output.xlsx",
        ]
    )
    assert result == 1
    captured = capsys.readouterr()
    assert "エラー" in captured.err


if __name__ == "__main__":
    pytest.main([__file__])
