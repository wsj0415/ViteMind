import requests
import socket
import ipaddress
from urllib.parse import urlparse, urljoin

def validate_url_ip(url):
    """
    Resolves the hostname in the URL and checks if it points to a private/loopback IP.
    Returns (True, None) if safe, (False, error_message) otherwise.
    Supports both IPv4 and IPv6.
    """
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            return False, "Invalid URL structure"

        # DNS Resolution (supports IPv4 and IPv6)
        # We check all resolved addresses
        addr_infos = socket.getaddrinfo(hostname, None)

        for family, type, proto, canonname, sockaddr in addr_infos:
            ip = sockaddr[0]
            ip_obj = ipaddress.ip_address(ip)

            # Fake IP block for proxies (Clash/Surge/etc), commonly 198.18.0.0/15
            if ip_obj.version == 4 and (ip.startswith("198.18.") or ip.startswith("198.19.")):
                continue

            # Block Private, Loopback, and Link-Local addresses
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local:
                return False, f"Blocked internal IP: {ip}"

        return True, None
    except Exception as e:
        return False, f"Validation error: {str(e)}"

def safe_get(url, timeout=10, max_redirects=5, **kwargs):
    """
    A security-hardened version of requests.get that prevents SSRF.
    It validates DNS resolution for every hop (including redirects).
    """
    current_url = url

    for _ in range(max_redirects + 1):
        # 1. Validate destination before connecting
        is_safe, error = validate_url_ip(current_url)
        if not is_safe:
            raise ValueError(f"SSRF Protection: {error} ({current_url})")

        # 2. Perform request with redirects disabled
        kwargs['allow_redirects'] = False
        kwargs['timeout'] = timeout

        try:
            resp = requests.get(current_url, **kwargs)
        except requests.RequestException as e:
             raise ValueError(f"Request failed: {e}")

        # 3. Handle Redirects Manually
        if 300 <= resp.status_code < 400 and 'Location' in resp.headers:
            new_url = resp.headers['Location']
            # Resolve relative URLs
            current_url = urljoin(current_url, new_url)
            continue

        # Return final response
        return resp

    raise ValueError(f"Too many redirects (max {max_redirects})")
