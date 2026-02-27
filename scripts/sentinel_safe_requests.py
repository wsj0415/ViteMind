import requests
import socket
import ipaddress
from urllib.parse import urlparse, urljoin
from contextlib import contextmanager

# Original socket.getaddrinfo to be used in patch and legacy check
_original_getaddrinfo = socket.getaddrinfo

def validate_ip(ip):
    """
    Checks if an IP address is private, loopback, or link-local.
    Returns (True, None) if safe, (False, error_message) otherwise.
    """
    try:
        ip_obj = ipaddress.ip_address(ip)
        if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local:
            return False, f"Blocked internal IP: {ip}"
        return True, None
    except ValueError:
        return False, f"Invalid IP: {ip}"

def validate_url_ip(url):
    """
    Legacy validation function.
    Resolves hostname and checks IPs.
    NOTE: Not TOCTOU safe. Use safe_get for requests.
    """
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            return False, "Invalid URL structure"

        addr_infos = _original_getaddrinfo(hostname, None)
        for family, type, proto, canonname, sockaddr in addr_infos:
            ip = sockaddr[0]
            is_safe, error = validate_ip(ip)
            if not is_safe:
                return False, error
        return True, None
    except Exception as e:
        return False, f"Validation error: {str(e)}"

@contextmanager
def safe_dns_request():
    """
    Context manager that patches socket.getaddrinfo to prevent SSRF.
    It validates every resolved IP against blocklists before returning.
    """
    def patched_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        # Resolve using original function
        res = _original_getaddrinfo(host, port, family, type, proto, flags)

        # Check all resolved IPs
        for family_res, _, _, _, sockaddr in res:
            ip = sockaddr[0]
            is_safe, error = validate_ip(ip)
            if not is_safe:
                raise ValueError(f"SSRF Protection: {error} ({host})")

        return res

    # Apply patch
    socket.getaddrinfo = patched_getaddrinfo
    try:
        yield
    finally:
        # Restore original
        socket.getaddrinfo = _original_getaddrinfo

def safe_get(url, timeout=10, max_redirects=5, **kwargs):
    """
    A security-hardened version of requests.get that prevents SSRF.
    It uses a DNS-patching context manager to prevent TOCTOU attacks.
    """
    current_url = url

    for _ in range(max_redirects + 1):
        # Perform request with redirects disabled
        # DNS validation happens inside safe_dns_request
        kwargs['allow_redirects'] = False
        kwargs['timeout'] = timeout

        try:
            with safe_dns_request():
                resp = requests.get(current_url, **kwargs)
        except requests.RequestException as e:
             raise ValueError(f"Request failed: {e}")
        except ValueError as e:
             # Catch our SSRF error from patched_getaddrinfo
             raise e

        # Handle Redirects Manually
        if 300 <= resp.status_code < 400 and 'Location' in resp.headers:
            new_url = resp.headers['Location']
            current_url = urljoin(current_url, new_url)
            continue

        return resp

    raise ValueError(f"Too many redirects (max {max_redirects})")
