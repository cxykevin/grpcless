
import os
import platform
import sys


__all__ = [
    "RESET",
    "FG_BLACK",
    "FG_RED",
    "FG_GREEN",
    "FG_YELLOW",
    "FG_BLUE",
    "FG_MAGENTA",
    "FG_CYAN",
    "FG_WHITE",
    "FG_DEFAULT",
    "BG_BLACK",
    "BG_RED",
    "BG_GREEN",
    "BG_YELLOW",
    "BG_BLUE",
    "BG_MAGENTA",
    "BG_CYAN",
    "BG_WHITE",
    "BG_DEFAULT",
    "FG_GREY",
    "BG_GREY",
]


def supports_color():
    if os.getenv('ANSI_COLORS_DISABLED') is not None:
        return False
    if not sys.stdout.isatty():
        return False
    plat = platform.system()
    if plat == 'Windows':
        if int(platform.release()) >= 10:
            try:
                build = int(platform.version().split('.')[-1])
                if build >= 14931:
                    return True
            except (ValueError, IndexError):
                pass
        return os.getenv('ANSICON') is not None or \
            os.getenv('WT_SESSION') is not None or \
            os.getenv('ConEmuANSI') == 'ON' or \
            os.getenv('TERM') == 'xterm'
    # 对于 Linux, macOS 等类 Unix 系统，大多数终端支持颜色
    return True


if supports_color():
    RESET = '\033[0m'
    FG_BLACK = '\033[30m'
    FG_RED = '\033[31m'
    FG_GREEN = '\033[32m'
    FG_YELLOW = '\033[33m'
    FG_BLUE = '\033[34m'
    FG_MAGENTA = '\033[35m'
    FG_CYAN = '\033[36m'
    FG_WHITE = '\033[37m'
    FG_DEFAULT = '\033[39m'
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    BG_DEFAULT = '\033[49m'
    FG_GREY = '\033[90m'
    BG_GREY = '\033[100m'
else:
    RESET = ''
    FG_BLACK = ''
    FG_RED = ''
    FG_GREEN = ''
    FG_YELLOW = ''
    FG_BLUE = ''
    FG_MAGENTA = ''
    FG_CYAN = ''
    FG_WHITE = ''
    FG_DEFAULT = ''
    BG_BLACK = ''
    BG_RED = ''
    BG_GREEN = ''
    BG_YELLOW = ''
    BG_BLUE = ''
    BG_MAGENTA = ''
    BG_CYAN = ''
    BG_WHITE = ''
    BG_DEFAULT = ''
    FG_GREY = ''
    BG_GREY = ''
