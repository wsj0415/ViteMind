"""Coordinate a single import without making source data authoritative.

The store must implement insert_new as insert-if-absent, save_prepared as a
guarded update of just-inserted pending rows, and publish_automatic as the
database transaction. The caller supplies trusted enrichment and model clients.
"""
import json
import uuid

from news_model_output import validate_model_output
from news_pipeline import prepare_candidates
from news_sources import SourceCollectionError, collect_sources


def _candidate(item):
    identity = [item.get(key) for key in ('source_type', 'source_id', 'source_item_id')]
    if any(not isinstance(value, str) or not value for value in identity):
        raise ValueError('source identity must contain three non-empty strings')
    if not isinstance(item.get('title'), str) or not item['title'].strip() or not isinstance(item.get('link'), str) or not item['link'].strip():
        raise ValueError('candidate title and link are required')
    result = {key: item.get(key) for key in ('source_type', 'source_id', 'source_item_id', 'source_name',
              'title', 'link', 'summary_raw', 'published_at', 'updated_at', 'first_seen_at')}
    result['candidate_id'] = str(uuid.uuid5(uuid.NAMESPACE_URL, json.dumps(identity, ensure_ascii=False, separators=(',', ':'))))
    result['status'] = 'pending'
    return result


def run_news_cycle(sources, store, *, enrich, summarize, now):
    """Collect, preserve, validate and select new candidates for an atomic publish."""
    if not sources:
        raise ValueError('no sources configured')
    config = store.settings()
    if not isinstance(config.get('review_required'), bool):
        raise ValueError('review mode must be an explicit boolean')
    try:
        collected, statuses = collect_sources(sources, now=now)
    except SourceCollectionError as exc:
        store.record_runs(exc.statuses)
        raise
    store.record_runs(statuses)
    unique, candidate_errors = {}, []
    for index, item in enumerate(collected):
        try:
            if not isinstance(item, dict):
                raise ValueError('invalid source item')
            candidate = _candidate(item)
        except ValueError:
            candidate_errors.append({'index': index, 'reason': 'invalid source item'})
            continue
        unique.setdefault(candidate['candidate_id'], candidate)
    inserted_ids = set(store.insert_new(list(unique.values()))) if unique else set()
    if not inserted_ids.issubset(unique):
        raise ValueError('store returned an unknown candidate ID')
    new = [item for candidate_id, item in unique.items() if candidate_id in inserted_ids]
    if not new:
        return {'new_count': 0, 'published_count': 0, 'model_errors': [], 'enrichment_errors': [], 'candidate_errors': candidate_errors}

    enriched, enrichment_errors = [], []
    for item in new:
        try:
            evidence = enrich(dict(item))
            if not isinstance(evidence, dict):
                enrichment_errors.append({'candidate_id': item['candidate_id'], 'error_type': 'InvalidEvidence'})
                continue
            # Never copy identity, URLs, dates or status from the enrichment source.
            trusted = {key: evidence.get(key) for key in ('source_excerpt', 'source_validated', 'link_verified', 'tutorial_evidence_verified')}
            enriched.append({**item, **trusted})
        except Exception as exc:
            # The raw candidate remains pending; other candidates can continue.
            enrichment_errors.append({'candidate_id': item['candidate_id'], 'error_type': type(exc).__name__})
            continue
    if not enriched:
        return {'new_count': len(new), 'published_count': 0, 'model_errors': [], 'enrichment_errors': enrichment_errors, 'candidate_errors': candidate_errors}
    drafts = summarize([dict(item) for item in enriched])
    accepted, errors = validate_model_output(enriched, drafts)
    accepted_ids = {item['candidate_id'] for item in accepted}
    errors.extend({'candidate_id': item['candidate_id'], 'reason': 'candidate omitted'}
                  for item in enriched if item['candidate_id'] not in accepted_ids)
    for item in accepted:
        item['status'] = 'new'  # Only for this run's rule evaluation.
    prepared = prepare_candidates(accepted, now=now, review_required=config['review_required'],
                                  rules=config.get('rules', ()), already_published=config.get('already_published', 0),
                                  opinions_published=config.get('opinions_published', 0))
    for item in prepared:
        item['status'] = 'new' if item['decision'] == 'publish_ready' else 'pending'
    store.save_prepared(prepared)
    publish_ids = [item['candidate_id'] for item in prepared if item['decision'] == 'publish_ready']
    if publish_ids:
        store.publish_automatic(publish_ids)
    return {'new_count': len(new), 'published_count': len(publish_ids), 'model_errors': errors, 'enrichment_errors': enrichment_errors, 'candidate_errors': candidate_errors}
