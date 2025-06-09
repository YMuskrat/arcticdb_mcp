import pandas as pd

from arcticdb_mcp.tools.symbol_tools import _df_to_records


def test_df_to_records_preserves_a_colliding_index_and_column() -> None:
    frame = pd.DataFrame(
        {"date": ["source-value"], "price": [10]},
        index=pd.DatetimeIndex(["2024-01-01"], name="date"),
    )

    assert _df_to_records(frame) == [
        {
            "date_index": "2024-01-01 00:00:00",
            "date": "source-value",
            "price": 10,
        }
    ]


def test_df_to_records_names_an_unnamed_index_that_collides() -> None:
    frame = pd.DataFrame(
        {"index": ["source-value"], "price": [10]},
        index=pd.Index([7]),
    )

    assert _df_to_records(frame) == [
        {"index_index": 7, "index": "source-value", "price": 10}
    ]
