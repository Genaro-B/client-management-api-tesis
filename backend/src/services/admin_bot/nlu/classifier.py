"""Clasificador local de intenciones (NLU) basado en scikit-learn.

Actúa como **fallback** del matcher determinístico (`AdminIntentRouter`):
solo se consulta cuando el matcher devuelve `no-entendido`.

Diseño:
- Vectorización TF-IDF combinando n-gramas de palabra (1-2) y de carácter
  (3-5, `char_wb`) para tolerar sinónimos y errores de tipeo leves.
- Clasificador lineal (`LogisticRegression`) con `predict_proba` para obtener
  confianza por intención.
- Entrenamiento **lazy**: el modelo se entrena la primera vez que se usa y
  queda cacheado en memoria (singleton a nivel de módulo).
- Persistencia **opcional** con `joblib`: si se define `ADMIN_BOT_NLU_MODEL_PATH`
  se intenta cargar/guardar el modelo; si falla o no existe, entrena en memoria
  sin romper nada.

Es 100% offline y determinístico; no requiere servicios externos.
"""
import json
import os
from functools import lru_cache
from typing import Dict, List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion, Pipeline

from src.core.config import get_admin_bot_nlu_threshold
from src.services.admin_bot.admin_intent_router import INTENT_NO_ENTENDIDO

# Ruta del dataset versionado (mismo directorio que este módulo).
_DATASET_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset.json")

# Umbral por defecto (coincide con el default de config).
UMBRAL_DEFAULT = 0.55


def _cargar_dataset(path: str) -> Tuple[List[str], List[str]]:
    """Devuelve (textos, etiquetas) a partir del JSON {intent: [frases]}."""
    with open(path, "r", encoding="utf-8") as fh:
        data: Dict[str, List[str]] = json.load(fh)
    textos: List[str] = []
    etiquetas: List[str] = []
    for intent, frases in data.items():
        for frase in frases:
            textos.append(frase)
            etiquetas.append(intent)
    return textos, etiquetas


def _construir_pipeline() -> Pipeline:
    """Pipeline TF-IDF (palabra + carácter) -> regresión logística."""
    features = FeatureUnion(
        [
            ("word", TfidfVectorizer(analyzer="word", ngram_range=(1, 2), sublinear_tf=True)),
            ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)),
        ]
    )
    return Pipeline(
        [
            ("features", features),
            ("clf", LogisticRegression(max_iter=1000, C=5.0)),
        ]
    )


class NluClassifier:
    """Clasificador local de intenciones administrativas.

    Uso:
        clf = NluClassifier()
        intent, conf = clf.classify("cuánta gente nueva se anotó este mes", 0.55)
    """

    def __init__(self, dataset_path: str = _DATASET_PATH) -> None:
        self.dataset_path = dataset_path
        self._pipeline: Pipeline | None = None
        self._modelo_path = os.getenv("ADMIN_BOT_NLU_MODEL_PATH") or ""

    # ------------------------------------------------------------------
    # Entrenamiento / carga (lazy)
    # ------------------------------------------------------------------

    def _entrenar(self) -> Pipeline:
        textos, etiquetas = _cargar_dataset(self.dataset_path)
        pipeline = _construir_pipeline()
        pipeline.fit(textos, etiquetas)
        return pipeline

    def _pipeline_entrenado(self) -> Pipeline:
        """Devuelve el pipeline, entrenando/cargando de forma lazy y cacheada."""
        if self._pipeline is not None:
            return self._pipeline

        # 1) Intento de carga desde disco (opcional, degrada con gracia).
        if self._modelo_path and os.path.exists(self._modelo_path):
            try:
                import joblib

                self._pipeline = joblib.load(self._modelo_path)
                return self._pipeline
            except Exception:
                # Modelo corrupto/versión distinta: reentrenamos en memoria.
                self._pipeline = None

        # 2) Entrenamiento en memoria.
        self._pipeline = self._entrenar()

        # 3) Intento de guardado (best-effort, nunca rompe).
        if self._modelo_path:
            try:
                import joblib

                joblib.dump(self._pipeline, self._modelo_path)
            except Exception:
                pass

        return self._pipeline

    # ------------------------------------------------------------------
    # Predicción
    # ------------------------------------------------------------------

    def classify(self, texto: str, umbral: float = UMBRAL_DEFAULT) -> Tuple[str, float]:
        """Clasifica `texto` y devuelve `(intent, confianza)`.

        Si la confianza máxima es menor a `umbral`, o el texto está vacío,
        devuelve `(no-entendido, confianza)`.
        """
        texto = (texto or "").strip()
        if not texto:
            return INTENT_NO_ENTENDIDO, 0.0

        pipeline = self._pipeline_entrenado()
        probas = pipeline.predict_proba([texto])[0]
        idx = int(probas.argmax())
        intent = str(pipeline.classes_[idx])
        confianza = float(probas[idx])

        # Muy poca confianza, o la propia clase no-entendido gana: no entendido.
        if confianza < umbral or intent == INTENT_NO_ENTENDIDO:
            return INTENT_NO_ENTENDIDO, confianza
        return intent, confianza


@lru_cache(maxsize=1)
def _singleton() -> NluClassifier:
    """Instancia compartida (entrena una sola vez por proceso)."""
    return NluClassifier()


def clasificar(texto: str, umbral: float | None = None) -> Tuple[str, float]:
    """Atajo sobre el clasificador singleton usando el umbral de config."""
    if umbral is None:
        umbral = get_admin_bot_nlu_threshold()
    return _singleton().classify(texto, umbral)
