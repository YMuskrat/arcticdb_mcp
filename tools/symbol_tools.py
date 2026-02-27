import pandas as pd
from typing import Optional

from ..registry import register_tool
from ..connection import get_ac


@register_tool("list_symbols")
def list_symbols(library: str):
    """List all symbol names stored in the given library."""
    return get_ac()[library].list_symbols()


@register_tool("read_symbol")
def read_symbol(library: str, symbol: str, as_of: Optional[int] = None):
    """
    Read a symbol's full data as a list of row records.
    Use as_of to read a specific historical version number; omit for the latest version.
    """
    lib = get_ac()[library]
    result = lib.read(symbol, as_of=as_of) if as_of is not None else lib.read(symbol)
    return result.data.to_dict(orient="records")


@register_tool("head_symbol")
def head_symbol(library: str, symbol: str, n: int = 5):
    """
    Return the first n rows of a symbol (default 5).
    Useful for previewing large datasets without loading all data.
    """
    result = get_ac()[library].head(symbol, n=n)
    return result.data.to_dict(orient="records")


@register_tool("tail_symbol")
def tail_symbol(library: str, symbol: str, n: int = 5):
    """
    Return the last n rows of a symbol (default 5).
    Useful for previewing the most recent data without loading all data.
    """
    result = get_ac()[library].tail(symbol, n=n)
    return result.data.to_dict(orient="records")


@register_tool("write_symbol")
def write_symbol(library: str, symbol: str, data: list):
    """
    Write data to a symbol, creating a new version.
    data is a list of row records, where each record is a dict of column name to value.
    Example: [{"timestamp": "2024-01-01", "price": 100.0, "volume": 200}]
    """
    df = pd.DataFrame(data)
    get_ac()[library].write(symbol, df)
    return f"Written {len(df)} rows to '{symbol}'."


@register_tool("append_symbol")
def append_symbol(library: str, symbol: str, data: list):
    """
    Append rows to an existing symbol, creating a new version.
    The new rows must have index values strictly later than the existing data.
    data is a list of row records, where each record is a dict of column name to value.
    """
    df = pd.DataFrame(data)
    get_ac()[library].append(symbol, df)
    return f"Appended {len(df)} rows to '{symbol}'."


@register_tool("update_symbol")
def update_symbol(library: str, symbol: str, data: list):
    """
    Overwrite a date range of a timeseries symbol with new data, creating a new version.
    The symbol must have a datetime index. Only the rows whose index falls within the
    range of the provided data are replaced; rows outside that range are preserved.
    data is a list of row records, where each record is a dict of column name to value.
    """
    df = pd.DataFrame(data)
    get_ac()[library].update(symbol, df)
    return f"Updated '{symbol}' with {len(df)} rows."


@register_tool("delete_symbol")
def delete_symbol(library: str, symbol: str):
    """
    Delete a symbol and all its versions from the library.
    No-op if the symbol does not exist.
    """
    get_ac()[library].delete(symbol)
    return f"Deleted '{symbol}'."


@register_tool("delete_data_in_range")
def delete_data_in_range(library: str, symbol: str, start: str, end: str):
    """
    Delete all rows within a date range from a timeseries symbol, creating a new version.
    The symbol must have a datetime index.
    start and end are ISO 8601 date strings, e.g. "2024-01-01".
    """
    date_range = (pd.Timestamp(start), pd.Timestamp(end))
    get_ac()[library].delete_data_in_range(symbol, date_range=date_range)
    return f"Deleted data in range {start} to {end} from '{symbol}'."


@register_tool("symbol_exists")
def symbol_exists(library: str, symbol: str):
    """Check whether a symbol exists in the given library."""
    return get_ac()[library].has_symbol(symbol)


@register_tool("get_symbol_info")
def get_symbol_info(library: str, symbol: str):
    """
    Return descriptive information about a symbol: row count, column names, and last update time.
    Raises ValueError if the symbol does not exist.
    """
    lib = get_ac()[library]
    if not lib.has_symbol(symbol):
        raise ValueError(f"Symbol '{symbol}' does not exist in library '{library}'.")
    info = lib.get_info(symbol)
    columns = info.get("col_names", info.get("columns"))
    return {
        "symbol": symbol,
        "rows": info.get("rows"),
        "columns": columns,
        "last_update": str(info.get("last_update")),
    }


@register_tool("read_metadata")
def read_metadata(library: str, symbol: str):
    """
    Read only the metadata for a symbol without loading its data.
    Faster than a full read when only metadata is needed.
    """
    result = get_ac()[library].read_metadata(symbol)
    return result.metadata


@register_tool("write_metadata")
def write_metadata(library: str, symbol: str, metadata: dict):
    """
    Update the metadata for a symbol without modifying its data.
    Creates a new version. The metadata must be a JSON-serialisable dict.
    """
    get_ac()[library].write_metadata(symbol, metadata)
    return f"Metadata updated for '{symbol}'."


@register_tool("list_versions")
def list_versions(library: str, symbol: str):
    """
    List all versions of a symbol with their version number and write timestamp.
    Versions are created on every write, append, update, or metadata change.
    """
    versions = get_ac()[library].list_versions(symbol)
    return [
        {
            "version": v.version,
            "date": str(v.timestamp),
        }
        for v in versions
    ]
