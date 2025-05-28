import sys

from .color import *
from .time import get_t, format_time_duration
import time as sys_time


def print_logo() -> None:
    sys.stderr.write(FG_BLUE+" ==== grpcE Engine ==== "+RESET+"\n")


def log_compile(compile_file: str) -> None:
    sys.stdout.write(
        f'{FG_GREY}{get_t()}{RESET}|{BG_MAGENTA}COMPILE{RESET}|{FG_GREY}   0ns{RESET}|Compile file "{compile_file}"\n')


def log_compile_global_fault(msg: str) -> None:
    sys.stdout.write(
        f'{FG_GREY}{get_t()}{RESET}|{BG_MAGENTA}COMPILE{RESET}|{FG_GREY}   0ns{RESET}|{FG_RED}ERR{RESET}: {msg}\n')


def log_compile_file_fault(file: str, msg: str) -> None:
    sys.stdout.write(
        f'{FG_GREY}{get_t()}{RESET}|{BG_MAGENTA}COMPILE{RESET}|{FG_GREY}   0ns{RESET}|{FG_RED}ERR{RESET}: {FG_GREY}{file}{RESET}|{msg}\n')


def log_import_access(path: str) -> None:
    sys.stdout.write(
        f'{FG_GREY}{get_t()}{RESET}|{BG_MAGENTA}PROTO  {RESET}|{FG_GREY}   0ns{RESET}|Access output path: "{path}"\n')


def log_import_proto(file: str) -> None:
    sys.stdout.write(
        f'{FG_GREY}{get_t()}{RESET}|{BG_MAGENTA}PROTO  {RESET}|{FG_GREY}   0ns{RESET}|Import file: "{file}"\n')


def log_start_server(host: str, port: int, loop: str) -> None:
    sys.stdout.write(
        f'{FG_GREY}{get_t()}{RESET}|{BG_BLUE}SERVER {RESET}|{FG_GREY}   0ns{RESET}|\n')
    sys.stdout.write(
        f'{FG_GREY}{get_t()}{RESET}|{BG_BLUE}SERVER {RESET}|{FG_GREY}   0ns{RESET}|{FG_BLUE} ▄████ {RESET}| Python grpcLess Engine\n')
    sys.stdout.write(
        f'{FG_GREY}{get_t()}{RESET}|{BG_BLUE}SERVER {RESET}|{FG_GREY}   0ns{RESET}|{FG_BLUE} █   ▄ {RESET}| {FG_GREY}Do less, Create more{RESET}\n')
    sys.stdout.write(
        f'{FG_GREY}{get_t()}{RESET}|{BG_BLUE}SERVER {RESET}|{FG_GREY}   0ns{RESET}|{FG_BLUE} ▀████ {RESET}| ------------------\n')
    sys.stdout.write(
        f'{FG_GREY}{get_t()}{RESET}|{BG_BLUE}SERVER {RESET}|{FG_GREY}   0ns{RESET}|{FG_BLUE} ▄   ▀ {RESET}| Loop Engine: {loop}\n')
    sys.stdout.write(
        f'{FG_GREY}{get_t()}{RESET}|{BG_BLUE}SERVER {RESET}|{FG_GREY}   0ns{RESET}|{FG_BLUE} ▀████ {RESET}| Address: {FG_GREEN}{host}:{port}{RESET}\n')
    sys.stdout.write(
        f'{FG_GREY}{get_t()}{RESET}|{BG_BLUE}SERVER {RESET}|{FG_GREY}   0ns{RESET}|\n')


def log_request(dur: float, name: str) -> None:
    sys.stdout.write(
        f'{FG_GREY}{get_t()}{RESET}|{BG_GREEN}REQUEST{RESET}|{FG_GREY}{format_time_duration(dur):>6}{RESET}|Get "{name}"\n')


def log_stream_start(name: str, stream_id: int) -> None:
    sys.stdout.write(
        f'{FG_GREY}{get_t()}{RESET}|{BG_GREEN}REQUEST{RESET}|{FG_GREY}   0ns{RESET}|Stream "{name}"{FG_GREY}[{stream_id}]{RESET} start\n')


def log_stream_stop(dur: float, name: str, stream_id: int) -> None:
    sys.stdout.write(
        f'{FG_GREY}{get_t()}{RESET}|{BG_GREEN}REQUEST{RESET}|{FG_GREY}{format_time_duration(dur):>6}{RESET}|Stream "{name}"{FG_GREY}[{stream_id}]{RESET} stop\n')


def log_print(msg: str) -> None:
    sys.stdout.write(
        f'{FG_GREY}{get_t()}{RESET}|{BG_GREY}DEBUG  {RESET}|{FG_GREY}   0ns{RESET}|{msg}\n')


def log_error(msg: str) -> None:
    sys.stdout.write(
        f'{FG_GREY}{get_t()}{RESET}|{BG_RED}ERROR  {RESET}|{FG_GREY}   0ns{RESET}|{msg}\n')


def log_build_start() -> None:
    global st_time
    st_time = sys_time.time()
    sys.stdout.write(
        f'{FG_GREY}{get_t()}{RESET}|{BG_BLUE}BUILD  {RESET}|{FG_GREY}   0ns{RESET}|Start build\n')


def log_build(msg: str) -> None:
    sys.stdout.write(
        f'{FG_GREY}{get_t()}{RESET}|{BG_BLUE}BUILD  {RESET}|{FG_GREY}{format_time_duration(sys_time.time()-st_time):>6}{RESET}|{msg}\n')


def log_client(dur: float, msg: str) -> None:
    sys.stdout.write(
        f'{FG_GREY}{get_t()}{RESET}|{BG_CYAN}CLIENT {RESET}|{FG_GREY}{format_time_duration(dur):>6}{RESET}|{msg}\n')
