import unittest
from datetime import datetime, timezone
from types import SimpleNamespace

from news_sources import GitHubReleaseSource, SourceError


class TestGitHubReleaseSource(unittest.TestCase):
    def test_only_recent_stable_releases_and_source_dates_survive(self):
        now = datetime(2026, 11, 1, 12, tzinfo=timezone.utc)
        release = {'id': 42, 'name': 'v1', 'html_url': 'https://github.com/example/project/releases/tag/v1',
                   'published_at': '2026-11-01T10:00:00Z', 'created_at': '2026-10-31T00:00:00Z',
                   'body': 'New agent capability', 'draft': False, 'prerelease': False}
        response = SimpleNamespace(status_code=200, json=lambda: [release, {**release, 'id': 43, 'prerelease': True}], links={})
        source = GitHubReleaseSource('example/project', request=lambda *a, **k: response)
        items = source.collect(now=now)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['published_at'], '2026-11-01T10:00:00Z')
        self.assertEqual(items[0]['updated_at'], None)
        self.assertEqual(items[0]['source_type'], 'github')
        self.assertEqual(items[0]['source_item_id'], '42')

    def test_failed_source_is_reported_not_empty(self):
        source = GitHubReleaseSource('example/project', request=lambda *a, **k: SimpleNamespace(status_code=403))
        with self.assertRaises(SourceError):
            source.collect(now=datetime(2026, 11, 1, tzinfo=timezone.utc))

    def test_follow_pagination_and_deduplicate_release_ids(self):
        release = {'id': 42, 'name': 'v1', 'html_url': 'https://github.com/example/project/releases/tag/v1',
                   'published_at': '2026-11-01T10:00:00Z', 'body': 'x', 'draft': False, 'prerelease': False}
        pages = iter([SimpleNamespace(status_code=200, json=lambda: [release], links={'next': {'url': 'https://api.github.com/repos/example/project/releases?page=2'}}),
                      SimpleNamespace(status_code=200, json=lambda: [release], links={})])
        source = GitHubReleaseSource('example/project', request=lambda *a, **k: next(pages))
        self.assertEqual(len(source.collect(now=datetime(2026,11,1,12,tzinfo=timezone.utc))), 1)

class TestRSSSource(unittest.TestCase):
    def test_feed_without_database_id_does_not_expose_url_secret_in_source_id(self):
        from news_sources import RSSSource
        body = b'<rss version="2.0"><channel><title>Feed</title><link>https://example.com</link><description>Feed</description><item><title>Agent</title><link>https://example.com/a</link></item></channel></rss>'
        response = SimpleNamespace(status_code=200, content=body)
        source = RSSSource({'url': 'https://example.com/feed?token=supersecret'}, request=lambda *a, **k: response)
        item = source.collect(now=datetime(2026, 11, 1, tzinfo=timezone.utc))[0]
        self.assertNotIn('supersecret', item['source_id'])
        self.assertTrue(item['source_id'].startswith('rss:'))

    def test_preserves_original_dates_and_existing_keyword_filters(self):
        from news_sources import RSSSource
        body = b'''<?xml version="1.0"?><rss version="2.0"><channel><title>Feed</title><link>https://example.com</link><description>Feed</description><item><title>Agent tutorial</title><link>https://example.com/a</link><description>Practical example</description><pubDate>Sat, 31 Oct 2026 12:00:00 GMT</pubDate></item><item><title>Agent advert</title><link>https://example.com/b</link><description>Spam</description></item></channel></rss>'''
        response = SimpleNamespace(status_code=200, content=body)
        config = {'id': 7, 'name': 'Feed', 'url': 'https://example.com/feed', 'include_keywords': 'agent', 'exclude_keywords': 'advert'}
        items = RSSSource(config, request=lambda *a, **k: response).collect(now=datetime(2026,11,1,tzinfo=timezone.utc))
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['source_id'], '7')
        self.assertEqual(items[0]['published_at'], '2026-10-31T12:00:00+00:00')
        self.assertIsNone(items[0]['updated_at'])
        self.assertEqual(items[0]['source_type'], 'rss')

    def test_unknown_published_date_does_not_become_updated_date(self):
        from news_sources import RSSSource
        body = b'''<feed xmlns="http://www.w3.org/2005/Atom"><title>Feed</title><id>f</id><updated>2026-10-31T12:00:00Z</updated><entry><title>Agent example</title><id>a</id><link href="https://example.com/a"/><updated>2026-10-31T12:00:00Z</updated></entry></feed>'''
        response = SimpleNamespace(status_code=200, content=body)
        item = RSSSource({'url': 'https://example.com/feed'}, request=lambda *a, **k: response).collect(now=datetime(2026,11,1,tzinfo=timezone.utc))[0]
        self.assertIsNone(item['published_at'])
        self.assertEqual(item['updated_at'], '2026-10-31T12:00:00+00:00')

