# Korpus 1 — Klinisk/medicinsk vägledning (WHO) · Korpusmanifest

> Levande dokument. Negative Space-korpusinsamling (iteration 2). Format speglar `corpus_manifest_D018.md`.
> v1.0 · 2026-07-07 — **REALISERAD via PDF-drop + lokal extraktion (pdftotext).**
> Mått: dokumentens egna sidantal (pdfinfo) + extraherade tecken.

## Beslut C1-A — NICE utgår; korpusen är WHO-baserad
- **NICE används INTE** (nedladdningar gav bara sammanfattningar; kapitel floodade verktyget). Korpus 1 byggs på **WHO**-riktlinjer. Se BUILD_LOG.md.

## Metod & verifiering
- Projektägaren laddade ner WHO-PDF:erna och la dem i `files/`. Jag extraherade text lokalt med `pdftotext` och verifierade **extraherbarhet FÖRE godkännande**: sidantal via `pdfinfo`, teckenantal, samt text/sida-kvot för att utesluta skannade/bild-PDF:er. Alla tre har äkta textlager (inga OCR-artefakter, inga tomma sidor) och slutar vid korrekt baksida/ISBN.

## Korpustabell — realiserad Korpus 1 (WHO)

| Dokument | År | Källa (fil) | Sidor | Extraherade tecken | ~tecken/sida | Extraherbar? |
|---|---|---|---|---|---|---|
| Guidelines on Core Components of Infection Prevention and Control Programmes at the National and Acute Health Care Facility Level | 2016 | WHO-PDF (iris/who.int) | 91 | 386 111 | 4 242 | ✅ verifierad |
| WHO Guidelines on Physical Activity and Sedentary Behaviour | 2020 | WHO-PDF (ISBN 978-92-4-001513-5) | 104 | 316 772 | 3 045 | ✅ verifierad |
| mhGAP Intervention Guide, Version 2.0 (mental, neurological and substance use disorders) | 2019 | WHO-PDF | 174 | 299 808 | 1 723 (fler tabeller/flödesscheman) | ✅ verifierad |

**Summa: 3 dokument · 369 sidor · 1 002 691 extraherade tecken.**
Källfiler: `.pdf` sparade i `files/`; extraherad text: `.txt` bredvid varje PDF.
Licens: WHO, CC BY-NC-SA 3.0 IGO (öppen tillgång).

## Status mot kravet ≥500 sidor
- **369 sidor — något under ~500.** Tre kompletta, verifierade WHO-riktlinjer. För att passera 500 s: lägg ytterligare **en** WHO-PDF i `files/` (t.ex. pandemiberedskap ~60 s, eller global strategi för IPC ~50 s) så extraherar jag den på samma sätt. Alternativt godtas 369 s som realiserad Korpus 1.

## Exkluderade
| Dokument | Skäl |
|---|---|
| **NICE (alla)** | Beslut C1-A — NICE utgår ur projektet. |
| Tidigare partiella WHO-textavsnitt (Bookshelf: Exec Summary/Background/Methods) | Delmängder av den fullständiga Physical Activity-PDF:en → borttagna för att undvika dubblerad text. |

## Problemlogg
- Inga skannade PDF:er / OCR-artefakter (verifierat via text/sida-kvot). Extraherbarhet bekräftad före godkännande.
- (Historik: WHO IRIS gav tom text via det automatiska hämtningsverktyget; löstes genom manuell PDF-nedladdning + lokal pdftotext.)

## Avvikelser från plan
- Plan: balanserad WHO + NICE, ≥500 s. **Realiserat: WHO-only, 369 s** (beslut C1-A). Marginellt under 500 s tills ev. ytterligare en WHO-PDF läggs till.

---
*Negative Space · Korpus 1 (klinisk, WHO) · Manifest v1.0 · 2026-07-07*
