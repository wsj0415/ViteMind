import sys
import unittest
from sentinel_safe_requests import safe_get, is_safe_url

class TestSSRF(unittest.TestCase):
    def test_is_safe_url_public(self):
        self.assertTrue(is_safe_url("https://www.google.com"))
        self.assertTrue(is_safe_url("http://example.com"))

    def test_is_safe_url_private(self):
        self.assertFalse(is_safe_url("http://localhost"))
        self.assertFalse(is_safe_url("http://127.0.0.1"))
        self.assertFalse(is_safe_url("http://0.0.0.0"))
        self.assertFalse(is_safe_url("http://192.168.1.1"))
        self.assertFalse(is_safe_url("http://10.0.0.1"))

    def test_is_safe_url_invalid(self):
        self.assertFalse(is_safe_url("ftp://example.com"))
        self.assertFalse(is_safe_url("not_a_url"))

    def test_safe_get_blocks_private(self):
        with self.assertRaises(ValueError) as cm:
            safe_get("http://127.0.0.1:8000")
        self.assertIn("Blocked unsafe/private URL", str(cm.exception))

    def test_safe_get_allows_public(self):
        # We can't easily rely on external network in sandbox tests,
        # but if this fails it might be network, not code.
        # We'll try a known stable public IP or skip if no net.
        try:
            resp = safe_get("http://example.com")
            self.assertEqual(resp.status_code, 200)
        except Exception as e:
            # If network is down, we might get connection error, but NOT ValueError
            self.assertNotIsInstance(e, ValueError)

if __name__ == '__main__':
    unittest.main()
