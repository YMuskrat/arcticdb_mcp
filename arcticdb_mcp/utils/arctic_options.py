from arcticdb_ext.storage import (
    ModifiableEnterpriseLibraryOption,
    ModifiableLibraryOption,
)


def parse_library_option(option: str):
    normalized = option.strip().upper()

    if hasattr(ModifiableLibraryOption, normalized):
        return getattr(ModifiableLibraryOption, normalized)

    if hasattr(ModifiableEnterpriseLibraryOption, normalized):
        return getattr(ModifiableEnterpriseLibraryOption, normalized)

    allowed = sorted(
        [name for name in dir(ModifiableLibraryOption) if name.isupper()]
        + [name for name in dir(ModifiableEnterpriseLibraryOption) if name.isupper()]
    )
    raise ValueError(f"Unsupported option '{option}'. Use one of: {allowed}")

