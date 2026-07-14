# RAG-kohort & lucka-i-täckning — Tillägg v4.0

> **Status: FÖRSLAG — EJ FATTAT, EJ BYGGT** (ärvt från v3.0). Detta dokument är ett
> **append-only tillägg** till `rag_kohort_preregistrering_v3.md` — Del A/B/C i v3 ändras
> INTE, de kompletteras här. Läs v3 först; detta dokument förutsätter dess terminologi
> (Lager 1/2, Nivå 0–3, Fas 1–3, mellanmjölks-fällan).
>
> **Fortsätter projektets egen D-nummerserie** (D-001 = v3:s Del B). Ingen D-numrering
> eller siffra från "Embracing the Novelty of Noise" (iteration 1) återanvänds.

-----

## D-002 — Objektivt kriterium för Fas 2:s böjningspunkt

- **Fråga:** Fas 2 (temperatur-pilotens låsning) kräver att avgöra om pilotsvepets kurva
  visar en "tydlig fasövergång." v3 lämnade detta odefinierat ("ögonmått"). Vilket
  objektivt, förutbestämt kriterium ska gälla?
- **Beslut:** Ett tröskeltest på andraderivatans storlek relativt sin egen brusnivå:
  **en fasövergång räknas som funnen om andraderivatan av svar↔käll-avståndet vid någon
  punkt i pilotsvepet överstiger 2× medianen av andraderivatans absolutvärde över hela
  svepet.** Om ingen sådan punkt finns: fallback till 0,2/0,5/0,9 gäller (oförändrat från
  v3).
- **Alternativ övervägt och avfärdat som PRIMÄR metod (kvar som möjlig framtida
  förstärkning):** formellt change-point-test (t.ex. PELT eller Bayesianskt
  brytpunktstest) med signifikansnivå **p < 0,10** (medvetet mer tillåtande än
  konventionella 0,05, eftersom pilotsvepet har begränsad statistisk styrka vid litet N —
  ett strikt 0,05-krav skulle systematiskt falla tillbaka på fasta värden även när en
  verklig, svagare övergång finns). Avfärdat som PRIMÄR metod för PoC pga extra
  beroende (bibliotek som `ruptures`) utan motsvarande vinst i denna skala; kan läggas
  till som sekundär bekräftelse om resurser tillåter.
- **Motivering:** Kriteriet är objektivt, förutbestämt, och kräver inget nytt bibliotek.
  Det jämför en observerad knyck mot svepets EGEN brusnivå snarare än mot ett godtyckligt
  absolut tal, vilket gör det robust över korpusar med olika allmän variansnivå.
- **Explicit regel, ingen tolkning i efterhand:** detta kriterium låses HÄR, innan Fas 1
  körs på någon korpus.
- **Påverkar:** Lager 2 / Fas 2 i v3, `analysis/rag_runner.py`.

## D-003 — Nivå 1:s matchningströskel: procedur, inte tal

- **Fråga:** Nivå 1 ("sök hela C — verkligen frånvarande?") saknade i v3 en definierad
  numerisk tröskel för "redan substantivt täckt." Vilket värde, eller vilken procedur,
  ska gälla?
- **Beslut:** Ingen universell siffra låses. I stället låses en **kalibreringsprocedur**,
  analog med iteration 1:s θ_absens/θ_match-metod: vid instans-kalibrering (Steg 0.5) för
  varje korpus, mät faktiska cosine-likheter för (a) kända relaterade textpar inom
  korpusen, (b) kända orelaterade textpar, (c) om möjligt "mellanmjölks"-liknande par.
  Sätt Nivå 1-tröskeln relativt dessa ankare (t.ex. strax under den observerade
  medel-likheten för kända relaterade par), enligt samma logik som θ_match i iteration 1
  (midpunkt mellan känd-relaterad-medel och mellanmjölks-medel).
- **Motivering:** En universell siffra skulle vara meningslös över korpusar med olika
  embedding-geometri (samma lärdom som θ-låsningen i iteration 1, D-017 där). Proceduren
  är domänagnostisk; talet är det inte, och ska inte förväntas vara det.
