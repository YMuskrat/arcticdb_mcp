from typing import Optional

from arcticdb.version_store.library import WriteMetadataPayload

from ..connection import get_ac
from ..registry import register_tool
from ..utils.batch_payloads import (
    build_delete_request,
    build_read_info_request,
    build_read_request,
    build_update_payload,
    build_write_payload,
)
from ..utils.serialization import serialize_batch_entry


@register_tool("write_batch")
def write_batch(
    library: str, payloads: list, prune_previous_versions: bool = False, validate_index=True
):
    """
    Write multiple symbols in one call.
    payload format: {"symbol": str, "data": list[dict], "metadata"?: any, "index_column"?: str}
    """
    write_payloads = [build_write_payload(payload) for payload in payloads]
    results = get_ac()[library].write_batch(
        write_payloads,
        prune_previous_versions=prune_previous_versions,
        validate_index=validate_index,
    )
    return [serialize_batch_entry(result) for result in results]


@register_tool("append_batch")
def append_batch(
    library: str,
    append_payloads: list,
    prune_previous_versions: bool = False,
    validate_index=True,
):
    """
    Append to multiple symbols in one call.
    payload format: {"symbol": str, "data": list[dict], "metadata"?: any, "index_column"?: str}
    """
    payloads = [build_write_payload(payload) for payload in append_payloads]
    results = get_ac()[library].append_batch(
        payloads,
        prune_previous_versions=prune_previous_versions,
        validate_index=validate_index,
    )
    return [serialize_batch_entry(result) for result in results]


@register_tool("update_batch")
def update_batch(
    library: str, update_payloads: list, upsert: bool = False, prune_previous_versions: bool = False
):
    """
    Update multiple symbols in one call.
    payload format: {"symbol": str, "data": list[dict], "metadata"?: any, "date_range"?: [start, end], "index_column"?: str}
    """
    lib = get_ac()[library]
    payloads = [build_update_payload(lib, payload) for payload in update_payloads]
    results = lib.update_batch(
        payloads, upsert=upsert, prune_previous_versions=prune_previous_versions
    )
    return [serialize_batch_entry(result) for result in results]


@register_tool("delete_batch")
def delete_batch(library: str, delete_requests: list):
    """
    Delete multiple symbols or symbol versions in one call.
    request item can be symbol string or {"symbol": str, "version_ids": [int, ...]}.
    """
    requests = [build_delete_request(request) for request in delete_requests]
    results = get_ac()[library].delete_batch(requests)
    return [serialize_batch_entry(result) for result in results]


@register_tool("read_batch")
def read_batch(
    library: str, symbols: list, output_format: Optional[str] = None, lazy: bool = False
):
    """
    Read multiple symbols in one call.
    symbols items can be symbol strings or request dicts with:
    symbol, as_of, date_range, row_range, columns, output_format.
    """
    if lazy:
        raise ValueError("lazy=True is not currently supported by this MCP tool.")

    requests = [build_read_request(symbol) for symbol in symbols]
    results = get_ac()[library].read_batch(
        requests, lazy=lazy, output_format=output_format
    )
    return [serialize_batch_entry(result, include_data=True) for result in results]


@register_tool("read_metadata_batch")
def read_metadata_batch(library: str, symbols: list):
    """
    Read metadata for multiple symbols in one call.
    symbols items can be symbol strings or request dicts with symbol/as_of.
    """
    requests = [build_read_info_request(symbol) for symbol in symbols]
    results = get_ac()[library].read_metadata_batch(requests)
    return [serialize_batch_entry(result) for result in results]


@register_tool("get_description_batch")
def get_description_batch(library: str, symbols: list):
    """
    Get schema/description for multiple symbols in one call.
    symbols items can be symbol strings or request dicts with symbol/as_of.
    """
    requests = [build_read_info_request(symbol) for symbol in symbols]
    results = get_ac()[library].get_description_batch(requests)
    return [serialize_batch_entry(result) for result in results]


@register_tool("write_metadata_batch")
def write_metadata_batch(
    library: str, write_metadata_payloads: list, prune_previous_versions: bool = False
):
    """
    Write metadata for multiple symbols in one call.
    payload format: {"symbol": str, "metadata": any}
    """
    payloads = []
    for payload in write_metadata_payloads:
        if "symbol" not in payload:
            raise ValueError("Each metadata payload must include 'symbol'.")
        if "metadata" not in payload:
            raise ValueError("Each metadata payload must include 'metadata'.")
        payloads.append(WriteMetadataPayload(payload["symbol"], payload["metadata"]))

    results = get_ac()[library].write_metadata_batch(
        payloads, prune_previous_versions=prune_previous_versions
    )
    return [serialize_batch_entry(result) for result in results]


@register_tool("write_pickle")
def write_pickle(
    library: str,
    symbol: str,
    data,
    metadata=None,
    prune_previous_versions: bool = False,
    staged: bool = False,
):
    """Write arbitrary pickle-serializable data to a symbol."""
    result = get_ac()[library].write_pickle(
        symbol,
        data,
        metadata=metadata,
        prune_previous_versions=prune_previous_versions,
        staged=staged,
    )
    return serialize_batch_entry(result)


@register_tool("write_pickle_batch")
def write_pickle_batch(library: str, payloads: list, prune_previous_versions: bool = False):
    """
    Write multiple pickle-serializable payloads in one call.
    payload format: {"symbol": str, "data": any, "metadata"?: any, "index_column"?: str}
    """
    write_payloads = [build_write_payload(payload, for_pickle=True) for payload in payloads]
    results = get_ac()[library].write_pickle_batch(
        write_payloads, prune_previous_versions=prune_previous_versions
    )
    return [serialize_batch_entry(result) for result in results]
