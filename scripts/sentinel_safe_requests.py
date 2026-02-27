import requests
import socket
import ipaddress
import contextlib
from urllib.parse import urlparse, urljoin

def is_unsafe_ip(ip_str):
    """
    Checks if an IP address is unsafe (Private, Loopback, Link-Local, Multicast, Reserved, Unspecified).
    """
    try:
        ip_obj = ipaddress.ip_address(ip_str)
        # Block Private, Loopback, Link-Local, Multicast, Reserved, Unspecified
        if (ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or
            ip_obj.is_multicast or ip_obj.is_reserved or ip_obj.is_unspecified):
            return True
        return False
    except ValueError:
        return True # Treat invalid IPs as unsafe

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
            if is_unsafe_ip(ip):
                return False, f"Blocked internal IP: {ip}"

        return True, None
    except Exception as e:
        return False, f"Validation error: {str(e)}"

@contextlib.contextmanager
def safe_dns_request():
    """
    Context manager that patches socket.getaddrinfo to prevent DNS rebinding (TOCTOU).
    It filters out unsafe IPs from DNS resolution results.
    """
    original_getaddrinfo = socket.getaddrinfo

    def patched_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        # Resolve using original function
        res = original_getaddrinfo(host, port, family, type, proto, flags)

        safe_res = []
        for item in res:
            # item structure: (family, type, proto, canonname, sockaddr)
            # sockaddr is (ip, port) for AF_INET/AF_INET6
            ip = item[4][0]

            if not is_unsafe_ip(ip):
                safe_res.append(item)

        if not safe_res and res:
            # All resolved IPs were unsafe
            raise ValueError(f"Blocked by Sentinel: Unsafe IP resolved for {host}")

        return safe_res

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
        # 1. Validate destination before connecting (Pre-check)
        is_safe, error = validate_url_ip(current_url)
        if not is_safe:
            raise ValueError(f"SSRF Protection: {error} ({current_url})")

        # 2. Perform request with redirects disabled
        kwargs['allow_redirects'] = False
        kwargs['timeout'] = timeout

        try:
            # Sentinel: Use safe_dns_request context to prevent TOCTOU
            with safe_dns_request():
                resp = requests.get(current_url, **kwargs)
        except requests.RequestException as e:
             raise ValueError(f"Request failed: {e}")
        except ValueError as e: # Catch our DNS block
             raise ValueError(f"SSRF Protection: {e}")

        # 3. Handle Redirects Manually
        if 300 <= resp.status_code < 400 and 'Location' in resp.headers:
            new_url = resp.headers['Location']
            # Resolve relative URLs
            current_url = urljoin(current_url, new_url)
            continue

        # Return final response
        return resp

    raise ValueError(f"Too many redirects (max {max_redirects})")
