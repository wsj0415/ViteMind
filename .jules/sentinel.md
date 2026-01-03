## 2025-01-03 - SSRF Protection in News Generator
**Vulnerability:** The `generate_news.py` script fetched RSS feeds from URLs (potentially user-influenced via database) without validating if the target was an internal network resource.
**Learning:** `requests` follows redirects by default, which can bypass initial IP checks. DNS rebinding is also a risk, though standard defense-in-depth usually focuses on validating the IP of the resolved hostname and handling redirects manually.
**Prevention:** Implemented `is_safe_url` using `socket.getaddrinfo` (supporting IPv6) to check for private/loopback IPs. Replaced `requests.get` with a loop using `Session` and `allow_redirects=False` to validate every hop in the redirect chain.
