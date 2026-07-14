"""D-009 grön tooling: embedding-wrapper. Lokal sentence-transformers-modell,
ingen API-kostnad. Modellnamn/dim styrs av config.py, inte hårdkodat här."""

from __future__ import annotations

import numpy as np

import config


class Embedder:
    def __init__(self, model_name: str = config.EMBEDDING_MODEL):
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name
        self._model = SentenceTransformer(model_name)

    def embed(self, texts: list[str], batch_size: int = 64) -> np.ndarray:
        """Returnerar (len(texts), dim) float32-array."""
        return np.asarray(
            self._model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=False,
                convert_to_numpy=True,
            ),
            dtype=np.float32,
        )
