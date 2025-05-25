import sys
from importlib.machinery import ModuleSpec
import types
import importlib
from importlib.abc import Loader


class LazyLoader(Loader):
    def __init__(self, module_name):
        self.module_name = module_name

    def create_module(self, spec):
        """创建模块对象"""
        # 先创建一个代理模块
        mod = LazyModule(self.module_name, self.module_name)
        import_pb_list.append(mod)
        return mod

    def exec_module(self, module):
        pass


class LazyModule(types.ModuleType):
    """代理模块，在访问属性时才加载真实模块"""

    def __init__(self, name, real_mod: str):
        self.__name__ = name
        self.__package__ = None
        self.__spec__ = None
        self.real_module = None
        self.real_module_name = real_mod

    def __set_real_module__(self):
        importlib.reload(sys.modules[self.real_module_name])


class ImportFixer:
    def find_spec(self, name: str, path, target=None):
        if (name.endswith("_pb2") or name.endswith("_grpc")):
            # 创建带有延迟加载器的 ModuleSpec
            loader = LazyLoader(name)
            spec = ModuleSpec(name, loader)
            return spec
        return None


import_pb_list: list[LazyModule] = []


fixer = ImportFixer()


def fix():
    sys.meta_path.insert(0, fixer)


def real_import():
    global import_pb_list
    sys.meta_path.remove(fixer)
    for i in import_pb_list:
        i.__set_real_module__()
    import_pb_list = []
