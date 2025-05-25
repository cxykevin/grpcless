from datetime import datetime


def get_t() -> str:
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def format_time_duration(seconds: float) -> str:
    if seconds < 0:
        return f"-{format_time_duration(-seconds)}"

    if seconds >= 180:
        return f"{int(seconds)//60}m"
    if seconds >= 1:
        return f"{int(seconds)}s"
    milliseconds = seconds * 1000
    if milliseconds >= 1:
        return f"{int(milliseconds)}ms"
    microseconds = milliseconds * 1000
    if microseconds >= 1:
        return f"{int(microseconds)}μs"
    nanoseconds = microseconds * 1000
    return f"{int(nanoseconds)}ns"
