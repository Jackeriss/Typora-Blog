"""全局静态变量"""
import os
from enum import IntEnum

from app.util.struct_util import StrEnum

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class HTTPCode(IntEnum):
    OK = 200
    BAD_REQUEST = 400 
    INTERNAL_SERVER_ERROR = 500


PAGE_LIMIT = 5
