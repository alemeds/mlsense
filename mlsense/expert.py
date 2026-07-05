"""Configurable expert system for product recommendations based on rules and sentiment."""

import json
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path


class ProductExpert:
    """Expert system for product recommendations using JSON-defined rules."""

    def __init__(self, categoria_config: Optional[Dict] = None, config_path: Optional[str] = None):
        """Initialize expert system with category configuration.

        Args:
            categoria_config: Dict with category definition. If provided, overrides config_path.
            config_path: Path to categoria JSON file. If None, uses default for argument.
        """
        if categoria_config:
            self.config = categoria_config
        elif config_path:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = self._config_por_defecto()

        self.aspectos = self.config.get('aspectos', {})
        self.reglas = self.config.get('reglas', [])
        self.regla_default = self.config.get('regla_default', {
            'recomendacion': 'NEUTRAL',
            'confianza': 0.5,
            'razon': 'Sin información suficiente'
        })

    def _config_por_defecto(self) -> Dict:
        """Return default configuration."""
        return {
            'categoria': 'general',
            'nombre_display': 'General',
            'aspectos': {},
            'reglas': [],
            'regla_default': {
                'recomendacion': 'NEUTRAL',
                'confianza': 0.5,
                'razon': 'Sin información suficiente'
            }
        }

    def inferir(self, sentimiento_global: float, aspectos: Dict[str, float]) -> Dict[str, Any]:
        """Infer recommendation based on global sentiment and aspect scores.

        Args:
            sentimiento_global: Overall sentiment score (-1 to 1)
            aspectos: Dict of aspect names to scores

        Returns:
            Dict with 'recomendacion', 'confianza', 'razon', and 'reglas_disparadas' list
        """
        reglas_disparadas = []

        for regla in self.reglas:
            if self._evaluar_regla(regla['si'], sentimiento_global, aspectos):
                reglas_disparadas.append({
                    'razon': regla['entonces'].get('razon', ''),
                    'recomendacion': regla['entonces']['recomendacion']
                })

        if reglas_disparadas:
            resultado = max(
                [r for r in reglas_disparadas],
                key=lambda x: self.reglas[
                    next(i for i, r in enumerate(self.reglas)
                         if r['entonces']['razon'] == x['razon'])
                ]['entonces'].get('confianza', 0.5)
            )
            return {
                'recomendacion': resultado['recomendacion'],
                'confianza': self._obtener_confianza(resultado),
                'razon': resultado['razon'],
                'reglas_disparadas': reglas_disparadas
            }

        return {
            'recomendacion': self.regla_default['recomendacion'],
            'confianza': self.regla_default['confianza'],
            'razon': self.regla_default['razon'],
            'reglas_disparadas': []
        }

    def _obtener_confianza(self, resultado: Dict) -> float:
        """Extract confidence from resultado dict."""
        for regla in self.reglas:
            if regla['entonces'].get('razon') == resultado['razon']:
                return regla['entonces'].get('confianza', 0.5)
        return 0.5

    def _evaluar_regla(self, condicion: Dict, sentimiento: float, aspectos: Dict[str, float]) -> bool:
        """Evaluate if rule condition is met.

        Supported conditions:
        - sentimiento_min: minimum sentiment score
        - sentimiento_max: maximum sentiment score
        - aspecto: aspect name to check
        - aspecto_min: minimum aspect score
        - aspecto_max: maximum aspect score

        Args:
            condicion: Dict with condition clauses
            sentimiento: Global sentiment score
            aspectos: Dict of aspect scores

        Returns:
            True if all conditions are met
        """
        if 'sentimiento_min' in condicion:
            if sentimiento < condicion['sentimiento_min']:
                return False

        if 'sentimiento_max' in condicion:
            if sentimiento > condicion['sentimiento_max']:
                return False

        if 'aspecto' in condicion:
            aspecto_nombre = condicion['aspecto']
            aspecto_score = aspectos.get(aspecto_nombre, 0.0)

            if 'aspecto_min' in condicion:
                if aspecto_score < condicion['aspecto_min']:
                    return False

            if 'aspecto_max' in condicion:
                if aspecto_score > condicion['aspecto_max']:
                    return False

        return True

    @staticmethod
    def cargar_desde_archivo(ruta: str) -> 'ProductExpert':
        """Load expert system from JSON file.

        Args:
            ruta: Path to JSON configuration file

        Returns:
            ProductExpert instance
        """
        return ProductExpert(config_path=ruta)

    @staticmethod
    def crear_config_vacia(categoria: str, nombre_display: str) -> Dict:
        """Create empty category configuration.

        Args:
            categoria: Category identifier
            nombre_display: Display name

        Returns:
            Empty config dict
        """
        return {
            'categoria': categoria,
            'nombre_display': nombre_display,
            'aspectos': {},
            'reglas': [],
            'regla_default': {
                'recomendacion': 'NEUTRAL',
                'confianza': 0.5,
                'razon': 'Sin información suficiente'
            }
        }

    def validar_config(self) -> Tuple[bool, List[str]]:
        """Validate configuration format.

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errores = []

        if not isinstance(self.config, dict):
            errores.append("Config must be a dict")
            return False, errores

        for regla in self.reglas:
            if 'si' not in regla or 'entonces' not in regla:
                errores.append("Each rule must have 'si' and 'entonces' clauses")

            si_clause = regla['si']
            entonces_clause = regla['entonces']

            if 'recomendacion' not in entonces_clause:
                errores.append("Each rule's 'entonces' must have 'recomendacion'")

        return len(errores) == 0, errores
