"""D-007: distance-concentration-kontroll. Obligatoriskt delsteg i Steg 0.5,
INNAN percentiltröskeln (D-005) tillämpas skarpt. Karakteriserar om
embedding-rummets avståndsfördelning är starkt koncentrerad — vilket skulle
urholka NN-distans-baserad gap-detektion oavsett sökalgoritm (ball-tree löser
bara ett annat problem, se negative_space_open_problems_v1_0.md C2)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from analysis.diversity import _l2_normalize


DUPLICATE_DISTANCE_EPSILON = 1e-4  # under denna räknas två chunkar som (nästan) identiska


@dataclass
class DistanceConcentrationResult:
    n: int
    mean_pairwise_distance: float
    std_pairwise_distance: float
    coefficient_of_variation: float  # std/mean över alla par — lägre = mer koncentrerat
    mean_relative_contrast: float    # medel över punkter av (dmax-dmin)/dmin till alla andra
    min_relative_contrast: float
    nn_distance_cv: float            # CV av k=1 NN-avstånd över alla punkter
    n_near_duplicate_points: int     # antal punkter vars närmaste granne har avstånd < epsilon
    n_excluded_from_relative_contrast: int


def distance_concentration_stats(embeddings: np.ndarray) -> DistanceConcentrationResult:
    normalized = _l2_normalize(embeddings)
    n = normalized.shape[0]

    sim = normalized @ normalized.T
    dist = 1.0 - sim
    np.fill_diagonal(dist, np.nan)
    # Flyttalsbrus kan ge marginellt negativa "avstånd" för nästan identiska
    # vektorer (cosine-likhet > 1.0 pga float32-precision) — klipp till 0.
    dist = np.clip(dist, 0.0, None)

    off_diag = dist[~np.isnan(dist)]
    mean_d = float(np.mean(off_diag))
    std_d = float(np.std(off_diag))
    cv = std_d / mean_d if mean_d > 0 else 0.0

    row_min = np.nanmin(dist, axis=1)
    row_max = np.nanmax(dist, axis=1)

    # (dmax-dmin)/dmin exploderar om dmin ~ 0 (nästan identiska/duplicerade
    # chunkar — hittat i Korpus 3, se D-007-resultat). Sådana punkter utesluts
    # ur relativ-kontrast-medlet (annars dominerar en division-nära-noll hela
    # statistiken) men RAPPORTERAS separat som en egen diagnostik — duplicerat
    # innehåll är i sig relevant för hur pålitlig NN-gap-signalen är.
    n_near_duplicates = int(np.sum(row_min < DUPLICATE_DISTANCE_EPSILON))
    valid = row_min >= DUPLICATE_DISTANCE_EPSILON

    if valid.any():
        relative_contrast = (row_max[valid] - row_min[valid]) / row_min[valid]
        mean_rc = float(np.mean(relative_contrast))
        min_rc = float(np.min(relative_contrast))
    else:
        mean_rc = float("nan")
        min_rc = float("nan")

    nn_cv = float(np.std(row_min) / np.mean(row_min)) if np.mean(row_min) > 0 else 0.0

    return DistanceConcentrationResult(
        n=n,
        mean_pairwise_distance=mean_d,
        std_pairwise_distance=std_d,
        coefficient_of_variation=cv,
        mean_relative_contrast=mean_rc,
        min_relative_contrast=min_rc,
        nn_distance_cv=nn_cv,
        n_near_duplicate_points=n_near_duplicates,
        n_excluded_from_relative_contrast=n_near_duplicates,
    )
