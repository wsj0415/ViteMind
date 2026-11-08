"""Server-side Supabase persistence for the news ingestion runner.

The caller constructs the client with a server-only service credential.
No credentials are logged or returned by this module.
"""
import hashlib
import re
import uuid


class SupabaseNewsStore:
    def __init__(self, client, *, now):
        if now.tzinfo is None:
            raise ValueError('now must include a timezone')
        self.client, self.now, self.token = client, now, str(uuid.uuid4())

    def settings(self):
        data = self.client.rpc('news_ingestion_config', {'p_now': self.now.isoformat()}).execute().data
        if not isinstance(data, dict) or not isinstance(data.get('review_required'), bool):
            raise ValueError('Could not read explicit news settings')
        return data

    def record_runs(self, statuses):
        rows = []
        for status in statuses:
            name = str(status.get('source_id') or status.get('source') or 'unknown')
            source_id = ('source:' + hashlib.sha256(name.encode()).hexdigest()) if '://' in name else name
            error = str(status.get('error') or '')
            http = re.search(r'\bHTTP (\d{3})\b', error)
            rows.append({'source_type': status.get('source_type') or 'unknown', 'source_id': source_id,
                         'started_at': self.now.isoformat(), 'finished_at': self.now.isoformat(),
                         'status': status['status'], 'item_count': status.get('count', 0),
                         'error_message': ('HTTP ' + http.group(1) if http else 'Source failed') if status['status'] == 'error' else None})
        if rows:
            self.client.table('news_source_runs').insert(rows).execute()

    def insert_new(self, rows):
        data = self.client.rpc('news_ingest_candidates', {'p_items': rows, 'p_token': self.token}).execute().data
        if not isinstance(data, list) or any(not isinstance(value, str) for value in data):
            raise ValueError('Invalid database import result')
        return data

    def save_prepared(self, rows):
        fields = ('candidate_id', 'title', 'summary', 'detail', 'source_excerpt', 'content_type',
                  'suggested_content_type', 'status', 'duplicate_suspected', 'source_validated',
                  'link_verified', 'tutorial_evidence_verified', 'decision', 'matched_keywords')
        items = [{key: row[key] for key in fields if key in row} for row in rows]
        if not items:
            return
        data = self.client.rpc('news_finalize_candidates', {'p_items': items, 'p_token': self.token}).execute().data
        if type(data) is not int or data != len(items):
            raise RuntimeError('Candidate finalization was incomplete')

    def publish_automatic(self, ids):
        data = self.client.rpc('news_publish_candidates', {'p_ids': ids, 'p_mode': 'automatic'}).execute().data
        if not isinstance(data, list) or len(data) != len(ids):
            raise RuntimeError('Publication result is incomplete; reconcile before retrying')
