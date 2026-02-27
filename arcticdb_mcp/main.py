import os
import sys
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


def main():
    port = os.getenv("ARCTICDB_MCP_PORT")
    if port:
        mcp.run(host="0.0.0.0", port=int(port))
    else:
        mcp.run()


if __name__ == "__main__":
    main()
