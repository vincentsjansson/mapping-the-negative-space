# Slutrapport — Korpusinsamling för "Mapping the Negative Space"

**Datum:** 2026-07-07 · **Syfte:** 3 strukturellt olika korpusar (utöver BCM-fallbacken) för att testa om k-formeln för gap-detektionens grannskapsstorlek generaliserar över domäner.

## Sammanställning sida vid sida

| | Korpus 2 — Telekom (RFC) | Korpus 1 — Klinisk (WHO, ej NICE) | Korpus 3 — Utbildning (UNESCO) |
|---|---|---|---|
| **Status** | ✅ KLAR | ✅ KLAR | ✅ KLAR |
| **Antal dokument** | 16 | 3 | 3 |
| **Sidor** | 568 (RFC-paginering) | 369 (pdfinfo) | 1 255 (pdfinfo) |
| **Tecken** | 1 290 499 | 1 002 691 | 4 499 309 |
| **≥500 sidor?** | Ja | **Nästan (369)** – se not | Ja (med marginal) |
| **Extraherbarhet verifierad** | Ja (plaintext) | Ja (pdftotext, ej skannad) | Ja (pdftotext, ej skannad) |
| **Källor** | rfc-editor.org (plaintext) | WHO-PDF (IPC, fysisk aktivitet, mhGAP) | UNESCO-PDF (GEM 2020, Reimagining 2021, GEM 2023) |
| **Licens** | IETF Trust / BCP 78 | CC BY-NC-SA 3.0 IGO | CC BY-SA 3.0 IGO |
| **Skrivform** | Tät, normativ standardtext | Direktiv-lik klinisk prosa | Narrativ policy-rapport |

Varje korpus: källfiler (`.pdf`/`.txt`) + extraherad text (`.txt`) + manifest i `files/`-mappen.

## Avvikelser från plan (öppet redovisade, jämför D-019 iteration 1)

1. **Korpus 1: NICE utgår (beslut C1-A).** Planen var balanserad WHO + NICE. NICE-nedladdningar gav bara sammanfattningar och NICE-kapitel floodade hämtningsverktyget, så NICE ströks helt. Korpusen är **WHO-only**: tre kompletta riktlinjer (IPC 91 s, fysisk aktivitet 104 s, mhGAP 174 s) = **369 s** — marginellt under ~500. En ytterligare WHO-PDF räcker för att passera 500 (se C1-manifest); annars godtas 369 s.

2. **Korpus 2: profilförskjutning.** Flaggskepps-RFC:er (TLS 1.3, HTTP-semantik, QUIC, TCP, DNS, OAuth) översteg fetch-verktygets ~117 KB-tak och uteslöts; ersattes av tematiskt närliggande, komplett fångbara RFC:er (DNSSEC, HTTP/1.1+cookies+HSTS, IPv6-sviten). Täcker fortfarande säkerhet + protokoll + infrastruktur.

3. **Korpus 3: löst via PDF-drop.** De första autonoma försöken trunkerades av ~117 KB-taket (endast sammanfattningar/excerpts). Efter att projektägaren la in fullrapport-PDF:erna extraherades de lokalt utan trunkering: GEM 2020 (522 s), Reimagining (186 s), GEM 2023 (547 s) = **1 255 s**. De tidigare trunkerade excerpt-txt-filerna togs bort (delmängder/trunkerade).

## Metodnot — extraherbarhetsverifiering (hård kravuppfyllelse)
För varje PDF kördes `pdfinfo` (sidantal) och `pdftotext` (extraktion), och text/sida-kvoten kontrollerades för att utesluta skannade/bild-PDF:er. Alla sex PDF:er har äkta textlager (3 045–4 242 tecken/sida för löptextdokument; mhGAP lägre p.g.a. tabeller/flödesscheman), inga OCR-artefakter, och slutar vid korrekt baksida/ISBN. **Inget dokument godkändes utan att extraherbarheten verifierats först.**

## Rekommendation / kvarvarande
- Alla tre korpusarna är redo för nästa pipeline-steg (chunkning/embedding/k-test, `rag_kohort_preregistrering_v3.md`).
- Enda öppna punkten: om **≥500 s** ska gälla strikt även för Korpus 1, lägg en (1) WHO-PDF till i `corpus1_clinical/files/` så extraherar jag den.

## Leverabler
- `corpus2_telecom_rfc/` — 16 RFC-filer + `corpus_manifest_C2_telecom.md`
- `corpus1_clinical/` — 3 WHO-PDF + extraherad text + `corpus_manifest_C1_clinical.md`
- `corpus3_education/` — 3 UNESCO-PDF + extraherad text + `corpus_manifest_C3_education.md`
- `BUILD_LOG.md` (steg-för-steg) · `DROP_LIST_corpus1_and_3.md`

---
*Negative Space · Slutrapport korpusinsamling · uppdaterad 2026-07-07*
