# Beslutslogg — Mapping the Negative Space (iteration 2)

> **Append-only.** Skriv aldrig över ett existerande D-beslut — lägg till ett nytt som
> ändrar/kompletterar det. Negativa/inkonklusiva resultat loggas lika öppet som positiva.
> Egen D-serie, helt skild från "Embracing the Novelty of Noise" (iteration 1).
>
> **Nästa lediga beslutsnummer: D-026.**
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
- **STATUS:** ~~FÖRSLAG~~ → ~~GENOMFÖRD 2026-07-15~~ → **KONTAMINERAD, OMKÖRS** (se
  läck-notering nedan, före det ursprungliga resultatet).

- **LÄCK-NOTERING (2026-07-15) — whitening fittades på HELA korpusen, inte per trunkering:**
  Vincent frågade specifikt om `whiten()` refittades på den beskurna korpusen i varje
  leave-one-out-veva. Svaret var nej: `.cache/{korpus}_whitened_embeddings.npy` byggdes EN gång
  per korpus (medelvärde + kovarians beräknat över SAMTLIGA chunkar, inklusive det som senare
  "togs bort" i varje enskilt leave-one-out-test), och `run_bakeoff_indices()` trunkerade bara
  den redan whitened matrisen. Whitening-transformens statistik såg alltså det borttagna
  innehållets bidrag till korpusens medelvärde/kovarians — en läcka som kan ha gynnat
  whitened_minilm artificiellt, mest potentiellt vid stora borttagningar (upp till 29 % av C1
  vid dokumentnivå-testerna). **Rättat:** `run_bakeoff_indices()` fick en ny `transform_fn`-
  parameter som appliceras EFTER trunkering, på rena/otransformerade embeddings — whitening
  fittas nu alltid bara på den faktiskt synliga (beskurna) korpusen. Nedanstående resultat är
  **KONTAMINERADE och ska INTE citeras som facit** — kvar synliga för spårbarhet, inte
  raderade, i väntan på omkörning med den rättade koden.

- **Resultat-notering (2026-07-15, KONTAMINERAD — se läck-notering ovan) — alla 90
  kombinationer körda (5 metoder × 3 embedding-rum ×
  3 korpusar × 2 k), samma borttagningsmål som D-006:s sektionsnivå-test per korpus (SUI-modul/
  §14 Security Considerations/GEM2023 Ch.9), rank-mått som i D-011:**

  | Korpus | Bästa kombo | rank/N |
  |---|---|---|
  | C1 klinisk | whitened_minilm / persistent_homology / sqrt-k | 0,0079 |
  | C2 telekom | whitened_minilm / persistent_homology / log-k | 0,0583 |
  | C3 utbildning | whitened_minilm / baseline / log-k | 0,0109 |

  **Vinnarkriteriet uppfylls INTE av någon metod.** `persistent_homology` vinner på C1 och C2
  (inom whitened_minilm) men är den SÄMSTA metoden på C3 (0,298–0,533, sämre än baseline på
  samma korpus). Leave-one-corpus-out-skyddet fångar detta direkt: väljer man
  `persistent_homology` på C1+C2 och bekräftar mot C3 (hållet utanför), misslyckas
  bekräftelsen — overfitting-kontrollen fungerade som avsett. **Per den pre-registrerade
  kontingensregeln: oavgjort, ingen metod låses.**

  **Sekundärt, oplanerat men konsekvent fynd på embedding-axeln:** i ALLA TRE korpusar använde
  den enskilt bästa kombinationen `whitened_minilm`. Whitening förbättrar även den REDAN
  BEFINTLIGA baseline-metoden kraftigt på C3 — från rå MiniLM+baseline (0,319–0,359, D-011:s
  ursprungliga resultat) till whitened_minilm+baseline (0,011–0,018), utan metodbyte. Detta var
  inte en pre-registrerad jämförelseaxel för "vinst" (bara metod-axeln var det) och ska INTE
  beskrivas som ett bekräftat, låst fynd — men är värt ett eget, framtida pre-registrerat
  beslut (D-014+) om det ska undersökas vidare, exakt i linje med hur D-011/D-012 byggdes ovanpå
  D-006 utan att röra det ursprungliga facit.
  - **Tekniskt fel upptäckt och rättat UNDER körningen (loggat för transparens, inte gömt):**
    `analysis/distance_concentration.py` hade en division-nära-noll-bugg vid nästan-identiska
    chunkar (upptäckt på Korpus 3, se D-007-resultatet 2026-07-13) — rättad innan detta
    D-013-facit togs fram, påverkar inte D-013:s siffror (annan modul).
- **Beslutat av:** Vincent (godkände genomförande efter FÖRSLAG-loggningen).
- **Påverkar:** `analysis/gap_methods.py` (ny), `.cache/bakeoff_c1.json`, `.cache/bakeoff_c2.json`,
  `.cache/bakeoff_c3.json`. Ändrar inte D-004/D-006/D-011/D-012:s redan körda resultat.

- **KORRIGERAT RESULTAT (2026-07-15, efter läck-fix — detta är facit, INTE raden ovan):**
  `run_bakeoff_indices()` fick en `transform_fn`-parameter (whitening appliceras nu EFTER
  trunkering, fittas bara på synlig data). Samtliga 90 kombinationer omkörda
  (`.cache/bakeoff_c1_v2.json`, `_c2_v2.json`, `_c3_v2.json`):

  | Korpus | Bästa kombo (korrigerat) | rank/N |
  |---|---|---|
  | C1 klinisk | whitened_minilm / persistent_homology / log-k | 0,0172 (~oförändrat) |
  | C2 telekom | **minilm (RÅ) / persistent_homology / sqrt-k** | 0,0996 (whitening-resultatet kollapsade från 0,0583 → 0,298) |
  | C3 utbildning | whitened_minilm / baseline / log-k | 0,0071 (~oförändrat, marginellt bättre) |

  **Vinnarkriteriet uppfylls fortfarande INTE av någon metod** — samma "oavgjort"-slutsats som
  innan, men av delvis andra skäl: C2:s bästa kombo är nu RÅ MiniLM, inte whitened. Läckan hade
  alltså inflaterat just C2:s whitening-resultat kraftigt, medan C1 och C3:s whitening-fynd höll
  sig i stort sett oförändrade efter rättningen. Se D-014 för det fullständiga
  robusthetstestet av whitening-fyndet över alla sex etablerade borttagningsmål.

---

## D-014 — Robusthetstest av D-013:s whitening-fynd över alla redan etablerade borttagningsmål

- **Datum:** 2026-07-15
- **Kategori:** Metod / Utvärderingsmått (uppföljning av D-013:s sekundärfynd)
- **Fråga:** D-013:s bakeoff testade whitening bara mot ETT borttagningsmål per korpus
  (sektionsnivå). Håller fyndet (whitened_minilm förbättrar baseline-metoden kraftigt) över de
  SEX borttagningsmål som redan är etablerade i D-006/D-011 (dokument- OCH sektionsnivå, alla
  tre korpusar), eller var det en engångsobservation kopplad till just det ena testade målet?
- **Beslut:** Kör **baseline-metoden** (redan låst, INGEN ny metod — isolerar embedding-effekten
  från metod-effekten) i BÅDA embedding-rummen (rå MiniLM vs. whitened_minilm) på samtliga sex
  redan etablerade borttagningsmål (D-006: C1 dokument mhGAP + sektion SUI; C2 dokument RFC9112
  + sektion §14; C3 dokument Reimagining + sektion Ch.9), båda k-kandidater = **12
  jämförelsepar** (24 körningar totalt).
- **Framgångskriterium (låst innan körning):** whitening räknas som **robust bekräftat** om
  rank/N förbättras (minskar) i minst **10 av 12** jämförelsepar — strängare majoritetsregel än
  D-006:s 50 % eftersom detta är en BEKRÄFTELSE-körning av ett redan observerat mönster, inte en
  förstagångsupptäckt. Under 10/12 → fyndet begränsas till "syntes på det ursprungliga
  testmålet", rapporteras ärligt, låses inte som generellt.
- **Förbjudet:** byta metod eller borttagningsmål i efterhand; lägga till fler embedding-rum för
  att förbättra utfallet.
- **Beslutat av:** Vincent.
- **Påverkar:** `analysis/gap_methods.py` (återanvänds oförändrad), rapportspråk. Ändrar inte
  D-004/D-006/D-011/D-012/D-013:s redan körda resultat.
- **STATUS: GENOMFÖRD 2026-07-15** (efter läck-fix i `run_bakeoff_indices` — se D-013:s
  korrigerade resultat-notering; denna körning skedde med den rättade koden, ingen kontaminerad
  version av D-014 finns).

