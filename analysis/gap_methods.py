"""D-013 (FÖRSLAG): metod-bakeoff. Fem gap-severity-operationaliseringar, alla
med samma gränssnitt: `severity_fn(embeddings, k) -> np.ndarray` (n,), högre
värde = mer gap-likt/anomalt. Opererar på REDAN VALT embedding-rum — vilket
rum (MiniLM/mpnet/whitened) avgörs utanför denna modul (D-013 embedding-axeln).

Rör inte analysis/gap_detection.py eller analysis/leave_one_out.py — detta är
ett fristående, parallellt metod-rum för jämförelse, inte en ersättning.
"""

from __future__ import annotations

import numpy as np
from sklearn.neighbors import BallTree, LocalOutlierFactor, KernelDensity

from analysis.diversity import _l2_normalize


def baseline_severity(embeddings: np.ndarray, k: int) -> np.ndarray:
    """Nuvarande metod (D-009/gap_detection.py): max av lokal-NN-rank och
    centroid-rank. Severity = rangposition (0..n-1), inte råa avstånd, för
    jämförbarhet med de andra metodernas godtyckliga skalor."""
    normalized = _l2_normalize(embeddings)
    n = normalized.shape[0]

    tree = BallTree(normalized)
    distances, _ = tree.query(normalized, k=k + 1)
    local_nn_distance = distances[:, -1]

    centroid = normalized.mean(axis=0, keepdims=True)
    centroid_distance = np.linalg.norm(normalized - centroid, axis=1)

    local_rank = local_nn_distance.argsort().argsort()
    centroid_rank = centroid_distance.argsort().argsort()
    return np.maximum(local_rank, centroid_rank).astype(np.float64)


def lof_severity(embeddings: np.ndarray, k: int) -> np.ndarray:
    """Local Outlier Factor — lokalt relativ densitet. Högre LOF = mer avvikande
    relativt sina egna grannars densitet (till skillnad från baseline, som
    jämför mot GLOBAL percentil)."""
    normalized = _l2_normalize(embeddings)
    clf = LocalOutlierFactor(n_neighbors=k, metric="euclidean")
    clf.fit_predict(normalized)
    return -clf.negative_outlier_factor_  # högre = mer outlier


def kde_severity(embeddings: np.ndarray, k: int) -> np.ndarray:
    """KDE-baserad densitetspoäng. Bandbredd sätts datadrivet (median
    k-NN-avstånd över korpusen) — en standard-heuristik, inte kalibrerad mot
    något facit. Severity = negativ log-densitet (låg densitet = gap-likt)."""
    normalized = _l2_normalize(embeddings)
    n = normalized.shape[0]

    tree = BallTree(normalized)
    distances, _ = tree.query(normalized, k=k + 1)
    bandwidth = float(np.median(distances[:, -1]))
    bandwidth = max(bandwidth, 1e-3)

    kde = KernelDensity(bandwidth=bandwidth, kernel="gaussian")
    kde.fit(normalized)
    log_density = kde.score_samples(normalized)
    return -log_density


def persistent_homology_severity(embeddings: np.ndarray, k: int) -> np.ndarray:
    """Persistent homologi (H1+H2) på VARJE punkts lokala k-grannskap (inkl.
    punkten själv). Severity = summan av bar-längder (total persistence) i H1
    och H2 — ett lokalt grannskap med mer "håligt"/icke-trivial topologi ger
    högre severity. Beräknas per punkt (litet moln, k<=10 punkter — snabbt per
    anrop, men N anrop totalt)."""
    from ripser import ripser

    normalized = _l2_normalize(embeddings)
    n = normalized.shape[0]

    tree = BallTree(normalized)
    _, neighbor_idx = tree.query(normalized, k=k + 1)  # inkl. punkten själv

    severity = np.zeros(n)
    for i in range(n):
        cloud = normalized[neighbor_idx[i]]
        if cloud.shape[0] < 4:
            continue
        result = ripser(cloud, maxdim=2)["dgms"]
        total = 0.0
        for dim_diagram in result[1:]:  # H1, H2 (hoppa H0)
            finite = dim_diagram[np.isfinite(dim_diagram[:, 1])]
            if finite.size:
                total += float(np.sum(finite[:, 1] - finite[:, 0]))
        severity[i] = total
    return severity


