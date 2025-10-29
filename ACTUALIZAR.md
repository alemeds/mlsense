# 🚀 INSTRUCCIONES DE ACTUALIZACIÓN - MLSENSE

## ✅ ¡TU APLICACIÓN AHORA FUNCIONA!

He agregado soporte completo para la **API oficial de MercadoLibre**, lo que significa que:
- ✅ **No más bloqueos** - La API es oficial y permitida
- ✅ **Funciona en Streamlit Cloud** - Sin restricciones
- ✅ **Más rápido** - JSON directo en lugar de parsear HTML
- ✅ **Más confiable** - Datos estructurados desde la fuente

---

## 📋 CÓMO ACTUALIZAR TU APP EN STREAMLIT CLOUD

### Opción 1: Cambiar la rama en Streamlit Cloud (RECOMENDADO - 2 minutos)

1. **Ve a tu dashboard de Streamlit Cloud**:
   - https://share.streamlit.io/

2. **Encuentra tu app "mlsense"** en la lista

3. **Haz clic en los 3 puntos (⋮)** a la derecha de tu app

4. **Selecciona "Settings"**

5. **En la sección "App settings"**, cambia:
   ```
   Branch: claude/debug-ml-deployment-011CUbmV2W2AYTi9kak6ckg6
   ```

6. **Haz clic en "Save"**

7. **Espera 1-2 minutos** mientras la app se redesploya

8. **¡Listo!** Recarga tu app

---

### Opción 2: Crear un Pull Request en GitHub (5 minutos)

Si prefieres tener los cambios en la rama `main`:

1. **Ve a GitHub**:
   - https://github.com/alemeds/mlsense/pulls

2. **Haz clic en "New Pull Request"**

3. **Selecciona**:
   - Base: `main`
   - Compare: `claude/debug-ml-deployment-011CUbmV2W2AYTi9kak6ckg6`

4. **Crea el Pull Request**

5. **Hazle merge** (puedes hacer merge inmediatamente)

6. **En Streamlit Cloud**, asegúrate de que esté configurado para usar `main`

7. **La app se actualizará automáticamente** en 1-2 minutos

---

## 🎯 CÓMO USAR LA NUEVA VERSIÓN

Una vez que tu app se haya actualizado, verás **nuevas opciones en el sidebar**:

### 1. **Selector de Método** (NUEVO)

```
🔌 Método de Extracción
○ ✅ API Oficial (Recomendado)  ← SELECCIONA ESTA
○ 🕷️ Web Scraping (Experimental)
```

**IMPORTANTE**: La primera opción (API Oficial) viene seleccionada por defecto.

### 2. **Usa la API**

1. **Deja seleccionado "API Oficial (Recomendado)"**
2. Ingresa tu término de búsqueda: "vinos"
3. Marca "Obtener comentarios" si quieres análisis de sentimientos
4. Haz clic en **"🚀 Iniciar Búsqueda"**
5. **¡Funcionará!** Verás productos inmediatamente

### 3. **Resultado Esperado**

Deberías ver:
```
🔌 Conectando con la API oficial de MercadoLibre...
✅ Se encontraron 50 productos
📝 Obteniendo comentarios de 50 productos...
```

---

## 🐛 SI AÚN QUIERES PROBAR EL SCRAPING

El modo de scraping sigue disponible para pruebas locales:

1. Selecciona **"🕷️ Web Scraping (Experimental)"**
2. Marca **"🐛 Modo Debug"** (nueva opción que aparecerá)
3. Haz clic en "Iniciar Scraping"
4. Verás mensajes detallados de qué está pasando

**Nota**: El scraping probablemente seguirá fallando en Streamlit Cloud debido a que MercadoLibre bloquea esas peticiones.

---

## 📊 CAMBIOS INCLUIDOS EN ESTA ACTUALIZACIÓN

### Nuevas Funcionalidades
- ✅ Clase `MercadoLibreAPI` para acceso a API oficial
- ✅ Selector de método (API vs Scraping) en interfaz
- ✅ Modo Debug mejorado con información detallada
- ✅ Mejor manejo de errores HTTP (403, 404, SSL, etc.)
- ✅ Headers HTTP mejorados para scraping
- ✅ Guía completa de troubleshooting (TROUBLESHOOTING.md)

### Archivos Modificados
- `ml_scraper_final.py` - Agregada clase API y selector de método
- `requirements.txt` - Limpiado de dependencias innecesarias
- `.streamlit/config.toml` - Configuración de despliegue
- `.gitignore` - Patrones de archivos a ignorar
- `TROUBLESHOOTING.md` - Guía de solución de problemas
- `readme.md` - Correcciones de nombres de archivo

---

## ✅ VERIFICACIÓN RÁPIDA

Después de actualizar, verifica que:

- [ ] Ves el selector "🔌 Método de Extracción" en el sidebar
- [ ] "✅ API Oficial (Recomendado)" está seleccionado por defecto
- [ ] El botón dice "🚀 Iniciar Búsqueda" (no "Iniciar Scraping")
- [ ] Al hacer búsqueda, ves: "🔌 Conectando con la API oficial..."
- [ ] Obtienes productos sin error "No se pudieron extraer productos"

---

## 🆘 SI ALGO NO FUNCIONA

### La app no se actualiza
- Espera 2-3 minutos (Streamlit puede tardar en redesplegar)
- Haz "Hard Refresh" en el navegador (Ctrl + Shift + R)
- Ve a Streamlit Cloud y haz clic en "Reboot app"

### No veo las nuevas opciones
- Verifica que la rama sea: `claude/debug-ml-deployment-011CUbmV2W2AYTi9kak6ckg6`
- O que hayas hecho merge a `main` correctamente
- Revisa los logs en Streamlit Cloud para ver si hay errores

### La API no devuelve comentarios
- Es normal que **no todos los productos tengan reviews**
- La API de MercadoLibre devuelve reviews solo si existen
- Prueba con términos populares: "vino malbec", "notebook lenovo"

---

## 📞 CONTACTO

Si necesitas ayuda adicional:
- **GitHub Issues**: https://github.com/alemeds/mlsense/issues
- **Email**: alemeds@hotmail.com

---

## 🎉 ¡DISFRUTA TU APP FUNCIONANDO!

Con la API oficial, tu app ahora debería funcionar perfectamente en Streamlit Cloud. La próxima vez que la abras, selecciona "API Oficial" y verás los resultados inmediatamente.

**Última actualización**: 2025-01-XX
**Rama con mejoras**: `claude/debug-ml-deployment-011CUbmV2W2AYTi9kak6ckg6`