- **Resultat:**

  | Korpus | Nivå | k | rå MiniLM rank/N | whitened rank/N | Förbättrad? |
  |---|---|---|---|---|---|
  | C1 klinisk | Dokument (mhGAP) | log | 0,8698 | 0,6539 | Ja |
  | C1 klinisk | Dokument (mhGAP) | sqrt | 0,8593 | 0,5692 | Ja |
  | C1 klinisk | Sektion (SUI) | log | 0,0595 | 0,2670 | **Nej** |
  | C1 klinisk | Sektion (SUI) | sqrt | 0,0537 | 0,0705 | **Nej** |
  | C2 telekom | Dokument (RFC9112) | log | 0,0106 | 0,2210 | **Nej** |
  | C2 telekom | Dokument (RFC9112) | sqrt | 0,0147 | 0,2087 | **Nej** |
  | C2 telekom | Sektion (§14) | log | 0,5473 | 0,4448 | Ja |
  | C2 telekom | Sektion (§14) | sqrt | 0,4341 | 0,4247 | Ja |
  | C3 utbildning | Dokument (Reimagining) | log | 0,7740 | 0,2254 | Ja |
  | C3 utbildning | Dokument (Reimagining) | sqrt | 0,7214 | 0,2405 | Ja |
  | C3 utbildning | Sektion (Ch.9) | log | 0,3188 | 0,0071 | Ja |
  | C3 utbildning | Sektion (Ch.9) | sqrt | 0,3589 | 0,0222 | Ja |

  **8 av 12 förbättrade — under den pre-registrerade gränsen på 10/12.** Per kontingensregeln:
  **whitening är INTE robust bekräftat som ett generellt förbättrande embedding-val.** Mönstret
  är korpus- och målberoende: whitening hjälper konsekvent på C3 (båda mål, alla fyra
  körningar) och på C1:s dokumentnivå, men SKADAR resultatet där rå MiniLM redan var mycket
  starkt (C1:s sektionsnivå, som var D-013:s ursprungliga, mest lovande testpunkt — rank/N
  försämras 4-5× där; C2:s dokumentnivå, redan excellent på rå MiniLM 0,011–0,015, försämras
  till ~0,21–0,22 med whitening).
  - **Ärlig slutsats:** D-013:s ursprungliga whitening-fynd var till stor del specifikt för det
    ENA testade målet per korpus (och delvis inflaterat av läckan för C2). Whitening är inte en
    generell förbättring av gap-detektionen i den här pipelinen — det är en korpus-/
    målberoende avvägning, konsekvent med hur k-formeln (D-004) och metod-bakeoffen (D-013)
    redan visat sig vara: inget som hittills testats generaliserar rakt av över alla tre
    korpusar och alla borttagningsstorlekar.

---

## D-015 (FÖRSLAG) — Lås global gap-detektionskonfiguration på värsta-fall-kriteriet; per-korpus leave-one-out blir enbart diagnostik

