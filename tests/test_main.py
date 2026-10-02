import unittest
import inspect
from unittest.mock import patch

import arcticdb_mcp.main as main_module


class MainEntrypointTests(unittest.TestCase):
    def test_main_runs_stdio_when_no_port_set(self):
        with patch.dict("os.environ", {}, clear=True):
            with patch.object(main_module.mcp, "run") as run_mock:
                main_module.main()
                run_mock.assert_called_once_with()

    def test_main_runs_http_sse_when_port_set(self):
        with patch.dict("os.environ", {"ARCTICDB_MCP_PORT": "8000"}, clear=True):
            with patch.object(main_module, "_run_http_sse") as run_mock:
                main_module.main()
                run_mock.assert_called_once_with(8000)

    def test_explicit_host_signature_selects_sse(self):
        def legacy_run(self, host, port, transport):
            return None

        legacy_signature = inspect.signature(legacy_run)
        with patch.dict("os.environ", {"ARCTICDB_MCP_PORT": "8000"}, clear=True):
            with patch.object(main_module.inspect, "signature", return_value=legacy_signature):
                with patch.object(main_module.mcp, "run") as run_mock:
                    main_module.main()
                    run_mock.assert_called_once_with(
                        transport="sse",
                        host="0.0.0.0",
                        port=8000,
                    )

    def test_transport_kwargs_signature_selects_http(self):
        def modern_run(self, transport, **transport_kwargs):
            return None

        with patch.object(main_module.inspect, "signature", return_value=inspect.signature(modern_run)):
            with patch.object(main_module.mcp, "run") as run_mock:
                main_module._run_http_sse(8000)
                run_mock.assert_called_once_with(transport="http", host="0.0.0.0", port=8000)


if __name__ == "__main__":
    unittest.main()
