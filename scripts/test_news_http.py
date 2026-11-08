import unittest
from unittest.mock import patch

from news_http import safe_news_get


class Response:
    def __init__(self, status, body=b'', headers=None):
        self.status_code, self.body, self.headers = status, body, headers or {}
        self.links, self.encoding = {}, 'utf-8'
    def iter_content(self, chunk_size): yield self.body
    def close(self): pass


class TestSafeNewsHTTP(unittest.TestCase):
    def test_unsafe_urls_are_rejected_before_request(self):
        for url in ('file:///etc/passwd', 'https://user:pass@example.com/', 'https://example.com:8080/'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                safe_news_get(url)

    def test_redirects_are_rechecked_and_credentials_not_forwarded(self):
        class Session:
            def __init__(self): self.calls = []
            def get(self, url, **kwargs):
                self.calls.append((url, kwargs))
                return Response(302, headers={'Location': 'https://other.example/path'}) if len(self.calls) == 1 else Response(200, b'ok')
            def close(self): pass
        session = Session()
        with patch('news_http._session', return_value=session):
            response = safe_news_get('https://example.com/a', headers={'Authorization': 'Bearer secret', 'User-Agent': 'test'})
        self.assertEqual(response.content, b'ok')
        self.assertNotIn('Authorization', session.calls[1][1]['headers'])

    def test_response_size_limit_and_redirect_limit(self):
        class Session:
            def get(self, *a, **k): return Response(200, b'x' * 20)
            def close(self): pass
        with patch('news_http._session', return_value=Session()), self.assertRaises(ValueError):
            safe_news_get('https://example.com/', max_bytes=10)
        class Redirect(Session):
            def get(self, *a, **k): return Response(302, headers={'Location': '/again'})
        with patch('news_http._session', return_value=Redirect()), self.assertRaises(ValueError):
            safe_news_get('https://example.com/', max_redirects=1)

    def test_actual_library_blocks_private_and_loopback_addresses(self):
        try:
            import AntiSSRF  # noqa: F401
        except ImportError:
            self.skipTest('install scripts/requirements-news.txt to test the pinned security library')
        for url in ('http://127.0.0.1/', 'http://169.254.169.254/', 'http://[::1]/'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                safe_news_get(url, timeout=2)

    def test_actual_library_pins_the_validated_ip_and_keeps_tls_hostname(self):
        try:
            import AntiSSRF  # noqa: F401
        except ImportError:
            self.skipTest('install scripts/requirements-news-security.txt to test the pinned security library')
        import socket
        import requests
        from news_http import _session
        session = _session()
        self.assertFalse(session.trust_env)
        request = requests.Request('GET', 'https://example.com/').prepare()
        with patch('socket.getaddrinfo', return_value=[(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('93.184.216.34', 443))]):
            host, tls = session.get_adapter(request.url).build_connection_pool_key_attributes(request, True)
        self.assertEqual(host['host'], '93.184.216.34')
        self.assertEqual(tls['server_hostname'], 'example.com')
        self.assertEqual(tls['assert_hostname'], 'example.com')
        session.close()


if __name__ == '__main__': unittest.main()
