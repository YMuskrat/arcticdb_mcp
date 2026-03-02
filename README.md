# arcticdb-mcp

[![PyPI](https://img.shields.io/pypi/v/arcticdb-mcp.svg)](https://pypi.org/project/arcticdb-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/arcticdb-mcp.svg)](https://pypi.org/project/arcticdb-mcp/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

`arcticdb-mcp` is an MCP server that gives AI assistants structured read/write access to [ArcticDB](https://github.com/man-group/ArcticDB).

It is built for assistant-driven data workflows on versioned DataFrame data: symbol reads/writes, snapshots, metadata, query operations, and batch operations.

## Table of Contents

- [Quickstart](#quickstart)
- [Demo Video](#demo-video)
- [Installation](#installation)
- [Configuration](#configuration)
- [Run Modes](#run-modes)
- [Tools](#tools)
- [Example Prompts](#example-prompts)
- [Development](#development)
- [Community Backlog](#community-backlog)
- [Contributing](#contributing)
- [License](#license)

## Quickstart

1. Install and run with `uvx` (recommended):

```bash
uvx arcticdb-mcp
```

2. Configure your MCP client (Claude Desktop / Cursor / Windsurf / Continue):

```json
{
  "mcpServers": {
    "arcticdb": {
      "command": "uvx",
      "args": ["arcticdb-mcp"],
      "env": {
        "ARCTICDB_URI": "lmdb:///path/to/your/database"
      }
    }
  }
}
```

3. Ask your assistant:

- "Show me the last 5 rows of AAPL in library finance"
- "Create a snapshot of finance before I update symbols"
- "List versions for symbol ES_intraday"

## Demo Video

Watch the live `watch db` demo:

<p align="center">
  <a href="demo/media/arcticdb-live-demo.mp4">
    <img src="demo/media/arcticdb-live-demo-preview.gif" alt="ArcticDB live demo preview" width="100%" />
  </a>
</p>

Click the preview to open the full video:
[`demo/media/arcticdb-live-demo.mp4`](demo/media/arcticdb-live-demo.mp4)

## Installation

Choose one:

```bash
# Recommended
uvx arcticdb-mcp

# Or
pipx install arcticdb-mcp

# Or
pip install arcticdb-mcp
```

Python requirement: `>=3.9`

## Configuration

Set `ARCTICDB_URI` in MCP client config or environment.

### URI examples

- Local LMDB (Linux/macOS): `lmdb:///path/to/db`
- Local LMDB (Windows): `lmdb://C:/path/to/db`
- AWS S3: `s3://s3.amazonaws.com:bucket?region=us-east-1&access=KEY&secret=SECRET`
- Azure Blob: `azure://AccountName=X;AccountKey=Y;Container=Z`
- S3-compatible (MinIO, etc.): `s3://your-endpoint:bucket?access=KEY&secret=SECRET`

You can also use a `.env` file:

```env
ARCTICDB_URI=lmdb:///path/to/db
```

## Run Modes

### stdio (default)

This is the default mode used by desktop MCP clients.

```bash
ARCTICDB_URI=lmdb:///path/to/db python -m arcticdb_mcp
```

### HTTP / SSE

Set `ARCTICDB_MCP_PORT` to run over HTTP/SSE:

```bash
ARCTICDB_URI=lmdb:///path/to/db ARCTICDB_MCP_PORT=8000 python -m arcticdb_mcp
```

Endpoint:

```text
http://localhost:8000/sse
```

## Tools

Current server exposes 47 tools.

### Arctic and Libraries

- `get_uri`
- `list_libraries`
- `create_library`
- `delete_library`
- `library_exists`
- `get_library`
- `modify_library_option`
- `get_library_options`
- `get_enterprise_options`

### Symbols

- `list_symbols`
- `symbol_exists`
- `read_symbol`
- `head_symbol`
- `tail_symbol`
- `write_symbol`
- `append_symbol`
- `update_symbol`
- `delete_symbol`
- `delete_data_in_range`
- `get_symbol_info`
- `list_versions`
- `read_metadata`
- `write_metadata`

### Batch Operations

- `write_batch`
- `append_batch`
- `update_batch`
- `delete_batch`
- `read_batch`
- `read_metadata_batch`
- `get_description_batch`
- `write_metadata_batch`
- `write_pickle`
- `write_pickle_batch`

### Snapshots

- `create_snapshot`
- `list_snapshots`
- `delete_snapshot`
- `read_symbol_from_snapshot`

### Query Helpers

- `query_filter`
- `query_filter_isin`
- `query_groupby`
- `query_date_range`
- `query_resample`

### Maintenance

- `reload_symbol_list`
- `compact_symbol_list`
- `is_symbol_fragmented`
- `defragment_symbol_data`
- `prune_previous_versions`

## Example Prompts

- "Read symbol NVDA from library finance"
- "Filter NVDA where price > 500 and volume >= 1000"
- "Resample ES_intraday to 5min and aggregate price mean, volume sum"
- "Write metadata owner=research to symbol ES_intraday"
- "Delete data in range for ES_intraday from 2024-01-01 to 2024-01-05"

## Development

```bash
git clone https://github.com/YMuskrat/arcticdb-mcp
cd arcticdb-mcp
pip install -e .
```

Run locally:

```bash
ARCTICDB_URI=lmdb:///path/to/db python -m arcticdb_mcp
```

Test with MCP Inspector:

```bash
ARCTICDB_URI=lmdb:///tmp/test_db npx @modelcontextprotocol/inspector python -m arcticdb_mcp
```

## Community Backlog

These ArcticDB capabilities are intentionally left open for contributors:

- `stage`
- `finalize_staged_data`
- `sort_and_finalize_staged_data`
- `delete_staged_data`
- `get_staged_symbols`
- `read_batch_and_join`
- `admin_tools`

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT
