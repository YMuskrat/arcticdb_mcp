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

## Quickstart

**1. Install**

```bash
pip install arcticdb-mcp
```

**2. Add to your MCP client config**

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

> **Windows users:** use two slashes with the drive letter — `lmdb://C:/path/to/your/database`

**3. Connect and start asking questions**

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
