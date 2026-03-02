from ..connection import get_ac
from ..registry import register_tool
from ..utils.arctic_options import parse_library_option
from ..utils.batch_payloads import build_read_info_request
from ..utils.serialization import normalize_value, serialize_symbol_description


@register_tool("get_uri")
def get_uri():
    """Return the ArcticDB URI used by this MCP server connection."""
    return get_ac().get_uri()


@register_tool("describe")
def describe(library: str = None):
    """
    Return a compact summary of the ArcticDB store.

    If library is provided, describes only that library.
    If omitted, describes all libraries.

    Returns per symbol: row count, column names, date range,
    latest version number, last update time, and metadata.
    Useful as a first call to orient Claude before any analysis.
    """
    ac = get_ac()
    libraries_to_scan = [library] if library else ac.list_libraries()

    result = {
        "uri": str(ac.get_uri()),
        "libraries": {},
    }

    for lib_name in libraries_to_scan:
        lib = ac[lib_name]
        symbols = lib.list_symbols()

        lib_entry = {
            "symbol_count": len(symbols),
            "symbols": {},
        }

        if symbols:
            requests = [build_read_info_request(s) for s in symbols]
            descriptions = lib.get_description_batch(requests)
            metadatas = lib.read_metadata_batch(requests)

            for symbol, desc, meta in zip(symbols, descriptions, metadatas):
                desc_info = serialize_symbol_description(desc)
                lib_entry["symbols"][symbol] = {
                    "rows": desc_info.get("row_count"),
                    "columns": desc_info.get("columns"),
                    "date_range": desc_info.get("date_range"),
                    "last_update": desc_info.get("last_update_time"),
                    "latest_version": getattr(meta, "version", None),
                    "metadata": normalize_value(getattr(meta, "metadata", None)),
                }

        result["libraries"][lib_name] = lib_entry

    return result


@register_tool("modify_library_option")
def modify_library_option(library: str, option: str, option_value):
    """
    Modify a configurable library option.
    Supported options include DEDUP, ROWS_PER_SEGMENT, COLUMNS_PER_SEGMENT,
    REPLICATION, and BACKGROUND_DELETION.
    """
    ac = get_ac()
    if not ac.has_library(library):
        raise ValueError(f"Library '{library}' does not exist.")

    library_option = parse_library_option(option)
    ac.modify_library_option(ac[library], library_option, option_value)
    return (
        f"Library '{library}' option '{option.upper()}' updated to '{option_value}'."
    )
