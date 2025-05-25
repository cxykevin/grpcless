import os
import sys
from .. import log
try:
    ABLE_BUILD_FLAG = True
    from grpc_tools import protoc
except ImportError:
    ABLE_BUILD_FLAG = False
import tempfile


def build(
    *proto_files: str,
    proto_path: str,
    output_dir: str = 'pb',
    output_type: list[str] = [
        "python", "grpclib_python", "mypy"],
        other_include: list[str] = [],):
    path = os.path.abspath(proto_path)
    outputpath = output_dir.lstrip("./")
    global_build_flag = True
    if (not os.path.exists(path)):
        global_build_flag = False
        if (not os.path.exists(outputpath)):
            log.log_compile_global_fault(
                "Compiled Proto not found")
            sys.exit(210)
    if (not os.path.exists(outputpath)):
        os.makedirs(outputpath)
    if (not os.path.exists(outputpath+os.sep+"__init__.py")):
        with open(outputpath+os.sep+"__init__.py", "w") as file:
            file.write("")
    if (not os.path.exists(outputpath+os.sep+".grpcEcache")):
        with open(outputpath+os.sep+".grpcEcache", "w") as file:
            file.write(";")
    with open(outputpath+os.sep+".grpcEcache", "r") as file:
        info = {i.split(";")[0]: i.split(";")[1]
                for i in file.read().rstrip("\n").split("\n")}
    if global_build_flag:
        if (ABLE_BUILD_FLAG is False):
            log.log_compile_global_fault(
                "grpcio-tools Not found")
            sys.exit(210)
        for protoname in proto_files:
            if (not os.path.exists(path+os.sep+protoname)):
                log.log_compile_global_fault(
                    f'File "{protoname}" not found')
            file_lasttime = os.path.getmtime(path+os.sep+protoname)
            if (info.get(path+os.sep+protoname, "") == str(file_lasttime)):
                continue

            args = [
                'grpc_tools.protoc',
                '-I=.',
                '--proto_path='+path
            ]
            args.extend(['-I='+i for i in other_include])
            args.extend(['--'+i+'_out=./'+outputpath for i in output_type])
            args.append(protoname)

            log.log_compile(protoname)

            # 保存原始的文件描述符
            original_stdout_fd = os.dup(sys.stdout.fileno())
            original_stderr_fd = os.dup(sys.stderr.fileno())

            # 创建临时文件
            with tempfile.NamedTemporaryFile(mode='w+', delete=False) as stdout_temp, \
                    tempfile.NamedTemporaryFile(mode='w+', delete=False) as stderr_temp:

                try:
                    # 重定向标准输出和标准错误到临时文件
                    os.dup2(stdout_temp.fileno(), sys.stdout.fileno())
                    os.dup2(stderr_temp.fileno(), sys.stderr.fileno())

                    # 执行 protoc
                    result = protoc.main(args)  # type: ignore

                finally:
                    # 恢复原始的文件描述符
                    os.dup2(original_stdout_fd, sys.stdout.fileno())
                    os.dup2(original_stderr_fd, sys.stderr.fileno())
                    os.close(original_stdout_fd)
                    os.close(original_stderr_fd)

                    # 确保所有内容都写入临时文件
                    sys.stdout.flush()
                    sys.stderr.flush()

            with open(stderr_temp.name, 'r') as f:
                stderr_output = f.read()

            # 删除临时文件
            os.unlink(stdout_temp.name)
            os.unlink(stderr_temp.name)

            # 处理输出
            if result != 0:
                stderr_output = stderr_output.strip('\n')
                for i in stderr_output.split("\n"):
                    if (" " in i):
                        file_name = i.split(" ")[0][:-1]
                        if (":" not in file_name):
                            log.log_compile_global_fault(
                                i)
                        else:
                            file_more = i[len(file_name)+2:]

                            log.log_compile_file_fault(
                                file_name, file_more)
                    else:
                        log.log_compile_global_fault(
                            i)

                sys.exit(212)
            # if "grpc_python" in output_type:
            #     patched_grpcname, patched_grpcnameorigin = patch_grpcname(
            #         protoname)
            #     with open(outputpath+os.sep+patched_grpcname, "r") as file:
            #         data = file.read()
            #     with open(outputpath+os.sep+patched_grpcname, "w") as file:
            #         file.write(data.replace(
            #             f"import {patched_grpcnameorigin}_pb2", f"from . import {patched_grpcnameorigin}_pb2"))

            info[path+os.sep+protoname] = str(file_lasttime)
        with open(outputpath+os.sep+".grpcEcache", "w") as file:
            file.write("\n".join([f"{k};{v}" for k, v in info.items()]))
