from grpclib.server import Stream as gStream
from operator import methodcaller
from ..proto import Proto
from ..middleware import LogMiddleware, LogStreamMiddleware, ErrorTraceMiddleware
from grpclib.server import Server
import asyncio
from typing import Literal, AsyncGenerator
import sys
from typing import Any, Callable
try:
    UVLOOPMODE = True
    import uvloop  # type: ignore
except:
    UVLOOPMODE = False
from . import fill_abc
from . import setio
from .. import log
from .. import printfix
from .. import stream
import asyncio


async def default_server_life(server):
    yield


class GRPCLess():
    def __init__(self, proto: Proto, *service: str, life: Callable[[Any], AsyncGenerator[None, None]] = default_server_life, global_middleware: list[Callable] = [ErrorTraceMiddleware]):
        self.proto = proto
        self.service_to_class = {
            j.split(":")[0]: i for i, j in enumerate(service)}
        self.services = []
        self._prod_v_class_code = []
        for i in service:
            obj, class_name, class_code = fill_abc.create_implementation(i,
                                                                         proto.get_service(i))
            self.services.append(obj)
            self._prod_v_class_code.append((i, class_name, class_code))
        self.service_from_proto = [i for i in service]
        self.life = life
        self.global_middleware = global_middleware
        self.prod_gen_code = []
        self.before_call = []

    def run(self,
            host: str = "0.0.0.0",
            port: int = 50051,
            loop: Literal["auto", "asyncio", "uvloop", "proactor"] = "auto",
            fix_print: bool = True,
            ):
        if (fix_print):
            printfix.fix()

        if loop == "auto":
            if UVLOOPMODE:
                loop = "uvloop"
            elif sys.platform == 'win32':
                loop = "proactor"
            else:
                loop = "asyncio"
        if loop == "uvloop" and UVLOOPMODE:
            uvloop.install()  # type: ignore
        elif loop == "proactor":
            asyncio.set_event_loop_policy(
                asyncio.WindowsProactorEventLoopPolicy())  # type: ignore

        async def start_server():
            server = Server([i() for i in self.services])
            for i in self.before_call:
                await i(self)
            async for _ in self.life(server):
                await server.start(host, port)
                await server.wait_closed()

        log.log_start_server(host, port, loop)

        asyncio.run(start_server())

    def add_middleware(self, middleware: Callable):
        self.global_middleware.append(middleware)

    def add_before_func(self, call):
        self.before_call.append(call)

    def __set_func_io(self, func: Callable, method: str, stream=None):
        return setio.set_func_io(self, func, method, stream)

    def request(self, method: str, *, middleware: list[Callable] = [], _sys_middleware: list[Callable] = [LogMiddleware], use_global_middleware: bool = True):
        sum_middleware = _sys_middleware + middleware

        def decorator(func):
            # 构建输入映射
            obj, methodname, request_solve, outtype_realobj, response_solve = self.__set_func_io(
                func, method)

            # 构建中间件
            async def run(request):
                return response_solve(await request_solve(request, func) or {}, outtype_realobj)
            if (use_global_middleware):
                for i in reversed(self.global_middleware):
                    run = i(run)
            for i in reversed(sum_middleware):
                run = i(run)

            async def wrapper(self, stream):
                request = await stream.recv_message()
                ret = await run(request)
                await stream.send_message(ret)
            setattr(obj, methodname, wrapper)
            return wrapper
        return decorator

    def stream(self, method: str, *, middleware: list[Callable] = [LogStreamMiddleware], use_global_middleware: bool = True, _sys_middleware: list[Callable] = [LogStreamMiddleware]):
        sum_middleware = _sys_middleware + middleware

        def decorator(func):
            # 构建输入映射
            obj, methodname, request_solve, outtype_realobj, response_solve = self.__set_func_io(
                func, method)

            async def run(request):
                streams = stream.Stream(
                    request, (lambda x: response_solve(x or {}, outtype_realobj)), methodname)
                ret = await func(streams)
                await asyncio.sleep(0.01)  # 不加这个会 13 INTERNAL
                # try:
                #     await streams.close()
                # except:
                #     pass
                return ret
            # 构建中间件
            if (use_global_middleware):
                for i in reversed(self.global_middleware):
                    run = i(run)
            for i in reversed(sum_middleware):
                run = i(run)

            async def wrapper(self, stream):
                stream.req_name = methodname
                return await run(stream)
            setattr(obj, methodname, wrapper)
            return wrapper
        return decorator

    def server_stream(self, method: str, *, middleware: list[Callable] = [LogStreamMiddleware], use_global_middleware: bool = True, _sys_middleware: list[Callable] = [LogStreamMiddleware]):
        sum_middleware = _sys_middleware + middleware

        def decorator(func):
            # 构建输入映射
            obj, methodname, request_solve, outtype_realobj, response_solve = self.__set_func_io(
                func, method, True)

            async def run(request: gStream):
                req_ctx = request
                req = await req_ctx.recv_message()
                streams = stream.ServerStream(
                    req_ctx, (lambda x: response_solve(x or {}, outtype_realobj)), methodname)
                ret = await request_solve(req, func, streams)
                await streams.close()
                await asyncio.sleep(0.01)  # 不加这个会 13 INTERNAL
                return ret
            # 构建中间件
            if (use_global_middleware):
                for i in reversed(self.global_middleware):
                    run = i(run)
            for i in reversed(sum_middleware):
                run = i(run)

            async def wrapper(self, stream):
                stream.req_name = methodname
                return await run(stream)
            setattr(obj, methodname, wrapper)
            return wrapper
        return decorator

    def client_stream(self, method: str, *, middleware: list[Callable] = [], use_global_middleware: bool = True, _sys_middleware: list[Callable] = [LogStreamMiddleware]):

        sum_middleware = _sys_middleware + middleware

        def decorator(func):
            # 构建输入映射
            obj, methodname, request_solve, outtype_realobj, response_solve = self.__set_func_io(
                func, method, True)

            async def run(request: gStream):
                req_ctx = request
                streams = stream.ClientStream(
                    req_ctx, (lambda x: response_solve(x or {}, outtype_realobj)), methodname)
                ret = response_solve(await func(streams) or {}, outtype_realobj)
                await request.send_message(ret)
                return None
            # 构建中间件
            if (use_global_middleware):
                for i in reversed(self.global_middleware):
                    run = i(run)
            for i in reversed(sum_middleware):
                run = i(run)

            async def wrapper(self, stream):
                stream.req_name = methodname
                return await run(stream)
            setattr(obj, methodname, wrapper)
            return wrapper
        return decorator
