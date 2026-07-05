"""MLSENSE: Multi-category sentiment analysis and expert system for product reviews."""

__version__ = "2.0.0"

from .sentiment import AnalizadorSentimiento
from .expert import ProductExpert
from .parsers import parse_mercadolibre_html
from .fetcher import fetch_product_url
from .demo_data import generate_demo_data

__all__ = [
    "AnalizadorSentimiento",
    "ProductExpert",
    "parse_mercadolibre_html",
    "fetch_product_url",
    "generate_demo_data",
]
