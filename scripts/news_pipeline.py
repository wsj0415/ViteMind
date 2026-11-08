"""Prepare candidate decisions without writing or authorizing publication.

Validation flags must come from trusted checks, never from a source or a model.
The final publish operation must recheck current settings and limits atomically.
"""

from datetime import datetime
from urllib.parse import urlsplit

from news_rules import apply_blocklist, choose_publication, flag_exact_duplicates, is_fresh


def _timestamp_status(item, now):
    kind = item.get('content_type')
    timestamp = item.get('published_at') if kind == 'technical_update' else item.get('updated_at') or item.get('published_at')
    try:
        value = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        if value.tzinfo is None or value > now:
            return 'unknown'
    except (AttributeError, TypeError, ValueError):
        return 'unknown'
    return 'fresh' if is_fresh(item, now) else 'stale'


def _usable_link(value):
    try:
        link = urlsplit(value)
        return link.scheme in ('http', 'https') and bool(link.hostname) and not link.username and not link.password
    except (TypeError, ValueError):
        return False


def prepare_candidates(items, *, now, review_required=False, rules=(), already_published=0, opinions_published=0):
    """Classify every candidate; a result is not a database publication permit."""
    if now.tzinfo is None:
        raise ValueError('now must include a timezone')
    candidates = flag_exact_duplicates(items)
    eligible = []
    for item in candidates:
        item['matched_keywords'] = apply_blocklist(item, rules)
        if item.get('status') != 'new':
            item['decision'] = 'unchanged'
            continue
        if item['matched_keywords']:
            item['decision'] = 'blocked'
            continue
        kind = item.get('content_type')
        basic = (kind in ('technical_update', 'tutorial', 'project', 'opinion')
                 and all(item.get(field) for field in ('source_type', 'source_id', 'source_item_id', 'title', 'summary', 'source_excerpt'))
                 and _usable_link(item.get('link'))
                 and item.get('source_validated') is True and item.get('link_verified') is True
                 and (kind != 'tutorial' or item.get('tutorial_evidence_verified') is True))
        if not basic or item.get('duplicate_suspected'):
            item['decision'] = 'needs_review'
            continue
        freshness = _timestamp_status(item, now)
        if freshness != 'fresh':
            item['decision'] = 'stale' if freshness == 'stale' else 'needs_review'
            continue
        if review_required:
            item['decision'] = 'queue'
        else:
            item['decision'] = 'deferred'
            eligible.append(item)

    for item in choose_publication(eligible, review_required=review_required,
                                   already_published=already_published, opinions_published=opinions_published):
        item['decision'] = 'publish_ready'
    return candidates
