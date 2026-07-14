# PDF-drop-lista — Korpus 1 (klinisk) & Korpus 3 (utbildning)

> Du valde att själv lägga käll-PDF:erna i projektmappen (mina hämtningsverktyg kan bara
> fånga ~40 sidor komplett per dokument och vissa WHO-PDF:er ger noll text via verktyget —
> men de laddas fint direkt i webbläsaren och extraheras lokalt med pdftotext/pypdf i sandboxen).
>
> **Så här gör du:**
> 1. Ladda ner PDF:erna nedan (länkarna går till officiella, fria fulltextkällor).
> 2. Lägg dem i rätt mapp:
>    - Korpus 1 → `corpora/corpus1_clinical/files/`
>    - Korpus 3 → `corpora/corpus3_education/files/`
> 3. Säg till mig. Jag kör då: extraktions-/extraherbarhetsverifiering per fil (kollar att
>    texten faktiskt går att läsa — inga skannade sidor, inga OCR-artefakter), skriver
>    manifesten i D-018-format, och rapporterar sidantal/tecken + ev. avvikelser.
>
> Listorna nedan är **rekommendationer** som når ≥ 500 sidor med balanserad källmix.
> Byt gärna ut enskilda dokument — allt som är fritt tillgänglig fulltext duger.

---

## Korpus 1 — Klinisk/medicinsk vägledning (balanserad WHO + NICE)

### WHO (ladda ner PDF direkt)

| # | Dokument | År | ~Sidor | Nedladdningslänk |
|---|---|---|---|---|
| 1 | mhGAP Intervention Guide, Version 2.0 (mental, neurologisk, substansbruk) | 2019 | ~174 | https://iris.who.int/bitstream/handle/10665/250239/9789241549790-eng.pdf |
| 2 | Guidelines on core components of infection prevention and control programmes | 2016 | ~91 | https://iris.who.int/bitstream/handle/10665/251730/9789241549929-eng.pdf |
| 3 | WHO Guidelines on physical activity and sedentary behaviour | 2020 | ~104 | https://www.who.int/publications/i/item/9789240015128 (klicka "Download") |

### NICE — UTGÅR (beslut C1-A, 2026-07-07)
**NICE används INTE.** Nedladdningar gav bara sammanfattningar/kortversioner. Korpus 1 byggs WHO-only.

### Fler WHO-dokument (valfritt, för extra volym)

| # | Dokument | År | ~Sidor | Nedladdningslänk |
|---|---|---|---|---|
| 4 | Consolidated guidelines / mental health (t.ex. mhGAP operations manual) | senaste | ~100+ | https://www.who.int/publications (sök, ladda ner PDF) |
| 5 | Pandemic influenza risk management | 2017 | ~60 | https://www.who.int/publications (sök, ladda ner PDF) |

**Balans (WHO-only):** #1 mhGAP ~174 + #2 fysisk aktivitet ~104 + #3 IPC ~91 ≈ **~369 s**; lägg till #4/#5 → **klart över 500 s.**
**Tips:** ladda ner WHO-PDF:erna direkt i webbläsaren (fungerar även om mitt verktyg får tom text från IRIS).

---

## Korpus 3 — Utbildningspolicy (UNESCO)

Ladda ner **fullständig rapport-PDF** (inte sammanfattningen) från landningssidorna:

| # | Dokument | År | ~Sidor | Landningssida (klicka "Download full report" / PDF) |
|---|---|---|---|---|
| 1 | GEM Report: Technology in education — A tool on whose terms? | 2023 | ~434 | https://www.unesco.org/gem-report/en/publication/technology |
| 2 | GEM Report: Inclusion and education — All means all | 2020 | ~388 | https://www.unesco.org/gem-report/en/publication/inclusion-and-education |
| 3 | Reimagining our futures together: a new social contract for education | 2021 | ~186 | https://www.unesco.org/en/futures-education/new-social-contract |

**Balans:** #1 ensam (~434 s) + #3 (~186 s) ≈ **~620 sidor**, eller #1 + #2 ≈ **~822 sidor.**
Narrativ policy-rapport-stil (distinkt från både klinisk direktivprosa och RFC-standardtext).

---

## Vad jag redan levererat (Korpus 2)

Korpus 2 (Telekom/RFC) är **klar** — 16 RFC:er, 568 sidor, 1 290 499 tecken, alla verifierat
kompletta. Se `corpus2_telecom_rfc/files/` och `corpus2_telecom_rfc/corpus_manifest_C2_telecom.md`.

---

*Negative Space · Drop-lista för Korpus 1 & 3 · 2026-07-05*
