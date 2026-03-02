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

from .registry import TOOL_REGISTRY

mcp = FastMCP("arcticdb-mcp")

# Import tool modules to trigger @register_tool side-effects
from . import tools as _tools  # noqa: F401

for name, func in TOOL_REGISTRY.items():
    mcp.tool(name=name)(func)


def _run_http_sse(port: int):
    """
    Run FastMCP in HTTP/SSE mode.
    FastMCP 3.x requires transport="sse"; older versions accepted host/port directly.
    """
    run_sig = inspect.signature(type(mcp).run)
    if "transport" in run_sig.parameters:
        mcp.run(transport="sse", host="0.0.0.0", port=port)
    else:
        mcp.run(host="0.0.0.0", port=port)


def main():
    port = os.getenv("ARCTICDB_MCP_PORT")
    if port:
        _run_http_sse(int(port))
    else:
        mcp.run()


if __name__ == "__main__":
    main()
