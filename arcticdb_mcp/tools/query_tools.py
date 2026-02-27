import pandas as pd
from arcticdb import QueryBuilder

from ..registry import register_tool
from ..connection import get_ac


@register_tool("query_filter")
def query_filter(library: str, symbol: str, filters: list):
    """
    Filter rows using conditions.
    filters: list of dicts, e.g.
    [{"column": "price", "op": ">", "value": 100},
     {"column": "volume", "op": "<", "value": 5000}]
    Supported ops: >, >=, <, <=, ==, !=
    """
    q = QueryBuilder()
    ops = {
        ">": lambda col, val: col > val,
        ">=": lambda col, val: col >= val,
        "<": lambda col, val: col < val,
        "<=": lambda col, val: col <= val,
        "==": lambda col, val: col == val,
        "!=": lambda col, val: col != val,
    }
    expression = None
    for f in filters:
        col = q[f["column"]]
        op = f["op"]
        val = f["value"]
        if op not in ops:
            raise ValueError(
                f"Unsupported operator '{op}'. Use one of {list(ops.keys())}"
            )
        condition = ops[op](col, val)
        expression = condition if expression is None else (expression & condition)

    q = q[expression]
    result = get_ac()[library].read(symbol, query_builder=q)
    return result.data.to_dict(orient="records")


@register_tool("query_filter_isin")
def query_filter_isin(library: str, symbol: str, column: str, values: list):
    """
    Filter rows where column value is in a list.
    e.g. column="status", values=["active", "pending"]
    """
    q = QueryBuilder()
    q = q[q[column].isin(values)]
    result = get_ac()[library].read(symbol, query_builder=q)
    return result.data.to_dict(orient="records")


@register_tool("query_groupby")
def query_groupby(library: str, symbol: str, groupby_column: str, aggregations: dict):
    """
    Group by a column and aggregate.
    aggregations: e.g. {"price": "mean", "volume": "sum"}
    Supported agg ops: mean, sum, min, max, count
    """
    q = QueryBuilder()
    q = q.groupby(groupby_column).agg(aggregations)
    result = get_ac()[library].read(symbol, query_builder=q)
    return result.data.to_dict(orient="records")


@register_tool("query_date_range")
def query_date_range(library: str, symbol: str, start: str, end: str):
    """
    Filter rows by date range on a datetime-indexed symbol.
    start/end: ISO format strings e.g. "2024-01-01"
    """
    result = get_ac()[library].read(
        symbol,
        date_range=(pd.Timestamp(start), pd.Timestamp(end)),
    )
    return result.data.to_dict(orient="records")


@register_tool("query_resample")
def query_resample(library: str, symbol: str, rule: str, aggregations: dict):
    """
    Resample a datetime-indexed symbol and aggregate.
    rule: pandas offset string e.g. "1h", "1D", "1W"
    aggregations: e.g. {"price": "mean", "volume": "sum"}
    Supported agg ops: mean, sum, min, max, count, first, last
    """
    q = QueryBuilder()
    q = q.resample(rule).agg(aggregations)
    result = get_ac()[library].read(symbol, query_builder=q)
    return result.data.to_dict(orient="records")
