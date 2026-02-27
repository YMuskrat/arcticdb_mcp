from ..registry import register_tool
from ..connection import get_ac


@register_tool("list_libraries")
def list_libraries():
    """List all libraries in the Arctic instance."""
    return get_ac().list_libraries()


@register_tool("create_library")
def create_library(name: str):
    """
    Create a new library with the given name.
    Libraries are the top-level containers for named symbols in ArcticDB.
    """
    get_ac().create_library(name)
    return f"Library '{name}' created."


@register_tool("delete_library")
def delete_library(name: str):
    """
    Delete a library and all its underlying data permanently.
    No-op if the library does not exist.
    """
    get_ac().delete_library(name)
    return f"Library '{name}' deleted."


@register_tool("library_exists")
def library_exists(name: str):
    """Check whether a library with the given name exists."""
    return get_ac().has_library(name)


@register_tool("get_library")
def get_library(name: str):
    """Return the name and full list of symbols stored in a library."""
    ac = get_ac()
    if not ac.has_library(name):
        raise ValueError(f"Library '{name}' does not exist.")
    lib = ac[name]
    return {
        "name": name,
        "symbols": lib.list_symbols(),
    }
