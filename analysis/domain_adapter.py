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
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CalibrationExample:
    failure_mode: str
    scenario: str
    label: str  # "trivial" | "icke-trivial"
    rationale: str


DOMAIN_CONTEXT_C1_CLINICAL = (
    "Korpus 1 består av tre WHO-riktlinjer: (1) Infection Prevention and Control "
    "Programmes (infektionskontroll på nationell/vårdinrättningsnivå), (2) Guidelines "
    "on Physical Activity and Sedentary Behaviour, (3) mhGAP Intervention Guide "
    "(psykisk hälsa, neurologiska tillstånd, substansbruk). Ett föreslaget "
    "lucka-scenario ska bedömas mot vad dessa tre dokument FAKTISKT täcker eller "
    "inte täcker — inte mot allmän klinisk kunskap i stort."
)


CALIBRATION_EXAMPLES_C1_CLINICAL: list[CalibrationExample] = [
    CalibrationExample(
        failure_mode="mellanmjölk (obligatoriskt, D-001 Lager 1 / A3)",
        scenario=(
            "Korpusen adresserar inte hur nedtrappning av stillasittande beteende bör "
            "sekvenseras i förhållande till infektionskontrollens isoleringsperioder för "
            "patienter som återhämtar sig från vårdrelaterade infektioner."
        ),
        label="trivial",
        rationale=(
            "Mekanisk sammanslagning av 'fysisk aktivitet' och 'infektionskontroll' till "
            "en skärningspunkt utan ett konkret, kontrollerbart påstående om VAD som "
            "saknas (ingen namngiven population, inget specifikt protokollmoment). Har "
            "exakt samma geometriska signatur (kort avstånd till chunkarnas centroid) "
            "som en genuint lyckad interpolation — det är därför geometrin ensam inte "
            "kan avgöra detta fall."
        ),
    ),
    CalibrationExample(
        failure_mode="generisk floskel utan mellanmjölks-geometri (H2)",
        scenario=(
            "Det skulle kunna finnas mer vägledning om hur vårdsystem bättre kan "
            "integrera olika typer av förebyggande vård med varandra."
        ),
        label="trivial",
        rationale=(
            "Kunde sägas om praktiskt taget vilken vårdkorpus som helst. Inte förankrat "
            "i de faktiska hämtade chunkarna, ingen namngiven population, miljö eller "
            "intervention. Inget påstående som går att verifiera som närvarande eller "
            "frånvarande i just DENNA korpus."
        ),
    ),
    CalibrationExample(
        failure_mode="överdrivet självsäkert men innehållslöst påstående (H2)",
        scenario=(
            "Korpusen misslyckas med att fastställa den definitiva tröskeln vid vilken "
            "stillasittande tid blir kliniskt irreversibel för kardiovaskulär risk, "
            "trots att detta är en kritisk, oadresserad lucka i litteraturen."
        ),
        label="trivial",
        rationale=(
            "Låter auktoritativt och specifikt ('definitiv tröskel', 'kliniskt "
            "irreversibel') men begreppet självt är inte operationaliserat eller "
            "kontrollerbart mot något som faktiskt skulle kunna stå i en WHO-riktlinje. "
            "Självsäker ton ersätter substans."
        ),
    ),
    CalibrationExample(
        failure_mode="korrekt-låtande men allmänt känd branschkunskap (H2)",
        scenario=(
            "Korpusen anger inte uttryckligen att obehandlad depression kan "
            "samförekomma med substansbruksyndrom."
        ),
        label="trivial",
        rationale=(
            "Extremt väletablerad, allmänt känd klinisk kunskap — och dessutom indirekt "
            "täckt genom mhGAP:s komorbiditetsvägledning. Sannolikt ett Nivå "
            "1-sökmissförhållande (fraseringsberoende), inte en genuin blind fläck. "
            "Visar varför Nivå 1 måste köras FÖRE Nivå 2, och varför "
            "'låter-korrekt'-påståenden kräver extra granskning snarare än att "
            "automatiskt godkännas."
        ),
    ),
    CalibrationExample(
        failure_mode="kontrastexempel: icke-trivial (för domarens kalibrering, ej krav i sig)",
        scenario=(
            "mhGAP namnger personer som injicerar droger som en specifik population i "
            "sin substansbruksmodul, men vare sig mhGAP eller IPC-riktlinjen adresserar "
            "skademinimering/injektionssäkerhet för denna population UTANFÖR formella "
            "vårdinrättningar — till skillnad från IPC-riktlinjens injektionssäkerhet "
            "SOM ÄR begränsad till vårdmiljö."
        ),
        label="icke-trivial",
        rationale=(
            "Namnger en specifik population, en specifik miljö och ett specifikt "
            "innehållsgap som går att kontrollera mot korpusens faktiska innehåll — "
            "ingen mekanisk sammanslagning, utan ett konkret, verifierbart "
            "gränssnittspåstående. Kandidat för Nivå 3 (mänsklig bedömning), inte en "
            "bekräftad lucka i sig."
        ),
    ),
]


