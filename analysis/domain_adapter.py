"""Nivå 2: trivialitetsdomare (domänadapter). Prompt-/few-shot ENDAST — ingen
fine-tuning (D-001 Lager 1). Detta steg (0.5.6) skriver bara kalibreringsexemplen;
själva LLM-anropande domar-logiken byggs vid Fas 1/Steg 0.5.8 (kräver API-nycklar).

Obligatoriskt: minst ett mellanmjölks-exempel (D-001 Lager 1, A3 i
rag_kohort_preregistrering_v3.md), märkt trivial:ja oavsett geometriskt avstånd.

Utökat utöver minimikravet, för att adressera H2 (negative_space_open_problems_v1_0.md
— "endast ETT obligatoriskt kalibreringsexempel täcker sannolikt inte alla failure
modes"): tre YTTERLIGARE distinkta trivial-typer, namngivna explicit i H2:s text
("generisk floskel utan mellanmjölks-geometri", "överdrivet självsäkert men
innehållslöst påstående", "korrekt-låtande men i själva verket allmänt känd
branschkunskap"). Detta är ett tillägg beslutat INNAN någon agent genererat
något för denna korpus — inte en efterhandsjustering baserad på observerade
domar-fel.

D-024: allt scenario-/rationale-/domänkontext-innehåll nedan är på ENGELSKA
(bytt från svenska) — svensk genererad text jämförd mot engelsk korpus var en
bevisad cross-lingual confound (all-MiniLM-L6-v2 är inte flerspråkig; engelska
gav +0,24-0,30 similaritet och rätt dokument i spot-checkar, svenska fel
dokument i 2/3 fall). label-värdena är nu "trivial"/"non-trivial" (tidigare
"trivial"/"icke-trivial") för intern konsekvens.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CalibrationExample:
    failure_mode: str
    scenario: str
    label: str  # "trivial" | "non-trivial"
    rationale: str


DOMAIN_CONTEXT_C1_CLINICAL = (
    "Corpus 1 consists of three WHO guidelines: (1) Infection Prevention and Control "
    "Programmes (infection control at national/facility level), (2) Guidelines "
    "on Physical Activity and Sedentary Behaviour, (3) mhGAP Intervention Guide "
    "(mental health, neurological conditions, substance use). A proposed "
    "gap scenario should be judged against what these three documents ACTUALLY cover or "
    "do not cover — not against general clinical knowledge at large."
)


CALIBRATION_EXAMPLES_C1_CLINICAL: list[CalibrationExample] = [
    CalibrationExample(
        failure_mode="mellanmjölk / mechanical merge (mandatory, D-001 Lager 1 / A3)",
        scenario=(
            "The corpus does not address how tapering of sedentary behaviour should be "
            "sequenced relative to infection-control isolation periods for patients "
            "recovering from healthcare-associated infections."
        ),
        label="trivial",
        rationale=(
            "Mechanical merge of 'physical activity' and 'infection control' into an "
            "intersection without a concrete, checkable claim about WHAT is missing "
            "(no named population, no specific protocol element). Has exactly the same "
            "geometric signature (short distance to the chunks' centroid) as a "
            "genuinely successful interpolation — which is why geometry alone cannot "
            "resolve this case."
        ),
    ),
    CalibrationExample(
        failure_mode="generic platitude without mellanmjölk geometry (H2)",
        scenario=(
            "There could be more guidance on how healthcare systems can better "
            "integrate different types of preventive care with each other."
        ),
        label="trivial",
        rationale=(
            "Could be said about virtually any healthcare corpus. Not grounded in the "
            "actual retrieved chunks, no named population, setting, or intervention. No "
            "claim that can be verified as present or absent in THIS specific corpus."
        ),
    ),
    CalibrationExample(
        failure_mode="overconfident but content-free claim (H2)",
        scenario=(
            "The corpus fails to establish the definitive threshold at which "
            "sedentary time becomes clinically irreversible for cardiovascular risk, "
            "despite this being a critical, unaddressed gap in the literature."
        ),
        label="trivial",
        rationale=(
            "Sounds authoritative and specific ('definitive threshold', 'clinically "
            "irreversible') but the concept itself is not operationalized or "
            "checkable against anything that could actually appear in a WHO "
            "guideline. Confident tone substitutes for substance."
        ),
    ),
    CalibrationExample(
        failure_mode="correct-sounding but widely known industry knowledge (H2)",
        scenario=(
            "The corpus does not explicitly state that untreated depression can "
            "co-occur with substance use disorder."
        ),
        label="trivial",
        rationale=(
            "Extremely well-established, widely known clinical knowledge — and "
            "moreover indirectly covered by mhGAP's comorbidity guidance. Likely a "
            "Level 1 search-miss (phrasing-dependent), not a genuine blind spot. "
            "Shows why Level 1 must run BEFORE Level 2, and why 'sounds correct' "
            "claims require extra scrutiny rather than automatic approval."
        ),
    ),
    CalibrationExample(
        failure_mode="contrast example: non-trivial (for judge calibration, not a requirement in itself)",
        scenario=(
            "mhGAP names people who inject drugs as a specific population in its "
            "substance-use module, but neither mhGAP nor the IPC guideline addresses "
            "harm reduction/injection safety for this population OUTSIDE formal "
            "healthcare facilities — unlike the IPC guideline's injection safety "
            "content, which IS limited to the healthcare setting."
        ),
        label="non-trivial",
        rationale=(
            "Names a specific population, a specific setting, and a specific content "
            "gap that can be checked against the corpus's actual content — not a "
            "mechanical merge, but a concrete, verifiable boundary claim. A candidate "
            "for Level 3 (human judgment), not a confirmed gap in itself."
        ),
    ),
]


DOMAIN_CONTEXT_C2_TELECOM = (
    "Corpus 2 consists of 16 IETF RFCs in three clusters: (A) Network security — DNSSEC "
    "(RFC 4033/4034), TLS extensions (RFC 6066), HTTP cookies (RFC 6265), HSTS (RFC 6797), "
    "OCSP (RFC 6960), JWT (RFC 7519); (B) Core protocol design — HTTP/1.1 (RFC 9112), "
    "Atom (RFC 4287); (C) Internet infrastructure — DHCP (RFC 2131), RIPv2 (RFC 2453), "
    "IPv4 link-local (RFC 3927), IPv6 addressing (RFC 4291/8200), SLAAC (RFC 4862), "
    "syslog (RFC 5424). The text is dense, normative protocol specification — not "
    "narrative prose. A proposed gap scenario should be judged against what THESE "
    "SPECIFIC RFCs actually specify, not against general networking knowledge at large."
)


CALIBRATION_EXAMPLES_C2_TELECOM: list[CalibrationExample] = [
    CalibrationExample(
        failure_mode="mellanmjölk / mechanical merge (mandatory, D-001 Lager 1 / A3)",
        scenario=(
            "The corpus does not address how DNSSEC validation failures should be "
            "communicated to the client via HSTS-like policy mechanisms."
        ),
        label="trivial",
        rationale=(
            "Mechanical merge of 'DNSSEC' (RFC 4033/4034) and 'HSTS' (RFC 6797) into "
            "an intersection without a concrete, checkable claim about WHICH specific "
            "mechanism or message format is missing. Same geometric signature as a "
            "genuinely grounded interpolation between the two RFC clusters."
        ),
    ),
    CalibrationExample(
        failure_mode="generic platitude without mellanmjölk geometry (H2)",
        scenario=(
            "There could be more guidance on how different internet protocols can "
            "interoperate more securely."
        ),
        label="trivial",
        rationale=(
            "Could be said about virtually any protocol corpus. Names no specific "
            "RFC pair, no specific mechanism or failure mode. No checkable claim "
            "against THIS corpus."
        ),
    ),
    CalibrationExample(
        failure_mode="overconfident but content-free claim (H2)",
        scenario=(
            "The corpus fails to specify the exact byte-level threshold at which a "
            "DHCP lease renewal becomes definitively unrecoverable, despite this "
            "being a critical, unaddressed gap."
        ),
        label="trivial",
        rationale=(
            "Sounds technically precise ('exact byte-level threshold') but the "
            "concept is not something RFC 2131 would actually specify, nor even a "
            "meaningful technical concept in a DHCP context. Confident technical "
            "jargon substitutes for substance."
        ),
    ),
    CalibrationExample(
        failure_mode="correct-sounding but widely known industry knowledge (H2)",
        scenario="The corpus does not explicitly state that IPv6 addresses are 128 bits long.",
        label="trivial",
        rationale=(
            "Extremely well-established knowledge — and moreover EXPLICITLY "
            "specified in both RFC 4291 and RFC 8200. This is a Level 1 search-miss "
            "(phrasing-dependent), not a genuine gap. Shows why Level 1 must run "
            "before Level 2 even in a tightly specified, technical corpus."
        ),
    ),
    CalibrationExample(
        failure_mode="contrast example: non-trivial (for judge calibration, not a requirement in itself)",
        scenario=(
            "RFC 6797 (HSTS) specifies how a client must force HTTPS upgrade, and "
            "RFC 6960 (OCSP) specifies how certificate revocation is checked, but no "
            "RFC in the corpus addresses what a client should do when an "
            "HSTS-enforced connection's OCSP check fails DURING a DHCP-assigned "
            "network handoff (RFC 2131) — e.g. when switching to a captive portal "
            "network."
        ),
        label="non-trivial",
        rationale=(
            "Names three specific RFCs and a concrete, verifiable intersection "
            "between their respective error-handling mechanisms — not a mechanical "
            "merge, but a precise boundary claim that can be checked against the "
            "corpus's actual content. A candidate for Level 3."
        ),
    ),
]


DOMAIN_CONTEXT_C3_EDUCATION = (
    "Corpus 3 consists of three UNESCO reports: (1) Global Education Monitoring Report "
    "2020 — Inclusion and education: All means all; (2) Reimagining our futures "
    "together (2021) — A new social contract for education; (3) Global Education "
    "Monitoring Report 2023 — Technology in education: A tool on whose terms? Narrative "
    "policy-report prose, not clinical directive text or technical protocol "
    "specification. A proposed gap scenario should be judged against what THESE THREE "
    "reports actually discuss, not against general education-policy debate at large."
)


CALIBRATION_EXAMPLES_C3_EDUCATION: list[CalibrationExample] = [
    CalibrationExample(
        failure_mode="mellanmjölk / mechanical merge (mandatory, D-001 Lager 1 / A3)",
        scenario=(
            "The corpus does not address how a new social contract for education "
            "should guarantee the inclusion of students with disabilities as schools "
            "rapidly digitize their teaching."
        ),
        label="trivial",
        rationale=(
            "Mechanical merge of 'inclusion' (GEM 2020) and 'technology in "
            "education' (GEM 2023) into an intersection without a concrete, "
            "checkable claim about WHICH specific accommodation, population, or "
            "technology is missing. Same geometric signature as a genuinely "
            "grounded interpolation between the two reports' themes."
        ),
    ),
    CalibrationExample(
        failure_mode="generic platitude without mellanmjölk geometry (H2)",
        scenario=(
            "There could be more discussion of how education systems worldwide can "
            "better meet all students' needs."
        ),
        label="trivial",
        rationale=(
            "Could be said about virtually any education-policy corpus. Names no "
            "specific report, population, region, or mechanism. No checkable claim "
            "against THIS corpus."
        ),
    ),
    CalibrationExample(
        failure_mode="overconfident but content-free claim (H2)",
        scenario=(
            "The corpus fails to establish the exact percentage of digital "
            "instruction time at which students' social development becomes "
            "irreversibly harmed, despite this being a critical, unaddressed gap."
        ),
        label="trivial",
        rationale=(
            "Sounds precise ('exact percentage', 'irreversibly harmed') but the "
            "concept is not something GEM 2023 or any of the other reports would "
            "formulate or measure that way. Confident tone substitutes for "
            "substance."
        ),
    ),
    CalibrationExample(
        failure_mode="correct-sounding but widely known industry knowledge (H2)",
        scenario=(
            "The corpus does not explicitly state that access to education differs "
            "between high-income and low-income countries."
        ),
        label="trivial",
        rationale=(
            "Extremely well-established knowledge that likely permeates all three "
            "reports (the GEM reports explicitly build on such income-stratified "
            "statistics). A Level 1 search-miss (phrasing-dependent), not a genuine "
            "gap."
        ),
    ),
    CalibrationExample(
        failure_mode="contrast example: non-trivial (for judge calibration, not a requirement in itself)",
        scenario=(
            "'Reimagining our futures together' (2021) proposes a new 'social "
            "contract' built on increased pedagogical collaboration among teachers, "
            "while GEM 2023 documents how EdTech procurement often happens without "
            "teacher input ('a tool on whose terms?') — but neither report "
            "concretely addresses how teachers' voice would be formally included in "
            "EdTech procurement processes specifically, the specific mechanism where "
            "the two reports' respective arguments meet."
        ),
        label="non-trivial",
        rationale=(
            "Names two specific reports and a concrete, verifiable intersection "
            "between their respective lines of argument — not a mechanical merge, "
            "but a precise, checkable claim about what neither report covers. A "
            "candidate for Level 3."
        ),
    ),
]


# ---------------------------------------------------------------------------
# D-019 delsteg A: UTELÄMNADE testfall (ej i domarens few-shot-prompt).
# Nya instanser av samma fem failure modes som CALIBRATION_EXAMPLES_C{1,2,3}
# ovan, men olika sakinnehåll — testar generalisering, inte återgivning av
# prompten. "label" här är FACIT (vad domaren BORDE svara), inte en del av
# prompten den ser.
# ---------------------------------------------------------------------------

HELD_OUT_EXAMPLES_C1_CLINICAL: list[CalibrationExample] = [
    CalibrationExample(
        failure_mode="mellanmjölk / mechanical merge (held out)",
        scenario=(
            "The corpus does not address how infection-control routines should be "
            "adapted for patients with concurrent mental health conditions per "
            "mhGAP's guidelines."
        ),
        label="trivial",
        rationale=(
            "Mechanical merge of 'infection control' and 'mhGAP/mental health' "
            "without a concrete, checkable claim about which specific routine or "
            "population is missing."
        ),
    ),
    CalibrationExample(
        failure_mode="generic platitude (held out)",
        scenario=(
            "There could be more guidelines on how different age groups are "
            "affected by health interventions."
        ),
        label="trivial",
        rationale="Generic, no named topic, no specific population or mechanism.",
    ),
    CalibrationExample(
        failure_mode="overconfident claim (held out)",
        scenario=(
            "The corpus fails to specify the exact number of daily steps at which "
            "sedentary behaviour becomes irreversibly dangerous for children under "
            "5, despite this being a critical unaddressed gap."
        ),
        label="trivial",
        rationale="Sounds precise but is not a real, measurable concept in the source material.",
    ),
    CalibrationExample(
        failure_mode="widely known industry knowledge (held out)",
        scenario=(
            "The corpus does not explicitly state that regular physical activity "
            "reduces the risk of cardiovascular disease."
        ),
        label="trivial",
        rationale="Extremely well-established knowledge, likely a Level 1 search-miss.",
    ),
    CalibrationExample(
        failure_mode="contrast example: non-trivial (held out)",
        scenario=(
            "mhGAP's substance-use module names elevated overdose risk in people who "
            "have recently completed treatment (reduced tolerance), but the IPC "
            "guideline's injection-safety protocol does not address this specific "
            "high-risk group upon re-entering care after relapse."
        ),
        label="non-trivial",
        rationale=(
            "Names a specific population, a specific clinical phenomenon, and a "
            "concrete intersection between two named documents."
        ),
    ),
]

HELD_OUT_EXAMPLES_C2_TELECOM: list[CalibrationExample] = [
    CalibrationExample(
        failure_mode="mellanmjölk / mechanical merge (held out)",
        scenario=(
            "The corpus does not address how IPv6 addresses should be logged in "
            "syslog messages during network failures."
        ),
        label="trivial",
        rationale="Mechanical merge of RFC 8200/4291 and RFC 5424 without a specific field format.",
    ),
    CalibrationExample(
        failure_mode="generic platitude (held out)",
        scenario="There could be more guidance on how protocols can be implemented more securely in practice.",
        label="trivial",
        rationale="Generic, no specific RFC pair or mechanism named.",
    ),
    CalibrationExample(
        failure_mode="overconfident claim (held out)",
        scenario=(
            "The corpus fails to specify the exact millisecond threshold at which a "
            "RIPv2 update becomes definitively stale, despite this being a critical "
            "unaddressed gap."
        ),
        label="trivial",
        rationale="Sounds technically precise but is not a concept RFC 2453 actually specifies that way.",
    ),
    CalibrationExample(
        failure_mode="widely known industry knowledge (held out)",
        scenario="The corpus does not explicitly state that HTTP is an application-layer protocol.",
        label="trivial",
        rationale="Extremely well-established, and moreover explicit in RFC 9112.",
    ),
    CalibrationExample(
        failure_mode="contrast example: non-trivial (held out)",
        scenario=(
            "RFC 4862 (SLAAC) specifies duplicate address detection for IPv6, and "
            "RFC 2131 (DHCP) specifies lease-conflict handling for IPv4, but no RFC "
            "in the corpus addresses how a dual-stack client should handle "
            "simultaneous address conflicts when switching between SLAAC and DHCP on "
            "the same network connection."
        ),
        label="non-trivial",
        rationale="Names two specific RFCs and a precise, verifiable intersection.",
    ),
]

HELD_OUT_EXAMPLES_C3_EDUCATION: list[CalibrationExample] = [
    CalibrationExample(
        failure_mode="mellanmjölk / mechanical merge (held out)",
        scenario=(
            "The corpus does not address how a new social contract for education "
            "should guarantee inclusion of students with disabilities."
        ),
        label="trivial",
        rationale="Mechanical merge of 'Reimagining' and GEM 2020 without a specific mechanism.",
    ),
    CalibrationExample(
        failure_mode="generic platitude (held out)",
        scenario="There could be more discussion of how teachers can become better at teaching diverse students.",
        label="trivial",
        rationale="Generic, no specific report, population, or mechanism.",
    ),
    CalibrationExample(
        failure_mode="overconfident claim (held out)",
        scenario=(
            "The corpus fails to establish the exact age at which classroom "
            "technology use becomes pedagogically counterproductive, despite this "
            "being a critical unaddressed gap."
        ),
        label="trivial",
        rationale="Sounds precise but is not a concept GEM 2023 would formulate that way.",
    ),
    CalibrationExample(
        failure_mode="widely known industry knowledge (held out)",
        scenario="The corpus does not explicitly state that girls in some regions have lower school attendance than boys.",
        label="trivial",
        rationale="Well-established knowledge the GEM reports explicitly build on.",
    ),
    CalibrationExample(
        failure_mode="contrast example: non-trivial (held out)",
        scenario=(
            "GEM 2020 documents barriers for students with disabilities in "
            "traditional instruction, and GEM 2023 documents how adaptive EdTech can "
            "tailor instruction, but neither report concretely addresses what data-"
            "privacy requirements apply when adaptive EdTech collects sensitive data "
            "about students' disabilities."
        ),
        label="non-trivial",
        rationale="Names two specific reports and a precise, verifiable intersection.",
    ),
]


# ---------------------------------------------------------------------------
# D-019 delsteg A: Nivå 2-domarens LLM-anropande logik. Prompt-/few-shot
# ENDAST (D-001 Lager 1) — kalibreringsexemplen skickas som demonstrationer i
# prompten, ingen fine-tuning.
# ---------------------------------------------------------------------------

JUDGE_PROMPT_TEMPLATE = """You are a triviality judge for a research project on \
geometric gap detection in document corpora.