- **Explicit regel:** proceduren, inklusive vilka ankarpar som används och hur talet
  härleds ur dem, dokumenteras och låses PER KORPUS innan produktionskörning — aldrig i
  efterhand utifrån hur många luckor tröskeln råkar ge.
- **Påverkar:** Lager 2 (Steg 0.5) i v3, `analysis/gap_verification.py`.

## D-004 — k-formel: dubbla kandidater, testade över flera korpusar via leave-one-out

- **Fråga:** k-formeln (k = max(3, round(0,5 · ln(N)))) i v3 är en omotiverad heuristik
  (öppen punkt M1 i `negative_space_open_problems_v1_0.md`). Ska den låsas som är, eller
  testas mot alternativ?
- **Beslut:** k låses INTE ännu. Två strukturellt olika kandidatformler pre-registreras
  och testas mot varandra över flera korpusar, med hjälp av leave-one-out-testet (D-006):

  | Kandidat | Formel | Skalningstyp |
  |---|---|---|
  | 1 (ursprunglig, v3) | k = round(0,5 · ln(N)) | Logaritmisk |
  | 2 (ny) | k = round(0,5 · √N) | Kvadratrot |

  Båda klipps till intervallet **[3, 10]**: k = max(3, min(10, formelresultat)).
  Nedre gräns oförändrad från v3; övre gräns ny — skyddar mot att stort k vid stora
  korpusar drar in för mycket innehåll per gap-region (ökad mellanmjölks-risk, se v3 A3).

- **Testprocedur (låst nu, innan någon korpus testas):**
  1. Kandidatformlerna (exakt dessa två) och spannet [3,10] är fasta — inga fler läggs
     till efteråt.
  2. Per tillgänglig korpus: beräkna k enligt båda formlerna.
  3. Kör leave-one-out (D-006) med respektive k-kandidat på varje korpus.
  4. **Utvärderingsmått (fast i förväg):** återupptäcks den kända, borttagna luckan
     (binärt: ja/nej inom top-N flaggade regioner, N pre-registrerad per körning)?
  5. **Stabilitetskriterium (fast i förväg):** en formel betraktas som den generella
     regeln om den återupptäcker den kända luckan på **minst 2 av de tillgängliga
     korpusarna** (kräver minst 2 korpusar utöver BCM-fallbacken för att vara testbart —
     se status nedan).
  6. Alla utfall för BÅDA kandidaterna på ALLA testade korpusar rapporteras — inte bara
     den bäst presterande.

- **De två möjliga slutlägena (båda giltiga och rapporterbara):**
  - **En formel vinner konsekvent** → låses som generell regel, med empirisk grund
    dokumenterad.
  - **Ingen formel vinner konsekvent / korpus-beroende** → k blir en
    **per-korpus-kalibreringsparameter** (samma logik som D-003): båda formlerna testas
    vid instans-kalibrering för en ny korpus, och den som ger bäst leave-one-out-träff
    väljs. Fortfarande domänagnostiskt som PROCEDUR, inte som TAL.

- **Explicit förbjudet:** att välja k baserat på vilken formel som ger "flest" eller
  "snyggast" luckor utan facit (leave-one-out). Att lägga till en tredje kandidatformel
  efter att resultat setts.

- **STATUS: blockerad på korpustillgång.** Kräver minst 2 korpusar utöver BCM-fallbacken
  (se Cowork-uppgift `cowork_uppgift_korpusinsamling.md`, ej levererad vid skrivande).
  Formlerna och proceduren är låsta HÄR och NU — exekveringen väntar på data.

- **Påverkar:** Lager 1 i v3, `analysis/gap_detection.py`.

## D-005 — Percentiltröskeln är ett explicit policy-val, inte en härledd storhet

- **Fråga:** Är 90:e/95:e percentilen (Lager 1) en siffra som kan härledas logiskt/
  matematiskt ur data, eller ett val?
