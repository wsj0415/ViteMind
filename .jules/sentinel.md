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

## 2025-01-29 - Insecure Public Delete (Table Wiping Risk)
**Vulnerability:** The `user_favorites` table allowed `DELETE` via RLS with `USING (true)`, enabling any anonymous user to wipe the entire table.
**Learning:** For anonymous features (Guestbook, Favorites) where users are identified by client-side UUIDs, standard RLS policies (`auth.uid() = user_id`) cannot be used. Falling back to `USING (true)` is catastrophic for `DELETE` operations.
**Prevention:** Use `SECURITY DEFINER` RPC functions for sensitive operations on anonymous data. This allows enforcing logic (e.g. `WHERE user_id = X AND news_id = Y`) that simple boolean RLS policies cannot express safely without authentication.
