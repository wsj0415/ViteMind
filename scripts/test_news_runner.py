import unittest
from datetime import datetime, timezone

from news_runner import run_news_cycle
from news_sources import SourceError


class Source:
    name = 'feed'
    def collect(self, *, now):
        return [{'source_type': 'rss', 'source_id': 'feed', 'source_item_id': 'one',
                 'title': 'Agent', 'link': 'https://example.com/a', 'summary_raw': 'example',
                 'published_at': '2026-11-01T10:00:00Z', 'updated_at': None}]


class Store:
    def __init__(self, review=False):
        self.review, self.rows, self.runs, self.published = review, {}, [], []
    def settings(self): return {'review_required': self.review, 'rules': [], 'already_published': 0, 'opinions_published': 0}
    def record_runs(self, statuses): self.runs.extend(statuses)
    def insert_new(self, rows):
        inserted = []
        for row in rows:
            if row['candidate_id'] not in self.rows:
                self.rows[row['candidate_id']] = dict(row)
                inserted.append(row['candidate_id'])
        return inserted
    def save_prepared(self, rows):
        for row in rows: self.rows[row['candidate_id']] = dict(row)
    def publish_automatic(self, ids): self.published.extend(ids)


def enrich(item):
    return {'source_excerpt': 'example', 'source_validated': True, 'link_verified': True,
            'tutorial_evidence_verified': False}


def summarize(items):
    return [{'candidate_id': item['candidate_id'], 'title': 'Agent 更新', 'summary': '摘要',
             'detail': '详情', 'content_type': 'technical_update'} for item in items]


class TestNewsRunner(unittest.TestCase):
    def setUp(self): self.now = datetime(2026, 11, 1, 12, tzinfo=timezone.utc)

    def test_auto_mode_persists_and_publishes_new_validated_items(self):
        store = Store()
        result = run_news_cycle([Source()], store, enrich=enrich, summarize=summarize, now=self.now)
        self.assertEqual(result['published_count'], 1)
        self.assertEqual(len(store.published), 1)
        self.assertEqual(list(store.rows.values())[0]['status'], 'new')

    def test_manual_review_keeps_candidate_and_never_publishes(self):
        store = Store(review=True)
        run_news_cycle([Source()], store, enrich=enrich, summarize=summarize, now=self.now)
        self.assertEqual(store.published, [])
        self.assertEqual(list(store.rows.values())[0]['status'], 'pending')

    def test_repeat_run_does_not_change_existing_pending_after_switch(self):
        store = Store(review=True)
        run_news_cycle([Source()], store, enrich=enrich, summarize=summarize, now=self.now)
        store.review = False
        result = run_news_cycle([Source()], store, enrich=enrich, summarize=summarize, now=self.now)
        self.assertEqual(result['new_count'], 0)
        self.assertEqual(store.published, [])
        self.assertEqual(list(store.rows.values())[0]['status'], 'pending')

    def test_model_failure_leaves_raw_candidate_pending(self):
        store = Store()
        def broken(_): raise RuntimeError('model unavailable')
        with self.assertRaises(RuntimeError):
            run_news_cycle([Source()], store, enrich=enrich, summarize=broken, now=self.now)
        self.assertEqual(list(store.rows.values())[0]['status'], 'pending')
        self.assertEqual(store.published, [])

    def test_failed_sources_are_recorded_and_not_reported_as_empty(self):
        class Broken:
            name = 'broken'
            def collect(self, *, now): raise SourceError('unavailable')
        store = Store()
        with self.assertRaises(SourceError):
            run_news_cycle([Broken()], store, enrich=enrich, summarize=summarize, now=self.now)
        self.assertEqual(store.runs[0]['status'], 'error')

    def test_enrichment_cannot_replace_source_identity_link_or_dates(self):
        store = Store()
        def forged(item):
            return {**enrich(item), 'link': 'https://evil.example', 'source_id': 'forged',
                    'published_at': '2030-01-01T00:00:00Z'}
        run_news_cycle([Source()], store, enrich=forged, summarize=summarize, now=self.now)
        item = list(store.rows.values())[0]
        self.assertEqual(item['link'], 'https://example.com/a')
        self.assertEqual(item['source_id'], 'feed')
        self.assertEqual(item['published_at'], '2026-11-01T10:00:00Z')

    def test_absent_review_setting_never_defaults_to_auto(self):
        class BrokenStore(Store):
            def settings(self): return {}
        with self.assertRaises(ValueError):
            run_news_cycle([Source()], BrokenStore(), enrich=enrich, summarize=summarize, now=self.now)

    def test_enrichment_failure_is_reported_and_raw_candidate_is_kept(self):
        def broken(_): raise RuntimeError('private detail should not appear')
        store = Store()
        result = run_news_cycle([Source()], store, enrich=broken, summarize=summarize, now=self.now)
        self.assertEqual(result['enrichment_errors'][0]['error_type'], 'RuntimeError')
        self.assertNotIn('private detail', str(result))
        self.assertEqual(list(store.rows.values())[0]['status'], 'pending')

    def test_model_omission_is_reported_not_confused_with_no_new_content(self):
        store = Store()
        result = run_news_cycle([Source()], store, enrich=enrich, summarize=lambda _: [], now=self.now)
        self.assertEqual(result['new_count'], 1)
        self.assertEqual(result['model_errors'][0]['reason'], 'candidate omitted')
        self.assertEqual(list(store.rows.values())[0]['status'], 'pending')

    def test_malformed_item_does_not_discard_other_items(self):
        class Mixed(Source):
            def collect(self, *, now):
                return [{'title': 'missing identity'}, *super().collect(now=now)]
        store = Store()
        result = run_news_cycle([Mixed()], store, enrich=enrich, summarize=summarize, now=self.now)
        self.assertEqual(result['new_count'], 1)
        self.assertEqual(result['published_count'], 1)
        self.assertEqual(result['candidate_errors'], [{'index': 0, 'reason': 'invalid source item'}])


if __name__ == '__main__': unittest.main()
