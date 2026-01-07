
import unittest
import requests
from unittest.mock import patch, MagicMock
import socket
from scripts.sentinel_safe_requests import is_ip_allowed, validate_url, safe_get

class TestSentinelSafeRequests(unittest.TestCase):
    def test_is_ip_allowed(self):
        self.assertFalse(is_ip_allowed("127.0.0.1"))
        self.assertFalse(is_ip_allowed("192.168.1.1"))
        self.assertFalse(is_ip_allowed("10.0.0.1"))
        self.assertFalse(is_ip_allowed("169.254.169.254"))
        self.assertFalse(is_ip_allowed("0.0.0.0"))
        self.assertTrue(is_ip_allowed("8.8.8.8")) # Google DNS

    @patch('socket.getaddrinfo')
    def test_validate_url_private(self, mock_getaddrinfo):
        # Mock resolving to private IP
        mock_getaddrinfo.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('127.0.0.1', 80))]
        with self.assertRaises(ValueError) as cm:
            validate_url("http://localhost")
        self.assertIn("Blocked", str(cm.exception))

    @patch('socket.getaddrinfo')
    def test_validate_url_dns_fail(self, mock_getaddrinfo):
        # Mock DNS failure
        mock_getaddrinfo.side_effect = socket.gaierror("Name or service not known")
        with self.assertRaises(ValueError) as cm:
            validate_url("http://nonexistent.domain")
        self.assertIn("Could not resolve", str(cm.exception))

    @patch('socket.getaddrinfo')
    def test_validate_url_public(self, mock_getaddrinfo):
        # Mock resolving to public IP
        mock_getaddrinfo.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('93.184.216.34', 80))]
        try:
            validate_url("http://example.com")
        except ValueError:
            self.fail("validate_url raised ValueError unexpectedly!")

    @patch('requests.get')
    @patch('scripts.sentinel_safe_requests.validate_url')
    def test_safe_get_redirects(self, mock_validate, mock_requests_get):
        # Setup mock responses for a redirect chain
        resp1 = MagicMock()
        resp1.is_redirect = True
        resp1.headers = {'Location': '/relative'}
        resp1.status_code = 301

        resp2 = MagicMock()
        resp2.is_redirect = True
        resp2.headers = {'Location': '//absolute.com/foo'}
        resp2.status_code = 302

        resp3 = MagicMock()
        resp3.is_redirect = False
        resp3.status_code = 200

        mock_requests_get.side_effect = [resp1, resp2, resp3]

        final_resp = safe_get("http://example.com/start")

        self.assertEqual(final_resp, resp3)
        self.assertEqual(len(final_resp.history), 2)

        mock_validate.assert_any_call("http://example.com/start")
        mock_validate.assert_any_call("http://example.com/relative")
        mock_validate.assert_any_call("http://absolute.com/foo")

if __name__ == '__main__':
    unittest.main()
