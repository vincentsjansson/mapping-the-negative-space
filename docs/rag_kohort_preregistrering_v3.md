# RAG-kohort & lucka-i-täckning — pre-registrering + byggspec (v3.0)

> **Status: FÖRSLAG — EJ FATTAT, EJ BYGGT.** v3.0 utökar v2.0 med: (1) ett pilotdrivet
> temperatur-svep i tre faser istället för tre fasta värden, (2) en icke-polariserad,
> tregradig tolkning av svar↔käll-avståndet (samma logik för lokalt gap och kant/outlier
> — tidigare version riskerade att belöna "mellanmjölks"-floskler), (3) ett explicit
> kalibreringsexempel för domänadaptern som fångar just den mekaniska medelvärdes-fällan.
> Grund för det fristående projektet **"Mapping the Negative Space: Geometric Gap
> Detection in Corpus Embeddings"** — iteration 2, efter Embracing Novelty of Noise.

-----

# DEL A — GENOMFÖRBARHET & OMFATTNING

## A1. Den logiska kärnan — håller den?

Definition 3 vilar på: **"det korpusen aldrig nämner är dess blinda fläckar."**

- **Styrka:** för en korpus-ägares egna dokument är detta rimligt.
- **Svaghet 1 (frånvaro ≠ blind fläck):** något kan saknas för att det är irrelevant, inte
  en blind fläck. Trivialitet (Nivå 2) fångar en del, inte allt.
- **Svaghet 2 (frånvaro kan vara medveten):** korpussökning kan inte skilja "aldrig tänkt
  på" från "medvetet utelämnad".
- **Konsekvens:** "äkta lucka" = frånvarande OCH relevant OCH icke-trivial OCH inte
  medvetet bortvald. De sista två kräver i praktiken en människa. **Det fullständiga
  äkthetstestet är inte automatiserbart.** Nivå 0–2 silar, Nivå 3 avgör.

## A1b. Geometrisk gap-detektion som förfilter

Två kompletterande gap-typer, räknade över HELA korpusen:

| Typ | Mått | Fångar | Exempel |
|---|---|---|---|
| **Lokalt gap** | NN-distans till närmaste granne-chunk | Konceptuella mellanrum MELLAN väletablerade teman | Leverantörsrisk och cyberrisk täcks väl var för sig, aldrig deras skärningspunkt |
| **Kant/outlier** | Avstånd till korpusens centroid | Ämnen bara nuddade perifert | En bisats nämner en risk korpusen aldrig återkommer till |

**Kostnad: trivial.** Beräknas på cachade embeddings. NN-distans via **ball-tree** (KD-tree
degraderar i 384 dimensioner). Centroid-avstånd O(N). Ingen API-kostnad.

**Urvalsregel:** 90:e percentilen på ENDERA måttet. Höj till 95:e om unionen överstiger
~15% av korpusen — beslutas INNAN agenter körs.

**Varför detta inte löser hela problemet:** geometrisk gleshet ≠ meningsfull lucka. Samma
confounder-klass som H7 (D-035, iteration 1). Översättningen "gles zon" → "saknat scenario"
är fortfarande en LLM-uppgift med konfabuleringsrisk.

**NY i v3.0 — geometrisk position avgör INTE kvalitet:** varken kort eller långt avstånd
mellan ett svar och dess källmaterial är i sig ett kvalitetsmått. Se A3 för den fulla
motiveringen (mellanmjölks-fällan) och Del B för den reviderade tolkningstabellen.

**Plats i pipelinen:**

| Nivå | När | Vad | Kostnad |
|---|---|---|---|
| **0** | FÖRE generering | Lokalt gap + kant/outlier över hela C + slumpmässig kontrollkohort | Gratis |
| — | Instans-kalibrering | Temperatur-pilot (se Lager 2) | Låg API-kostnad, engångs |
| 1 | EFTER lucka-påstående | Sök hela C — verkligen frånvarande? | Gratis |
| 2 | EFTER Nivå 1 | Trivialitetsdomare (domänadapter, inkl. mellanmjölks-kalibrering) | Billig |
| — | Parallellt med 1–2 | Svar↔käll-avstånd (diagnostik, tregradig tolkning) | Gratis |
| 3 | EFTER Nivå 2 | Mänsklig bedömning | Hoppas i väg 2 |

## A2. Kostnadsöversikt

Oförändrad från v2.0, med ett tillägg: temperatur-piloten (Fas 1) kräver ett litet extra
antal LLM-anrop per korpus, engångskostnad vid instans-kalibrering — låg, men inte gratis
(till skillnad från Nivå 0/1 som är ren geometri).

## A3. Specifika fällor

