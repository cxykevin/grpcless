# from .. import log
from . import compile
from . import import_pb
from . import utils
from typing import Any


try:
    from ..import_fixer import real_import
    DBG_DYNAMIC_IMPORT = True
except ImportError:
    DBG_DYNAMIC_IMPORT = False
    real_import = None


class Proto():
    def __init__(self,
                 *proto_files: str,
                 proto_path: str,
                 output_dir: str = 'pb',
                 output_type: list[str] = [
                     "python", "grpclib_python", "mypy"],
                 other_include: list[str] = [],
                 ):
        compile.build(
            *proto_files,
            proto_path=proto_path,
            output_dir=output_dir,
            output_type=output_type,
            other_include=other_include
        )
        self._output_dir = output_dir
        self._prod_dist = []
        import_pb.init_path(output_dir)
        import_protos: dict[str, tuple] = {}

        if (real_import is not None):
            real_import()

        for i in proto_files:
            import_protos[i] = import_pb.import_proto(output_dir, i)
            basename = utils.patch_pbname(i)[1]
            self._prod_dist.append((i, basename, import_protos[i][-1]))
            setattr(self, "pb_"+basename, import_protos[i][0])
            setattr(self, "grpc_"+basename, import_protos[i][1])
            setattr(self, "manifest_"+basename, import_protos[i][2])
        self.import_protos = import_protos

    def get_service(self, proto: str):
        protofile, service_name = proto.split(":")
        return getattr(self.import_protos[protofile][1], service_name+"Base")

    def __getattribute__(self, name: str) -> Any:
        return super().__getattribute__(name)
