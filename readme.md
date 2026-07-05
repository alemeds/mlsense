# 🛍️ MLSENSE v2

**Multi-categoría | Análisis de Sentimientos | Sistema Experto Configurable**

MLSENSE es una aplicación de análisis de sentimientos dirigida por datos y sistema experto inteligente para productos de e-commerce, desarrollada con **Streamlit** sin dependencias de APIs externas, credenciales o conexiones en vivo a MercadoLibre.

## 🎯 Características

### 📊 Análisis Generalizado de Sentimientos
- **Léxico multilenguaje**: Soporte completo para español rioplatense con al menos 400 términos
- **Manejo de contexto**: Negadores (no, nunca, jamás) invierten polaridad en ventana de 3 palabras
- **Intensificadores y atenuadores**: "muy", "re", "super" amplifican; "poco", "algo" reducen
- **Detección de aspectos**: Análisis local de opiniones por característica (aroma, sabor, durabilidad, etc.)
- **Rioplatensismos**: Reconocimiento nativo de términos coloquiales ("bárbaro", "berreta", "trucho", "joya")

### 🧠 Sistema Experto Inteligente
- **Dirigido por configuración JSON**: Carga reglas por categoría desde archivos JSON estructurados
- **Forward-chaining**: Evalúa todas las reglas aplicables y resuelve por confianza máxima
- **Trazabilidad completa**: Muestra qué reglas dispararon y por qué para cada producto
- **Multi-categoría**: Incluye configuraciones predefinidas para vinos, electrónica e indumentaria

### 📥 Cuatro Modos de Entrada de Datos

#### Modo A: HTML Subido (Principal) ⭐
Sube archivos HTML de páginas de MercadoLibre guardadas con "Guardar página como":
- Extrae datos de bloques JSON-LD (`<script type="application/ld+json">`)
- Fallback a `window.__PRELOADED_STATE__` (estructuras React/Next.js)
- Fallback DOM parsing tolerante a cambios de estructura
- Campos: nombre, precio, moneda, estrellas, calificaciones, envío, descuento, URL, comentarios

#### Modo B: URL de Producto (Best-Effort)
Pega un permalink individual de MercadoLibre:
- Fetch con headers de navegador real
- Degradación automática de SSL si es necesario (loguea warning)
- Manejo robusto de 403/429 (bloques de IP)
- Timeout 15s

#### Modo C: Datos Demo
Generador realista de 20-50 productos por categoría:
- Precios y ratings variados
- Comentarios en español rioplatense con distribución natural de sentimientos
- Semilla configurable para reproducibilidad
- Sin requiere acceso a internet

#### Modo D: 🔎 Búsqueda en Vivo (Beta) ⚠️
Busca directamente en MercadoLibre y extrae resultados en tiempo real:
- Input de término (ej: "celular samsung a56")
- Slider 5-30 productos
- Opción de traer comentarios (más lento, requiere fetches individuales)
- **Pausas aleatorias** 1.5-3.5s entre requests y **User-Agent rotativo** (respetuoso)
- **Manejo de bloqueos**: Si MercadoLibre bloquea la IP (habitual en Streamlit Cloud), muestra warning claro y sugiere Modo A
- **Cache de 15 minutos**: Evita repetir requests del mismo término en la sesión
- **⚠️ Advertencia**: No funciona en Streamlit Cloud (MercadoLibre bloquea IPs de datacenter). Ejecutá localmente o usá Modo A

## 🏗️ Arquitectura

```
mlsense/
├── ml_scraper_final.py        # Entrypoint (Streamlit Cloud)
├── mlsense/
│   ├── __init__.py
│   ├── app.py                 # UI Streamlit completa
│   ├── sentiment.py           # Motor de análisis de sentimientos
│   ├── expert.py              # Sistema experto forward-chaining
│   ├── parsers.py             # Parsing de HTML de MELI
│   ├── fetcher.py             # Fetch de URLs con degradación
│   └── demo_data.py           # Generador de datos demo
├── lexicons/
│   ├── lexicon_general.json    # Léxico base español rioplatense
│   ├── categoria_vinos.json    # Reglas y aspectos para vinos
│   ├── categoria_electronica.json
│   └── categoria_indumentaria.json
├── tests/
│   └── test_core.py           # 33 tests (pytest)
├── requirements.txt
└── setup.py
```

## 🚀 Instalación y Uso Local

### 1. Clonar el repositorio
```bash
git clone https://github.com/alemeds/mlsense.git
cd mlsense
```

### 2. Crear entorno virtual (recomendado)
```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecutar la app
```bash
streamlit run ml_scraper_final.py
```

La app se abrirá en `http://localhost:8501`

## 📖 Guía de Uso

### Flujo Principal: Guardar Página → Subir HTML

1. **En navegador (Chrome, Firefox, Edge, Safari):**
   - Visita un producto en mercadolibre.com.ar
   - Click derecho → "Guardar página como" → Guardar como `.html`

2. **En MLSENSE (Modo HTML):**
   - Elige categoría en sidebar
   - Selecciona "HTML subido"
   - Sube el archivo `.html`
   - Automáticamente extrae: nombre, precio, comentarios, etc.

3. **Analiza:**
   - **Tab Datos Extraídos**: Tabla con todos los productos
   - **Tab Sentimientos**: Análisis individual de cada comentario, gráficos de distribución
   - **Tab Sistema Experto**: Recomendaciones (COMPRAR, EVITAR, ESPERAR OFERTA) con trazabilidad
   - **Tab Comparación**: Scatter price vs. sentiment, tabla ordenable
   - **Tab Descargas**: Exporta como CSV/JSON

