import unittest
from datetime import datetime, timezone

from news_pipeline import prepare_candidates


class TestCandidatePreparation(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 11, 1, 12, tzinfo=timezone.utc)
        self.item = {
            'source_type': 'rss', 'source_id': 'feed-1', 'source_item_id': 'article-1',
            'title': 'Build an Agent', 'link': 'https://example.com/agent',
            'summary': 'A practical introduction', 'source_excerpt': 'Example code',
            'content_type': 'tutorial', 'published_at': '2026-10-31T12:00:00Z',
            'status': 'new', 'source_validated': True, 'link_verified': True,
            'tutorial_evidence_verified': True,
        }

    def test_default_auto_mode_selects_only_eligible_new_candidates(self):
        result = prepare_candidates([self.item], now=self.now)
        self.assertEqual(result[0]['decision'], 'publish_ready')
        self.assertNotIn('decision', self.item)

    def test_review_mode_queues_and_does_not_change_pending_on_switch(self):
        pending = {**self.item, 'status': 'pending', 'source_item_id': 'old', 'link': 'https://example.com/old'}
        result = prepare_candidates([self.item, pending], now=self.now, review_required=True)
        self.assertEqual([item['decision'] for item in result], ['queue', 'unchanged'])
        self.assertEqual(prepare_candidates([pending], now=self.now)[0]['decision'], 'unchanged')

    def test_block_rules_and_duplicate_keep_candidates_with_reasons(self):
        repeated = {**self.item, 'source_id': 'other', 'source_item_id': 'other'}
        blocked = {**self.item, 'title': 'Sponsored tutorial', 'source_item_id': 'third', 'link': 'https://example.com/third'}
        result = prepare_candidates([self.item, repeated, blocked], now=self.now,
                                    rules=[{'keyword': 'sponsored', 'content_type': 'tutorial'}])
        self.assertEqual([item['decision'] for item in result], ['publish_ready', 'needs_review', 'blocked'])
        self.assertEqual(result[2]['matched_keywords'], ['sponsored'])

    def test_unknown_dates_unclassified_or_unverified_are_never_auto_published(self):
        for change in ({'published_at': None}, {'content_type': None}, {'link_verified': False},
                       {'source_validated': False}, {'tutorial_evidence_verified': False}, {'summary': ''}):
            with self.subTest(change=change):
                result = prepare_candidates([{**self.item, **change}], now=self.now)
                self.assertEqual(result[0]['decision'], 'needs_review')

    def test_old_items_and_daily_capacity_are_explicit(self):
        old = {**self.item, 'published_at': '2026-10-01T12:00:00Z',
               'source_item_id': 'old', 'link': 'https://example.com/old'}
        result = prepare_candidates([old, self.item], now=self.now, already_published=5)
        self.assertEqual([item['decision'] for item in result], ['stale', 'deferred'])


if __name__ == '__main__':
    unittest.main()
