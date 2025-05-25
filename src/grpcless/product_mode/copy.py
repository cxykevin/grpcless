import os
import shutil
from .. import log


def copy_dist(*origin: str, dist: str = "dist"):
    for src in origin:
        if not os.path.exists(src):
            log.log_build(f"File not found: {src}")
            continue

        # 获取源文件/目录的名称
        src_name = os.path.basename(src)
        # 构建目标路径
        dst_path = os.path.join(dist, src_name)

        try:
            if os.path.isdir(src):
                # 如果是目录，使用shutil.copytree复制整个目录
                if os.path.exists(dst_path) and os.path.isdir(dst_path):
                    shutil.rmtree(dst_path)
                shutil.copytree(src, dst_path)
                log.log_build(f"Copy: {src} -> {dst_path}")
            else:
                # 如果是文件，使用shutil.copy2保留元数据
                shutil.copy2(src, dst_path)
                log.log_build(f"Copy: {src} -> {dst_path}")
        except Exception as e:
            log.log_build(f"Err: Copy: {src} -> {dst_path}")
