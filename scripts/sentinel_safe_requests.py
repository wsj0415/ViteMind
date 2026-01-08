import socket
import ipaddress
import requests
from urllib.parse import urlparse, urljoin

def is_safe_url(url):
    """
    Checks if a URL resolves to a safe (non-private) IP address.
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        # Resolve hostname to IPs
        # socket.getaddrinfo returns a list of (family, type, proto, canonname, sockaddr)
        addr_infos = socket.getaddrinfo(hostname, None)

        for *_, sockaddr in addr_infos:
            ip_str = sockaddr[0]
            ip = ipaddress.ip_address(ip_str)

            # Check for private, loopback, link-local, multicast, reserved
            if (ip.is_private or
                ip.is_loopback or
                ip.is_link_local or
                ip.is_multicast or
                ip.is_reserved):
                return False

        return True
    except Exception:
        # If any error occurs (DNS failure, invalid URL), assume unsafe
        return False

def safe_get(url, **kwargs):
    """
    A wrapper around requests.get that enforces SSRF protection.
    It validates the URL and any redirect targets before fetching.

    LIMITATION: This implementation is vulnerable to DNS Rebinding (TOCTOU) attacks.
    A malicious DNS server could return a safe IP during validation but a private IP
    during the actual connection. Fixing this requires a custom TransportAdapter
    that pins the resolved IP, which is beyond the scope of this initial fix.
    """
    if not is_safe_url(url):
        raise ValueError(f"Blocked unsafe/private URL: {url}")

    # Enforce a reasonable timeout if not provided to prevent hanging
    kwargs.setdefault('timeout', 10)

    # Disable auto-redirects to check each hop manually
    kwargs['allow_redirects'] = False

    try:
        response = requests.get(url, **kwargs)
    except requests.RequestException as e:
         raise e

    # Manual redirect handling
    history = []
    max_redirects = kwargs.pop('max_redirects', 5) # Custom param, not in requests

    while response.is_redirect:
        # Consume content to release connection
        _ = response.content

        history.append(response)
        if len(history) > max_redirects:
            raise requests.TooManyRedirects(f"Exceeded {max_redirects} redirects")

        location = response.headers.get('Location')
        if not location:
            break

        # Handle relative redirects
        next_url = urljoin(response.url, location)

        if not is_safe_url(next_url):
            raise ValueError(f"Blocked unsafe redirect to: {next_url}")

        try:
            response = requests.get(next_url, **kwargs)
        except requests.RequestException as e:
            raise e

    response.history = history
    return response
