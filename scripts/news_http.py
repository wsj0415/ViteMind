"""Bounded outbound GETs using Microsoft's DNS-pinning AntiSSRF adapter."""
import json
from urllib.parse import urljoin, urlsplit


def _session():
    from AntiSSRF import AntiSSRFPolicy, PolicyConfigOptions
    policy = AntiSSRFPolicy(PolicyConfigOptions.EXTERNAL_ONLY_LATEST)
    policy.allow_plain_text_http = True
    policy.add_xff_header = False
    session = policy.get_antissrf_session()
    # A proxy would make the actual connection and bypass address pinning.
    session.trust_env = False
    return session


def _origin(url):
    try:
        parsed = urlsplit(url)
        if (parsed.scheme not in ('http', 'https') or not parsed.hostname or parsed.username is not None
                or parsed.password is not None or parsed.port not in (None, 80, 443)):
            raise ValueError('Unsupported URL')
        return parsed.scheme, parsed.hostname.lower(), parsed.port or (443 if parsed.scheme == 'https' else 80)
    except (TypeError, ValueError) as exc:
        raise ValueError('Unsupported URL') from exc


class NewsResponse:
    def __init__(self, response, body):
        self.status_code = response.status_code
        self.headers = dict(response.headers)
        self.links = response.links
        self.content = body
        self.text = body.decode(response.encoding or 'utf-8', errors='replace')

    def json(self):
        return json.loads(self.content)


def safe_news_get(url, *, headers=None, timeout=20, max_redirects=5, max_bytes=2 * 1024 * 1024):
    """Resolve and pin each hop, reject private addresses and cap response bytes."""
    if max_redirects < 0 or max_bytes < 1:
        raise ValueError('Invalid request limits')
    origin = _origin(url)
    request_headers = dict(headers or {})
    session = _session()
    try:
        for hop in range(max_redirects + 1):
            try:
                response = session.get(url, headers=request_headers, timeout=timeout, allow_redirects=False, stream=True)
            except Exception:
                raise ValueError('External request failed') from None
            try:
                location = response.headers.get('Location')
                if 300 <= response.status_code < 400 and location:
                    if hop == max_redirects:
                        raise ValueError('Too many redirects')
                    target = urljoin(url, location)
                    target_origin = _origin(target)
                    if target_origin != origin:
                        request_headers = {key: value for key, value in request_headers.items()
                                           if key.lower() not in ('authorization', 'proxy-authorization', 'cookie')}
                    url, origin = target, target_origin
                    continue
                chunks, length = [], 0
                for chunk in response.iter_content(chunk_size=65536):
                    length += len(chunk)
                    if length > max_bytes:
                        raise ValueError('Response exceeds size limit')
                    chunks.append(chunk)
                return NewsResponse(response, b''.join(chunks))
            finally:
                response.close()
    finally:
        session.close()
