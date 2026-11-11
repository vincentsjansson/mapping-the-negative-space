# Mapping the Negative Space

Geometric gap detection in embedding space: finding what a document corpus **does not** cover.

**Author:** Vincent Jansson · Lund University
**Status:** Research PoC, Phase 3 preparation (decisions D-001–D-025 in [`beslutslogg.md`](beslutslogg.md))

Iteration 2 of a research programme. Its predecessor,
[Embracing the Novelty of Noise](https://github.com/vincentsjansson/Novelty_of_noise), was
deliberately kept in a separate repo, and only the tooling whitelisted in D-009 is reused.

---

## The question

Given an arbitrary corpus (risk frameworks, clinical guidelines, protocol standards),
can we locate its **coverage gaps**, the regions of meaning that the documents never
substantively address, in a way that is:

- **corpus-agnostic**: one configuration has to work across structurally different domains,
- **pre-registered**: thresholds and formulas are locked *before* results are seen,
- **verifiable**: every candidate gap is checked by an independent judge?

## Pipeline

```
corpus ──► chunk (400/50) ──► embed (all-MiniLM-L6-v2, 384-d, L2-norm)
       ──► gap detection (void_stat; k from two pre-registered candidates,
           round(0.5·ln N) vs round(0.5·√N), clipped to [3,10], current default √)
       ──► percentile threshold (90th / 95th, an explicit policy choice)
       ──► RAG cohort generates claims for each gap region
       ──► Level 1: LLM coverage judge  (is it really absent from the corpus?)
       ──► Level 2: authenticity judge   (is it a real, non-trivial gap?)
```

## Corpora (D-008)

| Corpus | Domain | Source | Licence |
|---|---|---|---|
| C0 | Business continuity / ERM | Iteration 1 fallback | — |
| C1 | Clinical guidelines | WHO (3 guidelines, 369 pp.) | CC BY-NC-SA 3.0 IGO |
| C2 | Telecom protocols | 16 IETF RFCs | IETF Trust / BCP 78 |
| C3 | Education policy | UNESCO (3 reports, 1 255 pp.) | CC BY-SA 3.0 IGO |

Source files are kept local and only the manifests are versioned
(see [`corpora/`](corpora/)).

## Methodological safeguards

- **Leave-one-out as external anchor (D-006, D-011, D-012):** known content is removed
  and we check whether the detector rediscovers it as a gap, swept over removal size.
- **Distance-concentration check (D-007):** guards against high-dimensional distance collapse.
- **Method and embedding bake-off (D-013–D-018):** whitening vs. raw space and several
  void-family methods, with the global config locked on a worst-case criterion.
- **Confounds found and fixed:** style mismatch in calibration anchors, threshold
  mis-calibration, and a cross-lingual confound (Swedish generation against an English
  corpus, D-024). Contaminated steps were re-run.
- **Level 1 judge validated:** escalated from bi-encoder (AUC 0.73) to cross-encoder
  (AUC 0.58) to an LLM coverage judge, which reached a balanced accuracy of 0.93 with zero
  false positives on style-matched anchors (D-021–D-023).

## Repository layout

```
analysis/     gap detection, verification, leave-one-out, RAG runner, diagnostics
processing/   corpus loading and embedding
corpora/      corpus manifests and build logs (source files are not versioned)
docs/         pre-registration (v3 + v4 addendum), lessons from iteration 1, open problems
config.py     all locked parameters, with references to the decision that set each one
beslutslogg.md  append-only decision log (Swedish)
```

## Setup

```bash
pip install -r requirements.txt
# Place corpus source files under corpora/<corpus>/files/ (see each manifest)
# API keys are read from a local .env, which is git-ignored
```

Documentation is mainly in Swedish. The decision log is the primary record of the method.
