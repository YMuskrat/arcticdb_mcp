from typing import Any, Callable, Dict

TOOL_REGISTRY: Dict[str, Callable] = {}
TOOL_METADATA: Dict[str, Dict[str, Any]] = {}


def register_tool(name: str, *, read_only: bool = False):
    def decorator(fn):
        if name in TOOL_REGISTRY and TOOL_REGISTRY[name] is not fn:
            raise ValueError(f"Tool '{name}' is already registered to another function.")
        TOOL_REGISTRY[name] = fn
        TOOL_METADATA[name] = {
            "read_only": bool(read_only),
        }
        return fn

    return decorator


def is_read_tool(name: str) -> bool:
    """Return True if the tool was explicitly registered as read-only."""
    meta = TOOL_METADATA.get(name)
    if meta is None:
        return False
    return bool(meta.get("read_only", False))


def get_tools(read_only: bool = False) -> Dict[str, Callable]:
    """Return registered tools, filtered to read-only tools if requested."""
    if not read_only:
        return dict(TOOL_REGISTRY)
    return {name: fn for name, fn in TOOL_REGISTRY.items() if is_read_tool(name)}

