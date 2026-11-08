import unittest

from news_model_output import validate_model_output


class TestModelOutput(unittest.TestCase):
    def setUp(self):
        self.source = {'candidate_id': 'a', 'link': 'https://example.com/a',
                       'published_at': '2026-10-31T12:00:00Z', 'updated_at': None,
                       'tutorial_evidence_verified': False}
        self.output = {'candidate_id': 'a', 'title': '技术更新', 'summary': '简要说明',
                       'detail': '依据原文说明。', 'content_type': 'technical_update'}

    def test_link_and_dates_are_copied_from_original(self):
        accepted, errors = validate_model_output([self.source], [self.output])
        self.assertEqual(errors, [])
        self.assertEqual(accepted[0]['link'], self.source['link'])
        self.assertEqual(accepted[0]['published_at'], self.source['published_at'])

    def test_changed_link_or_date_and_unknown_candidate_are_rejected(self):
        for change in ({'link': 'https://evil.example/a'}, {'published_at': '2026-11-01T00:00:00Z'},
                       {'candidate_id': 'unknown'}):
            with self.subTest(change=change):
                accepted, errors = validate_model_output([self.source], [{**self.output, **change}])
                self.assertEqual(accepted, [])
                self.assertTrue(errors)

    def test_tutorial_label_requires_independent_evidence(self):
        accepted, _ = validate_model_output([self.source], [{**self.output, 'content_type': 'tutorial'}])
        self.assertIsNone(accepted[0]['content_type'])
        self.assertEqual(accepted[0]['suggested_content_type'], 'tutorial')

    def test_duplicate_and_invalid_items_do_not_hide_valid_items(self):
        accepted, errors = validate_model_output([self.source], [self.output, self.output, {'candidate_id': 'missing'}])
        self.assertEqual(len(accepted), 1)
        self.assertEqual(len(errors), 2)

    def test_malformed_response_and_ambiguous_candidate_ids_fail_closed(self):
        with self.assertRaises(ValueError):
            validate_model_output([self.source], {'unexpected': 'object'})
        with self.assertRaises(ValueError):
            validate_model_output([self.source, self.source], [self.output])

    def test_malformed_category_is_rejected_without_crashing(self):
        accepted, errors = validate_model_output([self.source], [{**self.output, 'content_type': []}])
        self.assertEqual(accepted, [])
        self.assertEqual(len(errors), 1)
