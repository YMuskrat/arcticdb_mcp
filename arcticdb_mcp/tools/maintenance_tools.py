from typing import Optional

from ..connection import get_ac
from ..registry import register_tool
from ..utils.serialization import serialize_batch_entry


@register_tool("get_library_options")
def get_library_options(library: str):
    """Return non-enterprise library options."""
    options = get_ac()[library].options()
    return {
        "dynamic_schema": options.dynamic_schema,
        "dedup": options.dedup,
        "rows_per_segment": options.rows_per_segment,
        "columns_per_segment": options.columns_per_segment,
        "encoding_version": options.encoding_version,
    }


@register_tool("get_enterprise_options")
def get_enterprise_options(library: str):
    """Return enterprise library options."""
    options = get_ac()[library].enterprise_options()
    return {
        "replication": options.replication,
        "background_deletion": options.background_deletion,
    }


@register_tool("reload_symbol_list")
def reload_symbol_list(library: str):
    """Force a symbol-list cache reload for a library."""
    get_ac()[library].reload_symbol_list()
    return f"Symbol list cache reloaded for library '{library}'."


@register_tool("compact_symbol_list")
def compact_symbol_list(library: str):
    """Compact the symbol list cache into a single key in storage."""
    get_ac()[library].compact_symbol_list()
    return f"Symbol list cache compacted for library '{library}'."


@register_tool("prune_previous_versions")
def prune_previous_versions(library: str, symbol: str):
    """Remove all non-snapshotted symbol versions except the latest."""
    get_ac()[library].prune_previous_versions(symbol)
    return f"Pruned previous versions for symbol '{symbol}'."


@register_tool("is_symbol_fragmented")
def is_symbol_fragmented(
    library: str, symbol: str, segment_size: Optional[int] = None
):
    """Check whether compaction would reduce segment count for a symbol."""
    lib = get_ac()[library]
    if segment_size is None:
        return lib.is_symbol_fragmented(symbol)
    return lib.is_symbol_fragmented(symbol, segment_size=segment_size)


@register_tool("defragment_symbol_data")
def defragment_symbol_data(
    library: str,
    symbol: str,
    segment_size: Optional[int] = None,
    prune_previous_versions: bool = False,
):
    """
    Defragment symbol data by compacting fragmented row-sliced segments.
    Returns the resulting version information.
    """
    lib = get_ac()[library]
    kwargs = {"prune_previous_versions": prune_previous_versions}
    if segment_size is not None:
        kwargs["segment_size"] = segment_size
    try:
        result = lib.defragment_symbol_data(symbol, **kwargs)
        return serialize_batch_entry(result)
    except Exception as e:
        if "Nothing to compact" in str(e):
            return {
                "ok": True,
                "message": f"Symbol '{symbol}' is not fragmented; nothing to compact.",
            }
        raise
