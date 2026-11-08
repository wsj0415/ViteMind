"""Source adapters for collecting traceable news candidates."""
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from urllib.parse import urlparse

from news_http import safe_news_get as safe_get


class SourceError(RuntimeError):
    """A source failed; it must not be confused with an empty source."""


class SourceCollectionError(SourceError):
    """All sources failed; retain per-source diagnostic status."""

    def __init__(self, statuses):
        super().__init__('All sources failed')
        self.statuses = statuses


class GitHubReleaseSource:
    """Read public stable releases with their source timestamps intact."""

    def __init__(self, repository, request=safe_get, max_pages=5):
        parts = repository.split('/')
        if len(parts) != 2 or any(not p or p in ('.', '..') or not all(c.isalnum() or c in '._-' for c in p) for p in parts):
            raise ValueError('repository must be owner/name')
        self.repository = repository
        self.name = repository
        self.source_type = 'github'
        self.source_id = repository
        self.request = request
        self.max_pages = max_pages

    def collect(self, *, now=None):
        now = now or datetime.now(timezone.utc)
        if now.tzinfo is None:
            raise ValueError('now must include a timezone')
        url = f'https://api.github.com/repos/{self.repository}/releases?per_page=100'
        path = f'/repos/{self.repository}/releases'
        items, seen = [], set()
        for _ in range(self.max_pages):
            parsed = urlparse(url)
            if parsed.scheme != 'https' or parsed.netloc != 'api.github.com' or parsed.path != path:
                raise SourceError('Invalid GitHub pagination URL')
            try:
                response = self.request(url, headers={'Accept': 'application/vnd.github+json', 'User-Agent': 'ViteMind-news'}, timeout=20)
                if response.status_code != 200:
                    raise SourceError(f'GitHub releases returned HTTP {response.status_code}')
                releases = response.json()
                if not isinstance(releases, list):
                    raise SourceError('GitHub releases response is not a list')
                for release in releases:
                    if release.get('draft') or release.get('prerelease') or not release.get('published_at'):
                        continue
                    timestamp = datetime.fromisoformat(release['published_at'].replace('Z', '+00:00'))
                    if timestamp.tzinfo is None or not now - timedelta(hours=24) <= timestamp <= now:
                        continue
                    source_id = str(release['id'])
                    if source_id in seen:
                        continue
                    link = release['html_url']
                    link_parts = urlparse(link)
                    if link_parts.scheme != 'https' or link_parts.netloc != 'github.com' or not link_parts.path.startswith(f'/{self.repository}/releases/'):
                        raise SourceError('Invalid GitHub release URL')
                    seen.add(source_id)
                    items.append({'source_type': 'github', 'source_id': self.repository, 'source_item_id': source_id,
                                  'link': link, 'title': release.get('name') or release.get('tag_name') or 'Release',
                                  'summary_raw': release.get('body') or '', 'published_at': release['published_at'],
                                  'updated_at': None, 'first_seen_at': now.isoformat(), 'content_type': 'technical_update'})
                next_link = response.links.get('next', {}).get('url')
                if not next_link:
                    return items
                url = next_link
            except SourceError:
                raise
            except (KeyError, TypeError, ValueError, OSError) as exc:
                raise SourceError(f'GitHub releases could not be read: {type(exc).__name__}') from exc
        raise SourceError(f'GitHub releases exceeded {self.max_pages} pages')

class RSSSource:
    """Read a configured RSS/Atom feed without modifying source settings."""

    def __init__(self, config, request=safe_get):
        self.config = dict(config)
        self.name = self.config.get('name') or 'RSS source'
        self.source_type = 'rss'
        url = self.config.get('url', '')
        self.source_id = str(self.config['id']) if self.config.get('id') is not None else 'rss:' + sha256(url.encode()).hexdigest()
        self.request = request

    def collect(self, *, now=None):
        import feedparser
        now = now or datetime.now(timezone.utc)
        if now.tzinfo is None:
            raise ValueError('now must include a timezone')
        url = self.config.get('url', '')
        include = [s.strip().casefold() for s in (self.config.get('include_keywords') or '').split(',') if s.strip()]
        exclude = [s.strip().casefold() for s in (self.config.get('exclude_keywords') or '').split(',') if s.strip()]
        try:
            response = self.request(url, headers={'User-Agent': 'ViteMind-news'}, timeout=30)
            if response.status_code != 200:
                raise SourceError(f'RSS returned HTTP {response.status_code}')
            feed = feedparser.parse(response.content)
            if feed.bozo and not feed.entries:
                raise SourceError('RSS could not be parsed')
            results = []
            for entry in feed.entries:
                title, link = entry.get('title', ''), entry.get('link', '')
                if not title or urlparse(link).scheme not in ('http', 'https') or not urlparse(link).hostname:
                    continue
                summary = entry.get('summary', '')
                searchable = (title + ' ' + summary).casefold()
                if any(word in searchable for word in exclude) or (include and not any(word in searchable for word in include)):
                    continue
                def timestamp(field):
                    value = dict.get(entry, field + '_parsed')
                    return datetime(*value[:6], tzinfo=timezone.utc).isoformat() if value else None
                results.append({'source_type': 'rss', 'source_id': self.source_id,
                                'source_name': self.config.get('name') or 'Unknown', 'source_item_id': str(entry.get('id') or link),
                                'title': title, 'link': link, 'summary_raw': summary,
                                'published_at': timestamp('published'), 'updated_at': timestamp('updated'),
                                'first_seen_at': now.isoformat(), 'content_type': None})
            return results
        except SourceError:
            raise
        except (ValueError, TypeError, OSError) as exc:
            raise SourceError(f'RSS could not be read: {type(exc).__name__}') from exc


