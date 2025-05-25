import re
from typing import Any, Optional, Type


def extract_class_from_type_string(type_str: str, index: int = 0) -> list[str]:
    # 提取方括号中的内容
    match = re.search(r'\[(.*)\]', type_str)
    if not match:
        return []

    # 分割泛型参数
    generic_args = [str(arg.strip()) for arg in match.group(1).split(',')]

    if index >= len(generic_args):
        return []

    # 获取指定索引的参数
    class_path = generic_args[index]

    try:
        return class_path.rsplit('.', 1)
    except (ValueError, ImportError, AttributeError) as e:
        return []


def get_val_from_pb(pb: Any):
    return [tuple(i) for i in pb.__dict__["__init__"].__annotations__.items() if not i[0].startswith('__') and i[0] != "return"]
