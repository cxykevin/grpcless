from grpclib.server import Stream as gStream
from typing import Any, Callable
from grpclib.exceptions import StreamTerminatedError


class Stream(gStream):
    def __init__(self, stream: gStream, fix_func: Callable = (lambda x: x), name: str = ""):
        self._fix_func = fix_func
        self._original_stream = stream
        self.req_name = name

    def __getattr__(self, name):
        return getattr(self._original_stream, name)

    def original_stream_mode(self):
        self.send_message = self.send_message_original

    async def send_message(self, message: Any) -> None:
        message = self._fix_func(message)
        return await super().send_message(message)

    async def send_message_original(self, message: Any) -> None:
        return await super().send_message(message)

    async def recv_message(self) -> Any | None:
        ret = await super().recv_message()
        if (ret is None):
            raise StreamTerminatedError()
        return ret

    def __aiter__(self):
        return self

    async def __anext__(self) -> Any:
        if (ret := await super().recv_message()) is None:
            raise StopAsyncIteration
        else:
            return ret

    async def cancel(self):
        return await super().cancel()

    async def close(self):
        return await super().__aexit__(None, None, None)


class ClientStream(Stream):
    async def send_message(self, message: Any) -> None:
        raise Exception("ClientStream can't send message")


class ServerStream(Stream):
    async def recv_message(self) -> Any | None:
        raise Exception("ServerStream can't recv message")

    async def __anext__(self) -> Any:
        raise Exception("ServerStream can't recv message")
