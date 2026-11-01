import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import requests

import main
from agents import motivator


class MotivatorReportTests(unittest.TestCase):
    def check_report(self, api_key, response=None, error=None, fallback=False):
        historical = [{"timestamp": "old", "agents": {"motivator": {
            "status": "SUCCESS", "data": "historical result"
        }}}]
        original_try_call = main.try_call

        def call_agent(module):
            if module is motivator:
                return original_try_call(module)
            return "unchanged agent result"

        with tempfile.TemporaryDirectory() as directory:
            previous = os.getcwd()
            self.addCleanup(os.chdir, previous)
            os.chdir(directory)
            Path("reports.json").write_text(json.dumps(historical), encoding="utf-8")
            with (
                patch.dict(os.environ, {"OPENROUTER_API_KEY": api_key}),
                patch("socket.socket", side_effect=AssertionError("Network forbidden")),
                patch.object(motivator.requests, "post", return_value=response,
                             side_effect=error),
                patch.object(motivator, "send_notification"),
                patch.object(main, "try_call", side_effect=call_agent),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                main.main()
            reports = json.loads(Path("reports.json").read_text(encoding="utf-8"))
            self.assertEqual(reports[:-1], historical)
            result = reports[-1]["agents"]["motivator"]
            self.assertEqual(result["status"], "SUCCESS")
            self.assertIsInstance(result["data"], str)
            self.assertIn("fallback_used", result)
            self.assertIs(result["fallback_used"], fallback)
            if fallback:
                self.assertIn("fallback-quote-engine", result["data"])
            else:
                self.assertIn("Model response", result["data"])
            for name in ("weather", "finance", "news"):
                self.assertEqual(reports[-1]["agents"][name], {
                    "status": "SUCCESS", "data": "unchanged agent result"
                })
            os.chdir(previous)

    def test_main_model_response_records_false(self):
        response = Mock(status_code=200)
        response.json.return_value = {"choices": [{"message": {"content": "Model response"}}]}
        self.check_report("fake-test-key", response=response, fallback=False)

    def test_missing_key_records_fallback_true(self):
        self.check_report("", error=AssertionError("API must not be called"), fallback=True)

    def test_failed_http_responses_record_fallback_true(self):
        self.check_report("fake-test-key", response=Mock(status_code=503), fallback=True)

    def test_connection_timeout_records_fallback_true(self):
        self.check_report("fake-test-key", error=requests.Timeout("offline test"), fallback=True)


if __name__ == "__main__":
    unittest.main()
