import unittest
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

    def test_toctou_prevention(self):
        """Test that safe_get prevents TOCTOU by re-validating DNS during connection."""
        original_getaddrinfo = socket.getaddrinfo

        # Mock state
        call_count = [0]

        def side_effect_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
            # Only intercept for example.com (the test URL)
            if host == "example.com":
                call_count[0] += 1
                if call_count[0] <= 1:
                    # First call: validate_url_ip -> Return Safe IP
                    return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('93.184.216.34', port or 80))]
                else:
                    # Subsequent calls: requests.get -> Return Unsafe IP (localhost)
                    return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('127.0.0.1', port or 80))]

            # For other hosts, fallback to original
            return original_getaddrinfo(host, port, family, type, proto, flags)

        # Apply mock
        socket.getaddrinfo = side_effect_getaddrinfo

        try:
            with self.assertRaises(ValueError) as cm:
                safe_get("http://example.com")

            # Check for the specific error from the inner check
            self.assertIn("Blocked by Sentinel", str(cm.exception))

        finally:
            socket.getaddrinfo = original_getaddrinfo

if __name__ == '__main__':
    unittest.main()
