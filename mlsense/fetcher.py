"""Fetch and parse individual MercadoLibre product URLs."""

import urllib.request
import urllib.error
import urllib.parse
import ssl
import logging
import time
import random
import unicodedata
import re
from typing import Tuple, Optional, Dict, Any, List
from pathlib import Path


logger = logging.getLogger(__name__)

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
]


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


def build_search_url(termino: str) -> str:
    """Build MercadoLibre search URL from search term.

    Normalizes term: lowercase, removes diacritics, replaces spaces with hyphens.

    Args:
        termino: Search term (e.g. "Celular Samsung A56")

    Returns:
        Full search URL
    """
    termino = termino.strip()
    termino = termino.lower()
    termino = unicodedata.normalize('NFD', termino)
    termino = ''.join(c for c in termino if unicodedata.category(c) != 'Mn')
    termino = re.sub(r'[^a-z0-9\s]', '', termino)
    termino = re.sub(r'\s+', '-', termino).strip('-')

    return f"https://listado.mercadolibre.com.ar/{termino}"


def search_live(termino: str, max_productos: int = 15, con_comentarios: bool = True,
                max_paginas: int = 1) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Search MercadoLibre live and fetch product details.

    Fetches search results page, extracts products, and optionally fetches
    individual product pages for reviews. Includes random delays and User-Agent rotation.

    Args:
        termino: Search term
        max_productos: Maximum products to fetch (5-30)
        con_comentarios: Whether to fetch product reviews (slower)
        max_paginas: Maximum search result pages to process

    Returns:
        Tuple of (products_list, warnings_list)
    """
    from .parsers import parse_mercadolibre_html

    max_productos = max(5, min(30, max_productos))
    warnings = []
    productos = []

    search_url = build_search_url(termino)

    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9',
    }

    try:
        req = urllib.request.Request(search_url, headers=headers)
        context = ssl.create_default_context()

        with urllib.request.urlopen(req, timeout=15, context=context) as response:
            search_html = response.read().decode('utf-8', errors='replace')

    except urllib.error.HTTPError as e:
        if e.code == 403:
            return [], ["🚫 MercadoLibre bloqueó la IP del servidor (habitual en Streamlit Cloud). "
                       "Ejecutá la app localmente o usá el modo HTML subido."]
        elif e.code == 429:
            return [], ["⏱️ Rate limit. Esperá unos minutos e intentá de nuevo."]
        else:
            return [], [f"❌ Error HTTP {e.code} en búsqueda"]

    except Exception as e:
        return [], [f"❌ Error al buscar: {type(e).__name__}"]

    prods_buscados, parse_warnings = parse_mercadolibre_html(search_html)
    warnings.extend(parse_warnings)

    if not prods_buscados:
        return [], warnings + ["No se encontraron productos en la búsqueda."]

    productos = prods_buscados[:max_productos]

    if con_comentarios and productos:
        productos_con_reviews = []

        for i, producto in enumerate(productos):
            url = producto.get('url', '')

            if not url:
                productos_con_reviews.append(producto)
                continue

            time.sleep(random.uniform(1.5, 3.5))

            success, html, msg = fetch_product_url(url, timeout=15)

            if success and html:
                prods_detail, _ = parse_mercadolibre_html(html)
                if prods_detail:
                    producto_detail = prods_detail[0]
                    producto['comentarios'] = producto_detail.get('comentarios', [])

            elif msg and "bloqueó" in msg.lower():
                warnings.append(f"⚠️ Bloqueo a mitad de fetches de comentarios. "
                               f"Se obtuvieron {len(productos_con_reviews)}/{max_productos} con reviews.")
                productos_con_reviews.extend(productos[i:])
                break

            productos_con_reviews.append(producto)

        productos = productos_con_reviews

    return productos, warnings


def search_with_playwright(termino: str) -> Tuple[str, Optional[str], List[str]]:
    """Search MercadoLibre with Playwright and return HTML of current page.

    Args:
        termino: Search term

    Returns:
        Tuple of (search_url, html_content or None, screenshots_paths, warnings)
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return build_search_url(termino), None, [], ["❌ Playwright no instalado. Ejecuta: pip install playwright"]

    search_url = build_search_url(termino)
    screenshots = []
    warnings = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=random.choice(USER_AGENTS),
                viewport={"width": 1280, "height": 720}
            )
            page = context.new_page()

            page.goto(search_url, wait_until="load", timeout=30000)
            time.sleep(2)

            html = page.content()

            context.close()
            browser.close()

            return search_url, html, screenshots, warnings

    except Exception as e:
        return search_url, None, screenshots, [f"❌ Error con Playwright: {str(e)[:100]}"]


def extract_html_from_page(url: str) -> Tuple[Optional[str], List[str]]:
    """Extract HTML from a MercadoLibre product page using Playwright.

    Args:
        url: Product URL

    Returns:
        Tuple of (html_content or None, warnings)
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None, ["❌ Playwright no instalado"]

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent=random.choice(USER_AGENTS))
            page = context.new_page()

            page.goto(url, wait_until="load", timeout=30000)
            time.sleep(2)

            html = page.content()

            context.close()
            browser.close()

            return html, []

    except Exception as e:
        return None, [f"❌ Error extrayendo página: {str(e)[:100]}"]
