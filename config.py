"""
Mapping the Negative Space — iteration 2, config.py

Lager 1 = meta-design, låst för ALLA korpusar (D-001 Lager 1, D-004, D-005, D-009).
Lager 2 = instans-kalibrering PER KORPUS (D-001 Lager 2, D-003), None tills Steg 0.5
körs för respektive korpus. Fyll aldrig i ett Lager 2-värde i efterhand för att ett
resultat sett bättre ut — varje ifyllning är en loggad handling i beslutslogg.md.
"""

# ---------------------------------------------------------------------------
# LAGER 1 — låst, gäller alla korpusar (D-001, D-004, D-005, D-009)
# ---------------------------------------------------------------------------

GAP_TYPES = ("local_nn", "centroid_edge")

# D-005: policy-val, inte härlett. Höj till 95:e om unionen av flaggade regioner
# överstiger UNION_HIGH_THRESHOLD av korpusen.
PERCENTILE_DEFAULT = 90
PERCENTILE_HIGH = 95
UNION_HIGH_THRESHOLD = 0.15

# D-004: två k-kandidater, ingen låst än. Båda klipps till [K_MIN, K_MAX].
# Förbjudet att lägga till en tredje kandidat i efterhand.
K_MIN = 3
K_MAX = 10
K_CANDIDATES = ("log", "sqrt")  # k = round(0.5*ln N) | k = round(0.5*sqrt(N))

# D-009: _chunk() sliding-window defaults — ändringsbara, inte låsta.
CHUNK_SIZE_DEFAULT = 400
CHUNK_OVERLAP_DEFAULT = 50
MIN_CHARS_DEFAULT = 60

# D-009: grön tooling, embedding-wrapper. Lokal modell, ingen API-kostnad.
# 384 dimensioner (motiverar ball-tree-valet i A1b/C2 — se open_problems).
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

# D-009 val (b): klustersteget i compute_gaps() SKIPPAS för PoC.
# Inget CLUSTER_COS_DIST_THRESHOLD. Arbeta direkt mot GapDetectionResult.regions.
SKIP_CLUSTERING = True

# D-015: global standard-gap-detektion, låst på ett värsta-fall-kriterium (inte
# bästa snitt/topp) efter D-013:s bakeoff gav oavgjort på "bäst konsekvent
# överallt". void_stat + rått MiniLM (ingen whitening, D-016 RESOLVED — ingen
# automatisk whitening-regel) + sqrt-k är den enda kombinationen vars sämsta
# korpus inte kollapsar. sqrt-k avgör därmed ÄVEN D-004:s öppna k-fråga för
# standardmetoden (samma värsta-fall-kriterium, se D-015-noteringen).
# Explicit motiverat efterhandsval, inte ett rent pre-registrerat urval — se
# D-015 i beslutslogg.md för fullständig transparensnotering.
DEFAULT_GAP_METHOD = "void_stat"
DEFAULT_EMBEDDING_SPACE = "minilm"  # rått, ingen whitening (D-016 RESOLVED)
DEFAULT_K_CANDIDATE = "sqrt"
# Per-korpus leave-one-out med denna frysta konfiguration är ENBART diagnostik
# (D-015 per-korpus-regel) — får ALDRIG användas för att välja om metod/k/
# embedding på en specifik korpus. Ett svagt diagnostiskt utfall kräver antingen
# (a) rapporterad försiktighet, eller (b) ett nytt, dokumenterat D-beslut FÖRE
# någon inspektion av de faktiska luckorna — aldrig en tyst omväljning.

# Kontrollkohort (D-001 Lager 1): obligatorisk, lika stor som gap-kohorten,
# identisk pipeline, slumpmässigt vald.
CONTROL_COHORT_ENABLED = True

# D-002: Fas 2 böjningspunkt-kriterium (andraderivata > 2x median(|andraderivata|)).
PHASE2_DERIVATIVE_MULTIPLIER = 2.0
PHASE2_FALLBACK_TEMPERATURES = (0.2, 0.5, 0.9)
PHASE1_TEMPERATURE_SWEEP = tuple(round(t * 0.1, 1) for t in range(0, 11))  # 0.0..1.0

