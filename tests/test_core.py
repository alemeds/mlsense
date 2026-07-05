"""Core functionality tests for MLSENSE."""

import json
import pytest
from pathlib import Path

from mlsense.sentiment import AnalizadorSentimiento
from mlsense.expert import ProductExpert
from mlsense.parsers import parse_mercadolibre_html, _normalizar_precio
from mlsense.fetcher import build_search_url


class TestAnalizadorSentimiento:
    """Tests for sentiment analyzer."""

    def setup_method(self):
        """Set up sentiment analyzer for each test."""
        self.analizador = AnalizadorSentimiento()

    def test_analizar_positivo(self):
        """Test positive sentiment detection."""
        resultado = self.analizador.analizar_comentario("Excelente producto, muy bueno")
        assert resultado['score'] > 0.3
        assert 'Positivo' in resultado['etiqueta']

    def test_analizar_negativo(self):
        """Test negative sentiment detection."""
        resultado = self.analizador.analizar_comentario("Horrible, deficiente, muy malo")
        assert resultado['score'] < -0.3
        assert 'negativo' in resultado['etiqueta'].lower()

    def test_analizar_neutro(self):
        """Test neutral sentiment detection."""
        resultado = self.analizador.analizar_comentario("El producto es un objeto")
        assert -0.2 <= resultado['score'] <= 0.2

    def test_negador_invierte_polaridad(self):
        """Test that negators invert sentiment."""
        positivo = self.analizador.analizar_comentario("Muy bueno")
        negado = self.analizador.analizar_comentario("No es muy bueno")
        assert positivo['score'] > negado['score']

    def test_intensificador_amplifica(self):
        """Test that intensifiers amplify sentiment."""
        comentario = self.analizador.analizar_comentario("Excelente producto muy bueno")
        assert comentario['score'] > 0.3

    def test_atenuador_reduce(self):
        """Test that attenuators reduce sentiment."""
        comentario = self.analizador.analizar_comentario("Horrible producto muy malo")
        assert comentario['score'] < -0.2

    def test_detectar_aspectos(self):
        """Test aspect detection in comments."""
        aspectos_keywords = {
            'sabor': ['sabor', 'gusto'],
            'aroma': ['aroma', 'olor']
        }
        resultado = self.analizador.analizar_comentario(
            "El sabor es excelente y el aroma muy bueno",
            aspectos_keywords
        )
        assert 'aspectos' in resultado
        assert len(resultado['aspectos']) > 0

    def test_multiples_comentarios(self):
        """Test analysis of multiple comments."""
        comentarios = [
            "Excelente producto",
            "Muy bueno",
            "Horrible"
        ]
        score_general, resultados = self.analizador.analizar_multiples(comentarios)
        assert isinstance(score_general, float)
        assert len(resultados) == 3

    def test_rioplatense_slang(self):
        """Test rioplatense slang recognition."""
        resultado_barbaro = self.analizador.analizar_comentario("Barbaros este producto")
        resultado_berreta = self.analizador.analizar_comentario("Berreta y trucho")
        assert resultado_barbaro['score'] > 0
        assert resultado_berreta['score'] < 0

    def test_normalizacion(self):
        """Test text normalization."""
        texto_original = "EXCELENTE!!! Múúúy bueno"
        texto_norm = self.analizador.normalizar(texto_original)
        assert texto_norm == "excelente muy bueno"


class TestProductExpert:
    """Tests for expert system."""

    def setup_method(self):
        """Set up expert system for each test."""
        self.config = {
            'categoria': 'test',
            'nombre_display': 'Test',
            'aspectos': {
                'sabor': ['sabor', 'gusto'],
                'aroma': ['aroma', 'olor']
            },
            'reglas': [
                {
                    'si': {'sentimiento_min': 0.5},
                    'entonces': {
                        'recomendacion': 'COMPRAR',
                        'confianza': 0.9,
                        'razon': 'Sentimiento muy positivo'
                    }
                },
                {
                    'si': {'sentimiento_max': -0.5},
                    'entonces': {
                        'recomendacion': 'EVITAR',
                        'confianza': 0.9,
                        'razon': 'Sentimiento muy negativo'
                    }
                },
                {
                    'si': {'aspecto': 'sabor', 'aspecto_min': 0.3},
                    'entonces': {
                        'recomendacion': 'COMPRAR',
                        'confianza': 0.8,
                        'razon': 'Sabor excelente'
                    }
                }
            ],
            'regla_default': {
                'recomendacion': 'NEUTRAL',
                'confianza': 0.5,
                'razon': 'Sin evidencia'
            }
        }
        self.experto = ProductExpert(self.config)

    def test_inferir_positivo(self):
        """Test inference with positive sentiment."""
        resultado = self.experto.inferir(0.7, {})
        assert resultado['recomendacion'] == 'COMPRAR'
        assert resultado['confianza'] > 0.8

    def test_inferir_negativo(self):
        """Test inference with negative sentiment."""
        resultado = self.experto.inferir(-0.7, {})
        assert resultado['recomendacion'] == 'EVITAR'
        assert resultado['confianza'] > 0.8

    def test_inferir_default(self):
        """Test inference falls back to default rule."""
        resultado = self.experto.inferir(0.1, {})
        assert resultado['recomendacion'] == 'NEUTRAL'

    def test_inferir_por_aspecto(self):
        """Test inference based on aspect scores."""
        resultado = self.experto.inferir(0.2, {'sabor': 0.5})
        assert resultado['recomendacion'] == 'COMPRAR'

    def test_evaluar_condicion_sentimiento_min(self):
        """Test condition evaluation with sentiment_min."""
        assert self.experto._evaluar_regla(
            {'sentimiento_min': 0.5}, 0.7, {}
        ) is True
        assert self.experto._evaluar_regla(
            {'sentimiento_min': 0.5}, 0.3, {}
        ) is False

    def test_evaluar_condicion_aspecto(self):
        """Test condition evaluation with aspect."""
        assert self.experto._evaluar_regla(
            {'aspecto': 'sabor', 'aspecto_min': 0.3},
            0.0,
            {'sabor': 0.5}
        ) is True
        assert self.experto._evaluar_regla(
            {'aspecto': 'sabor', 'aspecto_min': 0.3},
            0.0,
            {'sabor': 0.1}
        ) is False

    def test_validar_config(self):
        """Test configuration validation."""
        is_valid, errores = self.experto.validar_config()
        assert is_valid is True
        assert len(errores) == 0

    def test_cargar_desde_archivo(self):
        """Test loading from JSON file."""
        config_path = Path(__file__).parent.parent / 'lexicons' / 'categoria_vinos.json'
        if config_path.exists():
            experto = ProductExpert.cargar_desde_archivo(str(config_path))
            assert experto.config['categoria'] == 'vinos'


