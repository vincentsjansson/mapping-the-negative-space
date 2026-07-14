"""D-006: leave-one-out som obligatoriskt externt ankare + facit-mekanism för
D-004 (k-formel). Ta bort ett dokument, eller en tydligt avgränsad sektion, som
KÄNT täcker ett specifikt ämne, kör gap-detektion på den beskurna korpusen,
kontrollera om de mest gap-flaggade regionerna "pekar mot" det borttagna
innehållet.

Operationalisering av "(a) uppstår en gap-region där det borttagna innehållets
embedding-grannskap satt": bland de LEAVE_ONE_OUT_TOP_N mest gap-flaggade
chunkarna i den BESKURNA korpusen, mäts om deras sanna närmaste embedding-granne
ligger i det BORTTAGNA innehållet snarare än i den kvarvarande korpusen. Om
andelen sådana chunkar >= LEAVE_ONE_OUT_SUCCESS_FRACTION: "återupptäckt" = ja
(binärt facit, används av D-004).

Ren geometri — inga API-anrop, ingen kostnad (jfr kickoff-instruktionen).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.neighbors import BallTree

import config
from analysis.diversity import _l2_normalize
from analysis.gap_detection import _k_candidates


@dataclass
class LeaveOneOutResult:
    removed_label: str
    k_candidate: str
    k: int
    n_truncated: int
    n_removed: int
    top_n: int
    n_pointing_to_removed: int
    fraction_pointing_to_removed: float
    rediscovered: bool  # binärt facit (D-004)


def run_leave_one_out_indices(
    embeddings: np.ndarray,
    removed_indices: list[int],
    removed_label: str,
    k_candidate: str,
    top_n: int = config.LEAVE_ONE_OUT_TOP_N,
) -> LeaveOneOutResult:
    """Generell version: tar bort exakt de rader i embeddings som anges av
    removed_indices (kan vara ett helt dokument eller en snävare sektion)."""
    n = embeddings.shape[0]
    removed_set = set(removed_indices)
    truncated_idx = [i for i in range(n) if i not in removed_set]
    if not removed_indices:
        raise ValueError("removed_indices är tom")

    truncated_emb = _l2_normalize(embeddings[truncated_idx])
    removed_emb = _l2_normalize(embeddings[removed_indices])
    n_truncated = truncated_emb.shape[0]

    k = _k_candidates(n_truncated)[k_candidate]

    tree = BallTree(truncated_emb)
    distances, _ = tree.query(truncated_emb, k=k + 1)
    local_nn_distance = distances[:, -1]

    centroid = truncated_emb.mean(axis=0, keepdims=True)
    centroid_distance = np.linalg.norm(truncated_emb - centroid, axis=1)

    local_rank = local_nn_distance.argsort().argsort() / (n_truncated - 1)
    centroid_rank = centroid_distance.argsort().argsort() / (n_truncated - 1)
    severity = np.maximum(local_rank, centroid_rank)

    top_indices = np.argsort(severity)[::-1][:top_n]

    tree_truncated_self = BallTree(truncated_emb)
    tree_removed = BallTree(removed_emb)

    n_pointing_to_removed = 0
    for idx in top_indices:
        point = truncated_emb[idx : idx + 1]
        d_remaining, _ = tree_truncated_self.query(point, k=2)  # k=1 är punkten själv
        d_remaining_nn = d_remaining[0, 1]
        d_removed_nn, _ = tree_removed.query(point, k=1)
        d_removed_nn = d_removed_nn[0, 0]
        if d_removed_nn < d_remaining_nn:
            n_pointing_to_removed += 1

    fraction = n_pointing_to_removed / top_n
    rediscovered = fraction >= config.LEAVE_ONE_OUT_SUCCESS_FRACTION

    return LeaveOneOutResult(
        removed_label=removed_label,
        k_candidate=k_candidate,
        k=k,
        n_truncated=n_truncated,
        n_removed=len(removed_indices),
        top_n=top_n,
        n_pointing_to_removed=n_pointing_to_removed,
        fraction_pointing_to_removed=fraction,
        rediscovered=rediscovered,
    )


def run_leave_one_out(
    records: list,
    embeddings: np.ndarray,
    removed_doc: str,
    k_candidate: str,
    top_n: int = config.LEAVE_ONE_OUT_TOP_N,
) -> LeaveOneOutResult:
    """Dokumentnivå: tar bort ett helt källdokument."""
    removed_idx = [i for i, r in enumerate(records) if r.source_file == removed_doc]
    if not removed_idx:
        raise ValueError(f"inget dokument matchar {removed_doc!r}")
    return run_leave_one_out_indices(embeddings, removed_idx, removed_doc, k_candidate, top_n)


def run_leave_one_out_section(
    records: list,
    embeddings: np.ndarray,
    source_file: str,
    chunk_index_range: tuple[int, int],
    label: str,
    k_candidate: str,
    top_n: int = config.LEAVE_ONE_OUT_TOP_N,
) -> LeaveOneOutResult:
    """Sektionsnivå: tar bort chunkar med chunk_index inom [start, end]
    (inklusive) från ETT källdokument."""
    start, end = chunk_index_range
    removed_idx = [
        i
        for i, r in enumerate(records)
        if r.source_file == source_file and start <= r.chunk_index <= end
    ]
    if not removed_idx:
        raise ValueError(f"ingen chunk matchar {source_file!r} i intervallet {chunk_index_range}")
    return run_leave_one_out_indices(embeddings, removed_idx, label, k_candidate, top_n)


# ---------------------------------------------------------------------------
# D-011: graderat leave-one-out-mått — TILLÄGG, inte ersättning. Rör inte
# ovanstående binära funktioner/logik. Nytt mått vid sidan av: rangen (i den
# globala gles-region-rankingen på den beskurna korpusen) för de kvarvarande
# chunkar vars index GRÄNSAR till den borttagna positionen (D-011 punkt a:
# array-adjacens i den fulla records-listan — dokumentoberoende, samma
# definition oavsett om borttagningen är en sektion eller ett helt dokument).
# ---------------------------------------------------------------------------


@dataclass
class GradedLeaveOneOutResult:
    removed_label: str
    k_candidate: str
    k: int
    n_original: int
    n_truncated: int
    n_removed: int
    fraction_removed: float
    boundary_before_rank: int | None  # 1-baserad rang, 1 = mest gap-lik
    boundary_after_rank: int | None
    best_rank: int
    best_rank_fraction: float  # best_rank / n_truncated


def run_graded_leave_one_out_indices(
    embeddings: np.ndarray,
    removed_indices: list[int],
    removed_label: str,
    k_candidate: str,
) -> GradedLeaveOneOutResult:
    n = embeddings.shape[0]
    removed_sorted = sorted(removed_indices)
    removed_set = set(removed_sorted)
    truncated_idx = [i for i in range(n) if i not in removed_set]
    if not removed_indices:
        raise ValueError("removed_indices är tom")

    # D-011 (a): gränsande KVARVARANDE index i den ORIGINALA (obeskurna)
    # records-listan — den kvarvarande chunken direkt före första borttagna
    # index, och direkt efter sista borttagna index.
    before_orig = removed_sorted[0] - 1
    after_orig = removed_sorted[-1] + 1
    boundary_orig = [
        i for i in (before_orig, after_orig) if 0 <= i < n and i not in removed_set
    ]
    if not boundary_orig:
        raise ValueError(
            "ingen kvarvarande gränsande chunk hittades (borttagningen täcker hela korpusen "
            "eller ligger i en av korpusens yttersta positioner utan kvarvarande granne)"
        )

    truncated_emb = _l2_normalize(embeddings[truncated_idx])
    n_truncated = truncated_emb.shape[0]
    k = _k_candidates(n_truncated)[k_candidate]

    tree = BallTree(truncated_emb)
    distances, _ = tree.query(truncated_emb, k=k + 1)
    local_nn_distance = distances[:, -1]

    centroid = truncated_emb.mean(axis=0, keepdims=True)
    centroid_distance = np.linalg.norm(truncated_emb - centroid, axis=1)

    local_rank = local_nn_distance.argsort().argsort()
    centroid_rank = centroid_distance.argsort().argsort()
    severity = np.maximum(local_rank, centroid_rank)  # högre värde = mer gap-lik

    # Global gles-region-ranking: position 0 = mest gap-lik (rang 1).
    order = np.argsort(severity)[::-1]
    trunc_pos_to_orig = {pos: orig for pos, orig in enumerate(truncated_idx)}
    orig_to_rank = {}
    for rank_minus_1, trunc_pos in enumerate(order):
        orig_idx = trunc_pos_to_orig[trunc_pos]
        orig_to_rank[orig_idx] = rank_minus_1 + 1  # 1-baserad

    before_rank = orig_to_rank.get(before_orig) if before_orig in boundary_orig else None
    after_rank = orig_to_rank.get(after_orig) if after_orig in boundary_orig else None

    candidate_ranks = [r for r in (before_rank, after_rank) if r is not None]
    best_rank = min(candidate_ranks)

    return GradedLeaveOneOutResult(
        removed_label=removed_label,
        k_candidate=k_candidate,
        k=k,
        n_original=n,
        n_truncated=n_truncated,
        n_removed=len(removed_indices),
        fraction_removed=len(removed_indices) / n,
        boundary_before_rank=before_rank,
        boundary_after_rank=after_rank,
        best_rank=best_rank,
        best_rank_fraction=best_rank / n_truncated,
    )


def run_graded_leave_one_out_section(
    records: list,
    embeddings: np.ndarray,
    source_file: str,
    chunk_index_range: tuple[int, int],
    label: str,
    k_candidate: str,
) -> GradedLeaveOneOutResult:
    start, end = chunk_index_range
    removed_idx = [
        i
        for i, r in enumerate(records)
        if r.source_file == source_file and start <= r.chunk_index <= end
    ]
    if not removed_idx:
        raise ValueError(f"ingen chunk matchar {source_file!r} i intervallet {chunk_index_range}")
    return run_graded_leave_one_out_indices(embeddings, removed_idx, label, k_candidate)


# ---------------------------------------------------------------------------
# D-012: storleksskalad topp-N-brytpunktssvep — TILLÄGG, inte ersättning.
# Rör inte run_leave_one_out_indices/run_leave_one_out/run_leave_one_out_section
# eller deras redan rapporterade resultat (LEAVE_ONE_OUT_TOP_N=10 facit).
# Samma severity-rankning + "pekar mot borttaget"-logik som det binära måttet,
# men utvärderad kumulativt över HELA den beskurna korpusen på en gång, så att
# fraction_pointing_to_removed kan läsas av vid VILKEN topp-N som helst utan
# att köra om testet — inklusive den faktiska brytpunkten (D-006:s 50 %-gräns).
# ---------------------------------------------------------------------------


@dataclass
class TopNSweepResult:
    removed_label: str
    k_candidate: str
    k: int
    n_truncated: int
    n_removed: int
    fraction_at_top1pct: float | None   # fraction_pointing_to_removed vid topp 1% av n_truncated
    top1pct_n: int
    fraction_at_top0_5pct: float | None  # vid topp 0,5%
    top0_5pct_n: int
    breakeven_top_n: int | None         # minsta topp-N där kumulativ andel >= framgångsgränsen
    breakeven_fraction_of_n: float | None


def run_topn_sweep_indices(
    embeddings: np.ndarray,
    removed_indices: list[int],
    removed_label: str,
    k_candidate: str,
    success_fraction: float = config.LEAVE_ONE_OUT_SUCCESS_FRACTION,
) -> TopNSweepResult:
    n = embeddings.shape[0]
    removed_set = set(removed_indices)
    truncated_idx = [i for i in range(n) if i not in removed_set]
    if not removed_indices:
        raise ValueError("removed_indices är tom")

    truncated_emb = _l2_normalize(embeddings[truncated_idx])
    removed_emb = _l2_normalize(embeddings[removed_indices])
    n_truncated = truncated_emb.shape[0]

    k = _k_candidates(n_truncated)[k_candidate]

    tree = BallTree(truncated_emb)
    distances, _ = tree.query(truncated_emb, k=k + 1)
    local_nn_distance = distances[:, -1]

    centroid = truncated_emb.mean(axis=0, keepdims=True)
    centroid_distance = np.linalg.norm(truncated_emb - centroid, axis=1)

    local_rank = local_nn_distance.argsort().argsort()
    centroid_rank = centroid_distance.argsort().argsort()
    severity = np.maximum(local_rank, centroid_rank)
    order = np.argsort(severity)[::-1]  # mest gap-lik först

    tree_truncated_self = BallTree(truncated_emb)
    tree_removed = BallTree(removed_emb)

    ordered_points = truncated_emb[order]
    d_remaining, _ = tree_truncated_self.query(ordered_points, k=2)
    d_remaining_nn = d_remaining[:, 1]
    d_removed_nn, _ = tree_removed.query(ordered_points, k=1)
    d_removed_nn = d_removed_nn[:, 0]

    points_to_removed = (d_removed_nn < d_remaining_nn).astype(np.float64)
    cumulative_fraction = np.cumsum(points_to_removed) / np.arange(1, n_truncated + 1)

    def _at_pct(pct: float) -> tuple[int, float | None]:
        top_n = max(1, round(pct * n_truncated))
        top_n = min(top_n, n_truncated)
        return top_n, float(cumulative_fraction[top_n - 1])

    top1pct_n, frac_1pct = _at_pct(0.01)
    top0_5pct_n, frac_0_5pct = _at_pct(0.005)

    crossing = np.where(cumulative_fraction >= success_fraction)[0]
    if crossing.size > 0:
        breakeven_top_n = int(crossing[0] + 1)
        breakeven_fraction_of_n = breakeven_top_n / n_truncated
    else:
        breakeven_top_n = None
        breakeven_fraction_of_n = None

    return TopNSweepResult(
        removed_label=removed_label,
        k_candidate=k_candidate,
        k=k,
        n_truncated=n_truncated,
        n_removed=len(removed_indices),
        fraction_at_top1pct=frac_1pct,
        top1pct_n=top1pct_n,
        fraction_at_top0_5pct=frac_0_5pct,
        top0_5pct_n=top0_5pct_n,
        breakeven_top_n=breakeven_top_n,
        breakeven_fraction_of_n=breakeven_fraction_of_n,
    )


def run_topn_sweep_section(
    records: list,
    embeddings: np.ndarray,
    source_file: str,
    chunk_index_range: tuple[int, int],
    label: str,
    k_candidate: str,
) -> TopNSweepResult:
    start, end = chunk_index_range
    removed_idx = [
        i
        for i, r in enumerate(records)
        if r.source_file == source_file and start <= r.chunk_index <= end
    ]
    if not removed_idx:
        raise ValueError(f"ingen chunk matchar {source_file!r} i intervallet {chunk_index_range}")
    return run_topn_sweep_indices(embeddings, removed_idx, label, k_candidate)


def run_topn_sweep_document(
    records: list,
    embeddings: np.ndarray,
    removed_doc: str,
    k_candidate: str,
) -> TopNSweepResult:
    removed_idx = [i for i, r in enumerate(records) if r.source_file == removed_doc]
    if not removed_idx:
        raise ValueError(f"inget dokument matchar {removed_doc!r}")
    return run_topn_sweep_indices(embeddings, removed_idx, removed_doc, k_candidate)


def run_graded_leave_one_out_document(
    records: list,
    embeddings: np.ndarray,
    removed_doc: str,
    k_candidate: str,
) -> GradedLeaveOneOutResult:
    removed_idx = [i for i, r in enumerate(records) if r.source_file == removed_doc]
    if not removed_idx:
        raise ValueError(f"inget dokument matchar {removed_doc!r}")
    return run_graded_leave_one_out_indices(embeddings, removed_idx, removed_doc, k_candidate)
