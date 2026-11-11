# Mapping the Negative Space

### Geometric Gap Detection in Corpus Embeddings

**Iteration 2** av ett fristående, pre-registrerat forskningsprogram om vad dokumentkorpusar
*inte* säger. Ett fristående repo, medvetet skilt från iteration 1 ("Embracing the Novelty of
Noise"). Föregångare till iteration 3 ("Bridging the Void").

---

## Frågan

En korpus-läsande AI kan bara svara på det korpusen *innehåller*. Det den aldrig nämner — dess
täckningsluckor, dess blinda fläckar — är osynligt för varje metod som resonerar utifrån
befintligt innehåll, och det är ofta just där den verkliga risken sitter. Premissen:
**det korpusen aldrig nämner är dess blinda fläckar.**

Detta projekt testar om sådana frånvaron kan hittas *geometriskt*: motsvarar glesa regioner i
en korpus embedding-rum faktiskt meningsfullt saknat innehåll? Och kan en agentkohort, styrd
mot de glesa regionerna, formulera luckor som överlever automatisk silning — bättre än ett
slumpmässigt regionval?

## Kort svar

**Nej, i huvudsak.** Rapporten (`Mapping_the_Negative_Space_PoC_Report.md`) redovisar ett
övervägande negativt utfall, öppet och pre-registrerat:

- Ingen gap-detektionsmetod, inget embedding-rum och ingen k-formel generaliserade pålitligt
  över tre strukturellt olika korpusar (D-004, D-013, D-015, D-018).
- Temperatur hade försumbar effekt på svar↔käll-avståndet (D-017).
- "Redan täckt" kunde inte operationaliseras med bi- eller cross-encoder (stil-matchad
  AUC 0,388); Nivå 1 fick bli en LLM-domare (D-021–D-024).
- **Effektstorlekssonden på den bäst-detekterande korpusen: d̂ = −0,208, 95 % CI
  [−0,387, −0,029], p = 0,024** — den geometriskt valda kohorten gav *färre* överlevande
  luckor än slumpkontrollen (D-025/D-026).

De negativa fynden är projektets primära metodbidrag: de visar, med en pre-registrerad och
självgranskande apparat, att **geometrisk gleshet i bästa fall är en svag proxy för
meningsfulla luckor** i denna pipeline.

---

## Pipeline (Nivå 0–3)

| Nivå | Vad | Kostnad |
|---|---|---|
| **0** | Geometriskt regionval: glesa regioner (`void_stat`, rått MiniLM, sqrt-k) + obligatorisk slumpkontroll | Gratis (ren geometri) |
| **1** | Bred korpussökning — är luckan verkligen frånvarande? Blev en **LLM-täckningsdomare** när embedding-mått misslyckades | ~1 LLM-anrop/påstående |
| **2** | Trivialitetsdomare (domänadapter, kalibrerad mot "mellanmjölks"-floskler) | Billig |
| **3** | Mänsklig bedömning — **medvetet utelämnad** i denna PoC | — |

Överlevande påståenden är *kandidater*, aldrig bekräftade luckor (Nivå 3 saknas).

## Korpusar (D-008, alla öppet licensierade)

| | C1 — Klinisk/WHO | C2 — Telekom/RFC | C3 — Utbildning/UNESCO |
|---|---|---|---|
| Dokument | 3 | 16 | 3 |
| Sidor | 369 | 568 | 1 255 |
| Tecken | 1 002 691 | 1 290 499 | 4 499 309 |
| Chunkar (N) | 2 939 | 3 214 | 14 181 |
| Licens | CC BY-NC-SA 3.0 IGO | IETF Trust / BCP 78 | CC BY-SA 3.0 IGO |

Deklarerade begränsningar (pre-registrerade, ej i efterhand): C1 är WHO-only och under
sidmålet (369 s, godtaget som är); C2 är förskjuten mot säkerhet/infrastruktur. Det breda
N-spannet är en avsiktlig fördel för att testa k-formlernas skalning.

---

## Metodologisk disciplin

Projektet är pre-registrerat som ett kliniskt studieprotokoll: varje hypotesrelevant beslut
låstes i en append-only-logg (`beslutslogg.md`, D-001–D-026) *innan* dess utfall sågs.
Inget hypotesrelevant tal justerades i efterhand. Fyra confounder identifierades och
korrigerades, var och en loggad med före/efter-tillstånd och temporal ordning:

1. **Whitening-läckan** — whitening fittades på hela korpusen inkl. borttaget innehåll
   (fångad *före* tolkning; C2:s resultat kollapsade 0,0583 → 0,0996 efter fix).
2. **Parvis-vs-max-tröskeln** — Nivå 1-tröskeln kalibrerad på fel statistik.
3. **Stil-confounden** — en stark AUC (0,952) visade sig vara en stil-artefakt (→ 0,388).
4. **Cross-lingual-confounden** — svensk generering mot engelsk korpus + ett saknat
   exkluderingsfönster.

Confound 1 fångades före tolkning; 2–4 under tolkning — och är skälet till att de
motsvarande tidiga, lovande talen inte står som fynd.

---

## Projektstruktur

```
CLAUDE.md                                # agent-instruktioner + hårda regler (D-009 grön tooling)
README.md                                # detta dokument
beslutslogg.md                           # append-only D-serie, D-001–D-026 (sanningskälla)
config.py                                # Lager 1 (låst) + Lager 2 (per-korpus-kalibrering)
Mapping_the_Negative_Space_PoC_Report.md # slutrapport (PoC)
docs/                                    # prereg v3, tillägg v4, lärdomar, open problems
processing/                              # corpus_loader (extraktion/chunkning), embedder
analysis/                                # gap_detection, gap_methods, leave_one_out,
                                         #   gap_verification (Nivå 1), domain_adapter (Nivå 2),
                                         #   rag_runner (sond), d026_arms, distance_concentration …
corpora/                                 # C1–C3 källfiler, extraherad text, manifest
.cache/                                  # embeddings (.npy) + alla resultatfiler (.json)
```

**Sanningskälla:** `beslutslogg.md` har företräde framför all annan dokumentation vid
konflikt. Nästa lediga beslutsnummer: **D-027**.

## Reproducerbarhet

Beroenden i `requirements.txt` (pdfplumber, sentence-transformers, scikit-learn, scipy,
ripser, anthropic, openai). Nivå 0–1 och all leave-one-out/bakeoff-geometri är gratis och
deterministisk (seed-låst); temperatur-piloten och sonden kräver API-nycklar
(Anthropic + OpenAI) och kostar LLM-anrop. Alla tre korpusarna är öppet licensierade →
offentlig reproducerbarhets-status.

---

## Vidare till iteration 3

Sonden visade att luckorna sannolikt *inte* sitter i tomrummen. Nästa iteration,
**Bridging the Void**, vänder på Nivå 0: i stället för att leta i glesa regioner kartläggs de
tätaste klustren, och hypotesen blir att den intressanta informationen sitter i de *obyggda
bryggorna mellan täta kluster* (bisociation) — validerad med iteration 1:s AnomalyScore. Se
det projektets egna dokument.

---

*Mapping the Negative Space · iteration 2. Negativa och inkonklusiva resultat rapporteras lika
öppet som positiva. Append-only-logg: ingenting raderas, allt kompletteras.*