## 📋 Formato de Configuración de Categoría

Las categorías se definen en JSON con este esquema:

```json
{
  "categoria": "vinos",
  "nombre_display": "Vinos",
  "aspectos": {
    "aroma": ["aroma", "olor", "bouquet", "nariz"],
    "sabor": ["sabor", "gusto", "boca", "taninos", "cuerpo"],
    "precio": ["precio", "caro", "barato", "vale"]
  },
  "reglas": [
    {
      "si": {"sentimiento_min": 0.6, "aspecto": "aroma", "aspecto_min": 0.3},
      "entonces": {
        "recomendacion": "COMPRAR",
        "confianza": 0.95,
        "razon": "Aroma excepcional y sentimiento muy positivo"
      }
    },
    {
      "si": {"sentimiento_max": -0.5},
      "entonces": {
        "recomendacion": "EVITAR",
        "confianza": 0.9,
        "razon": "Predominan reseñas negativas"
      }
    }
  ],
  "regla_default": {
    "recomendacion": "NEUTRAL",
    "confianza": 0.5,
    "razon": "Sin información suficiente"
  }
}
```

### Sintaxis de Condiciones (`si`)
- `sentimiento_min`: Score mínimo global (-1 a 1)
- `sentimiento_max`: Score máximo global
- `aspecto`: Nombre del aspecto a evaluar
- `aspecto_min`: Score mínimo del aspecto
- `aspecto_max`: Score máximo del aspecto

Las condiciones se combinan con AND lógico.

## 🧪 Testing

```bash
# Ejecutar todos los tests (33 casos)
pytest tests/ -v

# Solo tests de sentimientos
pytest tests/test_core.py::TestAnalizadorSentimiento -v

# Solo tests de búsqueda
pytest tests/test_core.py::TestBuildSearchUrl -v

# Con cobertura
pytest tests/ --cov=mlsense
```

**Cobertura mínima**: Análisis de sentimientos (positivos, negativos, negadores, intensificadores), sistema experto (evaluación de reglas, inferencia), parsing HTML (JSON-LD, __PRELOADED_STATE__), normalización de URL de búsqueda.

## 🔧 Arquitectura Interna

### `sentiment.py`
Motor léxico basado en diccionarios con corrección de contexto:
- Normalización: minúsculas, sin tildes, sin repeticiones
- Tokenización simple por palabras
- Multiplificador de contexto para negadores/intensificadores/atenuadores
- Detección de aspectos con ventana ±4 palabras

### `expert.py`
Sistema experto forward-chaining:
- Carga reglas desde JSON (validación de esquema)
- Evalúa condiciones en orden
- Dispara todas las reglas que matchean
- Resuelve por máxima confianza (tiebreaker)
- Expone traza de inferencia

### `parsers.py`
Estrategia multi-layer de extracción de HTML:
1. JSON-LD estructurado (W3C Microdata)
2. `__PRELOADED_STATE__` (React/Next.js)
3. DOM parsing con regex tolerante a cambios

### `fetcher.py`
Fetch robusto con degradación:
- Headers de navegador real
- SSL con verificación primero
- Downgrade a `CERT_NONE` en fallback (loguea warning)
- Manejo de 403 (IP bloqueada), 429 (rate limit), timeouts

### `demo_data.py`
Generador paramétrico de datos realistas:
- 400+ comentarios únicos en español rioplatense
- Distribución verosímil de sentimientos (positivos, negativos, mixtos, neutros)
- Semilla para reproducibilidad

## 📊 Interfaz Streamlit

**Sidebar (Control Central)**
- Selector de categoría (vinos / electrónica / indumentaria)
- Selector de modo (Demo / HTML / URL)
- Uploader de HTML o input de URL
- Disclaimer académico

**5 Tabs**
1. **Datos Extraídos**: Tabla con todos los campos, métricas resumidas
2. **Análisis de Sentimientos**: Tabla de scores por producto, histogramas, pie charts
3. **Sistema Experto**: Cards de recomendación por producto con expanders de trazabilidad
4. **Comparación**: Scatter price vs. sentiment, gráfico de barras, tabla
5. **Descargas**: CSV/JSON del análisis completo

## 🌍 Deployment en Streamlit Cloud

No requiere cambios:
1. Push a `main` en GitHub
2. Streamlit Cloud detecta el push
3. Redeploya automáticamente (mismo entrypoint `ml_scraper_final.py`)

Disponible en: https://mlsense.streamlit.app

## 📝 Especificaciones Técnicas

- **Lenguaje**: Python 3.8+
- **Framework**: Streamlit 1.28.0+
- **Dependencias**: pandas, plotly (sin sklearn, transformers, APIs externas)
- **Tests**: 26 casos con pytest
- **Cobertura mínima**: 80% en lógica de negocio

## 🔐 Seguridad y Privacidad

- ✅ **Sin hardcoding de credenciales**: Todo en `.env` (no incluido en repo)
- ✅ **Sin APIs externas**: Solo datos provistos por usuario
- ✅ **Sin almacenamiento en servidor**: Análisis local, sesiones volátiles
- ✅ **SSL verificado**: Fetch con contexto seguro primero
- ✅ **Validación de entrada**: Sanitización de HTML, manejo de excepciones

## 📄 Licencia

Proyecto académico sin afiliación con MercadoLibre.

## 🤝 Contribuir

Las mejoras se aceptan vía PR. Asegurate de:
- Ejecutar `pytest tests/ -q` antes de pushear
- Mantener compatibilidad con Streamlit Cloud
- Documentar cambios en README

---

**MLSENSE v2** — Empodérando decisiones de compra con análisis de sentimientos transparente y controlado por el usuario.
