import builtins
from ..log import log_print
import sys


def print(*values,
          sep: str = ' ',
          end: str = '\n',
          file=None,
          flush: bool = False) -> None:

    # 将所有值转换为字符串并用 sep 连接
    output = sep.join(str(value) for value in values)

    # 添加结束字符
    output += end

    # 写入到指定的文件对象
    if file is not None:
        file.write(output)
        if flush:
            file.flush()
        return

    for i in output.rstrip("\n").split("\n"):
        log_print(i)


def fix():
    builtins.print = print
