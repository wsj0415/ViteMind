import socket
import ipaddress
from urllib.parse import urlparse, urljoin
import requests

def is_ip_allowed(ip_str):
    """
    Check if an IP address is allowed (not private/reserved).
    Supports both IPv4 and IPv6.
    """
    try:
        ip = ipaddress.ip_address(ip_str)
        # Check for private, loopback, link-local, multicast, reserved
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved:
            return False

        # IPv6 specific checks if needed (is_private covers most unique local addresses)
        # But site-local was deprecated. unique-local (fc00::/7) is private.

        # Special case: 0.0.0.0 is not technically "private" in some definitions but unsafe
        if ip.is_unspecified:
            return False

        return True
    except ValueError:
        return False

def validate_url(url):
    """
    Validate URL scheme and resolve hostname to check against blocklist.
    """
    parsed = urlparse(url)
    if parsed.scheme not in ('http', 'https'):
        raise ValueError(f"Invalid scheme: {parsed.scheme}")

    hostname = parsed.hostname
    if not hostname:
        raise ValueError("No hostname found")

    # DNS Resolution
    try:
        # Resolve to IP(s)
        # Note: This is vulnerable to DNS Rebinding (TOCTOU).
        # We check the IP here, but requests.get will re-resolve it.
        # This is a known limitation documented in Sentinel's journal.
        addr_info = socket.getaddrinfo(hostname, None)
        for family, type, proto, canonname, sockaddr in addr_info:
            ip = sockaddr[0]
            # socket.getaddrinfo returns a tuple for sockaddr.
            # For AF_INET (IPv4), it's (ip, port)
            # For AF_INET6 (IPv6), it's (ip, port, flowinfo, scopeid)
            # In both cases, index 0 is the IP string.
            if not is_ip_allowed(ip):
                 raise ValueError(f"Blocked IP address: {ip} for hostname: {hostname}")
    except socket.gaierror:
        raise ValueError(f"Could not resolve hostname: {hostname}")

def safe_get(url, **kwargs):
    """
    A drop-in replacement for requests.get that enforces SSRF protection.
    """
    # 1. Validate initial URL
    validate_url(url)

    # 2. Handle Redirects Manually
    allow_redirects = kwargs.pop('allow_redirects', True)
    timeout = kwargs.get('timeout', 10) # Default timeout if not provided
    kwargs['timeout'] = timeout

    current_url = url
    max_redirects = 30

    with requests.Session() as session:
        for _ in range(max_redirects):
            # Validate before every request in the chain
            validate_url(current_url)

            # Disable auto-redirects in requests so we can inspect the Location header
            resp = session.get(current_url, allow_redirects=False, **kwargs)

            if resp.is_redirect and allow_redirects:
                location = resp.headers.get('Location')
                if not location:
                    return resp # Should not happen if is_redirect is True

                # Resolve relative URLs
                # Ensure location is a string (requests headers are usually strings)
                if not isinstance(location, str):
                    # Fallback or strict error?
                    # requests headers should be strings.
                    location = str(location)

                current_url = urljoin(current_url, location)
                continue

            return resp

        raise requests.TooManyRedirects("Too many redirects")
