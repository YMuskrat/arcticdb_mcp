import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

from arcticdb import Arctic
from arcticdb_mcp.connection import get_ac
from arcticdb_mcp.tools.symbol_tools import (
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    read_symbol,
    read_symbol_page,
)


class SymbolPaginationValidationTests(unittest.TestCase):
    def test_default_constants(self):
        self.assertEqual(DEFAULT_PAGE_SIZE, 100)
        self.assertEqual(MAX_PAGE_SIZE, 1000)

    def test_invalid_offset_rejected(self):
        for bad_offset in (-1, -100, "0", 1.5, True, False, None):
            with self.subTest(offset=bad_offset):
                with self.assertRaisesRegex(ValueError, "offset"):
                    read_symbol_page("lib", "sym", offset=bad_offset)

    def test_invalid_limit_rejected(self):
        for bad_limit in (0, -1, 1001, 5000, "100", 10.5, True, False, None):
            with self.subTest(limit=bad_limit):
                with self.assertRaisesRegex(ValueError, "limit"):
                    read_symbol_page("lib", "sym", limit=bad_limit)

    def test_invalid_columns_rejected(self):
        for bad_cols in ("single_col", 123, [1, 2], ["a", None]):
            with self.subTest(columns=bad_cols):
                with self.assertRaisesRegex(ValueError, "columns"):
                    read_symbol_page("lib", "sym", columns=bad_cols)

    def test_invalid_as_of_rejected(self):
        for bad_as_of in (-1, "1", 1.5, True, False):
            with self.subTest(as_of=bad_as_of):
                with self.assertRaisesRegex(ValueError, "as_of"):
                    read_symbol_page("lib", "sym", as_of=bad_as_of)

    def test_missing_library_rejected(self):
        mock_ac = MagicMock()
        mock_ac.has_library.return_value = False
        with patch("arcticdb_mcp.tools.symbol_tools.get_ac", return_value=mock_ac):
            with self.assertRaisesRegex(ValueError, "Library 'non_existent' does not exist"):
                read_symbol_page("non_existent", "sym")

    def test_missing_symbol_rejected(self):
        mock_ac = MagicMock()
        mock_ac.has_library.return_value = True
        mock_lib = MagicMock()
        mock_lib.has_symbol.return_value = False
        mock_ac.__getitem__.return_value = mock_lib
        with patch("arcticdb_mcp.tools.symbol_tools.get_ac", return_value=mock_ac):
            with self.assertRaisesRegex(ValueError, "Symbol 'missing' does not exist in library 'lib'"):
                read_symbol_page("lib", "missing")


class SymbolPaginationBackendTests(unittest.TestCase):
    def test_passes_backend_slicing_and_columns_projection(self):
        mock_ac = MagicMock()
        mock_lib = MagicMock()
        mock_ac.has_library.return_value = True
        mock_lib.has_symbol.return_value = True
        mock_ac.__getitem__.return_value = mock_lib

        # Mock result of read
        df = pd.DataFrame({"col_b": [20, 30]})
        mock_read_result = MagicMock()
        mock_read_result.data = df
        mock_read_result.version = 3
        mock_lib.read.return_value = mock_read_result

        # Mock get_description
        mock_desc = MagicMock()
        mock_desc.row_count = 10
        mock_lib.get_description.return_value = mock_desc

        with patch("arcticdb_mcp.tools.symbol_tools.get_ac", return_value=mock_ac):
            res = read_symbol_page(
                library="finance",
                symbol="AAPL",
                offset=2,
                limit=5,
                columns=["col_b"],
                as_of=3,
            )

        # Verify backend kwargs passed to ArcticDB
        mock_lib.read.assert_called_once_with(
            "AAPL",
            row_range=(2, 7),
            columns=["col_b"],
            as_of=3,
        )
        mock_lib.get_description.assert_called_once_with("AAPL", as_of=3)

        self.assertEqual(res["symbol"], "AAPL")
        self.assertEqual(res["library"], "finance")
        self.assertEqual(res["version"], 3)
        self.assertEqual(res["offset"], 2)
        self.assertEqual(res["limit"], 5)
        self.assertEqual(res["count"], 2)
        self.assertEqual(res["total_rows"], 10)
        self.assertTrue(res["has_more"])
        self.assertEqual(res["next_offset"], 4)
        self.assertEqual(res["columns"], ["col_b"])

    def test_read_symbol_remains_unchanged(self):
        mock_ac = MagicMock()
        mock_lib = MagicMock()
        mock_ac.__getitem__.return_value = mock_lib

        df = pd.DataFrame({"price": [100.0, 101.0]})
        mock_read_res = MagicMock()
        mock_read_res.data = df
        mock_lib.read.return_value = mock_read_res

        with patch("arcticdb_mcp.tools.symbol_tools.get_ac", return_value=mock_ac):
            records = read_symbol("finance", "AAPL", as_of=2)

        mock_lib.read.assert_called_once_with("AAPL", as_of=2)
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["price"], 100.0)


class SymbolPaginationLMDBIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.uri = f"lmdb://{self.temp_dir}"
        get_ac.cache_clear()

        self.ac = Arctic(self.uri)
        self.ac.create_library("market")
        self.lib = self.ac["market"]

    def tearDown(self):
        get_ac.cache_clear()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_reconstruct_multipage_symbol_with_version_pinning(self):
        # Seed 250 rows in initial version 0
        total_initial_rows = 250
        dates = pd.date_range("2024-01-01", periods=total_initial_rows, freq="h")
        df_v0 = pd.DataFrame(
            {
                "date": dates,
                "val": list(range(total_initial_rows)),
                "extra": [f"item_{i}" for i in range(total_initial_rows)],
            }
        ).set_index("date")
        self.lib.write("TICKER", df_v0)

        with patch.dict("os.environ", {"ARCTICDB_URI": self.uri}):
            # Read first page
            page1 = read_symbol_page("market", "TICKER", offset=0, limit=60)
            self.assertEqual(page1["offset"], 0)
            self.assertEqual(page1["limit"], 60)
            self.assertEqual(page1["count"], 60)
            self.assertEqual(page1["total_rows"], 250)
            self.assertTrue(page1["has_more"])
            self.assertEqual(page1["next_offset"], 60)
            self.assertEqual(page1["version"], 0)

            pinned_version = page1["version"]

            # Perform a concurrent mutation to the symbol
            df_v1 = pd.DataFrame(
                {
                    "date": pd.date_range("2025-01-01", periods=50, freq="h"),
                    "val": list(range(1000, 1050)),
                    "extra": [f"extra_{i}" for i in range(50)],
                }
            ).set_index("date")
            self.lib.write("TICKER", df_v1)
            self.assertEqual(self.lib.get_description("TICKER").row_count, 50)

            # Continue paginating through the remaining pages of version 0 using pinned version
            all_records = list(page1["data"])
            curr_offset = page1["next_offset"]

            page_count = 1
            while curr_offset is not None:
                page = read_symbol_page(
                    "market",
                    "TICKER",
                    offset=curr_offset,
                    limit=60,
                    as_of=pinned_version,
                )
                self.assertEqual(page["version"], pinned_version)
                self.assertEqual(page["total_rows"], total_initial_rows)
                all_records.extend(page["data"])
                curr_offset = page["next_offset"]
                page_count += 1

            self.assertEqual(page_count, 5)  # 60, 60, 60, 60, 10 = 250 rows across 5 pages
            self.assertEqual(len(all_records), total_initial_rows)

            # Verify no rows lost or duplicated, perfectly sequential
            reconstructed_vals = [r["val"] for r in all_records]
            self.assertEqual(reconstructed_vals, list(range(total_initial_rows)))

    def test_exact_page_boundary_and_empty_results(self):
        df = pd.DataFrame({"val": range(10)})
        self.lib.write("EXACT", df)

        with patch.dict("os.environ", {"ARCTICDB_URI": self.uri}):
            # Page 1: exactly half (0..5)
            p1 = read_symbol_page("market", "EXACT", offset=0, limit=5)
            self.assertEqual(p1["count"], 5)
            self.assertTrue(p1["has_more"])
            self.assertEqual(p1["next_offset"], 5)

            # Page 2: remaining half (5..10) - exact boundary
            p2 = read_symbol_page("market", "EXACT", offset=5, limit=5)
            self.assertEqual(p2["count"], 5)
            self.assertFalse(p2["has_more"])
            self.assertIsNone(p2["next_offset"])

            # Page 3: request beyond end
            p3 = read_symbol_page("market", "EXACT", offset=10, limit=5)
            self.assertEqual(p3["count"], 0)
            self.assertEqual(p3["data"], [])
            self.assertFalse(p3["has_more"])
            self.assertIsNone(p3["next_offset"])

    def test_column_projection_and_index_name_collision(self):
        # Index name 'val' collides with column 'val'
        df = pd.DataFrame({"val": [10, 20, 30], "other": [1, 2, 3]})
        df.index.name = "val"
        self.lib.write("COLLISION", df)

        with patch.dict("os.environ", {"ARCTICDB_URI": self.uri}):
            # 1. Project colliding column 'val': index becomes 'val_index' and column remains 'val'
            res_collision = read_symbol_page("market", "COLLISION", offset=0, limit=2, columns=["val"])
            self.assertEqual(res_collision["count"], 2)
            self.assertEqual(res_collision["columns"], ["val"])
            self.assertIn("val_index", res_collision["data"][0])
            self.assertIn("val", res_collision["data"][0])
            self.assertEqual(res_collision["data"][0]["val_index"], 0)
            self.assertEqual(res_collision["data"][0]["val"], 10)

            # 2. Project non-colliding column 'other': index is preserved as 'val'
            res_other = read_symbol_page("market", "COLLISION", offset=0, limit=2, columns=["other"])
            self.assertEqual(res_other["count"], 2)
            self.assertEqual(res_other["columns"], ["other"])
            self.assertIn("val", res_other["data"][0])
            self.assertIn("other", res_other["data"][0])
            self.assertEqual(res_other["data"][0]["val"], 0)
            self.assertEqual(res_other["data"][0]["other"], 1)



if __name__ == "__main__":
    unittest.main()
