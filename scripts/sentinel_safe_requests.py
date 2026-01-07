# sentinel_safe_requests.py
import requests
import socket
import ipaddress
from urllib.parse import urlparse, urljoin

# Private IP ranges (RFC 1918, Loopback, Link-Local, etc.)
PRIVATE_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
    ipaddress.ip_network("0.0.0.0/8"), # Often resolves to localhost on Linux
]

def is_ip_allowed(ip_str):
    """Check if the IP address is public and allowed."""
    try:
        ip = ipaddress.ip_address(ip_str)
        for network in PRIVATE_NETWORKS:
            if ip in network:
                return False
        return True
    except ValueError:
        return False

def validate_url(url):
    """
    Resolve the URL's hostname to an IP and check if it's allowed.
    Raises ValueError if the URL resolves to a private IP or cannot be resolved.

    SECURITY NOTE: This check is vulnerable to DNS Rebinding (TOCTOU).
    A sophisticated attacker could return a safe IP here and a malicious one
    during the actual request. A full fix requires a custom TransportAdapter
    resolving at the socket level.
    """
    parsed = urlparse(url)
    hostname = parsed.hostname
    if not hostname:
        raise ValueError("Invalid URL: No hostname")

    try:
        # Resolve hostname to IP
        ip_list = socket.getaddrinfo(hostname, None)
        # Check all resolved IPs
        for item in ip_list:
            ip_str = item[4][0]
            if not is_ip_allowed(ip_str):
                raise ValueError(f"Blocked: {url} resolves to private IP {ip_str}")
    except socket.gaierror:
        # Fail Closed: If we can't resolve it, we can't verify it's safe.
        raise ValueError(f"Blocked: Could not resolve hostname for {url}")

def safe_get(url, **kwargs):
    """
    A drop-in replacement for requests.get with SSRF protection.
    It resolves the URL first to check if it points to a private IP.
    It handles redirects manually to validate every hop.
    """
    # 1. Validate initial URL
    validate_url(url)

    # 2. Perform request with redirects disabled
    kwargs.pop('allow_redirects', None)

    response = requests.get(url, allow_redirects=False, **kwargs)

    # 3. Handle Redirects Manually
    history = []

    # We loop up to 5 times
    for _ in range(5):
        if not response.is_redirect:
            break

        location = response.headers.get('Location')
        if not location:
            break

        new_url = urljoin(url, location)

        # Validate the redirect target
        validate_url(new_url)

        history.append(response)

        # Update url for next request
        url = new_url
        response = requests.get(url, allow_redirects=False, **kwargs)
    else:
         raise requests.TooManyRedirects("Too many redirects")

    response.history = history
    return response