DOMAIN CONTEXT:
{domain_context}

Your task: assess whether a PROPOSED GAP SCENARIO is TRIVIAL (a platitude, a mechanical \
merge of themes without substance, a confident but content-free claim, or widely known \
knowledge) or NON-TRIVIAL (a specific, concrete, verifiable claim about what the corpus \
actually lacks).

CALIBRATION EXAMPLES:
{calibration_block}

Respond ONLY with valid JSON in this form:
{{"label": "trivial" or "non-trivial", "rationale": "1-2 sentence justification"}}

SCENARIO TO ASSESS:
{scenario}"""


def _format_calibration_block(examples: list[CalibrationExample]) -> str:
    parts = []
    for i, ex in enumerate(examples, 1):
        parts.append(
            f"{i}. Scenario: \"{ex.scenario}\"\n"
            f"   Label: {ex.label}\n"
            f"   Rationale: {ex.rationale}"
        )
    return "\n\n".join(parts)


def classify_scenario(
    anthropic_client,
    model: str,
    domain_context: str,
    calibration_examples: list[CalibrationExample],
    scenario: str,
    max_tokens: int = 500,
) -> dict:
    """Kör Nivå 2-domaren på ETT scenario. Returnerar {"label": ..., "rationale": ...}.
    Vid ett svar som inte går att tolka som JSON: label="parse_error".

    D-020: max_tokens höjt från 200 till 500 — 200 klippte domarens fulla
    resonemang mitt i rationale-fältet i 25% av fallen (ogiltig JSON), ren
    implementationsbugg, inget metodval."""
    import json
    import re

    prompt = JUDGE_PROMPT_TEMPLATE.format(
        domain_context=domain_context,
        calibration_block=_format_calibration_block(calibration_examples),
        scenario=scenario,
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
        return {"label": "parse_error", "rationale": text}
    try:
        parsed = json.loads(match.group(0))
    except json.JSONDecodeError:
        return {"label": "parse_error", "rationale": text}
    return {
        "label": parsed.get("label", "parse_error"),
        "rationale": parsed.get("rationale", ""),
    }
