import copy
import unittest

import pandas as pd

from arcticdb_mcp.utils.timeseries import UPDATE_INDEX_COLUMN_CANDIDATES, rows_to_timeseries_update_frame


class TimeseriesTests(unittest.TestCase):
    def test_supported_columns_preserve_values_timezone_and_input(self):
        for column in UPDATE_INDEX_COLUMN_CANDIDATES:
            with self.subTest(column=column):
                rows = [{column: '2026-01-02T00:00:00Z', 'price': 20},
                        {column: '2026-01-01T00:00:00Z', 'price': 10}]
                original = copy.deepcopy(rows)
                frame = rows_to_timeseries_update_frame(rows)
                expected = pd.DataFrame({'price': [10, 20]}, index=pd.DatetimeIndex(
                    ['2026-01-01T00:00:00Z', '2026-01-02T00:00:00Z'], name=column))
                pd.testing.assert_frame_equal(frame, expected)
                self.assertEqual(rows, original)

    def test_actionable_errors(self):
        for rows, message in [([], 'at least one row'), ([{'price': 10}], 'datetime-indexed'),
                              ([{'date': 'not-a-date', 'price': 10}], 'invalid datetime')]:
            with self.subTest(rows=rows), self.assertRaisesRegex(ValueError, message):
                rows_to_timeseries_update_frame(rows)
