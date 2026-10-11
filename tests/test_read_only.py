import asyncio
import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd
from fastmcp.exceptions import NotFoundError

from arcticdb import Arctic
from arcticdb_mcp.connection import get_ac
from arcticdb_mcp.main import create_mcp_server, is_read_only_mode, main
from arcticdb_mcp.registry import (
    TOOL_METADATA,
    TOOL_REGISTRY,
    get_tools,
    is_read_tool,
    register_tool,
)


class ReadOnlyConfigurationTests(unittest.TestCase):
    def test_default_is_not_read_only(self):
        with patch.dict("os.environ", {}, clear=True):
            self.assertFalse(is_read_only_mode())

    def test_empty_string_is_not_read_only(self):
        with patch.dict("os.environ", {"ARCTICDB_MCP_READ_ONLY": ""}, clear=True):
            self.assertFalse(is_read_only_mode())

    def test_truthy_values(self):
        for val in ("1", "true", "True", "TRUE", "yes", "YES", "on", "ON"):
            with self.subTest(val=val), patch.dict(
                "os.environ", {"ARCTICDB_MCP_READ_ONLY": val}, clear=True
            ):
                self.assertTrue(is_read_only_mode())

    def test_falsy_values(self):
        for val in ("0", "false", "False", "FALSE", "no", "NO", "off", "OFF"):
            with self.subTest(val=val), patch.dict(
                "os.environ", {"ARCTICDB_MCP_READ_ONLY": val}, clear=True
            ):
                self.assertFalse(is_read_only_mode())

    def test_invalid_values_raise_actionable_error(self):
        for val in ("invalid", "2", "maybe", "read-only", "none"):
            with self.subTest(val=val), patch.dict(
                "os.environ", {"ARCTICDB_MCP_READ_ONLY": val}, clear=True
            ):
                with self.assertRaisesRegex(ValueError, "ARCTICDB_MCP_READ_ONLY"):
                    is_read_only_mode()

    def test_main_rejects_invalid_read_only_config(self):
        with patch.dict("os.environ", {"ARCTICDB_MCP_READ_ONLY": "bad_value"}, clear=True):
            with self.assertRaisesRegex(ValueError, "ARCTICDB_MCP_READ_ONLY"):
                main()


class ReadOnlyServerTests(unittest.TestCase):
    MUTATING_TOOLS = {
        "modify_library_option",
        "create_library",
        "delete_library",
        "write_symbol",
        "append_symbol",
        "update_symbol",
        "delete_symbol",
        "delete_data_in_range",
        "write_metadata",
        "write_batch",
        "append_batch",
        "update_batch",
        "delete_batch",
        "write_metadata_batch",
        "write_pickle",
        "write_pickle_batch",
        "create_snapshot",
        "delete_snapshot",
        "reload_symbol_list",
        "compact_symbol_list",
        "prune_previous_versions",
        "defragment_symbol_data",
    }

    READ_TOOLS = {
        "get_uri",
        "describe",
        "list_libraries",
        "library_exists",
        "get_library",
        "list_symbols",
        "read_symbol",
        "head_symbol",
        "tail_symbol",
        "symbol_exists",
        "get_symbol_info",
        "read_metadata",
        "list_versions",
        "read_batch",
        "read_metadata_batch",
        "get_description_batch",
        "query_filter",
        "query_filter_isin",
        "query_groupby",
        "query_date_range",
        "query_resample",
        "list_snapshots",
        "read_symbol_from_snapshot",
        "get_library_options",
        "get_enterprise_options",
        "is_symbol_fragmented",
    }

    def test_all_tools_classified(self):
        all_registered = set(TOOL_REGISTRY.keys())
        expected = self.MUTATING_TOOLS | self.READ_TOOLS
        self.assertEqual(all_registered, expected)
        self.assertEqual(len(all_registered), 48)
        self.assertEqual(len(self.READ_TOOLS), 26)
        self.assertEqual(len(self.MUTATING_TOOLS), 22)

    def test_default_server_registers_all_tools(self):
        server = create_mcp_server(read_only=False)
        tools = asyncio.run(server.list_tools())
        registered_names = {t.name for t in tools}
        self.assertEqual(registered_names, set(TOOL_REGISTRY.keys()))

    def test_read_only_server_excludes_all_mutating_tools(self):
        server = create_mcp_server(read_only=True)
        tools = asyncio.run(server.list_tools())
        registered_names = {t.name for t in tools}

        self.assertEqual(registered_names, self.READ_TOOLS)
        for mutating_tool in self.MUTATING_TOOLS:
            self.assertNotIn(mutating_tool, registered_names)

    def test_read_only_server_rejects_direct_mutating_calls(self):
        server = create_mcp_server(read_only=True)
        for tool_name in ("write_symbol", "delete_library", "create_snapshot", "delete_batch"):
            with self.subTest(tool=tool_name):
                with self.assertRaises(NotFoundError):
                    asyncio.run(server.call_tool(tool_name, {}))

    def test_future_unclassified_tools_cannot_leak_into_read_only_mode(self):
        with patch.dict(TOOL_REGISTRY, dict(TOOL_REGISTRY)):
            with patch.dict(TOOL_METADATA, dict(TOOL_METADATA)):
                @register_tool("future_unclassified_operation")
                def future_op():
                    return "dangerous mutation"

                # Verify it is not classified as read tool
                self.assertFalse(is_read_tool("future_unclassified_operation"))

                # In default mode, it is registered
                default_server = create_mcp_server(read_only=False)
                default_tools = {t.name for t in asyncio.run(default_server.list_tools())}
                self.assertIn("future_unclassified_operation", default_tools)

                # In read-only mode, it MUST NOT be registered
                ro_server = create_mcp_server(read_only=True)
                ro_tools = {t.name for t in asyncio.run(ro_server.list_tools())}
                self.assertNotIn("future_unclassified_operation", ro_tools)


class ReadOnlyLMDBIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.uri = f"lmdb://{self.temp_dir}"
        get_ac.cache_clear()

        # Seed real LMDB database with library, symbols, and data
        ac = Arctic(self.uri)
        ac.create_library("market_data")
        lib = ac["market_data"]

        df = pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=5, freq="D"),
                "price": [10.0, 11.5, 12.0, 10.5, 13.0],
                "volume": [100, 150, 120, 200, 180],
            }
        ).set_index("date")
        lib.write("AAPL", df, metadata={"source": "exchange", "verified": True})

    def tearDown(self):
        get_ac.cache_clear()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _call(self, server, tool_name, args):
        import json
        res = asyncio.run(server.call_tool(tool_name, args))
        self.assertFalse(res.is_error)
        self.assertTrue(len(res.content) > 0)
        return json.loads(res.content[0].text)

    def test_read_operations_succeed_under_lmdb_read_only(self):
        with patch.dict("os.environ", {"ARCTICDB_URI": self.uri, "ARCTICDB_MCP_READ_ONLY": "true"}):
            server = create_mcp_server(read_only=True)

            # 1. list_libraries
            res_libs = self._call(server, "list_libraries", {})
            self.assertIn("market_data", res_libs)

            # 2. get_library
            res_lib = self._call(server, "get_library", {"name": "market_data"})
            self.assertEqual(res_lib["name"], "market_data")
            self.assertIn("AAPL", res_lib["symbols"])

            # 3. list_symbols
            res_syms = self._call(server, "list_symbols", {"library": "market_data"})
            self.assertIn("AAPL", res_syms)

            # 4. read_symbol
            res_read = self._call(server, "read_symbol", {"library": "market_data", "symbol": "AAPL"})
            self.assertEqual(len(res_read), 5)
            self.assertEqual(res_read[0]["price"], 10.0)

            # 5. head_symbol
            res_head = self._call(server, "head_symbol", {"library": "market_data", "symbol": "AAPL", "n": 2})
            self.assertEqual(len(res_head), 2)

            # 6. tail_symbol
            res_tail = self._call(server, "tail_symbol", {"library": "market_data", "symbol": "AAPL", "n": 2})
            self.assertEqual(len(res_tail), 2)

            # 7. get_symbol_info
            res_info = self._call(server, "get_symbol_info", {"library": "market_data", "symbol": "AAPL"})
            self.assertEqual(res_info["rows"], 5)
            self.assertIn("price", res_info["columns"])
            self.assertEqual(res_info["metadata"], {"source": "exchange", "verified": True})

            # 8. read_metadata
            res_meta = self._call(server, "read_metadata", {"library": "market_data", "symbol": "AAPL"})
            self.assertEqual(res_meta, {"source": "exchange", "verified": True})

            # 9. describe
            res_desc = self._call(server, "describe", {"library": "market_data"})
            self.assertIn("market_data", res_desc["libraries"])

            # 10. query_filter
            res_q = self._call(
                server,
                "query_filter",
                {
                    "library": "market_data",
                    "symbol": "AAPL",
                    "filters": [{"column": "price", "op": ">", "value": 11.0}],
                },
            )
            self.assertEqual(len(res_q), 3)

            # 11. read_batch
            res_batch = self._call(server, "read_batch", {"library": "market_data", "symbols": ["AAPL"]})
            self.assertEqual(len(res_batch), 1)
            self.assertEqual(res_batch[0]["symbol"], "AAPL")


    def test_mutations_blocked_and_do_not_affect_lmdb(self):
        with patch.dict("os.environ", {"ARCTICDB_URI": self.uri, "ARCTICDB_MCP_READ_ONLY": "true"}):
            server = create_mcp_server(read_only=True)

            # Calling mutating tools must fail with NotFoundError
            with self.assertRaises(NotFoundError):
                asyncio.run(
                    server.call_tool(
                        "write_symbol",
                        {
                            "library": "market_data",
                            "symbol": "AAPL",
                            "data": [{"date": "2025-01-01", "price": 999.0}],
                        },
                    )
                )

            with self.assertRaises(NotFoundError):
                asyncio.run(server.call_tool("delete_library", {"name": "market_data"}))

            # Verify underlying data was completely untouched
            ac = Arctic(self.uri)
            self.assertTrue(ac.has_library("market_data"))
            self.assertEqual(len(ac["market_data"].read("AAPL").data), 5)


if __name__ == "__main__":
    unittest.main()
