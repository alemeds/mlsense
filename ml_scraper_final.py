import streamlit as st
import pandas as pd
import urllib.request
import urllib.parse
import urllib.error
import re
import csv
import time
import random
import ssl
import json
import io
import statistics
import math
from datetime import datetime
from collections import defaultdict, Counter

# Configuración de la página
st.set_page_config(
    page_title="MercadoLibre Scraper & Análisis",
    page_icon="🛒",
    layout="wide"
)

# =====================================
# API DE MERCADOLIBRE (ALTERNATIVA)
# =====================================

class MercadoLibreAPI:
    """Clase para acceder a la API oficial de MercadoLibre"""

    def __init__(self):
        self.base_url = "https://api.mercadolibre.com"
        self.site_id = "MLA"  # Argentina

    def search_products(self, query, limit=50):
        """
        Busca productos usando la API oficial

        Args:
            query (str): Término de búsqueda
            limit (int): Número máximo de resultados

        Returns:
            list: Lista de productos encontrados
        """
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"{self.base_url}/sites/{self.site_id}/search?q={encoded_query}&limit={limit}"

            req = urllib.request.Request(url)
            req.add_header('Accept', 'application/json')

            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))

                products = []
                for item in data.get('results', []):
                    product = {
                        'nombre': item.get('title', 'Sin título'),
                        'precio': str(item.get('price', 0)),
                        'estrellas': '0',
                        'calificaciones': '0',
                        'descuento': 'Sin descuento',
                        'envio': 'Gratis' if item.get('shipping', {}).get('free_shipping') else 'Con costo',
                        'url': item.get('permalink', ''),
                        'id': item.get('id', '')
                    }

                    # Intentar obtener reviews
                    if item.get('reviews'):
                        reviews_data = item['reviews']
                        product['estrellas'] = str(reviews_data.get('rating_average', 0))
                        product['calificaciones'] = str(reviews_data.get('total', 0))

                    products.append(product)

                return products

        except urllib.error.HTTPError as e:
            st.error(f"❌ Error HTTP {e.code}: {e.reason}")
            return []
        except Exception as e:
            st.error(f"❌ Error al acceder a la API: {type(e).__name__}: {e}")
            return []

    def get_product_reviews(self, product_id, max_reviews=5):
        """
        Obtiene reviews de un producto específico

        Args:
            product_id (str): ID del producto
            max_reviews (int): Número máximo de reviews

        Returns:
            list: Lista de comentarios
        """
        try:
            url = f"{self.base_url}/reviews/item/{product_id}"

            req = urllib.request.Request(url)
            req.add_header('Accept', 'application/json')

            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))

                reviews = []
                for review in data.get('reviews', [])[:max_reviews]:
                    reviews.append({
                        'comentario': review.get('content', ''),
                        'puntuacion': str(review.get('rate', 3))
                    })

                return reviews

        except urllib.error.HTTPError as e:
            # Muchos productos no tienen reviews, esto es normal
            return []
        except Exception as e:
            return []

# =====================================
# DATOS DE DEMOSTRACIÓN
# =====================================

def generar_datos_demo(num_productos=20):
    """Genera datos de demostración realistas de vinos"""

    productos_demo = [
        {
            'nombre': 'Vino Tinto Malbec Reserva Premium 750ml',
            'precio': '8500',
            'estrellas': '4.7',
            'calificaciones': '342',
            'envio': 'Gratis',
            'url': 'https://mercadolibre.com.ar/producto-demo',
            'comentario_1': 'Excelente vino, muy buen aroma frutal y equilibrado. La relación precio-calidad es increíble.',
            'puntuacion_comentario_1': '5',
            'comentario_2': 'Muy rico, suave y con buen cuerpo. Llegó rápido y bien embalado.',
            'puntuacion_comentario_2': '5',
            'comentario_3': 'Buen vino por el precio. El aroma es agradable pero podría ser más intenso.',
            'puntuacion_comentario_3': '4',
            'comentario_4': 'Perfecto para acompañar carnes. Muy recomendable.',
            'puntuacion_comentario_4': '5',
            'comentario_5': 'Excelente producto, volveré a comprarlo.',
            'puntuacion_comentario_5': '5'
        },
        {
            'nombre': 'Vino Cabernet Sauvignon Gran Reserva 750ml',
            'precio': '12000',
            'estrellas': '4.9',
            'calificaciones': '567',
            'envio': 'Gratis',
            'url': 'https://mercadolibre.com.ar/producto-demo',
            'comentario_1': 'Impresionante calidad. El aroma es espectacular, muy frutado y con notas especiadas.',
            'puntuacion_comentario_1': '5',
            'comentario_2': 'Premium en todo sentido. El precio lo vale completamente.',
            'puntuacion_comentario_2': '5',
            'comentario_3': 'Uno de los mejores malbec que he probado. Recomendable 100%.',
            'puntuacion_comentario_3': '5',
            'comentario_4': 'Excelente bouquet, muy aromático. Llegó en perfecto estado.',
            'puntuacion_comentario_4': '5',
            'comentario_5': 'Maravilloso vino, ideal para ocasiones especiales.',
            'puntuacion_comentario_5': '5'
        },
        {
            'nombre': 'Vino Tinto Económico 1 Litro',
            'precio': '1200',
            'estrellas': '2.3',
            'calificaciones': '89',
            'envio': 'Con costo',
            'url': 'https://mercadolibre.com.ar/producto-demo',
            'comentario_1': 'Muy malo, sabor desagradable. No lo recomiendo.',
            'puntuacion_comentario_1': '1',
            'comentario_2': 'Demasiado ácido y aspero. Decepcionante.',
            'puntuacion_comentario_2': '2',
            'comentario_3': 'Por el precio no se puede esperar mucho, pero está muy flojo.',
            'puntuacion_comentario_3': '2',
            'comentario_4': 'Horrible, sabe a vinagre. Tirar el dinero.',
            'puntuacion_comentario_4': '1',
            'comentario_5': 'No lo compraría de nuevo. Muy ordinario.',
            'puntuacion_comentario_5': '2'
        },
        {
            'nombre': 'Vino Merlot Orgánico Premium 750ml',
            'precio': '9800',
            'estrellas': '4.5',
            'calificaciones': '234',
            'envio': 'Gratis',
            'url': 'https://mercadolibre.com.ar/producto-demo',
            'comentario_1': 'Buen vino orgánico. El aroma es delicioso, muy floral y frutado.',
            'puntuacion_comentario_1': '4',
            'comentario_2': 'Excelente relación calidad-precio. El envío fue rapidísimo.',
            'puntuacion_comentario_2': '5',
            'comentario_3': 'Rico y suave. Muy recomendable para quienes buscan vinos orgánicos.',
            'puntuacion_comentario_3': '4',
            'comentario_4': 'Buen bouquet, equilibrado. La entrega fue perfecta.',
            'puntuacion_comentario_4': '5',
            'comentario_5': 'Satisfecho con la compra. Volveré a pedir.',
            'puntuacion_comentario_5': '4'
        },
        {
            'nombre': 'Vino Blanco Chardonnay 750ml',
            'precio': '6500',
            'estrellas': '4.2',
            'calificaciones': '178',
            'envio': 'Gratis',
            'url': 'https://mercadolibre.com.ar/producto-demo',
            'comentario_1': 'Fresco y aromático. Perfecto para el verano.',
            'puntuacion_comentario_1': '4',
            'comentario_2': 'Buen vino blanco, muy agradable al paladar.',
            'puntuacion_comentario_2': '4',
            'comentario_3': 'El aroma es intenso y frutal. Me gustó mucho.',
            'puntuacion_comentario_3': '5',
            'comentario_4': 'Relación precio-calidad muy buena. Llegó en tiempo.',
            'puntuacion_comentario_4': '4',
            'comentario_5': 'Rico y refrescante. Recomendable.',
            'puntuacion_comentario_5': '4'
        },
        {
            'nombre': 'Vino Tinto de Mesa 2 Litros',
            'precio': '2800',
            'estrellas': '3.1',
            'calificaciones': '156',
            'envio': 'Con costo',
            'url': 'https://mercadolibre.com.ar/producto-demo',
            'comentario_1': 'Para el precio está bien, pero no esperes gran calidad.',
            'puntuacion_comentario_1': '3',
            'comentario_2': 'Aguado y sin mucho sabor. Cumple pero nada más.',
            'puntuacion_comentario_2': '3',
            'comentario_3': 'Es lo que es, vino de mesa económico.',
            'puntuacion_comentario_3': '3',
            'comentario_4': 'Ni bueno ni malo, bastante flojo.',
            'puntuacion_comentario_4': '3',
            'comentario_5': 'Para cocinar puede servir.',
            'puntuacion_comentario_5': '3'
        },
        {
            'nombre': 'Vino Tinto Syrah Gran Reserva 750ml',
            'precio': '11500',
            'estrellas': '4.8',
            'calificaciones': '445',
            'envio': 'Gratis',
            'url': 'https://mercadolibre.com.ar/producto-demo',
            'comentario_1': 'Fantástico vino, el aroma es increíble. Muy recomendable.',
            'puntuacion_comentario_1': '5',
            'comentario_2': 'Excelente calidad premium. El precio es justo.',
            'puntuacion_comentario_2': '5',
            'comentario_3': 'Impresionante bouquet, muy complejo y aromático.',
            'puntuacion_comentario_3': '5',
            'comentario_4': 'Uno de los mejores que he probado. El envío fue rápido.',
            'puntuacion_comentario_4': '5',
            'comentario_5': 'Espectacular, vale cada peso.',
            'puntuacion_comentario_5': '5'
        }
    ]

    # Retornar los primeros num_productos
    return productos_demo[:min(num_productos, len(productos_demo))]

