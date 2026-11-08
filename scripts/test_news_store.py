import unittest
from datetime import datetime, timezone
from types import SimpleNamespace

from news_store import SupabaseNewsStore


class FakeClient:
    def __init__(self): self.calls, self.results = [], {}
    def rpc(self, name, params):
        self.calls.append((name, params))
        return SimpleNamespace(execute=lambda: SimpleNamespace(data=self.results[name]))
    def table(self, name):
        def insert(rows):
            self.calls.append((name, rows))
            return SimpleNamespace(execute=lambda: SimpleNamespace(data=rows))
        return SimpleNamespace(insert=insert)


class TestSupabaseNewsStore(unittest.TestCase):
    def setUp(self):
        self.client = FakeClient()
        self.store = SupabaseNewsStore(self.client, now=datetime(2026, 11, 1, tzinfo=timezone.utc))

    def test_settings_require_explicit_database_response(self):
        self.client.results['news_ingestion_config'] = {'review_required': False, 'rules': []}
        self.assertFalse(self.store.settings()['review_required'])
        self.client.results['news_ingestion_config'] = None
        with self.assertRaises(ValueError): self.store.settings()

    def test_import_and_finalize_share_token_and_strip_unknown_fields(self):
        self.client.results['news_ingest_candidates'] = ['one']
        self.client.results['news_finalize_candidates'] = 1
        self.assertEqual(self.store.insert_new([{'candidate_id': 'one', 'title': 'x'}]), ['one'])
        self.store.save_prepared([{'candidate_id': 'one', 'title': 'y', 'status': 'new', 'link': 'https://evil.example', 'unexpected': 'x'}])
        ingest, finalize = self.client.calls
        self.assertEqual(ingest[1]['p_token'], finalize[1]['p_token'])
        self.assertNotIn('link', finalize[1]['p_items'][0])
        self.assertNotIn('unexpected', finalize[1]['p_items'][0])

    def test_failed_finalize_or_incomplete_publish_cannot_look_successful(self):
        self.client.results['news_finalize_candidates'] = 0
        with self.assertRaises(RuntimeError): self.store.save_prepared([{'candidate_id': 'one', 'status': 'pending'}])
        self.client.results['news_publish_candidates'] = []
        with self.assertRaises(RuntimeError): self.store.publish_automatic(['one'])

    def test_failure_logs_do_not_persist_source_exception_text(self):
        self.store.record_runs([{'source': 'feed', 'status': 'error', 'error': 'token=secret'}])
        self.assertNotIn('secret', str(self.client.calls))


if __name__ == '__main__': unittest.main()
