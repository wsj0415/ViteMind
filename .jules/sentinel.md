# Sentinel's Journal

## 2025-01-04 - Missing SSRF Protection in News Generator
**Vulnerability:** The `scripts/generate_news.py` script fetches RSS feeds from URLs provided in a database (Supabase) without any validation. This allows an attacker with database access (or if the script processes untrusted inputs in the future) to perform Server-Side Request Forgery (SSRF) attacks against the local network or loopback interfaces.
**Learning:** The project documentation/memory claimed SSRF protection existed ("validating all RSS feed URLs..."), but the actual code had none. This highlights the importance of "Trust but Verify" — never rely solely on documentation or memory.
**Prevention:** Implement strict URL validation that resolves hostnames and checks against a blocklist of private/reserved IP ranges before making any HTTP requests.
