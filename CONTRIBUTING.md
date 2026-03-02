# Contributing to arcticdb-mcp

Thanks for contributing.

## Setup

```bash
git clone https://github.com/YMuskrat/arcticdb-mcp
cd arcticdb-mcp
pip install -e .
```

Run server locally:

```bash
ARCTICDB_URI=lmdb:///tmp/test_db python -m arcticdb_mcp
```

Open MCP Inspector:

```bash
ARCTICDB_URI=lmdb:///tmp/test_db npx @modelcontextprotocol/inspector python -m arcticdb_mcp
```

## Project Rules

- Tool modules in `arcticdb_mcp/tools/` should contain tool functions only.
- Helper logic should live in `arcticdb_mcp/utils/`.
- Use `@register_tool("tool_name")` for every new tool.
- Use explicit typed parameters (avoid dynamic `**kwargs` schemas).
- Return JSON-serializable responses only.
- Reuse `get_ac()` from `connection.py` (do not instantiate `Arctic` directly inside tools).

## Adding a New Tool

1. Pick the right file under `arcticdb_mcp/tools/`.
2. Implement a focused tool function with a clear docstring.
3. Move parsing/transformation helpers to `arcticdb_mcp/utils/`.
4. If you add a new tools module, import it in `arcticdb_mcp/tools/__init__.py`.
5. Validate in MCP Inspector before opening the PR.

Example:

```python
@register_tool("your_tool_name")
def your_tool_name(library: str, symbol: str):
    """Describe exactly what this tool does and when to use it."""
    lib = get_ac()[library]
    return lib.list_symbols() if symbol == "*" else lib.read(symbol).data.to_dict(orient="records")
```

## Community Contribution Backlog

The following ArcticDB capabilities are not implemented as MCP tools yet and are open for community contributions.

| Proposed MCP Tool | ArcticDB API | Suggested Module | Scope |
|---|---|---|---|
| `stage` | `Library.stage` | `arcticdb_mcp/tools/batch_tools.py` | Stage one or more payloads without finalizing versions. |
| `finalize_staged_data` | `Library.finalize_staged_data` | `arcticdb_mcp/tools/batch_tools.py` | Finalize previously staged payloads for one symbol. |
| `sort_and_finalize_staged_data` | `Library.sort_and_finalize_staged_data` | `arcticdb_mcp/tools/batch_tools.py` | Sort staged rows by index, then finalize safely. |
| `delete_staged_data` | `Library.delete_staged_data` | `arcticdb_mcp/tools/batch_tools.py` | Delete staged (not yet finalized) data for a symbol. |
| `get_staged_symbols` | `Library.get_staged_symbols` | `arcticdb_mcp/tools/batch_tools.py` | List symbols that currently have staged data. |
| `read_batch_and_join` | `Library.read_batch_and_join` | `arcticdb_mcp/tools/batch_tools.py` | Join/query across multiple symbols in one server-side read. |
| `admin_tools` | `Library.admin_tools` | `arcticdb_mcp/tools/maintenance_tools.py` | Expose safe, explicit admin operations with strict validation. |

If you pick one, open an issue first so work does not overlap.

## PR Checklist

- Keep behavior backward compatible unless change is intentional and documented.
- Add or update docs (`README.md`, docstrings) as needed.
- Confirm tools load and run in MCP Inspector.
- Include a concise PR description with scope and test notes.

## Reporting Bugs

Please include:

- ArcticDB backend (`LMDB`, `S3`, `Azure`, etc.)
- OS and Python version
- Full error message and stack trace
- Minimal reproduction steps
