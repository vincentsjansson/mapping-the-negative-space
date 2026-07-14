"""D-009 grön tooling: compute_gaps() — lokalt NN-gap + kant/centroid-gap.

D-009 val (b): klustersteget SKIPPAS för PoC. Ingen CLUSTER_COS_DIST_THRESHOLD.
Resultatet är GapDetectionResult.regions — en per-chunk-lista, inte klustrade
regioner. Klustring = eget beslut (D-011+) om det behövs senare.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.neighbors import BallTree

import config
from analysis.diversity import _l2_normalize


@dataclass
class GapRegion:
    chunk_index: int
    local_nn_distance: float
    centroid_distance: float
    is_local_gap: bool
    is_centroid_gap: bool


@dataclass
class GapDetectionResult:
    regions: list[GapRegion]
    k: int
    percentile_used: int
    local_threshold: float
    centroid_threshold: float
    union_fraction: float


def _k_candidates(n: int) -> dict[str, int]:
    """D-004: två k-kandidater, klippta till [K_MIN, K_MAX]. Ingen tredje läggs till."""
    k_log = round(0.5 * np.log(n))
    k_sqrt = round(0.5 * np.sqrt(n))
    return {
        "log": int(max(config.K_MIN, min(config.K_MAX, k_log))),
        "sqrt": int(max(config.K_MIN, min(config.K_MAX, k_sqrt))),
    }


def compute_gaps(
    embeddings: np.ndarray,
    k_candidate: str = "log",
    percentile: int = config.PERCENTILE_DEFAULT,
) -> GapDetectionResult:
    """Beräknar lokalt NN-gap (avstånd till k:e närmaste granne) och
    kant/centroid-gap (avstånd till korpusens centroid) per chunk.

    Ingen klustring (D-009 val b). Arbetar direkt mot embeddings, en region per
    chunk. Percentiltröskeln är ett policy-val (D-005), inte härledd.
    """
    n = embeddings.shape[0]
    if k_candidate not in config.K_CANDIDATES:
        raise ValueError(f"okänd k_candidate: {k_candidate!r}, förväntade en av {config.K_CANDIDATES}")

    k = _k_candidates(n)[k_candidate]
    if k >= n:
        raise ValueError(f"k={k} >= n={n}; korpusen är för liten för detta k")

    normalized = _l2_normalize(embeddings)

    # Lokalt NN-gap: cosine-avstånd via L2-normaliserade vektorer + euklidisk
    # ball-tree (euklidiskt avstånd mellan L2-normaliserade vektorer är en
    # monoton funktion av cosine-avstånd, så rangordningen bevaras).
    tree = BallTree(normalized)
    distances, _ = tree.query(normalized, k=k + 1)  # +1: varje punkt är sin egen närmaste granne
    local_nn_distance = distances[:, -1]  # k:e (icke-själv) grannens avstånd

    centroid = normalized.mean(axis=0, keepdims=True)
    centroid_distance = np.linalg.norm(normalized - centroid, axis=1)

    local_threshold = float(np.percentile(local_nn_distance, percentile))
    centroid_threshold = float(np.percentile(centroid_distance, percentile))

    is_local_gap = local_nn_distance >= local_threshold
    is_centroid_gap = centroid_distance >= centroid_threshold
    union_fraction = float(np.mean(is_local_gap | is_centroid_gap))

    # D-005: höj till 95:e percentilen om unionen överskrider 15% av korpusen.
    if union_fraction > config.UNION_HIGH_THRESHOLD and percentile != config.PERCENTILE_HIGH:
        return compute_gaps(embeddings, k_candidate=k_candidate, percentile=config.PERCENTILE_HIGH)

    regions = [
        GapRegion(
            chunk_index=i,
            local_nn_distance=float(local_nn_distance[i]),
            centroid_distance=float(centroid_distance[i]),
            is_local_gap=bool(is_local_gap[i]),
            is_centroid_gap=bool(is_centroid_gap[i]),
        )
        for i in range(n)
    ]

    return GapDetectionResult(
        regions=regions,
        k=k,
        percentile_used=percentile,
        local_threshold=local_threshold,
        centroid_threshold=centroid_threshold,
        union_fraction=union_fraction,
    )
