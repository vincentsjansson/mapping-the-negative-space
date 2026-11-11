"""D-027 -- Bisociationstest mellan täta kluster (sista test innan projektet
avslutas, se beslutslogg.md).

Vänder på hela D-001-premissen: i stället för att leta gles-flaggade regioner
och pröva om de är genuina luckor, tar detta test korpusens TÄTASTE (bäst
täckta) kluster och frågar om en LLM kan bisociera dem till en genuint
icke-trivial koppling som inte redan står i korpusen. Samma validerade
tvåstegs-domare (Nivå 1 + Nivå 2) som D-019/D-025:s sond, oförändrad.
"""

from __future__ import annotations

import numpy as np
from sklearn.cluster import KMeans
from sklearn.neighbors import BallTree

from analysis.diversity import _l2_normalize
from analysis.gap_methods import void_severity


def find_dense_clusters(embeddings, k, n_clusters=8, density_fraction=0.20, seed=2026):
    """De TÄTASTE chunkarna (lägst void_severity) klustras med k-means till
    n_clusters distinkta, väl täckta tema-centroider."""
    severity = void_severity(embeddings, k)
    order = np.argsort(severity)  # stigande: lägst (tätast) först
    n_dense = max(n_clusters * 10, int(len(severity) * density_fraction))
    dense_idx = order[:n_dense]
    dense_emb = _l2_normalize(embeddings[dense_idx])

    km = KMeans(n_clusters=n_clusters, random_state=seed, n_init=10)
    labels = km.fit_predict(dense_emb)

    clusters = []
    for c in range(n_clusters):
        member_positions = np.where(labels == c)[0]
        member_idx = [int(dense_idx[p]) for p in member_positions]
        centroid = km.cluster_centers_[c]
        centroid = centroid / np.linalg.norm(centroid)
        clusters.append({"cluster_id": c, "member_indices": member_idx, "centroid": centroid})
    return clusters


def most_distant_pairs(clusters, top_n_pairs=8):
    """Mekaniskt par-urval: cosine-avstånd mellan klustercentroider, fallande
    sortering, topp-N par. Inget urval efter innehåll."""
    pairs = []
    n = len(clusters)
    for i in range(n):
        for j in range(i + 1, n):
            ci, cj = clusters[i]["centroid"], clusters[j]["centroid"]
            cos_sim = float(ci @ cj)
            distance = 1.0 - cos_sim
            pairs.append((distance, i, j))
    pairs.sort(reverse=True, key=lambda t: t[0])
    return pairs[:top_n_pairs]


def representative_chunks(records, cluster, embeddings, n=4):
    """De n chunkarna i klustret närmast dess centroid (mest representativa)."""
    member_idx = cluster["member_indices"]
    member_emb = _l2_normalize(embeddings[member_idx])
    centroid = cluster["centroid"]
    sims = member_emb @ centroid
    order = np.argsort(sims)[::-1][:n]
    return [member_idx[i] for i in order]


BISOCIATION_PROMPT_TEMPLATE = """You are a domain expert reading excerpts from two \
DIFFERENT, well-covered areas of a document corpus.

DOMAIN CONTEXT:
{domain_context}

EXCERPTS FROM AREA A:
{excerpts_a}

EXCERPTS FROM AREA B:
{excerpts_b}

TASK: Propose ONE specific, concrete connection, mechanism, or interaction BETWEEN \
Area A and Area B that is NOT stated in either set of excerpts above -- something a \
reader would only see by combining the two areas, not by reading either alone. Be \
specific and concrete (name the actual mechanism/population/intersection). Avoid \
generic platitudes or simply restating either area. Answer in 2-4 sentences, nothing \
else."""


# D-028: kontrastiva promptvarianter -- testar om D-027:s 0/8-nollresultat är en
# promptartefakt (associativ sammanslagning) snarare än en fundamental
# generatorbegränsning. Samma struktur (domain_context/excerpts_a/excerpts_b),
# ny TASK-instruktion.
BISOCIATION_PROMPT_A_CONFLICT = """You are a domain expert reading excerpts from two \
DIFFERENT, well-covered areas of a document corpus.

DOMAIN CONTEXT:
{domain_context}

EXCERPTS FROM AREA A:
{excerpts_a}

EXCERPTS FROM AREA B:
{excerpts_b}

TASK: Consider a specific real-world case that falls within the scope of BOTH Area A \
and Area B at the same time. Identify ONE concrete way in which following Area A's \
guidance would practically undermine, complicate, or contradict Area B's guidance for \
that same case -- a genuine point of tension, not a shared theme. Name the exact \
requirement or assumption in each area that conflicts. Avoid vague statements that the \
two areas are simply "related" or should be "considered together" -- state the specific \
conflict. Answer in 2-4 sentences, nothing else."""

