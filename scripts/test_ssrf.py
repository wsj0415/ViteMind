
import unittest
from unittest.mock import patch
import socket
from sentinel_safe_requests import validate_url_ip, safe_get
import requests

class TestSSRFProtection(unittest.TestCase):

    def test_validate_safe_url(self):
        """Test that public URLs are allowed."""
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

        # Localhost (depends on /etc/hosts but usually resolves to 127.0.0.1)
        safe, error = validate_url_ip("http://localhost")
        self.assertFalse(safe)

    def test_safe_get_blocks_ssrf(self):
        """Test that safe_get raises ValueError for internal IPs."""
        with self.assertRaises(ValueError) as cm:
            safe_get("http://127.0.0.1:8000")
        self.assertIn("SSRF Protection", str(cm.exception))

    def test_safe_get_works_for_public(self):
        """Test that safe_get actually fetches data for public URLs."""
        try:
            # Use a reliable public API that returns small data
            response = safe_get("https://httpbin.org/get", timeout=5)
            self.assertEqual(response.status_code, 200)
        except Exception as e:
            self.fail(f"safe_get failed for valid URL: {e}")

    @patch('socket.getaddrinfo')
    def test_dns_rebinding_prevention(self, mock_getaddrinfo):
        """Test that safe_get prevents TOCTOU/DNS rebinding attacks."""

        # Safe IP (example.com)
        safe_addr = (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('93.184.216.34', 80))
        # Unsafe IP (localhost)
        unsafe_addr = (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('127.0.0.1', 80))

        def side_effect(*args, **kwargs):
            # Check if this is the validation call (sentinel_safe_requests.py: socket.getaddrinfo(hostname, None))
            # args[1] is port.
            if len(args) > 1 and args[1] is None:
                return [safe_addr]

            # Connection time: Return Unsafe IP to simulate rebinding
            return [unsafe_addr]

        mock_getaddrinfo.side_effect = side_effect

        with self.assertRaises(ValueError) as cm:
             safe_get("http://example.com")

        self.assertIn("Blocked internal IP", str(cm.exception))

if __name__ == '__main__':
    unittest.main()