DOMAIN_CONTEXT_C2_TELECOM = (
    "Korpus 2 består av 16 IETF RFC:er i tre kluster: (A) Nätverkssäkerhet — DNSSEC "
    "(RFC 4033/4034), TLS-tillägg (RFC 6066), HTTP-cookies (RFC 6265), HSTS (RFC 6797), "
    "OCSP (RFC 6960), JWT (RFC 7519); (B) Kärnprotokolldesign — HTTP/1.1 (RFC 9112), "
    "Atom (RFC 4287); (C) Internetinfrastruktur — DHCP (RFC 2131), RIPv2 (RFC 2453), "
    "IPv4 link-local (RFC 3927), IPv6-adressering (RFC 4291/8200), SLAAC (RFC 4862), "
    "syslog (RFC 5424). Texten är tät, normativ protokollspecifikation — inte narrativ "
    "prosa. Ett föreslaget lucka-scenario ska bedömas mot vad DESSA SPECIFIKA RFC:er "
    "faktiskt specificerar, inte mot allmän nätverkskunskap i stort."
)


CALIBRATION_EXAMPLES_C2_TELECOM: list[CalibrationExample] = [
    CalibrationExample(
        failure_mode="mellanmjölk (obligatoriskt, D-001 Lager 1 / A3)",
        scenario=(
            "Korpusen adresserar inte hur DNSSEC-valideringsfel bör kommuniceras via "
            "HSTS-liknande policymekanismer till klienten."
        ),
        label="trivial",
        rationale=(
            "Mekanisk sammanslagning av 'DNSSEC' (RFC 4033/4034) och 'HSTS' (RFC 6797) "
            "till en skärningspunkt utan ett konkret, kontrollerbart påstående om VILKEN "
            "specifik mekanism eller vilket meddelandeformat som saknas. Samma "
            "geometriska signatur som en genuint grundad interpolation mellan de två "
            "RFC-klustren."
        ),
    ),
    CalibrationExample(
        failure_mode="generisk floskel utan mellanmjölks-geometri (H2)",
        scenario=(
            "Det skulle kunna finnas mer vägledning om hur olika internetprotokoll kan "
            "samverka på ett säkrare sätt."
        ),
        label="trivial",
        rationale=(
            "Kunde sägas om praktiskt taget vilken protokollkorpus som helst. Namnger "
            "inget specifikt RFC-par, ingen specifik mekanism eller felläge. Inget "
            "kontrollerbart påstående mot DENNA korpus."
        ),
    ),
    CalibrationExample(
        failure_mode="överdrivet självsäkert men innehållslöst påstående (H2)",
        scenario=(
            "Korpusen misslyckas med att specificera den exakta byte-nivå-tröskeln vid "
            "vilken DHCP-lease-förnyelse blir definitivt återställningsbar, trots att "
            "detta är en kritisk, oadresserad lucka."
        ),
        label="trivial",
        rationale=(
            "Låter tekniskt precist ('exakt byte-nivå-tröskel') men begreppet är inte "
            "något RFC 2131 faktiskt skulle specificera eller ens ett meningsfullt "
            "tekniskt koncept i DHCP-sammanhang. Självsäker teknisk jargong ersätter "
            "substans."
        ),
    ),
    CalibrationExample(
        failure_mode="korrekt-låtande men allmänt känd branschkunskap (H2)",
        scenario=(
            "Korpusen anger inte uttryckligen att IPv6-adresser är 128 bitar långa."
        ),
        label="trivial",
        rationale=(
            "Extremt väletablerad kunskap — och dessutom EXPLICIT specificerad i både "
            "RFC 4291 och RFC 8200. Detta är ett Nivå 1-sökmissförhållande "
            "(fraseringsberoende), inte en genuin lucka. Visar varför Nivå 1 måste köras "
            "före Nivå 2 även i en tätt specificerad, teknisk korpus."
        ),
    ),
    CalibrationExample(
        failure_mode="kontrastexempel: icke-trivial (för domarens kalibrering, ej krav i sig)",
        scenario=(
            "RFC 6797 (HSTS) specificerar hur en klient ska tvinga HTTPS-uppgradering, "
            "och RFC 6960 (OCSP) specificerar hur certifikatåterkallelse kontrolleras, "
            "men ingen RFC i korpusen adresserar vad en klient ska göra när en "
            "HSTS-framtvingad anslutnings OCSP-kontroll misslyckas UNDER en "
            "DHCP-tilldelad nätverksväxling (RFC 2131) — t.ex. vid byte till ett captive "
            "portal-nätverk."
        ),
        label="icke-trivial",
        rationale=(
            "Namnger tre specifika RFC:er och en konkret, verifierbar skärningspunkt "
            "mellan deras respektive felhanteringsmekanismer — inte en mekanisk "
            "sammanslagning, utan ett precist gränssnittspåstående som går att "
            "kontrollera mot korpusens faktiska innehåll. Kandidat för Nivå 3."
        ),
    ),
]