class TestParsers:
    """Tests for HTML parsers."""

    def test_normalizar_precio_con_punto(self):
        """Test price normalization with dot."""
        assert _normalizar_precio("1.500,00") == "1500.0"

    def test_normalizar_precio_con_coma(self):
        """Test price normalization with comma as thousand separator."""
        assert _normalizar_precio("1.500,00") == "1500.0"

    def test_normalizar_precio_simple(self):
        """Test price normalization simple."""
        assert _normalizar_precio("100") == "100.0"

    def test_normalizar_precio_invalido(self):
        """Test price normalization with invalid input."""
        assert _normalizar_precio("no es precio") == "0"

    def test_parse_html_vacio(self):
        """Test parsing empty HTML."""
        productos, warnings = parse_mercadolibre_html("<html></html>")
        assert isinstance(productos, list)
        assert isinstance(warnings, list)

    def test_parse_json_ld(self):
        """Test JSON-LD extraction."""
        html = """
        <script type="application/ld+json">
        {
            "@type": "Product",
            "name": "Test Product",
            "price": "100",
            "url": "http://example.com"
        }
        </script>
        """
        productos, _ = parse_mercadolibre_html(html)
        assert len(productos) > 0
        assert productos[0]['nombre'] == 'Test Product'

    def test_parse_preloaded_state(self):
        """Test __PRELOADED_STATE__ extraction."""
        html = """
        <script>
        window.__PRELOADED_STATE__ = {"results": [{"title": "Producto Test", "price": 200, "id": "123"}]};
        </script>
        """
        productos, _ = parse_mercadolibre_html(html)
        assert len(productos) > 0
        assert 'Producto Test' in productos[0]['nombre']


class TestIntegracion:
    """Integration tests."""

    def test_flujo_completo(self):
        """Test complete flow: sentiment + expert."""
        analizador = AnalizadorSentimiento()
        categoria = {
            'categoria': 'test',
            'nombre_display': 'Test',
            'aspectos': {},
            'reglas': [
                {
                    'si': {'sentimiento_min': 0.5},
                    'entonces': {
                        'recomendacion': 'COMPRAR',
                        'confianza': 0.9,
                        'razon': 'Positivo'
                    }
                }
            ],
            'regla_default': {
                'recomendacion': 'NEUTRAL',
                'confianza': 0.5,
                'razon': 'Neutral'
            }
        }
        experto = ProductExpert(categoria)

        comentarios = [
            "Excelente producto, muy bueno",
            "Magnífico, lo recomiendo",
            "Fantástico"
        ]

        score, _ = analizador.analizar_multiples(comentarios)
        resultado = experto.inferir(score, {})

        assert score > 0.5
        assert resultado['recomendacion'] == 'COMPRAR'


class TestBuildSearchUrl:
    """Tests for search URL builder."""

    def test_build_search_url_simple(self):
        """Test simple search term."""
        url = build_search_url("celular")
        assert url == "https://listado.mercadolibre.com.ar/celular"

    def test_build_search_url_con_espacios(self):
        """Test search term with spaces."""
        url = build_search_url("celular samsung a56")
        assert url == "https://listado.mercadolibre.com.ar/celular-samsung-a56"

    def test_build_search_url_mayusculas(self):
        """Test uppercase conversion."""
        url = build_search_url("CELULAR SAMSUNG")
        assert url == "https://listado.mercadolibre.com.ar/celular-samsung"

    def test_build_search_url_con_tildes(self):
        """Test diacritic removal."""
        url = build_search_url("Televisión Samsung")
        assert url == "https://listado.mercadolibre.com.ar/television-samsung"

    def test_build_search_url_con_simbolos(self):
        """Test special character removal."""
        url = build_search_url("iPhone 15 Pro Max")
        assert "iphone-15-pro-max" in url

    def test_build_search_url_espacios_multiples(self):
        """Test multiple spaces collapse."""
        url = build_search_url("celular   samsung    a56")
        assert url == "https://listado.mercadolibre.com.ar/celular-samsung-a56"

    def test_build_search_url_espacios_al_inicio_fin(self):
        """Test trimming spaces."""
        url = build_search_url("   celular samsung   ")
        assert url == "https://listado.mercadolibre.com.ar/celular-samsung"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
