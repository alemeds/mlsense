# 🔧 Troubleshooting - MLSense

## ⚠️ Problema: "No se pudieron extraer productos"

### Causas Comunes

#### 1. **MercadoLibre está bloqueando el scraping**
MercadoLibre detecta el tráfico automatizado y puede bloquear las peticiones.

**Síntomas:**
- Error HTTP 403 (Forbidden)
- La página se carga pero no se extraen productos
- Funciona localmente pero no en Streamlit Cloud

**Soluciones:**

1. **Activar modo Debug** en la aplicación:
   - Marca la casilla "🐛 Modo Debug" en el sidebar
   - Ejecuta el scraping nuevamente
   - Revisa los mensajes de error detallados

2. **Usar la API oficial de MercadoLibre** (Recomendado):
   - Registrarse en: https://developers.mercadolibre.com.ar
   - Obtener credenciales de API
   - Implementar autenticación OAuth
   - Beneficios: Más confiable, no hay bloqueos, datos estructurados

3. **Reducir la frecuencia de peticiones**:
   - Usar menos páginas (1-2 máximo)
   - Extraer comentarios de menos productos (10-20)
   - Aumentar el tiempo entre peticiones

4. **Probar con otro término de búsqueda**:
   - Algunos términos pueden tener restricciones específicas
   - Prueba con términos simples como "vino", "laptop", etc.

#### 2. **Restricciones de Streamlit Cloud**

**Síntomas:**
- Funciona perfectamente en local
- Falla solo en Streamlit Cloud
- Timeout errors

**Soluciones:**

1. **Limitaciones de red conocidas**:
   - Streamlit Cloud tiene timeouts de 30 segundos
   - Algunas peticiones externas pueden estar bloqueadas
   - No todas las configuraciones SSL son compatibles

2. **Ejecutar localmente**:
   ```bash
   git clone https://github.com/alemeds/mlsense.git
   cd mlsense
   pip install -r requirements.txt
   streamlit run ml_scraper_final.py
   ```

#### 3. **Estructura HTML de MercadoLibre cambió**

**Síntomas:**
- Se obtiene HTML pero no se extraen productos
- El modo debug muestra HTML recibido pero vacío de productos

**Soluciones:**

1. **Actualizar los selectores**:
   - Los patrones regex en `extract_traditional_way()` pueden estar desactualizados
   - MercadoLibre actualiza su estructura frecuentemente

2. **Usar API oficial** (solución permanente)

## 🚀 Alternativas Recomendadas

### Opción 1: API Oficial de MercadoLibre

**Ventajas:**
- ✅ No hay bloqueos
- ✅ Datos estructurados y confiables
- ✅ Mayor límite de peticiones
- ✅ Documentación completa
- ✅ Soporte oficial

**Implementación básica:**

```python
import requests

# 1. Obtener credenciales en: https://developers.mercadolibre.com.ar
APP_ID = "tu_app_id"
SECRET_KEY = "tu_secret_key"

# 2. Buscar productos
def search_products(query):
    url = f"https://api.mercadolibre.com/sites/MLA/search?q={query}"
    response = requests.get(url)
    return response.json()

# 3. Obtener reviews de un producto
def get_reviews(product_id):
    url = f"https://api.mercadolibre.com/reviews/item/{product_id}"
    response = requests.get(url)
    return response.json()
```

### Opción 2: Servicios de Scraping Profesionales

Si necesitas continuar con scraping:

- **ScraperAPI**: https://www.scraperapi.com/
- **Bright Data**: https://brightdata.com/
- **Apify**: https://apify.com/

Estos servicios manejan:
- Rotación de IPs
- Evasión de bloqueos
- Renderizado de JavaScript
- CAPTCHA solving

### Opción 3: Datos Pre-extraídos

Para propósitos académicos:
- Usar datasets públicos de e-commerce
- Kaggle tiene varios datasets de MercadoLibre
- Crear un dataset de prueba con datos sintéticos

## 🐛 Cómo usar el Modo Debug

1. **Activar en el sidebar**: Marca "🐛 Modo Debug"
2. **Ejecutar scraping**: Haz clic en "Iniciar Scraping"
3. **Revisar los mensajes**:
   - 🔍 URL generada
   - 📡 Intentos de acceso
   - ✅ Estado HTTP recibido
   - ⚠️ Advertencias de parsing
   - ❌ Errores específicos
4. **Ver HTML recibido**: Expande "Ver muestra del HTML recibido"
5. **Compartir logs**: Captura los mensajes para reportar issues

## 📝 Checklist de Diagnóstico

Antes de reportar un problema, verifica:

- [ ] ¿Activaste el modo Debug?
- [ ] ¿Probaste con un término de búsqueda simple ("vino")?
- [ ] ¿Redujiste el número de páginas a 1?
- [ ] ¿Funciona en local pero no en Streamlit Cloud?
- [ ] ¿Revisaste los mensajes de error específicos?
- [ ] ¿Probaste desactivar "Obtener comentarios"?
- [ ] ¿Revisaste la URL generada en modo debug?

## 🆘 Soporte

### Reportar un Bug

Crea un issue en GitHub con:
1. **Modo debug activado**: Captura de pantalla de los errores
2. **Configuración usada**: Término de búsqueda, páginas, etc.
3. **Entorno**: Local o Streamlit Cloud
4. **HTML recibido**: Si es posible, la muestra del HTML

### Contacto

- **GitHub Issues**: https://github.com/alemeds/mlsense/issues
- **Email**: alemeds@hotmail.com

## ⚡ Solución Rápida Temporal

Si necesitas que funcione YA para una presentación:

1. **Ejecuta localmente**: No uses Streamlit Cloud temporalmente
2. **Usa datos de ejemplo**: Carga un CSV pre-generado
3. **Modo demo**: Crea productos de prueba manualmente

```python
# Código de ejemplo para datos de prueba
productos_demo = [
    {
        'nombre': 'Vino Malbec Premium',
        'precio': '5000',
        'estrellas': '4.5',
        'calificaciones': '120',
        'comentario_1': 'Excelente vino, muy buen aroma',
        'puntuacion_comentario_1': '5',
        # ... más comentarios
    }
]
```

## 🔮 Roadmap de Mejoras

Próximas actualizaciones para resolver estos problemas:

- [ ] Migración a API oficial de MercadoLibre
- [ ] Caché de resultados para reducir peticiones
- [ ] Modo "demo" con datos de ejemplo
- [ ] Integración con ScraperAPI
- [ ] Base de datos para almacenar resultados históricos
- [ ] Exportación/importación de datasets

---

**Última actualización**: 2025-01-XX
**Versión**: 1.1.0
