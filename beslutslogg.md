# Beslutslogg — Mapping the Negative Space (iteration 2)

> **Append-only.** Skriv aldrig över ett existerande D-beslut — lägg till ett nytt som
> ändrar/kompletterar det. Negativa/inkonklusiva resultat loggas lika öppet som positiva.
> Egen D-serie, helt skild från "Embracing the Novelty of Noise" (iteration 1).
>
> **Nästa lediga beslutsnummer: D-014.**
>
> Full text och resonemang för D-001 finns i `docs/rag_kohort_preregistrering_v3.md` (Del B),
> för D-002–D-009 i `docs/rag_kohort_tillagg_v4.md`. Denna logg är den incheckade,
> kanoniska sammanfattningen (Steg 0 i byggspecen).

---

## D-001 — RAG-kohort & geometrisk lucka-i-täckning (VÄG 2, smal PoC)

- **Datum:** 2026-07-13 (commit)
- **Kategori:** Metod / Produkt
- **Status:** FÖRSLAG → **VÄG 2 VALD** (smal PoC-demo) som startpunkt. Nivå 3 (mänsklig
  bedömning) medvetet utelämnad initialt — omprövas explicit innan slutrapport.
- **Fråga:** Kan en korpus-läsande agentkohort, styrd mot geometriskt identifierade glesa
  regioner i en godtycklig korpus C, formulera luckor som överlever automatisk silning —
  bättre än slumpmässigt regionval — och är arkitekturen domänagnostisk i praktiken?
- **Lager 1 (låst, gäller alla korpusar):** två gap-typer (lokalt NN-gap + kant/centroid-gap
  över hela C); percentiltröskel 90:e på endera måttet (höj till 95:e om unionen > 15 %);
  obligatorisk lika stor slumpmässig kontrollkohort; domänadapter (prompt/few-shot, ej
  fine-tuning) med obligatoriskt mellanmjölks-kalibreringsexempel; tregradig, icke-polariserad
  tolkning av svar↔käll-avstånd (samma tabell för båda gap-typer).
- **Explicit utanför scope:** att polarisera avståndsmålet per gap-typ (kort=bra lokalt /
  långt=bra kant) — avfärdat; avståndet är alltid diagnostiskt, aldrig egen godkännandegrind.
- **Påverkar:** `analysis/gap_detection.py`, `analysis/rag_runner.py`,
  `analysis/gap_verification.py`, `analysis/answer_source_distance.py`,
  `analysis/domain_adapter.py`, `config.py`.

---

## D-002 — Objektivt kriterium för Fas 2:s böjningspunkt

- **Fråga:** Hur avgörs objektivt om temperatur-pilotens kurva visar en "tydlig fasövergång"?
- **Beslut:** Fasövergång = funnen om **andraderivatan av svar↔käll-avståndet vid någon
  svep-punkt överstiger 2× medianen av |andraderivatan| över hela svepet.** Annars fallback
  till fasta 0,2 / 0,5 / 0,9. Låst HÄR, innan Fas 1 körs på någon korpus.
- **Avfärdat som primär metod (kvar som möjlig framtida förstärkning):** formellt
  change-point-test (PELT/Bayesianskt) med p < 0,10 — extra beroende utan proportionell
  vinst i denna skala.
- **Påverkar:** Lager 2 / Fas 2, `analysis/rag_runner.py`.

---

## D-003 — Nivå 1:s matchningströskel: procedur, inte tal

- **Fråga:** Vilket värde/procedur för "redan substantivt täckt" i Nivå 1?
- **Beslut:** Ingen universell siffra. En **kalibreringsprocedur** låses: vid Steg 0.5 per
  korpus, mät cosine-likhet för (a) kända relaterade textpar, (b) kända orelaterade par,
  (c) om möjligt mellanmjölks-liknande par; sätt tröskeln relativt dessa ankare (midpunkt
  mellan känd-relaterad-medel och mellanmjölks-medel). Talet låses per korpus innan
  produktionskörning — aldrig i efterhand.