Oförändrat från v2.0 (prompt-eko, retrieval-täckningsillusion, domar-cirkularitet,
specificitet≠äkthet, restriction of range, retrieval-fattigdoms-confound,
embedding-anisotropi vid flerdomän), **plus två nya:**

- **NY — Mellanmjölks-fällan:** vid låg temperatur kan modellen, istället för att
  identifiera en genuin lucka, mekaniskt "slå ihop" k-chunkarnas innehåll till en trivial
  medelpunkt (t.ex. bokstavligen lägga sig mitt emellan två teman utan att säga något
  substantiellt om skärningspunkten). Detta ger **exakt samma geometriska signatur** som
  en genuint lyckad interpolation — kort avstånd till chunkarnas centroid. **Konsekvens:**
  avståndsmåttet kan INTE ensamt skilja en bra lucka-identifiering från en floskel. Endast
  Nivå 2 (domänadaptern, kalibrerad för att känna igen mönstret) kan göra den
  distinktionen. Se domänadapterns kalibreringsexempel i Del B.
- **NY — Obegränsad extrapolation vid kantläge:** att belöna "långt avstånd" för
  kantfall utan en övre gräns driver systemet mot att generera innehåll allt längre bort
  från korpusen, utan naturligt stopp — vilket kolliderar med den tidigare avfärdade
  hyperplan-idén (ett obegränsat halvrum bortom korpusens hölje är "allt icke-relaterat",
  inte en lucka). Långt avstånd är därför en riskflagga, aldrig ett mål i sig, för BÅDA
  gap-typerna.

## A4. Beslutsgrind

Oförändrad från v2.0. Väg 2 (smal PoC) kvarstår som startpunkt, uppgradering till väg 1
omprövas explicit inför slutgiltig rapportskrivning.

-----

# DEL B — PRE-REGISTRERING (tvålagers, committas vid start i nytt repo)

