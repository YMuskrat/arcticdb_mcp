from typing import Callable, Dict

TOOL_REGISTRY: Dict[str, Callable] = {}


def register_tool(name: str):
    def decorator(fn):
        TOOL_REGISTRY[name] = fn
        return fn

    return decorator