# =====================================
# SISTEMA EXPERTO SIMPLIFICADO
# =====================================

class Vino:
    """Clase para representar los hechos sobre vino"""
    def __init__(self, sentimiento=None, aroma=False, precio=False, envio=False):
        self.sentimiento = sentimiento
        self.aroma = aroma
        self.precio = precio
        self.envio = envio

class WineExpert:
    """Sistema Experto Simplificado para Recomendación de Vinos"""
    
    def __init__(self):
        self.hechos = []
        self.recomendaciones = []
    
    def reset(self):
        """Reinicia el estado del motor de inferencia"""
        self.hechos = []
        self.recomendaciones = []
    
    def declare(self, hecho):
        """Declara un hecho al motor de inferencia"""
        self.hechos.append(hecho)
    
    def run(self):
        """Ejecuta el motor de inferencia y genera recomendaciones"""
        self.recomendaciones = []
        
        for hecho in self.hechos:
            if isinstance(hecho, Vino):
                # Aplicar reglas en orden de prioridad
                self._aplicar_reglas(hecho)
        
        # Mostrar recomendaciones
        for recomendacion in self.recomendaciones:
            print(recomendacion)
    
    def _aplicar_reglas(self, vino):
        """Aplica las reglas del sistema experto"""
        
        # Regla 1: Recomendación total (máxima prioridad)
        if (vino.sentimiento == 'positivo' and 
            vino.aroma and 
            vino.precio):
            self.recomendaciones.append("RECOMENDADO: Buen aroma y buena relación precio-calidad.")
            return  # Termina aquí para evitar múltiples recomendaciones
        
        # Regla 2: Recomendación por envío
        if (vino.sentimiento == 'positivo' and 
            vino.envio):
            self.recomendaciones.append("RECOMENDADO: Envío rápido y sentimiento positivo.")
            return
        
        # Regla 3: Recomendación por aroma
        if (vino.sentimiento == 'positivo' and 
            vino.aroma):
            self.recomendaciones.append("RECOMENDADO: Principalmente por su aroma.")
            return
        
        # Regla 4: No recomendado
        if vino.sentimiento == 'negativo':
            self.recomendaciones.append("NO RECOMENDADO: Evaluación negativa.")
            return
        
        # Regla por defecto para sentimiento neutral o sin aspectos destacados
        if vino.sentimiento == 'positivo':
            self.recomendaciones.append("RECOMENDADO: Evaluación positiva general.")
        else:
            self.recomendaciones.append("NEUTRAL: Revisar detalles del producto.")

def ejecutar_sistema_experto(sentimiento, aspectos):
    """
    Función helper para ejecutar el sistema experto
    
    Args:
        sentimiento (str): 'positivo', 'negativo', o 'neutral'
        aspectos (dict): Diccionario con claves 'aroma', 'precio', 'envio' (bool)
    
    Returns:
        list: Lista de recomendaciones generadas
    """
    engine = WineExpert()
    engine.reset()
    
    vino = Vino(
        sentimiento=sentimiento,
        aroma=aspectos.get('aroma', False),
        precio=aspectos.get('precio', False),
        envio=aspectos.get('envio', False)
    )
    
    engine.declare(vino)
    engine.run()
    
    return engine.recomendaciones

def es_valor_valido(valor):
    """Verifica si un valor es válido para procesar como texto"""
    if valor is None:
        return False
    if isinstance(valor, float) and (math.isnan(valor) or str(valor) == 'nan'):
        return False
    if isinstance(valor, str) and valor.strip() == '':
        return False
    return True