# Fas 1 (temperatur-pilot): antal pilot-regioner, modeller. Låst HÄR, innan
# piloten körs på någon korpus. Vincent valde uttryckligen "båda modellerna som
# generatorer, jämfört sida vid sida" — dubbel kostnad men modelloberoende svar
# på om temperatur-fasövergången är modellspecifik eller generell.
PHASE1_PILOT_N_REGIONS = 3
PHASE1_GENERATOR_MODELS = {
    "anthropic": "claude-haiku-4-5-20251001",
    "openai": "gpt-4o-mini",
}
PHASE1_MAX_TOKENS = 300
# Pilotregionerna dras med denna seed och undantas explicit ur Fas 3:s
# produktionsurval (disjunkthet, v3 Del B/Fas 1-kravet).
PHASE1_PILOT_SEED = 42

# D-006: leave-one-out top-N för "återupptäckt" (binärt facit-mått för D-004).
LEAVE_ONE_OUT_TOP_N = 10
# Bland de N mest gap-flaggade regionerna i den BESKURNA korpusen: andel vars
# sanna närmaste granne ligger i det BORTTAGNA dokumentet (snarare än i den
# kvarvarande korpusen) för att räknas som "återupptäckt" (binärt facit).
# Låst HÄR, innan leave-one-out körs på någon korpus — majoritetsregel, samma
# logik som andra tröskelval i detta projekt (policy, inte härledning).
LEAVE_ONE_OUT_SUCCESS_FRACTION = 0.5

# D-011: graderat leave-one-out-mått, storlekssvep för Korpus 1. Strukturella
# gränser i mhGAP-texten (rubriker/modulgränser), inte godtyckligt valda för
# att forma kurvan. Punkt 3 och 4 återanvänder EXAKT de gränser som redan
# kördes i D-006:s binära test. Pre-registrerat innan någon rank-körning.
LEAVE_ONE_OUT_SIZE_SWEEP_C1 = [
    {
        "label": "Enskild sektion — mhGAP SUI Quick Overview",
        "source_file": "mhgGAP Intervention Guide.pdf",
        "chunk_index_range": (666, 669),
    },
    {
        "label": "Halv modul — mhGAP SUI (första halvan)",
        "source_file": "mhgGAP Intervention Guide.pdf",
        "chunk_index_range": (663, 679),
    },
    {
        "label": "Hel modul — mhGAP SUI (Self-harm/Suicide), samma som D-006 sektionsnivå",
        "source_file": "mhgGAP Intervention Guide.pdf",
        "chunk_index_range": (663, 695),
    },
    # Punkt 4 (helt dokument, 850 chunkar) hanteras separat via
    # run_leave_one_out (dokumentnivå), samma anrop som D-006 redan gjorde.
]

# D-011: storlekssvep för Korpus 2. Strukturella gränser i RFC 6797 (HSTS),
# §14 "Security Considerations" med numrerade §14.x-underavsnitt. Punkt 3 och
# den separata dokumentnivå-punkten (RFC 9112) återanvänder EXAKT samma
# gränser som redan kördes i D-006:s binära test. Pre-registrerat innan någon
# rank-körning.
LEAVE_ONE_OUT_SIZE_SWEEP_C2 = [
    {
        "label": "Enskild sektion — RFC6797 §14.5 Denial of Service",
        "source_file": "rfc6797.txt",
        "chunk_index_range": (204, 210),
    },
    {
        "label": "Halv sektion — RFC6797 §14.1-14.4 (första halvan av Security Considerations)",
        "source_file": "rfc6797.txt",
        "chunk_index_range": (184, 204),
    },
    {
        "label": "Hel sektion — RFC6797 §14 Security Considerations (hela), samma som D-006 sektionsnivå",
        "source_file": "rfc6797.txt",
        "chunk_index_range": (184, 225),
    },
    # Bonus (helt dokument, RFC 9112, 286 chunkar) hanteras separat via
    # run_leave_one_out_document, samma gränser som D-006:s dokumenttest.
]

# D-011: storlekssvep för Korpus 3. Strukturella gränser i GEM2023 (teknik i
# utbildning) Kapitel 9 "Teachers" (chunk 2005-2196, verifierad kapitelrubrik
# i texten). Punkt 3 och den separata dokumentnivå-punkten (Reimagining our
# futures together) återanvänder EXAKT samma gränser som redan kördes i
# D-006:s binära test. Pre-registrerat innan någon rank-körning.
LEAVE_ONE_OUT_SIZE_SWEEP_C3 = [
    {
        "label": "Enskild sektion — GEM2023 Ch.9, tätaste teacher shortage/training-fönster",
        "source_file": "385723eng.pdf",
        "chunk_index_range": (2095, 2109),
    },
    {
        "label": "Halvt kapitel — GEM2023 Ch.9 Teachers (första halvan)",
        "source_file": "385723eng.pdf",
        "chunk_index_range": (2005, 2100),
    },
    {
        "label": "Helt kapitel — GEM2023 Ch.9 Teachers (hela), samma som D-006 sektionsnivå",
        "source_file": "385723eng.pdf",
        "chunk_index_range": (2005, 2196),
    },
    # Bonus (helt dokument, Reimagining our futures together, 1473 chunkar)
    # hanteras separat via run_leave_one_out_document, samma gränser som
    # D-006:s dokumenttest.
]


