import inspect
import random
from abc import ABC, abstractmethod
from typing import Type, TypeVar, Any, get_type_hints

T = TypeVar('T', bound=ABC)


def create_implementation(_, abstract_class):
    """
    动态创建实现抽象类的类

    Args:
        abstract_class: 抽象类

    Returns:
        新创建的类
    """

    # 创建方法字典
    methods = {}

    rand_class_name = "VC_"+str(random.randint(1000000, 9999999))

    class_code = f"class {rand_class_name}(abstract_class):\n"

    # 获取所有抽象方法
    for name, method in inspect.getmembers(abstract_class, predicate=inspect.isfunction):
        if getattr(method, '__isabstractmethod__', False):
            # 获取返回类型
            hints = get_type_hints(method)
            return_type = hints.get('return', None)

            # 创建默认实现
            def make_method(name, return_type):
                def default_impl(self, *args, **kwargs):
                    return None
                # 复制原始方法的元数据
                default_impl.__module__ = method.__module__
                default_impl.__qualname__ = method.__qualname__
                default_impl.__doc__ = method.__doc__
                default_impl.__annotations__ = method.__annotations__
                default_impl.__name__ = name
                default_impl.__signature__ = inspect.signature(  # type: ignore
                    method)  # type: ignore

                return default_impl

            methods[name] = make_method(name, return_type)
            sig = inspect.signature(method)
            param_parts = []
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    param_parts.append('self')
                    continue
                if param.default is param.empty:
                    param_parts.append(param_name)
                else:
                    default_repr = repr(param.default)
                    param_parts.append(f"{param_name}={default_repr}")
                if param.kind == param.VAR_POSITIONAL:
                    param_parts[-1] = f"*{param_name}"
                elif param.kind == param.VAR_KEYWORD:
                    param_parts[-1] = f"**{param_name}"

            # 组合参数字符串
            params_str = ", ".join(param_parts)
            def_string = f"    def {name}({params_str}):\n        return None\n"

            class_code += def_string

    # 动态创建类
    return type(abstract_class.__name__, (abstract_class,), methods), rand_class_name, class_code
