from typing import Callable, Any
import traceback

from .. import log
from grpclib.exceptions import GRPCError, StreamTerminatedError
from grpclib.const import Status


def ErrorTraceMiddleware(func: Callable[[Any], Any]) -> Callable:
    async def warpper(request) -> Any:
        try:
            ret = await func(request)
        except GRPCError as e:
            raise e
        except StreamTerminatedError as e:
            raise e
        except Exception as e:
            error_str = traceback.format_exc().strip("\n")
            for i in error_str.split("\n"):
                log.log_error("    "+i)

            raise GRPCError(
                status=Status.INTERNAL,
                message="Server Error: "+str(e),
                details={
                    "fullname": repr(e),
                    "middleware": "grpce.middleware.ErrorTraceMiddleware",
                    "server": "grpcE"
                }
            )
        return ret
    return warpper
