import unittest
import socket
from unittest.mock import patch
from sentinel_safe_requests import validate_url_ip, safe_get
import requests

class TestSSRFProtection(unittest.TestCase):

    def test_validate_safe_url(self):
        """Test that public URLs are allowed."""
        # Note: This requires actual DNS resolution.
        # We can assume google.com is safe.
        safe, error = validate_url_ip("https://www.google.com")
        self.assertTrue(safe, f"Google should be safe: {error}")

    def test_validate_unsafe_ip(self):
        """Test that private IPs are blocked."""
        # 127.0.0.1
        safe, error = validate_url_ip("http://127.0.0.1")
        self.assertFalse(safe)
        self.assertIn("Blocked internal IP", error)

        # 0.0.0.0
        safe, error = validate_url_ip("http://0.0.0.0")
        self.assertFalse(safe)

        # Localhost
        safe, error = validate_url_ip("http://localhost")
        self.assertFalse(safe)

    def test_safe_get_blocks_ssrf_direct_ip(self):
        """Test that safe_get raises ValueError for internal IPs."""
        with self.assertRaises(ValueError) as cm:
            safe_get("http://127.0.0.1:8000")
        self.assertIn("SSRF Protection", str(cm.exception))

    @patch('socket.getaddrinfo')
    def test_safe_get_blocks_dns_spoofing(self, mock_getaddrinfo):
        """
        Test that safe_get checks the resolved IP, blocking 'safe' URLs
        that resolve to internal IPs (DNS Rebinding simulation).
        """
        # Simulate google.com resolving to 127.0.0.1
        mock_getaddrinfo.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('127.0.0.1', 80))
        ]

        with self.assertRaises(ValueError) as cm:
            safe_get("http://google.com")

        self.assertIn("SSRF Protection", str(cm.exception))
        self.assertIn("127.0.0.1", str(cm.exception))

    def test_safe_get_works_for_public(self):
        """Test that safe_get actually fetches data for public URLs."""
        try:
            # Use a reliable public API that returns small data
            response = safe_get("https://httpbin.org/get", timeout=5)
            self.assertEqual(response.status_code, 200)
        except Exception as e:
            self.fail(f"safe_get failed for valid URL: {e}")

if __name__ == '__main__':
    unittest.main()
