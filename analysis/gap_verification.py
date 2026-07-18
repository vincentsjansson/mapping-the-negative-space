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

import config
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


# ---------------------------------------------------------------------------
# D-019 delsteg B: Nivå 1 — bred korpussökning. Fanns tidigare bara som
# tröskelkalibrering (D-003/D-010 ovan); själva sökfunktionen ("är detta
# påstående redan täckt NÅGONSTANS i korpusen?") byggs här.
# ---------------------------------------------------------------------------


@dataclass
class Level1SearchResult:
    claim: str
    max_similarity: float
    threshold: float
    already_covered: bool
    best_match_chunk_index: int
    best_match_source_file: str
    best_match_text_preview: str


def search_corpus_for_coverage(
    claim_text: str,
    records: list,
    embeddings: np.ndarray,
    embedder,
    threshold: float,
    excluded_indices: set[int] | None = None,
) -> Level1SearchResult:
    """Nivå 1: embeddar ett föreslaget lucka-påstående och söker HELA korpusen
    efter dess mest lika chunk. already_covered = max_similarity >= threshold
    (D-003/D-010:s kalibrerade tröskel). Ren cosine-likhetssökning — samma
    embedder/embedding-rum som resten av pipelinen (D-009), ingen separat
    sökindexstruktur utöver en linjär skanning (korpusstorlekarna i detta
    projekt, 3-14k chunkar, gör exakt linjär sökning fullt rimlig; ingen
    approximativ ANN-lösning behövs).

    D-020 (H3 löst): claim_text trunkeras till CHUNK_SIZE_DEFAULT tecken innan
    embedding — D-003:s ankarpar byggdes på chunkar av den längden, och långa,
    syntetiserande LLM-genererade påståenden fick annars systematiskt högre
    similarity mot NÅGON korpuschunk oavsett genuin nyhet (samma längd/format-
    confound som H3/lärdomar §0 flaggade, aldrig löst förrän nu).

    D-024: excluded_indices (t.ex. ±2-fönster runt claimens källkontext)
    exkluderas ur sökningen — annars kan ett claim trivialt "hitta täckning"
    i sina EGNA källchunkar (det genererades ju från dem). Samma
    exkluderingslogik som D-021:s ankarkalibrering, nu konsekvent tillämpad
    här också, inte bara i kalibreringssteget."""
    claim_text = claim_text[: config.CHUNK_SIZE_DEFAULT]

    normalized_corpus = _l2_normalize(embeddings)
    claim_emb = _l2_normalize(embedder.embed([claim_text]))[0]

    similarities = normalized_corpus @ claim_emb
    if excluded_indices:
        for i in excluded_indices:
            if 0 <= i < len(similarities):
                similarities[i] = -1
    best_idx = int(np.argmax(similarities))
    max_sim = float(similarities[best_idx])

    return Level1SearchResult(
        claim=claim_text,
        max_similarity=max_sim,
        threshold=threshold,
        already_covered=max_sim >= threshold,
        best_match_chunk_index=records[best_idx].chunk_index,
        best_match_source_file=records[best_idx].source_file,
        best_match_text_preview=records[best_idx].text[:150],
    )


# ---------------------------------------------------------------------------
# D-023: Nivå 1 blir en LLM-täckningsdomare — embedding-baserade metoder
# (D-003/D-010 bi-encoder max-cosine, D-022 cross-encoder) klarade inte
# separations-gaten (AUC 0,728 resp. 0,579, mål 0,85). Samma struktur som den
# fungerande Nivå 2-domaren (analysis/domain_adapter.py): prompt/few-shot,
# temperature=0, JSON-svar.
# ---------------------------------------------------------------------------