class TestSourceCollection(unittest.TestCase):
    def test_one_failure_does_not_hide_other_source_results(self):
        from news_sources import collect_sources
        class Source:
            def __init__(self, name, result): self.name, self.result = name, result
            def collect(self, *, now):
                if isinstance(self.result, Exception): raise self.result
                return self.result
        now = datetime(2026, 11, 1, tzinfo=timezone.utc)
        items, statuses = collect_sources([Source('broken', SourceError('HTTP 404')), Source('healthy', [{'title': 'Example'}])], now=now)
        self.assertEqual(items, [{'title': 'Example'}])
        self.assertEqual([s['status'] for s in statuses], ['error', 'ok'])

    def test_every_source_failing_is_not_an_empty_success(self):
        from news_sources import collect_sources
        class Failed:
            name = 'broken'
            def collect(self, *, now): raise SourceError('unavailable')
        with self.assertRaises(SourceError) as error:
            collect_sources([Failed()], now=datetime(2026,11,1,tzinfo=timezone.utc))
        self.assertEqual(error.exception.statuses[0]['error'], 'unavailable')

class TestGitHubCookbookSource(unittest.TestCase):
    def test_changed_tutorial_file_is_candidate_without_fabricated_publish_date(self):
        from news_sources import GitHubCookbookSource
        now = datetime(2026, 11, 1, 12, tzinfo=timezone.utc)
        sha = 'a' * 40
        commit = {'sha': sha, 'commit': {'committer': {'date': '2026-10-31T12:00:00Z'}}}
        detail = {'files': [{'filename': 'examples/agent_basics.ipynb', 'status': 'added'},
                            {'filename': 'examples/misc.md', 'status': 'modified'},
                            {'filename': 'examples/agent_deleted.ipynb', 'status': 'removed'}]}
        pages = iter([SimpleNamespace(status_code=200, json=lambda: [commit], links={}),
                      SimpleNamespace(status_code=200, json=lambda: detail, links={})])
        source = GitHubCookbookSource('example/cookbook', 'examples', ('agent', 'rag'), request=lambda *a, **k: next(pages))
        items = source.collect(now=now)
        self.assertEqual(len(items), 1)
        self.assertIsNone(items[0]['published_at'])
        self.assertEqual(items[0]['updated_at'], '2026-10-31T12:00:00Z')
        self.assertIsNone(items[0]['content_type'])
        self.assertEqual(items[0]['suggested_content_type'], 'tutorial')
        self.assertEqual(items[0]['source_item_id'], 'examples/agent_basics.ipynb')

    def test_truncated_commit_detail_is_not_silently_accepted(self):
        from news_sources import GitHubCookbookSource
        sha = 'b' * 40
        commit = {'sha': sha, 'commit': {'committer': {'date': '2026-10-31T12:00:00Z'}}}
        pages = iter([SimpleNamespace(status_code=200, json=lambda: [commit], links={}),
                      SimpleNamespace(status_code=200, json=lambda: {'files': []}, links={'next': {'url': 'https://api.github.com/next'}})])
        source = GitHubCookbookSource('example/cookbook', 'examples', ('agent',), request=lambda *a, **k: next(pages))
        with self.assertRaises(SourceError):
            source.collect(now=datetime(2026,11,1,12,tzinfo=timezone.utc))
