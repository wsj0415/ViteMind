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

class TestReviewValidation(unittest.TestCase):
    candidate = {"link": "https://example.com/a", "date": "2026-10-31", "summary": "Evidence", "source_quality": "rss_summary"}
    item = {"link": "https://example.com/a", "date": "1999-01-01", "title": "标题", "summary": "摘要", "detail": "正文", "tags": ["News"]}

    def test_source_date_overrides_model_and_items_start_pending(self):
        result = generate_news.validate_insights([self.item], [self.candidate])
        self.assertEqual(result[0]["date"], "2026-10-31")
        self.assertEqual(result[0]["review_status"], "pending")

    def test_rejects_unknown_and_duplicate_links(self):
        with self.assertRaises(ValueError):
            generate_news.validate_insights([{**self.item, "link": "https://wrong.example/"}], [self.candidate])
        with self.assertRaises(ValueError):
            generate_news.validate_insights([self.item, self.item], [self.candidate])

    def test_invalid_output_does_not_pass(self):
        with self.assertRaises(ValueError):
            generate_news.validate_insights([{**self.item, "tags": "News"}], [self.candidate])

class TestReviewPublication(unittest.TestCase):
    def test_only_approved_items_are_published(self):
        import json
        import tempfile
        from pathlib import Path
        base = {"date": "2026-10-31", "title": "标题", "summary": "摘要", "detail": "正文", "tags": ["News"]}
        items = [{**base, "link": "https://example.com/a", "review_status": "approved"},
                 {**base, "link": "https://example.com/b", "review_status": "pending"},
                 {**base, "link": "https://example.com/c", "review_status": "rejected"}]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'draft.json'
            path.write_text(json.dumps({"version": 1, "items": items}), encoding='utf-8')
            with patch.object(generate_news, 'archive_history') as archive:
                generate_news.publish_approved(path)
                self.assertEqual([i['link'] for i in archive.call_args.args[0]], ['https://example.com/a'])

    @patch('generate_news.safe_get', side_effect=OSError('unavailable'))
    def test_all_feed_failures_do_not_report_no_news(self, get):
        with patch.dict('os.environ', {'SUPABASE_URL': '', 'SUPABASE_KEY': '', 'SUPABASE_SERVICE_ROLE_KEY': ''}):
            with self.assertRaisesRegex(RuntimeError, 'All RSS feeds failed'):
                generate_news.fetch_rss_data(set())