def detectar_aspectos(comentario):
    """
    Detecta aspectos mencionados en un comentario
    
    Args:
        comentario (str): Texto del comentario
    
    Returns:
        dict: Diccionario con aspectos detectados
    """
    # Validación robusta del input
    if not es_valor_valido(comentario):
        return {'aroma': False, 'precio': False, 'envio': False}
    
    # Convertir a string si no lo es y hacer lowercase
    comentario = str(comentario).lower().strip()
    
    # Palabras clave para cada aspecto
    palabras_aroma = [
        'aroma', 'aromatico', 'aromatica', 'olor', 'fragancia', 'bouquet',
        'nariz', 'perfume', 'esencia', 'frutado', 'floral', 'especiado'
    ]
    
    palabras_precio = [
        'precio', 'barato', 'economico', 'accesible', 'vale', 'cuesta',
        'relacion', 'calidad-precio', 'precio-calidad', 'caro', 'costoso',
        'inversion', 'dinero', 'pesos', '$'
    ]
    
    palabras_envio = [
        'envio', 'entrega', 'llego', 'rapido', 'tiempo',
        'demora', 'shipping', 'delivery', 'recibi', 'tardo'
    ]
    
    return {
        'aroma': any(palabra in comentario for palabra in palabras_aroma),
        'precio': any(palabra in comentario for palabra in palabras_precio),
        'envio': any(palabra in comentario for palabra in palabras_envio)
    }

def clasificar_sentimiento(puntuacion_sentimiento):
    """
    Clasifica una puntuación numérica en categoría de sentimiento
    
    Args:
        puntuacion_sentimiento (float): Puntuación de 1.0 a 5.0
    
    Returns:
        str: 'positivo', 'negativo', o 'neutral'
    """
    try:
        puntuacion = float(puntuacion_sentimiento)
        if puntuacion >= 4.0:
            return 'positivo'
        elif puntuacion <= 2.5:
            return 'negativo'
        else:
            return 'neutral'
    except (ValueError, TypeError):
        return 'neutral'

# =====================================
# SCRAPER DE MERCADOLIBRE
# =====================================

