from .pool import PoolObj
from ..engine import GRPCLess
from contextlib import asynccontextmanager
from typing import TypeVar, Generic, AsyncGenerator, Any

T = TypeVar('T')


class Client(Generic[T]):
    def __init__(self, app: GRPCLess, addr: str, service: str, args: dict = {}):
        self.pool = PoolObj(addr.split(":")[0], int(
            addr.split(":")[1]), **args)
        self.proto_file_name = service.split(":")[0]
        self.service_name = service.split(":")[1]
        self.service = getattr(
            app.proto.import_protos[self.proto_file_name][1], self.service_name+"Stub")

        async def start_pool(*args):
            await self.pool.start()
        app.add_before_func(start_pool)

    @asynccontextmanager
    async def __call__(self) -> AsyncGenerator[T, None]:
        async with self.pool.get_connection() as conn:
            yield self.service(conn)
