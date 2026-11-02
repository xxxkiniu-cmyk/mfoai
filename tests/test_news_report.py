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
from agents import finance, news
from core import llm_client


class NewsReportTests(unittest.TestCase):
    def test_full_model_summary_survives_report_save(self):
        summary = "Pełne podsumowanie wiadomości. " * 100 + "NEWS_END_7f92"
        expected = (
            "📰 Wiadomości świat:\n• Pierwszy nagłówek\n• Drugi nagłówek"
            "\n\n🤖 Podsumowanie AI:\n" + summary
        )
        rss = (
            '<rss><channel><title>BBC</title><item><title>Pierwszy nagłówek</title>'
            '</item><item><title>Drugi nagłówek</title></item></channel></rss>'
        ).encode("utf-8")
        response = Mock()
        response.json.return_value = {
            "choices": [{"message": {"content": summary}, "finish_reason": "stop"}]
        }
        original_try_call = main.try_call

        def call_agent(module):
            if module is news:
                return original_try_call(module)
            if module is main.agents.motivator:
                return {"ok": True, "fallback_used": False}
            return "unchanged result"

        historical = [{"agents": {"news": {"status": "SUCCESS", "data": "old"}}}]
        with tempfile.TemporaryDirectory() as directory:
            previous = os.getcwd()
            try:
                os.chdir(directory)
                Path("reports.json").write_text(json.dumps(historical), encoding="utf-8")
                with (
                    patch("socket.socket", side_effect=AssertionError("Network forbidden")),
                    patch.object(news.urllib.request, "urlopen", return_value=io.BytesIO(rss)),
                    patch.object(llm_client, "OPENROUTER_API_KEY", "fake-test-key"),
                    patch.object(llm_client.requests, "post", return_value=response),
                    patch.object(news, "send"),
                    patch.object(main, "try_call", side_effect=call_agent),
                    contextlib.redirect_stdout(io.StringIO()),
                ):
                    main.main()
                reports = json.loads(Path("reports.json").read_text(encoding="utf-8"))
                self.assertEqual(reports[:-1], historical)
                result = reports[-1]["agents"]["news"]
                self.assertEqual(result["status"], "SUCCESS")
                self.assertTrue(result["data"].endswith("NEWS_END_7f92"))
                self.assertEqual(result["data"], expected)
            finally:
                os.chdir(previous)


class FinanceReportTests(unittest.TestCase):
    def run_report(self, response=None, error=None):
        weather_response = Mock()
        weather_response.json.return_value = {"current": {"temperature_2m": 12}}

        def http_get(url, **kwargs):
            if url.startswith("https://api.nbp.pl/"):
                if error is not None:
                    raise error
                return response
            if url.startswith("https://api.open-meteo.com/"):
                return weather_response
            raise AssertionError(f"Unexpected HTTP GET: {url}")

        rss = b'<rss><channel><title>BBC</title><item><title>Offline news</title></item></channel></rss>'
        model_response = Mock()
        model_response.raise_for_status.return_value = None
        model_response.json.return_value = {
            "choices": [{"message": {"content": "Offline summary"}}]
        }
        with tempfile.TemporaryDirectory() as directory:
            previous = os.getcwd()
            try:
                os.chdir(directory)
                with (
                    patch.dict(os.environ, {"OPENROUTER_API_KEY": "", "OPENROUTER_KEY": ""}),
                    patch("socket.socket", side_effect=AssertionError("Network forbidden")),
                    patch.object(finance.requests, "get", side_effect=http_get),
                    patch.object(finance.requests, "post", return_value=model_response),
                    patch.object(news.urllib.request, "urlopen", return_value=io.BytesIO(rss)),
                    patch.object(finance, "send_notification"),
                    patch.object(main.agents.weather, "send_notification"),
                    patch.object(main.agents.motivator, "send_notification"),
                    patch.object(news, "send"),
                    contextlib.redirect_stdout(io.StringIO()),
                ):
                    main.main()
                reports = json.loads(Path("reports.json").read_text(encoding="utf-8"))
                self.assertEqual(len(reports), 1)
                agents = reports[0]["agents"]
                self.assertEqual(agents["news"]["status"], "SUCCESS")
                self.assertIn("Offline news", agents["news"]["data"])
                self.assertEqual(agents["weather"]["status"], "SUCCESS")
                self.assertEqual(agents["motivator"]["status"], "SUCCESS")
                self.assertIs(agents["motivator"]["fallback_used"], True)
                return agents["finance"]
            finally:
                os.chdir(previous)

    def test_finance_http_503_is_reported_as_error(self):
        result = self.run_report(response=Mock(status_code=503))
        self.assertEqual(result["status"], "ERROR")
        self.assertEqual(result["error"], "HTTP 503")

    def test_finance_timeout_is_reported_as_error(self):
        result = self.run_report(error=requests.Timeout("offline timeout"))
        self.assertEqual(result["status"], "ERROR")
        self.assertEqual(result["error"], "offline timeout")

    def test_finance_invalid_json_is_reported_as_error(self):
        response = Mock(status_code=200)
        response.json.side_effect = ValueError("invalid JSON")
        result = self.run_report(response=response)
        self.assertEqual(result["status"], "ERROR")
        self.assertEqual(result["error"], "invalid JSON")

    def test_finance_valid_rates_are_reported_as_success(self):
        response = Mock(status_code=200)
        response.json.return_value = [{"rates": [
            {"code": "EUR", "mid": 4.25}, {"code": "USD", "mid": 3.75},
        ]}]
        result = self.run_report(response=response)
        self.assertEqual(result["status"], "SUCCESS")
        self.assertIn("4.2500 PLN", result["data"])
        self.assertIn("3.7500 PLN", result["data"])