def void_severity(embeddings: np.ndarray, k: int, n_random: int = 10, seed: int = 42) -> np.ndarray:
    """Empty-space/void-statistik — lokal spherical-contact-approximation.
    För varje punkt: sampla n_random slumpmässiga probe-punkter inom dess egen
    k-NN-radie, mät avståndet från varje probe till NÄRMASTE riktiga
    korpuspunkt. Severity = medel-probe-avstånd — mycket tomrum runt punkten
    ger höga probe-avstånd (F-funktionen i punktprocess-statistik, lokalt
    approximerad kring varje datapunkt snarare än globalt)."""
    normalized = _l2_normalize(embeddings)
    n, d = normalized.shape

    tree = BallTree(normalized)
    distances, _ = tree.query(normalized, k=k + 1)
    local_radius = distances[:, -1]

    rng = np.random.default_rng(seed)
    directions = rng.normal(size=(n, n_random, d))
    directions /= np.linalg.norm(directions, axis=2, keepdims=True)
    radii = rng.uniform(0.0, 1.0, size=(n, n_random, 1)) * local_radius[:, None, None]
    probes = normalized[:, None, :] + radii * directions
    probes = probes.reshape(n * n_random, d)
    probes = _l2_normalize(probes)

    probe_dist, _ = tree.query(probes, k=1)
    probe_dist = probe_dist.reshape(n, n_random)
    return probe_dist.mean(axis=1)


METHODS = {
    "baseline": baseline_severity,
    "lof": lof_severity,
    "kde": kde_severity,
    "persistent_homology": persistent_homology_severity,
    "void_stat": void_severity,
}


from dataclasses import dataclass


@dataclass
class BakeoffResult:
    method: str
    embedding_space: str
    corpus: str
    k_candidate: str
    k: int
    n_truncated: int
    n_removed: int
    best_rank: int
    best_rank_fraction: float


def run_bakeoff_indices(
    embeddings: np.ndarray,
    removed_indices: list[int],
    method: str,
    embedding_space: str,
    corpus: str,
    k_candidate: str,
    k: int,
    transform_fn=None,
) -> BakeoffResult:
    """Samma gränssnitt/logik som D-011:s run_graded_leave_one_out_indices
    (analysis/leave_one_out.py) — gränsande kvarvarande index i den ORIGINALA
    listan, rang i severity-rankningen — men med METOD som pluggbar parameter
    (D-013) i stället för den hårdkodade baseline-severityn.

    `transform_fn` (t.ex. whiten): appliceras EFTER trunkering, på
    truncated_emb — INTE på hela embeddings innan borttagning. Annars fittas
    transformen (t.ex. whitening-matrisens medelvärde/kovarians) på statistik
    som inkluderar det som ska "tas bort", vilket är en läcka i
    leave-one-out-testet (upptäckt och rättad 2026-07-15, se D-014 i
    beslutslogg.md). embeddings som skickas in ska alltså vara RÅA
    (otransformerade) när transform_fn används."""
    n = embeddings.shape[0]
    removed_sorted = sorted(removed_indices)
    removed_set = set(removed_sorted)
    truncated_idx = [i for i in range(n) if i not in removed_set]

    before_orig = removed_sorted[0] - 1
    after_orig = removed_sorted[-1] + 1
    boundary_orig = [i for i in (before_orig, after_orig) if 0 <= i < n and i not in removed_set]
    if not boundary_orig:
        raise ValueError("ingen kvarvarande gränsande chunk hittades")

    truncated_emb = embeddings[truncated_idx]
    if transform_fn is not None:
        truncated_emb = transform_fn(truncated_emb)
    n_truncated = truncated_emb.shape[0]

    # Slås samman vid anropstillfället (inte modulnivå) så att METHODS_D018,
    # definierad längre ner i filen, är tillgänglig utan att D-013:s METHODS
    # behöver muteras eller flyttas.
    all_methods = {**METHODS, **globals().get("METHODS_D018", {})}
    severity = all_methods[method](truncated_emb, k)
    order = np.argsort(severity)[::-1]
    trunc_pos_to_orig = {pos: orig for pos, orig in enumerate(truncated_idx)}
    orig_to_rank = {}
    for rank_minus_1, trunc_pos in enumerate(order):
        orig_idx = trunc_pos_to_orig[trunc_pos]
        orig_to_rank[orig_idx] = rank_minus_1 + 1

    candidate_ranks = [orig_to_rank[i] for i in boundary_orig if i in orig_to_rank]
    best_rank = min(candidate_ranks)

    return BakeoffResult(
        method=method,
        embedding_space=embedding_space,
        corpus=corpus,
        k_candidate=k_candidate,
        k=k,
        n_truncated=n_truncated,
        n_removed=len(removed_indices),
        best_rank=best_rank,
        best_rank_fraction=best_rank / n_truncated,
    )


