from typing import Iterable

import pandas as pd

UPDATE_INDEX_COLUMN_CANDIDATES: Iterable[str] = (
    "index",
    "timestamp",
    "ts",
    "datetime",
    "date",
    "time",
)


def rows_to_timeseries_update_frame(data: list) -> pd.DataFrame:
    """Build a datetime-indexed frame for ArcticDB update operations."""
    df = pd.DataFrame(data)
    if df.empty:
        raise ValueError("data must contain at least one row.")

    if isinstance(df.index, pd.DatetimeIndex):
        return df.sort_index()

    for column in UPDATE_INDEX_COLUMN_CANDIDATES:
        if column not in df.columns:
            continue

        index = pd.to_datetime(df[column], errors="coerce")
        if index.isna().any():
            raise ValueError(
                f"Column '{column}' contains invalid datetime values. "
                "Use ISO 8601 strings, for example 2024-01-01T09:30:00Z."
            )

        df = df.drop(columns=[column]).copy()
        df.index = index
        df.index.name = column
        return df.sort_index()

    allowed = ", ".join(UPDATE_INDEX_COLUMN_CANDIDATES)
    raise ValueError(
        "update_symbol requires datetime-indexed rows. "
        f"Include one index column in data: {allowed}."
    )

