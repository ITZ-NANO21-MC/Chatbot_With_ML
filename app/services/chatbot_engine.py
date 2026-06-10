# -*- coding: utf-8 -*-
"""Módulo del Motor del Chatbot.

Define la clase principal que encapsula toda la lógica de Procesamiento
de Lenguaje Natural (PLN) para comprender y responder a las preguntas
de los usuarios.
"""
import json
from typing import Optional, Tuple

import numpy as np
from rapidfuzz import fuzz, process
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.utils.logger import get_logger
from app import config


class ChatbotEngine:
    """Motor de clasificación de intenciones y respuestas.

    Esta clase carga una base de conocimiento desde un archivo, entrena un
    modelo de clasificación basado en TF-IDF y utiliza una estrategia de
    fallback con fuzzy matching para encontrar la respuesta más adecuada
    a una consulta de usuario.
    """

    def __init__(self, knowledge_base_path: str):
        """Inicializa el motor del chatbot.

        Args:
            knowledge_base_path (str): Ruta al archivo JSON de la base de
                                       conocimiento.
        """
        self.logger = get_logger(__name__)
        self.logger.info("Inicializando ChatbotEngine...")

        try:
            self._cargar_conocimiento(knowledge_base_path)
            self._entrenar_vectorizador()
            self.logger.info("Motor del chatbot inicializado exitosamente.")
        except Exception as e:
            self.logger.error(f"Error crítico durante la inicialización: {e}", exc_info=True)
            raise

    def _cargar_conocimiento(self, file_path: str):
        """Carga y expande la base de conocimiento desde un archivo JSON.

        El método lee el archivo, y por cada entrada, expande las preguntas
        con sus sinónimos para aumentar la robustez del modelo.

        Args:
            file_path (str): Ruta al archivo JSON.
        """
        self.logger.info(f"Cargando base de conocimiento desde: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)["conocimiento"]

        self.base_preguntas = [item["pregunta_base"] for item in data]
        self.respuestas_base = [item["respuesta"] for item in data]
        
        self.preguntas_expandidas = []
        self.respuestas_expandidas = []

        for item in data:
            pregunta_base = item["pregunta_base"]
            respuesta = item["respuesta"]
            # Añadir la pregunta base y su respuesta
            self.preguntas_expandidas.append(pregunta_base)
            self.respuestas_expandidas.append(respuesta)
            # Añadir todos los sinónimos con la misma respuesta
            for sinonimo in item.get("sinonimos", []):
                self.preguntas_expandidas.append(sinonimo)
                self.respuestas_expandidas.append(respuesta)
        
        self.logger.info(f"Datos expandidos: {len(self.base_preguntas)} -> {len(self.preguntas_expandidas)} preguntas")

    def _entrenar_vectorizador(self):
        """Entrena el modelo TfidfVectorizer.

        Convierte el corpus de texto de las preguntas expandidas en una
        matriz de características TF-IDF, que el modelo usará para calcular
        la similitud entre textos.
        """
        self.logger.info("Entrenando el vectorizador TF-IDF...")
        self.vectorizer = TfidfVectorizer()
        self.X_train = self.vectorizer.fit_transform(self.preguntas_expandidas)
        self.logger.info("Vectorizador entrenado exitosamente.")

    def _clasificar_con_tfidf(self, pregunta: str) -> Tuple[Optional[str], float]:
        """Clasifica la pregunta usando similitud de coseno con TF-IDF.

        Este es el método principal de clasificación. Vectoriza la pregunta
        del usuario y calcula la similitud del coseno con todas las
        preguntas de la base de conocimiento entrenada.

        Args:
            pregunta (str): La pregunta del usuario.

        Returns:
            Tuple[Optional[str], float]: Una tupla con la respuesta encontrada
                                         y el nivel de confianza, o (None, 0.0)
                                         si no se alcanza el umbral.
        """
        try:
            pregunta_vec = self.vectorizer.transform([pregunta.lower().strip()])
            similitudes = cosine_similarity(pregunta_vec, self.X_train)
            max_idx = np.argmax(similitudes)
            confianza = similitudes[0, max_idx]

            if confianza > config.TFIDF_CONFIDENCE_THRESHOLD:
                self.logger.info(f"TF-IDF: '{pregunta}' -> confianza: {confianza:.2f}")
                return self.respuestas_expandidas[max_idx], confianza
            else:
                self.logger.warning(f"TF-IDF: confianza baja ({confianza:.2f}) para: '{pregunta}'")
                return None, confianza
        except Exception as e:
            self.logger.error(f"Error en TF-IDF para '{pregunta}': {e}")
            return None, 0.0

    def _respaldo_con_fuzzy(self, pregunta: str) -> Optional[str]:
        """Busca una respuesta usando fuzzy matching como fallback.

        Este método se usa si TF-IDF no encuentra una coincidencia con
        suficiente confianza. Utiliza rapidfuzz para encontrar la pregunta
        más similar en la base de conocimiento original, siendo eficaz
        contra errores tipográficos.

        Args:
            pregunta (str): La pregunta del usuario.

        Returns:
            Optional[str]: La respuesta encontrada o None si no hay una
                           coincidencia lo suficientemente buena.
        """
        try:
            mejor_coincidencia, puntuacion, idx = process.extractOne(
                pregunta.lower().strip(),
                self.base_preguntas,
                scorer=fuzz.token_sort_ratio
            )

            if puntuacion >= config.FUZZY_SCORE_THRESHOLD:
                self.logger.info(f"Fuzzy: '{pregunta}' -> coincide con '{mejor_coincidencia}' ({puntuacion}/100)")
                return self.respuestas_base[idx]
            else:
                self.logger.info(f"Fuzzy: sin coincidencia sólida para '{pregunta}' ({puntuacion}/100)")
                return None
        except Exception as e:
            self.logger.error(f"Error en fuzzy matching para '{pregunta}': {e}")
            return None

    def responder(self, pregunta: str) -> str:
        """Orquesta la obtención de una respuesta para la pregunta del usuario.

        Aplica una estrategia de dos pasos:
        1. Intenta clasificar con el modelo TF-IDF, que es rápido y preciso.
        2. Si falla, utiliza el respaldo de fuzzy matching para capturar errores.
        3. Si todo falla, devuelve una respuesta genérica.

        Args:
            pregunta (str): La pregunta del usuario.

        Returns:
            str: La respuesta generada por el bot.
        """
        self.logger.info(f"=== Nueva consulta: '{pregunta}' ===")
        
        respuesta, confianza = self._clasificar_con_tfidf(pregunta)
        if respuesta:
            self.logger.info(f"Respondiendo vía TF-IDF (confianza: {confianza:.2f})")
            return respuesta
        
        respuesta_fuzzy = self._respaldo_con_fuzzy(pregunta)
        if respuesta_fuzzy:
            self.logger.info("Respondiendo vía Fuzzy Matching (red de seguridad)")
            return respuesta_fuzzy
        
        self.logger.warning(f"Sin respuesta adecuada para: '{pregunta}'")
        return "No estoy seguro de entender. ¿Podrías intentar con otras palabras?"
