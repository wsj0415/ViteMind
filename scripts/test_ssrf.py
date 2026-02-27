import unittest
import socket
from unittest.mock import patch, MagicMock
from sentinel_safe_requests import validate_url_ip, safe_get, validate_ip

class TestSSRFProtection(unittest.TestCase):

    def test_validate_safe_url(self):
        """Test that public URLs are allowed."""
        safe, error = validate_url_ip("https://www.google.com")
        self.assertTrue(safe, f"Google should be safe: {error}")

    def test_validate_unsafe_ip(self):
        """Test that private IPs are blocked by validator."""
        # 127.0.0.1
        safe, error = validate_url_ip("http://127.0.0.1")
        self.assertFalse(safe)
        self.assertIn("Blocked internal IP", error)

    def test_safe_get_blocks_ssrf(self):
        """Test that safe_get raises ValueError for internal IPs (caught by patch)."""
        # This relies on the context manager patching getaddrinfo and real system resolution
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

    @patch('sentinel_safe_requests._original_getaddrinfo')
    def test_dns_rebinding_simulation(self, mock_original_resolver):
        """
        Simulate a DNS rebinding attack / TOCTOU.
        We mock the underlying resolver to return a private IP.
        safe_get's patch should catch this at connection time.
        """
        # Mock getaddrinfo to return a private IP
        # Format: [(family, type, proto, canonname, sockaddr)]
        # sockaddr for AF_INET is (ip, port)
        mock_original_resolver.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('192.168.1.1', 80))
        ]

        # Even if we pass a safe-looking hostname, the resolver returns private IP
        # and it should be blocked by the patch.
        with self.assertRaises(ValueError) as cm:
            safe_get("http://looks-safe.com")

        self.assertIn("SSRF Protection", str(cm.exception))
        self.assertIn("Blocked internal IP: 192.168.1.1", str(cm.exception))

if __name__ == '__main__':
    unittest.main()