- **Beslut:** Den är och förblir **ett policy-val**, inte en härledning — samma
  kategori av beslut som att sätta en signifikansnivå till 0,05 vs. 0,10 (jfr D-002).
  Den styr en avvägning (fler flaggade kandidater att granska vs. risk att missa
  luckor) som inte har ett matematiskt "rätt" svar. 90:e percentilen (höj till 95:e vid
  unionsöverskridande >15 %) behålls oförändrad från v3 som DEFAULT, motiverad av
  rimlighet, inte av matematik.
- **Möjlig framtida förfining (ej krav för PoC):** när leave-one-out-data (D-006) finns
  över flera percentilval (t.ex. 85:e/90:e/95:e), kan en precision/recall-liknande kurva
  mot den kända luckan plottas, och percentilvalet göras mer informerat — analogt med att
  välja en punkt på en ROC-kurva. Detta är fortfarande ett VAL av var man vill stå på
  kurvan, inte en härledning av ett "sant" värde, och ska aldrig beskrivas som sådan i
  formella avsnitt.
- **Explicit regel:** om detta förfiningssteg görs, ska percentil-kandidaterna och
  utvärderingsmåttet vara pre-registrerade innan leave-one-out-datan tas fram — samma
  disciplin som D-004.
- **Påverkar:** Lager 1 i v3, dokumentationsspråk i slutrapporten (undvik att framställa
  percentilen som empiriskt härledd om den inte är det).

## D-006 — Leave-one-out-test som obligatoriskt externt ankare

- **Fråga:** v3:s design testar bara gap-kohorten mot en slumpmässig kontrollkohort —
  ingen extern ground truth (CRITICAL C1 i `negative_space_open_problems_v1_0.md`).
- **Beslut:** Ett leave-one-out-test läggs till som **obligatoriskt steg i Lager 1**,
  före produktionskörning (Fas 3):
  1. Ta bort ett dokument, eller en tydligt avgränsad sektion, ur korpusen som **känt**
     täcker ett specifikt, namngivet ämne.
  2. Kör Nivå 0–2 på den beskurna korpusen.
  3. Kontrollera: (a) uppstår en gap-region där det borttagna dokumentets
     embedding-grannskap satt, (b) klassar Nivå 2 det resulterande scenariot som
     icke-trivialt.
  4. Rapportera utfallet oavsett resultat (positivt eller negativt är båda giltiga,
     jfr iteration 1:s praxis).
- **Dubbelanvändning:** detta test är samtidigt facit-mekanismen för D-004 (k-formel)
  och en direkt stängning av C1.
- **STATUS: väntar på korpustillgång** (samma blockering som D-004).
- **Påverkar:** Lager 1 i v3, ny modul `analysis/leave_one_out.py` (ej specificerad än).

## D-007 — Distance-concentration-kontroll läggs till i Steg 0.5

- **Fråga:** Högdimensionell distance concentration (CRITICAL C2 i
  `negative_space_open_problems_v1_0.md`) kan urholka NN-distans-baserad gap-detektion
  oavsett sökalgoritm (ball-tree löser bara ett annat problem).
- **Beslut:** En empirisk karakterisering av embedding-rummets faktiska
  avståndsfördelning (analog med iteration 1:s embedding-karakterisering, D-008 där)
  läggs till som obligatoriskt delsteg i Steg 0.5, INNAN percentiltröskeln (D-005)
  tillämpas skarpt. Om avstånden visar sig starkt koncentrerade (låg spridning runt
  medelvärdet): perentiltröskelns styrka som signal ska diskuteras explicit i
  slutrapporten, och lokal densitetsnormalisering övervägs som komplement (ej krav för
  PoC, men ska nämnas som öppen fråga om koncentration upptäcks).
- **Påverkar:** Steg 0.5 i v3:s byggspec (Del C).

## D-008 — Korpusleverans godkänd, Korpus 1 accepterad under målstorlek

