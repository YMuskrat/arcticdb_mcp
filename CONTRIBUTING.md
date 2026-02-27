# Contributing to arcticdb-mcp

Contributions are welcome — bug fixes, new tools, documentation improvements, and backend-specific testing are all valuable.

## Setup

```bash
git clone https://github.com/YMuskrat/arcticdb-mcp
cd arcticdb-mcp
pip install -e .
```

Test your changes with the MCP Inspector:

```bash
ARCTICDB_URI=lmdb:///tmp/test_db npx @modelcontextprotocol/inspector python -m arcticdb_mcp
```

## Adding a new tool

The pattern is intentionally simple. Pick the right file under `tools/` (or create a new one for a new category), add a function with the `@register_tool` decorator:

```python
@register_tool("your_tool_name")
def your_tool_name(library: str, symbol: str):
    """
    Clear description of what this tool does.
    This is what the AI reads to decide when to call it — make it specific.
    """
    result = get_ac()[library].some_arcticdb_method(symbol)
    return result
```

Rules:
- No `**kwargs` — FastMCP needs explicit typed parameters to build the tool schema
- Every tool must have a docstring
- Return JSON-serialisable values (dicts, lists, strings, numbers, bools)
- Use `get_ac()` for the connection — never instantiate `Arctic` directly

If you add a new file under `tools/`, import it in `tools/__init__.py`:

```python
from . import your_new_module
```

## Submitting a PR

1. Fork the repo and create a branch from `main`
2. Make your changes
3. Verify all existing tools still appear correctly in the Inspector
4. Open a PR with a clear description of what you added and why

## Reporting bugs

Use the bug report issue template. Include the ArcticDB backend you are using (LMDB, S3, Azure), your OS, and the full error message.

## Suggesting new tools

Open a feature request issue. Check the [ArcticDB Library API](https://docs.arcticdb.io/latest/api/library/) first — if the method exists there, it can likely become a tool.