- **Datum:** 2026-07-16
- **Kategori:** Metod / Val av standardkonfiguration (bygger på D-013/D-014)
- **Fråga:** D-013:s pre-registrerade kriterium ("lägst rank/N konsekvent över alla tre
  korpusar") gav oavgjort — ingen metod är bäst överallt. Men projektets mål är pålitlighet
  över korpusar, inte högsta topp på någon enskild. Under en fast konfiguration (rått minilm,
  sqrt-k) är void_stat den enda metoden vars sämsta korpus (0,196) inte kollapsar, medan alla
  andra har minst en korpus på 0,43–0,47. Bör den globala standarden låsas på ett
  värsta-fall-kriterium i stället?
- **Beslut:** Lås `void_stat` + rått minilm + sqrt-k som global standard-gap-detektion.
  Motivering: minimera det högsta rank/N över korpusarna (bästa golv), inte bästa snitt eller
  bästa topp.
- **Explicit transparens (icke förhandlingsbar):** detta kriterium (värsta-fall) valdes efter
  att D-013:s oavgjort setts, motiverat av projektets uttalade mål att fungera pålitligt över
  godtyckliga korpusar. Det är därför INTE ett rent pre-registrerat urval utan ett motiverat,
  öppet redovisat efterhandsval — och det verkliga out-of-sample-testet är nästa nya korpus,
  där konfigurationen tillämpas fryst.
- **Per-korpus-regel (låst framåt):** för varje ny korpus körs leave-one-out ENBART som
  diagnostik/hälsokontroll med den frysta konfigurationen, och rapporteras. Metodvalet får
  ALDRIG göras om baserat på det diagnostiska utfallet (det vore att spendera den enda externa
  ground truth på urval → overfitting). Om diagnosen faller på en ny korpus: (a) rapportera
  försiktighet, eller (b) fatta ett nytt, dokumenterat D-beslut innan de substantiella luckorna
  inspekteras — aldrig en tyst omväljning.
- **Sidonoteringar:** `persistent_homology` behålls som dokumenterad högrisk-högbelöning-metod
  (bäst på C1/C2, kollapsar på C3) — inte standard just p.g.a. C3-kraschen. Whitening loggas
  som korpus-beroende (D-014: 8/12, hjälper C3, skadar C1-sektion/C2-dokument) — inte global;
  får bara aktiveras per korpus via ett framtida pre-registrerat beslut.
- **Förbjudet:** göra om metodvalet per korpus mot leave-one-out-facit; tyst byta till
  whitening; omtolka värsta-fall-kriteriet i efterhand för att gynna en annan metod.
- **k-notering:** sqrt-k-valet avgör härmed ÄVEN D-004:s öppna k-fråga FÖR STANDARDMETODEN —
  inte genom D-004:s eget vinnarkriterium (som redan gav "k blir per-korpus-parameter", D-004
  RESOLVED, oförändrat), utan genom samma värsta-fall-logik som D-015 använder för
  metod/embedding-valet. D-004:s per-korpus-resultat och RESOLVED-notering står kvar orörda;
  detta är bara vilket k-val standardpipelinen faktiskt kör med.
- **Beslutat av:** Vincent.
- **Påverkar:** `config.py` (standard-metod/embedding/k), `beslutslogg.md`. Ändrar inte
  D-013/D-014:s redan körda resultat.
- **STATUS:** ~~FÖRSLAG~~ → **GENOMFÖRD 2026-07-16.** `config.py` uppdaterad:
  `DEFAULT_GAP_METHOD="void_stat"`, `DEFAULT_EMBEDDING_SPACE="minilm"` (rått, oförändrad
  `EMBEDDING_MODEL`), `DEFAULT_K_CANDIDATE="sqrt"`. Inga Lager 1-låsta värden i övrigt rörda.

- **KORRIGERINGSNOTERING (2026-07-16, efter D-018:s fullständiga körning) — D-015:s
  värsta-fall-siffra (~0,196) täckte bara sektionsnivå, inte dokumentnivå:**
  D-015:s ursprungliga värsta-fall-jämförelse byggde på D-013:s bakeoff, som (liksom D-011)
  bara testade ETT borttagningsmål per korpus — sektionsnivå (SUI-modul/§14/Ch.9). D-018:s
  fullständiga körning (dokument OCH sektion, alla tre korpusar, samma frysta konfiguration
  void_stat+rått minilm+sqrt-k) visar att `void_stat`s VERKLIGA globala värsta-fall är
  **0,877** (C3, dokumentnivå — Reimagining our futures together), inte 0,196.
  - **Precisering:** `void_stat` är pålitlig för sektions-skaliga luckor (rank/N ~0,14–0,20
    över alla tre korpusar) men OPÅLITLIG för dokument-skaliga luckor (0,379 på C1, 0,877 på
    C3 — bara C2:s dokumentnivå är stark, 0,034). Den ursprungliga D-015-siffran (~0,196) var
    korrekt för vad den faktiskt mätte (sektionsnivå), men ofullständig som ett påstående om
    metodens generella tillförlitlighet.
  - **`void_stat` förblir global standard.** Även med den fullständiga (dokument+sektion)
    jämförelsen har `void_stat` fortfarande BÄST globalt värsta-fall av de tre testade
    metoderna (0,877 mot cvde 0,927 och dtm 0,899, se D-018) och vinner tydligt på C1 och C2.
    Beslutet i D-015 (`config.py`: `DEFAULT_GAP_METHOD="void_stat"` osv.) ändras INTE av
    denna notering.
  - **Reliabilitetspåståendet begränsas:** framtida rapportspråk om `void_stat`s
    tillförlitlighet ska specificera "på sektions-skaliga luckor", inte generellt, tills
    dokumentnivå-detektion är löst eller separat validerad.
  - **Strukturell observation (inte void_stat-specifik):** dokument-skalig detektion är svag
    för ALLA tre testade metoder i D-018 utom på C2 (void_stat 0,034, cvde 0,010, dtm 0,006 —
    alla starka där) — men kollapsar på C1 (0,38–0,93) och C3 (0,50–0,88) oavsett metod. Detta
    är sannolikt en **fundamental geometrisk begränsning** (stora, tematiskt breda
    borttagningar lämnar inget lokalt "hål" att detektera med NN-baserade mått, se
    resonemanget i D-006/D-011 om varför hela-dokument-borttagningar redan då gav svaga
    binära/graderade resultat på C1/C3) — inte ett metodval som kan lösas genom att byta
    severity-funktion.
  - **D-015:s ursprungliga siffra (~0,196) raderas INTE** — kvar ovan, kompletterad med denna
    notering, i linje med append-only-principen.
  - **Påverkar:** rapportspråk (reliabilitetspåståenden om `void_stat`), `beslutslogg.md`.
    Ändrar inte `config.py` (D-015:s val står kvar) eller D-013/D-014/D-018:s redan körda
    resultat.

---

## D-016 (FÖRSLAG) — Whitening som korpus-beroende val via en inneboende egenskap (ej mot facit)

- **Datum:** 2026-07-16
- **Kategori:** Metod / embedding-förbehandling (bygger på D-007, D-014, D-015)
- **Fråga:** D-014 visade att whitening är korpus-beroende (hjälper C3, skadar C1-sektion/
  C2-dokument), så det låses inte globalt (D-015). Men det är beräkningsmässigt trivialt
  (kovarians + egenvärdesuppdelning per korpus; anisotropi-måttet finns i D-007). Kan whitening
  aktiveras per korpus via en regel som beror på en inneboende korpusegenskap — inte på
  leave-one-out-facit, vilket vore overfitting?
- **Steg 0 (blockerande mekanism-analys, ren geometri, ingen kostnad):** över de 12
  D-014-fallen, korrelera whitening-vinsten (rå rank/N − whitenad rank/N) mot tre
  kandidat-prediktorer: (a) inneboende anisotropi/distance-concentration (D-007-måttet), (b)
  korpus-N, (c) borttagningsandel. Rapportera vilken egenskap som faktiskt förutsäger vinsten.
  STOPPA och visa resultatet innan någon regel formuleras.
- **Beslut (villkorat av Steg 0):** om en inneboende egenskap (troligen anisotropi eller N) rent
  förutsäger vinsten → pre-registrera en regel: applicera whitening om och endast om den
  egenskapen överstiger en tröskel θ. Egenskapen mäts enbart på korpusens egna embeddings —
  inget borttaget innehåll, ingen ground truth. Om ingen inneboende egenskap rent förutsäger
  vinsten → whitening förblir ett manuellt, fall-för-fall dokumenterat beslut, ingen automatisk
  regel.
- **Tröskel θ:** provisorisk, kalibrerad på endast tre dev-korpusar → explicit flaggad som svag,
  ej bevisat optimal, valideras out-of-sample på nästa nya korpus.
- **Läckage-skydd:** whitening-transformen re-fittas alltid på det behållna innehållet i varje
  leave-one-out-diagnostik (D-014-fixen), aldrig på hela korpusen.
- **Eftersom det är billigt:** räkna och rapportera BÅDE rått och whitenat per korpus i
  diagnostiken; produktion använder den som regeln väljer, aldrig den som råkar ge bäst
  leave-one-out (det vore omval mot facit).
- **Förbjudet:** sätta/justera θ utifrån vilken tröskel som ger bäst leave-one-out; välja
  whitening per korpus genom att titta på facit.
- **Beslutat av:** Vincent.
- **Påverkar:** `analysis/gap_methods.py`, `config.py`, `beslutslogg.md`. Ändrar inte
  D-013/D-014/D-015.
- **STATUS:** ~~FÖRSLAG~~ → **RESOLVED 2026-07-16** (se notering nedan).

- **RESOLVED (2026-07-16): ingen automatisk whitening-regel; mekanism öppen p.g.a. konfundering**
  - **Steg 0-facit:** över de 12 D-014-fallen korrelerar whitening-vinsten lika starkt med
    anisotropi (D-007) som med korpus-N (båda Pearson r=+0,774, p=0,003) — de är empiriskt
    oskiljbara, eftersom de tre korpusarna rangordnas identiskt i båda. Borttagningsandel: svag,
    icke-signifikant (r=0,27, p=0,40).
  - **Beslut:** D-016:s kontingens "ingen inneboende egenskap förutsäger rent" gäller → ingen
    automatisk whitening-regel införs. Whitening förblir utanför standardpipelinen (D-015). Det
    behålls som ett dokumenterat, korpus-beroende fynd (starkast på C3), men aktiveras aldrig
    via en tröskel förrän mekanismen är löst.
  - **Teoretisk not (hypotes, ej datastödd här):** whitening är mekanistiskt en
    anti-anisotropi-operation, så anisotropin är den a priori mer troliga drivkraften — men data
    kan inte skilja den från N i detta dataset.
  - **Villkor för att återöppna:** en framtida korpus som bryter anisotropi–N-konfunderingen (hög
    anisotropi + litet N, eller låg anisotropi + stort N). Först då kan Steg 0 köras om
    meningsfullt och en regel eventuellt pre-registreras.
  - **Förbjudet:** att i efterhand välja anisotropi eller N som "drivkraften" utan
    konfund-brytande data.
  - **Påverkar:** `beslutslogg.md`. Ändrar inte D-013/D-014/D-015.

---

## D-017 (FÖRSLAG) — Robusthetskontroll av C2/C3:s fasövergångar innan någon temperatur låses

- **Datum:** 2026-07-16
- **Kategori:** Metod / Validering (bygger på D-002, Steg 0.5.8)
- **Fråga:** C2 och C3 flaggade fasövergångar (D-002) där C1 inte gjorde det, men (a) hela
  temperatursvepet rör avståndet bara ~0,05–0,15, (b) de två modellerna är oense om övergångens
  läge, (c) varje temperaturpunkt är n=3 regioner. Är övergångarna verkliga eller brus i en
  nästan platt kurva som utlöser ett relativt kriterium?
- **Beslut:** Innan någon temperatur låses för Fas 3, kör en robusthetskontroll (ren geometri,
  ingen ny API-kostnad — återanvänd de sparade genereringarna): (1) jämför den flaggade
  andraderivat-bulan mot region-till-region-standardavvikelsen per temperatur; (2) bootstrappa
  de tre regionerna och kontrollera om samma temperaturer flaggas stabilt; (3) rapportera
  effektstorleken (max−min medelavstånd) mot bruset. STOPPA och rapportera.
- **Kontingens:** om övergångarna INTE överlever bruset → slutsats "temperatureffekten är
  försumbar över alla tre korpusar; fast fallback 0,2/0,5/0,9 för alla", plus en metodnotering
  att D-002 är brus-känsligt på platta kurvor. Om de ÖVERLEVER → först då formuleras en separat
  regel för hur två modellers kandidater förenas (eget D-beslut).
- **Förbjudet:** låsa en temperatur från en övergång som inte klarat robusthetskontrollen; slå
  ihop två modellers kandidater innan signalen bekräftats.
- **Beslutat av:** Vincent.
- **Påverkar:** `beslutslogg.md`, ev. `config.py` (temperaturer). Avslutar Steg 0.5.
- **STATUS:** ~~FÖRSLAG~~ → **RESOLVED 2026-07-16** (se notering nedan).

- **RESOLVED (2026-07-16): C2/C3:s fasövergångar överlever INTE robusthetskontrollen — fast
  fallback låses för alla tre korpusar**
  - **Facit:** bootstrap-stabilitet för de D-002-flaggade temperaturerna når högst 70 % (C2
    Anthropic T=1,0) och ligger i övrigt i 23–60 %-intervallet — en verklig fasövergång
    förväntas flaggas stabilt i >90 % av omsamplingarna, inte i en minoritet till knapp
    majoritet av dem. Effekt/brus-kvoten (max−min medelavstånd över hela svepet, delat på
    genomsnittligt region-brus) är **≤1 i tre av fyra fall** (C2 Anthropic 0,94, C2 OpenAI 0,60,
    C3 OpenAI 0,42; enda undantaget C3 Anthropic på 1,29) — hela temperatursvepets rörelse är av
    samma storleksordning som eller mindre än bruset vid en enda punkt.
  - **Beslut:** Kontingensen "överlever inte bruset" gäller. **Fast fallback 0,2/0,5/0,9 låses
    för Fas 3 på alla tre korpusar** (C1, C2, C3) — inte bara C1 (som redan hade fallback via
    D-002:s egen regel), utan nu även C2 och C3, vars D-002-flaggade övergångar underkänns av
    robusthetskontrollen.
  - **Substantivt fynd:** temperatur har en **försumbar effekt på svar↔käll-avståndet över alla
    tre korpusar** i den här pipelinen, inom det testade intervallet (0,0–1,0) och med den
    testade pilotstorleken (3 regioner × 2 modeller). Detta rapporteras som ett eget resultat,
    inte bara en null-notering — det är relevant för hur mycket vikt temperaturvalet ska ges i
    Fas 3-tolkningen.
  - **Metodnotering (D-002 skrivs inte om, kompletteras):** D-002:s andraderivat-kriterium är
    **brus-känsligt på nästan platta kurvor** — ett rent relativt kriterium (andraderivata > 2×
    median|andraderivata|) kan flagga "toppar" i vad som i praktiken är brus, eftersom
    tröskeln skalas mot kurvans EGEN (låga) variansnivå snarare än mot en absolut
    signal-styrka. D-017 inför därför ett **robusthetskrav (bootstrap-stabilitet +
    effekt/brus-kvot) OVANPÅ D-002** som ett obligatoriskt efterföljande steg, utan att ändra
    D-002:s ursprungliga kriterium eller text.
  - **Påverkar:** `config.py` (`phase2_locked_temperatures` för C2 och C3), `beslutslogg.md`.
    Ändrar inte D-002:s text eller D-006/D-011/D-013/D-014/D-015/D-016:s resultat.

---

## D-018 (FÖRSLAG) — Andra-rundas bakeoff: void-familj-metoder mot void_stat, pre-registrerat

- **Datum:** 2026-07-16
- **Kategori:** Metod / gap-detektion (bygger på D-013, D-015)
- **Fråga:** void_stat blev D-015:s låsta standard på värsta-fall-kriteriet, men dess golv var
  måttligt (~topp 20 %). Finns det en metod i samma "tomrums"-familj som slår den robust över
  alla tre korpusar — utan att återöppna "lägg-till-metoder-tills-en-vinner"-fällan?
- **Metodkandidater (LÅST lista, ingen femte i efterhand, jfr D-004):**
  1. `void_stat` (regerande standard, baslinjen att slå).
  2. Watershed-/Voronoi-basin void-finder (ZOBOV/VIDE-stil, tessellerings-baserad, form-fri).
  3. Voronoi cell-volym-densitet (högdim-variant, CVDE).
  4. Distance-to-measure (DTM), brus-robust tomrumsmått.
  - **Fast övrigt (isolerar metod-axeln):** rått minilm + sqrt-k (D-015:s frysta config).
    Embedding och k återöppnas INTE — annars konfunderas metod-jämförelsen.
- **Utvärdering (låst):** graderat rank/N (D-011) som primärt mått, samma redan etablerade
  borttagningsmål (dokument + sektion per korpus), alla tre korpusar. Binärt facit rapporteras
  för fullständighet. Ren geometri, ingen LLM-kostnad.
- **Vinnarkriterium (låst, incumbent-fördel):** en utmanare ersätter `void_stat` som global
  standard ENDAST om den slår `void_stat`s värsta-fall-rank/N (D-015-kriteriet) på ALLA tre
  korpusar OCH överlever leave-one-corpus-out. Oavgjort eller marginellt → `void_stat` står
  kvar (regerande mästare byts inte på svaga skäl).
- **Overfitting-skydd:** låst kandidatlista; leave-one-corpus-out; alla metoder rapporteras på
  alla korpusar oavsett utfall; det verkliga out-of-sample-testet är en framtida ny korpus, inte
  de tre befintliga; avtagande avkastning uttryckligen erkänd (`void_stat`s tak var top 20 % —
  en utmanare väntas förbättra marginellt, inte transformera).
- **Om en metod inte kan implementeras rent i 384 dim** (t.ex. Voronoi kollapsar): den droppas
  och rapporteras som oduglig, aldrig tyst ersatt.
- **Förbjudet:** lägga till en metod efter att ha sett resultat; byta standard till en utmanare
  som inte slår `void_stat` på både värsta-fall och leave-one-corpus-out; justera embedding/k
  för att gynna en utmanare.
- **Beslutat av:** Vincent.
- **Påverkar:** `analysis/gap_methods.py`, ev. `config.py` (om standarden byts),
  `beslutslogg.md`. Ändrar inte D-013/D-015:s redan körda resultat.
- **STATUS:** ~~FÖRSLAG~~ → **GENOMFÖRD 2026-07-16.**

- **Utfall:** bakeoffen kördes (rått MiniLM, sqrt-k, D-015:s frysta config; alla sex redan
  etablerade borttagningsmål — dokument + sektion per korpus). Ingen utmanare uppfyllde
  incumbent-kriteriet:
  - Watershed-/Voronoi-basin (kandidat 2): **oduglig i 384 dim** — droppad, exakt
    Voronoi-tessellering kombinatoriskt intraktabel bortom ~10-20 dimensioner.
  - `cvde` (kandidat 3): implementerad men **rank-degenererad** mot baseline:s lokala
    komponent (bevisat identisk rangordning som rått k:e-NN-avstånd); slog inte `void_stat` på
    alla tre korpusar (globalt värsta-fall 0,9268 mot `void_stat`s 0,8773).
  - `dtm` (kandidat 4): genuint distinkt signal, men slog inte heller `void_stat` på alla tre
    korpusar (globalt värsta-fall 0,8990).
  - **`void_stat` + rått MiniLM + sqrt-k kvarstår som global standard** (D-015 oförändrad).
    Se även korrigeringsnoteringen under D-015 (2026-07-16) — `void_stat`s verkliga globala
    värsta-fall är 0,877 (C3, dokumentnivå), inte den ursprungliga sektionsnivå-baserade
    siffran ~0,196.
- **Påverkar:** `analysis/gap_methods.py` (implementationerna kvarstår), `beslutslogg.md`.
  Footer-sammanfattningen längst ner i filen speglade redan detta utfall — orörd här.

---

## D-019 (FÖRSLAG) — Fas 3-förberedelse: Nivå 2-dry-run, Nivå 1-verifiering, två-modell-poolningsregel, liten C1-effektstorlekssond

- **Datum:** 2026-07-16
- **Kategori:** Metod / Fas 3-förberedelse (bygger på D-001, D-015, D-017)
- **Fråga:** Innan betald full Fas 3 körs: delar av silningskedjan (Nivå 1/2) har aldrig
  exekverats, två-modell-poolningen är ospecificerad, och detektionens effektstorlek är okänd.
  Vad måste preciseras/valideras billigt först?
- **Beslut:** Fyra delsteg, STOPPA efter varje. Inget av dem är full Fas 3.
  - **A — Nivå 2-domaren byggs och dry-runnas mot sina egna kalibreringsexempel.** Bygg den
    LLM-anropande trivialitetsdomar-logiken (D-001 Lager 2; hittills finns bara
    kalibreringsexempel). Kör den mot `CALIBRATION_EXAMPLES_C{1,2,3}` och kontrollera att den
    klassar de kända trivial/icke-trivial-fallen korrekt. **Framgångskriterium (låst):**
    domaren måste klassa sina egna kalibreringsexempel rätt för att gå vidare; klarar den inte
    det → STOPP, domaren förbättras innan Fas 3. Litet, avgränsat antal LLM-anrop.
    - **PRECISERING (2026-07-16):** dry-runnet ska köras mot BÅDE kalibreringsexemplen OCH en
      handfull UTELÄMNADE exempel — nya instanser av samma failure-modes (mellanmjölk,
      generisk floskel, överdrivet självsäkert, allmänt känd branschkunskap, icke-trivialt
      kontrastfall), men INTE de exempel som ligger i domarens few-shot-prompt. Test enbart mot
      de egna exemplen är cirkulärt (de finns redan i prompten domaren dömer utifrån).
      **Framgångskriteriet gäller de utelämnade fallen**, inte kalibreringsexemplen (som
      domaren trivialt bör klara eftersom de är del av dess egen instruktion).
  - **B — Nivå 1-verifiering.** Bekräfta att den breda korpussökningen är implementerad och att
    D-003/D-010-tröskeln beter sig rimligt på några testpåståenden. Notera uttryckligen:
    tröskeln byggde på ett proxy-mellanmjölksankare; omkalibrering när riktiga ankare finns
    (efter generering) är ett framtida dokumenterat beslut, aldrig en tyst justering.
  - **C — Två-modell-poolningsregel (LÅST innan någon Fas 3-jämförelse).** Byggspecen skrevs
    före "haiku + gpt-4o-mini parallellt"-designen. Pre-registrera: äkthetsandelen beräknas per
    kohort (gles vs slump) över de poolade påståendena från BÅDA modellerna som primärt mått,
    OCH rapporteras per modell separat som robusthetskontroll. Ingen efterhands-hopslagning.
    - **SKÄRPNING (2026-07-16) — analysenhet är REGIONEN, inte påståendet:** varje region ger
      6 korrelerade påståenden (3 temperaturer × 2 modeller) — att poola på påstående-nivå vore
      pseudo-replikation (n uppblåst 6×, korrelerade observationer räknade som oberoende).
      Poolningsregeln preciseras till:
      1. Per region, beräkna en **äkthetsandel** = andelen av regionens (upp till 6)
         påståenden som överlever Nivå 1+2 som icke-triviala.
      2. Jämför gles- mot slumpkohort **på region-nivå** — n = antal regioner per kohort, inte
         antal påståenden.
      3. Modell och temperatur poolas IN i region-måttet (steg 1); per-modell äkthetsandel
         rapporteras separat som robusthetskontroll, exakt som redan beslutat ovan.
      **Konsekvens för delsteg D:** sonden dimensioneras därmed i **antal regioner**, inte
      antal påståenden — regionantalet är den faktiska analysenheten vars storlek Claude Code
      föreslår och Vincent låser.
  - **D — Liten C1-effektstorlekssond.** Minimal Fas 3 endast på C1: ett i förväg fastställt
    antal glesa regioner (`void_stat`, D-015) + lika stor slumpkohort, de tre fasta
    temperaturerna (0,2/0,5/0,9, D-017), båda modeller, genom Nivå 0–1–2. Syfte: uppskatta
    effektstorleken (skillnad i äkthetsandel gles−slump), INTE ett hypotestest.
    Uppskalningsregel (låst INNAN sonden körs): vilken uppskattad separation som motiverar full
    Fas 3 på C1–C3 bestäms och skrivs ner före körning. Sondens p-värde används ALDRIG som
    resultat — bara för att dimensionera den riktiga körningen. Sondstorleken fastställs innan
    körning (Claude Code föreslår, Vincent låser).
    - **LÅSTA SONDPARAMETRAR (2026-07-16):**
      - **Sondstorlek:** 20 glesa regioner (`void_stat`, D-015, sqrt-k) + 20 slumpmässiga
        regioner på C1, disjunkta från de sparade pilotregionerna. Tre fasta temperaturer
        (0,2/0,5/0,9, D-017), båda modellerna (haiku + gpt-4o-mini). Varje region körs genom
        Nivå 0→1→2.
      - **Mått:** äkthetsandel per region (D-019 delsteg C:s skärpning — andel av regionens
        påståenden som överlever Nivå 1+2 som icke-triviala). Rapportera: medel-äkthetsandel
        för gles vs. slump, skillnaden d̂, och 95 % CI på skillnaden. Per-modell äkthetsandel
        separat som robusthetskontroll. Spara domarens motiveringar per påstående för
        kvalitativ spot-check.
      - **Uppskalningsregel, tre grenar (låsta här, innan sonden körs):**
        1. d̂ tydligt positiv med undre CI-gräns > 0 → dimensionera full Fas 3 för 80 % styrka
           vid d̂; kör om inom budgettaket.
        2. d̂ positiv men liten / CI täcker 0 → beräkna nödvändig n; kör om inom taket, annars
           dokumentera "underpowered inom budget, D-001 uppskjuten".
        3. d̂ ≤ 0 → gleshet slår inte slump ens på bäst-detekterande korpus → starkt negativt,
           skriv upp, skala inte.
      - **Budgettak för full Fas 3:** sätts av Vincent och låses INNAN uppskalningsbeslutet,
        helst innan d̂ ses.
      - **Förbjudet:** använda sondens p-värde som resultat (bara d̂ + CI för dimensionering);
        ändra sondstorleken efter påbörjad körning; höja budgettaket efter att d̂ setts för att
        rättfärdiga fortsättning.
  - **Två småkontroller:** (i) produktionsregionerna är disjunkta från de sparade
    pilotregionerna; (ii) retrieval använder sqrt-k (D-015).
- **Förbjudet:** gå till full Fas 3 innan Nivå 2-domaren klarat sitt dry-run; välja
  poolningsregeln efter att ha sett resultat; använda sondens p-värde som utfall; ändra
  sondstorleken efter påbörjad körning.
- **Beslutat av:** Vincent.
- **Påverkar:** `analysis/domain_adapter.py` (Nivå 2-logik), `analysis/gap_verification.py`
  (Nivå 1), `analysis/rag_runner.py` (sond), `config.py`, `beslutslogg.md`.
- **STATUS: FÖRSLAG.** Inget byggt eller kört. Delsteg A och D kostar LLM-anrop — väntar på
  Vincents bekräftelse av delstegen innan genomförande.

---

## D-020 — Längdnormalisering för Nivå 1 (H3, äntligen löst) + parse_error-fix, innan sonden körs om

- **Datum:** 2026-07-18
- **Kategori:** Metod / bugfix (bygger på D-003/D-010, adresserar H3 i
  `negative_space_open_problems_v1_0.md`)
- **Fråga:** D-019 delsteg D:s första sondkörning (2026-07-16, se `.cache/d019_probe_result.json`)
  gav en degenererad sanity-check: Nivå 1 flaggade 97,9 % av de 240 genererade påståendena som
  "redan täckt" (median similaritet 0,472, långt över tröskeln 0,357 — inte ett gränsfall), och
  Nivå 2 gav 25 % `parse_error`. Två separata orsaker identifierade:
  1. **Nivå 1:** samma längd/format-confound som redan flaggades i
     `lardomar_iteration1_till_negative_space.md` §0 och H3 (aldrig löst, "STATUS: öppet") —
     långa, syntetiserande LLM-genererade scenarier (flera meningar) jämförs mot en tröskel
     kalibrerad på korta korpuschunkar (~400 tecken, D-003:s ankarpar). Längre text får
     systematiskt högre cosine-similarity mot NÅGON korpuschunk oavsett genuin nyhet.
  2. **Nivå 2:** `classify_scenario()`s `max_tokens=200`-default var för snålt tilltaget för
     domarens fulla resonemang — svaret klipptes av mitt i `rationale`-fältet innan avslutande
     `}`, vilket gjorde JSON ogiltig. Ren implementationsbugg, inget metodval, aldrig
     pre-registrerad som ett låst värde.
- **Beslut:**
  1. **H3 löst:** innan ett genererat påstående skickas till Nivå 1-sökningen, trunkeras det
     till `CHUNK_SIZE_DEFAULT` tecken (400, samma längd som D-003:s ankarpar byggdes på) INNAN
     embedding. Detta återställer längdjämförbarhet med den kalibrerade tröskeln utan att
     kräva en ny, dyrare ankarprocedur. Explicit regel, låst innan sonden körs om.
  2. **parse_error-fix:** `classify_scenario()`s `max_tokens` höjs till 500. Ren bugfix, ändrar
     inget låst värde eller D-003/D-010:s tröskel.
- **Explicit avgränsning:** H3-fixen ändrar HUR text förbereds inför Nivå 1-jämförelsen, INTE
  D-003/D-010:s kalibrerade tröskelvärde (0,357 för C1) — tröskeln står kvar orörd, bara
  jämförelseobjektets längd normaliseras till samma skala som ankarna.
- **Förbjudet:** justera trunkeringslängden i efterhand baserat på hur många påståenden som
  passerar Nivå 1 efter fixen; välja ett annat värde än `CHUNK_SIZE_DEFAULT` utan ny motivering.
- **Beslutat av:** Vincent (via bekräftat AskUserQuestion-val "Fixa båda, kör om hela sonden").
- **Påverkar:** `analysis/gap_verification.py` (`search_corpus_for_coverage` — trunkering
  innan embedding), `analysis/domain_adapter.py` (`classify_scenario` — `max_tokens`),
  `beslutslogg.md`. Ändrar inte D-003/D-010:s tröskelvärden eller D-019 delsteg A/B/C:s
  redan godkända resultat.
- **STATUS: GENOMFÖRD 2026-07-18.** Kodändringarna implementerade; sonden (D-019 delsteg D)
  körs om härnäst med samma 40 regioner/parametrar som redan låstes 2026-07-16.

- **UPPFÖLJNINGSNOTERING (2026-07-18) — trunkeringsfixen var otillräcklig:** sonden kördes om
  med båda D-020-fixarna. `parse_error` gick till 0/240 (bekräftat löst). Men Nivå 1:s
  genomsläpp förblev degenererat: 97,5% already_covered (var 97,9% innan fixen) —
  statistiskt oförändrat. Rotorsaksdiagnosen (längd/format) var alltså FEL eller ofullständig.
  Direkt test (30 slumpmässiga äkta korpuschunkar): parvis similaritet mot en slumpmässig
  annan chunk medel=0,242, men MAX-similaritet mot resten av korpusen (2938 kandidater)
  medel=0,751 — tröskeln kalibrerades på fel statistik (pairwise), Nivå 1 gör i praktiken en
  max-över-N-sökning. Se D-021 för den föreslagna åtgärden. D-020:s trunkering behålls (gjorde
  ingen skada, löste parse_error) men var inte huvudorsaken.

---

## D-021 (FÖRSLAG) — Omkalibrera Nivå 1-tröskeln på claim-mot-chunk-ankare (H3)

- **Datum:** 2026-07-18
- **Kategori:** Metod / kalibrering (bygger på D-003/D-010/D-020, adresserar H3)
- **Fråga:** D-019-sonden visade Nivå 1 filtrerar ~98 % som "redan täckt"; D-020:s trunkering
  räckte inte (trunkerad claim fortfarande 0,432 > 0,357). Rotorsak: tröskeln (D-003/D-010)
  kalibrerades på chunk-mot-chunk-par, men ett genererat lucka-påstående är genererat FRÅN
  källchunkarna, handlar om samma ämne och använder samma vokabulär → claim-mot-chunk-likhet
  har en högre baslinje, och "samma ämne" förväxlas med "samma innehåll" (H3, öppet sedan
  lärdomsdokumentet).
- **Beslut:** Kalibrera om Nivå 1-tröskeln på rätt textklass — claim-mot-chunk-par: en
  fördelning av kända "täckta" påståenden (om innehåll som FAKTISKT står i korpusen) mot kända
  "nya/otäckta" påståenden (om genuint frånvarande innehåll). Tröskeln sätts mellan de två,
  samma ankar-logik som D-003 men med claim-chunk-par. D-020:s trunkering behålls (rimlig
  oavsett), men räcker inte ensam.
- **Ankar-konstruktion:** Claude Code föreslår hur "täckta" och "nya" claim-ankare tas fram
  (med särskild noggrannhet mot cirkularitet/läckage — t.ex. "täckta" = parafraser av
  befintligt chunk-innehåll; "nya" = de utelämnade icke-triviala kontrastexemplen från D-019 A)
  och STOPPAR för Vincents låsning innan omkalibrering.
- **Validering:** efter omkalibrering, kontrollera att Nivå 1-genomsläppet på sonddata ligger
  i ett vettigt mellanläge innan d̂ beräknas.
- **Förbjudet:** sätta tröskeln utifrån vilket värde som ger önskat d̂; tolka d̂ på degenererat
  Nivå 1.
- **Beslutat av:** Vincent.
- **Påverkar:** `analysis/gap_verification.py`, `config.py` (Nivå 1-tröskeln blir
  claim-chunk-kalibrerad), `beslutslogg.md`. Ändrar inte D-003/D-010:s chunk-chunk-kalibrering
  i efterhand — kompletterar den för claim-jämförelser.
- **STATUS: FÖRSLAG.** Ingen ankar-konstruktion föreslagen ännu, ingen omkalibrering körd.
  Väntar på att Claude Code lägger fram ett förslag till ankar-konstruktion, som Vincent sedan
  granskar och låser innan genomförande.

- **SKÄRPNING (2026-07-18) — rotorsaken är TVÅ separata felmatchningar, inte en:** "annan
  textklass" i frågan ovan är ofullständig som förklaring. Den belagda rotorsaken (se
  uppföljningsnoteringen under D-020) är en **statistisk felmatchning**: tröskeln kalibrerades
  mot PARVIS chunk-chunk-likhet (medel ~0,24), men Nivå 1 använder MAX över ~2900 chunkar
  (medel ~0,75 för äkta korpusinnehåll) — en ~3× order-statistik-inflation som är oberoende av
  vilken TEXTKLASS som jämförs. Omkalibreringen måste därför rätta BÅDA felen samtidigt:
  1. **Rätt statistik:** ankarnas likhetsvärden ska mätas som MAX-över-hela-korpusen, exakt
     den operation Nivå 1 faktiskt utför vid körning — inte som ett enda parvis värde.
  2. **Rätt textklass:** ankarna ska vara claim-stil (genererade lucka-påståenden), inte
     chunk-par. Ett äkta korpuschunk matchar dessutom sin egen överlappande
     glidfönster-granne (D-009:s `_chunk()`, `CHUNK_OVERLAP_DEFAULT=50`) på ~0,9 — ett sådant
     par är alltså INTE ett giltigt "täckt"-ankare (cirkulärt: hög likhet av
     konstruktionsskäl, inte av substansskäl).
