from __future__ import annotations

from typing import Any

import pandas as pd
from arcticdb.version_store.library import (
    DeleteRequest,
    ReadInfoRequest,
    ReadRequest,
    UpdatePayload,
    WritePayload,
)

from .timeseries import rows_to_timeseries_update_frame


def parse_date_range(date_range):
    if date_range is None:
        return None
    if not isinstance(date_range, (list, tuple)) or len(date_range) != 2:
        raise ValueError("date_range must be a 2-item list/tuple: [start, end].")

    start = pd.Timestamp(date_range[0]) if date_range[0] is not None else None
    end = pd.Timestamp(date_range[1]) if date_range[1] is not None else None
    return (start, end)


def parse_row_range(row_range):
    if row_range is None:
        return None
    if not isinstance(row_range, (list, tuple)) or len(row_range) != 2:
        raise ValueError("row_range must be a 2-item list/tuple: [start, end].")
    return (row_range[0], row_range[1])


def to_dataframe(data):
    if isinstance(data, pd.DataFrame):
        return data
    if isinstance(data, (list, dict)):
        return pd.DataFrame(data)
    raise ValueError(
        "data must be a table-like object (list of row dicts or dict of arrays)."
    )


def build_write_payload(payload: dict, for_pickle: bool = False) -> WritePayload:
    if "symbol" not in payload:
        raise ValueError("Each payload must include 'symbol'.")
    if "data" not in payload:
        raise ValueError("Each payload must include 'data'.")

    symbol = payload["symbol"]
    data = payload["data"] if for_pickle else to_dataframe(payload["data"])
    metadata = payload.get("metadata")
    index_column = payload.get("index_column")

    if (
        not for_pickle
        and index_column
        and isinstance(data, pd.DataFrame)
        and index_column in data.columns
    ):
        data = data.copy()
        converted = pd.to_datetime(data[index_column], errors="coerce")
        if not converted.isna().any():
            data[index_column] = converted
        data = data.set_index(index_column)

    # Index is set explicitly above when index_column is provided.
    return WritePayload(symbol, data, metadata=metadata, index_column=None)


def build_update_payload(lib, payload: dict) -> UpdatePayload:
    if "symbol" not in payload:
        raise ValueError("Each update payload must include 'symbol'.")
    if "data" not in payload:
        raise ValueError("Each update payload must include 'data'.")

    symbol = payload["symbol"]
    metadata = payload.get("metadata")
    index_column = payload.get("index_column")
    date_range = parse_date_range(payload.get("date_range"))
    data = payload["data"]

    if index_column:
        df = to_dataframe(data)
        if index_column not in df.columns:
            raise ValueError(f"index_column '{index_column}' is missing from data.")
        index = pd.to_datetime(df[index_column], errors="coerce")
        if index.isna().any():
            raise ValueError(
                f"index_column '{index_column}' contains invalid datetime values."
            )
        df = df.drop(columns=[index_column]).copy()
        df.index = index
        df.index.name = index_column
    elif isinstance(data, pd.DataFrame):
        df = data
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("update_batch requires a datetime index.")
    else:
        df = rows_to_timeseries_update_frame(data)

    # Align index naming with existing symbol descriptor to avoid update mismatch.
    if lib.has_symbol(symbol):
        desc = lib.get_description(symbol)
        expected_index_name = desc.index[0].name if desc.index else None
        df.index.name = expected_index_name or "index"

    return UpdatePayload(symbol=symbol, data=df, metadata=metadata, date_range=date_range)


def build_read_request(entry: Any):
    if isinstance(entry, str):
        return entry
    if not isinstance(entry, dict):
        raise ValueError("Each read request must be a symbol string or request dict.")
    if "symbol" not in entry:
        raise ValueError("Each read request dict must include 'symbol'.")

    return ReadRequest(
        symbol=entry["symbol"],
        as_of=entry.get("as_of"),
        date_range=parse_date_range(entry.get("date_range")),
        row_range=parse_row_range(entry.get("row_range")),
        columns=entry.get("columns"),
        output_format=entry.get("output_format"),
    )


def build_read_info_request(entry: Any):
    if isinstance(entry, str):
        return entry
    if not isinstance(entry, dict):
        raise ValueError(
            "Each info request must be a symbol string or request dict with symbol/as_of."
        )
    if "symbol" not in entry:
        raise ValueError("Each info request dict must include 'symbol'.")
    return ReadInfoRequest(symbol=entry["symbol"], as_of=entry.get("as_of"))


def build_delete_request(entry: Any):
    if isinstance(entry, str):
        return entry
    if not isinstance(entry, dict):
        raise ValueError("Each delete request must be a symbol string or request dict.")
    if "symbol" not in entry:
        raise ValueError("Each delete request dict must include 'symbol'.")

    version_ids = entry.get("version_ids")
    if version_ids is None:
        return entry["symbol"]
    if not isinstance(version_ids, list):
        raise ValueError("version_ids must be a list of integers.")
    return DeleteRequest(symbol=entry["symbol"], version_ids=version_ids)

