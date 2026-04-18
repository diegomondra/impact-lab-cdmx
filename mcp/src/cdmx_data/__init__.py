__version__ = "0.1.0"
__all__ = ["CDMX"]


def __getattr__(name):
    if name == "CDMX":
        from cdmx_data.core import CDMX
        return CDMX
    raise AttributeError(f"module 'cdmx_data' has no attribute {name!r}")
