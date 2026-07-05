"""Main Streamlit app for MLSENSE."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from pathlib import Path
from typing import List, Dict, Any

from .sentiment import AnalizadorSentimiento
from .expert import ProductExpert
from .parsers import parse_mercadolibre_html
from .fetcher import fetch_product_url, search_live, extract_html_from_page
from .demo_data import generate_demo_data


def configurar_pagina():
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title="MLSENSE v2 - Análisis de Sentimientos",
        page_icon="🛍️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.markdown("""
    <style>
    .metric-card { padding: 20px; border-radius: 8px; background-color: #f0f2f6; }
    .recommendation { padding: 15px; border-radius: 8px; margin: 10px 0; }
    .recommendation.buy { background-color: #d4edda; border-left: 4px solid #28a745; }
    .recommendation.avoid { background-color: #f8d7da; border-left: 4px solid #dc3545; }
    .recommendation.neutral { background-color: #fff3cd; border-left: 4px solid #ffc107; }
    .recommendation.wait { background-color: #d1ecf1; border-left: 4px solid #17a2b8; }
    </style>
    """, unsafe_allow_html=True)


def cargar_categoria(nombre_categoria: str) -> Dict[str, Any]:
    """Load category configuration from JSON file.

    Args:
        nombre_categoria: Category identifier

    Returns:
        Category configuration dict
    """
    ruta = Path(__file__).parent.parent / "lexicons" / f"categoria_{nombre_categoria}.json"
    if ruta.exists():
        with open(ruta, 'r', encoding='utf-8') as f:
            return json.load(f)
    return ProductExpert.crear_config_vacia(nombre_categoria, nombre_categoria.title())


def tab_datos_extraidos(productos: List[Dict[str, Any]]):
    """Display extracted products tab."""
    st.subheader("📋 Datos Extraídos")

    if not productos:
        st.info("No hay productos. Carga datos en la barra lateral.")
        return

    df_productos = pd.DataFrame(productos)

    columnas_a_mostrar = ['nombre', 'precio', 'moneda', 'estrellas', 'calificaciones', 'envio', 'descuento', 'url']
    columnas_validas = [col for col in columnas_a_mostrar if col in df_productos.columns]

    st.dataframe(
        df_productos[columnas_validas],
        use_container_width=True,
        hide_index=True
    )

    col1, col2 = st.columns(2)
    with col1:
        if 'precio' in df_productos.columns:
            try:
                precios = pd.to_numeric(df_productos['precio'], errors='coerce').dropna()
                st.metric("💰 Precio Promedio", f"${precios.mean():.2f}")
            except:
                pass

    with col2:
        if 'calificaciones' in df_productos.columns:
            try:
                cals = pd.to_numeric(df_productos['calificaciones'], errors='coerce').sum()
                st.metric("⭐ Total Calificaciones", f"{int(cals)}")
            except:
                pass


def tab_sentimientos(productos: List[Dict[str, Any]], categoria_config: Dict[str, Any]):
    """Display sentiment analysis tab."""
    st.subheader("😊 Análisis de Sentimientos")

    if not productos:
        st.info("No hay productos. Carga datos en la barra lateral.")
        return

    analizador = AnalizadorSentimiento()
    experto = ProductExpert(categoria_config)

    resultados = []

    for producto in productos:
        comentarios = producto.get('comentarios', [])
        nombre = producto.get('nombre', 'Producto sin nombre')

        if comentarios:
            score_general, analisis_comentarios = analizador.analizar_multiples(
                comentarios,
                categoria_config.get('aspectos', {})
            )

            aspectos_scores = {}
            for analisis in analisis_comentarios:
                for aspecto, score in analisis.get('aspectos', {}).items():
                    if aspecto not in aspectos_scores:
                        aspectos_scores[aspecto] = []
                    aspectos_scores[aspecto].append(score)

            aspectos_promedio = {
                aspecto: sum(scores) / len(scores)
                for aspecto, scores in aspectos_scores.items()
            }

            inferencia = experto.inferir(score_general, aspectos_promedio)

            resultados.append({
                'nombre': nombre,
                'score_general': score_general,
                'etiqueta': analizador._clasificar_sentimiento(score_general),
                'num_comentarios': len(comentarios),
                'recomendacion': inferencia['recomendacion'],
                'confianza': inferencia['confianza'],
                'razon': inferencia['razon'],
                'aspectos': aspectos_promedio,
                'reglas_disparadas': inferencia.get('reglas_disparadas', [])
            })

    if not resultados:
        st.warning("No hay comentarios en los productos.")
        return

    df_sentimientos = pd.DataFrame([
        {
            'Producto': r['nombre'][:40],
            'Score': f"{r['score_general']:.2f}",
            'Sentimiento': r['etiqueta'],
            'Comentarios': r['num_comentarios'],
            'Recomendación': r['recomendacion'],
            'Confianza': f"{r['confianza']:.2f}"
        }
        for r in resultados
    ])

    st.dataframe(df_sentimientos, use_container_width=True, hide_index=True)

    col1, col2 = st.columns(2)

    with col1:
        if 'score_general' in df_sentimientos.columns:
            scores = pd.to_numeric(df_sentimientos['Score'], errors='coerce')
            fig = px.histogram(scores, nbins=5, title="Distribución de Sentimientos")
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        etiquetas_dist = df_sentimientos['Sentimiento'].value_counts()
        fig = px.pie(
            values=etiquetas_dist.values,
            names=etiquetas_dist.index,
            title="Proporción de Etiquetas"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("🔍 Detalles por Producto")
    for resultado in resultados:
        with st.expander(f"📌 {resultado['nombre'][:60]}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Score", f"{resultado['score_general']:.2f}")
            with col2:
                st.metric("Sentimiento", resultado['etiqueta'])
            with col3:
                st.metric("Comentarios", resultado['num_comentarios'])

            if resultado['aspectos']:
                st.write("**Aspectos detectados:**")
                for aspecto, score in resultado['aspectos'].items():
                    st.write(f"- {aspecto.capitalize()}: {score:.2f}")


def tab_experto(productos: List[Dict[str, Any]], categoria_config: Dict[str, Any]):
    """Display expert system recommendations tab."""
    st.subheader("🧠 Sistema Experto")

    if not productos:
        st.info("No hay productos. Carga datos en la barra lateral.")
        return

    analizador = AnalizadorSentimiento()
    experto = ProductExpert(categoria_config)

    recomendaciones = []

    for producto in productos:
        comentarios = producto.get('comentarios', [])
        nombre = producto.get('nombre', 'Producto sin nombre')

        if comentarios:
            score_general, analisis_comentarios = analizador.analizar_multiples(
                comentarios,
                categoria_config.get('aspectos', {})
            )

            aspectos_scores = {}
            for analisis in analisis_comentarios:
                for aspecto, score in analisis.get('aspectos', {}).items():
                    if aspecto not in aspectos_scores:
                        aspectos_scores[aspecto] = []
                    aspectos_scores[aspecto].append(score)

            aspectos_promedio = {
                aspecto: sum(scores) / len(scores)
                for aspecto, scores in aspectos_scores.items()
            }

            inferencia = experto.inferir(score_general, aspectos_promedio)

            recomendaciones.append({
                'nombre': nombre,
                'score': score_general,
                'recomendacion': inferencia['recomendacion'],
                'confianza': inferencia['confianza'],
                'razon': inferencia['razon'],
                'precio': producto.get('precio', '0'),
                'url': producto.get('url', ''),
                'aspectos': aspectos_promedio
            })

    if not recomendaciones:
        st.warning("No hay suficientes datos para análisis.")
        return

    colores_recomendacion = {
        'COMPRAR': '#28a745',
        'EVITAR': '#dc3545',
        'ESPERAR OFERTA': '#17a2b8',
        'NEUTRAL': '#ffc107'
    }

    for rec in recomendaciones:
        color = colores_recomendacion.get(rec['recomendacion'], '#6c757d')
        st.markdown(f"""
        <div style="padding: 15px; border-left: 4px solid {color}; background-color: #f8f9fa; border-radius: 4px; margin: 10px 0;">
        <h4>{rec['nombre'][:70]}</h4>
        <p><strong>Recomendación:</strong> {rec['recomendacion']} (Confianza: {rec['confianza']:.0%})</p>
        <p><strong>Razón:</strong> {rec['razon']}</p>
        <p><strong>Precio:</strong> ${rec['precio']} | <a href="{rec['url']}" target="_blank">Ver en MercadoLibre</a></p>
        </div>
        """, unsafe_allow_html=True)

        with st.expander(f"🧠 Traza de razonamiento - {rec['nombre'][:40]}"):
            st.write(f"**Score de sentimiento:** {rec['score']:.2f}")
            if rec['aspectos']:
                st.write("**Aspectos detectados:**")
                for aspecto, score in rec['aspectos'].items():
                    st.write(f"- {aspecto.capitalize()}: {score:.2f}")


def tab_comparacion(productos: List[Dict[str, Any]], categoria_config: Dict[str, Any]):
    """Display comparison tab."""
    st.subheader("📊 Comparación de Productos")

    if not productos:
        st.info("No hay productos para comparar.")
        return

    analizador = AnalizadorSentimiento()
    experto = ProductExpert(categoria_config)

    datos_comparacion = []

    for producto in productos:
        comentarios = producto.get('comentarios', [])
        if comentarios:
            score_general, _ = analizador.analizar_multiples(comentarios)

            aspectos_scores = {}
            for comentario in comentarios:
                analisis = analizador.analizar_comentario(comentario, categoria_config.get('aspectos', {}))
                for aspecto, score in analisis.get('aspectos', {}).items():
                    if aspecto not in aspectos_scores:
                        aspectos_scores[aspecto] = []
                    aspectos_scores[aspecto].append(score)

            aspectos_promedio = {
                aspecto: sum(scores) / len(scores) if scores else 0
                for aspecto, scores in aspectos_scores.items()
            }

            inferencia = experto.inferir(score_general, aspectos_promedio)

            datos_comparacion.append({
                'nombre': producto.get('nombre', '')[:50],
                'precio': float(producto.get('precio', 0)),
                'score_sentimiento': score_general,
                'recomendacion': inferencia['recomendacion'],
                'url': producto.get('url', '')
            })

    if not datos_comparacion:
        st.info("No hay datos para comparación.")
        return

    df_comp = pd.DataFrame(datos_comparacion)

    col1, col2 = st.columns(2)

    with col1:
        fig_scatter = px.scatter(
            df_comp,
            x='precio',
            y='score_sentimiento',
            color='recomendacion',
            hover_name='nombre',
            title="Precio vs. Sentimiento",
            color_discrete_map={
                'COMPRAR': '#28a745',
                'EVITAR': '#dc3545',
                'ESPERAR OFERTA': '#17a2b8',
                'NEUTRAL': '#ffc107'
            }
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col2:
        fig_bar = px.bar(
            df_comp.sort_values('score_sentimiento'),
            x='score_sentimiento',
            y='nombre',
            title="Score de Sentimiento por Producto",
            orientation='h'
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.write("**Tabla de comparación:**")
    st.dataframe(df_comp, use_container_width=True, hide_index=True)


def tab_descargas(productos: List[Dict[str, Any]], categoria_config: Dict[str, Any]):
    """Display downloads tab."""
    st.subheader("📥 Descargas")

    if not productos:
        st.info("No hay datos para descargar.")
        return

    analizador = AnalizadorSentimiento()

    datos_export = []
    for producto in productos:
        comentarios = producto.get('comentarios', [])
        if comentarios:
            score_general, _ = analizador.analizar_multiples(comentarios)
        else:
            score_general = 0.0

        datos_export.append({
            'nombre': producto.get('nombre', ''),
            'precio': producto.get('precio', ''),
            'moneda': producto.get('moneda', 'ARS'),
            'estrellas': producto.get('estrellas', '0'),
            'calificaciones': producto.get('calificaciones', '0'),
            'envio': producto.get('envio', ''),
            'descuento': producto.get('descuento', ''),
            'url': producto.get('url', ''),
            'score_sentimiento': score_general,
            'num_comentarios': len(comentarios)
        })

    df_export = pd.DataFrame(datos_export)

    csv = df_export.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 Descargar como CSV",
        data=csv,
        file_name="mlsense_analisis.csv",
        mime="text/csv"
    )

    json_str = json.dumps(datos_export, indent=2, ensure_ascii=False)
    st.download_button(
        label="📥 Descargar como JSON",
        data=json_str,
        file_name="mlsense_analisis.json",
        mime="application/json"
    )


def sidebar_entrada_datos() -> tuple:
    """Sidebar for data input mode selection.

    Returns:
        Tuple of (modo, productos, categoria)
    """
    st.sidebar.title("⚙️ Configuración")

    categoria = st.sidebar.selectbox(
        "Categoría",
        options=["vinos", "electronica", "indumentaria"],
        index=0
    )

    categoria_config = cargar_categoria(categoria)

    st.sidebar.markdown("---")
    st.sidebar.subheader("📥 Fuente de Datos")

    modo = st.sidebar.radio(
        "Elige modo de entrada",
        options=["Demo", "HTML subido", "URL de producto", "🌐 Navegación Interactiva", "🔎 Búsqueda en vivo (beta)"]
    )

    productos = []

    if modo == "Demo":
        cantidad = st.sidebar.slider("Cantidad de productos", 5, 50, 20)
        if st.sidebar.button("🎲 Generar Demo"):
            productos = generate_demo_data(categoria, cantidad)
            st.session_state.productos = productos

    elif modo == "HTML subido":
        archivos = st.sidebar.file_uploader(
            "Sube archivo HTML",
            type=["html", "htm"],
            accept_multiple_files=True
        )

        if archivos:
            todos_productos = []
            for archivo in archivos:
                contenido = archivo.read().decode('utf-8', errors='replace')
                prods, warnings = parse_mercadolibre_html(contenido)
                todos_productos.extend(prods)

                if warnings:
                    with st.sidebar.expander(f"⚠️ {archivo.name}"):
                        for warning in warnings:
                            st.warning(warning)

            st.session_state.productos = todos_productos
            productos = todos_productos

    elif modo == "URL de producto":
        url = st.sidebar.text_input("URL del producto MercadoLibre")
        if st.sidebar.button("🔗 Fetch"):
            success, html, mensaje = fetch_product_url(url)
            if success:
                prods, warnings = parse_mercadolibre_html(html)
                st.session_state.productos = prods
                productos = prods
                for warning in warnings:
                    st.sidebar.info(warning)
            else:
                st.sidebar.error(f"❌ {mensaje}")

    elif modo == "🌐 Navegación Interactiva":
        st.sidebar.markdown("**Con Playwright + Capuras**")
        termino = st.sidebar.text_input("Término a buscar", placeholder="ej: chaleco termico")

        if st.sidebar.button("🌐 Buscar en MercadoLibre"):
            if not termino.strip():
                st.sidebar.error("Ingresá un término")
            else:
                with st.spinner("🌐 Abriendo navegador y buscando..."):
                    url, html, screenshots, warnings = _busqueda_playwright(termino)

                    if warnings:
                        for w in warnings:
                            st.sidebar.warning(w)

                    if html:
                        prods, parse_warnings = parse_mercadolibre_html(html)

                        if parse_warnings:
                            with st.sidebar.expander("⚠️ Parsing"):
                                for w in parse_warnings:
                                    st.caption(w)

                        if prods:
                            st.session_state.playwright_productos = prods
                            st.session_state.playwright_url = url
                            st.success(f"✓ {len(prods)} productos encontrados")

        if 'playwright_productos' in st.session_state:
            productos = st.session_state.playwright_productos
            st.sidebar.success("✓ Productos listos para analizar")

    elif modo == "🔎 Búsqueda en vivo (beta)":
        termino = st.sidebar.text_input("Ej: celular samsung a56", key="search_input")
        col1, col2 = st.sidebar.columns(2)
        with col1:
            cantidad = st.number_input("Productos", 5, 30, 15)
        with col2:
            con_comentarios = st.checkbox("Con comentarios", value=True)

        if st.sidebar.button("🔍 Buscar"):
            if not termino.strip():
                st.sidebar.error("Ingresá un término de búsqueda")
            else:
                with st.spinner("Buscando en MercadoLibre..."):
                    prods, warnings = _busqueda_live_cached(termino, cantidad, con_comentarios)

                    if warnings:
                        for warning in warnings:
                            st.sidebar.warning(warning)

                    if prods:
                        st.session_state.productos = prods
                        productos = prods
                    else:
                        st.sidebar.error("No se encontraron productos")

    if 'productos' in st.session_state:
        productos = st.session_state.productos

    return modo, productos, categoria_config


@st.cache_data(ttl=900)
def _busqueda_playwright(termino: str):
    """Cached Playwright search wrapper.

    Args:
        termino: Search term

    Returns:
        Tuple of (url, html, screenshots, warnings)
    """
    from .fetcher import search_with_playwright
    return search_with_playwright(termino)


@st.cache_data(ttl=900)
def _busqueda_live_cached(termino: str, max_productos: int, con_comentarios: bool):
    """Cached live search wrapper.

    Args:
        termino: Search term
        max_productos: Max products
        con_comentarios: Include comments

    Returns:
        Tuple of (products, warnings)
    """
    return search_live(termino, max_productos, con_comentarios)


def main():
    """Main app entry point."""
    configurar_pagina()
    st.title("🛍️ MLSENSE v2")
    st.markdown("*Multi-categoría | Análisis de Sentimientos | Sistema Experto*")

    modo, productos, categoria_config = sidebar_entrada_datos()

    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    **📚 Proyecto académico**
    - Sin afiliación con MercadoLibre
    - Análisis basado en datos provistos por el usuario
    - Configuración: [JSON personalizado]
    """)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Datos Extraídos",
        "😊 Análisis de Sentimientos",
        "🧠 Sistema Experto",
        "📊 Comparación",
        "📥 Descargas"
    ])

    with tab1:
        tab_datos_extraidos(productos)

    with tab2:
        tab_sentimientos(productos, categoria_config)

    with tab3:
        tab_experto(productos, categoria_config)

    with tab4:
        tab_comparacion(productos, categoria_config)

    with tab5:
        tab_descargas(productos, categoria_config)