```markdown
## D-001 — RAG-kohort & geometrisk lucka-i-täckning (iteration 2, "Negative Space")

- **Datum**: TBD (vid commit)
- **Kategori**: Metod / Produkt
- **Status**: FÖRSLAG → VÄG 2 VALD (smal PoC-demo) som startpunkt. Nivå 3 medvetet
  utelämnad initialt — omprövas explicit innan slutgiltig rapportskrivning.
- **Fråga**: Kan en korpus-läsande agentkohort, styrd mot geometriskt identifierade glesa
  regioner i en godtycklig korpus C, formulera luckor som överlever automatisk silning —
  bättre än slumpmässig regionval — och är arkitekturen domänagnostisk i praktiken?

### LAGER 1 — Meta-design (låst nu, gäller ALLA framtida korpusar)

- **Gap-typer:** lokalt gap (NN-distans) + kant/outlier (centroid-avstånd), hela korpusen.
- **Percentiltröskel:** 90:e percentilen på ENDERA måttet; höj till 95:e om unionen >15%.
- **k-METOD:** k = max(3, round(0,5 × ln(N))). Ingen manuell justering.
- **Kontrollkohort (obligatorisk):** lika stor slumpmässig regiongrupp, identisk pipeline.
  Utan denna kan Nivå 0:s kärnpåstående inte testas (restriction of range).
- **Domänadapter (Nivå 2):** `(scenario, domain_context, kalibreringsexempel) → beslut`.
  Prompt-/few-shot ENDAST, INTE fine-tuning. **NY — obligatoriskt kalibreringsexempel:**
  varje domänadapter måste innehålla minst ett exempel på en "mellanmjölks-floskel"
  (mekanisk sammanslagning av k-chunkarnas innehåll utan substantiellt nytt påstående),
  märkt "trivial: ja", oavsett hur nära chunkarnas centroid svarets embedding hamnar.
  Detta säkerställer att domaren är kalibrerad att fånga fällan geometrin inte kan se.
- **NY — Svar↔käll-avstånd, TREGRADIG tolkning (ersätter v2.0:s tvågradiga, ej polariserad
  per gap-typ — samma tabell gäller BÅDA lokalt gap och kant/outlier):**

  | Avstånd | Tolkning | Kräver |
  |---|---|---|
  | Extremt kort (nästan identiskt med en enskild chunk) | Ren parafrasering — ej en lucka | Avfärdas oavsett Nivå 1/2 |
  | **Måttligt** (nära centroid, ej identisk med någon enskild chunk) | **Förväntat och sunt läge för BÅDA gap-typer — men avgörs INTE av avståndet ensamt** | Nivå 2:s domän-bedömning är AVGÖRANDE här — detta är där mellanmjölk gömmer sig |
  | Extremt långt | Riskflagga: hallucination (lokalt gap) eller meningslös extrapolation bortom korpusen (kantläge) | Kräver stark Nivå 1-bekräftelse för att inte avfärdas |

  **Explicit avfärdat:** att polarisera målet per gap-typ (kort=bra vid lokalt gap,
  långt=bra vid kantläge). Kort avstånd är geometriskt identiskt med en mekanisk
  medelvärdesberäkning (mellanmjölks-fällan) — att belöna det skulle belöna exakt den
  floskel domänadaptern är satt att fånga. Långt avstånd utan gräns driver mot meningslös
  extrapolation. Avståndet är alltid diagnostiskt, aldrig en egen godkännande-grind.

### LAGER 2 — Instans-kalibrering (låst PER KORPUS, Steg 0.5, före agentkörning)

- **θ_absens:** omkalibreras mot korpusens observerade geometri (D-017-proceduren).
- **Faktiskt percentil- och k-värde:** från Lager 1:s formler, applicerade på korpusens N.
- **Domänadapterns kalibreringsexempel:** domänspecifika, inklusive det obligatoriska
  mellanmjölks-exemplet ovan.
- **NY — Temperatur-pilot, trestegsraket (ersätter v2.0:s fasta 0,2/0,5/0,9):**

  **Fas 1 — Pilotsvep:** kör ett litet, i förväg avsatt sub-urval av regioner (disjunkt
  från produktionsurvalet i Fas 3 — samma regioner får ALDRIG förekomma i båda) vid tät
  temperaturupplösning (t.ex. 0,0 / 0,1 / 0,2 ... 1,0). Mät svar↔käll-avstånd vid varje
  temperatur.

  **Fas 2 — Låsning av tre temperaturer:** välj de tre temperaturer som pre-registrerat
  motsvarar 25:e/50:e/75:e percentilen av den observerade FÖRÄNDRINGSTAKTEN (derivatan) i
  svar↔käll-avstånd över sveppet. **Explicit regel, ingen tolkning i efterhand.**
  **Fallback, pre-registrerad:** om kurvan är monoton utan tydlig böjningspunkt (ingen
  urskiljbar "fasövergång"), används de ursprungliga fasta värdena 0,2/0,5/0,9 istället.
  Detta beslut (fasövergång funnen eller ej) dokumenteras med kurvan bifogad, INNAN Fas 3
  påbörjas.

  **Fas 3 — Produktionskörning:** de tre låsta temperaturerna körs (repeated measures,
  samma region tre gånger) på resterande, disjunkta regioner — gap-kohort OCH
  kontrollkohort.

  **Kostnadsnot:** Fas 1 är en engångskostnad per korpus, litet urval — håller
  budgeten under kontroll jämfört med ett fullständigt tätt svep över hela korpusen.

- **Reproducerbarhets-status:** offentlig vs. konfidentiell, beslutas innan partner
  engageras.
- **Fallback vid saknad extern korpus:** kör mot BCM-korpusen (D-018) som instans #1.

### Pre-registrerad definition av "äkta lucka" (väg 2)

Oförändrad från v2.0: frånvarande i HELA C (Nivå 1) OCH icke-trivial (Nivå 2, nu med
mellanmjölks-kalibrering). "Automatiskt godkänd" ≠ "äkta" utan Nivå 3.

### Pre-registrerade metriker

Oförändrat från v2.0 (Nivå 0-spridning, äkthetsandel gap vs. kontroll, specificitet,
konfabuleringsandel, gap-mått-korrelation), **plus:**
- Svar↔käll-avstånd, tregradig klassificering, korsat mot Nivå 1 OCH Nivå 2-utfall
  (inte bara Nivå 1 som i v2.0 — mellanmjölks-fällan kräver Nivå 2 för att upptäckas).
- Andel luckor i "måttligt avstånd"-kategorin som ändå klassas trivial av Nivå 2 —
  **detta är det direkta måttet på hur ofta mellanmjölks-fällan faktiskt inträffar.**
- Pilotkurvans form per korpus (monoton vs. tydlig fasövergång) — rapporteras alltid,
  oavsett vilket utfall.

### Pre-registrerad tolkningstabell

| Utfall | Tolkning |
|---|---|
| Gap-kohort äkthetsandel >> kontrollkohort | Nivå 0 är en användbar förfilter-signal |
| Gap-kohort ≈ kontrollkohort | Geometrisk gleshet ≠ meningsfull lucka — negativt delfynd |
| Hög andel "måttligt avstånd + Nivå 2 trivial" | Mellanmjölks-fällan är vanlig — avstånd allena hade gett falska positiva |
| Hög andel "måttligt avstånd + Nivå 2 icke-trivial" | Domänadaptern fångar genuina, grundade luckor — starkt resultat |
| Pilot visar tydlig fasövergång, konsekvent mellan korpusar | Stöd för att en universell temperatur-känslighet finns i uppgiften |
| Pilot visar ingen fasövergång | Negativt delfynd — fallback till fasta temperaturer, rapporteras ärligt |
| Resultat konsekvent över flera korpusar | Stöd för domänagnostisk arkitektur |
| Resultat skiljer sig kraftigt mellan korpusar | Domänagnostisk i design, ej i praktiskt utfall utan per-korpus-kalibrering |

### EXPLICIT UTANFÖR scope

Oförändrat från v2.0, plus: **att polarisera avståndsmålet per gap-typ** (kort=bra vid
lokalt gap, långt=bra vid kantläge) — explicit avfärdat i A3/Lager 1 ovan. Att definiera
"informativ temperatur" i Fas 2 som något annat än den pre-registrerade percentil-regeln.

### Förkastade alternativ

Oförändrat från v2.0 (Isolation Forest, stödjande hyperplan, TDA, RAG som ersättning för
blinda ensemblen, LLM-domare ensam, sammanslagen specificitet/äkthet), **plus:**
- **Polariserad avstånds-tolkning per gap-typ:** förkastat — kolliderar med
  mellanmjölks-fällan (kort avstånd är inte urskiljbart från en trivial floskel) och med
  den tidigare avfärdade obegränsade-halvrums-invändningen (långt avstånd utan gräns).
- **Fritt vald "sweet spot"-temperatur utan pre-registrerad regel:** förkastat —
  efterhandsoptimering i pilotform, samma metodfel som att välja bästa temperatur direkt.

### Öppna sår ärvda från iteration 1

H7 (embedding-geometri-confounder) och M1 (domänagnosticism kräver flera korpusar för att
vara bevisad) — oförändrade, se v2.0.

- **Påverkar moduler**: `analysis/gap_detection.py`, `analysis/rag_runner.py` (nu med
  pilot-/produktionsfas-logik), `analysis/gap_verification.py`,
  `analysis/answer_source_distance.py` (tregradig klassificering),
  `analysis/domain_adapter.py` (inkl. mellanmjölks-kalibreringsexempel), `config.py`.
- **Beslutat av**: Vincent + AI-kollaboratör
```

