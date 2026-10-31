import unittest
from types import SimpleNamespace
from unittest.mock import patch

import httpx
from openai import AuthenticationError, PermissionDeniedError

# Keep tests independent of local credentials and external services.
with patch("dotenv.load_dotenv", return_value=False):
    import generate_news


class TestNewsGeneration(unittest.TestCase):
    articles = [{
        "date": "2026-10-31", "title": "Example",
        "link": "https://example.com/news", "summary": "Source text",
    }]

    @patch("time.sleep")
    @patch("openai.OpenAI")
    def test_authentication_failures_stop_without_retry(self, client, sleep):
        create = client.return_value.chat.completions.create
        for code, error_type in [(401, AuthenticationError), (403, PermissionDeniedError)]:
            with self.subTest(status=code):
                create.reset_mock()
                response = httpx.Response(code, request=httpx.Request("POST", "https://example.com"))
                create.side_effect = error_type("Account verification required", response=response, body=None)
                with self.assertRaisesRegex(RuntimeError, f"HTTP {code}"):
                    generate_news.distill_wisdom(self.articles)
                create.assert_called_once()
        sleep.assert_not_called()

    @patch("time.sleep")
    @patch("openai.OpenAI")
    def test_exhausted_retries_fail_instead_of_returning_empty_news(self, client, sleep):
        create = client.return_value.chat.completions.create
        create.side_effect = RuntimeError("Service unavailable")
        with self.assertRaisesRegex(RuntimeError, "failed after 3 attempts"):
            generate_news.distill_wisdom(self.articles)
        self.assertEqual(create.call_count, 3)
        self.assertEqual(sleep.call_count, 2)

    @patch("openai.OpenAI")
    def test_valid_json_is_returned_including_legitimate_empty_selection(self, client):
        create = client.return_value.chat.completions.create
        for content, expected in [('[]', []), ('[{"title": "Example"}]', [{"title": "Example"}])]:
            with self.subTest(content=content):
                create.return_value = SimpleNamespace(choices=[SimpleNamespace(
                    message=SimpleNamespace(content=content)
                )])
                self.assertEqual(generate_news.distill_wisdom(self.articles), expected)


if __name__ == "__main__":
    unittest.main()
