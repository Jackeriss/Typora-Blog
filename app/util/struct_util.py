from enum import Enum


class StrEnum(str, Enum):
    """ 字符串类型的枚举 """

    def __new__(cls, *args):
        for arg in args:
            if not isinstance(arg, str):
                raise TypeError("Not str: {}".format(arg))
        return super(StrEnum, cls).__new__(cls, *args)