DOMAIN_CONTEXT_C3_EDUCATION = (
    "Korpus 3 består av tre UNESCO-rapporter: (1) Global Education Monitoring Report "
    "2020 — Inclusion and education: All means all; (2) Reimagining our futures "
    "together (2021) — A new social contract for education; (3) Global Education "
    "Monitoring Report 2023 — Technology in education: A tool on whose terms? Narrativ "
    "policyrapport-prosa, inte klinisk direktivtext eller teknisk protokollspecifikation. "
    "Ett föreslaget lucka-scenario ska bedömas mot vad DESSA TRE rapporter faktiskt "
    "diskuterar, inte mot allmän utbildningspolicy-debatt i stort."
)


CALIBRATION_EXAMPLES_C3_EDUCATION: list[CalibrationExample] = [
    CalibrationExample(
        failure_mode="mellanmjölk (obligatoriskt, D-001 Lager 1 / A3)",
        scenario=(
            "Korpusen adresserar inte hur inkluderande utbildning för elever med "
            "funktionsnedsättning bör anpassas när skolor snabbt digitaliserar sin "
            "undervisning."
        ),
        label="trivial",
        rationale=(
            "Mekanisk sammanslagning av 'inkludering' (GEM 2020) och 'teknik i "
            "utbildning' (GEM 2023) till en skärningspunkt utan ett konkret, "
            "kontrollerbart påstående om VILKEN specifik anpassning, population eller "
            "teknologi som saknas. Samma geometriska signatur som en genuint grundad "
            "interpolation mellan de två rapporternas teman."
        ),
    ),
    CalibrationExample(
        failure_mode="generisk floskel utan mellanmjölks-geometri (H2)",
        scenario=(
            "Det skulle kunna finnas mer diskussion om hur utbildningssystem globalt "
            "kan bli bättre på att möta alla elevers behov."
        ),
        label="trivial",
        rationale=(
            "Kunde sägas om praktiskt taget vilken utbildningspolicy-korpus som helst. "
            "Namnger ingen specifik rapport, population, region eller mekanism. Inget "
            "kontrollerbart påstående mot DENNA korpus."
        ),
    ),
    CalibrationExample(
        failure_mode="överdrivet självsäkert men innehållslöst påstående (H2)",
        scenario=(
            "Korpusen misslyckas med att fastställa den exakta procentandelen "
            "digital undervisningstid vid vilken elevers social utveckling blir "
            "irreversibelt skadad, trots att detta är en kritisk, oadresserad lucka."
        ),
        label="trivial",
        rationale=(
            "Låter precist ('exakt procentandel', 'irreversibelt skadad') men "
            "begreppet är inte något som GEM 2023 eller någon av de andra rapporterna "
            "skulle formulera eller mäta på det sättet. Självsäker ton ersätter "
            "substans."
        ),
    ),
    CalibrationExample(
        failure_mode="korrekt-låtande men allmänt känd branschkunskap (H2)",
        scenario=(
            "Korpusen anger inte uttryckligen att tillgång till utbildning skiljer sig "
            "mellan höginkomst- och låginkomstländer."
        ),
        label="trivial",
        rationale=(
            "Extremt väletablerad kunskap som sannolikt genomsyrar samtliga tre "
            "rapporter (GEM-rapporterna bygger uttryckligen på sådan "
            "inkomstuppdelad statistik). Ett Nivå 1-sökmissförhållande "
            "(fraseringsberoende), inte en genuin lucka."
        ),
    ),
    CalibrationExample(
        failure_mode="kontrastexempel: icke-trivial (för domarens kalibrering, ej krav i sig)",
        scenario=(
            "'Reimagining our futures together' (2021) föreslår ett nytt 'socialt "
            "kontrakt' som bygger på ökat pedagogiskt samarbete mellan lärare, medan "
            "GEM 2023 dokumenterar hur EdTech-upphandling ofta sker utan lärarinflytande "
            "('a tool on whose terms?') — men ingen av rapporterna adresserar konkret "
            "hur lärarkårens röst formellt skulle inkluderas i just "
            "EdTech-upphandlingsprocesser, den specifika mekanism där de två "
            "rapporternas respektive argument möts."
        ),
        label="icke-trivial",
        rationale=(
            "Namnger två specifika rapporter och en konkret, verifierbar "
            "skärningspunkt mellan deras respektive argumentationslinjer — inte en "
            "mekanisk sammanslagning, utan ett precist, kontrollerbart påstående om "
            "vad ingen av rapporterna täcker. Kandidat för Nivå 3."
        ),
    ),
]
