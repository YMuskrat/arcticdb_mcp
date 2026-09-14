import pandas as pd
import pytest

from arcticdb_mcp.utils.batch_payloads import build_write_payload


def test_build_write_payload_requires_a_requested_index_column() -> None:
    with pytest.raises(ValueError, match="index_column 'date' is missing"):
        build_write_payload(
            {"symbol": "prices", "data": [{"price": 10}], "index_column": "date"}
        )


def test_build_write_payload_rejects_invalid_requested_index_values() -> None:
    with pytest.raises(ValueError, match="contains invalid datetime values"):
        build_write_payload(
            {
                "symbol": "prices",
                "data": [{"date": "not-a-date", "price": 10}],
                "index_column": "date",
            }
        )


def test_build_write_payload_converts_a_requested_index_column() -> None:
    payload = build_write_payload(
        {
            "symbol": "prices",
            "data": [{"date": "2024-01-01", "price": 10}],
            "index_column": "date",
        }
    )

    assert isinstance(payload.data.index, pd.DatetimeIndex)
    assert payload.data.index.name == "date"
    assert payload.data.iloc[0]["price"] == 10
