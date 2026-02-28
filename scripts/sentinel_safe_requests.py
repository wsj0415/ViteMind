import requests
import socket
import ipaddress
from contextlib import contextmanager
from urllib.parse import urlparse

def is_unsafe_ip(ip):
    """
    Checks if an IP address object or string is unsafe (private, loopback, link-local).
    """
    try:
        if isinstance(ip, str):
            ip_obj = ipaddress.ip_address(ip)
        else:
            ip_obj = ip
        return ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local
    except ValueError:
        # Fail secure: If it's not a valid IP, block it to be safe
        return True

def validate_url_ip(url):
    """
    Resolves the hostname in the URL and checks if it points to a private/loopback IP.
    Returns (True, None) if safe, (False, error_message) otherwise.
    """
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            return False, "Invalid URL structure"

        # DNS Resolution
        addr_infos = socket.getaddrinfo(hostname, None)

        for family, type, proto, canonname, sockaddr in addr_infos:
            ip = sockaddr[0]
            if is_unsafe_ip(ip):
                return False, f"Blocked internal IP: {ip}"

        return True, None
    except Exception as e:
        return False, f"Validation error: {str(e)}"

@contextmanager
def safe_dns_request():
    """
    Context manager that patches socket.getaddrinfo to block resolution of unsafe IPs.
    This prevents DNS rebinding attacks (TOCTOU) and protects redirects.

    WARNING: This modifies the global socket module and is NOT thread-safe.
    It should only be used in single-threaded scripts or controlled environments.
    """
    original_getaddrinfo = socket.getaddrinfo

    def patched_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        # Perform the actual resolution
        res = original_getaddrinfo(host, port, family, type, proto, flags)

        # Verify all resolved IPs
        for family_res, type_res, proto_res, canonname, sockaddr in res:
            ip = sockaddr[0]
            if is_unsafe_ip(ip):
                raise ValueError(f"SSRF Protection: Blocked access to internal IP {ip} for host {host}")

        return res

    socket.getaddrinfo = patched_getaddrinfo
    try:
        yield
    finally:
        socket.getaddrinfo = original_getaddrinfo

def safe_get(url, timeout=10, **kwargs):
    """
    A security-hardened version of requests.get that prevents SSRF.
    It uses a context manager to patch DNS resolution, ensuring that
    even if a DNS rebinding attack occurs (or during redirects),
    we never connect to a private IP.
    """
    # Enforce a reasonable timeout if not provided
    if 'timeout' not in kwargs:
        kwargs['timeout'] = timeout

    with safe_dns_request():
        return requests.get(url, **kwargs)