- **Påverkar:** Steg 0.5, `analysis/gap_verification.py`.

---

## D-004 — k-formel: dubbla kandidater, testade via leave-one-out

- **Fråga:** Låsa k-heuristiken som är, eller testa mot alternativ?
- **Beslut:** k låses INTE ännu. Två kandidater pre-registreras, båda klippta till **[3, 10]**
  (`k = max(3, min(10, formel))`):
  - Kandidat 1 (logaritmisk): `k = round(0,5 · ln N)`
  - Kandidat 2 (kvadratrot): `k = round(0,5 · √N)`
- **Testprocedur (låst):** per korpus, kör leave-one-out (D-006) med båda k. Utvärderingsmått:
  återupptäcks den kända borttagna luckan inom top-N flaggade regioner (binärt). En formel är
  generell regel om den träffar på **≥ 2 korpusar** (utöver BCM-fallback). Alla utfall för
  båda kandidaterna på alla korpusar rapporteras.
- **Slutlägen:** en formel vinner konsekvent → låses; annars → k blir per-korpus-parameter.
- **Förbjudet:** välja k utan facit; lägga till en tredje kandidat i efterhand.
- **STATUS:** ~~körbar~~ → **RESOLVED 2026-07-13** (se notering nedan). Formler/procedur låsta här.
- **Påverkar:** Lager 1, `analysis/gap_detection.py`, `analysis/leave_one_out.py`.

- **RESOLVED-notering (2026-07-13) — facit för den redan låsta kontingensregeln, inget nytt beslut:**
  Leave-one-out (D-006) kört på alla tre korpusar (C1 klinisk, C2 telekom, C3 utbildning),
  båda k-kandidaterna, på både dokument- och sektionsnivå. Binärt topp-10-facit:
  11 av 12 körningar gav 0/10; enda undantaget C1/mhGAP dokumentnivå (k_log 2/10, k_sqrt 1/10).
  **Ingen körning nådde framgångsgränsen (≥50 % av topp-10). Ingen formel når "≥2 korpusar".**
  Per D-004:s andra pre-registrerade slutläge: **k blir en per-korpus-kalibreringsparameter**
  (ingen universell formel låses). Detta är ett av de två i förväg definierade giltiga utfallen,
  inte ett misslyckande. Det graderade måttet (D-011) nyanserar men motsäger inte: k_log och
  k_sqrt presterar genomgående likartat; skillnaderna MELLAN korpusar (C1 bäst på sektioner,
  C2 bäst på hela dokument, C3 svagt överlag) dominerar över skillnaden mellan formlerna.
  Facit står; radera aldrig denna rad om ett senare beslut ändrar hanteringen av k — komplettera.

---

## D-005 — Percentiltröskeln är ett policy-val, inte en härledd storhet

- **Beslut:** 90:e/95:e percentilen är **ett policy-val** (som val av signifikansnivå),
  inte en härledning. 90:e default (höj till 95:e vid unionsöverskridande > 15 %). Får aldrig
  beskrivas som empiriskt bevisad optimal i formella avsnitt.
- **Möjlig framtida förfining (ej krav):** precision/recall-kurva mot känd lucka över
  pre-registrerade percentil-kandidater — fortfarande ett VAL på kurvan.
- **Påverkar:** Lager 1, rapportspråk.

---

## D-006 — Leave-one-out-test som obligatoriskt externt ankare

- **Fråga:** v3 saknade extern ground truth (bara kontrollkohort). (CRITICAL C1.)
- **Beslut:** Obligatoriskt steg i Lager 1 före Fas 3: ta bort ett dokument/sektion som känt
  täcker ett namngivet ämne → kör Nivå 0–2 på beskuren korpus → kontrollera (a) uppstår
  gap-region där det borttagnas grannskap satt, (b) klassar Nivå 2 scenariot icke-trivialt.
  Rapporteras oavsett utfall. Är samtidigt facit för D-004.
- **STATUS:** körbar (D-008).
- **Påverkar:** Lager 1, `analysis/leave_one_out.py`.

