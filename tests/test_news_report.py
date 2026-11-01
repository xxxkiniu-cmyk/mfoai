import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import main
from agents import news
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


if __name__ == "__main__":
    unittest.main()
