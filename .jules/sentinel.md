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

## 2025-01-13 - Unrestricted DELETE in Anonymous RLS
**Vulnerability:** The `user_favorites` table used an RLS policy `USING (true)` for DELETE operations to allow anonymous users to remove items. This allowed any malicious actor to wipe the entire table by sending a DELETE request without a WHERE clause.
**Learning:** When using anonymous authentication (client-side IDs), standard RLS cannot enforce ownership securely because the ID is not verified by a token. `USING (true)` essentially disables RLS for that operation.
**Prevention:** Use `SECURITY DEFINER` RPC functions for sensitive operations (like DELETE) to strictly enforce parameter requirements (e.g., matching a specific ID) and prevent mass-action attacks.