def collect_sources(sources, *, now=None):
    """Return source-isolated results; fail when no source could be read."""
    now = now or datetime.now(timezone.utc)
    items, statuses = [], []
    for source in sources:
        identity = {'source': source.name, 'source_type': getattr(source, 'source_type', 'unknown'),
                    'source_id': getattr(source, 'source_id', source.name)}
        try:
            found = source.collect(now=now)
            items.extend(found)
            statuses.append({**identity, 'status': 'ok', 'count': len(found)})
        except SourceError as exc:
            statuses.append({**identity, 'status': 'error', 'error': str(exc)})
    if sources and not any(status['status'] == 'ok' for status in statuses):
        raise SourceCollectionError(statuses)
    return items, statuses

class GitHubCookbookSource:
    """Discover changed tutorial files, not commit messages, in one known directory."""

    def __init__(self, repository, directory, keywords=(), request=safe_get, max_pages=3, max_commits=50):
        from urllib.parse import quote
        # Reuse the same repository validation as the release adapter.
        GitHubReleaseSource(repository, request=request)
        parts = directory.split('/')
        if not directory or any(not p or p in ('.', '..') for p in parts):
            raise ValueError('directory must be a relative repository path')
        self.repository, self.directory = repository, directory
        self.name = f'{repository}/{directory}'
        self.source_type = 'github'
        self.source_id = self.name
        self.keywords = tuple(k.casefold() for k in keywords)
        self.request, self.max_pages, self.max_commits = request, max_pages, max_commits
        self.encoded_directory = quote(directory, safe='/')

    def collect(self, *, now=None):
        import re
        from urllib.parse import quote, urlencode
        now = now or datetime.now(timezone.utc)
        if now.tzinfo is None:
            raise ValueError('now must include a timezone')
        path = f'/repos/{self.repository}/commits'
        query = urlencode({'path': self.directory, 'since': (now - timedelta(days=7)).isoformat(), 'per_page': 100})
        url = f'https://api.github.com{path}?{query}'
        headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'ViteMind-news'}
        commits, items, seen = [], [], set()
        try:
            for _ in range(self.max_pages):
                parsed = urlparse(url)
                if parsed.scheme != 'https' or parsed.netloc != 'api.github.com' or parsed.path != path:
                    raise SourceError('Invalid GitHub pagination URL')
                response = self.request(url, headers=headers, timeout=20)
                if response.status_code != 200:
                    raise SourceError(f'GitHub commits returned HTTP {response.status_code}')
                page = response.json()
                if not isinstance(page, list):
                    raise SourceError('GitHub commits response is not a list')
                commits.extend(page)
                if len(commits) > self.max_commits:
                    raise SourceError(f'GitHub commits exceeded {self.max_commits} items')
                url = response.links.get('next', {}).get('url')
                if not url:
                    break
            else:
                raise SourceError(f'GitHub commits exceeded {self.max_pages} pages')
            for commit in commits:
                sha = commit['sha']
                if not re.fullmatch(r'[0-9a-f]{40}', sha):
                    raise SourceError('Invalid GitHub commit ID')
                date_text = commit['commit']['committer']['date']
                date = datetime.fromisoformat(date_text.replace('Z', '+00:00'))
                if date.tzinfo is None or not now - timedelta(days=7) <= date <= now:
                    continue
                detail = self.request(f'https://api.github.com{path}/{sha}?per_page=100', headers=headers, timeout=20)
                if detail.status_code != 200:
                    raise SourceError(f'GitHub commit detail returned HTTP {detail.status_code}')
                if detail.links.get('next'):
                    raise SourceError('GitHub commit detail is paginated; refusing partial result')
                files = detail.json().get('files')
                if not isinstance(files, list):
                    raise SourceError('GitHub commit detail missing files')
                for file in files:
                    name = file.get('filename', '')
                    if file.get('status') not in ('added', 'modified', 'renamed') or not name.startswith(self.directory + '/'):
                        continue
                    if any(part in ('', '.', '..') for part in name.split('/')) or not name.lower().endswith(('.md', '.mdx', '.ipynb')):
                        continue
                    if self.keywords and not any(word in name.casefold() for word in self.keywords):
                        continue
                    if name in seen:
                        continue
                    seen.add(name)
                    items.append({'source_type': 'github', 'source_id': self.repository, 'source_item_id': name,
                                  'link': f'https://github.com/{self.repository}/blob/{sha}/{quote(name, safe="/")}',
                                  'title': name.rsplit('/', 1)[-1].rsplit('.', 1)[0].replace('_', ' '),
                                  'summary_raw': '', 'published_at': None, 'updated_at': date_text,
                                  'first_seen_at': now.isoformat(), 'content_type': None,
                                  'suggested_content_type': 'tutorial'})
            return items
        except SourceError:
            raise
        except (KeyError, TypeError, ValueError, OSError) as exc:
            raise SourceError(f'GitHub cookbook could not be read: {type(exc).__name__}') from exc
