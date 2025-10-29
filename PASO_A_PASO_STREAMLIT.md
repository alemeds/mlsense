# 🚨 PASO A PASO: Actualizar Streamlit Cloud

## ⚠️ ATENCIÓN: Tu app necesita actualizarse para usar la API

Los cambios están en GitHub, pero Streamlit Cloud necesita saber que debe usar la versión nueva.

---

## 📋 **GUÍA PASO A PASO CON CAPTURAS**

### **Paso 1: Ve a tu Dashboard de Streamlit**

1. Abre: https://share.streamlit.io/
2. Inicia sesión si es necesario
3. Verás una lista de tus apps

### **Paso 2: Encuentra tu App "mlsense"**

Busca en la lista tu aplicación (debería estar como "mlsense" o similar)

### **Paso 3: Abre la Configuración**

Haz clic en el **menú de 3 puntos (⋮)** a la derecha de tu app:

```
┌─────────────────────────────────┐
│ mlsense                    ⋮    │  ← Haz clic aquí
│ https://mlsense.streamlit.app   │
│ Last deployed: ...              │
└─────────────────────────────────┘
```

Se abrirá un menú:
```
⋮ Settings
  View app
  View logs
  Reboot app
  Delete app
```

**Haz clic en "Settings"**

### **Paso 4: Cambiar la Rama (Branch)**

En la página de Settings, busca la sección que dice:

```
Repository, branch, and file path
    Repository: alemeds/mlsense
    Branch: [main ▼]  ← AQUÍ ESTÁ EL PROBLEMA
    Main file path: ml_scraper_final.py
```

**Haz clic en el dropdown "Branch"** y verás opciones como:
```
- main
- claude/debug-ml-deployment-011CUbmV2W2AYTi9kak6ckg6  ← SELECCIONA ESTA
```

**Selecciona**: `claude/debug-ml-deployment-011CUbmV2W2AYTi9kak6ckg6`

### **Paso 5: Guardar y Redesplegar**

1. **Haz clic en "Save"** (abajo de la página)
2. Verás un mensaje: "Your app is redeploying..."
3. **Espera 1-2 minutos** mientras se actualiza
4. **NO cierres la página** hasta que termine

### **Paso 6: Verificar que Funcionó**

Una vez que termine de redesplegar:

1. Ve a tu app: https://mlsense.streamlit.app
2. En el **sidebar (panel izquierdo)**, deberías ver **NUEVAS opciones**:

```
⚙️ Configuración

🔌 Método de Extracción    ← ESTO ES NUEVO
● ✅ API Oficial (Recomendado)
○ 🕷️ Web Scraping (Experimental)

────────────────────────

Término de búsqueda
[vinos]

☑ Obtener comentarios
```

Si ves esto, **¡funcionó!** ✅

### **Paso 7: Usar la API**

Ahora:

1. **Deja seleccionado** "✅ API Oficial (Recomendado)"
2. Término de búsqueda: "vinos"
3. Marca "Obtener comentarios"
4. Haz clic en **"🚀 Iniciar Búsqueda"** (ya no dice "Iniciar Scraping")

**Deberías ver:**
```
🔌 Conectando con la API oficial de MercadoLibre...
✅ Se encontraron 50 productos
```

---

## 🆘 **SOLUCIÓN RÁPIDA SI NO FUNCIONA**

### Opción A: Reboot Manual

Si la app no se actualiza:

1. Ve a Settings de tu app en Streamlit Cloud
2. En el menú (⋮), selecciona **"Reboot app"**
3. Espera 1 minuto
4. Recarga la página de tu app (F5 o Ctrl+R)

### Opción B: Hard Refresh del Navegador

A veces el navegador cachea la versión vieja:

- **Windows/Linux**: Ctrl + Shift + R
- **Mac**: Cmd + Shift + R

### Opción C: Ver los Logs

Si sigue sin funcionar:

1. En Streamlit Cloud, haz clic en **"View logs"** (menú ⋮)
2. Busca líneas que digan:
   - "Cloning into..." - Debería mostrar la rama correcta
   - Error messages en rojo

---

## ✅ **CHECKLIST DE VERIFICACIÓN**

Después de actualizar, verifica:

- [ ] La rama en Settings dice: `claude/debug-ml-deployment-011CUbmV2W2AYTi9kak6ckg6`
- [ ] Ves "🔌 Método de Extracción" en el sidebar
- [ ] "✅ API Oficial" está como opción
- [ ] El botón dice "Iniciar Búsqueda" (no "Iniciar Scraping")
- [ ] Al buscar, ves "Conectando con la API oficial..."
- [ ] Obtienes productos (50 productos)

---

## 📸 **¿Qué Debo Ver?**

### ANTES (versión vieja):
```
⚙️ Configuración
Término de búsqueda: [vinos]
Número de páginas: [1-5]
☑ Obtener comentarios
────────────────
🐛 Modo Debug
[🚀 Iniciar Scraping]
```

### DESPUÉS (versión nueva):
```
⚙️ Configuración
🔌 Método de Extracción        ← NUEVO
● ✅ API Oficial (Recomendado)  ← NUEVO
○ 🕷️ Web Scraping              ← NUEVO
────────────────
Término de búsqueda: [vinos]
☑ Obtener comentarios
[🚀 Iniciar Búsqueda]          ← CAMBIÓ
```

---

## 🎯 **RESUMEN RÁPIDO**

1. Ve a: https://share.streamlit.io/
2. Tu app → ⋮ → Settings
3. Branch: `claude/debug-ml-deployment-011CUbmV2W2AYTi9kak6ckg6`
4. Save
5. Espera 2 minutos
6. Recarga tu app
7. Selecciona "API Oficial"
8. ¡Funciona!

---

¿Hiciste estos pasos? Si no, dime en qué paso necesitas ayuda.
Si ya lo hiciste y no funcionó, comparte:
- ¿Qué rama está configurada en Settings?
- ¿Ves el selector "🔌 Método de Extracción"?
