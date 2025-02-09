"""カスタム例外クラスの定義"""


class XML2XLSXError(Exception):
    """xml2xlsxの基本例外クラス"""

    pass


class ConfigGenerationError(XML2XLSXError):
    """設定ファイル生成時のエラー"""

    pass


class XMLParseError(XML2XLSXError):
    """XMLの解析に失敗した場合のエラー"""

    pass


class ConfigurationError(XML2XLSXError):
    """設定ファイルの読み込みや処理に関するエラー"""

    pass


class InvalidPathError(XML2XLSXError):
    """XMLパスが不正な場合のエラー"""

    pass


class DataTypeError(XML2XLSXError):
    """データ型の不一致や変換エラー"""

    pass


class SheetNameError(XML2XLSXError):
    """シート名に関するエラー（長さ超過など）"""

    pass


class DataIntegrityError(XML2XLSXError):
    """データの整合性に関するエラー"""

    pass
