from typing import Callable, Dict

TOOL_REGISTRY: Dict[str, Callable] = {}


def register_tool(name: str):
    def decorator(fn):
        if name in TOOL_REGISTRY and TOOL_REGISTRY[name] is not fn:
            raise ValueError(f"Tool '{name}' is already registered to another function.")
        TOOL_REGISTRY[name] = fn
        return fn

    return decorator
