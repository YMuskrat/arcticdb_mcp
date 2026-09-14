import json

import numpy as np
import pandas as pd

from arcticdb_mcp.utils.serialization import normalize_value


def test_dataframe_values_are_json_serializable() -> None:
    frame = pd.DataFrame(
        {"price": np.array([10], dtype=np.int64), "ratio": [float("nan")]},
        index=pd.DatetimeIndex(["2024-01-01"], name="date"),
    )

    records = normalize_value(frame)

    assert records == [{"date": "2024-01-01 00:00:00", "price": 10, "ratio": None}]
    json.dumps(records, allow_nan=False)


def test_series_values_are_normalized_recursively() -> None:
    series = pd.Series([pd.Timestamp("2024-01-01"), np.int64(2)])

    assert normalize_value(series) == {
        "0": "2024-01-01 00:00:00",
        "1": 2,
    }
