"""xml2xlsx converter package"""

__version__ = "0.1.0"

from .converter import XmlToExcelConverter
from .cli import main

__all__ = ["XmlToExcelConverter", "main"]
