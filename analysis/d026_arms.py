"""D-026 -- Arm 1 (geometri/association) och Arm 2 (siktning, LLM med facit).

Arm 1a: boilerplate-anrikning i void_stat:s topp-glesa regioner vs korpus-baslinje.
Arm 1b: rent geometriskt facit-test -- ta bort kända sektioner (mekaniskt urval,
        se beslutslogg.md D-026), mät om deras plats rankas gles av void_stat.
Arm 2:  sikta en LLM-generator mot en borttagen sektions plats, be den beskriva
        vad som saknas, döm mot facit (bred ämnesträff + specifikt omfång).

Klassificeraren (`is_structural_noncontent`) och sektionslistan är låsta INNAN
körning (D-026, godkänt 2026-07-19) -- får inte justeras efter att ha sett
utfallet.
"""

from __future__ import annotations

import re

import numpy as np

from analysis.surface_stats import _surface_stats
from analysis.gap_methods import void_severity
from analysis.leave_one_out import run_graded_leave_one_out_section
from analysis.diversity import _l2_normalize

CHUNK_MARKERS = [
    "copyright", "isbn", "all rights reserved", "licence", "license",
    "cc by", "creative commons", "catalogu", "who library",
]
_REFLIST_YEAR = re.compile(r"\(\d{4}\)")
_REFLIST_PAGES = re.compile(r"\d+[-–]\d+\.")


def is_structural_noncontent(text: str) -> tuple[bool, str | None]:
    """Objektiv, innehållsoberoende klassificerare (D-026, spot-checkad 9/10)."""
    t = text.lower()
    if any(m in t for m in CHUNK_MARKERS):
        return True, "copyright/license/frontmatter"
    n_year = len(_REFLIST_YEAR.findall(text))
    n_pages = len(_REFLIST_PAGES.findall(text))
    n_etal = t.count("et al")
    if (n_year + n_pages + n_etal) >= 3:
        return True, "reference-list density"
    stats = _surface_stats(text)
    if stats["n_sentences"] <= 1 and stats["rare_word_ratio"] > 0.5:
        return True, "table/figure artifact (surface_stats)"
    return False, None


def arm1a_boilerplate_enrichment(records, embeddings, k, top_n=20):
    """Andel strukturellt-icke-innehåll i topp-N glesaste regioner vs korpus-baslinje."""
    severity = void_severity(embeddings, k)
    order = np.argsort(severity)[::-1]
    top_sparse_idx = [int(i) for i in order[:top_n]]

    baseline_flags = [is_structural_noncontent(r.text)[0] for r in records]
    baseline_rate = sum(baseline_flags) / len(baseline_flags)

    sparse_flags = [is_structural_noncontent(records[i].text)[0] for i in top_sparse_idx]
    sparse_rate = sum(sparse_flags) / len(sparse_flags)

    enrichment = sparse_rate / baseline_rate if baseline_rate > 0 else float("inf")

    return {
        "top_n": top_n,
        "corpus_baseline_rate": baseline_rate,
        "sparse_cohort_rate": sparse_rate,
        "enrichment_ratio": enrichment,
        "sparse_region_indices": top_sparse_idx,
        "sparse_flags_detail": [
            {"chunk_index": i, "flagged": f, "reason": is_structural_noncontent(records[i].text)[1]}
            for i, f in zip(top_sparse_idx, sparse_flags)
        ],
    }


def arm1b_geometry_ground_truth(records, embeddings, sections, k_candidate):
    """Rent geometriskt facit-test -- återanvänder D-011:s låsta graderade
    leave-one-out-maskineri (`run_graded_leave_one_out_section`) rakt av, i
    stället för att uppfinna ett nytt mått. `best_rank_fraction` = 0 betyder
    "mest gap-lik plats i hela den beskurna korpusen", 1 betyder minst gap-lik.

    `sections`: dict source_file -> lista av sektioner (som i
    .cache/d026_sections_mechanical.json), dokumentnyckeln är redan det
    faktiska `source_file`-namnet i records.
    """
    results = []
    for source_file, doc_sections in sections.items():
        for sec in doc_sections:
            start, end = sec["start_chunk"], sec["end_chunk"]
            r = run_graded_leave_one_out_section(
                records, embeddings, source_file, (start, end), sec["heading"], k_candidate,
            )
            results.append({
                "heading": sec["heading"], "source_file": source_file,
                "start_chunk": start, "end_chunk": end, "size": sec["size"],
                "best_rank": r.best_rank, "best_rank_fraction": r.best_rank_fraction,
                "n_truncated": r.n_truncated,
            })
    return results


