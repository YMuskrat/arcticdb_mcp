import unittest
from unittest.mock import patch

import arcticdb_mcp.main as server


class PortTests(unittest.TestCase):
    def test_valid_boundaries(self):
        for port in ('1', '8000', '65535'):
            with self.subTest(port=port), patch.dict('os.environ', {'ARCTICDB_MCP_PORT': port}, clear=True):
                with patch.object(server, '_run_http_sse') as run:
                    server.main()
                    run.assert_called_once_with(int(port))

    def test_invalid_ports_never_start_server(self):
        for port in ('abc', '0', '-1', '65536', '1.5'):
            with self.subTest(port=port), patch.dict('os.environ', {'ARCTICDB_MCP_PORT': port}, clear=True):
                with patch.object(server, '_run_http_sse') as http, patch.object(server.mcp, 'run') as stdio:
                    with self.assertRaisesRegex(ValueError, 'ARCTICDB_MCP_PORT.*1.*65535'):
                        server.main()
                    http.assert_not_called()
                    stdio.assert_not_called()

    def test_empty_port_selects_stdio(self):
        with patch.dict('os.environ', {'ARCTICDB_MCP_PORT': ''}, clear=True):
            with patch.object(server.mcp, 'run') as run:
                server.main()
                run.assert_called_once_with()