- **OBLIGATORISK SEPARATIONS-GATE (låst här, före någon tröskel sätts):** innan ett
  tröskelvärde beräknas, mät om "täckta" och "nya" claim-ankarnas MAX-likhetsfördelningar
  (mot hela korpusen, punkt 1 ovan) faktiskt separerar från varandra.
  - Om fördelningarna **överlappar kraftigt** → max-cosine-sökning är fel operationalisering
    för "redan täckt" på denna textklass (domän-vokabulären dränker den specifika
    täckningssignalen). Ingen tröskel sätts. Nivå 1 behöver då en annan mekanism (t.ex.
    NLI/entailment: "medför någon chunk claimens SPECIFIKA påstående?", inte bara tematisk
    likhet) — det är ett eget, större D-beslut, inte en kalibreringsjustering.
  - **Förbjudet, explicit:** att sätta en tröskel på icke-separerande fördelningar bara för
    att få igenom fler påståenden i sonden. Separations-gaten går före leveranstryck.
- **Påverkar (oförändrat):** `analysis/gap_verification.py`, `config.py`, `beslutslogg.md`.

- **Separations-gate-resultat (2026-07-18):** täckta ankare median=0,449, nya ankare
  median=0,376. Mann-Whitney p=0,00125 (statistiskt signifikant riktning), men **AUC=0,728**
  och tungt rått överlapp (23/30 täckta inom nya-intervallet, 26/30 nya inom
  täckta-intervallet). Gränsfall — varken ren separation eller totalt sammanbrott. Ingen
  tröskel satt. Se D-022 för vald fortsättning (eskalering till cross-encoder, inte en
  midpunkt-tröskel på detta överlapp).

