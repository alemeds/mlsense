"""Fetch and parse individual MercadoLibre product URLs."""

import urllib.request
import urllib.error
import ssl
import logging
from typing import Tuple, Optional, Dict, Any


logger = logging.getLogger(__name__)


def fetch_product_url(url: str, timeout: int = 15) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """Fetch MercadoLibre product URL with browser headers.

    Attempts SSL verification first, degrading to unverified on failure.

    Args:
        url: Product URL
        timeout: Request timeout in seconds

    Returns:
        Tuple of (success, html_content or None, message)
    """
    if not url or not url.startswith('http'):
        return False, None, "Invalid URL format"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9',
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        context = ssl.create_default_context()

        with urllib.request.urlopen(req, timeout=timeout, context=context) as response:
            content = response.read().decode('utf-8', errors='replace')
            return True, content, "Success"

    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        if isinstance(e, urllib.error.HTTPError):
            if e.code == 403:
                logger.warning(f"403 Forbidden from {url} - trying without SSL verification")
                return _fetch_sin_verificacion(url, headers, timeout)
            elif e.code == 429:
                return False, None, "Too many requests. MercadoLibre blocked this IP. Use Mode A (HTML upload)."
            elif 400 <= e.code < 500:
                return False, None, f"Client error {e.code}: {e.reason}. Try uploading HTML instead."
            else:
                return False, None, f"Server error {e.code}: {e.reason}"
        else:
            return False, None, f"Connection error: {str(e)}. Check URL and internet connection."

    except ssl.SSLError as e:
        logger.warning(f"SSL error for {url} - trying without verification")
        return _fetch_sin_verificacion(url, headers, timeout)

    except Exception as e:
        return False, None, f"Unexpected error: {type(e).__name__}: {str(e)[:100]}"


def _fetch_sin_verificacion(url: str, headers: Dict, timeout: int) -> Tuple[bool, Optional[str], str]:
    """Fetch URL without SSL verification (fallback).

    Args:
        url: Product URL
        headers: HTTP headers
        timeout: Request timeout

    Returns:
        Tuple of (success, html_content or None, message)
    """
    try:
        context = ssl._create_unverified_context()
        req = urllib.request.Request(url, headers=headers)

        with urllib.request.urlopen(req, timeout=timeout, context=context) as response:
            content = response.read().decode('utf-8', errors='replace')
            logger.warning(f"Fetched without SSL verification: {url}")
            return True, content, "Success (unverified SSL)"

    except Exception as e:
        return False, None, f"Failed even without verification: {type(e).__name__}"
