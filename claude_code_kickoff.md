# Claude Code — kickoff (Mapping the Negative Space, iteration 2)

Klistra in prompten nedan i Claude Code, körd från repo-roten
(`Mapping the negative space/`). Steg 0 i byggspecen är redan klart:
`beslutslogg.md` finns med D-001–D-009 incheckade.

---

## Prompt att klistra in

```
Du bygger iteration 2 av ett forskningsprojekt: "Mapping the Negative Space —
Geometric Gap Detection in Corpus Embeddings". Ett fristående repo, helt skilt från
iteration 1 ("Embracing the Novelty of Noise").

LÄS FÖRST, INNAN DU RÖR KOD, i denna ordning:
1. docs/CLAUDE.md              (hårda regler + D-009 grön tooling-lista)
2. docs/rag_kohort_preregistrering_v3.md   (Del A/B/C — byggspecen är Del C)
3. docs/rag_kohort_tillagg_v4.md           (D-002–D-009 + uppdaterad Steg 0.5)
4. docs/lardomar_iteration1_till_negative_space.md
5. docs/negative_space_open_problems_v1_0.md
6. beslutslogg.md              (Steg 0 klart: D-001–D-009 incheckade; nästa = D-010)

HÅRDA REGLER (icke förhandlingsbara):
- INGEN kontakt med iteration 1-repot. Återanvänd ALDRIG kod, trösklar eller
  θ/τ/δ/α/β/k-värden därifrån. Enda tillåtna bryggan är D-009:s gröna tooling-lista —
  och den koden skrivs REN från grunden här, inga filer kopieras, inga kalibrerade
  BCM-värden importeras.
- compute_gaps: SKIPPA klustersteget (D-009 val b). Inget hårdkodat
  CLUSTER_COS_DIST_THRESHOLD. Arbeta direkt mot GapDetectionResult.regions.
- k-formeln är INTE låst (D-004): två kandidater (log + sqrt, klippta till [3,10]),
  testas mot varandra via leave-one-out (D-006). Lägg aldrig till en tredje.
- Percentiltröskel (90:e/95:e) är ett POLICY-VAL (D-005), aldrig "empiriskt optimal".
- Nivå 1-tröskel och θ_absens: procedur, inte universell siffra — kalibreras PER KORPUS
  i Steg 0.5 (D-003), aldrig i efterhand utifrån hur många luckor de råkar ge.
- Pre-registreringsdisciplin: justera aldrig en hyperparameter i efterhand för att
  förbättra ett resultat. Ändring = nytt D-beslut (D-010+) INNAN nästa körning.
- Om du möter ett beslut som inte är fattat ("STATUS: öppet"): FRÅGA, gissa inte.

STOPPA-DISCIPLIN: kör aldrig hela pipelinen i ett svep. Byggspecen (Del C, steg 0–11
och den uppdaterade Steg 0.5 i tillägg v4) har explicita STOPPA-punkter efter varje
delsteg. Visa resultat (histogram, regionantal, kurvor, valda värden), invänta min
bekräftelse, fortsätt inte automatiskt.

STARTA HÄR — Steg 0.5, delsteg 1 (instans-kalibrering, en korpus i taget):
Föreslå först repo-strukturen (config.py + processing/ + analysis/ enligt modul-listan i
byggspecen och D-001:s "påverkar"-fält) och requirements. Sätt Lager 1-värden låsta i
config, Lager 2-värden som None. Bygg sedan den gröna toolingen (embedder, corpus_loader
med _extract_text/_chunk, gap_detection.compute_gaps utan klustring, diversity-helpers,
surface_stats). När den finns: kör Steg 0.5.1 (fastställ N genom chunkning) på Korpus 1
(corpora/corpus1_clinical/files) och STOPPA med resultatet.

Korpusar tillgängliga (D-008): C1 klinisk/WHO (~1,00M tecken, WHO-only, godtagen under
mål), C2 telekom/RFC (~1,29M), C3 utbildning/UNESCO (~4,50M). Alla öppet licensierade.

NOT: Steg 0.5.8 (temperatur-pilot) kräver API-nycklar (Anthropic + OpenAI) och kostar
LLM-anrop — säg till innan du når dit. Steg 0.5.1–0.5.7 är ren geometri/text, ingen
kostnad.
```

---

## Snabb-checklista innan du kör

- [ ] Repo-roten är `Mapping the negative space/` (där `beslutslogg.md` och `corpora/` ligger).
- [x] `CLAUDE.md` ligger i repo-roten (läses automatiskt av Claude Code). Kopian i `docs/` finns kvar som en del av dokumentuppsättningen.
- [ ] API-nycklar behövs först vid Steg 0.5.8 (temperatur-pilot), inte innan.
- [ ] Nästa lediga beslutsnummer i `beslutslogg.md`: **D-010**.