class MercadoLibreScraper:
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
        ]
    
    def get_user_agent(self):
        return random.choice(self.user_agents)
    
    def fetch_url(self, url, debug=False):
        """
        Obtiene el contenido HTML de una URL con manejo mejorado de errores

        Args:
            url (str): URL a obtener
            debug (bool): Si es True, muestra información de debugging

        Returns:
            str: Contenido HTML o None si hay error
        """
        headers = {
            'User-Agent': self.get_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }

        req = urllib.request.Request(url, headers=headers)

        # Intentar primero con SSL verification deshabilitada
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            with urllib.request.urlopen(req, context=context, timeout=30) as response:
                status_code = response.getcode()
                if debug:
                    st.info(f"✅ Respuesta HTTP {status_code} de {url}")

                content = response.read()

                # Manejar diferentes encodings
                try:
                    return content.decode('utf-8')
                except UnicodeDecodeError:
                    return content.decode('latin-1')

        except urllib.error.HTTPError as e:
            if debug:
                st.error(f"❌ Error HTTP {e.code}: {e.reason}")
                st.error(f"URL: {url}")

            # Si es un error 403 (Forbidden), es probable que MercadoLibre esté bloqueando
            if e.code == 403:
                st.warning("⚠️ MercadoLibre está bloqueando el acceso. Esto puede deberse a:")
                st.warning("- Detección de scraping automatizado")
                st.warning("- Restricciones en Streamlit Cloud")
                st.warning("- Límites de rate limiting")

            return None

        except urllib.error.URLError as e:
            if debug:
                st.error(f"❌ Error de URL: {e.reason}")
            return None

        except ssl.SSLError as e:
            # Si falla SSL, intentar con verificación habilitada
            if debug:
                st.warning(f"⚠️ Error SSL, reintentando con verificación habilitada...")

            try:
                with urllib.request.urlopen(req, timeout=30) as response:
                    content = response.read()
                    try:
                        return content.decode('utf-8')
                    except UnicodeDecodeError:
                        return content.decode('latin-1')
            except Exception as e2:
                if debug:
                    st.error(f"❌ Error en segundo intento: {e2}")
                return None

        except Exception as e:
            if debug:
                st.error(f"❌ Error inesperado: {type(e).__name__}: {e}")
            return None
    
    def extract_json_data(self, html_content):
        if not html_content:
            return []
        
        json_match = re.search(r'<script type="application/ld\+json">(.*?)</script>', html_content, re.DOTALL)
        if not json_match:
            json_match = re.search(r'window\.__PRELOADED_STATE__\s*=\s*({.*?});', html_content, re.DOTALL)
            if not json_match:
                return []
        
        try:
            return json.loads(json_match.group(1).strip())
        except json.JSONDecodeError:
            return []
    
    def process_product_data(self, json_data):
        products_list = []
        
        if isinstance(json_data, dict) and "@graph" in json_data:
            for item in json_data["@graph"]:
                if item.get("@type") == "Product":
                    try:
                        product = {
                            'nombre': item.get("name", "No disponible"),
                            'estrellas': str(item.get("aggregateRating", {}).get("ratingValue", 0)),
                            'calificaciones': str(item.get("aggregateRating", {}).get("ratingCount", 0)),
                            'precio': str(item.get("offers", {}).get("price", "Precio no disponible")),
                            'descuento': "Sin descuento",
                            'envio': "Verificar en sitio",
                            'url': ""
                        }
                        
                        if "offers" in item and "url" in item["offers"]:
                            full_url = item["offers"]["url"]
                            clean_url = re.search(r'(https://[^#?]*)', full_url)
                            product['url'] = clean_url.group(1) if clean_url else full_url
                        
                        products_list.append(product)
                    except Exception as e:
                        st.warning(f"Error al procesar un producto: {e}")
        
        return products_list
    
    def extract_traditional_way(self, html_content):
        products_list = []
        
        if not html_content:
            return products_list
        
        product_patterns = [
            r'<div[^>]*class="[^"]*ui-search-result[^"]*"[^>]*>.*?</div>\s*</div>\s*</div>\s*</div>',
            r'<li[^>]*class="[^"]*ui-search-layout__item[^"]*"[^>]*>.*?</li>'
        ]
        
        product_blocks = []
        for pattern in product_patterns:
            blocks = re.findall(pattern, html_content, re.DOTALL)
            if len(blocks) >= 5:
                product_blocks = blocks
                break
        
        for block in product_blocks:
            try:
                # URL del producto
                url_patterns = [
                    r'<a[^>]*href="(https://[^"]*?/p/[^"#]*)[#"]',
                    r'<a[^>]*href="(https://articulo\.mercadolibre\.[^/]*/[^"#]*)[#"]'
                ]
                product_url = ""
                for pattern in url_patterns:
                    url_match = re.search(pattern, block)
                    if url_match:
                        product_url = url_match.group(1).strip()
                        break
                
                # Nombre del producto
                title_patterns = [
                    r'<a[^>]*class="[^"]*poly-component__title[^"]*"[^>]*>(.*?)</a>',
                    r'<h2[^>]*class="[^"]*ui-search-item__title[^"]*"[^>]*>(.*?)</h2>'
                ]
                title = "Nombre no disponible"
                for pattern in title_patterns:
                    title_match = re.search(pattern, block, re.DOTALL)
                    if title_match:
                        title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
                        break
                
                # Precio
                price_patterns = [
                    r'<meta[^>]*itemprop="price"[^>]*content="(\d+)"',
                    r'<span[^>]*class="[^"]*price-tag-fraction[^"]*"[^>]*>(.*?)</span>'
                ]
                price = "0"
                for pattern in price_patterns:
                    price_match = re.search(pattern, block)
                    if price_match:
                        price = re.sub(r'[^\d.]', '', price_match.group(1).strip())
                        break
                
                # Estrellas
                stars = "0"
                stars_match = re.search(r'<p[^>]*class="[^"]*ui-review-capability__rating__average[^"]*"[^>]*>(.*?)</p>', block)
                if stars_match:
                    stars = stars_match.group(1).replace(',', '.').strip()
                
                # Número de calificaciones
                ratings_count = "0"
                ratings_match = re.search(r'<p[^>]*class="[^"]*ui-review-capability__rating__label[^"]*"[^>]*>([^<]*?)calificaciones</p>', block)
                if ratings_match:
                    ratings_text = ratings_match.group(1).strip()
                    ratings_val = re.search(r'(\d+[,.]?\d*)', ratings_text)
                    if ratings_val:
                        ratings_count = ratings_val.group(1).replace('.', '').replace(',', '')
                
                product_data = {
                    'nombre': title,
                    'estrellas': stars,
                    'calificaciones': ratings_count,
                    'precio': price,
                    'descuento': "Sin descuento",
                    'envio': "Estándar",
                    'url': product_url
                }
                
                products_list.append(product_data)
                
            except Exception as e:
                continue
        
        return products_list
    
    def extract_comments(self, product_url, max_comments=5):
        comments_data = []
        
        product_html = self.fetch_url(product_url)
        if not product_html:
            return comments_data
        
        time.sleep(random.uniform(1.0, 2.0))
        
        # Buscar bloques completos de comentarios
        comment_patterns = [
            r'<div[^>]*class="ui-review-capability-comments__comment[^"]*"[^>]*>.*?</div>\s*</div>\s*</div>',
            r'<article[^>]*class="[^"]*ui-review-capability-reviews__review[^"]*"[^>]*>.*?</article>',
            r'<div[^>]*class="ui-review-capability__review[^"]*"[^>]*>.*?</div>\s*</div>'
        ]
        
        comment_blocks = []
        for pattern in comment_patterns:
            blocks = re.findall(pattern, product_html, re.DOTALL)
            if blocks:
                comment_blocks = blocks
                break
        
        # Procesar cada bloque de comentario
        for i, block in enumerate(comment_blocks[:max_comments]):
            try:
                # Extraer texto del comentario
                comment_text = ""
                text_patterns = [
                    r'<p[^>]*class="ui-review-capability-comments__comment__content[^"]*"[^>]*>(.*?)</p>',
                    r'<p[^>]*class="ui-review-capability__summary__plain_text__summary_container"[^>]*>(.*?)</p>'
                ]
                
                for pattern in text_patterns:
                    text_match = re.search(pattern, block, re.DOTALL)
                    if text_match:
                        comment_text = re.sub(r'<[^>]+>', '', text_match.group(1)).strip()
                        comment_text = re.sub(r'\s+', ' ', comment_text).strip()
                        break
                
                # Extraer puntuación
                rating = "3"
                rating_match = re.search(r'<p class="andes-visually-hidden">Calificación (\d+) de 5</p>', block)
                
                if rating_match:
                    rating = rating_match.group(1)
                else:
                    # Intentar contar estrellas en el HTML
                    star_count = len(re.findall(r'<svg class="ui-review-capability-comments__comment__rating__star"', block))
                    if star_count > 0 and star_count <= 5:
                        rating = str(star_count)
                
                if comment_text:
                    comments_data.append({
                        'comentario': comment_text,
                        'puntuacion': rating
                    })
                
            except Exception as e:
                continue
        
        return comments_data
    
    def scrape_products(self, search_term, max_pages=1, get_comments=False, max_products_comments=10, debug=False):
        all_products = []

        # Construir URL base
        if ' ' in search_term:
            formatted_search = search_term.replace(' ', '-')
            base_url = f"https://listado.mercadolibre.com.ar/{formatted_search}?sb=all_mercadolibre#D[A:{urllib.parse.quote(search_term)}]"
        else:
            base_url = f"https://listado.mercadolibre.com.ar/{search_term}#D[A:{search_term}]"

        if debug:
            st.info(f"🔍 URL generada: {base_url}")

        progress_bar = st.progress(0)
        status_text = st.empty()

        # Scraping de páginas
        for page in range(1, max_pages + 1):
            if page == 1:
                page_url = base_url
            else:
                page_url = f"{base_url}&page={page}"

            status_text.text(f"Extrayendo datos de la página {page}...")
            progress_bar.progress(page / max_pages * 0.7)

            if debug:
                st.info(f"📡 Intentando acceder a: {page_url[:80]}...")

            page_html = self.fetch_url(page_url, debug=debug)

            if page_html:
                if debug:
                    st.success(f"✅ Se obtuvo HTML (tamaño: {len(page_html)} caracteres)")

                # Intentar extraer datos
                json_data = self.extract_json_data(page_html)
                page_products = []

                if json_data:
                    if debug:
                        st.info(f"📊 Se encontró JSON LD estructurado")
                    page_products = self.process_product_data(json_data)
                else:
                    if debug:
                        st.warning("⚠️ No se encontró JSON LD, usando extracción tradicional")

                if not page_products:
                    page_products = self.extract_traditional_way(page_html)
                    if debug and page_products:
                        st.info(f"📦 Extracción tradicional encontró {len(page_products)} productos")

                if page_products:
                    all_products.extend(page_products)
                    st.success(f"✅ Se encontraron {len(page_products)} productos en la página {page}")
                else:
                    st.warning(f"⚠️ No se pudieron extraer productos de la página {page}")
                    if debug:
                        # Mostrar una muestra del HTML para debugging
                        with st.expander("🔍 Ver muestra del HTML recibido"):
                            st.code(page_html[:2000] + "\n\n...(truncado)")
            else:
                st.error(f"❌ No se pudo obtener el HTML de la página {page}")

            if page < max_pages:
                time.sleep(random.uniform(2.0, 3.0))
        
        # Extraer comentarios si se solicita
        if get_comments and all_products:
            status_text.text("Extrayendo comentarios...")
            max_products_comments = min(max_products_comments, len(all_products))
            
            for count, product in enumerate(all_products[:max_products_comments]):
                if 'url' in product and product['url']:
                    progress = 0.7 + (count / max_products_comments) * 0.3
                    progress_bar.progress(progress)
                    status_text.text(f"Procesando comentarios {count+1}/{max_products_comments}: {product['nombre'][:30]}...")
                    
                    comments = self.extract_comments(product['url'], 5)
                    
                    # Agregar comentarios al producto
                    for i, comment in enumerate(comments):
                        product[f'comentario_{i+1}'] = comment['comentario']
                        product[f'puntuacion_comentario_{i+1}'] = comment['puntuacion']
                    
                    # Rellenar comentarios faltantes
                    for i in range(len(comments), 5):
                        product[f'comentario_{i+1}'] = ""
                        product[f'puntuacion_comentario_{i+1}'] = ""
                    
                    if count < max_products_comments - 1:
                        time.sleep(random.uniform(2.0, 3.0))
        
        progress_bar.progress(1.0)
        status_text.text("¡Scraping completado!")
        
        return all_products