-----

# DEL C — CLAUDE CODE-BYGGSPEC

## Steg 0 — Commit Del B i nytt repos `beslutslogg.md`.

## Steg 0.5 — Instans-kalibrering (per korpus, före all agentkörning)
Fastställ N, beräkna k, kalibrera θ_absens. Skriv domänadapterns kalibreringsexempel,
**inklusive det obligatoriska mellanmjölks-exemplet.** Deklarera reproducerbarhets-status.

**Temperatur-pilot (Fas 1):** avsätt ett litet, disjunkt sub-urval av regioner. Kör tätt
temperatursvep (0,0–1,0). Beräkna svar↔käll-avstånd per temperatur. Plotta kurvan.

**Temperatur-låsning (Fas 2):** applicera den pre-registrerade percentil-regeln på
derivatan. Om ingen fasövergång syns: falla tillbaka till 0,2/0,5/0,9. STOPPA, visa kurva
och vilka tre temperaturer som valdes (eller fallback-beslutet), innan Fas 3.

## Steg 1 — Nivå 0: gap-detektion, båda typer, plus kontrollkohort
Oförändrat från v2.0. STOPPA, visa histogram, regionantal, överlapp.

## Steg 2 — Retrieval-modul, styrd av Nivå 0
Oförändrat. STOPPA, visa exempel.

## Steg 3 — RAG-orkestrering (produktionsfas, Fas 3)
Kör de tre LÅSTA temperaturerna (från Fas 2) på de disjunkta produktionsregionerna —
gap-kohort och kontrollkohort. `--dry-run` först. STOPPA.

## Steg 4 — Kör kohorten
Ny run-id. Rapportera finish_reason. STOPPA.

## Steg 5 — Nivå 1 (bred korpussökning)
Oförändrat. STOPPA.

## Steg 6 — Nivå 2 (domänadapter-domare, med mellanmjölks-kalibrering)
STOPPA, visa andel trivial vs. icke-trivial, SÄRSKILT för "måttligt avstånd"-fallen.

## Steg 7 — Svar↔käll-avstånd, tregradig klassificering
Korsa mot BÅDE Nivå 1 och Nivå 2-utfall. STOPPA, visa mellanmjölks-andelen explicit.

## Steg 8 — [Om väg 2] Nivå 3 utelämnad / [om uppgraderat] mänsklig bedömning.

## Steg 9 — Sammanställning mot tolkningstabellen. Tolka INTE i förväg. STOPPA.

## Steg 10 — Logga resultat (egen D-post), inklusive pilotkurvans utfall per korpus.

## Steg 11 — [Vid flera korpusar] Upprepa Steg 0.5–10, ny pilot per korpus.

-----

*Mapping the Negative Space — v3.0. FÖRSLAG, ej fattat. Granska Del A före beslut.*
