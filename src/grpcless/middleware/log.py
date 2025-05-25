from typing import Callable, Coroutine, Any
import time
import random
from .. import log


def LogMiddleware(func: Callable[[Any], Coroutine]) -> Callable:
    async def warpper(request) -> Coroutine:
        st = time.time()
        try:
            ret = await func(request)
        except Exception as e:
            ed = time.time()
            log.log_request(ed - st, request.__name__)
            raise e
        ed = time.time()
        log.log_request(ed - st, request.__name__)
        return ret
    return warpper


def LogStreamMiddleware(func: Callable[[Any], Coroutine]) -> Callable:
    async def warpper(request) -> Coroutine:
        st = time.time()
        stream_id = random.randint(1000, 9999)
        log.log_stream_start(request.req_name, stream_id)
        try:
            ret = await func(request)
        except Exception as e:
            ed = time.time()
            log.log_stream_stop(ed - st, request.req_name, stream_id)
            raise e
        ed = time.time()
        log.log_stream_stop(ed - st, request.req_name, stream_id)
        return ret
    return warpper