---

## D-022 (FÖRSLAG) — Byt Nivå 1:s bi-encoder max-cosine mot en cross-encoder/reranker

- **Datum:** 2026-07-18
- **Kategori:** Metod / Nivå 1-arkitektur (bygger på D-003/D-010/D-021)
- **Fråga:** D-021:s gate: max-cosine diskriminerar inte täckta från nya claims tillräckligt
  (AUC 0,728, ~80 % överlapp, medianer 0,07 isär). Rotorsak: bi-encoder cosine mäter
  ämnes-likhet, inte om en chunk täcker claimens specifika påstående.
- **Beslut:** Byt Nivå 1:s scoring till en lokal cross-encoder/reranker som poängsätter
  (claim, chunk)-par direkt. Ingen API-kostnad per anrop. Nivå 1 = max cross-encoder-score
  över korpusen (grovsålla topp-k kandidater med cosine för hastighet, rerankera dem).
- **Valideringsgate (låst):** revalidera mot SAMMA D-021-ankare (30 täckta, 30 nya).
  Cross-encodern måste nå **AUC ≥ 0,85** för att litas på; annars är den otillräcklig →
  eskalera (LLM-entailment, med dess kostnad, eller ompröva Nivå 1).
- **Tröskel** sätts först efter passerad validering, på cross-encoder-score-fördelningarna
  (samma midpunkt-logik).
