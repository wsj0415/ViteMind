import requests
import socket
import ipaddress
import contextlib
from urllib.parse import urlparse, urljoin

def validate_url_ip(url):
    """
    Resolves the hostname in the URL and checks if it points to a private/loopback IP.
    Returns (True, safe_ip) if safe, (False, error_message) otherwise.
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

        safe_ip = None
        for family, type, proto, canonname, sockaddr in addr_infos:
            ip = sockaddr[0]
            ip_obj = ipaddress.ip_address(ip)

            # Block Private, Loopback, and Link-Local addresses
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local:
                return False, f"Blocked internal IP: {ip}"

            # Capture the first validated IP to pin later
            if safe_ip is None:
                safe_ip = ip

        return True, safe_ip
    except Exception as e:
        return False, f"Validation error: {str(e)}"

@contextlib.contextmanager
def safe_dns_request(hostname, safe_ip):
    """
    Context manager that patches socket.getaddrinfo to return a pinned safe IP
    for the specific hostname. This prevents DNS rebinding (TOCTOU) attacks.
    """
    original_getaddrinfo = socket.getaddrinfo

    def patched_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        # Only pin DNS for the target hostname
        if host == hostname:
            # Return the pinned IP using the original structure logic
            # We call original getaddrinfo with the IP to get the correct struct
            return original_getaddrinfo(safe_ip, port, family, type, proto, flags)
        return original_getaddrinfo(host, port, family, type, proto, flags)

    socket.getaddrinfo = patched_getaddrinfo
    try:
        yield
    finally:
        socket.getaddrinfo = original_getaddrinfo

def safe_get(url, timeout=10, max_redirects=5, **kwargs):
    """
    A security-hardened version of requests.get that prevents SSRF.
    It validates DNS resolution for every hop (including redirects).
    """
    current_url = url

    for _ in range(max_redirects + 1):
        # 1. Validate destination before connecting
        is_safe, safe_ip_or_error = validate_url_ip(current_url)
        if not is_safe:
            raise ValueError(f"SSRF Protection: {safe_ip_or_error} ({current_url})")

        safe_ip = safe_ip_or_error
        hostname = urlparse(current_url).hostname

        # 2. Perform request with redirects disabled
        kwargs['allow_redirects'] = False
        kwargs['timeout'] = timeout

        try:
            # Use safe_dns_request context to pin the DNS to the validated IP
            with safe_dns_request(hostname, safe_ip):
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
