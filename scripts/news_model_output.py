"""Validate model output against candidate provenance, without claiming fact checking."""


def validate_model_output(candidates, output):
    """Return accepted drafts and indexed validation errors; preserve source dates and URL."""
    if not isinstance(output, list):
        raise ValueError('model output must be an array')
    sources = {}
    for candidate in candidates:
        candidate_id = candidate.get('candidate_id')
        if not isinstance(candidate_id, str) or not candidate_id or candidate_id in sources:
            raise ValueError('candidate IDs must be unique non-empty strings')
        sources[candidate_id] = candidate
    accepted, errors, seen = [], [], set()
    allowed_types = {'technical_update', 'tutorial', 'project', 'opinion'}
    for index, draft in enumerate(output):
        if not isinstance(draft, dict):
            errors.append({'index': index, 'reason': 'invalid item'})
            continue
        candidate_id = draft.get('candidate_id')
        if not isinstance(candidate_id, str) or candidate_id not in sources or candidate_id in seen:
            errors.append({'index': index, 'reason': 'unknown or duplicate candidate'})
            continue
        source = sources[candidate_id]
        if any(key in draft and draft[key] != source.get(key) for key in ('link', 'published_at', 'updated_at')):
            errors.append({'index': index, 'reason': 'source link or date changed'})
            continue
        if (any(not isinstance(draft.get(key), str) or not draft[key].strip() for key in ('title', 'summary', 'detail'))
                or not isinstance(draft.get('content_type'), str) or draft['content_type'] not in allowed_types):
            errors.append({'index': index, 'reason': 'invalid draft fields'})
            continue
        seen.add(candidate_id)
        kind = draft['content_type']
        result = {**source, **{key: draft[key].strip() for key in ('title', 'summary', 'detail')},
                  'content_type': kind}
        if kind == 'tutorial' and source.get('tutorial_evidence_verified') is not True:
            result.update(content_type=None, suggested_content_type=kind)
        accepted.append(result)
    return accepted, errors
