"""Pure selection rules; callers must validate sources before publication."""


def flag_exact_duplicates(items):
    """Mark repeated source IDs or URLs while retaining every source record.

    ``duplicate_of`` is an index within this result, not a persistent ID.
    Query strings are retained because they can identify different content.
    """
    from urllib.parse import urlsplit, urlunsplit

    source_ids, links, result = {}, {}, []
    for index, original in enumerate(items):
        item = dict(original)
        source_key = (item.get('source_type'), item.get('source_id'), item.get('source_item_id'))
        source_key = source_key if all(source_key) else None
        try:
            parsed = urlsplit(item.get('link') or '')
            link = urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), parsed.path, parsed.query, ''))
            if parsed.scheme.lower() not in ('http', 'https') or not parsed.hostname or parsed.username or parsed.password:
                link = None
        except (TypeError, ValueError):
            link = None
        duplicate = source_ids.get(source_key) if source_key else None
        if duplicate is None and link:
            duplicate = links.get(link)
        if duplicate is not None:
            item['duplicate_of'] = duplicate
            item['duplicate_suspected'] = True
        if source_key:
            source_ids.setdefault(source_key, index)
        if link:
            links.setdefault(link, index)
        result.append(item)
    return result


def apply_blocklist(item, rules):
    """Return matching enabled literal rules for this item's content type."""
    content = '\n'.join(str(item.get(field) or '') for field in ('title', 'summary', 'source_excerpt')).casefold()
    matches = []
    for rule in rules:
        word = str(rule.get('keyword') or '').strip()
        scope = rule.get('content_type')
        if rule.get('enabled', True) and word and (not scope or scope == item.get('content_type')) and word.casefold() in content:
            matches.append(word)
    return matches


def choose_publication(items, *, review_required, rules=(), already_published=0, opinions_published=0):
    """Select from previously validated candidates; never select pending work."""
    if review_required:
        return []
    selected, opinions = [], opinions_published
    capacity = max(0, 5 - already_published)
    for item in items:
        if len(selected) >= capacity:
            break
        if (item.get('status') != 'new'
                or item.get('content_type') not in ('technical_update', 'tutorial', 'project', 'opinion')
                or item.get('duplicate_suspected') or apply_blocklist(item, rules)):
            continue
        if item.get('content_type') == 'opinion':
            if opinions >= 1:
                continue
            opinions += 1
        selected.append(item)
    return selected


def is_fresh(item, now):
    """Check source timestamps without substituting the first-seen date."""
    from datetime import datetime, timedelta
    kind = item.get('content_type')
    if kind not in ('technical_update', 'tutorial', 'project', 'opinion') or now.tzinfo is None:
        return False
    raw = item.get('published_at') if kind == 'technical_update' else (item.get('updated_at') or item.get('published_at'))
    if not raw:
        return False
    try:
        date = datetime.fromisoformat(raw.replace('Z', '+00:00'))
        if date.tzinfo is None or date > now:
            return False
        return now - date <= (timedelta(hours=24) if kind == 'technical_update' else timedelta(days=7))
    except (TypeError, ValueError, AttributeError):
        return False
