import sys
import importlib
import os
from .. import log
from . import utils


ENVCLEAN_LIST = [
    "DESCRIPTOR"
]


def init_path(path: str) -> None:
    log.log_import_access(path)
    sys.path.append(os.path.abspath(path))


def import_proto(path: str, proto: str) -> tuple:
    proto_pkg = utils.patch_pbname(proto)[1]+"_pb2"
    grpcproto_pkg = utils.patch_grpcname(proto)[1]+"_grpc"
    log.log_import_proto(proto)
    protoobj = importlib.import_module(proto_pkg)
    grpcprotoobj = importlib.import_module(grpcproto_pkg)
    return protoobj, grpcprotoobj, import_pyi(path, proto), (proto_pkg, grpcproto_pkg)


def import_pyi(path: str, proto: str) -> object:
    proto_pkg = path+os.sep+utils.patch_pbname(proto)[0]+"i"
    with open(proto_pkg) as f:
        code = f.read()
    env = {}
    try:
        exec(code, env, env)
    except Exception:
        pass
    for i in list(env.keys()):
        if i.startswith("_") or i in ENVCLEAN_LIST:
            del env[i]
    return env