# D-024: engelska (bytt från svenska) — samma cross-lingual confound-fix som
# PROMPT_TEMPLATE (rag_runner.py) och domain_adapter.py. label-värden nu
# "covered"/"not_covered" (tidigare "täckt"/"ej_täckt").
#
# D-024/D-023-uppföljning: prompten ramar EXPLICIT om uppgiften till en POSITIV
# täckningsfråga ("är X faktiskt beskrivet i utdragen, och var?"), INTE "medför
# utdraget absens-påståendet" — en absens (att något INTE sägs) kan inte
# verifieras genom entailment mot en enskild chunk (det var precis D-022:s
# cross-encoder-feltolkning). Modellen instrueras att först extrahera X (det
# specifika innehåll claimen påstår saknas), sedan leta efter X i utdragen,
# och citera VILKET utdragsnummer om täckt.
COVERAGE_JUDGE_PROMPT_TEMPLATE = """You are a coverage judge for a research project on \
geometric gap detection in document corpora.

DOMAIN CONTEXT:
{domain_context}

You will be given a CLAIMED GAP SCENARIO of the form "the corpus does not address X" \
(where X is some specific topic, population, or mechanism), plus excerpts from the corpus.

Do this in order:
1. Identify exactly what X is — the specific content the claim says is missing. Do not \
just note the general topic; identify the precise detail, population, or mechanism.
2. Check whether X is actually stated in the excerpts below. This is a POSITIVE search \
question ("is X described in these excerpts, and where?") — you are NOT judging whether \
an excerpt logically entails the absence claim (that is not a well-formed question; \
absence cannot be verified against a single excerpt by entailment).
3. If X is described in one or more excerpts, label the scenario "covered" and name the \
excerpt number(s) in your rationale. If none of the excerpts state X — even if some \
discuss the same general topic — label it "not_covered".

Be strict about SPECIFICITY: excerpts mentioning the same GENERAL TOPIC is not enough for \
"covered" — X itself must actually appear.

MOST RELEVANT EXCERPTS FROM THE CORPUS (top-{k}, retrieved via cosine similarity):
{chunks_block}

Respond ONLY with valid JSON in this form:
{{"label": "covered" or "not_covered", "confidence": <number 0.0-1.0>, "rationale": "name the excerpt number if covered; 1-2 sentence justification"}}

CLAIMED GAP SCENARIO TO ASSESS:
{claim}"""


@dataclass
class CoverageJudgeResult:
    claim: str
    label: str  # "covered" | "not_covered" | "parse_error"
    confidence: float | None
    rationale: str
    candidate_chunk_indices: list[int]


def judge_coverage(
    anthropic_client,
    model: str,
    domain_context: str,
    claim_text: str,
    records: list,
    embeddings: np.ndarray,
    embedder,
    top_k: int = 30,  # D-023-uppföljning 2026-07-18: höjt 10->30, se beslutslogg.md
    excluded_indices: set[int] | None = None,
    max_tokens: int = 500,
) -> CoverageJudgeResult:
    """D-023: LLM-täckningsdomare. Grov kandidat-hämtning via cosine (topp-k),
    LLM avgör täckning på innehållsnivå. excluded_indices (D-021:s ±2-fönster
    runt claimens källregion) exkluderas ur kandidat-hämtningen för att inte
    trivialt matcha sin egen sliding-window-granne."""
    import json
    import re

    claim_t = claim_text[:config.CHUNK_SIZE_DEFAULT] if hasattr(claim_text, "__len__") else claim_text
    normalized_corpus = _l2_normalize(embeddings)
    claim_emb = _l2_normalize(embedder.embed([claim_t]))[0]
    sims = normalized_corpus @ claim_emb
    if excluded_indices:
        for i in excluded_indices:
            if 0 <= i < len(sims):
                sims[i] = -1
    top_k_idx = np.argsort(sims)[::-1][:top_k]

    chunks_block = "\n\n".join(f"[{j+1}] {records[i].text}" for j, i in enumerate(top_k_idx))
    prompt = COVERAGE_JUDGE_PROMPT_TEMPLATE.format(
        domain_context=domain_context, k=top_k, chunks_block=chunks_block, claim=claim_t
    )
    resp = anthropic_client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=0.0,
        messages=[{"role": "user", "content": prompt}],
    )
    text = resp.content[0].text.strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return CoverageJudgeResult(claim=claim_t, label="parse_error", confidence=None, rationale=text, candidate_chunk_indices=[int(i) for i in top_k_idx])
    try:
        parsed = json.loads(match.group(0))
    except json.JSONDecodeError:
        return CoverageJudgeResult(claim=claim_t, label="parse_error", confidence=None, rationale=text, candidate_chunk_indices=[int(i) for i in top_k_idx])

    return CoverageJudgeResult(
        claim=claim_t,
        label=parsed.get("label", "parse_error"),
        confidence=parsed.get("confidence"),
        rationale=parsed.get("rationale", ""),
        candidate_chunk_indices=[int(i) for i in top_k_idx],
    )
