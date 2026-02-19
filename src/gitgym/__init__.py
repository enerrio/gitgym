from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("gitgym")
except PackageNotFoundError:
    __version__ = "unknown"