BISOCIATION_PROMPT_B_BREAKS = """You are a domain expert reading excerpts from two \
DIFFERENT, well-covered areas of a document corpus.

DOMAIN CONTEXT:
{domain_context}

EXCERPTS FROM AREA A:
{excerpts_a}

EXCERPTS FROM AREA B:
{excerpts_b}

TASK: Area A and Area B each make recommendations optimized for their own context. \
Identify ONE specific requirement, procedure, or assumption in Area A that becomes \
difficult, risky, or impossible to satisfy BECAUSE of a constraint stated in Area B (or \
vice versa), for the same population or setting. Name the exact requirement and the \
exact constraint that conflicts with it. Do not simply state that the two areas overlap \
or interact -- identify what specifically breaks. Answer in 2-4 sentences, nothing \
else."""

BISOCIATION_PROMPT_C_ANTIEXAMPLE = """You are a domain expert reading excerpts from two \
DIFFERENT, well-covered areas of a document corpus.

DOMAIN CONTEXT:
{domain_context}

EXCERPTS FROM AREA A:
{excerpts_a}

EXCERPTS FROM AREA B:
{excerpts_b}

TASK: Consider a specific real-world case that falls within the scope of BOTH Area A \
and Area B at the same time. Identify ONE concrete way in which following Area A's \
guidance would practically undermine, complicate, or contradict Area B's guidance for \
that same case -- a genuine point of tension, not a shared theme. Name the exact \
requirement or assumption in each area that conflicts. Avoid vague statements that the \
two areas are simply "related" or should be "considered together" -- state the specific \
conflict.

Do NOT produce a generic statement that merely notes both areas apply to an overlapping \
population (e.g. "pregnant healthcare workers need both X and Y") -- that is not a \
conflict, just a co-occurrence. A valid answer names a SPECIFIC action, dose, procedure, \
or timeline in one area that would have to be violated, delayed, or skipped to satisfy \
the other. Answer in 2-4 sentences, nothing else."""

PROMPT_VARIANTS = {
    "prompt0_original": BISOCIATION_PROMPT_TEMPLATE,
    "promptA_conflict": BISOCIATION_PROMPT_A_CONFLICT,
    "promptB_breaks": BISOCIATION_PROMPT_B_BREAKS,
    "promptC_antiexample": BISOCIATION_PROMPT_C_ANTIEXAMPLE,
}


def run_bisociation_pair(
    anthropic_client, generator_model, judge_model, domain_context,
    records, embeddings, embedder, cluster_a, cluster_b, n_context=4,
    temperature=0.7, max_tokens_generate=300, prompt_template=None,
):
    from analysis.gap_verification import judge_coverage
    from analysis.domain_adapter import classify_scenario, CALIBRATION_EXAMPLES_C1_CLINICAL

    if prompt_template is None:
        prompt_template = BISOCIATION_PROMPT_TEMPLATE

    idx_a = representative_chunks(records, cluster_a, embeddings, n_context)
    idx_b = representative_chunks(records, cluster_b, embeddings, n_context)
    excerpts_a = "\n\n".join(f"[{j+1}] {records[i].text}" for j, i in enumerate(idx_a))
    excerpts_b = "\n\n".join(f"[{j+1}] {records[i].text}" for j, i in enumerate(idx_b))

    prompt = prompt_template.format(
        domain_context=domain_context, excerpts_a=excerpts_a, excerpts_b=excerpts_b,
    )
    resp = anthropic_client.messages.create(
        model=generator_model, max_tokens=max_tokens_generate, temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
    )
    claim = resp.content[0].text.strip()

    excluded_window = set()
    for ci in idx_a + idx_b:
        for offset in range(-2, 3):
            excluded_window.add(ci + offset)

    level1 = judge_coverage(
        anthropic_client, judge_model, domain_context, claim, records, embeddings,
        embedder, top_k=30, excluded_indices=excluded_window,
    )
    level2 = classify_scenario(
        anthropic_client, judge_model, domain_context, CALIBRATION_EXAMPLES_C1_CLINICAL, claim,
    )
    survives = (level1.label == "not_covered") and (level2["label"] == "non-trivial")

    return {
        "cluster_a_id": cluster_a["cluster_id"], "cluster_b_id": cluster_b["cluster_id"],
        "cluster_a_size": len(cluster_a["member_indices"]),
        "cluster_b_size": len(cluster_b["member_indices"]),
        "context_a_indices": idx_a, "context_b_indices": idx_b,
        "claim": claim,
        "level1_label": level1.label, "level1_confidence": level1.confidence,
        "level1_rationale": level1.rationale,
        "level2_label": level2["label"], "level2_rationale": level2["rationale"],
        "survives": survives,
    }
