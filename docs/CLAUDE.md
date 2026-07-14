# CLAUDE.md — Mapping the Negative Space

**Läs detta innan du rör kod, korpusar eller pre-registreringsdokument.**

## Vad det här projektet är

Ett fristående forskningsprojekt: geometrisk gap-detektion i embedding-rum för att hitta
täckningsluckor i en godtycklig dokumentkorpus. **Iteration 2** av ett större
forskningsprogram — föregångaren heter "Embracing the Novelty of Noise" och bor i ett
ANNAT repo. De två projekten är medvetet separerade.

## Normativa dokument (läs i denna ordning)

1. `rag_kohort_preregistrering_v3.md` — grunddesign (Del A/B/C: genomförbarhet,
   pre-registrering, byggspec)
2. `rag_kohort_tillagg_v4.md` — append-only tillägg med D-002–D-009 (låsta beslut om
   böjningspunkt, matchningströskel, k-formel, percentiltröskel, leave-one-out,
   distance-concentration, korpusleverans, tooling-återanvändning)
3. `lardomar_iteration1_till_negative_space.md` — destillerade mönster från iteration 1
   (INTE dess siffror/kod)
4. `negative_space_open_problems_v1_0.md` — öppna kritikpunkter, egen severity-tier

Beslutslogg-formatet (D-002, D-003, …) fortsätter i `rag_kohort_tillagg_v4.md`. Nästa
beslut ska numreras **D-010**. Skriv aldrig över ett existerande D-beslut — lägg till ett
nytt som ändrar/kompletterar det, i samma append-only-stil som redan används.

## HÅRD REGEL: ingen kontakt med Embracing-repot

- Referera **aldrig** kod, trösklar, θ/τ/δ/α/β/k-värden, eller N(j)-liknande apparater
  från "Embracing the Novelty of Noise". Det gäller även om du (Claude) har sett det
  repot i ett annat sammanhang eller känner igen mönstret.
- Enda tillåtna bryggan är listan i D-009 nedan — inget annat.
- Om du är osäker på om något "känns bekant" från det andra projektet: anta att det INTE
  får återanvändas om det inte står explicit i D-009.

## D-009 — Vad som FÅR återanvändas som tooling (och inget annat)

| Komponent | Status |
|---|---|
| Embedding-wrapper (`embedder.py`-motsvarighet) | Återanvänd, byt modellnamn vid behov |
| `_l2_normalize()` | Återanvänd rakt av |
| `_mean_pairwise_distance()` | Återanvänd rakt av |
| `compute_gaps()` (lokalt gap + centroid-gap) | Återanvänd, **MEN se förbehåll nedan** |
| `_extract_text()` (pdfplumber-baserad) | Återanvänd som fristående funktion |
| `_chunk()` (sliding window) | Återanvänd, chunk_size/overlap/min_chars behandlas som ändringsbara defaults, inte låsta värden |
| `_spearman_ci()` (Fisher z, 95% CI) | Återanvänd rakt av |
| `_surface_stats()` (textstatistik-kontroll) | Återanvänd rakt av — används för C2-confounder-kontrollen |

**Kritiskt förbehåll:** `compute_gaps()`:s interna klustersteg hade
`CLUSTER_COS_DIST_THRESHOLD = 0,30` hårdkodat, kalibrerat mot BCM-korpusens δ=0,70.
**Beslut (D-009): skippa klustersteget för PoC.** Arbeta direkt mot
`GapDetectionResult.regions`, inte mot klustrade regioner. Om klustring behövs senare:
det är ett NYTT beslut (D-011+), inte en tyst återaktivering av det gamla värdet.

**Allt annat är exkluderat**, inklusive men inte begränsat till: N(j)-formeln
(`scorer.py`), τ-kohort-logik (`agents/runner.py`), θ_absens/θ_match (`gap_verification.py`,
`embedding_characterization.py`), SVB/Basel-specifik kod (`proxy_bundle.py`), och
BCM-kopplad datastruktur i `deduplicator.py`/`instability_tool.py`/`rag_runner.py`.

## Öppna, låsta beslut att känna till innan du kodar (se tillägg v4 för fullständig text)

- **k-formel (D-004):** två kandidater — k=round(0,5·ln N) och k=round(0,5·√N), klippt
  till [3,10]. Ingen av dem är låst än. Testas via leave-one-out (D-006) över de fyra
  tillgängliga korpusarna. Lägg ALDRIG till en tredje kandidat i efterhand.
- **Perentiltröskel (D-005):** 90:e/95:e percentilen är ett explicit policy-val, inte
  härledd. Skriv aldrig i rapport/kod-kommentarer att den är empiriskt bevisad optimal.
- **Nivå 1-matchningströskel (D-003):** ingen universell siffra — kalibreras per korpus
  enligt en ankar-procedur, precis som θ_absens gjordes i iteration 1 (fast med NYA
  ankare, NYTT värde per korpus).
- **Fas 2 böjningspunkt (D-002):** objektivt kriterium (andraderivat > 2× median av
  |andraderivata| över svepet) — ingen visuell bedömning av kurvan tillåten.
- **Leave-one-out (D-006) och distance-concentration-kontroll (D-007):** obligatoriska
  steg i Steg 0.5, INNAN produktionskörning (Fas 3).

## Fyra tillgängliga korpusar (D-008)

| Korpus | Domän | N (ungefärligt, tecken) | Status |
|---|---|---|---|
| BCM (fallback, iteration 1) | Business continuity / risk | — | Tillgänglig |
| Korpus 1 | Klinisk (WHO, endast) | ~1,00M | 369 sidor — under mål, godtaget som är (D-008), lägg INTE till mer data i efterhand |
| Korpus 2 | Telekom (RFC, säkerhet/infrastruktur-kluster) | ~1,29M | Tematiskt smalare än planerat, giltig som distinkt korpus |
| Korpus 3 | Utbildning (UNESCO GEM) | ~4,50M | Klar, med marginal |

Manifest för respektive korpus: `corpus_manifest_C1_clinical.md`,
`corpus_manifest_C2_telecom_rfc.md`, `corpus_manifest_C3_education.md`.

## Arbetssätt — STOPPA-disciplin

Byggspecen (Del C i v3, uppdaterad Steg 0.5 i tillägg v4) har explicita STOPPA-punkter
efter varje steg: visa resultat, invänta bekräftelse, fortsätt inte automatiskt till
nästa steg. Detta gäller även för dig som kodande agent — kör inte hela pipelinen i ett
svep även om det vore tekniskt möjligt.

## Pre-registreringsdisciplin — icke förhandlingsbar

- Inga hyperparametrar/trösklar/formler justeras i efterhand för att förbättra ett
  resultat. Om ett tal ska ändras: det är ett nytt, motiverat D-beslut, fattat INNAN
  nästa körning — aldrig en tyst justering efter att ett resultat setts.
- Negativa/inkonklusiva resultat rapporteras lika öppet som positiva. Radera aldrig ett
  D-beslut eller en tabellrad för att den ser dålig ut — komplettera med en RESOLVED/
  UPPDATERAD-notering i stället, precis som i alla existerande dokument.
- Om du stöter på ett beslut som inte är fattat än (markerat "STATUS: öppet" i
  open-problems-dokumentet): fråga, gissa inte.