- **Förbjudet:** sätta tröskel före passerad AUC-validering; tolka sond-d̂ på en Nivå 1 som
  inte klarat AUC-målet.
- **Beslutat av:** Vincent.
- **Påverkar:** `analysis/gap_verification.py`, `config.py`, `requirements.txt`
  (cross-encoder), `beslutslogg.md`. Kompletterar D-021 (som visade att bi-encodern är
  otillräcklig).
- **STATUS:** ~~FÖRSLAG~~ → **GATE EJ KLARAD, 2026-07-18.**

- **Resultat:** `cross-encoder/nli-deberta-v3-base` validerad mot samma 30 täckta + 30 nya
  D-021-ankare (topp-20 cosine-grovsåll, rerankerad, max entailment-sannolikhet). Täckta
  median=0,298, nya median=0,178 — **AUC=0,579** (SÄMRE än bi-encoderns 0,728), Mann-Whitney
  p=0,149 (ej signifikant). 26/30 täckta och 29/30 nya i det gemensamma överlappet.
  **Gaten (AUC≥0,85) klarades inte.** Ingen tröskel satt, ingen sond körd.
- **Trolig förklaring (ej datastödd, för framtida referens):** NLI-modeller tränas på korta,
  direkta premiss/hypotes-par. Våra "hypoteser" är FRÅNVARO-påståenden ("X adresseras INTE")
  — en atypisk uppgift för entailment, som avgör om premissen STÖDJER hypotesen, inte om den
  bekräftar en frånvaro. Möjlig strukturell mismatch, inte nödvändigtvis ett dödsslag för
  cross-encoder-idén i allmänhet.
- **Påverkar:** `beslutslogg.md`. Se D-023 för eskalering enligt D-022:s egen kontingensklausul.

---

## D-023 (FÖRSLAG) — Nivå 1 blir en LLM-täckningsdomare (embedding-metoder uttömda)

