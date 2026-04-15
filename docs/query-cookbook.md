# Query cookbook

These are tool argument objects to paste into MCP Inspector after selecting
the named tool. They assume a library named `finance` and an existing symbol
named `prices` with a datetime index and columns `price`, `volume`, and `venue`.
Use your own library, symbol, and column names. These examples do not create data.

## Check the schema first

Select `get_symbol_info`:

```json
{"library": "finance", "symbol": "prices"}
```

Use `head_symbol` to inspect a small sample before choosing filters:

```json
{"library": "finance", "symbol": "prices", "n": 5}
```

## Combine comparisons

Select `query_filter`:

```json
{
  "library": "finance",
  "symbol": "prices",
  "filters": [
    {"column": "price", "op": ">", "value": 100},
    {"column": "volume", "op": ">=", "value": 1000}
  ]
}
```

Conditions are combined with AND: a row must satisfy both comparisons.
Supported operators are `>`, `>=`, `<`, `<=`, `==`, and `!=`. The list must
contain at least one condition. Use JSON numbers for numeric comparisons.
This tool does not accept an arbitrary Python expression or an OR expression.

## Match one of several values

Select `query_filter_isin`:

```json
{"library": "finance", "symbol": "prices", "column": "venue", "values": ["XNAS", "XNYS"]}
```

## Select a time interval

Select `query_date_range` on a datetime-indexed symbol:

```json
{"library": "finance", "symbol": "prices", "start": "2026-01-01T00:00:00", "end": "2026-01-02T00:00:00"}
```

Match the timezone convention of the stored index. This operation uses the
index; it does not filter an ordinary string column that happens to contain dates.

## Aggregate by a column or time bucket

Select `query_groupby` to summarize by venue:

```json
{"library": "finance", "symbol": "prices", "groupby_column": "venue", "aggregations": {"price": "mean", "volume": "sum"}}
```

Select `query_resample` to summarize a datetime-indexed symbol by hour:

```json
{"library": "finance", "symbol": "prices", "rule": "1h", "aggregations": {"price": "mean", "volume": "sum"}}
```

Each example is a separate backend read. The tools do not automatically pass
the result of one query into the next. Query results are returned as row
records with the index included, and these tools currently have no result-size
limit parameter. Start with a small symbol when exploring a new query.
