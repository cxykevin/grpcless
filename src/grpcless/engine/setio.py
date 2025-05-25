import inspect

from . import utils
from typing import Callable


def set_func_io(self, func: Callable, method: str, stream=None):
    if (":" in method):
        obj = self.services[self.service_to_class[method.split(":")[
            0]]]
        methodname = method.split(":")[1]
    else:
        obj = self.services[0]
        methodname = method
    func_inspect = inspect.signature(func)
    build_code = "(lambda request,func,stream=None: func("
    for name, _ in func_inspect.parameters.items():
        if name == "stream":
            continue
        build_code += f"{name}=request.{name},"
    if (stream != None):
        build_code += f"stream=stream,"
    build_code += "))"
    request_solve = eval(build_code)

    # 展开输出
    method_obj = getattr(obj, methodname)
    out_typename = utils.extract_class_from_type_string(
        method_obj.__annotations__["stream"], 1)
    if (out_typename[0].endswith("_pb2")):
        out_typename[0] = out_typename[0][:-4]  # type: ignore
    outtype_obj = getattr(self.proto, "manifest_" +
                          out_typename[0])[out_typename[1]]
    outtype_realobj = getattr(getattr(self.proto, "pb_" +
                                      out_typename[0]), out_typename[1])
    vals = utils.get_val_from_pb(outtype_obj)

    outtype_obj.__instancecheck__ = (lambda *args, **kwargs: True)
    outtype_obj.__subclasscheck__ = (lambda *args, **kwargs: True)

    # 构建输出映射
    build_code_out = "(lambda response,type_f: type_f("
    for name, _ in vals:
        build_code_out += f"{name}=response.get(\"{name}\",None),"
    build_code_out += "))"
    self.prod_gen_code.append({
        "name": method,
        "code": (build_code, build_code_out),
        "outtype": (out_typename[0], out_typename[1])
    })
    response_solve = eval(build_code_out)
    return obj, methodname, request_solve, outtype_realobj, response_solve
