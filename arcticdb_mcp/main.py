import os
import sys
import inspect
from pathlib import Path
from fastmcp import FastMCP

# Allow running both as a package module and as a standalone script
if __package__ in (None, ""):
    pkg_path = Path(__file__).resolve().parent
    sys.path.insert(0, str(pkg_path.parent))
    __package__ = pkg_path.name

from typing import Optional
from .registry import TOOL_REGISTRY, get_tools


def is_read_only_mode() -> bool:
    """
    Check if read-only mode is enabled via ARCTICDB_MCP_READ_ONLY environment variable.
    Returns True for '1', 'true', 'yes', 'on' (case-insensitive).
    Returns False for '0', 'false', 'no', 'off', or when unset/empty.
    Raises ValueError for any unrecognized value.
    """
    val = os.getenv("ARCTICDB_MCP_READ_ONLY")
    if val is None or val == "":
        return False
    val_clean = val.strip().lower()
    if val_clean in ("1", "true", "yes", "on"):
        return True
    if val_clean in ("0", "false", "no", "off"):
        return False
    raise ValueError(
        f"Invalid ARCTICDB_MCP_READ_ONLY value: {val!r}. "
        "Expected boolean ('true', 'false', '1', '0')."
    )


# Import tool modules to trigger @register_tool side-effects
from . import tools as _tools  # noqa: F401


def register_tools_to_server(server: FastMCP, read_only: bool = False) -> None:
    """Register tools onto a FastMCP server instance, respecting read_only mode."""
    tools = get_tools(read_only=read_only)
    for name, func in tools.items():
        server.tool(name=name)(func)


def create_mcp_server(read_only: Optional[bool] = None) -> FastMCP:
    """Create and configure a FastMCP server instance with registered tools."""
    if read_only is None:
        read_only = is_read_only_mode()
    server = FastMCP("arcticdb-mcp")
    register_tools_to_server(server, read_only=read_only)
    return server


mcp = create_mcp_server()



def _run_http_sse(port: int):
    """
    Run FastMCP in HTTP/SSE mode.
    - fastmcp 3.x: run() uses **transport_kwargs; use transport="http"
    - fastmcp 2.x: run() has explicit host/port params; use transport="sse"
    """
    run_sig = inspect.signature(type(mcp).run)
    params = run_sig.parameters
    if "host" in params:
        # fastmcp 2.x — explicit host/port on run()
        mcp.run(transport="sse", host="0.0.0.0", port=port)
    elif "transport" in params:
        # fastmcp 3.x — host/port passed as transport_kwargs, transport="http"
        mcp.run(transport="http", host="0.0.0.0", port=port)


def main():
    is_read_only_mode()
    port = os.getenv("ARCTICDB_MCP_PORT")
    if port:
        try:
            parsed_port = int(port)
        except ValueError:
            raise ValueError("ARCTICDB_MCP_PORT must be an integer from 1 to 65535.") from None
        if not 1 <= parsed_port <= 65535:
            raise ValueError("ARCTICDB_MCP_PORT must be an integer from 1 to 65535.")
        _run_http_sse(parsed_port)
    else:
        mcp.run()


if __name__ == "__main__":
    main()
