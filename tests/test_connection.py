import unittest
from unittest.mock import patch

from arcticdb_mcp.connection import get_ac


class ConnectionTests(unittest.TestCase):
    def setUp(self):
        get_ac.cache_clear()
        self.addCleanup(get_ac.cache_clear)

    def test_reuses_successful_connection(self):
        with patch.dict('os.environ', {'ARCTICDB_URI': 'lmdb://test-only'}, clear=True):
            with patch('arcticdb_mcp.connection.Arctic') as constructor:
                self.assertIs(get_ac(), constructor.return_value)
                self.assertIs(get_ac(), constructor.return_value)
                constructor.assert_called_once_with('lmdb://test-only')

    def test_missing_configuration_never_connects(self):
        for environment in ({}, {'ARCTICDB_URI': ''}):
            with self.subTest(environment=environment), patch.dict('os.environ', environment, clear=True):
                with patch('arcticdb_mcp.connection.Arctic') as constructor:
                    with self.assertRaisesRegex(RuntimeError, 'ARCTICDB_URI'):
                        get_ac()
                    constructor.assert_not_called()

    def test_failure_preserves_cause_and_is_not_cached(self):
        failure = ValueError('synthetic connection failure')
        connection = object()
        with patch.dict('os.environ', {'ARCTICDB_URI': 'lmdb://test-only'}, clear=True):
            with patch('arcticdb_mcp.connection.Arctic', side_effect=[failure, connection]) as constructor:
                with self.assertRaises(RuntimeError) as caught:
                    get_ac()
                self.assertIs(caught.exception.__cause__, failure)
                self.assertIs(get_ac(), connection)
                self.assertIs(get_ac(), connection)
                self.assertEqual(constructor.call_count, 2)
