"""HTML parsers for MercadoLibre product data extraction."""

import json
import re
from typing import List, Dict, Any, Tuple
from html.parser import HTMLParser


def parse_mercadolibre_html(html_content: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Parse MercadoLibre HTML and extract product data.

    Attempts multiple strategies:
    1. JSON-LD structured data (type Product or ItemList)
    2. __PRELOADED_STATE__ window variable
    3. Fallback DOM parsing with regex

    Args:
        html_content: HTML string

    Returns:
        Tuple of (products_list, warnings_list)
    """
    productos = []
    warnings = []

    productos, success = _extraer_json_ld(html_content)
    if success and productos:
        return productos, warnings

    productos, success = _extraer_preloaded_state(html_content)
    if success and productos:
        return productos, warnings

    productos, parse_warnings = _extraer_dom_fallback(html_content)
    warnings.extend(parse_warnings)

    return productos, warnings


def _extraer_json_ld(html_content: str) -> Tuple[List[Dict[str, Any]], bool]:
    """Extract products from JSON-LD structured data.

    Args:
        html_content: HTML string

    Returns:
        Tuple of (products_list, success_bool)
    """
    json_ld_pattern = r'<script type="application/ld\+json">(.*?)</script>'
    matches = re.findall(json_ld_pattern, html_content, re.DOTALL | re.IGNORECASE)

    productos = []

    for match in matches:
        try:
            data = json.loads(match)
            prods = _parsear_json_ld_data(data)
            productos.extend(prods)
        except json.JSONDecodeError:
            continue

    return productos, bool(productos)


def _parsear_json_ld_data(data: Dict) -> List[Dict[str, Any]]:
    """Parse JSON-LD data structure.

    Args:
        data: Parsed JSON object

    Returns:
        List of products
    """
    productos = []

    if data.get('@type') == 'Product':
        productos.append(_extraer_producto_json_ld(data))
    elif data.get('@type') == 'ItemList':
        for item in data.get('itemListElement', []):
            if 'url' in item:
                productos.append({
                    'nombre': item.get('name', 'Sin título'),
                    'precio': _normalizar_precio(item.get('price', '')),
                    'url': item['url'],
                    'id': item.get('identifier', ''),
                    'estrellas': '0',
                    'calificaciones': '0',
                    'envio': 'Desconocido',
                    'descuento': 'Sin descuento',
                    'comentarios': []
                })
    elif data.get('@type') == 'ItemList' or '@graph' in data:
        for item in data.get('@graph', []):
            if item.get('@type') == 'Product':
                productos.append(_extraer_producto_json_ld(item))

    return productos


def _extraer_producto_json_ld(item: Dict) -> Dict[str, Any]:
    """Extract single product from JSON-LD Product.

    Args:
        item: Product JSON-LD object

    Returns:
        Product dict
    """
    agregacion = item.get('aggregateRating', {})
    return {
        'nombre': item.get('name', 'Sin título'),
        'precio': _normalizar_precio(item.get('price', '0')),
        'moneda': item.get('priceCurrency', 'ARS'),
        'url': item.get('url', ''),
        'id': item.get('sku', item.get('productID', '')),
        'estrellas': str(agregacion.get('ratingValue', '0')),
        'calificaciones': str(agregacion.get('reviewCount', '0')),
        'envio': 'Desconocido',
        'descuento': 'Sin descuento',
        'vendedor': item.get('brand', {}).get('name', ''),
        'comentarios': []
    }


def _extraer_preloaded_state(html_content: str) -> Tuple[List[Dict[str, Any]], bool]:
    """Extract products from __PRELOADED_STATE__ window variable.

    Args:
        html_content: HTML string

    Returns:
        Tuple of (products_list, success_bool)
    """
    pattern = r'window\.__PRELOADED_STATE__\s*=\s*(\{.*?\});'
    matches = re.findall(pattern, html_content, re.DOTALL)

    for match in matches:
        try:
            data = json.loads(match)
            productos = _extraer_de_preloaded(data)
            if productos:
                return productos, True
        except json.JSONDecodeError:
            continue

    return [], False


def _extraer_de_preloaded(data: Dict) -> List[Dict[str, Any]]:
    """Extract products from parsed __PRELOADED_STATE__.

    Args:
        data: Parsed state object

    Returns:
        List of products
    """
    productos = []

    def buscar_resultados(obj):
        if isinstance(obj, dict):
            if 'results' in obj and isinstance(obj['results'], list):
                for item in obj['results']:
                    if isinstance(item, dict) and 'title' in item:
                        productos.append({
                            'nombre': item.get('title', 'Sin título'),
                            'precio': _normalizar_precio(str(item.get('price', 0))),
                            'url': item.get('permalink', ''),
                            'id': item.get('id', ''),
                            'estrellas': str(item.get('reviews', {}).get('rating_average', 0)),
                            'calificaciones': str(item.get('reviews', {}).get('total', 0)),
                            'envio': 'Gratis' if item.get('shipping', {}).get('free_shipping') else 'Con costo',
                            'descuento': f"{item.get('discount', 0)}%" if item.get('discount') else 'Sin descuento',
                            'comentarios': []
                        })
            for value in obj.values():
                buscar_resultados(value)
        elif isinstance(obj, list):
            for item in obj:
                buscar_resultados(item)

    buscar_resultados(data)
    return productos


def _extraer_dom_fallback(html_content: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Fallback DOM parsing with regex patterns.

    Looks for MercadoLibre specific class patterns.

    Args:
        html_content: HTML string

    Returns:
        Tuple of (products_list, warnings_list)
    """
    productos = []
    warnings = []

    patron_producto = r'<li[^>]*class="[^"]*ui-search-result[^"]*"[^>]*>(.*?)</li>'
    matches = re.findall(patron_producto, html_content, re.DOTALL | re.IGNORECASE)

    if not matches:
        warnings.append("No structured data or classic DOM patterns found. HTML may be from unsupported page type.")
        return [], warnings

    for match in matches:
        try:
            producto = _extraer_producto_del_dom(match)
            if producto:
                productos.append(producto)
        except Exception as e:
            continue

    if productos:
        warnings.append(f"Extracted {len(productos)} products using fallback DOM parser. Some data may be incomplete.")
    else:
        warnings.append("Could not extract products from HTML. Page structure may have changed.")

    return productos, warnings


def _extraer_producto_del_dom(html_item: str) -> Dict[str, Any]:
    """Extract product from DOM item HTML.

    Args:
        html_item: HTML fragment

    Returns:
        Product dict
    """
    producto = {
        'nombre': '',
        'precio': '0',
        'estrellas': '0',
        'calificaciones': '0',
        'envio': 'Desconocido',
        'descuento': 'Sin descuento',
        'url': '',
        'id': '',
        'comentarios': []
    }

    nombre_match = re.search(r'<h2[^>]*>(.*?)</h2>', html_item, re.DOTALL | re.IGNORECASE)
    if nombre_match:
        texto = nombre_match.group(1)
        texto = re.sub(r'<[^>]*>', '', texto)
        producto['nombre'] = texto.strip()[:200]

    precio_match = re.search(r'<span[^>]*class="[^"]*andes-money-amount__fraction[^"]*"[^>]*>([0-9.]+)</span>', html_item, re.IGNORECASE)
    if precio_match:
        producto['precio'] = _normalizar_precio(precio_match.group(1))

    url_match = re.search(r'href="([^"]*)"', html_item)
    if url_match:
        producto['url'] = url_match.group(1)

    envio_match = re.search(r'envío gratis', html_item, re.IGNORECASE)
    if envio_match:
        producto['envio'] = 'Gratis'

    stars_match = re.search(r'(\d+(?:[.,]\d)?)\s*(?:de 5|★)', html_item, re.IGNORECASE)
    if stars_match:
        producto['estrellas'] = stars_match.group(1).replace(',', '.')

    return producto


def _normalizar_precio(precio_str: str) -> str:
    """Normalize price string to float representation.

    Args:
        precio_str: Price string with possible separators

    Returns:
        Normalized price string
    """
    if not precio_str:
        return '0'

    precio_str = str(precio_str).strip()

    precio_limpio = re.sub(r'[^\d.,]', '', precio_str)

    if ',' in precio_limpio and '.' in precio_limpio:
        coma_pos = precio_limpio.index(',')
        punto_pos = precio_limpio.index('.')
        if punto_pos < coma_pos:
            precio_limpio = precio_limpio.replace('.', '').replace(',', '.')
        else:
            precio_limpio = precio_limpio.replace(',', '')
    elif ',' in precio_limpio:
        if precio_limpio.count(',') == 1 and len(precio_limpio.split(',')[1]) == 2:
            precio_limpio = precio_limpio.replace(',', '.')
        else:
            precio_limpio = precio_limpio.replace(',', '')

    try:
        return str(float(precio_limpio))
    except ValueError:
        return '0'
