"""Pilot- (Fas 1/2) och produktionsfas (Fas 3) RAG-orkestrering.

Fas 1 (pilotsvep): för ett litet, i förväg avsatt sub-urval av gap-regioner,
generera ett lucka-scenario vid varje temperatur i PHASE1_TEMPERATURE_SWEEP,
med BÅDA generatormodellerna (Vincents val: jämförelse sida vid sida). Mät
svar↔käll-avstånd (embedding-avstånd mellan genererat scenario och regionens
källchunkar, via den lokala D-009-embeddern — ingen extra API-kostnad för
mätningen, bara för genereringen).

Kostar riktiga LLM-anrop. Körs inte utan att användaren uttryckligen bett om
det (kickoff-instruktionen, bekräftat av Vincent inför detta steg).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np
from sklearn.neighbors import BallTree

import config
from analysis.diversity import _l2_normalize
from analysis.gap_detection import compute_gaps, _k_candidates


PROMPT_TEMPLATE = """Du är en domänexpert som läser utdrag ur en klinisk WHO-riktlinjekorpus.

DOMÄNKONTEXT:
{domain_context}

UTDRAG UR KORPUSEN (närliggande, men INTE identiska, källchunkar):
{source_excerpts}

UPPGIFT: Baserat ENDAST på utdragen ovan, formulera EN specifik, konkret
täckningslucka — ett ämne, en population, eller en skärningspunkt mellan
utdragen som korpusen INTE verkar adressera. Var specifik och konkret (namnge
population/miljö/åtgärd om möjligt). Undvik generiska floskler eller att bara
sammanfatta utdragen. Svara med 2-4 meningar, inget annat."""


@dataclass
class PilotObservation:
    region_chunk_index: int
    model_provider: str
    model_name: str
    temperature: float
    generated_text: str
    answer_source_distance: float


def select_pilot_regions(
    records: list,
    embeddings: np.ndarray,
    n_regions: int = config.PHASE1_PILOT_N_REGIONS,
    k_candidate: str = "log",
    seed: int = config.PHASE1_PILOT_SEED,
) -> list[int]:
    """Drar n_regions gap-flaggade regioner (union av lokalt+centroid-gap),
    seedat för reproducerbarhet. Dessa index sparas separat och undantas ur
    Fas 3:s produktionsurval (disjunkthetskravet, v3 Del B)."""
    result = compute_gaps(embeddings, k_candidate=k_candidate)
    gap_indices = [r.chunk_index for r in result.regions if r.is_local_gap or r.is_centroid_gap]
    rng = np.random.default_rng(seed)
    chosen = rng.choice(gap_indices, size=min(n_regions, len(gap_indices)), replace=False)
    return sorted(int(i) for i in chosen)


def _source_context(records: list, embeddings: np.ndarray, region_idx: int, k: int) -> list[int]:
    """De k närmaste grannarna (embedding-mässigt) till en gap-region — de
    'kringliggande men inte identiska' källchunkarna som utgör kontext."""
    normalized = _l2_normalize(embeddings)
    tree = BallTree(normalized)
    _, neighbor_idx = tree.query(normalized[region_idx : region_idx + 1], k=k + 1)
    return [int(i) for i in neighbor_idx[0] if i != region_idx][:k]


def _generate_anthropic(client, model: str, prompt: str, temperature: float, max_tokens: int) -> str:
    resp = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text.strip()


def _generate_openai(client, model: str, prompt: str, temperature: float, max_tokens: int) -> str:
    resp = client.chat.completions.create(
        model=model,
        max_completion_tokens=max_tokens,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content.strip()


def run_phase1_pilot(
    records: list,
    embeddings: np.ndarray,
    domain_context: str,
    pilot_region_indices: list[int],
    embedder,
    anthropic_client,
    openai_client,
    temperatures: tuple[float, ...] = config.PHASE1_TEMPERATURE_SWEEP,
    k_context: int = 4,
) -> list[PilotObservation]:
    normalized = _l2_normalize(embeddings)
    observations: list[PilotObservation] = []

    for region_idx in pilot_region_indices:
        context_idx = _source_context(records, embeddings, region_idx, k_context)
        source_excerpts = "\n\n".join(
            f"[{j+1}] {records[i].text}" for j, i in enumerate(context_idx)
        )
        prompt = PROMPT_TEMPLATE.format(
            domain_context=domain_context, source_excerpts=source_excerpts
        )
        source_centroid = normalized[context_idx].mean(axis=0, keepdims=True)
        source_centroid = source_centroid / np.linalg.norm(source_centroid)

        for temperature in temperatures:
            for provider, model in config.PHASE1_GENERATOR_MODELS.items():
                if provider == "anthropic":
                    text = _generate_anthropic(
                        anthropic_client, model, prompt, temperature, config.PHASE1_MAX_TOKENS
                    )
                else:
                    text = _generate_openai(
                        openai_client, model, prompt, temperature, config.PHASE1_MAX_TOKENS
                    )

                gen_emb = _l2_normalize(embedder.embed([text]))
                distance = float(np.linalg.norm(gen_emb[0] - source_centroid[0]))

                observations.append(
                    PilotObservation(
                        region_chunk_index=region_idx,
                        model_provider=provider,
                        model_name=model,
                        temperature=temperature,
                        generated_text=text,
                        answer_source_distance=distance,
                    )
                )

    return observations


def save_pilot_observations(observations: list[PilotObservation], path: str | Path) -> None:
    path = Path(path)
    path.write_text(
        json.dumps([asdict(o) for o in observations], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
