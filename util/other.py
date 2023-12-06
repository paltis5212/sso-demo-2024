from enum import Enum


def get_enum_value_list(enum_class: type[Enum]):
    """取得枚舉的 value 列表"""
    return [e.value for e in enum_class.__members__.values()]