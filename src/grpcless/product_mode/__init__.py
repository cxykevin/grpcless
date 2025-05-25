from . import build, copy
from ..engine import GRPCLess


def run(app: GRPCLess, dist: str = "dist", origin=[]):
    build.build(app, dist)
    copy.copy_dist(*origin, dist=dist)
