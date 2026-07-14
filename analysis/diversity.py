"""D-009 grön tooling: ren linjär algebra, domänagnostisk."""

from __future__ import annotations

import numpy as np


def _l2_normalize(vectors: np.ndarray) -> np.ndarray:
    """L2-normaliserar varje rad. Nollvektorer lämnas oförändrade."""
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)
    return vectors / norms


def _mean_pairwise_distance(vectors: np.ndarray) -> float:
    """Medel cosine-avstånd (1 - cosine-likhet) över alla par, exkl. diagonalen."""
    n = vectors.shape[0]
    if n < 2:
        return 0.0
    normalized = _l2_normalize(vectors)
    sim = normalized @ normalized.T
    dist = 1.0 - sim
    off_diag_sum = dist.sum() - np.trace(dist)
    n_pairs = n * (n - 1)
    return float(off_diag_sum / n_pairs)