# ---------------------------------------------------------------------------
# LAGER 2 — instans-kalibrering PER KORPUS (D-001 Lager 2, D-003, D-007, Steg 0.5)
# None = ej kalibrerat än. Fylls i, ett fält i taget, med STOPPA efter varje
# delsteg i Steg 0.5. Skriv aldrig ett nytt värde utan motsvarande beslutsrad.
# ---------------------------------------------------------------------------

CORPUS_CONFIGS = {
    "c1_clinical": {
        "label": "Korpus 1 — Klinisk/WHO",
        "source_dir": "corpora/corpus1_clinical/files",
        "n_chunks": 2939,                    # Steg 0.5.1 (chunk_size=400/overlap=50/min_chars=60, pdfplumber-baserad extraktion)
        "distance_concentration": {          # Steg 0.5.2 (D-007) — ingen stark koncentration
            "coefficient_of_variation": 0.180,
            "mean_relative_contrast": 3.76,
            "min_relative_contrast": 0.79,
            "assessment": "ej starkt koncentrerad — perceniltröskel behåller signal",
        },
        "k_log": 4,                          # Steg 0.5.3 (D-004, kandidat 1), N=2939
        "k_sqrt": 10,                         # Steg 0.5.3 (D-004, kandidat 2), klippt till K_MAX
        # D-010: θ_absens och Nivå 1-matchningströskeln (D-003) är SAMMA parameter,
        # kalibrerad en gång via D-003:s ankarprocedur. theta_absens finns inte
        # som separat fält.
        "level1_match_threshold": 0.357,       # Steg 0.5.4+0.5.5 (D-003, D-010), midpunkt känd-relaterad/orelaterad
        "domain_adapter_examples": "analysis.domain_adapter.CALIBRATION_EXAMPLES_C1_CLINICAL",  # Steg 0.5.6, 5 exempel (D-001 + H2)
        "leave_one_out_result": {             # Steg 0.5.7 (D-006) — bägge negativa
            "document_level": {"k_log": False, "k_sqrt": False},
            "section_level_SUI_module": {"k_log": False, "k_sqrt": False},
        },
        "phase2_locked_temperatures": (0.2, 0.5, 0.9),  # Steg 0.5.8 (D-002) — FALLBACK, ingen fasövergång funnen (varken Anthropic eller OpenAI klarade 2x-median-kriteriet)
        "reproducibility_status": "public",   # WHO CC BY-NC-SA 3.0 IGO — offentlig (D-008)
    },
    "c2_telecom_rfc": {
        "label": "Korpus 2 — Telekom/RFC",
        "source_dir": "corpora/corpus2_telecom_rfc/files",
        "n_chunks": None,
        "distance_concentration": None,
        "k_log": None,
        "k_sqrt": None,
        "level1_match_threshold": None,
        "domain_adapter_examples": None,
        "leave_one_out_result": None,
        "phase2_locked_temperatures": (0.2, 0.5, 0.9),  # Steg 0.5.8 (D-002) — FALLBACK, D-017 RESOLVED: fasövergång flaggad men överlevde inte robusthetskontrollen (bootstrap-stabilitet ≤60%, effekt/brus-kvot <1)
        "reproducibility_status": "public",  # IETF Trust/BCP 78 (D-008)
    },
    "c3_education": {
        "label": "Korpus 3 — Utbildning/UNESCO",
        "source_dir": "corpora/corpus3_education/files",
        "n_chunks": None,
        "distance_concentration": None,
        "k_log": None,
        "k_sqrt": None,
        "level1_match_threshold": None,
        "domain_adapter_examples": None,
        "leave_one_out_result": None,
        "phase2_locked_temperatures": (0.2, 0.5, 0.9),  # Steg 0.5.8 (D-002) — FALLBACK, D-017 RESOLVED: fasövergång flaggad men överlevde inte robusthetskontrollen (bootstrap-stabilitet ≤70%, effekt/brus-kvot ~0.4-1.3)
        "reproducibility_status": "public",  # CC BY-SA 3.0 IGO (D-008)
    },
}
