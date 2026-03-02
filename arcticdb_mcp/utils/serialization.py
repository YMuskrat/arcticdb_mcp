from __future__ import annotations

from typing import Any

import pandas as pd


def normalize_value(value: Any) -> Any:
    """Convert ArcticDB/Pandas values to JSON-serializable Python values."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, pd.DataFrame):
        return value.reset_index().to_dict(orient="records")

    if isinstance(value, pd.Series):
        return value.to_dict()

    if isinstance(value, (pd.Timestamp, pd.Timedelta)):
        return str(value)

    if isinstance(value, dict):
        return {str(k): normalize_value(v) for k, v in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [normalize_value(v) for v in value]

    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass

    return str(value)


def serialize_versioned_item(item: Any, include_data: bool = False) -> dict:
    result = {
        "symbol": getattr(item, "symbol", None),
        "library": getattr(item, "library", None),
        "version": getattr(item, "version", None),
        "metadata": normalize_value(getattr(item, "metadata", None)),
        "timestamp": str(getattr(item, "timestamp", None)),
    }

    if include_data:
        result["data"] = normalize_value(getattr(item, "data", None))

    return result


def serialize_data_error(error: Any) -> dict:
    return {
        "error": True,
        "symbol": getattr(error, "symbol", None),
        "error_code": getattr(error, "error_code", None),
        "error_category": str(getattr(error, "error_category", None)),
        "exception_string": getattr(error, "exception_string", None),
        "version_request_type": str(getattr(error, "version_request_type", None)),
        "version_request_data": normalize_value(
            getattr(error, "version_request_data", None)
        ),
    }


def serialize_symbol_description(description: Any) -> dict:
    columns = []
    for column in getattr(description, "columns", ()):
        name = getattr(column, "name", None)
        if name is not None:
            columns.append(name)

    index = []
    for column in getattr(description, "index", ()):
        index.append(getattr(column, "name", None))

    date_range = None
    raw_date_range = getattr(description, "date_range", None)
    if raw_date_range and len(raw_date_range) == 2:
        start, end = raw_date_range
        if not (pd.isna(start) or pd.isna(end)):
            date_range = [str(start), str(end)]

    return {
        "columns": columns,
        "index": index,
        "index_type": getattr(description, "index_type", None),
        "row_count": getattr(description, "row_count", None),
        "last_update_time": str(getattr(description, "last_update_time", None)),
        "date_range": date_range,
        "sorted": str(getattr(description, "sorted", None)),
    }


def serialize_batch_entry(entry: Any, include_data: bool = False) -> Any:
    if entry is None:
        return {"ok": True}

    if hasattr(entry, "error_code") and hasattr(entry, "exception_string"):
        return serialize_data_error(entry)

    if (
        hasattr(entry, "symbol")
        and hasattr(entry, "version")
        and hasattr(entry, "timestamp")
    ):
        return serialize_versioned_item(entry, include_data=include_data)

    if hasattr(entry, "row_count") and hasattr(entry, "columns"):
        return serialize_symbol_description(entry)

    return normalize_value(entry)

