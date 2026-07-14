"""Nivå 1 (bred korpussökning): är ett föreslaget lucka-ämne redan substantivt
täckt någonstans i korpusen?

D-003 (kalibreringsprocedur, inte ett universellt tal) + D-010 (θ_absens och
Nivå 1-matchningströskeln är EN parameter, kalibrerad här). Ankarprocedur:
mät cosine-likhet för kända relaterade textpar och kända orelaterade textpar
ur DEN AKTUELLA korpusen; sätt tröskeln relativt dessa ankare. Inga värden
eller kod från iteration 1:s D-017 återanvänds — bara ankarmönstret, med helt
nya ankare.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

import numpy as np

from analysis.diversity import _l2_normalize


@dataclass
class Level1ThresholdCalibration:
    n_related_pairs_sampled: int
    n_unrelated_pairs_sampled: int
    related_mean_similarity: float
    related_std_similarity: float
    unrelated_mean_similarity: float
    unrelated_std_similarity: float
    mellanmjolk_anchor_available: bool
    threshold: float


def calibrate_level1_threshold(
    records: list,
    embeddings: np.ndarray,
    n_samples: int = 200,
    seed: int = 42,
) -> Level1ThresholdCalibration:
    """D-003-ankarprocedur.

    - **Kända relaterade par:** angränsande chunkar (konsekutiv chunk_index)
      inom SAMMA källdokument. Sliding-window-chunkningen (D-009) garanterar
      överlappande text mellan dem, vilket gör "relaterad" till ett objektivt,
      strukturellt kriterium — inte ett manuellt urval av "vad som känns likt."
    - **Kända orelaterade par:** chunkar från OLIKA källdokument (Korpus 1:s tre
      WHO-riktlinjer täcker distinkta kliniska ämnen: infektionskontroll,
      fysisk aktivitet, mental hälsa).
    - **Mellanmjölks-ankare:** kräver genererad text (RAG-svar som mekaniskt
      snittar k källchunkar) — existerar inte förrän Fas 1/3 körs. Explicit
      INTE tillgänglig vid detta kalibreringssteg (D-003 säger "om möjligt").
      Tröskeln sätts därför som midpunkten mellan känd-relaterad-medel och
      känd-orelaterad-medel (samma "midpunkt"-logik som D-003 föreskriver,
      med känd-orelaterad-medel som substitut för mellanmjölks-medel tills
      ett riktigt mellanmjölks-ankare kan konstrueras).
    """
    rng = np.random.default_rng(seed)
    normalized = _l2_normalize(embeddings)

    by_doc: dict[str, list[int]] = defaultdict(list)
    for i, r in enumerate(records):
        by_doc[r.source_file].append(i)

    # Kända relaterade par: konsekutiva chunkar inom samma dokument.
    related_pairs: list[tuple[int, int]] = []
    for doc, idxs in by_doc.items():
        idxs_sorted = sorted(idxs, key=lambda i: records[i].chunk_index)
        related_pairs.extend(zip(idxs_sorted, idxs_sorted[1:]))

    n_related = min(n_samples, len(related_pairs))
    related_sample_idx = rng.choice(len(related_pairs), size=n_related, replace=False)
    related_sims = np.array(
        [
            float(normalized[related_pairs[i][0]] @ normalized[related_pairs[i][1]])
            for i in related_sample_idx
        ]
    )

    # Kända orelaterade par: chunkar från olika dokument.
    docs = list(by_doc.keys())
    if len(docs) < 2:
        raise ValueError("kräver minst 2 källdokument för orelaterade ankarpar")

    unrelated_sims = []
    for _ in range(n_samples):
        d1, d2 = rng.choice(len(docs), size=2, replace=False)
        i = rng.choice(by_doc[docs[d1]])
        j = rng.choice(by_doc[docs[d2]])
        unrelated_sims.append(float(normalized[i] @ normalized[j]))
    unrelated_sims = np.array(unrelated_sims)

    related_mean = float(np.mean(related_sims))
    unrelated_mean = float(np.mean(unrelated_sims))
    threshold = (related_mean + unrelated_mean) / 2.0

    return Level1ThresholdCalibration(
        n_related_pairs_sampled=n_related,
        n_unrelated_pairs_sampled=len(unrelated_sims),
        related_mean_similarity=related_mean,
        related_std_similarity=float(np.std(related_sims)),
        unrelated_mean_similarity=unrelated_mean,
        unrelated_std_similarity=float(np.std(unrelated_sims)),
        mellanmjolk_anchor_available=False,
        threshold=threshold,
    )
