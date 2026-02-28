import requests
import socket
import ipaddress
import contextlib
from urllib.parse import urlparse, urljoin

@contextlib.contextmanager
def safe_dns_request():
    """
    Context manager that patches socket.getaddrinfo to validate all resolved IPs.
    Prevents DNS rebinding attacks (TOCTOU) by ensuring that the IP used for connection
    is validated at the moment of resolution.
    """
    original_getaddrinfo = socket.getaddrinfo

    def patched_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        # Resolve using the original function
        res = original_getaddrinfo(host, port, family, type, proto, flags)

        # Validate all returned addresses
        for _, _, _, _, sockaddr in res:
            ip = sockaddr[0]
            try:
                ip_obj = ipaddress.ip_address(ip)
            except ValueError:
                # If ipaddress fails to parse, it might be something weird (e.g. invalid string)
                # We skip validation for non-parsable IPs (though getaddrinfo usually returns valid ones)
                continue

            # Block Private, Loopback, and Link-Local addresses
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local:
                raise ValueError(f"Blocked internal IP: {ip}")
        return res

    socket.getaddrinfo = patched_getaddrinfo
    try:
        yield
    finally:
        socket.getaddrinfo = original_getaddrinfo

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
        # using the safe context manager to perform validation
        with safe_dns_request():
            socket.getaddrinfo(hostname, None)

        return True, None
    except ValueError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Validation error: {str(e)}"

def safe_get(url, timeout=10, max_redirects=5, **kwargs):
    """
    A security-hardened version of requests.get that prevents SSRF.
    It validates DNS resolution for every hop (including redirects) using a
    monkey-patched socket.getaddrinfo to prevent TOCTOU/DNS rebinding.
    """
    current_url = url

    for _ in range(max_redirects + 1):
        # 1. Validate destination before connecting (First line of defense)
        is_safe, error = validate_url_ip(current_url)
        if not is_safe:
            raise ValueError(f"SSRF Protection: {error} ({current_url})")

        # 2. Perform request with redirects disabled
        kwargs['allow_redirects'] = False
        kwargs['timeout'] = timeout

        try:
            # 3. Use context manager to prevent DNS rebinding during connection
            with safe_dns_request():
                resp = requests.get(current_url, **kwargs)
        except requests.RequestException as e:
             raise ValueError(f"Request failed: {e}")
        except ValueError as e:
             # Catch the validation error from the context manager
             raise ValueError(f"SSRF Protection: {e}")

        # 4. Handle Redirects Manually
        if 300 <= resp.status_code < 400 and 'Location' in resp.headers:
            new_url = resp.headers['Location']
            # Resolve relative URLs
            current_url = urljoin(current_url, new_url)
            continue

        # Return final response
        return resp

    raise ValueError(f"Too many redirects (max {max_redirects})")
