from ..registry import register_tool
from ..connection import get_ac


@register_tool("create_snapshot")
def create_snapshot(library: str, snapshot_name: str):
    """
    Create a named snapshot of the current library state.
    A snapshot captures the latest version of every symbol at the time of creation,
    allowing point-in-time reads across the whole library. Raises an error if a
    snapshot with that name already exists.
    """
    get_ac()[library].snapshot(snapshot_name)
    return f"Snapshot '{snapshot_name}' created in library '{library}'."


@register_tool("list_snapshots")
def list_snapshots(library: str):
    """List the names of all snapshots in a library."""
    return list(get_ac()[library].list_snapshots().keys())


@register_tool("delete_snapshot")
def delete_snapshot(library: str, snapshot_name: str):
    """
    Delete a named snapshot from a library.
    Only the snapshot reference is removed; the underlying symbol data is not affected.
    Raises an error if the snapshot does not exist.
    """
    get_ac()[library].delete_snapshot(snapshot_name)
    return f"Snapshot '{snapshot_name}' deleted from library '{library}'."


@register_tool("read_symbol_from_snapshot")
def read_symbol_from_snapshot(library: str, symbol: str, snapshot_name: str):
    """
    Read a symbol as it existed at the time a named snapshot was created.
    Returns the symbol's data as a list of row records.
    """
    result = get_ac()[library].read(symbol, as_of=snapshot_name)
    return result.data.reset_index().to_dict(orient="records")