# =====================================
# ANALIZADOR DE SENTIMIENTOS
# =====================================

class AnalizadorSentimiento:
    def __init__(self):
        self.palabras_positivas = [
            'excelente', 'bueno', 'buena', 'increible', 'delicioso', 'deliciosa',
            'suave', 'equilibrado', 'equilibrada', 'aromatico', 'aromatica', 'rico', 'rica',
            'agradable', 'elegante', 'intenso', 'intensa', 'fresco', 'fresca', 'fino', 'fina',
            'recomendable', 'espectacular', 'fantastico', 'fantastica', 'perfecto', 'perfecta',
            'sorprendente', 'impresionante', 'encantador', 'encantadora', 'satisfecho', 'satisfecha',
            'satisfactorio', 'satisfactoria', 'premium', 'calidad', 'maravilloso', 'maravillosa'
        ]
        
        self.palabras_negativas = [
            'malo', 'mala', 'horrible', 'terrible', 'desagradable', 'decepcionante',
            'aspero', 'acido', 'amargo', 'amarga', 'seco', 'seca',
            'flojo', 'floja', 'aguado', 'aguada', 'insipido', 'insipida',
            'ordinario', 'ordinaria', 'descompuesto', 'descompuesta',
            'vinagre', 'oxidado', 'oxidada', 'rancio', 'rancia'
        ]
        
        self.multiplicadores = [
            'muy', 'super', 'tan', 'bastante', 'realmente',
            'extremadamente', 'verdaderamente', 'increiblemente',
            'totalmente', 'absolutamente', 'completamente', 'demasiado'
        ]
        
        self.negadores = [
            'no', 'nunca', 'jamas', 'ni', 'tampoco', 'apenas'
        ]
    
    def normalizar_texto(self, texto):
        # Validación robusta del input
        if not es_valor_valido(texto):
            return ""
        
        texto = str(texto).lower()
        
        # Eliminar acentos
        replacements = [
            ('á', 'a'), ('é', 'e'), ('í', 'i'), ('ó', 'o'), ('ú', 'u'),
            ('ü', 'u'), ('ñ', 'n')
        ]
        for orig, repl in replacements:
            texto = texto.replace(orig, repl)
        
        texto = re.sub(r'[^\w\s]', ' ', texto)
        texto = re.sub(r'\s+', ' ', texto).strip()
        
        return texto
    
    def calcular_sentimiento(self, comentario):
        # Validación robusta del input
        if not es_valor_valido(comentario):
            return 3.0
        
        texto = self.normalizar_texto(comentario)
        palabras = texto.split()
        
        if not palabras:
            return 3.0
        
        puntuacion = 0
        contador_palabras_relevantes = 0
        
        i = 0
        while i < len(palabras):
            palabra = palabras[i]
            multiplicador = 1.0
            negacion = 1.0
            
            # Verificar multiplicadores y negadores
            j = max(0, i - 3)
            while j < i:
                if palabras[j] in self.multiplicadores:
                    multiplicador = 1.5
                if palabras[j] in self.negadores:
                    negacion = -1.0
                j += 1
            
            if palabra in self.palabras_positivas:
                puntuacion += 1.0 * multiplicador * negacion
                contador_palabras_relevantes += 1
            elif palabra in self.palabras_negativas:
                puntuacion -= 1.0 * multiplicador * negacion
                contador_palabras_relevantes += 1
            
            i += 1
        
        if contador_palabras_relevantes == 0:
            return 3.0
        
        promedio = puntuacion / contador_palabras_relevantes
        sentimiento = 3.0 + (promedio * 2.0)
        sentimiento = max(1.0, min(5.0, sentimiento))
        
        return sentimiento
    
    def analizar_productos(self, productos):
        resultados_productos = []
        
        for producto in productos:
            comentarios = []
            puntuaciones = []
            sentimientos = []
            
            # Extraer comentarios y puntuaciones del producto
            for i in range(1, 6):
                comentario_key = f'comentario_{i}'
                puntuacion_key = f'puntuacion_comentario_{i}'
                
                if comentario_key in producto and es_valor_valido(producto[comentario_key]):
                    comentario = producto[comentario_key]
                    comentarios.append(comentario)
                    
                    # Obtener puntuación original
                    try:
                        puntuacion = float(producto.get(puntuacion_key, 3.0))
                    except (ValueError, TypeError):
                        puntuacion = 3.0
                    puntuaciones.append(puntuacion)
                    
                    # Calcular sentimiento
                    sentimiento = self.calcular_sentimiento(comentario)
                    sentimientos.append(sentimiento)
            
            # Calcular promedios
            if sentimientos:
                sentimiento_promedio = statistics.mean(sentimientos)
                puntuacion_promedio = statistics.mean(puntuaciones)
            else:
                sentimiento_promedio = 3.0
                puntuacion_promedio = 3.0
            
            # Obtener precio
            try:
                precio = float(re.sub(r'[^\d.]', '', str(producto.get('precio', '0'))))
            except (ValueError, TypeError):
                precio = 0.0
            
            # Crear resultado con todos los datos del producto original
            resultado = producto.copy()
            resultado.update({
                'nombre_producto': producto.get('nombre', 'Sin nombre'),
                'sentimiento_promedio': round(sentimiento_promedio, 2),
                'calificacion_promedio': round(puntuacion_promedio, 2),
                'precio': precio,
                'estrellas': float(producto.get('estrellas', 0)) if es_valor_valido(producto.get('estrellas')) else 0.0,
                'num_comentarios': len(comentarios),
                'url': producto.get('url', '')
            })
            
            resultados_productos.append(resultado)
        
        return resultados_productos

# =====================================
# FUNCIONES DEL SISTEMA EXPERTO
# =====================================