---

## D-007 — Distance-concentration-kontroll läggs till i Steg 0.5

- **Fråga:** Högdimensionell distance concentration kan urholka NN-gap oavsett sökalgoritm.
  (CRITICAL C2.)
- **Beslut:** Empirisk karakterisering av avståndsfördelningen läggs till som obligatoriskt
  delsteg i Steg 0.5, INNAN percentiltröskeln tillämpas skarpt. Vid stark koncentration:
  diskutera percentilens signalstyrka explicit i rapporten; lokal densitetsnormalisering
  övervägs som komplement (ej krav för PoC).
- **Påverkar:** Steg 0.5.

---

## D-008 — Korpusleverans godkänd, Korpus 1 accepterad under målstorlek

- **Beslut:** **369 sidor för Korpus 1 (klinisk, WHO-only) godtas som är. Ingen extra PDF
  läggs till.** Fattat innan analys — inte efter svagt resultat.
- **Dokumenterade begränsningar:** Korpus 1 WHO-only (ej WHO+NICE); Korpus 2 (telekom)
  förskjuten mot säkerhet/infrastruktur (DNSSEC, HTTP/HSTS, IPv6); alla tre öppet licensierade
  → offentlig reproducerbarhets-status.
- **Bieffekt:** brett N-spann (telekom ~1,29M, klinisk ~1,00M, utbildning ~4,50M tecken) att
  testa k-formlernas skalning över.
- **Påverkar:** korpusmanifesten, D-004 (fler N-punkter).

---

## D-009 — Återanvänd tooling från iteration 1: grön lista, med ett exponerat undantag

- **Grön lista (återanvänds som tooling, alla parametrar omkalibreras för denna korpus):**
  embedding-wrapper, `_l2_normalize()`, `_mean_pairwise_distance()`, `compute_gaps()`
  (lokalt + centroid), `_extract_text()` (pdfplumber), `_chunk()` (sliding window;
  chunk_size=400/overlap=50/min_chars=60 = **ändringsbara defaults**, ej låsta),
  `_spearman_ci()` (Fisher z, 95 % CI), `_surface_stats()`.
- **KRITISKT FÖRBEHÅLL — `compute_gaps()`:** iteration 1:s interna `_cluster_regions()` hade
  `CLUSTER_COS_DIST_THRESHOLD = 0.30` hårdkodat (BCM-δ=0,70). **Val (b): klustersteget
  SKIPPAS för PoC.** Arbeta direkt mot `GapDetectionResult.regions`. Klustring = nytt beslut
  (D-011+) om det behövs, aldrig tyst återaktivering.
- **Explicit exkluderat (ej kopierat):** N(j)-formeln, τ-kohorter, θ_absens/θ_match/δ,
  SVB/Basel-logik, embedding_characterization, scorer, deduplicator, proxy_bundle, runner,
  gap_verification (iter 1), rag_runner (iter 1, 20-agent-hårdkopplad), instability_tool.
- **Not:** koden i detta repo skrivs ren från grunden enligt dessa specifikationer — inga
  filer kopieras från iteration 1-repot, och inga av dess kalibrerade värden importeras.
- **Påverkar:** hela kodbasen, `analysis/gap_detection.py`.

---

## D-010 — θ_absens och Nivå 1-matchningströskeln slås ihop till EN kalibrerad parameter

- **Datum:** 2026-07-13
- **Kategori:** Metod / Steg 0.5-genomförande
- **Fråga:** Tillägg v4:s uppdaterade Steg 0.5-lista har två separata punkter — (4) "kalibrera
  θ_absens (oförändrad procedur från v3/D-017-analogin)" och (5) "Nivå 1-matchningströskel
  (D-003)". D-017 är dock ett iteration 1-beslut vars procedur INTE står på D-009:s gröna
  lista — `docs/CLAUDE.md`s hårda regel exkluderar θ_absens-logik explicit
  (`gap_verification.py`, `embedding_characterization.py`). Att följa Steg 0.5.4 bokstavligt
  hade krävt kunskap om en exkluderad procedur. Hur löses detta utan att gissa på D-017:s
  innehåll?
