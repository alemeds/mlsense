"""Sentiment analysis engine with Spanish rioplatense lexicon support."""

import json
import re
import unicodedata
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class AnalizadorSentimiento:
    """Sentiment analyzer using lexicon-based approach with Spanish support."""

    def __init__(self, lexicon_path: Optional[str] = None):
        """Initialize sentiment analyzer with lexicon.

        Args:
            lexicon_path: Path to lexicon JSON file. If None, uses default general lexicon.
        """
        if lexicon_path is None:
            lexicon_path = Path(__file__).parent.parent / "lexicons" / "lexicon_general.json"

        with open(lexicon_path, 'r', encoding='utf-8') as f:
            self.lexicon = json.load(f)

        self.positivos = self.lexicon.get('positivos', {})
        self.negativos = self.lexicon.get('negativos', {})
        self.negadores = self.lexicon.get('negadores', [])
        self.intensificadores = self.lexicon.get('intensificadores', {})
        self.atenuadores = self.lexicon.get('atenuadores', {})

    def normalizar(self, texto: str) -> str:
        """Normalize text for sentiment analysis.

        Args:
            texto: Text to normalize

        Returns:
            Normalized text (lowercase, no diacritics, collapsed repetitions)
        """
        texto = texto.lower()
        texto = unicodedata.normalize('NFD', texto)
        texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
        texto = re.sub(r'([a-z])\1{2,}', r'\1', texto)
        texto = re.sub(r'[^a-z\s]', '', texto)
        return texto.strip()

    def tokenizar(self, texto: str) -> List[str]:
        """Tokenize text into words.

        Args:
            texto: Text to tokenize

        Returns:
            List of tokens
        """
        texto = self.normalizar(texto)
        return re.findall(r'\b\w+\b', texto)

    def detectar_aspectos(self, tokens: List[str], aspectos_keywords: Dict[str, List[str]]) -> Dict[str, float]:
        """Detect sentiment for specific aspects in comment.

        Args:
            tokens: Tokenized comment
            aspectos_keywords: Dict mapping aspect names to keyword lists

        Returns:
            Dict with aspect scores
        """
        aspectos_score = {}

        for aspecto, keywords in aspectos_keywords.items():
            keywords_norm = [self.normalizar(kw) for kw in keywords]
            scores = []

            for i, token in enumerate(tokens):
                if token in keywords_norm:
                    ventana = tokens[max(0, i-4):min(len(tokens), i+5)]
                    score = self._calcular_sentimiento_ventana(ventana)
                    scores.append(score)

            if scores:
                aspectos_score[aspecto] = sum(scores) / len(scores)

        return aspectos_score

    def _calcular_sentimiento_ventana(self, ventana: List[str]) -> float:
        """Calculate sentiment for a word window.

        Args:
            ventana: Window of words

        Returns:
            Sentiment score
        """
        score = 0.0
        multiplicador = 1.0

        for i, word in enumerate(ventana):
            if word in self.negadores:
                multiplicador *= -1
            elif word in self.intensificadores:
                multiplicador *= self.intensificadores[word]
            elif word in self.atenuadores:
                multiplicador *= self.atenuadores[word]
            elif word in self.positivos:
                score += self.positivos[word] * multiplicador
            elif word in self.negativos:
                score += self.negativos[word] * multiplicador

        return max(-1.0, min(1.0, score / 10.0))

    def analizar_comentario(self, comentario: str,
                           aspectos_keywords: Optional[Dict[str, List[str]]] = None) -> Dict:
        """Analyze sentiment of a comment.

        Args:
            comentario: Comment text
            aspectos_keywords: Optional dict of aspects and keywords for aspect detection

        Returns:
            Dict with 'score' (float -1 to 1), 'etiqueta' (str), and optional 'aspectos' (dict)
        """
        tokens = self.tokenizar(comentario)
        if not tokens:
            return {'score': 0.0, 'etiqueta': 'Neutro', 'aspectos': {}}

        score = 0.0
        multiplicador = 1.0

        for word in tokens:
            if word in self.negadores:
                multiplicador *= -1
            elif word in self.intensificadores:
                multiplicador *= self.intensificadores[word]
            elif word in self.atenuadores:
                multiplicador *= self.atenuadores[word]
            elif word in self.positivos:
                score += self.positivos[word] * multiplicador
            elif word in self.negativos:
                score += self.negativos[word] * multiplicador

        score = max(-1.0, min(1.0, score / (len(tokens) * 2)))

        etiqueta = self._clasificar_sentimiento(score)

        resultado = {
            'score': score,
            'etiqueta': etiqueta,
        }

        if aspectos_keywords:
            resultado['aspectos'] = self.detectar_aspectos(tokens, aspectos_keywords)

        return resultado

    def _clasificar_sentimiento(self, puntuacion: float) -> str:
        """Classify sentiment score into category.

        Args:
            puntuacion: Score from -1 to 1

        Returns:
            Sentiment label
        """
        if puntuacion >= 0.5:
            return "Muy positivo"
        elif puntuacion >= 0.1:
            return "Positivo"
        elif puntuacion <= -0.5:
            return "Muy negativo"
        elif puntuacion <= -0.1:
            return "Negativo"
        else:
            return "Neutro"

    def analizar_multiples(self, comentarios: List[str],
                          aspectos_keywords: Optional[Dict[str, List[str]]] = None) -> Tuple[float, List[Dict]]:
        """Analyze multiple comments and return aggregate score.

        Args:
            comentarios: List of comment texts
            aspectos_keywords: Optional aspect keywords

        Returns:
            Tuple of (aggregate_score, list_of_results)
        """
        resultados = []
        for comentario in comentarios:
            if comentario.strip():
                resultados.append(self.analizar_comentario(comentario, aspectos_keywords))

        if not resultados:
            return 0.0, []

        avg_score = sum(r['score'] for r in resultados) / len(resultados)
        return avg_score, resultados
