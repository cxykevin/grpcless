#!/usr/bin/env python
import argparse
import importlib.util
import os
import sys
try:
    from ..product_mode import run as build
except ImportError:
    build = None


def import_from_path(path: str):
    """从路径导入对象，格式为 file_path:object_name"""
    if ":" not in path:
        raise ValueError(
            f"Invalid format: {path}. Expected format: file_path:object_name")

    file_path, object_name = path.split(":", 1)

    # 确保文件路径是绝对路径
    if not os.path.isabs(file_path):
        file_path = os.path.abspath(file_path)

    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # 导入模块
    module_name = os.path.basename(file_path).replace(".py", "")
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not import module from {file_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    # 获取对象
    if not hasattr(module, object_name):
        raise AttributeError(
            f"Object '{object_name}' not found in {file_path}")

    return getattr(module, object_name)


def run_command(args):
    """执行run命令的逻辑"""
    try:
        app = import_from_path(args.app_path)
        app.run(host=args.host, port=args.port, loop=args.loop)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def build_command(args):
    """执行build命令的逻辑"""
    try:
        app = import_from_path(args.app_path)
        if (build != None):
            build(app, args.dist, args.sources)
        else:
            print("build is not useable in product mode!")
            sys.exit(1)

    except Exception as e:
        print(f"Error during build: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """主函数，设置命令行参数解析"""
    parser = argparse.ArgumentParser(
        description="Command line tool for running and building applications"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # 创建run命令的子解析器
    run_parser = subparsers.add_parser("run", help="Run an application")
    run_parser.add_argument(
        "app_path",
        type=str,
        help="Path to the application in the format file_path:app_name (e.g., main.py:app)"
    )
    run_parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind the server to (default: 0.0.0.0)"
    )
    run_parser.add_argument(
        "--port",
        type=int,
        default=50051,
        help="Port to bind the server to (default: 50051)"
    )
    run_parser.add_argument(
        "--loop",
        type=str,
        choices=["auto", "asyncio", "uvloop", "proactor"],
        default="auto",
        help="Event loop implementation to use (default: auto)"
    )

    # 创建build命令的子解析器
    build_parser = subparsers.add_parser("build", help="Build an application")
    build_parser.add_argument(
        "app_path",
        type=str,
        help="Path to the application in the format file_path:app_name (e.g., main.py:app)"
    )
    build_parser.add_argument(
        "--dist",
        type=str,
        default="dist",
        help="Directory where build artifacts will be saved"
    )
    build_parser.add_argument(
        "sources",
        nargs="*",
        help="Source files or directories to include in the build"
    )

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    if args.command == "run":
        run_command(args)
    elif args.command == "build":
        build_command(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