def arm1b_random_control(records, embeddings, sections, k_candidate, seed=2026):
    """Matchad slumpkontroll till Arm 1b: samma antal kontigua sektioner, samma
    storleksfördelning (per dokument), men slumpmässigt placerade i stället för
    vid kända rubrikgränser. Samma D-011-maskineri, för direkt jämförbarhet."""
    rng = np.random.default_rng(seed)
    results = []
    for source_file, doc_sections in sections.items():
        n_doc = sum(1 for r in records if r.source_file == source_file)
        for sec in doc_sections:
            size = sec["size"]
            max_start = n_doc - size
            if max_start < 0:
                continue
            start = int(rng.integers(0, max_start + 1))
            end = start + size - 1
            label = f"random_control[{sec['heading']}]"
            r = run_graded_leave_one_out_section(
                records, embeddings, source_file, (start, end), label, k_candidate,
            )
            results.append({
                "heading": label, "source_file": source_file,
                "start_chunk": start, "end_chunk": end, "size": size,
                "best_rank": r.best_rank, "best_rank_fraction": r.best_rank_fraction,
                "n_truncated": r.n_truncated,
            })
    return results


# ---------------------------------------------------------------------------
# Arm 2 (siktning, LLM med facit) -- testar Mod A. Sikta generatorn mot en
# borttagen sektions PLATS via de positionellt gränsande chunkarna (inte
# embedding-närmaste, D-026:s poäng är just att testa positionell siktning),
# be den beskriva vad som "bygger bro" mellan dem, och mät om det genererade
# innehållet återfinner den borttagna sektionens SPECIFIKA innehåll/omfång.
# ---------------------------------------------------------------------------

BRIDGING_PROMPT_TEMPLATE = """You are a domain expert reading two excerpts from a \
document, taken from immediately before and immediately after a gap in the text \
(the material that originally connected them has been removed for this exercise).

DOMAIN CONTEXT:
{domain_context}

EXCERPT A (immediately BEFORE the gap):
{excerpt_before}

EXCERPT B (immediately AFTER the gap):
{excerpt_after}

TASK: Based on these two excerpts, describe the content that most plausibly BRIDGES \
the gap between them -- what specific topic, subtopic, or transition would a document \
of this kind cover here to connect Excerpt A to Excerpt B? Be as specific and concrete \
as you can (name the population/mechanism/procedure/topic you infer belongs here, not \
just a generic transition sentence). Answer in 3-5 sentences, nothing else."""


SCOPE_RECOVERY_JUDGE_PROMPT_TEMPLATE = """You are a scope-recovery judge for a research \
project testing whether an LLM, given only the material immediately surrounding a \
removed section of a document, can recover what was actually removed.

DOMAIN CONTEXT:
{domain_context}

ACTUAL REMOVED CONTENT (ground truth, what was really there):
{removed_text}

GENERATED BRIDGING TEXT (the model's guess, given only the surrounding excerpts, \
WITHOUT seeing the removed content):
{generated_text}

Do this in order:
1. Identify the SPECIFIC scope of the actual removed content: the precise \
sub-topics, populations, mechanisms, or procedures it covers -- not just its general \
subject area.
2. Check whether the generated text recovers that SPECIFIC scope, not merely the same \
broad topic. A generated text that names the right general subject area (e.g. "epilepsy \
management") but misses the actual sub-scope that was removed (e.g. the removed content \
was specifically about pediatric dosing, but the generated text talks about adult \
diagnosis) should be judged as NOT recovering the scope.
3. Label "scope_recovered" if the generated text captures the specific sub-topics/scope \
of the removed content (broad topical overlap is NOT sufficient on its own). Label \
"topic_only" if it gets the general subject area right but misses the specific scope. \
Label "not_recovered" if it misses both.

Respond ONLY with valid JSON in this form:
{{"label": "scope_recovered" or "topic_only" or "not_recovered", "confidence": <number 0.0-1.0>, "rationale": "1-3 sentence justification, citing what specific scope was or wasn't recovered"}}"""


