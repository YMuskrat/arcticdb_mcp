# arcticdb-mcp

MCP server that gives AI assistants full read/write access to [ArcticDB](https://github.com/man-group/ArcticDB) — versioned, queryable, serverless DataFrames at scale.

<!-- GIF DEMO HERE -->

---

## Why ArcticDB + AI

Most databases give your AI assistant data. ArcticDB gives it **versioned** data — every write is a new version, every version is recoverable. This means your AI can:

- Detect when a new data update introduced anomalies by comparing it to the previous version
- Roll back to a known-good state without any data loss
- Query billions of rows with date range, filter, and groupby — without loading them into memory
- Work across LMDB (local), S3, Azure Blob, and MinIO with zero infrastructure changes

---

## Configure Your AI Assistant

We provide full instructions for configuring arcticdb-mcp with Claude Desktop. Many MCP clients use a similar configuration file — you can adapt these steps to work with the client of your choice.

> **Cursor / Windsurf / Continue.dev** — these all use the same JSON config format as Claude Desktop. Use any of the blocks below as-is.

> **n8n / HTTP-based tools** — see [HTTP / SSE mode](#http--sse-mode-n8n-and-other-tools) below.

---

### Claude Desktop configuration file location

| OS | Path |
|----|------|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

You can also use the **Settings** menu in Claude Desktop to locate the file.

Edit the `mcpServers` section using one of the methods below.

---

### If you are using uvx *(recommended)*

No install step needed — `uvx` fetches and runs arcticdb-mcp directly from PyPI.

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

---

### If you are using uv

```json
{
  "mcpServers": {
    "arcticdb": {
      "command": "uv",
      "args": ["run", "arcticdb-mcp"],
      "env": {
        "ARCTICDB_URI": "lmdb:///path/to/your/database"
      }
    }
  }
}
```

---

### If you are using pipx

```bash
pipx install arcticdb-mcp
```

```json
{
  "mcpServers": {
    "arcticdb": {
      "command": "arcticdb-mcp",
      "env": {
        "ARCTICDB_URI": "lmdb:///path/to/your/database"
      }
    }
  }
}
```

---

### If you are using pip

```bash
pip install arcticdb-mcp
```

```json
{
  "mcpServers": {
    "arcticdb": {
      "command": "python",
      "args": ["-m", "arcticdb_mcp"],
      "env": {
        "ARCTICDB_URI": "lmdb:///path/to/your/database"
      }
    }
  }
}
```

---

### If you are using Docker

**Local LMDB** — mount your database directory as a volume:

```json
{
  "mcpServers": {
    "arcticdb": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-e", "ARCTICDB_URI=lmdb:///data/db",
        "-v", "/path/to/your/database:/data/db",
        "ymuskrat/arcticdb-mcp"
      ]
    }
  }
}
```

**S3 / Azure** — no volume needed, pass credentials via env:

```json
{
  "mcpServers": {
    "arcticdb": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "ymuskrat/arcticdb-mcp"],
      "env": {
        "ARCTICDB_URI": "s3://s3.amazonaws.com:bucket?region=us-east-1&access=KEY&secret=SECRET"
      }
    }
  }
}
```

Build the image locally:

```bash
docker build -t arcticdb-mcp .
```

---

### ArcticDB URI

Replace `lmdb:///path/to/your/database` with your ArcticDB connection URI:

| Backend | URI format |
|---------|-----------|
| Local (LMDB) | `lmdb:///path/to/db` (Linux/Mac) · `lmdb://C:/path/to/db` (Windows) |
| AWS S3 | `s3://s3.amazonaws.com:bucket?region=us-east-1&access=KEY&secret=SECRET` |
| Azure Blob | `azure://AccountName=X;AccountKey=Y;Container=Z` |
| MinIO / S3-compatible | `s3://your-endpoint:bucket?access=KEY&secret=SECRET` |

You can also set the URI in a `.env` file in your working directory instead of the config.

---

**Then ask your AI assistant:**

```
"Show me the last 5 rows of AAPL in the finance library"
"Filter NVDA prices greater than 500 in 2024"
"Compare the latest version of this symbol to the previous one"
"Create a snapshot of the finance library before I update it"
```

---

## Backends

| Backend | URI format |
|---------|-----------|
| Local (LMDB) | `lmdb:///path/to/db` (Linux/Mac) · `lmdb://C:/path/to/db` (Windows) |
| AWS S3 | `s3://s3.amazonaws.com:bucket?region=us-east-1&access=KEY&secret=SECRET` |
| Azure Blob | `azure://AccountName=X;AccountKey=Y;Container=Z` |
| MinIO / S3-compatible | `s3://your-endpoint:bucket?access=KEY&secret=SECRET` |

Set the URI via environment variable:

```bash
export ARCTICDB_URI="lmdb:///path/to/your/database"
```

Or use a `.env` file in your working directory.

---

## Tools

### Libraries
| Tool | Description |
|------|-------------|
| `list_libraries` | List all libraries in the Arctic instance |
| `create_library` | Create a new library |
| `delete_library` | Delete a library and all its data |
| `library_exists` | Check whether a library exists |
| `get_library` | Get a library's name and symbol list |

### Symbols
| Tool | Description |
|------|-------------|
| `list_symbols` | List all symbols in a library |
| `read_symbol` | Read a symbol's full data. Use `as_of` for a specific version |
| `head_symbol` | Read the first n rows of a symbol |
| `tail_symbol` | Read the last n rows of a symbol |
| `write_symbol` | Write data to a symbol, creating a new version |
| `append_symbol` | Append rows to an existing symbol |
| `update_symbol` | Overwrite a date range of a timeseries symbol |
| `delete_symbol` | Delete a symbol and all its versions |
| `delete_data_in_range` | Delete rows within a date range, creating a new version |
| `symbol_exists` | Check whether a symbol exists |
| `get_symbol_info` | Get row count, column names, and last update time |
| `read_metadata` | Read a symbol's metadata without loading data |
| `write_metadata` | Update a symbol's metadata |
| `list_versions` | List all versions of a symbol with timestamps |

### Snapshots
| Tool | Description |
|------|-------------|
| `create_snapshot` | Snapshot the current state of a library |
| `list_snapshots` | List all snapshots in a library |
| `delete_snapshot` | Delete a named snapshot |
| `read_symbol_from_snapshot` | Read a symbol as it existed at snapshot time |

### Queries
| Tool | Description |
|------|-------------|
| `query_filter` | Filter rows with `>`, `>=`, `<`, `<=`, `==`, `!=` conditions |
| `query_filter_isin` | Filter rows where a column value is in a list |
| `query_groupby` | Group by a column and aggregate (mean, sum, min, max, count) |
| `query_date_range` | Filter a datetime-indexed symbol by date range |
| `query_resample` | Resample a datetime-indexed symbol (1h, 1D, 1W, ...) |

---

## HTTP / SSE mode (n8n and other tools)

Tools like n8n, Zapier, or any custom application that can't launch a local process need the server running as an HTTP service. Set `ARCTICDB_MCP_PORT` to switch from stdio to SSE transport:

```bash
ARCTICDB_URI=lmdb:///path/to/your/database ARCTICDB_MCP_PORT=8000 python -m arcticdb_mcp
```

The MCP endpoint will be available at:

```
http://localhost:8000/sse
```

**With Docker:**

```bash
docker run -d \
  -e ARCTICDB_URI=lmdb:///data/db \
  -e ARCTICDB_MCP_PORT=8000 \
  -v /path/to/your/database:/data/db \
  -p 8000:8000 \
  ymuskrat/arcticdb-mcp
```

**In n8n** — add an MCP Client node and point it to `http://your-host:8000/sse`.

---

## Development

```bash
git clone https://github.com/YMuskrat/arcticdb-mcp
pip install -e ".[dev]"

# Test with MCP Inspector
ARCTICDB_URI=lmdb:///tmp/test_db npx @modelcontextprotocol/inspector python -m arcticdb_mcp
```

---

## License

MIT