class ReportHistoryTests(unittest.TestCase):
    def setUp(self):
        stack = contextlib.ExitStack()
        self.addCleanup(stack.close)
        directory = stack.enter_context(tempfile.TemporaryDirectory())
        previous = os.getcwd()
        os.chdir(directory)
        stack.callback(os.chdir, previous)
        self.path = Path("reports.json")
        stack.enter_context(patch.object(main, "try_call", return_value={
            "ok": True, "fallback_used": False, "response": "offline"
        }))
        stack.enter_context(patch("socket.socket", side_effect=AssertionError("Network forbidden")))
        stack.enter_context(patch.object(news, "send"))
        stack.enter_context(patch.object(main.agents.motivator, "send_notification"))
        stack.enter_context(contextlib.redirect_stdout(io.StringIO()))

    def assert_original_preserved(self, original):
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(sorted(p.name for p in Path.cwd().iterdir()), ["reports.json"])

    def test_missing_file_creates_one_report(self):
        main.main()
        reports = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(len(reports), 1)
        self.assertEqual(reports[0]["agents"]["news"]["status"], "SUCCESS")
        self.assertEqual(sorted(p.name for p in Path.cwd().iterdir()), ["reports.json"])

    def test_valid_history_is_extended_by_one_report(self):
        history = [{"old": "pierwszy"}, {"old": "drugi"}]
        self.path.write_text(json.dumps(history), encoding="utf-8")
        main.main()
        reports = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(reports[:-1], history)
        self.assertEqual(len(reports), 3)

    def test_corrupt_json_is_not_overwritten_or_disclosed(self):
        original = b'{"private-marker": broken'
        self.path.write_bytes(original)
        with self.assertRaisesRegex(RuntimeError, "reports.json") as raised:
            main.main()
        self.assertNotIn("private-marker", str(raised.exception))
        self.assert_original_preserved(original)

    def test_non_list_json_is_not_overwritten(self):
        for original in (b'{}', b'null', b'"private-marker"', b'42'):
            with self.subTest(original_type=type(json.loads(original)).__name__):
                self.path.write_bytes(original)
                with self.assertRaisesRegex(RuntimeError, "reports.json"):
                    main.main()
                self.assert_original_preserved(original)

    def test_read_failure_does_not_overwrite_history(self):
        original = b'[{"old": true}]\n'
        self.path.write_bytes(original)
        with patch("builtins.open", side_effect=PermissionError("private-marker")):
            with self.assertRaisesRegex(RuntimeError, "reports.json") as raised:
                main.main()
        self.assertNotIn("private-marker", str(raised.exception))
        self.assert_original_preserved(original)

    def test_partial_write_failure_preserves_original_and_cleans_temp(self):
        original = b'[{"old": true}]\n'
        self.path.write_bytes(original)

        def fail_dump(history, output, **kwargs):
            output.write('[{"partial":')
            raise OSError("private-marker")

        with patch.object(main.json, "dump", side_effect=fail_dump):
            with self.assertRaisesRegex(RuntimeError, "reports.json") as raised:
                main.main()
        self.assertNotIn("private-marker", str(raised.exception))
        self.assert_original_preserved(original)

    def test_replace_failure_preserves_original_and_cleans_temp(self):
        original = b'[{"old": true}]\n'
        self.path.write_bytes(original)
        with patch.object(main.os, "replace", side_effect=OSError("private-marker")):
            with self.assertRaisesRegex(RuntimeError, "reports.json") as raised:
                main.main()
        self.assertNotIn("private-marker", str(raised.exception))
        self.assert_original_preserved(original)


if __name__ == "__main__":
    unittest.main()
