## 2025-02-14 - [CRITICAL] Missing SSRF Protection in News Generator
**Vulnerability:** The memory claimed `scripts/generate_news.py` had SSRF protection (resolving IPs, blocking private ranges), but the actual code used standard `requests.get` which is vulnerable to SSRF if feed URLs are manipulated.
**Learning:** Documentation and "memory" can drift from reality. Always verify security claims against the actual code. Blindly trusting that a "Smart Incremental Pipeline" is secure because the spec says so is dangerous.
**Prevention:** Implemented a reusable `safe_get` function in `scripts/sentinel_safe_requests.py` that resolves DNS and blocks private IPs before making requests. Enforced this in the news generator.
