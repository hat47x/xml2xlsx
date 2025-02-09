"""設定ファイル操作モジュール"""

from typing import Any, Dict
import toml


def load_config(file_path: str) -> Dict[str, Any]:
    """
    TOMLファイルから設定を読み込む

    Args:
        file_path: 設定ファイルのパス

    Returns:
        設定データを含む辞書

    Raises:
        FileNotFoundError: 設定ファイルが存在しない場合
        TomlDecodeError: TOMLファイルの解析に失敗した場合
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return toml.load(f)