- **Fråga:** Cowork levererade tre korpusar (Telekom/RFC, Klinisk/WHO, Utbildning/UNESCO).
  Korpus 1 (klinisk) landade på 369 sidor mot målet ~500. Ska ytterligare en WHO-PDF
  läggas till innan analys, eller godtas 369 sidor som är?
- **Beslut:** **369 sidor godtas som är. Ingen ytterligare PDF läggs till.** Beslutet
  fattas HÄR, innan k-formels-testet (D-004) eller något annat analyssteg körs på
  korpusen — inte efter att ett resultat setts och befunnits svagt. Att lägga till data
  i efterhand FÖR ATT ett tidigt resultat sett instabilt ut hade varit exakt den typen av
  efterhandsjustering pre-registreringsdisciplinen (D-004, analogt med iteration 1:s
  D-021) är satt att förhindra.
- **Dokumenterade begränsningar (ska stå i `corpus_manifest_C1_clinical.md`):**
  1. Korpus 1 är **WHO-only**, inte WHO+NICE som ursprungligen planerat — en smalare
     institutionell/stilmässig variation inom korpusen än avsett, utöver
     storleksavvikelsen.
  2. Korpus 2 (telekom) fick en tematisk förskjutning mot säkerhet/infrastruktur
     (DNSSEC, HTTP/1.1+cookies+HSTS, IPv6) i stället för de ursprungligen tänkta
     flaggskepps-RFC:erna — smalare tematisk spridning än "telekomstandarder" antydde,
     om än fortfarande giltig som en strukturellt distinkt korpus.
  3. Reproducerbarhets-status: samtliga tre korpusar bygger på öppet licensierat
     material (CC BY-NC-SA 3.0 IGO, CC BY-SA 3.0 IGO, IETF Trust/BCP 78) — **offentlig
     reproducerbarhets-status för alla tre.**
- **Positiv bieffekt noterad:** korpusarnas teckenantal spänner ett brett spann
  (telekom ~1,29M, klinisk ~1,00M, utbildning ~4,50M tecken) — ett bredare spann av N att
  testa k-formlernas skalning över än om alla tre råkat vara ungefär lika stora.
- **Påverkar:** `corpus_manifest_C1_clinical.md`, `corpus_manifest_C2_telecom_rfc.md`,
  D-004 (fler N-punkter att testa k-kandidaterna mot).

## D-009 — Återanvänd tooling från iteration 1: grön lista, med ett exponerat undantag

- **Fråga:** Vilken kod, om någon, från "Embracing the Novelty of Noise"-repot är ren,
  domänagnostisk tooling som kan återanvändas i Negative Space, utan att kalibrerade
  BCM-specifika trösklar eller antaganden följer med?
- **Metod:** Den gamla sessionen (med full kontext om Embracing-repot) fick en avgränsad
  fråga: identifiera ENDAST kod utan hårdkodade trösklar/domänvärden, och exkludera
  explicit allt som rör N(j), τ-kohorter, θ_absens/θ_match/δ, eller SVB/Basel III-logik.
- **Beslut — följande återanvänds, som TOOLING, alla parametrar omkalibreras för denna
  korpus:**

  | Komponent | Källa (iteration 1) | Status |
  |---|---|---|
  | Embedding-wrapper | `processing/embedder.py` | Fullt återanvändbar, byt modellnamn vid behov |
  | `_l2_normalize()` | `diversity.py` | Fullt återanvändbar, ren linjär algebra |
  | `_mean_pairwise_distance()` | `diversity.py` | Fullt återanvändbar |
  | `compute_gaps()` (lokalt gap + centroid-gap) | `analysis/gap_detection.py` | Återanvänds — **se förbehåll nedan** |
  | `_extract_text()` (pdfplumber) | `processing/corpus_loader.py` | Fullt återanvändbar, extraheras som fristående funktion |
  | `_chunk()` (sliding window) | `processing/corpus_loader.py` | Återanvänds, alla parametrar (chunk_size=400, overlap=50, min_chars=60) behandlas som defaultvärden att ompröva, inte låsta |
  | `_spearman_ci()` (Fisher z, 95% CI) | `analysis/h7_surface_stats.py` | Fullt återanvändbar |
  | `_surface_stats()` (ordlängd, meningsantal, sällsynta ord) | `analysis/h7_surface_stats.py` | Fullt återanvändbar — direkt användbar för samma typ av textstatistik-kontroll som H7 i iteration 1 (jfr `lardomar_iteration1_till_negative_space.md` §3) |

