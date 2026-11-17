"""Offline notification contracts: no business API, model, or socket access."""

import contextlib
import io
import os
import unittest
from unittest.mock import Mock, patch

import requests

from agents import finance, motivator, weather


_SOCKET_PATCHES = []


def setUpModule():
    # Module-wide guard also catches accidental I/O outside an individual test.
    for target in ("socket.socket", "socket.create_connection"):
        guard = patch(target, side_effect=AssertionError("Network forbidden"))
        _SOCKET_PATCHES.append((guard, guard.start()))


def tearDownModule():
    try:
        for _, guard in _SOCKET_PATCHES:
            guard.assert_not_called()
    finally:
        for guard, _ in reversed(_SOCKET_PATCHES):
            guard.stop()
        _SOCKET_PATCHES.clear()


class NotificationTimeoutTests(unittest.TestCase):
    CASES = (
        (motivator, "Zażółć gęślą jaźń!", "💪 Motywacja dnia:\nZażółć gęślą jaźń!", {
            "Title": "MFO.ai - Motivator", "Priority": "default", "Tags": "fire,muscle"
        }),
        (finance, {"ok": True, "EUR": "4.1234 PLN", "USD": "3.9876 PLN"},
         "📊 Kursy walut (NBP):\n💶 EUR: 4.1234 PLN\n💵 USD: 3.9876 PLN", {
             "Title": "MFO.ai - Finance", "Priority": "low",
             "Tags": "chart_with_upwards_trend,moneybag"
         }),
        (weather, "Temp: 12°C | Opady: 0 mm", "🌤️ Prognoza Pogody:\nTemp: 12°C | Opady: 0 mm", {
            "Title": "MFO.ai - Weather Agent", "Priority": "default"
        }),
    )

    def setUp(self):
        self.enterContext(contextlib.redirect_stdout(io.StringIO()))
        self.enterContext(patch.dict(os.environ, {}, clear=True))
        # Only the mocked notification POST is allowed. Business GETs are forbidden.
        self.get = self.enterContext(patch.object(
            requests, "get", side_effect=AssertionError("Business API forbidden")
        ))
        self.addCleanup(self.get.assert_not_called)

    def assert_post(self, post, body, headers, topic="mfoai_bot_alerts"):
        post.assert_called_once_with(
            f"https://ntfy.sh/{topic}", data=body.encode("utf-8"),
            headers=headers, timeout=10,
        )
        self.assertIs(type(post.call_args.kwargs["timeout"]), int)

    @staticmethod
    def response(status):
        response = requests.Response()
        response.status_code = status
        response.url = "https://ntfy.sh/offline-test"
        response.raise_for_status = Mock(wraps=response.raise_for_status)
        return response

    def test_success_preserves_request_and_checks_status_for_default_and_configured_topic(self):
        for module, message, body, headers in self.CASES:
            for topic in (None, "offline-custom-topic"):
                with self.subTest(agent=module.__name__, topic=topic):
                    if topic is None:
                        os.environ.pop("NTFY_TOPIC", None)
                    else:
                        os.environ["NTFY_TOPIC"] = topic
                    response = self.response(200)
                    with patch.object(requests, "post", return_value=response) as post:
                        self.assertIsNone(module.send_notification(message))
                    self.assert_post(post, body, headers, topic or "mfoai_bot_alerts")
                    response.raise_for_status.assert_called_once_with()

    def test_timeout_is_caught_for_every_agent(self):
        for module, message, body, headers in self.CASES:
            with self.subTest(agent=module.__name__):
                with patch.object(requests, "post", side_effect=requests.Timeout("offline timeout")) as post:
                    self.assertIsNone(module.send_notification(message))
                self.assert_post(post, body, headers)

    def test_real_http_503_status_check_is_called_and_error_is_caught(self):
        for module, message, body, headers in self.CASES:
            with self.subTest(agent=module.__name__):
                response = self.response(503)
                with self.assertRaises(requests.HTTPError):
                    response.raise_for_status()
                response.raise_for_status.reset_mock()
                with patch.object(requests, "post", return_value=response) as post:
                    self.assertIsNone(module.send_notification(message))
                self.assert_post(post, body, headers)
                response.raise_for_status.assert_called_once_with()

    def test_run_retains_successful_business_result_despite_notification_timeout(self):
        self.check_runs(notification_timeout=True)

    def test_run_retains_successful_business_result_despite_notification_http_503(self):
        self.check_runs(notification_timeout=False)

    def check_runs(self, notification_timeout):
        motivation = {
            "ok": True, "model": "offline-model", "fallback_used": False,
            "latency": "0.1s", "response": self.CASES[0][1],
        }
        for module, fetch_name, result, case in (
            (motivator, "get_motivation", motivation, self.CASES[0]),
            (finance, "fetch_rates", dict(self.CASES[1][1]), self.CASES[1]),
        ):
            with self.subTest(agent=module.__name__):
                original = result.copy()
                response = self.response(503)
                with (
                    patch.object(module, fetch_name, return_value=result) as fetch,
                    patch.object(requests, "post", return_value=response,
                                 side_effect=requests.Timeout("offline timeout") if notification_timeout else None) as post,
                ):
                    actual = module.run()
                self.assertIs(actual, result)
                self.assertEqual(actual, original)
                fetch.assert_called_once_with()
                self.assert_post(post, case[2], case[3])
                if notification_timeout:
                    response.raise_for_status.assert_not_called()
                else:
                    response.raise_for_status.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
