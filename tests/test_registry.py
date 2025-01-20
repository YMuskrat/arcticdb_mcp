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