def bridging_context(records, source_file, start_chunk, end_chunk, window=7):
    """Positionellt (INTE embedding-mässigt) gränsande chunkar, i dokumentordning."""
    doc_records = sorted(
        (r for r in records if r.source_file == source_file), key=lambda r: r.chunk_index
    )
    before = [r for r in doc_records if r.chunk_index < start_chunk][-window:]
    after = [r for r in doc_records if r.chunk_index > end_chunk][:window]
    return before, after


def run_arm2_section(
    anthropic_client,
    judge_model,
    generator_model,
    domain_context,
    records,
    embeddings,
    embedder,
    source_file,
    start_chunk,
    end_chunk,
    heading,
    window=7,
    temperature=0.5,
    max_tokens_generate=300,
    max_tokens_judge=500,
):
    import json
    import re

    before, after = bridging_context(records, source_file, start_chunk, end_chunk, window)
    excerpt_before = "\n\n".join(f"[{j+1}] {r.text}" for j, r in enumerate(before))
    excerpt_after = "\n\n".join(f"[{j+1}] {r.text}" for j, r in enumerate(after))

    gen_prompt = BRIDGING_PROMPT_TEMPLATE.format(
        domain_context=domain_context, excerpt_before=excerpt_before, excerpt_after=excerpt_after,
    )
    gen_resp = anthropic_client.messages.create(
        model=generator_model, max_tokens=max_tokens_generate, temperature=temperature,
        messages=[{"role": "user", "content": gen_prompt}],
    )
    generated_text = gen_resp.content[0].text.strip()

    # (a) embedding-likhet: genererad text vs den BORTTAGNA sektionens centroid
    removed_idx = [
        i for i, r in enumerate(records)
        if r.source_file == source_file and start_chunk <= r.chunk_index <= end_chunk
    ]
    removed_emb = _l2_normalize(embeddings[removed_idx])
    removed_centroid = removed_emb.mean(axis=0, keepdims=True)
    removed_centroid = removed_centroid / np.linalg.norm(removed_centroid)
    gen_emb = _l2_normalize(embedder.embed([generated_text]))
    centroid_similarity = float(gen_emb[0] @ removed_centroid[0])

    # (b) LLM-domare: specifikt omfång, inte bara bred ämnesträff
    removed_text = " ".join(records[i].text for i in removed_idx)
    removed_text_truncated = removed_text[:3000]  # rimlig kontextgräns för domarprompten
    judge_prompt = SCOPE_RECOVERY_JUDGE_PROMPT_TEMPLATE.format(
        domain_context=domain_context, removed_text=removed_text_truncated,
        generated_text=generated_text,
    )
    judge_resp = anthropic_client.messages.create(
        model=judge_model, max_tokens=max_tokens_judge, temperature=0.0,
        messages=[{"role": "user", "content": judge_prompt}],
    )
    judge_text = judge_resp.content[0].text.strip()
    match = re.search(r"\{.*\}", judge_text, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group(0))
        except json.JSONDecodeError:
            parsed = {"label": "parse_error", "confidence": None, "rationale": judge_text}
    else:
        parsed = {"label": "parse_error", "confidence": None, "rationale": judge_text}

    return {
        "heading": heading, "source_file": source_file,
        "start_chunk": start_chunk, "end_chunk": end_chunk,
        "n_before_context": len(before), "n_after_context": len(after),
        "generated_text": generated_text,
        "centroid_similarity": centroid_similarity,
        "judge_label": parsed.get("label", "parse_error"),
        "judge_confidence": parsed.get("confidence"),
        "judge_rationale": parsed.get("rationale", ""),
    }
