# Sentinel Journal

## 2025-01-12 - Missing Security Headers
**Vulnerability:** The application is a static site (SSG) but may be hosted on platforms that don't add security headers by default (like GitHub Pages or Netlify).
**Learning:** Even static sites can benefit from headers like CSP, though difficult to enforce without a server. However, meta tags can be used for some.
**Prevention:** Add `<meta http-equiv="Content-Security-Policy">` where appropriate, or configure hosting headers.

## 2025-01-12 - SSRF Risk in News Generator
**Vulnerability:** `scripts/generate_news.py` makes requests to URLs that could potentially be internal (though unlikely given the feed sources).
**Learning:** Python `requests` library follows redirects by default and doesn't block private IP ranges.
**Prevention:** Implement a safe request wrapper that validates IPs and disables redirects or checks them.

## 2025-01-13 - Unvalidated User Links (XSS)
**Vulnerability:** The "Submit Tool" modal allowed any string in the "Link" field, enabling XSS via `javascript:` URIs if approved or stored in local storage.
**Learning:** Frontend forms feeding into a database/storage must validate data type and format (Protocol Whitelisting) before persistence, even if there is a manual approval process.
**Prevention:** Enforce strict URL protocol validation (`http:`, `https:`) at the input stage.

## 2025-01-20 - SSRF TOCTOU Vulnerability
**Vulnerability:** The previous SSRF protection checked the IP of the URL *before* the request, allowing DNS Rebinding attacks (Time-of-Check Time-of-Use) where the DNS resolution changes to a private IP during the actual connection.
**Learning:** `requests` performs its own DNS resolution. Validating the URL string beforehand is insufficient.
**Prevention:** Implemented a `safe_dns_request` context manager that monkey-patches `socket.getaddrinfo` to verify *every* IP resolution during the request lifecycle.
