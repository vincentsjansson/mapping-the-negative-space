# Mapping the Negative Space

## Geometric Gap Detection in Corpus Embeddings

### A Proof-of-Concept Report

**Author:** Vincent Jansson

**Year:** 2026

*Iteration 2 of a longer research programme. The predecessor iteration ("Embracing the Novelty of Noise") is a separate project in a separate repository; by a hard methodological rule (`CLAUDE.md`), no decision, threshold, statistic, or corpus-specific calibration from that iteration is reused here. Every number in this report is traceable to a decision-log entry (D-001–D-026) or a result file in this repository's own `.cache/`.*

---

## Abstract

Organisations increasingly rely on retrieval-augmented systems over their own document corpora, but such systems can only answer from what a corpus *contains*. What a corpus never says — its coverage gaps, its blind spots — is invisible to any method that reasons from present content alone, and yet those absences are frequently where the most consequential risk sits. This study asks whether such absences can be surfaced *geometrically*: whether regions of low local density in an embedding space of a corpus correspond to meaningful, genuinely-missing content, and whether a language-model cohort steered toward those sparse regions can articulate coverage gaps that survive automated screening better than a random-region control.

The study evaluates a four-level screening pipeline (geometric region selection, broad-corpus coverage search, graded triviality judgement, and leave-one-out external verification) across three structurally dissimilar, openly-licensed corpora — clinical/WHO (C1), telecom/RFC (C2), and education/UNESCO (C3) — and, for the paid effect-size probe, on C1 only. Each design decision was pre-registered and locked in an append-only decision log before the corresponding result was observed; corrections, contaminations, and confounds are logged with both before- and after-states and their temporal order.

The headline results are predominantly negative and are reported as such. No gap-detection method, embedding space, or neighbourhood-size formula generalised reliably across the three corpora (D-004, D-013, D-015, D-018); whitening improved detection in only 8 of 12 pre-registered comparisons, below the locked 10/12 bar (D-014); temperature had a negligible effect on the answer-to-source distance across all three corpora (D-017); and both bi-encoder (style-matched AUC 0.388) and cross-encoder (AUC 0.579) operationalisations of "already covered" failed their separation gate, forcing Level 1 to become an LLM coverage judge (D-021–D-024). The C1 effect-size probe returned a difference in per-region authenticity of **d̂ = −0.208, 95% CI [−0.387, −0.029], p = 0.024** (D-025/D-026 probe file) — the sparse (geometrically-selected) cohort produced *fewer* surviving non-trivial gap statements than the random control, a directionally negative result on the best-detecting corpus. The follow-up association test (D-026) found both the detection step and the generation step independently weak and did not fit cleanly into any of its three pre-registered interpretive branches.

Set against these negative and inconclusive findings, the validated contributions are narrow and methodological: a distance-concentration characterisation that keeps the percentile signal interpretable on C1 (CV 0.180); a leave-one-corpus-out overfitting control that correctly caught a method (`persistent_homology`) which won on two corpora and collapsed on the third; the exposure and correction of four distinct confounds (a whitening leak, a pairwise-vs-max threshold mismatch, a generation-style artefact, and a cross-lingual mismatch); and an LLM coverage judge that passes its anchor gate at balanced accuracy 0.933. We argue that the negative findings themselves are the primary methodological contribution of this proof-of-concept: they demonstrate, with a pre-registered and self-auditing apparatus, that *geometric sparsity is at best a weak proxy for meaningful coverage gaps* in this pipeline, and that the discipline of logging each confound with its temporal order is what makes that conclusion trustworthy rather than merely disappointing.

---

## Preface

This is an independent proof-of-concept study, carried out under a pre-registration discipline modelled on a clinical-trial protocol rather than on exploratory data analysis. Every hypothesis-relevant decision was written into an append-only decision log (`beslutslogg.md`, entries D-001 through D-026) and locked *before* the corresponding result was observed and interpreted. Decisions were never overwritten; where a later decision revised an earlier one, it was appended as a new entry that cites the old, and the superseded text was left in place so that the reasoning trace is preserved in full.