- **Datum:** 2026-07-16
- **Kategori:** Metod / Nivå 1 (eskalering per D-022:s klausul)
- **Fråga:** D-021 (bi-encoder, AUC 0,728) och D-022 (cross-encoder, AUC 0,579) klarade inte
  separations-gaten. "Är den specifika luckan täckt?" kräver läsförståelse, inte vektor-likhet
  — ämnes-signalen dränker innehålls-signalen oavsett avståndsmått.
- **Beslut:** Nivå 1 blir en LLM-täckningsdomare, samma struktur som den fungerande Nivå 2.
  Input: claimen + de topp-k mest relevanta chunkarna (cosine som grov kandidat-hämtning;
  ±2-fönster runt claimens källregion exkluderat, per D-021:s konsistens-fix). Output:
  "täckt / ej täckt" + konfidens (0–1) + motivering, temperature=0.
- **Förbättrad ankar-design (rättar D-021:s stil-missmatch):** validera mot ankare i SAMMA
  absens-format som de riktiga påståendena:
  - "Täckta" ankare = **falska gap-påståenden**: "korpusen adresserar inte X" där X FAKTISKT
    står i korpusen → domaren ska svara "täckt".
  - "Nya" ankare = **äkta gap-påståenden**: "korpusen adresserar inte X" där X genuint saknas
    → domaren ska svara "ej täckt".
  - Båda i samma stil, skiljer sig bara i faktisk täckningsstatus — fixar samtidigt att
    D-021:s täckta ankare (summeringar) hade fel register.
- **Valideringsgate (låst):** AUC ≥ 0,85 (eller balanserad träffsäkerhet ≥ 0,85 om bara
  etiketter) mot de nya ankarna. **Caveat dokumenteras:** ankarvalidering är nödvändig men
  LÄTT för en LLM på rena konstruerade fall — att passera är nödvändigt, inte tillräckligt
  bevis för riktiga, stökiga claims. Det verkliga provet är sonden + kvalitativ granskning av
  motiveringarna.
- **Kostnad:** ~1 LLM-anrop/claim (som Nivå 2). Validering 60 ankare, sond-omkörning 240 —
  överkomligt.
- **Kontingens:** klarar inte ens LLM-domaren gaten → "redan täckt" är inte pålitligt
  operationaliserbart i denna pipeline → kliv tillbaka, skriv upp lärdomarna, ingen femte
  mekanism byggs.
- **Scope-observation (noteras, inget nytt beslut):** med Nivå 1 som LLM-domare krymper
  geometrins roll till Nivå 0:s grova regionval. "Geometri hittar luckor"-tesen smalnar till
  "geometri föreslår regioner, LLM:er bedömer" — redovisas öppet i slutrapporten.
- **Förbjudet:** sätta tröskel/köra sond före passerad gate; behandla ankar-AUC som
  tillräckligt bevis för riktiga claims.
- **Beslutat av:** Vincent.
- **Påverkar:** `analysis/gap_verification.py`, `config.py`, `beslutslogg.md`. Kompletterar
  D-021/D-022 (embedding-metoder otillräckliga).
- **STATUS:** ~~FÖRSLAG~~ → **GATE KLARAD, 2026-07-18.**

- **Prompt-precisering (2026-07-18):** `COVERAGE_JUDGE_PROMPT_TEMPLATE` skärpt till en
  explicit tre-stegs instruktion (identifiera X → sök positivt efter X i utdragen, INTE
  entailment mot absens-påståendet → citera utdragsnummer om täckt). Motverkar direkt
  D-022:s feltolkning (att fråga om en chunk "medför" en frånvaro, vilket inte är en
  välformad fråga).
- **Valideringsresultat** (engelska, stil-matchade D-021/D-023-ankare — 30 falska gap
  [täckta] + 30 äkta gap [nya], ±2-exkluderingsfönster, `top_k=10`):

  | Mått | Värde |
  |---|---|
  | Balanserad träffsäkerhet | **0,933** |
  | Konfidensviktad AUC | **0,971** |
  | Sensitivitet (täckta korrekt) | 0,867 (26/30) |
  | Specificitet (äkta gap korrekt) | **1,000 (30/30)** — inga falska positiva |
  | parse_error | 0/60 |

  **Gaten (≥0,85) klarad med god marginal.** De 4 felklassade "täckta" fallen är alla
  samma mönster: domaren resonerar korrekt strikt om specificitet, men den exakta chunk som
  nämner den specifika frasen (t.ex. "leadership and governance", "injection safety") fanns
  inte bland de topp-10 cosine-hämtade kandidaterna — ett retrieval-djup-problem, inte ett
  domar-resonemangsfel. Korrekt klassade "täckta" fall citerar konsekvent utdragsnummer och
  konkret textstöd (spot-checkat, se `.cache/d023_judge_validation.json`).
- **Caveat kvarstår (som redan noterat ovan):** ankarvalidering är nödvändig men lätt för en
  LLM på rena konstruerade fall. Det verkliga provet är sonden på riktiga, stökiga claims —
  ej körd än.
- **Påverkar:** `analysis/gap_verification.py` (prompt uppdaterad), `beslutslogg.md`. Ingen
  tröskel satt, ingen sond körd.

- **PRE-REGISTRERAD JUSTERING (2026-07-18) — top_k höjt 10 → 30, innan omvalidering:**
  de fyra falska negativa berodde på att rätt chunk saknades i topp-10 cosine-kandidater
  (retrieval-djup), inte på domarens resonemang. `judge_coverage()`s `top_k` höjs till 30 —
  en djupare kandidatpool, inte en finjustering mot ankarnas facit (inget annat i domaren
  eller ankarna ändras). Motiverat och loggat FÖRE omvalidering, i linje med
  pre-registreringsdisciplinen.
  - **Förbjudet:** justera top_k ytterligare efter att ha sett omvalideringsresultatet.
  - **Påverkar:** `analysis/gap_verification.py` (`judge_coverage` default `top_k=30`).

---

## D-024 (FÖRSLAG) — Cross-lingual confound: svensk generering mot engelsk korpus; byt till engelska, ompröva kontaminerade steg

- **Datum:** 2026-07-18
- **Kategori:** Metod / kritisk confound (upptäckt under D-023:s ankarkonstruktion)
- **Fråga:** Genererade claims/ankare är svenska, C1 är engelsk, `all-MiniLM-L6-v2` är inte
  flerspråkig. Test: engelska ger +0,24–0,30 similaritet och rätt dokument; svenska ger fel
  dokument i 2/3 testade fall. Vad är kontaminerat och hur fixas det?
- **Kontaminerat** (similaritet svensk-genererad ↔ engelsk korpus):
  - Temperatur-piloterna (D-002/D-017, svar↔käll-avstånd → "temperatur inert" kan vara
    artefakt, MÅSTE omprövas).
  - D-019-sondens Nivå 1 (98 % täckt).
  - D-021/D-022 ankar-gates (AUC 0,728/0,579, tolkningsvärde ogiltigt — blandning av
    cross-lingual-brus och det genuina ämne-vs-innehåll-problemet).
- **INTE kontaminerat:** gap-detektionen D-004–D-018 (engelska mot engelska); Nivå 2-domaren
  (LLM-läsning). Står oförändrat.
- **Beslut:** Byt hela generings-/ankarspråket till engelska (`PROMPT_TEMPLATE`,
  domänkontext, kalibreringsexempel, alla ankare). Behåll all-MiniLM; ingen flerspråkig modell
  (skulle bryta D-015).
- **Obligatorisk revision innan omkörning:** systematisk genomgång av alla ställen där
  genererad text jämförs med korpus, och alla kalibrering-vs-query-operationer, för att fånga
  en eventuell fjärde confound innan tid läggs på omkörning.
- **Omkörning i ordning (engelska, sanity-först):** (1) revision; (2) D-021 ankar-gate; (3)
  D-023 LLM-domare; (4) sond. D-002/D-017 temperatur-omprövning: separat beslut om den ska
  köras om eller bara flaggas som ej tillförlitlig.
- **Förbjudet:** tolka kontaminerat resultat som facit; blanda språk i pipelinen.
- **Beslutat av:** Vincent.
- **Påverkar:** `analysis/rag_runner.py`, `analysis/domain_adapter.py`,
  `analysis/gap_verification.py`, ankar-filer, `config.py`, `beslutslogg.md`.
- **STATUS:** ~~FÖRSLAG~~ → **GENOMFÖRD 2026-07-18** (revision + fixar + omkörning, se
  notering nedan).

- **Obligatorisk revision (2026-07-18):** genomgång av alla ställen där genererad text
  jämförs med korpus, och alla kalibrering-vs-query-operationer. Bekräftade D-024:s egen
  kontaminationslista. **En fjärde, verklig inkonsistens hittad** (inte språk): D-021:s
  "täckta" ankare byggdes MED ett ±2-exkluderingsfönster runt källkontexten, men
  `search_corpus_for_coverage()` (funktionen som faktiskt användes i D-019:s riktiga sond)
  hade INGET exkluderingsfönster alls — ett genererat påstående kunde trivialt "hitta
  täckning" i sina EGNA källchunkar. Rättad (se nedan).
