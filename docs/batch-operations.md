# Batch tool arguments

Select the named tool in MCP Inspector and supply the JSON object shown.
Use an existing disposable library named `batch_examples` for the write example;
the call creates new versions of the named symbols if they already exist.

## Write two time series

Select `write_batch`:

```json
{
  "library": "batch_examples",
  "payloads": [
    {
      "symbol": "sample_a",
      "index_column": "date",
      "data": [{"date": "2026-01-01", "price": 10.0}],
      "metadata": {"source": "synthetic"}
    },
    {
      "symbol": "sample_b",
      "index_column": "date",
      "data": [{"date": "2026-01-01", "price": 20.0}]
    }
  ]
}
```

For time-series batch writes, specify `index_column` explicitly. Unlike
`write_symbol`, the batch-write helper does not infer it from common column
names. A supplied column must exist and contain valid datetime values.
Without `index_column`, row-list input retains its default dataframe index.

## Read selected columns and rows

Select `read_batch`:

```json
{
  "library": "batch_examples",
  "symbols": [
    {"symbol": "sample_a", "columns": ["price"], "row_range": [0, 1]},
    "sample_b"
  ]
}
```

The `symbols` list accepts both symbol strings and request objects. Request
objects can specify `as_of`, `date_range`, `row_range`, `columns`, and
`output_format`. This tool currently rejects `lazy: true`.

## Know the top-level parameter names

| Tool | List parameter | Required fields per object |
|---|---|---|
| `write_batch` | `payloads` | `symbol`, `data` |
| `append_batch` | `append_payloads` | `symbol`, `data` |
| `update_batch` | `update_payloads` | `symbol`, `data` |
| `write_metadata_batch` | `write_metadata_payloads` | `symbol`, `metadata` |
| `read_batch` | `symbols` | `symbol`, or a symbol string |

An append must be compatible with the existing symbol's schema and index.
An update requires datetime-indexed data; it changes a date range rather than
performing an arbitrary row-key merge. Check the tool docstring before using
optional pruning or upsert parameters.

## Inspect each returned entry

Batch tools serialize results separately. A backend data-error entry has
`error: true` and diagnostic fields such as `symbol`, `error_code`, and
`exception_string`. Input validation or a backend failure can also raise for
the whole call. Do not treat receipt of a response as proof that every item
succeeded, or assume that the batch is an all-or-nothing transaction.

Record the successful symbols before deciding what to retry. Repeating a
successful write or append can create another version or duplicate an append.
The tools do not implement automatic retries or rollback across symbols.