def aplicar_sistema_experto_a_productos(productos_con_sentimiento):
    """
    Aplica el sistema experto a productos con análisis de sentimiento
    
    Args:
        productos_con_sentimiento (list): Lista de productos con sentimiento analizado
    
    Returns:
        list: Lista de productos con recomendaciones del sistema experto
    """
    productos_con_recomendaciones = []
    
    for producto in productos_con_sentimiento:
        # Obtener el sentimiento promedio
        sentimiento_numerico = producto.get('sentimiento_promedio', 3.0)
        sentimiento_categoria = clasificar_sentimiento(sentimiento_numerico)
        
        # Detectar aspectos en los comentarios del producto original
        aspectos_detectados = {'aroma': False, 'precio': False, 'envio': False}
        
        # Buscar en comentarios del producto (si existen)
        for i in range(1, 6):
            comentario_key = f'comentario_{i}'
            if comentario_key in producto and es_valor_valido(producto[comentario_key]):
                comentario_texto = producto[comentario_key]
                aspectos_comentario = detectar_aspectos(comentario_texto)
                # Combinar aspectos (OR lógico)
                for aspecto in aspectos_detectados:
                    aspectos_detectados[aspecto] = (
                        aspectos_detectados[aspecto] or aspectos_comentario[aspecto]
                    )
        
        # Ejecutar sistema experto
        recomendaciones = ejecutar_sistema_experto(sentimiento_categoria, aspectos_detectados)
        
        # Agregar recomendación al producto
        producto_con_recomendacion = producto.copy()
        producto_con_recomendacion['recomendacion_experto'] = recomendaciones[0] if recomendaciones else "Sin recomendación específica"
        producto_con_recomendacion['aspectos_detectados'] = aspectos_detectados
        producto_con_recomendacion['sentimiento_categoria'] = sentimiento_categoria
        
        productos_con_recomendaciones.append(producto_con_recomendacion)
    
    return productos_con_recomendaciones

