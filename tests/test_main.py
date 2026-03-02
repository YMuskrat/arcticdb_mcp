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
            with patch.object(main_module.mcp, "run") as run_mock:
                main_module.main()
                run_mock.assert_called_once_with(
                    transport="sse",
                    host="0.0.0.0",
                    port=8000,
                )

    def test_main_http_fallback_when_transport_param_missing(self):
        def legacy_run(self, host, port):
            return None

        legacy_signature = inspect.signature(legacy_run)
        with patch.dict("os.environ", {"ARCTICDB_MCP_PORT": "8000"}, clear=True):
            with patch.object(main_module.inspect, "signature", return_value=legacy_signature):
                with patch.object(main_module.mcp, "run") as run_mock:
                    main_module.main()
                    run_mock.assert_called_once_with(
                        host="0.0.0.0",
                        port=8000,
                    )


if __name__ == "__main__":
    unittest.main()