No hypothesis-relevant parameter was tuned after its outcome was seen. Where a value was chosen after a result was observed — most notably the worst-case configuration selection in D-015 — this is flagged explicitly in the text as a motivated, openly-declared post-hoc choice rather than presented as a clean pre-registered selection, and the genuine out-of-sample test is deferred to the next new corpus. Where an error or confound was discovered, it is reported with both its before-state and its after-state, and with an honest statement of whether it was caught *before* interpretation (e.g. the whitening leak of D-013, caught by the author's own question before the contaminated numbers were treated as fact) or *during* it (e.g. the cross-lingual confound of D-024, discovered while constructing anchors for a later step). Contaminated numbers are retained, struck through in the log and clearly marked "do not cite as fact," rather than deleted.

The reader should therefore expect a report in which negative and inconclusive results are given the same prominence as positive ones, and in which the machinery for catching the study's own mistakes is treated as a first-class result.

---

## Table of Contents

1. Introduction
   1.1 Background
   1.2 Purpose and Research Questions
   1.3 Scope
   1.4 Report Structure
2. Method
   2.1 Theoretical Background
   2.2 System Architecture
   2.3 Corpora
   2.4 Definitions and Metrics
   2.5 Pre-registration and Methodological Discipline
   2.6 Backtest Design
3. Results
   3.1 Leave-one-out (binary facit)
   3.2 Method and embedding bake-off
   3.3 Whitening robustness
   3.4 Temperature robustness
   3.5 Level 1 rebuild
   3.6 The C1 effect-size probe
   3.7 D-026 association test — Arms 1a, 1b, 2
4. Discussion and Conclusions
   4.1 Interpretation through the organising principle
   4.2 The Red Thread: fabrication as a structural threat
   4.3 Methodological discipline as a contribution
   4.4 Was the purpose achieved?
   4.5 Threats to validity and limitations
   4.6 Future work
5. References
6. Appendices
   A. Decision-log extract (D-001–D-026)
   B. Prompts (verbatim)
   C. Full result tables

---

## 1. Introduction

### 1.1 Background

Retrieval-augmented generation and, more broadly, any system that answers questions from a fixed document corpus share a structural limitation: they can only surface what the corpus contains. A corpus is, in effect, a positive space of asserted content, and the systems built on top of it inherit that positivity. The complementary object — the *negative space*, the set of topics, intersections, and edge cases the corpus never addresses — is precisely what such systems cannot see, and yet it is often where a corpus owner's real exposure lies: the risk never written down, the population never mentioned, the interaction between two well-covered themes that is itself never discussed. The motivating premise of this project, carried forward from the design document, is compact: *what a corpus never mentions is its blind spots.*

That premise is attractive but fragile. Absence is not the same as a blind spot. Something may be missing because it is irrelevant, because it was deliberately left out, or because it belongs to a different document altogether — none of which a purely geometric or retrieval-based method can distinguish from a genuine, consequential gap. A full authenticity test for a coverage gap ("absent AND relevant AND non-trivial AND not deliberately excluded") is therefore not automatable end-to-end; the last two conjuncts require a human. This study accepts that limitation up front and asks a deliberately narrower, testable question: whether *geometric sparsity* in a corpus's embedding space is a usable proxy for the first, automatable part of the definition — whether the regions an embedding model renders as low-density are, in fact, where meaningful missing content sits.

Concretely, the study investigates whether a corpus-reading agent cohort, steered toward geometrically-identified sparse regions of an arbitrary corpus, can formulate coverage-gap statements that survive automated screening *better than a random-region control*, and whether the architecture is genuinely domain-agnostic in practice across three structurally dissimilar corpora.

### 1.2 Purpose and Research Questions

The organising principle of the entire investigation — made explicit only late in the project, in D-026, but latent throughout — is the separation of two questions that a naive "geometry finds gaps" claim silently conflates:

1. **Is the hole a gap?** — a question about *detection*: does geometric sparsity mark locations where genuinely-missing, content-bearing material would sit, as opposed to boilerplate, structural artefacts, or arbitrary thin spots?
2. **Can the hole be filled?** — a question about *generation*: given a location the geometry flags, can a language model articulate the specific content that is actually missing there, rather than a plausible-sounding but wrong guess?

These are logically independent. The pipeline can fail at either step, and the failure modes call for entirely different remedies. Keeping them separate is what allows a negative composite result to be diagnosed rather than merely lamented.

The project probed this principle from several distinct angles, each locked as its own pre-registered test: the generalisation of the neighbourhood-size (k) formula across domains (D-004); a five-method, three-embedding-space detection bake-off (D-013); a robustness test of the whitening embedding transform (D-014); a global-configuration selection on a worst-case criterion (D-015); a second-round void-family bake-off (D-018); a robustness check on temperature phase transitions (D-017); the operationalisation of "already covered" for the broad-corpus search (D-020–D-024); a paid effect-size probe on the best-detecting corpus (D-025); and a two-armed association test separating detection from generation with independent ground truth (D-026).

From these, four explicit research questions are formulated:

- **RQ1.** Does geometric sparsity identify meaningful coverage gaps better than chance — i.e. does a sparse-region cohort produce a higher rate of surviving non-trivial gap statements than an equally-sized random-region control?
- **RQ2.** Does any single gap-detection method, embedding space, or neighbourhood-size formula generalise reliably across three structurally dissimilar corpora, or is the choice irreducibly corpus- and scale-dependent?
- **RQ3.** Can "already covered" be operationalised so that the pipeline reliably distinguishes genuine absence from mere topical proximity within the corpus vocabulary?
- **RQ4.** When geometry flags a hole, can the generation step recover the specific content that was actually removed from that location, or only its broad topic?

### 1.3 Scope

This is a proof-of-concept, and its claims are bounded accordingly. Three caveats are load-bearing and are flagged here so that no result below is read beyond its warrant.

First, **the effect-size probe is a pilot with n = 40 regions** (20 sparse + 20 random) on a single corpus. Its purpose, fixed before any paid generation was run (D-019 sub-step D), was to *estimate an effect size to dimension a full study*, not to constitute a hypothesis test; its p-value is reported for completeness but was pre-committed never to be used as a result in its own right.

Second, **the probe was run on C1 only** — the clinical/WHO corpus, chosen as the best-detecting of the three under the frozen configuration. No claim about C2 or C3 generation performance is supported by the probe.

Third, **the probe result does not generalise across corpora.** The whole detection arc (D-004–D-018) already established that no configuration is uniformly best across the three corpora; the probe inherits that limitation and is explicitly a single-corpus, single-scale observation. Cross-corpus generalisation of the probe is out of scope and is named as future work, not as a supported finding.

Additional standing limitations (pilot size, corpus composition, boilerplate-classifier recall, single-corpus generation evidence, embedding-model dependence, and training-data awareness of the generator models) are enumerated in §4.5.

### 1.4 Report Structure

Section 2 (Method) states the theoretical background for each geometric and information-theoretic primitive used, the four-level system architecture and its locked model strings and parameters, the three corpora with their composition tables and declared limitations, the formal definitions and metrics with their governing D-numbers, the pre-registration discipline including the identification and correction of the four confounds, and the backtest design. Section 3 (Results) reports every measurement without interpretation, one sub-section per measurement, with numbered tables and exact figures each cited to a D-entry or result file. Section 4 (Discussion) interprets those results through the organising principle of §1.2, develops the fabrication-as-structural-threat "red thread," argues for methodological discipline as a contribution, answers RQ1–RQ4 explicitly with a "what was shown / what was not shown" accounting, enumerates the threats to validity, and orders future work from highest evidential priority to most speculative. Section 5 lists references in APA 7 style. Section 6 contains the decision-log extract (Appendix A), the verbatim prompts (Appendix B), and the full result tables (Appendix C).

---

## 2. Method

### 2.1 Theoretical Background

The pipeline draws on several distinct literatures for its geometric and information-theoretic primitives. Each is stated here as a short titled paragraph; the implementations and the way each was actually used are given in §2.2–2.4.

**Void and spherical-contact statistics.** The eventual locked detection method, `void_stat` (D-015), operationalises a coverage gap as an *empty-space* score: for a candidate region, how large is the local void around it relative to the corpus. This is the embedding-space analogue of the spherical-contact distribution and the empty-space function *F* from spatial point-process statistics (Baddeley, Rubak, & Turner, 2015), which measure the distance from an arbitrary location to the nearest point of a pattern and are the classical way to characterise voids in a point cloud.

**Persistent homology.** One bake-off candidate (D-013) scored regions by the persistence of topological features (H1/H2) in their neighbourhood, following the persistent-homology framework of computational topology (Edelsbrunner & Harer, 2010). The intuition is that a genuine gap should register as a persistent hole in the filtration of the local point cloud rather than as a transient one.

**Local Outlier Factor and Kernel Density Estimation.** Two further candidates operationalised sparsity as *relative local density*: the Local Outlier Factor (Breunig, Kriegel, Ng, & Sander, 2000), which compares a point's local reachability density to that of its neighbours, and a kernel-density-estimate score (Silverman, 1986), which flags regions of low estimated probability mass. Both formalise "sparse" as "low density relative to the rest of the corpus."

**Embedding anisotropy and the whitening transform.** Contextual and sentence embeddings are known to occupy a narrow, anisotropic cone rather than filling their nominal space, which inflates apparent similarity between arbitrary items (Ethayarajh, 2019). Whitening — mean-centring followed by a covariance-based transform to unit isotropy — is the standard counter-measure, and was tested here as an alternative embedding space (D-013, D-014, D-016). The distance-concentration phenomenon (Beyer, Goldstein, Ramakrishnan, & Shaft, 1999; Aggarwal, Hinneburg, & Keim, 2001), whereby nearest- and farthest-neighbour distances converge as dimension grows, is a related but distinct high-dimensional risk that motivated the explicit Step 0.5 characterisation (D-007).

**Novelty search.** The conceptual framing of "search the sparse regions" is kin to novelty search (Lehman & Stanley, 2011), which abandons an explicit objective in favour of rewarding behavioural novelty — reaching parts of a space nothing has reached before. The project borrows the *intuition* (value the unreached) while noting, in the discussion, that novelty in a representation is not the same as significance to a corpus owner.

**Bisociation.** The idea that a meaningful gap often sits at the *intersection* of two well-covered but never-connected themes is Koestler's (1964) notion of bisociation — creativity as the joining of two previously-unrelated matrices of thought. This is the theoretical warrant for the "local gap between established themes" gap-type; it is a theory-validated but mechanism-unproven framing here — the report treats bisociation as a motivating theory whose operational mechanism was not demonstrated by the data.

**Literature-based discovery.** The most speculative future direction — building explicit concept bridges between disjoint regions — descends from Swanson's (1986) literature-based discovery, in which two literatures that never cite each other (the Raynaud's/fish-oil case) are connected through a shared intermediate term. It is named in §4.6 as a *conceptual, not validated* direction for a separate future project.

### 2.2 System Architecture

The pipeline is a four-level screening chain (Levels 0–3) in which each level is cheaper to be wrong about than the next, and each is designed to remove candidates the previous one could not.

