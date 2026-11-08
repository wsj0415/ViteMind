import unittest
from news_rules import apply_blocklist, choose_publication


class TestNewsRules(unittest.TestCase):
    def test_keyword_matching_is_literal_case_insensitive_and_type_specific(self):
        item = {'title': 'AGENT 报告: 广告', 'summary': '', 'source_excerpt': '', 'content_type': 'tutorial'}
        rules = [{'keyword': '广告', 'enabled': True, 'content_type': 'tutorial'},
                 {'keyword': 'agent', 'enabled': True, 'content_type': 'opinion'}]
        self.assertEqual(apply_blocklist(item, rules), ['广告'])
        self.assertEqual(apply_blocklist({**item, 'content_type': 'opinion'}, rules), ['agent'])

    def test_disabled_and_empty_rules_do_not_block(self):
        item = {'title': 'Test', 'content_type': 'technical_update'}
        self.assertEqual(apply_blocklist(item, [{'keyword': 'test', 'enabled': False}, {'keyword': '  ', 'enabled': True}]), [])

    def test_auto_mode_limits_publication_and_opinions(self):
        items = [{'id': str(i), 'content_type': 'opinion' if i < 2 else 'tutorial', 'status': 'new'} for i in range(9)]
        result = choose_publication(items, review_required=False)
        self.assertEqual([x['id'] for x in result], ['0', '2', '3', '4', '5'])

    def test_manual_mode_and_non_new_items_do_not_publish(self):
        items = [{'id': 'a', 'content_type': 'tutorial', 'status': 'new'}, {'id': 'b', 'content_type': 'tutorial', 'status': 'pending'}]
        self.assertEqual(choose_publication(items, review_required=True), [])
        self.assertEqual([x['id'] for x in choose_publication(items, review_required=False)], ['a'])

class TestFreshness(unittest.TestCase):
    def test_technical_updates_use_24_hours_and_tutorials_use_seven_days(self):
        from news_rules import is_fresh
        from datetime import datetime, timezone
        now = datetime(2026, 11, 1, 12, tzinfo=timezone.utc)
        item = {'published_at': '2026-10-30T12:00:00Z', 'updated_at': None, 'first_seen_at': '2026-11-01T12:00:00Z'}
        self.assertFalse(is_fresh({**item, 'content_type': 'technical_update'}, now))
        self.assertTrue(is_fresh({**item, 'content_type': 'tutorial'}, now))

    def test_unknown_publication_date_uses_update_without_fabricating_date(self):
        from news_rules import is_fresh
        from datetime import datetime, timezone
        now = datetime(2026, 11, 1, 12, tzinfo=timezone.utc)
        item = {'published_at': None, 'updated_at': '2026-10-31T12:00:00Z', 'first_seen_at': '2026-11-01T12:00:00Z', 'content_type': 'tutorial'}
        self.assertTrue(is_fresh(item, now))
        self.assertIsNone(item['published_at'])

    def test_future_source_date_is_not_clamped(self):
        from news_rules import is_fresh
        from datetime import datetime, timezone
        item = {'published_at': '2026-12-01T00:00:00Z', 'content_type': 'technical_update'}
        self.assertFalse(is_fresh(item, datetime(2026,11,1,tzinfo=timezone.utc)))
        self.assertEqual(item['published_at'], '2026-12-01T00:00:00Z')

class TestPublicationSafety(unittest.TestCase):
    def test_unclassified_items_are_not_auto_published(self):
        item = {'id': 'a', 'status': 'new', 'content_type': None}
        self.assertEqual(choose_publication([item], review_required=False), [])

    def test_exact_duplicate_links_are_flagged_without_losing_sources(self):
        from news_rules import flag_exact_duplicates
        items = [
            {'source_id': '1', 'source_item_id': 'a', 'link': 'https://EXAMPLE.com/article#section'},
            {'source_id': '2', 'source_item_id': 'b', 'link': 'https://example.com/article'},
            {'source_id': '3', 'source_item_id': 'c', 'link': 'https://example.com/article?version=2'},
        ]
        result = flag_exact_duplicates(items)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[1]['duplicate_of'], 0)
        self.assertNotIn('duplicate_of', result[2])
        self.assertNotIn('duplicate_of', items[1])

    def test_auto_selection_rejects_blocked_and_possible_duplicates(self):
        items = [
            {'id': 'a', 'title': 'Sponsored AI', 'content_type': 'tutorial', 'status': 'new'},
            {'id': 'b', 'title': 'Original', 'content_type': 'tutorial', 'status': 'new', 'duplicate_suspected': True},
            {'id': 'c', 'title': 'Useful', 'content_type': 'project', 'status': 'new'},
        ]
        result = choose_publication(items, review_required=False, rules=[{'keyword': 'sponsored', 'enabled': True}])
        self.assertEqual([i['id'] for i in result], ['c'])

    def test_daily_remaining_capacity_and_opinion_limit_apply_across_runs(self):
        items = [{'id': 'a', 'status': 'new', 'content_type': 'opinion'},
                 {'id': 'b', 'status': 'new', 'content_type': 'project'},
                 {'id': 'c', 'status': 'new', 'content_type': 'tutorial'}]
        result = choose_publication(items, review_required=False, already_published=4, opinions_published=1)
        self.assertEqual([i['id'] for i in result], ['b'])