- **Fixar genomförda:**
  1. `PROMPT_TEMPLATE` (rag_runner.py), `DOMAIN_CONTEXT_C{1,2,3}`,
     `CALIBRATION_EXAMPLES_C{1,2,3}`, `HELD_OUT_EXAMPLES_C{1,2,3}`, `JUDGE_PROMPT_TEMPLATE`
     (domain_adapter.py) och `COVERAGE_JUDGE_PROMPT_TEMPLATE` (gap_verification.py) — alla
     bytta till engelska. label-värden `"trivial"/"icke-trivial"` → `"trivial"/"non-trivial"`,
     `"täckt"/"ej_täckt"` → `"covered"/"not_covered"`.
  2. `search_corpus_for_coverage()` fick en `excluded_indices`-parameter, samma
     exkluderingslogik som D-021:s ankarkalibrering, nu tillämpningsbar konsekvent.
- **Omkörning, D-021 bi-encoder-gate, engelska, STIL-OMATCHAD** (30 syntetiserande
  sammanfattningar vs. 30 absens-claims): **AUC=0,952** (mot 0,728 på svenska). Spot-check:
  ett självskade/suicid-claim toppar nu korrekt mot mhGAP:s SUI-modul (chunk 663–695) — den
  svenska sökningen hade hittat fel dokument helt.
- **Omkörning, STIL-MATCHAD** (D-023:s 30 falska gap-påståenden [täckta, absens-stil] vs. de
  30 äkta gap-påståendena [nya, absens-stil], båda engelska, ±2-fönster): **AUC=0,388,
  p=0,933 — ingen separation, riktningen till och med svagt omvänd.** 28/30 och 29/30 i det
  gemensamma överlappet.
  - **Slutsats:** det tidigare AUC=0,952 var till stor del en STIL-ARTEFAKT (syntetiserande
    sammanfattning vs. absens-påstående är lätta att skilja lexikalt, oavsett faktisk
    täckning) — inte ett genuint täckningssignal. När båda ankarmängderna tvingas till SAMMA
    textklass (absens-påståenden, den faktiska produktionsklassen), försvinner
    bi-encoderns separationsförmåga nästan helt. Detta gäller oavsett språk — engelska löste
    retrieval-kvaliteten (rätt dokument hittas) men INTE den underliggande
    täcknings-vs-icke-täckning-distinktionen inom absens-stil.
  - **Både bi-encoder (D-003/D-010/D-021) och cross-encoder (D-022) är därmed uteslutna för
    Nivå 1.** LLM-domaren (D-023) är nödvändig, inte bara ett av flera alternativ.
- **Påverkar:** `analysis/rag_runner.py`, `analysis/domain_adapter.py`,
  `analysis/gap_verification.py`, `beslutslogg.md`. Nästa steg: validera D-023:s
  `judge_coverage()` mot samma stil-matchade engelska ankare.

---

## D-025 (FÖRSLAG) — Parallellisera sond-körningen på region-nivå (körningsoptimering, ingen ändring av experimentets parametrar)

- **Datum:** 2026-07-16
- **Kategori:** Infrastruktur / körning (påverkar INTE experimentdesignen)
- **Fråga:** Sonden tar ~35–40 min sekventiellt. Kan körningen parallelliseras utan att
  påverka giltigheten?
- **Beslut:** Parallellisera på region-nivå: `ThreadPoolExecutor(max_workers=5)`, egna
  klienter per tråd, exponentiell backoff-retry mot `RateLimitError` (5 försök + jitter),
  trådsäker checkpoint-skrivning (`threading.Lock`), skip-and-resume vid regionfel.
- **Varför giltigheten inte påverkas:** regionvalet är seed-låst (2026) och bit-för-bit
  identiskt oavsett parallellisering; alla parametrar oförändrade (temperaturer D-017, båda
  modeller, exkluderingsfönster, Nivå 1-domare top_k=30 D-023, Nivå 2-domare);
  region-nivå-äkthetsmåttet (D-019 C) är ordnings-oberoende; LLM-genereringen var redan
  körning-till-körning stokastisk (temp > 0), så parallell vs sekventiell ändrar inte
  experimentets natur.
- **OBLIGATORISK fullständighets-spärr:** d̂ beräknas ALDRIG på en partiell körning. Före
  analys, verifiera att alla 40 regioner (20 gles + 20 slump) finns i checkpointen; har någon
  region misslyckats och hoppats över, återuppta tills alla 40 är klara. Rapportera antalet
  färdiga regioner explicit.
- **Förbjudet:** tolka d̂ på färre än 40 regioner; ändra någon experiment-parameter i samband
  med parallelliseringen.
- **Beslutat av:** Vincent.
- **Påverkar:** sond-skriptets körningsinfrastruktur. Ändrar inte D-015/D-017/D-019/D-023.
- **STATUS: FÖRSLAG.** Ingen betald sond körd. Fullständighets-spärren verifieras i koden
  innan genomförande.

---

*Steg 0 (byggspec Del C) genomfört: Del B (D-001) + D-002–D-009 incheckade. D-010 tillagt
2026-07-13 (Steg 0.5-genomförande). D-011 tillagt 2026-07-13 (graderat leave-one-out-mått).
D-004 RESOLVED 2026-07-13 (k blir per-korpus-parameter — facit över alla tre korpusar). D-012
tillagt 2026-07-13 (storleksskalad topp-N-brytpunktssvep). D-013 GENOMFÖRD 2026-07-15
(metod-/embedding-bakeoff, 90 kombinationer; en whitening-läcka i den första körningen
upptäcktes av Vincent, rättades i `run_bakeoff_indices` och samtliga 90 kombinationer kördes
om — korrigerat facit: oavgjort på metod-axeln, precis som ursprungligen). D-014 GENOMFÖRD
2026-07-15 (robusthetstest av whitening — 8/12, UNDER den pre-registrerade 10/12-gränsen;
whitening INTE robust bekräftat, korpus-/målberoende avvägning snarare än generell förbättring).
D-015 GENOMFÖRD 2026-07-16 (värsta-fall-kriterium för global standardkonfiguration,
void_stat+rått minilm+sqrt-k låst i config.py; sqrt-k avgör även k-valet för standardmetoden).
D-016 RESOLVED 2026-07-16 (Steg 0 kört — anisotropi och korpus-N empiriskt oskiljbara,
konfunderade över de tre korpusarna; ingen automatisk whitening-regel införs; öppnas igen bara
av en framtida korpus som bryter konfunderingen). Temperatur-piloten (Steg 0.5.8) kördes på
C2 och C3 2026-07-16 — båda modeller flaggade fasövergångar (till skillnad från C1), men
kurvorna är nästan platta och modellerna oense om läget. D-017 RESOLVED 2026-07-16
(robusthetskontroll — bootstrap-stabilitet ≤70 %, effekt/brus-kvot ≤1 i tre av fyra fall;
övergångarna överlever inte bruset; fast fallback 0,2/0,5/0,9 låst för alla tre korpusar;
substantivt fynd: temperatur har försumbar effekt på svar↔käll-avståndet i denna pipeline).
**Steg 0.5 formellt avslutat för C1, C2 och C3.** D-018 kördes 2026-07-16 (void-familj-bakeoff
mot void_stat — ingen utmanare slog void_stat på alla tre korpusar, void_stat behåller
standardplatsen; en korrigeringsnotering under D-015 preciserade att void_stats
reliabilitet gäller sektionsskala, inte dokumentskala). D-019 (FÖRSLAG) tillagt 2026-07-16
(Fas 3-förberedelse: Nivå 2-dry-run, Nivå 1-verifiering, två-modell-poolningsregel,
C1-effektstorlekssond) — delsteg A/B/C godkända, delsteg D:s dry-run och sond körda 2026-07-18.
Sonden avslöjade degenererad Nivå 1 (~98% already_covered); D-020 (max_tokens-fix + trunkering)
löste Nivå 2:s parse_error helt men INTE Nivå 1 — rotorsaken är att D-003/D-010:s tröskel
kalibrerades på pairwise chunk-chunk-similaritet medan Nivå 1 gör en max-över-N-sökning
(bekräftat: äkta korpuschunkar har pairwise-medel 0,24 men max-mot-korpus-medel 0,75). D-021
(FÖRSLAG) tillagt 2026-07-18 (omkalibrera Nivå 1-tröskeln på claim-mot-chunk-ankare, H3) — EJ
FATTAT. Ingen d̂ beräknad (degenererat Nivå 1 tolkas aldrig). Nästa steg: Claude Code föreslår
ankar-konstruktion för D-021, Vincent granskar och låser.*