def whiten(embeddings: np.ndarray, eps: float = 1e-6) -> np.ndarray:
    """PCA-whitening (embedding-rum c i D-013): tar bort anisotropi genom att
    normalisera varians i varje huvudkomponent-riktning till 1. Re-normaliseras
    till enhetslängd efteråt så nedströms-kod (som antar L2-normaliserade
    vektorer) fungerar oförändrat."""
    centered = embeddings - embeddings.mean(axis=0, keepdims=True)
    cov = np.cov(centered, rowvar=False)
    eigvals, eigvecs = np.linalg.eigh(cov)
    eigvals = np.clip(eigvals, eps, None)
    whitening_matrix = eigvecs @ np.diag(1.0 / np.sqrt(eigvals)) @ eigvecs.T
    whitened = centered @ whitening_matrix
    return _l2_normalize(whitened)


# ---------------------------------------------------------------------------
# D-018 (FÖRSLAG): andra-rundas bakeoff, void-familjen mot regerande standard
# void_stat. Fyra kandidater pre-registrerade; en droppas nedan som
# implementations-odugliga i 384 dim (rapporterat, inte tyst ersatt).
# ---------------------------------------------------------------------------

# --- Kandidat 2: Watershed-/Voronoi-basin void-finder (ZOBOV/VIDE-stil) ----
#
# DROPPAD — kan inte implementeras rent i 384 dimensioner.
#
# ZOBOV/VIDE bygger på en EXAKT Voronoi-tessellering av punktmolnet (varje
# punkts Voronoi-cell beräknas explicit som en polytop), följt av en
# watershed-sammanslagning av angränsande celler till "zoner"/bassänger.
# Beräkningskomplexiteten för en exakt Voronoi-tessellering (t.ex. via
# qhull, som scipy.spatial.Voronoi använder) är O(n^ceil(d/2)) i värsta fall
# och i praktiken helt oanvändbar bortom ~10-20 dimensioner för icke-trivialt
# N — inte en prestandafråga som löses med mer tid, utan en kombinatorisk
# explosion i antalet Voronoi-facetter. Vid d=384 finns ingen standardimplementation
# (qhull/scipy, CGAL, eller motsvarande) som klarar detta för N i
# storleksordningen 3000-14000 punkter. Ingen approximation testad här heller
# — watershed-sammanslagningssteget bygger specifikt på Voronoi-cellernas
# ANGRÄNSNING (grannskapsgraf), vilket inte har någon etablerad,
# dimensionsagnostisk motsvarighet på samma sätt som cell-VOLYM har
# (se kandidat 3 nedan). Rapporteras som oduglig, inte tyst ersatt med
# någon annan metod.
VORONOI_BASIN_STATUS = "DROPPAD (D-018): exakt Voronoi-tessellering intraktabel vid d=384"