**Level 0 — geometric region selection (free).** Over cached embeddings of the whole corpus, two gap-types are computed: a *local gap* (distance to nearest-neighbour chunk) and an *edge/centroid gap* (distance to the corpus centroid). Regions above the 90th percentile on either measure are flagged (raised to the 95th if the flagged union exceeds 15% of the corpus, D-005). Nearest-neighbour search uses a ball-tree, because KD-trees degrade at 384 dimensions. After the bake-offs, the locked production detector is `void_stat` on raw MiniLM embeddings with sqrt-k neighbourhood size (D-015). An equally-sized random-region control cohort is mandatory (D-001) so that Level 0's core claim is testable rather than self-confirming.

**Level 1 — broad-corpus coverage search.** Given a generated gap statement, the pipeline asks whether the corpus in fact already covers it. After bi-encoder and cross-encoder operationalisations were exhausted (§2.5, §3.5), Level 1 became an **LLM coverage judge** (D-023): the claim plus the top-k cosine-retrieved chunks (a ±2-chunk window around the claim's own source region excluded, D-024) are passed to a language model that returns covered / not-covered, a confidence, and a rationale, at temperature 0, with `top_k = 30` (D-023 pre-registered adjustment).

**Level 2 — graded triviality judge (`void_stat` region → judgement).** A domain-adapted LLM triviality judge classifies a surviving statement as trivial or non-trivial, calibrated by few-shot examples that deliberately include a "middle-of-the-road" (mechanical-averaging) example so that the judge catches the one failure mode the geometry cannot see (D-001, H2). It is prompt/few-shot only, never fine-tuned.

**Level 3 — human judgement.** Deliberately omitted from this PoC (Path 2, D-001) and named as the non-automatable arbiter; the surviving statements are *candidates*, never confirmed gaps.

The two LLM judges (Level 1 coverage, Level 2 triviality) are the load-bearing decision points. The generator and judge model strings are locked in `config.py`: the Phase-1 generators are `claude-haiku-4-5-20251001` (Anthropic) and `gpt-4o-mini` (OpenAI), run side-by-side so that any temperature effect can be tested for model-specificity vs. generality. Locked geometric parameters include `PERCENTILE_DEFAULT = 90`, `UNION_HIGH_THRESHOLD = 0.15`, `K_MIN = 3`, `K_MAX = 10`, `K_CANDIDATES = (log, sqrt)`, `CHUNK_SIZE_DEFAULT = 400 / OVERLAP 50 / MIN_CHARS 60`, `EMBEDDING_MODEL = sentence-transformers/all-MiniLM-L6-v2` (384-d), `SKIP_CLUSTERING = True` (D-009), and the frozen production triple `DEFAULT_GAP_METHOD = void_stat / DEFAULT_EMBEDDING_SPACE = minilm / DEFAULT_K_CANDIDATE = sqrt` (D-015).

### 2.3 Corpora

Three structurally dissimilar, openly-licensed corpora were built to test whether the architecture is domain-agnostic in practice; a fourth (BCM, the iteration-1 fallback) was available but not used in the runs reported here. All three are public, giving the study a reproducible-corpus status (D-008). Composition is given in Table 2.1.

**Table 2.1 — Corpus composition.**

| | C1 — Clinical (WHO) | C2 — Telecom (RFC) | C3 — Education (UNESCO) |
|---|---|---|---|
| Documents | 3 | 16 | 3 |
| Pages | 369 | 568 | 1,255 |
| Characters | 1,002,691 | 1,290,499 | 4,499,309 |
| Chunks (N) | 2,939 | 3,214 | 14,181 |
| Register | directive clinical prose | dense normative standards text | narrative policy report |
| Licence | CC BY-NC-SA 3.0 IGO | IETF Trust / BCP 78 | CC BY-SA 3.0 IGO |
| Source docs | IPC Core Components; Physical Activity & Sedentary Behaviour; mhGAP-IG 2.0 | 16 RFCs (DNSSEC, HTTP/1.1 + cookies + HSTS, IPv6 suite) | GEM 2020; Reimagining our futures together; GEM 2023 |

*Chunk counts derived from the leave-one-out truncation records (`*_graded_loo.json`): C1 N = 2,935–2,939 depending on the run's own truncation; C2 N = 3,214; C3 N = 14,181. The C1 config value of record is 2,939 (`config.py`).*

**Declared limitations (D-008, pre-registered before analysis, not after a weak result).** C1 is WHO-only (the planned WHO + NICE balance was abandoned when NICE downloads returned only summaries and flooded the fetch tool); it is 369 pages, below the ~500-page target, and was accepted as-is with no document added afterward. C2 is thematically narrower than planned — flagship RFCs (TLS 1.3, HTTP semantics, QUIC, TCP, DNS, OAuth) exceeded the fetch tool's ~117 KB ceiling and were replaced by completely-fetchable, thematically-adjacent RFCs, leaving the corpus skewed toward security/infrastructure. The wide N-span (C1 ≈ 1.00M, C2 ≈ 1.29M, C3 ≈ 4.50M characters) is a deliberate benefit: it gives the k-formula scaling test several N-points to run over. A text-surface-statistics control (`_surface_stats()`, D-009) is retained for the C2 confounder check, so that a detection difference cannot be attributed to raw surface features alone.

### 2.4 Definitions and Metrics

**Gap-types (Level 0).** For chunk *i* with embedding *e_i*, the local-gap severity is the distance to its nearest neighbour, and the edge severity is the distance to the corpus centroid *c* = (1/N) Σ *e_j*. Both are computed on L2-normalised embeddings; a region is flagged if either severity exceeds the 90th percentile of its distribution (D-005).

**void_stat severity.** The locked detector scores a region by its local empty-space statistic — the size of the void around the region relative to the corpus — rather than by a single nearest-neighbour distance; it is the empty-space/*F*-function analogue described in §2.1. It is a policy choice of severity function, selected on a worst-case criterion (D-015), not a derived optimum.

**Neighbourhood size k (D-004).** Two pre-registered candidates, each clipped to [3, 10] via *k* = max(3, min(10, ·)): the logarithmic *k* = round(0.5·ln N) and the square-root *k* = round(0.5·√N). No third candidate may be added post-hoc. Realised values: C1 *k_log* = 4, *k_sqrt* = 10; C2 *k_log* = 4, *k_sqrt* = 10; C3 *k_log* = 5, *k_sqrt* = 10.

**Graded leave-one-out rank/N (D-011).** For a removed unit, the pipeline finds the rank, in the global sparse-region ranking of the truncated corpus, of the region nearest the removed unit's original position, and reports both `rank` and the normalised `rank/N` (0 = most gap-like). By removing units of different sizes, a curve of *fraction removed* vs *rank/N* is obtained. This graded measure supplements — never replaces — the binary top-10 facit of D-004/D-006.

**Binary leave-one-out facit (D-006).** Among the `LEAVE_ONE_OUT_TOP_N = 10` most gap-flagged regions of the truncated corpus, the fraction whose true nearest neighbour lies in the *removed* document; a run "succeeds" if this fraction reaches `LEAVE_ONE_OUT_SUCCESS_FRACTION = 0.5` (a locked policy majority rule).

**Per-region authenticity and effect size d̂ (D-019 sub-step C).** Because each region yields up to six correlated statements (3 temperatures × 2 models), the analysis unit is the *region*, not the statement, to avoid pseudo-replication. A region's authenticity rate is the fraction of its statements that survive Levels 1 and 2 as non-trivial. The probe reports the mean authenticity for the sparse vs. random cohorts, their difference **d̂**, and a 95% CI on the difference; per-model rates are reported separately as a robustness check.

**Distance concentration (D-007).** Characterised on C1 by the coefficient of variation of pairwise distances (0.180), the mean relative contrast (3.76), and the minimum relative contrast (0.79); assessment: not strongly concentrated, so the percentile threshold retains signal.

**Locked thresholds cited to D-numbers.** `level1_match_threshold = 0.357` for C1 (D-003/D-010, midpoint of known-related/unrelated anchors); percentile 90/95 (D-005); `PHASE2_DERIVATIVE_MULTIPLIER = 2.0` and fallback temperatures (0.2, 0.5, 0.9) (D-002/D-017); AUC gate ≥ 0.85 for any Level-1 discriminator (D-022/D-023).

### 2.5 Pre-registration and Methodological Discipline

Every hypothesis-relevant number was locked in `beslutslogg.md` before its result was seen. The most important methodological events of the project, however, were the identification and correction of four confounds — because they are the reason several early, encouraging numbers do not appear as findings. They are stated here with both before- and after-states and, critically, their *temporal order* relative to interpretation.

**Confound 1 — the whitening leak (caught before interpretation).** In the first D-013 bake-off, the whitening transform was fitted once per corpus over *all* chunks, including the content later "removed" in each leave-one-out fold; `run_bakeoff_indices()` then truncated the already-whitened matrix. The transform's mean/covariance therefore saw the removed content's contribution — a leak that could inflate the whitened-embedding results, most at large removals (up to 29% of C1). The author caught this by asking directly whether `whiten()` was re-fitted per fold; the answer was no. A `transform_fn` parameter was added so whitening is applied *after* truncation on raw embeddings, all 90 combinations were re-run, and the contaminated numbers were retained struck-through and marked "do not cite." The correction mattered: C2's best combination flipped from whitened (0.0583) to raw MiniLM (0.0996), confirming the leak had inflated exactly C2's whitening result. This was caught *before* the numbers were treated as fact.

**Confound 2 — the pairwise-vs-max threshold mismatch (caught during interpretation).** The Level-1 threshold (D-003/D-010, 0.357 on C1) was calibrated against *pairwise* chunk-chunk similarity (mean ≈ 0.24), but Level 1 at run-time performs a *max-over-N* search (mean ≈ 0.75 for genuine corpus content over ~2,900 candidates). The threshold was thus calibrated on the wrong statistic — an order-statistic inflation of roughly 3×, independent of text class. This surfaced only when the D-019 probe's Level 1 flagged 97.5–97.9% of statements as "already covered," a degenerate pass-through; a length-truncation fix (D-020) removed the Level-2 parse errors but not the degeneracy, and the direct 30-chunk test then exposed the pairwise/max mismatch as the true cause.

**Confound 3 — the style confound (caught during interpretation).** When Level-1 anchors were revalidated in English, an apparently strong bi-encoder separation (AUC 0.952) turned out to be a *style* artefact: the "covered" anchors were synthesising summaries and the "new" anchors were absence-statements, which are lexically easy to tell apart regardless of actual coverage. Forcing both anchor sets into the same text class — absence-statements, the real production class — collapsed the separation to AUC 0.388 (p = 0.933), directionally reversed. This is why the bi-encoder was ultimately excluded for Level 1.

**Confound 4 — the cross-lingual confound (caught during interpretation, exposing a fourth error).** Generated claims and anchors were Swedish, C1 is English, and `all-MiniLM-L6-v2` is not multilingual; English gave +0.24–0.30 similarity and the correct document, while Swedish retrieved the wrong document in 2 of 3 tested cases. The generation/anchor language was switched wholesale to English, keeping the same monolingual model (a multilingual model would have broken D-015). The mandatory pre-rerun audit that D-024 required then exposed a *fourth, non-language* inconsistency: D-021's "covered" anchors had been built with a ±2 exclusion window, but `search_corpus_for_coverage()` — the function actually used in the probe — had no exclusion window at all, so a statement could trivially "find coverage" in its own source chunks. It was fixed with an `excluded_indices` parameter before any interpretation of the corrected numbers.

Honest temporal accounting: **Confound 1 was caught before interpretation**; **Confounds 2, 3, and 4 were caught during interpretation** of results that had already been computed, and are the reason the corresponding early numbers (the 0.357 pass-through, the AUC 0.952, the Swedish probe) do not appear as findings. All four are logged append-only with their before/after states.

### 2.6 Backtest Design

The study has two complementary backtests, neither of which pretends to be a full authenticity test (which requires Level 3).

**Leave-one-out (external ground truth).** A document or clearly-bounded section known to cover a named topic is removed; Levels 0–2 are run on the truncated corpus; the pipeline is then checked for whether a gap-region appears where the removed material's neighbourhood sat (binary, D-006) and how deep in the ranking that region falls (graded rank/N, D-011). This provides an *external* facit — an independent known outcome to measure against — which the design document (critique C1) identified as the missing piece in the earlier control-cohort-only design. Its limitation is structural and pre-registered: a small removed section cannot win a global top-10 window by construction, and a whole-document removal leaves no local "hole" to detect; the graded measure exists precisely to separate "near but not top-10" from "invisible."

**The probe: sparse-vs-random.** The paid effect-size probe (D-025/D-026) compares the sparse (geometrically-selected) cohort against an equally-sized random-region control on the *same* pipeline, same corpus, and reports the difference in per-region authenticity with a CI. What this test *does*: it tells us whether geometric sparsity yields a *higher* surviving-authenticity rate than chance on the best-detecting corpus. What it *does not do*: it cannot tell us whether a surviving statement names a gap that genuinely exists and is worth finding — that is the non-automatable Level-3 question — and, because the probe is single-corpus and single-scale, it does not license any cross-corpus claim. The D-026 association test was added specifically to diagnose *why* the composite result came out as it did, by separating the detection and generation questions with independent ground truth (§2.2 organising principle).

---

## 3. Results

All figures in this section are reported without interpretation; interpretation is deferred in its entirety to Section 4. Each number is cited to a decision-log entry or a `.cache/` result file. Full tables are reproduced in Appendix C.

### 3.1 Leave-one-out (binary facit) — D-004 / D-006

Leave-one-out was run on all three corpora, both k-candidates, at document and section level (12 runs). On the binary top-10 facit, 11 of 12 runs returned 0/10; the sole exception was C1 / mhGAP at document level (k_log 2/10, k_sqrt 1/10). No run reached the pre-registered success bar (≥ 50% of the top-10 pointing to the removed material). Per the second pre-registered outcome of D-004, **k becomes a per-corpus calibration parameter**; no universal formula is locked. k_log and k_sqrt performed comparably throughout; differences *between* corpora dominated differences between the formulas (D-004 RESOLVED note).

### 3.2 Method and embedding bake-off — D-013 / D-018

The D-013 bake-off ran all 90 combinations (5 methods × 3 embedding spaces × 3 corpora × 2 k) against the section-level removal target per corpus, scored by graded rank/N. After the whitening leak was fixed (§2.5), the corrected best combinations are in Table 3.1.

**Table 3.1 — D-013 corrected best combination per corpus (`bakeoff_*_v2.json`).**

| Corpus | Best combination (corrected) | rank/N |
|---|---|---|
| C1 clinical | whitened_minilm / persistent_homology / log-k | 0.0172 |
| C2 telecom | raw minilm / persistent_homology / sqrt-k | 0.0996 |
| C3 education | whitened_minilm / baseline / log-k | 0.0071 |

The winner criterion (lowest rank/N *consistently across all three corpora* and ≥ 2 embedding spaces) was **not met by any method**. `persistent_homology` won on C1 and C2 but was the *worst* method on C3 (0.298–0.533); the leave-one-corpus-out control caught this directly — selecting it on C1+C2 and confirming against held-out C3 fails. Outcome: undecided, no method locked. For reference, the frozen `void_stat`/raw-minilm rows were C1 sqrt 0.1418 / log 0.3482, C2 sqrt 0.1964 / log 0.1929, C3 sqrt 0.1546 / log 0.1299.

The second-round void-family bake-off (D-018, frozen config: raw MiniLM, sqrt-k, document + section per corpus) is in Table 3.2. Watershed/Voronoi-basin was dropped as intractable beyond ~10–20 dimensions; `cvde` was rank-degenerate against the baseline's local component; `dtm` gave a genuinely distinct signal. No challenger beat `void_stat`'s global worst-case, so `void_stat` remains the standard.

**Table 3.2 — D-018 rank/N and global worst-case (`bakeoff_d018.json`).**

| Corpus / level | void_stat | cvde | dtm |
|---|---|---|---|
| C1 doc | 0.3791 | 0.9268 | 0.8990 |
| C1 section | 0.1418 | 0.0354 | 0.0478 |
| C2 doc | 0.0342 | 0.0096 | 0.0055 |
| C2 section | 0.1964 | 0.2904 | 0.4927 |
| C3 doc | 0.8773 | 0.5021 | 0.5237 |
| C3 section | 0.1546 | 0.2125 | 0.1527 |
| **Global worst-case** | **0.8773** | 0.9268 | 0.8990 |

The D-015 correction note records that `void_stat`'s true global worst-case is 0.8773 (C3, document level), not the section-only ~0.196 that the D-015 selection had originally cited.

### 3.3 Whitening robustness — D-014

The whitening finding was tested over all six established removal targets (document + section, three corpora), both k-candidates, comparing raw MiniLM vs whitened on the baseline method (12 comparison pairs). Results in Table 3.3.

**Table 3.3 — D-014 whitening robustness (`d014_whitening_robustness_v2.json`).**

| Corpus | Level | k | raw rank/N | whitened rank/N | Improved? |
|---|---|---|---|---|---|
| C1 | Doc (mhGAP) | log | 0.8698 | 0.6539 | Yes |
| C1 | Doc (mhGAP) | sqrt | 0.8593 | 0.5692 | Yes |
| C1 | Section (SUI) | log | 0.0595 | 0.2670 | No |
| C1 | Section (SUI) | sqrt | 0.0537 | 0.0705 | No |
| C2 | Doc (RFC9112) | log | 0.0106 | 0.2210 | No |
| C2 | Doc (RFC9112) | sqrt | 0.0147 | 0.2087 | No |
| C2 | Section (§14) | log | 0.5473 | 0.4448 | Yes |
| C2 | Section (§14) | sqrt | 0.4341 | 0.4247 | Yes |
| C3 | Doc (Reimagining) | log | 0.7740 | 0.2254 | Yes |
| C3 | Doc (Reimagining) | sqrt | 0.7214 | 0.2405 | Yes |
| C3 | Section (Ch.9) | log | 0.3188 | 0.0071 | Yes |
| C3 | Section (Ch.9) | sqrt | 0.3589 | 0.0222 | Yes |

**8 of 12 pairs improved**, below the pre-registered 10/12 bar; whitening is not robustly confirmed as a general improvement. The D-016 mechanism analysis found whitening gain correlated equally with anisotropy and corpus-N (both Pearson r = +0.774, p = 0.003 — empirically indistinguishable over three corpora) and only weakly with removal fraction (r = 0.27, p = 0.40); no automatic whitening rule was introduced.

### 3.4 Temperature robustness — D-017

C2 and C3 flagged phase transitions (D-002) where C1 did not, but the whole temperature sweep moved the answer-to-source distance by only ~0.05–0.15, the two models disagreed on the transition location, and each temperature point had n = 3 regions. Under the robustness check, bootstrap stability of the flagged temperatures reached at most 70% (C2 Anthropic T = 1.0) and otherwise sat in the 23–60% range; the effect/noise ratio (sweep range over mean per-point region noise) was ≤ 1 in three of four cases (C2 Anthropic 0.94, C2 OpenAI 0.60, C3 OpenAI 0.42; sole exception C3 Anthropic 1.29). The transitions do not survive the noise. **Fixed fallback temperatures (0.2, 0.5, 0.9) are locked for all three corpora**, and the substantive finding is recorded that temperature has a negligible effect on the answer-to-source distance in this pipeline over the tested range.

### 3.5 Level 1 rebuild — D-020 / D-021 / D-022 / D-023 / D-024

The Level-1 "already covered" discriminator was rebuilt across five logged steps; the sequence of separation results is in Table 3.4. All AUC figures are against the 30 covered + 30 new anchors of the respective step.

**Table 3.4 — Level-1 discriminator separation across the rebuild.**

| Step | Discriminator | Anchors | AUC | p | Gate (≥0.85)? |
|---|---|---|---|---|---|
| D-021 | bi-encoder max-cosine (Swedish) | style-mismatched | 0.728 | 0.00125 | Fail |
| D-022 | cross-encoder (nli-deberta-v3-base) | style-mismatched | 0.579 | 0.149 | Fail |
| D-024 | bi-encoder (English) | style-**mismatched** | 0.952 | 9.3×10⁻¹⁰ | (artefact) |
| D-024 | bi-encoder (English) | style-**matched** | 0.388 | 0.933 | Fail |
| D-023 | **LLM coverage judge (English)** | style-matched | — | — | **Pass** |

The degeneracy that triggered the rebuild: the first probe (D-019/D-020) had Level 1 flag 97.9% of statements as already-covered (median similarity 0.472 vs threshold 0.357); after the D-020 fixes, parse errors went to 0/240 but already-covered stayed at 97.5%. A direct 30-chunk test showed pairwise similarity mean 0.242 but max-over-corpus mean 0.751 — the threshold had been calibrated on the wrong statistic (§2.5, Confound 2). The English style-matched bi-encoder result (AUC 0.388, p = 0.933; `d023_style_matched_gate_en.json`) shows the separation collapses when both anchor sets are held to the production text class, excluding both the bi-encoder and the cross-encoder for Level 1.

The LLM coverage judge (D-023) validation, English style-matched anchors (30 false-gap [covered] + 30 true-gap [new], ±2 exclusion window, top_k 10), is in Table 3.5.

**Table 3.5 — D-023 LLM coverage-judge validation (`d023_judge_validation.json`).**

| Metric | Value |
|---|---|
| Balanced accuracy | 0.933 |
| Confidence-weighted AUC | 0.971 |
| Sensitivity (covered correct) | 0.867 (26/30) |
| Specificity (true gaps correct) | 1.000 (30/30) |
| parse_error | 0/60 |

The gate (≥ 0.85) is passed with margin. The four misclassified "covered" cases were all the same pattern — the specific chunk naming the phrase was absent from the top-10 cosine candidates, a retrieval-depth issue, not a reasoning error — which is why top_k was pre-registered up to 30 before any re-validation. The Level-2 dry-run (D-019 sub-step A) classified its 30 held-out cases correctly (24 trivial + 6 non-trivial; `d019_step_a_dryrun.json`).

### 3.6 The C1 effect-size probe — D-025 / D-026

The probe was run on C1 only, 20 sparse + 20 random regions (all 40 present in the checkpoint per the D-025 completeness gate), three fixed temperatures, both models, through Levels 0–1–2, yielding 240 statements. Level 1 (the LLM judge) returned 190/240 not-covered; 115/240 statements survived Levels 1 and 2. Per-region authenticity (`d019_region_authenticity.json`) is in Table 3.6.

**Table 3.6 — Probe per-region authenticity and effect size.**

| Cohort | Mean authenticity | Anthropic | OpenAI |
|---|---|---|---|
| Sparse (n = 20) | 0.375 | 0.600 | 0.150 |
| Random (n = 20) | 0.583 | 0.833 | 0.333 |
| **Difference d̂** | **−0.208** | | |

95% CI on d̂: **[−0.387, −0.029]**; p = 0.024. The difference is negative: the sparse cohort produced a lower mean per-region authenticity than the random cohort. Per the pre-registration, the p-value is reported for completeness only and was committed never to be used as a result in its own right.

### 3.7 D-026 association test — Arms 1a, 1b, 2

**Arm 1a (boilerplate enrichment, `d026_arm1a_result.json`).** Corpus baseline structural-non-content rate 8.7% (0.0868); sparse top-20 (`void_stat`) rate 5.0%; enrichment ratio 0.576 — the wrong direction (sparse regions have *lower* boilerplate share than the corpus mean). A known recall weakness in the classifier means 0.576 likely understates the true value; even a coarse manual correction gives a ratio ≈ 1.15 — weak-to-no enrichment.

**Arm 1b (pure-geometry facit test, 38 sections, D-011 rank/N machinery; `d026_arm1b_result.json`).** Known content-bearing sections `best_rank_fraction` mean 0.260 / median 0.151 (0 = most gap-like) vs matched random control mean 0.318 / median 0.248. Mann-Whitney (real < random) p = 0.182 — the direction weakly favours known sections being more gap-like than chance, not statistically significant (n = 38).

**Arm 2 (LLM aiming, 5 sections, 10 calls; `d026_arm2_result.json`).** 1/5 `scope_recovered`, 1/5 `topic_only`, 3/5 `not_recovered`. No clear relationship between embedding-centroid similarity and the judge's scope verdict — the "Methods" section had the highest centroid similarity (0.608) yet was judged not to recover the scope. The single full hit ("Preface," mhGAP) has a trivial explanation: the boundary context literally contained a truncated table of contents (TOC leakage), making the aiming near-mechanical rather than genuine inference.

The outcome does not fit cleanly into any of the three pre-registered interpretive branches (Arm 1 falls / Arm 1 holds but Arm 2 falls / both hold). The coherent practical finding, though not a pre-defined branch, is that **both the detection step (Arm 1) and the generation step (Arm 2) are weak**, independently of one another.

---

## 4. Discussion and Conclusions

### 4.1 Interpretation through the organising principle

Read through the §1.2 principle — *is the hole a gap?* (detection) versus *can the hole be filled?* (generation) — the results converge on a single, unglamorous claim: **geometric sparsity is at best a weak proxy for meaningful coverage gaps in this pipeline**, and the two putative failure modes it could hide behind are both, in fact, weak.

On the detection side, nothing generalised. The k-formula did not (§3.1); no detection method won across all three corpora (§3.2); whitening helped on only 8 of 12 targets, and its apparent driver (anisotropy) is statistically inseparable from corpus size (§3.3). The one place detection looked usable — `void_stat` at section scale — is exactly where the D-015 correction note narrows the reliability claim: `void_stat` is reasonable for section-scale gaps (rank/N ≈ 0.14–0.20 across corpora) but unreliable for document-scale ones (up to 0.877 on C3). And Arm 1b, the cleanest pure-geometry facit test of all, could only muster a weak, non-significant direction (p = 0.182, n = 38) toward known content-bearing sections being more gap-like than chance.

The most direct evidence bears on RQ1. The probe's **d̂ = −0.208, 95% CI [−0.387, −0.029]** means that on the best-detecting corpus, the geometrically-selected cohort produced *fewer* surviving non-trivial gap statements than a random-region control. The plain reading is that the geometry is not merely uninformative but, if anything, anti-informative for authenticity as this pipeline measures it — importance and geometric isolation appear uncorrelated, and to the extent they relate at all, sparse regions were slightly *worse* seeds than random ones. One must be careful here: "authenticity" is survival through two LLM judges, not a Level-3 human verdict, and the probe is a single corpus at a single scale (§1.3). But within those bounds the direction is unambiguous and negative.

Arm 2 speaks to RQ4 and closes the diagnostic loop. Even when the generator was *aimed* at a known removed location, it recovered the specific scope in only 1 of 5 cases, and that one hit was an artefact of TOC leakage. Centroid similarity did not track scope recovery (the highest-similarity section, "Methods" at 0.608, was not recovered). So the composite negative of the probe is not rescued by either pre-registered failure mode in its pure form: detection is weak *and* aimed generation is weak. The premise that a corpus's blind spots sit at its embedding voids is, on this evidence, not supported.

### 4.2 The Red Thread: fabrication as a structural threat

A single thread runs through both iterations of this programme and through every level of this pipeline: a language model asked to characterise an absence will produce a fluent, specific, confident account of something that is not there. It is worth stating plainly because it is the mechanism behind the most important numbers in this report.

Arm 2 is the sharpest instance. The task was maximally favourable — the content had been removed on purpose, its neighbours were supplied, and the model was told to describe what belonged in the hole — and still, in the majority of cases, the generator fabricated a plausible but wrong account (the "Executive Summary" case invented a conflict-of-interest conclusion where the removed text was the guideline's opening rationale; the judge's own rationale documents the mismatch). This is not a tuning problem. It is the same structural behaviour that makes "generate the missing scenario from a sparse region" untrustworthy in the first place: the model's fluency is orthogonal to whether the content it describes is real. Level 1 and Level 2 exist precisely to catch this, and the reason Level 1 had to become an LLM judge (§3.5) is that no vector-similarity method could distinguish a claim about genuine absence from a claim that merely shares the corpus's vocabulary. The fabrication threat is therefore not a caveat to the method; it is the reason the method's central step cannot be trusted without a reader in the loop.

### 4.3 Methodological discipline as a contribution

If the substantive findings are negative, the process is where this PoC earns its keep. Four things would not have survived contact with an ordinary exploratory workflow, and each was caught only because of the pre-registration discipline.

The whitening leak (§2.5, Confound 1) produced an encouraging C2 result (0.0583) that was a leak artefact; it was caught before interpretation because the fitting procedure had been written down and could be questioned. The leave-one-corpus-out control (D-013) caught `persistent_homology`, a method that won on two corpora and would have been locked in had the third not been held out. The pairwise-vs-max mismatch, the style artefact, and the cross-lingual confound (Confounds 2–4) each turned a strong-looking separation into a null once the comparison was made honest — the AUC 0.952 that became 0.388 is the cleanest example of a number that a less disciplined study would have reported as a success. And the append-only log, by forbidding the deletion of superseded results, is what lets a reader see that d̂ = −0.208 was pre-committed to be reported whatever its sign. The contribution is not any one detector; it is a demonstration that a self-auditing, pre-registered apparatus can produce a *trustworthy* negative result in a domain where fluent positive results are cheap.

### 4.4 Was the purpose achieved?

**What was shown.** That geometric sparsity, as operationalised here, does not identify meaningful coverage gaps better than chance on the best-detecting corpus (d̂ = −0.208); that no detection method, embedding space, or k-formula generalises across three structurally dissimilar corpora; that temperature is inert for the answer-to-source distance in this pipeline; that "already covered" cannot be operationalised by bi- or cross-encoder similarity and requires an LLM judge; and that even aimed generation recovers specific missing content in only a minority of cases. Each of these is a real, pre-registered answer to a real question.

**What was not shown.** That the method works — no positive detection result generalised. That it fails universally either — the evidence is single-corpus for the probe and single-scale for much of the detection work, so a stronger claim than "weak proxy, negative on C1" is not supported. Nothing here bears on Level 3: no surviving statement was human-verified, so no confirmed gap was ever produced, only candidates.

**RQ1 (better than chance?)** — No; directionally worse on C1 (d̂ = −0.208, CI excludes 0). **RQ2 (does anything generalise?)** — No; the choice of method/embedding/k is irreducibly corpus- and scale-dependent (§3.1–3.3). **RQ3 (can "already covered" be operationalised?)** — Not by embedding similarity; only an LLM coverage judge passed the gate (balanced accuracy 0.933), which narrows the "geometry finds gaps" thesis to "geometry proposes regions, LLMs judge." **RQ4 (can the hole be filled?)** — Only weakly: 1/5 scope recovery under maximally favourable aiming, the one hit trivially explained.

### 4.5 Threats to validity and limitations

The following bound every claim above. **Pilot size:** the probe is n = 40 regions on one corpus; its CI is wide and its p-value was pre-committed as non-inferential. **Single corpus for generation:** the probe and Arm 2 are C1-only; C2/C3 generation performance is unmeasured. **Boilerplate-recall weakness:** the Arm 1a classifier has a known recall gap (it missed title-page fragments without keyword markers), so the 0.576 enrichment ratio is a lower-bound estimate and the manual correction to ≈ 1.15 is coarse. **Single-corpus detection targets:** several detection tests used one removal target per corpus per scale, so "document-scale is unreliable" rests on a small number of targets. **Embedding-model dependence:** all geometry is computed on `all-MiniLM-L6-v2` (384-d); a different embedding model could change the sparsity structure, and the whitening/anisotropy findings are specific to this model's geometry. **Training-data awareness:** the generator and judge models may have seen WHO/RFC/UNESCO material in pre-training, which could inflate both fabrication plausibility and judge confidence in ways this design cannot isolate. **Level-3 absence:** "authenticity" is survival through two LLM screens, not human confirmation; the whole pipeline measures a necessary, not sufficient, condition for a genuine gap.

### 4.6 Future work

Ordered from highest evidential priority to most speculative.

*Highest priority — repair or retire detection.* Because the probe was negative on the best-detecting corpus, the first question is whether the negative is robust: re-run the probe on C2 and C3 under the frozen configuration, purely as diagnostic (D-015 forbids re-selecting the method against this facit). If detection is uniformly negative, the geometric premise should be retired for this representation, not patched.

*High priority — local-density normalisation.* The distance-concentration characterisation (D-007) and the document-scale collapse (§3.2) both point at the same weakness: a global percentile is a weak signal when the local density varies. A pre-registered test of density-normalised severity (against, not selecting on, the leave-one-out facit) is the most defensible next geometric step.

*Medium priority — inter-rater control on the LLM judges.* H1 in the open-problems document remains open: both Level 1 and Level 2 are LLMs judging LLM output. A cheap second-judge inter-rater check on the existing Level-2 outputs would test whether the judges are stable or merely confident.

*Speculative — concept bridges / literature-based discovery.* The most ambitious direction — treating a gap not as an empty region but as an *unbuilt bridge* between two well-covered regions, and generating the connecting concept in the manner of Swanson's literature-based discovery — is a **conceptual, not validated** proposal. It is best pursued as a separate new project with its own pre-registration, not as a continuation of this pipeline, because it changes the object of study from a void to a missing edge. Bisociation (Koestler, 1964) supplies the theory for why such intersections should be fertile; this study validated the *theory's plausibility* only in the weak sense that the local-gap gap-type is well-defined, and demonstrated *none of its mechanism* — the intersection-as-gap idea was not operationally tested and must not be described as validated.

---

## 5. References

Aggarwal, C. C., Hinneburg, A., & Keim, D. A. (2001). On the surprising behavior of distance metrics in high dimensional space. In *Database Theory — ICDT 2001* (pp. 420–434). Springer. https://doi.org/10.1007/3-540-44503-X_27

Baddeley, A., Rubak, E., & Turner, R. (2015). *Spatial point patterns: Methodology and applications with R*. Chapman and Hall/CRC. https://doi.org/10.1201/b19708

Beyer, K., Goldstein, J., Ramakrishnan, R., & Shaft, U. (1999). When is "nearest neighbor" meaningful? In *Database Theory — ICDT'99* (pp. 217–235). Springer. https://doi.org/10.1007/3-540-49257-7_15

Breunig, M. M., Kriegel, H.-P., Ng, R. T., & Sander, J. (2000). LOF: Identifying density-based local outliers. *ACM SIGMOD Record, 29*(2), 93–104. https://doi.org/10.1145/335191.335388

Edelsbrunner, H., & Harer, J. (2010). *Computational topology: An introduction*. American Mathematical Society. https://doi.org/10.1090/mbk/069

Ethayarajh, K. (2019). How contextual are contextualized word representations? Comparing the geometry of BERT, ELMo, and GPT-2 embeddings. In *Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing (EMNLP-IJCNLP)* (pp. 55–65). Association for Computational Linguistics. https://doi.org/10.18653/v1/D19-1006

Koestler, A. (1964). *The act of creation*. Hutchinson.

Lehman, J., & Stanley, K. O. (2011). Abandoning objectives: Evolution through the search for novelty alone. *Evolutionary Computation, 19*(2), 189–223. https://doi.org/10.1162/EVCO_a_00025

Silverman, B. W. (1986). *Density estimation for statistics and data analysis*. Chapman and Hall. https://doi.org/10.1201/9781315140919

Swanson, D. R. (1986). Undiscovered public knowledge. *The Library Quarterly, 56*(2), 103–118. https://doi.org/10.1086/601720

*Note on scope of the reference list: the entries above are the standard primary sources for the geometric and information-theoretic primitives named in §2.1. They are the literature the project actually reached for in framing its methods. Reference-management metadata (exact editions/DOIs) was completed at write-up; any entry a reader cannot resolve should be treated as provisional and verified against the primary source.*

---

## 6. Appendices

### Appendix A — Decision-log extract (D-001–D-026)

One line per decision; full text in `beslutslogg.md`.

| D | Title | Status / outcome |
|---|---|---|
| D-001 | RAG cohort & geometric gap-in-coverage (Path 2, narrow PoC) | Path 2 chosen; Level 3 deferred |
| D-002 | Objective criterion for the Phase-2 inflection point | Locked: 2nd derivative > 2× median\|2nd derivative\|, else fallback |
| D-003 | Level-1 match threshold: procedure, not a number | Per-corpus anchor procedure locked |
| D-004 | k-formula: two candidates, tested by leave-one-out | RESOLVED — k becomes a per-corpus parameter (no formula generalised) |
| D-005 | Percentile threshold is a policy choice | 90th default / 95th if union > 15% |
| D-006 | Leave-one-out as mandatory external anchor | Runnable; 11/12 runs 0/10 |
| D-007 | Distance-concentration control added to Step 0.5 | C1 not strongly concentrated (CV 0.180) |
| D-008 | Corpus delivery approved; C1 accepted under target | 369 pp accepted as-is |
| D-009 | Reused iteration-1 tooling: green list, one exposed exception | Clustering step skipped for PoC |
| D-010 | θ_absens and Level-1 threshold merged into one parameter | Single calibrated parameter |
| D-011 | Graded leave-one-out: removed fraction vs rank/N | Added alongside binary facit |
| D-012 | Size-scaled top-N breakpoint sweep | Added; binary facit unchanged |
| D-013 | Method & embedding bake-off (5×3) | GENOMFÖRD; undecided (whitening leak found & fixed) |
| D-014 | Whitening robustness over six removal targets | 8/12 improved — below 10/12 bar; not robust |
| D-015 | Lock global config on worst-case criterion | void_stat + raw MiniLM + sqrt-k locked |
| D-016 | Whitening as intrinsic-property rule | RESOLVED — no rule (anisotropy/N confounded, r = +0.774) |
| D-017 | Robustness of C2/C3 temperature transitions | RESOLVED — do not survive noise; fixed fallback all corpora |
| D-018 | Second-round void-family bake-off | GENOMFÖRD; no challenger beat void_stat (worst-case 0.877) |
| D-019 | Phase-3 prep: Level-2 dry-run, Level-1 verify, pooling rule, C1 probe | FÖRSLAG; sub-steps A–C approved, D run |
| D-020 | Length normalisation for Level 1 + parse_error fix | GENOMFÖRD; parse_error solved, Level 1 still degenerate |
| D-021 | Recalibrate Level-1 threshold on claim-vs-chunk anchors | Separation gate borderline (AUC 0.728) |
| D-022 | Swap bi-encoder for cross-encoder/reranker | Gate not passed (AUC 0.579) |
| D-023 | Level 1 becomes an LLM coverage judge | GATE PASSED (balanced acc 0.933) |
| D-024 | Cross-lingual confound: switch to English, re-examine | GENOMFÖRD; style-matched AUC 0.388 — bi/cross-encoder excluded |
| D-025 | Parallelise probe run (no design change) | FÖRSLAG; completeness gate 40 regions |
| D-026 | Association test: detection (geometry) vs filling (aiming) | GENOMFÖRD; inconclusive vs 3 branches — both steps weak |

### Appendix B — Prompts (verbatim)

**B.1 Generation prompt — Level 0→ statement (`rag_runner.PROMPT_TEMPLATE`).**

```
You are a domain expert reading excerpts from a corpus of documents.

DOMAIN CONTEXT:
{domain_context}

EXCERPTS FROM THE CORPUS (nearby, but NOT identical, source chunks):
{source_excerpts}

TASK: Based ONLY on the excerpts above, formulate ONE specific, concrete
coverage gap — a topic, a population, or an intersection between the
excerpts that the corpus does NOT appear to address. Be specific and
concrete (name a population/setting/intervention where possible). Avoid
generic platitudes or simply summarizing the excerpts. Answer in 2-4
sentences, nothing else.
```

**B.2 Level-1 coverage judge (D-023).** The judge is an LLM given the claim plus the top-*k* cosine-retrieved chunks (±2-chunk source window excluded), at temperature 0, `top_k = 30`. Per the D-023 log, the coverage-judge prompt was sharpened to an explicit three-step instruction: *(1) identify X (the specific thing the claim says is absent); (2) search positively for X in the supplied excerpts — do NOT perform entailment against the absence-statement; (3) cite the excerpt number if X is covered.* Output: `covered` / `not_covered` + confidence (0–1) + rationale. *Note: the verbatim `COVERAGE_JUDGE_PROMPT_TEMPLATE` string is not present in the current code snapshot (`gap_verification.py` in this checkout contains the superseded bi-encoder calibration); the specification above is quoted from the D-023 decision-log entry and should be treated as provisional pending the code file.*

**B.3 Level-2 triviality judge (`domain_adapter`).** Prompt/few-shot only, never fine-tuned. Each corpus supplies a `DOMAIN_CONTEXT` and five calibration examples spanning the mandatory *mellanmjölk* (mechanical-merge) failure mode plus four H2 modes (generic platitude, overconfident-but-content-free, widely-known industry knowledge, and one non-trivial contrast). Verbatim C1 mandatory *mellanmjölk* example:

```
scenario:  "The corpus does not address how tapering of sedentary behaviour
            should be sequenced relative to infection-control isolation periods
            for patients recovering from healthcare-associated infections."
label:     trivial
rationale: "Mechanical merge of 'physical activity' and 'infection control' into
            an intersection without a concrete, checkable claim about WHAT is
            missing ... Has exactly the same geometric signature (short distance
            to the chunks' centroid) as a genuinely successful interpolation —
            which is why geometry alone cannot resolve this case."
```

Verbatim C1 non-trivial contrast example:

```
scenario:  "mhGAP names people who inject drugs as a specific population in its
            substance-use module, but neither mhGAP nor the IPC guideline
            addresses harm reduction/injection safety for this population OUTSIDE
            formal healthcare facilities — unlike the IPC guideline's injection
            safety content, which IS limited to the healthcare setting."
label:     non-trivial
rationale: "Names a specific population, a specific setting, and a specific
            content gap that can be checked against the corpus's actual content
            ... A candidate for Level 3 (human judgment), not a confirmed gap."
```

*Note: the top-level `classify_scenario` instruction wrapper (the text framing these few-shot examples) is likewise not present verbatim in the current code snapshot; the calibration examples above are reproduced verbatim from `analysis/domain_adapter.py`.*

**B.4 Arm-2 aiming prompts (`d026_arms`).** The bridging (generation) prompt and the scope-recovery judge used in the D-026 Arm-2 test are present verbatim in `analysis/d026_arms.py`. The scope-recovery judge instructs the model, in order, to (1) identify the specific scope of the actually-removed content, (2) check whether the generated bridging text recovers that *specific* scope rather than merely the broad topic, and (3) label `scope_recovered` / `topic_only` / `not_recovered`, responding in JSON with a confidence and a rationale.

### Appendix C — Full result tables

**C.1 Graded leave-one-out rank/N (D-011, `*_graded_loo.json`).** Raw MiniLM; 0 = most gap-like.

| Corpus | Removal (size) | k_log rank/N | k_sqrt rank/N |
|---|---|---|---|
| C1 | section, mhGAP SUI single (n=4) | 0.2995 | 0.2934 |
| C1 | section, SUI half (n=17) | 0.0602 | 0.0527 |
| C1 | section, SUI whole (n=33) | 0.0595 | 0.0537 |
| C1 | document, mhGAP (n=850) | 0.8698 | 0.8593 |
| C2 | section, RFC6797 §14.5 (n=7) | 0.2301 | 0.2223 |
| C2 | section, §14.1–14.4 (n=21) | 0.1939 | 0.2841 |
| C2 | section, §14 whole (n=42) | 0.5473 | 0.4341 |
| C2 | document, RFC9112 (n=286) | 0.0106 | 0.0147 |
| C3 | section, Ch.9 tightest (n=15) | 0.3799 | 0.4641 |
| C3 | section, Ch.9 half (n=96) | 0.3343 | 0.4349 |
| C3 | section, Ch.9 whole (n=192) | 0.3188 | 0.3589 |
| C3 | document, Reimagining (n=1473) | 0.7740 | 0.7214 |

**C.2 D-013 contaminated vs corrected best combination.**

| Corpus | Contaminated best rank/N | Corrected best rank/N |
|---|---|---|
| C1 | 0.0079 | 0.0172 |
| C2 | 0.0583 (whitened) | 0.0996 (raw MiniLM — whitening collapsed to 0.298) |
| C3 | 0.0109 | 0.0071 |

**C.3 Probe per-region authenticity (D-026, `d019_region_authenticity.json`).** 20 sparse + 20 random; d̂ = −0.208, 95% CI [−0.387, −0.029], p = 0.024.

| Cohort | Mean | Anthropic (haiku) | OpenAI (gpt-4o-mini) |
|---|---|---|---|
| Sparse | 0.375 | 0.600 | 0.150 |
| Random | 0.583 | 0.833 | 0.333 |

**C.4 D-026 arm summary.**

| Arm | Measure | Value |
|---|---|---|
| 1a | corpus baseline boilerplate rate | 0.0868 (8.7%) |
| 1a | sparse top-20 boilerplate rate | 0.050 (5.0%) |
| 1a | enrichment ratio | 0.576 (wrong direction; ≈1.15 after manual correction) |
| 1b | known sections best_rank_fraction (mean / median) | 0.260 / 0.151 |
| 1b | random control (mean / median) | 0.318 / 0.248 |
| 1b | Mann-Whitney (real < random), n=38 | p = 0.182 (n.s.) |
| 2 | scope_recovered / topic_only / not_recovered | 1 / 1 / 3 (of 5) |
| 2 | highest centroid similarity (Methods, not recovered) | 0.608 |

*End of report.*
