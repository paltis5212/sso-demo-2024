from enum import Enum
import random
import string


def get_enum_value_list(enum_class: type[Enum]):
    """取得枚舉的 value 列表"""
    return [e.value for e in enum_class.__members__.values()]

def rand_str(length: int = 10):
    """生成隨機字串"""
    return "".join(
        random.choice(string.ascii_letters + string.digits) for x in range(length)
    )