def cvde_severity(embeddings: np.ndarray, k: int) -> np.ndarray:
    """Kandidat 3: Voronoi cell-volym-densitet, högdimensionell variant (CVDE).

    Exakt Voronoi-cellvolym är lika intraktabel som kandidat 2 (samma
    tessellerings-problem). Den etablerade högdim-säkra proxyn är
    k-NN-boll-volymestimatorn (Loftsgaarden–Quesenberry): lokal densitet
    ∝ k / (n · V_d(r_k)), där r_k är avståndet till k:e närmaste grannen och
    V_d(r) är volymen av en d-dimensionell boll med radie r — en sluten
    formel, matematiskt definierad för GODTYCKLIG dimension (beräknad i
    log-rymd här för numerisk stabilitet vid d=384).

    FLAGGAD MATEMATISK DEGENERATION (upptäckt vid implementation, INNAN
    bakeoffen körs — inte ett resultat som gömts efteråt): eftersom formeln
    ovan bara beror på r_k via en monoton term (d·log(r_k)), ger den EXAKT
    SAMMA RANGORDNING av punkterna som att ranka dem direkt efter deras k:e
    NN-avstånd. Det är precis den lokala halvan av baseline-metoden (som tar
    max av lokal-NN-rank och centroid-rank). Som en FRISTÅENDE
    rank-baserad severity tillför CVDE alltså sannolikt ingen ny geometrisk
    signal jämfört med baseline — men droppas INTE här, eftersom D-018 bara
    tillåter droppning vid implementations-oduglighet (kandidat 2), inte vid
    förväntad redundans. Körs i bakeoffen; resultatet bör tolkas mot denna
    reservation, inte som ett oberoende fynd om det liknar baseline."""
    from scipy.special import gammaln

    normalized = _l2_normalize(embeddings)
    n, d = normalized.shape

    tree = BallTree(normalized)
    distances, _ = tree.query(normalized, k=k + 1)
    r_k = np.clip(distances[:, -1], 1e-10, None)

    log_unit_ball_volume = (d / 2) * np.log(np.pi) - gammaln(d / 2 + 1)
    log_density = np.log(k) - np.log(n) - log_unit_ball_volume - d * np.log(r_k)
    return -log_density  # hög severity = låg densitet = gap-likt


def dtm_severity(embeddings: np.ndarray, k: int) -> np.ndarray:
    """Kandidat 4: Distance-to-measure (DTM) — brus-robust tomrumsmått
    (Chazal et al.). DTM(x) = kvadratroten av medelvärdet av
    d(x, granne_i)^2 över de k närmaste grannarna.

    Till skillnad från baseline och CVDE (som båda bara använder AVSTÅNDET
    TILL DEN k:TE grannen, en enda punkt på avståndsfördelningen) använder
    DTM samtliga k grannars avstånd via kvadratiskt medelvärde — mer
    brus-robust mot en enskild extrem grannobservation, och en genuint
    annan geometrisk signal (inte bara en monoton omskrivning) än de rent
    k:e-NN-baserade måtten ovan."""
    normalized = _l2_normalize(embeddings)
    tree = BallTree(normalized)
    distances, _ = tree.query(normalized, k=k + 1)
    neighbor_distances = distances[:, 1:]  # exkl. punkten själv (avstånd 0)
    return np.sqrt(np.mean(neighbor_distances**2, axis=1))


# D-018:s kandidatlista, redo för bakeoff-körning. void_stat återanvänds
# oförändrad från D-013:s METHODS-dict (analysis.gap_methods.void_severity).
# Voronoi-basin utesluten (droppad, se VORONOI_BASIN_STATUS ovan).
METHODS_D018 = {
    "void_stat": void_severity,
    "cvde": cvde_severity,
    "dtm": dtm_severity,
}
