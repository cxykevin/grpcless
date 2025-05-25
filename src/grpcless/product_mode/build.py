import os
from ..engine import GRPCLess
import shutil
from .. import log

NOWPATH = os.path.abspath(os.path.dirname(
    __file__)+os.sep+".."+os.sep+"..")
PKGNAME = "grpcless"

REWRITE_ENGINE_SETIO_TEMPLATE = """
def set_func_io(self, func, method: str, stream=None):
"""
REWRITE_ENGINE_FILLABC_HEAD_TEMPLATE = """
def create_implementation(srv, abstract_class):
"""

REWRITE_PROTO_HEAD_TEMPLATE = """
from typing import Any
"""
REWRITE_PROTO_CLASS_TEMPLATE = """
class Proto():
    def __init__(self,
                 *proto_files: str,
                 proto_path: str,
                 output_dir: str = 'pb',
                 output_type: list[str] = [
                     "python", "grpclib_python", "mypy"],
                 other_include: list[str] = [],
                 ):
"""
REWRITE_PROTO_TAIL_TEMPLATE = """
    def get_service(self, proto: str):
        protofile, service_name = proto.split(":")
        return getattr(self.import_protos[protofile][1], service_name+"Base")
"""


def build(app: GRPCLess, dist: str = "dist"):
    log.log_build_start()
    if (os.path.exists(dist)):
        log.log_build("Remove old dist")
        shutil.rmtree(dist)
    log.log_build("Copy lib")
    shutil.copytree(NOWPATH+os.sep+PKGNAME, dist+os.sep+PKGNAME)
    log.log_build("Create setio")
    rewrite_ENGINE_SETIO_TEMPLATE = """
from . import utils
def set_func_io(self, func, method: str, stream=None):
"""
    for i in app.prod_gen_code:
        method = i["name"]
        if (":" in method):
            obj = f"self.services[self.service_to_class[{repr(method)}]]"
            methodname = method.split(":")[1]
        else:
            obj = f"self.services[0]"
            methodname = method
        rewrite_ENGINE_SETIO_TEMPLATE += f"    if method == '{i["name"]}':\n"
        rewrite_ENGINE_SETIO_TEMPLATE += f"        return {obj},{repr(methodname)},{i["code"][0]},self.proto.pb_{i["outtype"][0]}.{i["outtype"][1]},{i["code"][1]}\n"
    rewrite_ENGINE_SETIO_TEMPLATE += "    raise ValueError('method not found')"
    with open(dist+os.sep+PKGNAME+os.sep+"engine"+os.sep+"setio.py", "w") as f:
        f.write(rewrite_ENGINE_SETIO_TEMPLATE)

    log.log_build("Create fillabc")
    code_fill_abc = REWRITE_ENGINE_FILLABC_HEAD_TEMPLATE
    for i in app._prod_v_class_code:
        srv_name = i[0]
        cls_name = i[1]
        cls_code = i[2]
        code_fill_abc += f"    if(srv=={repr(srv_name)}):\n"
        code_fill_abc += '\n'.join([" "*8+j for j in cls_code.split("\n")])
        code_fill_abc += f"\n        return {cls_name},{repr(cls_name)},''\n"

    with open(dist+os.sep+PKGNAME+os.sep+"engine"+os.sep+"fill_abc.py", "w") as f:
        f.write(code_fill_abc)

    log.log_build("Copy proto")
    # copy proto
    proto_dist_path = app.proto._output_dir
    for i in os.listdir(proto_dist_path):
        if (i.endswith(".py") and i != "__init__.py"):
            shutil.copy(proto_dist_path+os.sep+i, dist+os.sep+i)

    log.log_build("Create protoobj")
    code_head = REWRITE_PROTO_HEAD_TEMPLATE
    code_class_first = REWRITE_PROTO_CLASS_TEMPLATE
    code_class_first += "        self.import_protos={\n"
    code_class_second = ""
    cnt = 0
    for i in app.proto._prod_dist:
        file_name = i[0]
        base_name = i[1]
        proto_module = i[2][0]
        proto_grpc_module = i[2][1]
        code_head += f"import {proto_module} as pb_module_gen_{cnt}\n"
        code_head += f"import {proto_grpc_module} as pbgrpc_module_gen_{cnt}\n"
        code_class_first += f"            {repr(file_name)}: (pb_module_gen_{cnt}, pbgrpc_module_gen_{cnt}, {{}}),\n"
        code_class_second += f"        self.pb_{base_name}=pb_module_gen_{cnt}\n"
        code_class_second += f"        self.grpc_{base_name}=pbgrpc_module_gen_{cnt}\n"
        code_class_second += f"        self.manifest_{base_name}={{}}\n"
        cnt += 1
    code_class_first += "        }\n"
    code = code_head + code_class_first + \
        code_class_second + REWRITE_PROTO_TAIL_TEMPLATE
    with open(dist+os.sep+PKGNAME+os.sep+"proto"+os.sep+"__init__.py", "w") as f:
        f.write(code)

    # 删除不必要的组件
    shutil.rmtree(dist+os.sep+PKGNAME+os.sep+"product_mode")
    shutil.rmtree(dist+os.sep+PKGNAME+os.sep+"import_fixer")

    log.log_build("Finish level")
