# Korpus 3 — Utbildningspolicy (UNESCO) · Korpusmanifest

> Levande dokument. Negative Space-korpusinsamling (iteration 2). Format speglar `corpus_manifest_D018.md`.
> v1.0 · 2026-07-07 — **REALISERAD via PDF-drop + lokal extraktion (pdftotext).**
> Mått: dokumentens egna sidantal (pdfinfo) + extraherade tecken.

## Metod & verifiering
- Projektägaren laddade ner UNESCO-PDF:erna (unesdoc) och la dem i `files/`. Jag extraherade text lokalt med `pdftotext` och verifierade **extraherbarhet FÖRE godkännande**: sidantal via `pdfinfo`, teckenantal, text/sida-kvot. Alla tre har äkta textlager (inga skannade sidor, inga OCR-artefakter) och slutar vid korrekt baksida/ISBN.
- **Motivering för domänen**: narrativ policy-rapport-stil — en tredje, distinkt skrivform (jämfört med klinisk direktivprosa och RFC-standardtext).

## Korpustabell — realiserad Korpus 3 (UNESCO)

| Dokument | År | Källa (fil) | Sidor | Extraherade tecken | ~tecken/sida | Extraherbar? |
|---|---|---|---|---|---|---|
| Global Education Monitoring Report — Inclusion and education: All means all | 2020 | UNESCO-PDF `373718eng.pdf` (ISBN 978-92-3-100388-2) | 522 | 1 909 644 | 3 658 | ✅ verifierad |
| Reimagining our futures together: A new social contract for education | 2021 | UNESCO-PDF `379707eng.pdf` | 186 | 516 669 | 2 777 | ✅ verifierad |
| Global Education Monitoring Report — Technology in education: A tool on whose terms? | 2023 | UNESCO-PDF `385723eng.pdf` (ISBN 978-92-3-100609-8) | 547 | 2 072 996 | 3 789 | ✅ verifierad |

**Summa: 3 dokument · 1 255 sidor · 4 499 309 extraherade tecken.** Klarar kravet ≥500 sidor med god marginal.
Källfiler: `.pdf` i `files/`; extraherad text: `.txt` bredvid varje PDF.
Licens: UNESCO öppen tillgång (CC BY-SA 3.0 IGO).

## Exkluderade / borttagna
| Dokument | Skäl |
|---|---|
| Tidigare GEM 2023-sammanfattning (txt) | Delmängd av den fullständiga 2023-rapporten (`385723eng`) → borttagen (dubblett). |
| Tidigare GEM 2020-excerpt (txt, ~35 s) | Delmängd av den fullständiga 2020-rapporten (`373718eng`) → borttagen (dubblett). |
| Tidigare GEM 2021/2-excerpt (txt, ~35 s) | Trunkerat verktygs-excerpt; korpusen består nu av kompletta fullrapporter → borttaget för att hålla korpusen fri från trunkerade filer. (2021/2-rapporten kan läggas till som komplett PDF om önskas.) |

## Problemlogg
- Inga skannade PDF:er / OCR-artefakter (verifierat). Extraherbarhet bekräftad före godkännande.
- (Historik: fullrapporter gick ej att fånga komplett via det automatiska hämtningsverktyget p.g.a. ~117 KB-tak; löstes helt via PDF-drop + lokal pdftotext.)

## Avvikelser från plan
- Ingen väsentlig avvikelse kvar. Plan: GEM-fullrapport(er) ~500 s. **Realiserat: 3 kompletta fullrapporter, 1 255 s.** (Not: 2021/2 non-state actors ingår ej som fullrapport; 2020 + 2023 + Reimagining täcker temat med marginal.)

---
*Negative Space · Korpus 3 (UNESCO) · Manifest v1.0 · 2026-07-07*
