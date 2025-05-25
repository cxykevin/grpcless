
def patch_grpcname(protoname: str) -> tuple[str, str]:
    patch_grpcnameorigin = protoname
    if (patch_grpcnameorigin.endswith(".proto")):
        patch_grpcnameorigin = patch_grpcnameorigin[:-6]
    patch_grpcname = patch_grpcnameorigin + "_grpc.py"
    return patch_grpcname, patch_grpcnameorigin


def patch_pbname(protoname: str) -> tuple[str, str]:
    patch_pbnameorigin = protoname
    if (patch_pbnameorigin.endswith(".proto")):
        patch_pbnameorigin = patch_pbnameorigin[:-6]
    patch_pbname = patch_pbnameorigin + "_pb2.py"
    return patch_pbname, patch_pbnameorigin
