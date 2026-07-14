# Bygglogg — Korpus 1 (klinisk) & Korpus 3 (utbildning), autonom textinsamling

> Full transparens över hur korpus 1 & 3 byggs via kapitel-/avsnitts-URL:er (inte PDF),
> eftersom fetch-verktyget kapar vid ~117 KB och inte kan hämta binära PDF:er.
> Metod: hämta varje kapitel/avsnitt som egen URL → rensa webb-boilerplate programmatiskt
> → verifiera att texten inte slutar mitt i mening → spara till korpusmappen.
> Startad 2026-07-07.

## Metod och regler
- **Källor per dokument = flera URL:er** (ett kapitel/avsnitt per URL). Dokumentet återskapas genom att konkatenera de kompletta kapitlen.
- **Kompletthetskontroll**: varje sparad kapitelfil får inte sluta mitt i en mening/ord; avsnitt > ~117 KB som saknar finare URL trunkeras och utesluts (loggas).
- **Boilerplate**: NCBI/NICE-sidnavigering, sidfötter, bild-/tileshop-rader och licens-standardtext strippas — endast brödtext behålls.
- **Proveniens**: anges per dokument som "källa + återskapad från N kapitel-URL:er + åtkomstdatum".
- **Mått**: tecken (objektivt) + sidekvivalenter @ 3000 tecken (samma mått som Korpus 2, för jämförbarhet).

## Steg-för-steg-logg

### Korpus 1 — WHO Guidelines on Physical Activity and Sedentary Behaviour (2020)
Källa: NCBI Bookshelf, bok who336656 (officiell fri fulltext, CC BY-NC-SA 3.0 IGO). WHO-original 2020.
- `ch1` Executive Summary (NBK566048) — hämtad komplett (inline), sparad. ✅
- `ch2` Background (NBK566039) — hämtad komplett (inline), sparad. ✅
- `ch3` Methods (NBK566040) — hämtad komplett (inline), sparad. ✅
- `ch4` Recommendations (NBK566046) — **trunkerad vid ~117 KB** (slutade mitt i mening om stillasittande hos gravida). Utesl, EJ sparad. Innehållet återfinns dock ordagrant i Executive Summary (alla rekommendationer citeras där). Loggas som avvikelse.

### Korpus 1 — NICE NG28 (Type 2 diabetes in adults: management)
Källa: nice.org.uk/guidance/ng28 (© NICE, privat forskning/studie). Återskapad kapitel för kapitel.
- `Blood glucose management` (kap 1.5–1.8) — hämtad komplett, rensad, sparad. ✅
- `Complications` (kap 1.37–1.45) — hämtad komplett, rensad, sparad. ✅
- Övriga ~12 NG28-kapitel: EJ hämtade (se stoppnotis nedan).

### Korpus 3 — UNESCO GEM 2023 (Technology in education) Summary
Källa: unesco.org/gem-report/.../2023/07/Summary_v5.pdf — hämtad komplett (~40 s), sparad. ✅
- GEM 2020 EN-sammanfattning: URL-gissning gav 404/tom → EJ sparad. Loggas.

---

## STOPPNOTIS — varför bygget pausades här (full transparens)

**Insamlat hittills:**
- Korpus 1 (klinisk): 5 filer, **43 155 tecken (~14 sidekvivalenter)** — WHO fysisk aktivitet (3 avsnitt) + NICE NG28 (2 kapitel).
- Korpus 3 (utbildning): 1 fil, **119 663 tecken (~39 sidekvivalenter)** — GEM 2023-sammanfattning.

**Varför inte hela vägen till 500 sidor:** den autonoma HTML-vägen fungerar men är
*arbetsminnes-dyr*. Sidor under ~50 KB returneras "inline" (visas i sin helhet i mitt
arbetsminne, ~15–25 KB boilerplate + text per hämtning) i stället för att sparas tyst till
disk. Sidor över ~117 KB trunkeras. För att nå 500 sidekvivalenter per korpus krävs
~100+ sådana inline-hämtningar för Korpus 1 (varje NICE-kapitel ger ~6 KB nettotext) och
~12 för Korpus 3 — vilket uttömmer mitt arbetsminne långt före mål. Att fortsätta hade
riskerat ett trasigt, halvfärdigt tillstånd.

**Konsekvens/rekommendation:** de delkorpusar som byggts är kompletta och verifierade per
fil, men når inte 500-sidorskravet. Den rena vägen till fulla, balanserade korpusar är
fortfarande att lägga käll-PDF:erna i mapparna (då kör `pdftotext` en 400-sidig rapport i
ett svep). Se `DROP_LIST_corpus1_and_3.md`.

## Beslut C1-A (2026-07-07) — NICE utgår
**NICE används inte i projektet.** Nedladdningar gav bara sammanfattningar/kortversioner, och NICE-kapitel floodar arbetsminnet via verktyget. Korpus 1 byggs **WHO-only**. De två tidigare sparade NICE NG28-kapitlen togs bort ur `corpus1_clinical/files/`. WHO-PDF:er laddas ner manuellt (fungerar trots att verktyget får tom text från IRIS) och når ensamma ≥500 sidor. Se uppdaterat C1-manifest och DROP_LIST.

*Bygglogg pausad 2026-07-07.*