def mostrar_recomendaciones_experto(df_sentimientos):
    """Muestra las recomendaciones del sistema experto en Streamlit"""
    st.subheader("🧠 Recomendaciones del Sistema Experto")
    
    # Aplicar sistema experto
    productos_con_recomendaciones = aplicar_sistema_experto_a_productos(
        df_sentimientos.to_dict('records')
    )
    
    # Crear DataFrame con recomendaciones
    df_recomendaciones = pd.DataFrame(productos_con_recomendaciones)
    
    # Mostrar estadísticas de recomendaciones
    col1, col2, col3 = st.columns(3)
    
    with col1:
        recomendados = len(df_recomendaciones[df_recomendaciones['recomendacion_experto'].str.contains('RECOMENDADO', na=False)])
        st.metric("Productos Recomendados", recomendados)
    
    with col2:
        no_recomendados = len(df_recomendaciones[df_recomendaciones['recomendacion_experto'].str.contains('NO RECOMENDADO', na=False)])
        st.metric("No Recomendados", no_recomendados)
    
    with col3:
        neutrales = len(df_recomendaciones) - recomendados - no_recomendados
        st.metric("Evaluación Neutral", neutrales)
    
    # Mostrar productos recomendados
    productos_recomendados = df_recomendaciones[
        df_recomendaciones['recomendacion_experto'].str.contains('RECOMENDADO', na=False) &
        ~df_recomendaciones['recomendacion_experto'].str.contains('NO RECOMENDADO', na=False)
    ].sort_values('sentimiento_promedio', ascending=False)
    
    if not productos_recomendados.empty:
        st.subheader("🏆 Productos Recomendados por el Sistema Experto")
        for idx, producto in productos_recomendados.head(10).iterrows():
            with st.expander(f"⭐ {producto['nombre_producto'][:50]}... - {producto['sentimiento_promedio']} ⭐"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Recomendación:** {producto['recomendacion_experto']}")
                    st.write(f"**Sentimiento:** {producto['sentimiento_promedio']} ({producto['sentimiento_categoria']})")
                    st.write(f"**Precio:** ${producto['precio']:,.0f}")
                with col2:
                    st.write("**Aspectos Detectados:**")
                    aspectos = producto['aspectos_detectados']
                    st.write(f"- Aroma: {'Si' if aspectos['aroma'] else 'No'}")
                    st.write(f"- Precio: {'Si' if aspectos['precio'] else 'No'}")
                    st.write(f"- Envío: {'Si' if aspectos['envio'] else 'No'}")
                    if producto.get('url'):
                        st.link_button("Ver en MercadoLibre", producto['url'])
    
    return df_recomendaciones

# =====================================
# APLICACIÓN PRINCIPAL
# =====================================

def main():
    st.title("🛒 MercadoLibre Scraper & Análisis de Sentimientos")
    st.markdown("---")
    
    # Sidebar para configuración
    st.sidebar.header("⚙️ Configuración")

    # NUEVO: Selector de método
    st.sidebar.markdown("### 🔌 Método de Extracción")
    method = st.sidebar.radio(
        "Selecciona cómo obtener los datos:",
        ("🎯 Modo Demo (Recomendado)", "✅ API Oficial", "🕷️ Web Scraping"),
        help="Demo: Usa datos de ejemplo para demostrar las funcionalidades. API/Scraping: Pueden estar bloqueados."
    )
    use_demo = "Demo" in method
    use_api = "API" in method

    if use_demo:
        st.sidebar.success("🎯 Usando datos de demostración - Funciona 100%")
    elif use_api:
        st.sidebar.warning("⚠️ API puede estar bloqueada por MercadoLibre")
    else:
        st.sidebar.warning("⚠️ Scraping puede fallar en Streamlit Cloud debido a bloqueos de ML")

    st.sidebar.markdown("---")

    # Parámetros de búsqueda
    if not use_demo:
        search_term = st.sidebar.text_input("Término de búsqueda", value="vinos", help="Ejemplo: vinos, autos, cascos moto")
    else:
        search_term = "vinos"  # Fijo para demo
        st.sidebar.info("💡 En modo demo se muestran datos de ejemplo de vinos")

    if not use_api and not use_demo:
        max_pages = st.sidebar.slider("Número de páginas", 1, 5, 1)
    else:
        max_pages = 1  # La API y demo manejan límites diferentes

    get_comments = st.sidebar.checkbox("Obtener comentarios", value=True)

    # Modo debugging (solo para scraping)
    if not use_api and not use_demo:
        st.sidebar.markdown("---")
        debug_mode = st.sidebar.checkbox("🐛 Modo Debug", value=False, help="Muestra información detallada del proceso de scraping para diagnosticar problemas")
    else:
        debug_mode = False

    if get_comments and not use_demo:
        # Calcular el máximo teórico de productos según las páginas seleccionadas
        estimated_max_products = max_pages * 50  # Aproximadamente 50 productos por página

        # Mostrar información sobre productos estimados
        st.sidebar.info(f"📊 Productos estimados: ~{estimated_max_products} productos en {max_pages} página(s)")

        # Permitir seleccionar hasta el máximo estimado de productos
        max_products_comments = st.sidebar.slider(
            "Productos para comentarios",
            1,
            estimated_max_products,
            min(50, estimated_max_products),  # Valor por defecto: mínimo entre 50 y el máximo estimado
            help=f"Puedes seleccionar hasta {estimated_max_products} productos para extraer comentarios"
        )

        # Mostrar tiempo estimado
        estimated_time_minutes = max_products_comments * 0.1  # Aproximadamente 6 segundos por producto
        st.sidebar.warning(f"⏱️ Tiempo estimado: ~{estimated_time_minutes:.1f} minutos")
    elif use_demo:
        max_products_comments = 7  # Número fijo de productos demo
    else:
        max_products_comments = 0
    
    # Botón de inicio
    if use_demo:
        button_label = "🎯 Cargar Datos Demo"
    elif use_api:
        button_label = "🚀 Iniciar Búsqueda"
    else:
        button_label = "🚀 Iniciar Scraping"

    if st.sidebar.button(button_label, type="primary"):
        if search_term:
            st.header(f"🔍 Resultados para: {search_term}")

            productos = []

            if use_demo:
                # Usar datos de demostración
                st.info("🎯 Cargando datos de demostración...")
                with st.spinner("Generando productos de ejemplo..."):
                    import time
                    time.sleep(0.5)  # Simular carga
                    num_productos = min(max_products_comments if get_comments else 7, 7)
                    productos = generar_datos_demo(num_productos)
                    st.success(f"✅ Se cargaron {len(productos)} productos de demostración")

            elif use_api:
                # Usar API oficial
                st.info("🔌 Conectando con la API oficial de MercadoLibre...")
                api = MercadoLibreAPI()

                with st.spinner("Obteniendo productos desde la API..."):
                    limit = min(max_products_comments if get_comments else 50, 50)
                    productos = api.search_products(search_term, limit=limit)

                    if productos and get_comments:
                        st.info(f"📝 Obteniendo comentarios de {len(productos)} productos...")
                        progress_bar = st.progress(0)

                        for idx, producto in enumerate(productos):
                            if 'id' in producto and producto['id']:
                                reviews = api.get_product_reviews(producto['id'], max_reviews=5)

                                # Agregar comentarios al producto
                                for i, review in enumerate(reviews):
                                    producto[f'comentario_{i+1}'] = review['comentario']
                                    producto[f'puntuacion_comentario_{i+1}'] = review['puntuacion']

                                # Rellenar comentarios faltantes
                                for i in range(len(reviews), 5):
                                    producto[f'comentario_{i+1}'] = ""
                                    producto[f'puntuacion_comentario_{i+1}'] = ""

                            progress_bar.progress((idx + 1) / len(productos))
                            time.sleep(0.1)  # Pequeña pausa para no saturar la API

                        progress_bar.empty()

            else:
                # Usar scraping tradicional
                scraper = MercadoLibreScraper()

                with st.spinner("Realizando scraping..."):
                    productos = scraper.scrape_products(
                        search_term=search_term,
                        max_pages=max_pages,
                        get_comments=get_comments,
                        max_products_comments=max_products_comments,
                        debug=debug_mode
                    )
            
            if productos:
                st.success(f"✅ Se encontraron {len(productos)} productos")
                
                # Convertir a DataFrame
                df_productos = pd.DataFrame(productos)
                
                # Tabs para mostrar resultados
                tab1, tab2, tab3, tab4 = st.tabs(["📊 Datos Extraídos", "🎯 Análisis de Sentimientos", "🧠 Sistema Experto", "📥 Descargas"])
                
                with tab1:
                    st.subheader("Datos de Productos Extraídos")
                    
                    # Mostrar estadísticas básicas
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Productos", len(productos))
                    with col2:
                        productos_con_precio = df_productos[df_productos['precio'].astype(str) != '0']
                        if not productos_con_precio.empty:
                            try:
                                precio_promedio = pd.to_numeric(productos_con_precio['precio'], errors='coerce').mean()
                                st.metric("Precio Promedio", f"${precio_promedio:,.0f}" if not pd.isna(precio_promedio) else "N/A")
                            except:
                                st.metric("Precio Promedio", "N/A")
                        else:
                            st.metric("Precio Promedio", "N/A")
                    with col3:
                        productos_con_estrellas = df_productos[df_productos['estrellas'].astype(str) != '0']
                        if not productos_con_estrellas.empty:
                            try:
                                estrellas_promedio = pd.to_numeric(productos_con_estrellas['estrellas'], errors='coerce').mean()
                                st.metric("Estrellas Promedio", f"{estrellas_promedio:.1f}" if not pd.isna(estrellas_promedio) else "N/A")
                            except:
                                st.metric("Estrellas Promedio", "N/A")
                        else:
                            st.metric("Estrellas Promedio", "N/A")
                    with col4:
                        productos_con_comentarios = sum(1 for p in productos if any(es_valor_valido(p.get(f'comentario_{i}', '')) for i in range(1, 6)))
                        st.metric("Con Comentarios", productos_con_comentarios)
                    
                    # Mostrar tabla de productos
                    st.dataframe(df_productos, use_container_width=True)
                
                with tab2:
                    if get_comments:
                        st.subheader("🎯 Análisis de Sentimientos")
                        
                        # Realizar análisis de sentimientos
                        analizador = AnalizadorSentimiento()
                        
                        with st.spinner("Analizando sentimientos..."):
                            resultados_sentimiento = analizador.analizar_productos(productos)
                        
                        if resultados_sentimiento:
                            df_sentimientos = pd.DataFrame(resultados_sentimiento)
                            
                            # Métricas de sentimiento
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                sent_promedio = df_sentimientos['sentimiento_promedio'].mean()
                                st.metric("Sentimiento Promedio", f"{sent_promedio:.2f} ⭐")
                            with col2:
                                if not df_sentimientos.empty:
                                    mejor_producto = df_sentimientos.loc[df_sentimientos['sentimiento_promedio'].idxmax()]
                                    st.metric("Mejor Valorado", f"{mejor_producto['sentimiento_promedio']:.2f} ⭐")
                                else:
                                    st.metric("Mejor Valorado", "N/A")
                            with col3:
                                total_con_comentarios = len(df_sentimientos[df_sentimientos['num_comentarios'] > 0])
                                st.metric("Productos Analizados", total_con_comentarios)
                            
                            # Top 10 productos por sentimiento
                            st.subheader("🏆 Top 10 Productos por Sentimiento")
                            top_productos = df_sentimientos.nlargest(10, 'sentimiento_promedio')
                            
                            for idx, producto in top_productos.iterrows():
                                with st.expander(f"#{idx+1} {producto['nombre_producto'][:60]}... - {producto['sentimiento_promedio']} ⭐"):
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.write(f"**Sentimiento:** {producto['sentimiento_promedio']} ⭐")
                                        st.write(f"**Calificación Original:** {producto['calificacion_promedio']}")
                                        st.write(f"**Precio:** ${producto['precio']:,.0f}")
                                    with col2:
                                        st.write(f"**Estrellas ML:** {producto['estrellas']}")
                                        st.write(f"**Comentarios:** {producto['num_comentarios']}")
                                        if producto.get('url'):
                                            st.link_button("Ver en MercadoLibre", producto['url'])
                            
                            # Tabla completa de resultados de sentimiento
                            st.subheader("📊 Resultados Completos")
                            st.dataframe(df_sentimientos.sort_values('sentimiento_promedio', ascending=False), use_container_width=True)
                            
                            # Guardar resultados en session state para otras pestañas
                            st.session_state['df_sentimientos'] = df_sentimientos
                    else:
                        st.info("Para realizar análisis de sentimientos, activa la opción 'Obtener comentarios' en la configuración.")
                
                with tab3:
                    if get_comments and 'df_sentimientos' in st.session_state:
                        # Mostrar recomendaciones del sistema experto
                        df_recomendaciones = mostrar_recomendaciones_experto(st.session_state['df_sentimientos'])
                        st.session_state['df_recomendaciones'] = df_recomendaciones
                    else:
                        st.info("Para usar el sistema experto, activa la opción 'Obtener comentarios' en la configuración y ejecuta el análisis de sentimientos.")
                
                with tab4:
                    st.subheader("📥 Descargar Resultados")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write("**Datos de Productos**")
                        
                        # Crear CSV de productos
                        csv_productos = df_productos.to_csv(index=False, encoding='utf-8')
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename_productos = f"{search_term.replace(' ', '_')}_productos_{timestamp}.csv"
                        
                        st.download_button(
                            label="⬇️ Descargar CSV Productos",
                            data=csv_productos,
                            file_name=filename_productos,
                            mime='text/csv'
                        )
                    
                    with col2:
                        if 'df_sentimientos' in st.session_state:
                            st.write("**Análisis de Sentimientos**")
                            
                            # Crear CSV de sentimientos
                            csv_sentimientos = st.session_state['df_sentimientos'].to_csv(index=False, encoding='utf-8')
                            filename_sentimientos = f"{search_term.replace(' ', '_')}_sentimientos_{timestamp}.csv"
                            
                            st.download_button(
                                label="⬇️ Descargar CSV Sentimientos",
                                data=csv_sentimientos,
                                file_name=filename_sentimientos,
                                mime='text/csv'
                            )
                        else:
                            st.info("No hay datos de sentimientos para descargar.")
                    
                    with col3:
                        if 'df_recomendaciones' in st.session_state:
                            st.write("**Sistema Experto**")
                            
                            # Crear CSV de recomendaciones
                            csv_recomendaciones = st.session_state['df_recomendaciones'].to_csv(index=False, encoding='utf-8')
                            filename_recomendaciones = f"{search_term.replace(' ', '_')}_recomendaciones_{timestamp}.csv"
                            
                            st.download_button(
                                label="⬇️ Descargar CSV Recomendaciones",
                                data=csv_recomendaciones,
                                file_name=filename_recomendaciones,
                                mime='text/csv'
                            )
                        else:
                            st.info("No hay recomendaciones del sistema experto para descargar.")
                
                # Guardar productos en session state
                st.session_state['productos'] = productos
                st.session_state['df_productos'] = df_productos
                
            else:
                st.error("❌ No se pudieron encontrar productos. Intenta con otro término de búsqueda.")
        else:
            st.warning("⚠️ Por favor, ingresa un término de búsqueda.")
    
    # Sección de información
    st.markdown("---")
    
    # Mostrar resultados previos si existen
    if 'productos' in st.session_state and st.session_state['productos']:
        st.header("📋 Sesión Actual")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"Productos cargados: {len(st.session_state['productos'])}")
        with col2:
            if st.button("🗑️ Limpiar Datos"):
                for key in ['productos', 'df_productos', 'df_sentimientos', 'df_recomendaciones']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
    
    # Sección de ayuda e información
    with st.expander("ℹ️ Información y Ayuda"):
        st.markdown("""
        ### 🎯 ¿Qué hace esta aplicación?
        
        Esta herramienta permite:
        - **Extraer productos** de MercadoLibre mediante web scraping
        - **Obtener comentarios** y calificaciones de productos
        - **Analizar sentimientos** de los comentarios usando procesamiento de lenguaje natural
        - **Sistema Experto** para recomendaciones basadas en reglas de negocio
        - **Descargar resultados** en formato CSV
        
        ### 🚀 Cómo usar:
        
        1. **Configura la búsqueda** en el panel lateral:
           - Ingresa el término de búsqueda (ej: "vinos", "notebooks", "celulares")
           - Selecciona el número de páginas a analizar (1-5 páginas)
           - Activa la extracción de comentarios si deseas análisis de sentimiento
           - Selecciona cuántos productos analizar (hasta 250 productos)
        
        2. **Inicia el scraping** haciendo clic en "Iniciar Scraping"
        
        3. **Revisa los resultados** en las pestañas:
           - **Datos Extraídos**: Información básica de productos
           - **Análisis de Sentimientos**: Valoración automática de comentarios
           - **Sistema Experto**: Recomendaciones basadas en reglas
           - **Descargas**: Descarga los resultados en CSV
        
        ### 🧠 Sistema Experto:
        
        El sistema experto aplica reglas de negocio para generar recomendaciones:
        - **Análisis de aspectos**: Detecta menciones de aroma, precio y envío
        - **Reglas de inferencia**: Aplica lógica experta para recomendar productos
        - **Explicabilidad**: Cada recomendación incluye la justificación
        
        ### 📊 Análisis de Sentimientos:
        
        El sistema analiza automáticamente los comentarios y asigna una puntuación de 1 a 5 estrellas basada en:
        - **Palabras positivas**: excelente, bueno, recomendable, etc.
        - **Palabras negativas**: malo, terrible, decepcionante, etc.
        - **Modificadores**: muy, super, bastante (intensifican el sentimiento)
        - **Negaciones**: no, nunca, jamás (invierten el sentimiento)
        
        ### ⚠️ Consideraciones:
        
        - El scraping puede tomar varios minutos dependiendo del número de páginas y productos
        - Cada producto con comentarios toma aproximadamente 6 segundos en procesarse
        - **Tiempo estimado para 250 productos: ~25 minutos**
        - Algunos productos pueden no tener comentarios disponibles
        - Los resultados dependen de la estructura actual de MercadoLibre
        - Se incluyen pausas entre solicitudes para evitar bloqueos
        
        ### 🔧 Parámetros Recomendados:
        
        - **Para pruebas rápidas**: 1 página, 10-20 productos con comentarios (~2-3 minutos)
        - **Para análisis medio**: 2-3 páginas, 50-100 productos con comentarios (~8-15 minutos)
        - **Para análisis completo**: 4-5 páginas, 150-250 productos con comentarios (~20-25 minutos)
        
        ### 📁 Archivos de Salida:
        
        - **Productos CSV**: Contiene toda la información extraída de productos
        - **Sentimientos CSV**: Contiene el análisis de sentimientos resumido por producto
        - **Recomendaciones CSV**: Contiene las recomendaciones del sistema experto
        """)
    
    # Footer con información adicional
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 20px;'>
            <p>🛒 <strong>MercadoLibre Scraper & Análisis</strong> - Versión Completa con Sistema Experto</p>
            <p>Herramienta para extracción y análisis de productos de MercadoLibre</p>
            <p><em>Desarrollado con Streamlit y Python - Incluye Sistema Experto Integrado</em></p>
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()