- **KRITISKT FÖRBEHÅLL — `compute_gaps()`:** funktionens interna `_cluster_regions()`-steg
  har `CLUSTER_COS_DIST_THRESHOLD = 0.30` hårdkodat på modulnivå, kalibrerat mot
  BCM-korpusens δ=0,70 (iteration 1, D-017). Detta värde får **INTE** ärvas tyst. Beslut:
  antingen (a) exponera `cluster_distance_threshold` som explicit parameter och
  kalibrera den på nytt per korpus (samma logik som D-003), eller (b) skippa
  klustersteget helt och arbeta direkt mot `GapDetectionResult.regions`. **Val: (b) för
  PoC** — klustring läggs till senare, som eget beslut, om regionantalet visar sig
  hanterbart utan det.
- **Explicit exkluderat (loggat för spårbarhet, INTE kopierat):**
  `embedding_characterization.py` (hårdkodade SVB/Basel-textpar), `processing/scorer.py`
  (N(j)-formeln), `processing/deduplicator.py` (kohort-taxonomi-låst),
  `validation/proxy_bundle.py` (SVB/θ-låst), `agents/runner.py` (BCM-prompter/τ-kohorter),
  `analysis/gap_verification.py` (θ_absens/θ_match hårdkodade),
  `analysis/rag_runner.py` (20-agent-struktur hårdkopplad),
  `analysis/instability_tool.py` (resample-datastruktur BCM-specifik).
- **Motivering:** Detta undviker att uppfinna PDF-extraktion, chunkning,
  cosine-baserad gap-beräkning och CI-statistik på nytt, samtidigt som det håller en hård
  gräns mot att kalibrerade BCM-värden (θ, τ, δ, α/β/k) smyger in via en
  "koden-fanns-redan"-genväg — precis den risk som flaggades innan denna fråga
  ställdes.
- **Påverkar:** Ny kodbas för Negative Space (separat repo), `analysis/gap_detection.py`
  (motsvarighet), Lager 1 i v3.

-----

## Uppdaterad Steg 0.5 (ersätter v3:s Steg 0.5-beskrivning i sin helhet)

**Steg 0.5 — Instans-kalibrering (per korpus, före all agentkörning):**

1. Fastställ N (antal chunkar).
2. **Distance-concentration-kontroll (D-007):** karakterisera avståndsfördelningen.
   Flagga om starkt koncentrerad.
3. **k-beräkning (D-004):** räkna ut k enligt båda kandidatformlerna (om
   leave-one-out-data för denna korpustyp saknas: använd båda som parallella spår tills
   D-004:s stabilitetskriterium kan utvärderas).
4. Kalibrera θ_absens (oförändrad procedur från v3/D-017-analogin).
5. **Nivå 1-matchningströskel (D-003):** kalibrera enligt ankarprocedur.
6. Skriv domänadapterns kalibreringsexempel, inklusive mellanmjölks-exemplet.
7. **Leave-one-out-test (D-006):** kör om en känd lucka finns att konstruera för denna
   korpus.
8. Temperatur-pilot (Fas 1) + låsning (Fas 2, med D-002:s objektiva kriterium).
9. Deklarera reproducerbarhets-status.

STOPPA efter varje nummer, visa resultat, innan nästa steg.

-----

*Mapping the Negative Space — Tillägg v4.0. FÖRSLAG, ej fattat. Bygger på v3.0 (Del A/B/C
oförändrade) plus D-002–D-009. Korpusleverans godkänd (D-008) — D-004 och D-006 är nu
körbara på alla fyra korpusar (BCM-fallback + Telekom/Klinisk/Utbildning). Tooling
för Steg 1+ specificerad (D-009).*
