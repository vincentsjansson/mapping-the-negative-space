"""D-009 grön tooling: textstatistik-kontroll (confounder-kontroll mot H7-mönstret,
se lardomar_iteration1_till_negative_space.md §3) + Spearman-CI via Fisher z."""

from __future__ import annotations

import re

import numpy as np
from scipy import stats


def _surface_stats(text: str) -> dict:
    """Enkel, billig textstatistik: ordlängd, meningsantal, andel sällsynta ord.
    'Sällsynt' = ord som förekommer exakt en gång i den givna texten (proxy;
    ingen extern frekvenslista behövs för en per-chunk-kontroll)."""
    words = re.findall(r"[^\W\d_]+", text.lower(), flags=re.UNICODE)
    sentences = re.split(r"[.!?]+", text)
    sentences = [s for s in sentences if s.strip()]

    if not words:
        return {
            "n_words": 0,
            "mean_word_length": 0.0,
            "n_sentences": len(sentences),
            "rare_word_ratio": 0.0,
        }

    from collections import Counter

    counts = Counter(words)
    rare = sum(1 for w in words if counts[w] == 1)

    return {
        "n_words": len(words),
        "mean_word_length": float(np.mean([len(w) for w in words])),
        "n_sentences": len(sentences),
        "rare_word_ratio": rare / len(words),
    }


def _spearman_ci(x: np.ndarray, y: np.ndarray, alpha: float = 0.05) -> dict:
    """Spearman rho + 95% CI via Fisher z-transformation."""
    rho, p_value = stats.spearmanr(x, y)
    n = len(x)
    if n < 4 or abs(rho) >= 1.0:
        return {"rho": float(rho), "p_value": float(p_value), "ci_low": None, "ci_high": None}

    z = np.arctanh(rho)
    se = 1.0 / np.sqrt(n - 3)
    z_crit = stats.norm.ppf(1 - alpha / 2)
    ci_low = np.tanh(z - z_crit * se)
    ci_high = np.tanh(z + z_crit * se)

    return {
        "rho": float(rho),
        "p_value": float(p_value),
        "ci_low": float(ci_low),
        "ci_high": float(ci_high),
    }