- **Beslut:** θ_absens och Nivå 1-matchningströskeln behandlas som **EN och samma kalibrerade
  parameter**, framtagen EN gång via D-003:s egen ankarprocedur (kända relaterade textpar,
  kända orelaterade textpar, ur den aktuella korpusen — inga värden eller kod från D-017
  återanvänds). Steg 0.5.4 och 0.5.5 slås därmed ihop till ett kombinerat delsteg.
- **Motivering:** D-003:s egen text säger redan att Nivå 1-tröskeln ska kalibreras "precis
  som θ_absens gjordes i iteration 1 (fast med NYA ankare, NYTT värde per korpus)" — dvs.
  bara MÖNSTRET (ankarpar → tröskel) förs över, aldrig den gamla proceduren i detalj eller
  dess värden. Att ha en enda parameter, kalibrerad en gång med en fullt specificerad,
  egen procedur, undviker helt risken att av misstag återskapa något D-017-specifikt.
- **Avvägning, explicit noterad:** om θ_absens (gap-detektionens "är regionen gles nog för
  att räknas") och Nivå 1-tröskeln (bred korpussöknings "är detta ämne redan täckt") egentligen
  behöver mäta två olika saker, tappas den distinktionen med detta beslut. Bedöms acceptabelt
  för PoC — kan delas upp igen som ett nytt beslut (D-011+) om Steg 5/6 visar att en enda
  tröskel inte räcker.
- **Beslutat av:** Vincent (valde uttryckligen "alternativ 1" av tre framlagda alternativ).
- **Påverkar:** `config.py` (fält `level1_match_threshold` blir den enda kombinerade
  parametern; `theta_absens`-fältet utgår), Steg 0.5.4–0.5.5 (slås ihop), `analysis/gap_verification.py`.

---

## D-011 — Graderat leave-one-out: borttagen andel vs. återupptäckts-rank

- **Datum:** 2026-07-13
- **Kategori:** Metod / Utvärderingsmått (tillägg till D-004/D-006)
- **Fråga:** Det binära top-N-måttet (D-004/D-006) missar små sektioner per konstruktion. En
  borttagen region på ~1,1 % av korpusen (SUI-modulen, 33 chunkar) kan inte vinna ett globalt
  topp-10-fönster (top 0,34 %) även om den skapar en verklig lokal grop — den måste konkurrera
  mot alla naturligt glesa punkter i hela 2900+-korpusen. Både dokument- och sektionsnivå gav
  0/10 på Korpus 1 för båda k-kandidaterna. Frågan: kan metodens känslighet mätas **graderat**
  i stället för binärt, så att "nära men inte i topp-10" skiljs från "helt osynlig"?
- **Beslut:** Inför ett **rank-baserat** leave-one-out-mått vid sidan av — inte i stället för —
  det binära. För varje borttagen enhet: kör Nivå 0–2 på beskuren korpus, ta reda på **rangen**
  (i den globala gles-region-rankingen) för den region som ligger närmast det borttagnas
  ursprungliga plats, och rapportera `rank` och normaliserat `rank/N`. Genom att ta bort enheter
  av **olika storlek** fås en kurva: **andel av korpus borttagen (x) vs. rank/N (y)**. Tolkning:
  en liten borttagning förväntas kräva djup sökning (hög rank/N); en stor förväntas hittas nära
  toppen (låg rank/N). Kurvans form är resultatet och rapporteras oavsett utfall.
- **Låst innan körning:**
  - (a) "närmast det borttagnas plats" = den kvarvarande chunk vars index gränsar till den
    borttagna sektionens ursprungliga position (samma grannskapsdefinition som D-006).
  - (b) rapporteras för **båda** k-kandidaterna (D-004).
  - (c) storlekssvepet (vilka borttagningsstorlekar som testas) **pre-registreras** innan
    någon körning — aldrig valt i efterhand för att forma kurvan.
- **Förhållande till existerande beslut:** Detta är den graderade förfining som D-005 redan
  förutsåg ("precision/recall-kurva mot känd lucka … fortfarande ett VAL på kurvan"). Det
  **binära topp-10-resultatet (D-004/D-006) står kvar oförändrat** — D-011 är ett tillägg, inte
  en efterhandsjustering av ett redan kört test. Ingen rad i den befintliga leave-one-out-tabellen
  ändras.
- **Förbjudet:** att i efterhand välja borttagningsstorlekar som får kurvan att se snällare ut;
  att ersätta eller radera det binära måttet.
- **Beslutat av:** Vincent.
- **Påverkar:** `analysis/leave_one_out.py` (nytt rank-mått + storlekssvep), rapportspråk.
  Ändrar inte D-004:s formler eller D-006:s procedur.
- **STATUS:** loggat. Storlekssvep + körning återstår (nästa steg, med STOPPA efter varje delsteg).

---

## D-012 — Topp-N i D-004/D-006:s binära test var ett fast tal, inte skalat mot N — storleksskalad brytpunktssvep läggs till

- **Datum:** 2026-07-13
- **Kategori:** Metod / Utvärderingsmått (tillägg till D-004/D-006/D-011)
- **Fråga:** `LEAVE_ONE_OUT_TOP_N = 10` (D-006) är ett FAST absoluttal, applicerat oförändrat på
  tre korpusar vars N skiljer ~5× (C1 N≈2900, C2 N≈3200, C3 N≈14000). Topp-10 motsvarar därför
  olika stränga barer per korpus: ~0,34–0,40 % av C1/C2, men bara ~0,07 % av C3 — nästan 5×
  strängare för C3 av ren storleksskäl, oavsett faktisk signalkvalitet. Upptäckt EFTER att det
  binära facit (D-004/D-006, 11/12 = 0/10) redan var kört och loggat. Bör detta korrigeras, och
  hur, utan att tyst skriva om ett redan rapporterat negativt resultat?
- **Beslut:** Det ursprungliga fasta topp-10-facit (D-004/D-006-RESOLVED-noteringen) ändras
  INTE — det står kvar precis som loggat. Vid sidan av läggs en **storleksskalad
  brytpunktssvep**: för samma redan använda borttagningar (dokument- och sektionsnivå-testerna
  i D-006, alla tre korpusar, båda k), svep topp-N över ett spann (10, 20, 50, 100, sedan
  procentandelar av N_truncated) och rapportera:
  1. `fraction_pointing_to_removed` vid **topp 1 % av N_truncated** och **topp 0,5 % av
     N_truncated** (Vincents val — testa båda, inte bara en).
  2. Den minsta topp-N (och motsvarande topp-N/N_truncated) vid vilken
     `fraction_pointing_to_removed` korsar 50 %-framgångsgränsen (D-006:s
     `LEAVE_ONE_OUT_SUCCESS_FRACTION`) — den faktiska statistiska brytpunkten, per
     korpus/storlek/k-kandidat.
- **Explicit avgränsning:** detta är en ren geometrisk brytpunktsanalys (ingen LLM-kostnad).
  En separat, praktisk fråga — hur många källchunkar (k) som ryms i en enskild LLM-prompt
  innan tokengränsen nås — hör till Fas 3:s agent-design, INTE till detta beslut, och tas upp
  separat när Fas 3 planeras.
- **Förhållande till D-004/D-006/D-011:** tillägg, inte ersättning eller efterhandsjustering av
  redan kört facit. Ändrar inte `LEAVE_ONE_OUT_TOP_N=10`:s redan rapporterade resultat.
- **Förbjudet:** att skriva om det befintliga topp-10-facit; att välja svepets stopppunkter i
  efterhand för att få en snällare brytpunkt.
- **Beslutat av:** Vincent.
- **Påverkar:** `analysis/leave_one_out.py` (nytt svep-mått), rapportspråk. Ändrar inte D-004:s
  formler, D-006:s procedur eller D-011:s redan körda resultat.
- **STATUS:** loggat. Implementation + körning återstår (nästa steg, STOPPA efter varje delsteg).

---

## D-013 (FÖRSLAG) — Bredda gap-detektionen till en pre-registrerad metod- och embedding-bakeoff

- **Datum:** 2026-07-13
- **Kategori:** Metod / Utvärderingsmått (tillägg till D-004/D-006/D-011/D-012)
- **Fråga:** Nuvarande gap-detektion (lokalt NN + centroid, global percentil) klarade inte
  leave-one-out-facit (D-004/D-006 RESOLVED) på någon av C1–C3. Ska metod-rummet breddas till en
  pre-registrerad, låst uppsättning alternativa gap-operationaliseringar, jämförda sida vid sida,
  där vinnaren = den som fungerar konsekvent bäst över alla tre korpusar och ≥2 embedding-rum?
- **Beslut:** Ja. Två axlar pre-registreras och låses INNAN körning.
  - **Metodkandidater (låst lista, ingen sjätte i efterhand, jfr D-004):**
    1. Baslinje: lokalt NN + centroid, global percentil (nuvarande).
    2. LOF (local outlier factor) — lokalt relativ densitet.
    3. KDE-baserad densitetspoäng.
    4. Persistent homologi — H1/H2-persistence för regionens grannskap.
    5. Empty-space/void-statistik — lokal void-poäng via spherical contact / J-funktion.
  - **Embedding-rum (låst lista, ingen fjärde i efterhand):**
    (a) all-MiniLM-L6-v2 (384d, nuvarande baslinje) · (b) all-mpnet-base-v2 (768d, annan
    familj) · (c) whitening-/isotropi-transform av (a). Alla lokala, ingen API-kostnad.
  - **Utvärdering (låst):** primärt D-011:s graderade rank/N (cutoff-fritt), sekundärt D-006:s
    binära facit; körs för varje (metod × embedding × korpus × k). Ren geometri, ingen
    LLM-kostnad.
  - **Vinnarkriterium (låst):** en metod "vinner" om den ger lägst rank/N konsekvent över ALLA
    tre korpusar OCH ≥2 embedding-rum. Oavgjort → ingen låses, rapporteras som sådant.
  - **Overfitting-skydd:** (1) låst kandidat-/embedding-lista; (2) leave-one-corpus-out — varje
    kandidat väljs på två korpusar och bekräftas på den tredje, roterat, som
    utanför-urvalet-kontroll; (3) alla kandidater rapporteras på alla korpusar oavsett utfall.
- **Förbjudet:** lägga till metod/embedding i efterhand; välja vinnare utan att alla kört; tysta
  bort en förlorande kandidat.
- **Beslutat av:** Vincent.
- **Påverkar:** ny modul `analysis/gap_methods.py`, `config.py`, `beslutslogg.md`. Ändrar inte
  D-004/D-006/D-011:s redan körda resultat.
- **STATUS: FÖRSLAG.** Inget kört. Ingen implementation påbörjad. Väntar på beslut om
  genomförande innan Steg 0.5 (Korpus 2/3 temperatur-pilot) eller något annat fortsätter.

---

*Steg 0 (byggspec Del C) genomfört: Del B (D-001) + D-002–D-009 incheckade. D-010 tillagt
2026-07-13 (Steg 0.5-genomförande). D-011 tillagt 2026-07-13 (graderat leave-one-out-mått).
D-004 RESOLVED 2026-07-13 (k blir per-korpus-parameter — facit över alla tre korpusar). D-012
tillagt 2026-07-13 (storleksskalad topp-N-brytpunktssvep). D-013 (FÖRSLAG) tillagt 2026-07-13
(metod-/embedding-bakeoff) — EJ FATTAT, väntar på beslut. Nästa steg: invänta besked om D-013,
under tiden återstår temperatur-piloten (Steg 0.5.8) på C2/C3.*
