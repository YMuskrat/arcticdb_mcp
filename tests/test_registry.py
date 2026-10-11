import unittest
from unittest.mock import patch

from arcticdb_mcp.registry import TOOL_REGISTRY, register_tool


class RegistryTests(unittest.TestCase):
    def test_duplicate_does_not_replace_original(self):
        with patch.dict(TOOL_REGISTRY, {}, clear=True):
            first = lambda: 1
            second = lambda: 2
            self.assertIs(register_tool('example')(first), first)
            self.assertIs(register_tool('example')(first), first)
            with self.assertRaisesRegex(ValueError, 'example'):
                register_tool('example')(second)
            self.assertIs(TOOL_REGISTRY['example'], first)

    def test_default_read_only_is_false(self):
        from arcticdb_mcp.registry import TOOL_METADATA, is_read_tool, get_tools
        with patch.dict(TOOL_REGISTRY, {}, clear=True), patch.dict(TOOL_METADATA, {}, clear=True):
            fn = lambda: 10
            register_tool('unclassified')(fn)
            self.assertFalse(is_read_tool('unclassified'))
            self.assertEqual(get_tools(read_only=True), {})
            self.assertEqual(get_tools(read_only=False), {'unclassified': fn})

    def test_explicit_read_only_classification(self):
        from arcticdb_mcp.registry import TOOL_METADATA, is_read_tool, get_tools
        with patch.dict(TOOL_REGISTRY, {}, clear=True), patch.dict(TOOL_METADATA, {}, clear=True):
            r_fn = lambda: 1
            w_fn = lambda: 2
            register_tool('read_op', read_only=True)(r_fn)
            register_tool('write_op', read_only=False)(w_fn)
            self.assertTrue(is_read_tool('read_op'))
            self.assertFalse(is_read_tool('write_op'))
            self.assertFalse(is_read_tool('unknown_op'))
            self.assertEqual(get_tools(read_only=True), {'read_op': r_fn})
            self.assertEqual(get_tools(read_only=False), {'read_op': r_fn, 'write_op': w_fn})

