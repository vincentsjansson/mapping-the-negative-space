# Korpus 2 — Telekomstandarder (IETF RFC) · Korpusmanifest

> Levande dokument. Hör ihop med Negative Space-korpusinsamlingen (iteration 2).
> Format speglar `corpus_manifest_D018.md` från iteration 1.
> v1.0 · 2026-07-05 (realiserad korpus dokumenterad)
> Syfte: en av tre strukturellt olika korpusar för att testa om k-formeln för
> gap-detektionens grannskapsstorlek generaliserar över domäner (se `rag_kohort_preregistrering_v3.md`, Lager 1).

---

## Insamlingsbeslut — sammansättning och avgränsning

- **Datum**: 2026-07-05
- **Kategori**: Korpus (Negative Space, iteration 2)
- **Fråga**: Vilka IETF-RFC:er ska ingå i telekom-korpusen, och hur säkras att varje fil är legitimt fritt tillgänglig och har komplett, extraherbar text före godkännande?
- **Valt alternativ**: Ett tematiskt brett urval av **16 RFC:er** i den kanoniska plaintext-formen (`rfc-editor.org/rfc/rfcNNNN.txt`), fördelat över tre kluster — **nätverkssäkerhet**, **kärnprotokolldesign** och **internetinfrastruktur**. Användaren efterfrågade "alla tre" RFC-teman; de samlas därför som **ETT** telekom-korpus som spänner över alla tre klustren (inte tre separata korpusar), vilket bevarar tre-korpus-designen där klinisk / telekom / utbildning är de strukturellt distinkta domänerna.
- **Hård kvalitetsgrind (körd FÖRE godkännande, inte efteråt)**: Varje fil verifierades vara **komplett** med en innehållsbaserad kontroll — sista icke-tomma raden måste vara antingen en sidfot `[Page N]` eller ett "Authors' Addresses"/"Full Copyright"-block. Filer som slutade mitt i en mening eller mitt i ett ord underkändes och lades **inte** in. Detta fångade flera avkortade filer som en ren storleksgrind hade släppt igenom (se problemloggen).
- **Motivering**: RFC-arkivet är fritt tillgängligt, redan i extraherbar plaintext (ingen OCR, inga skannade sidor), och strukturellt motsatt narrativ policy-prosa — tät, normativ, mycket strukturerad text. Det gör det till ett rent test av om gap-geometrin (och k) beter sig annorlunda i en icke-narrativ domän.
- **Beslutat av**: Projektägare (Vincent) + AI-kollaboratör

---

## Proveniens och licens (gäller alla filer)

- **Källa**: RFC Editor, `https://www.rfc-editor.org/rfc/rfcNNNN.txt` (kanonisk plaintext).
- **Licensstatus**: IETF-dokument. Upphovsrätt IETF Trust / bidragsgivare; omfattas av **BCP 78 (IETF Trust Legal Provisions Relating to IETF Documents)**. Fritt tillgängliga och fritt reproducerbara i sin helhet; ingen betalvägg, ingen medlemslåsning. Lämpliga att chunka/embedda i nästa pipeline-steg utan licensproblem.
- **Åtkomstdatum**: 2026-07-05.
- **Extraherbarhet**: Trivial — filerna ÄR plaintext. Verifierad komplett per fil (se kolumn nedan).
- **Sidräkning**: "Sidor" = högsta `[Page N]`-sidfoten i dokumentet (RFC:ernas egen paginering). RFC 9112 är i det opaginerade v3-formatet utan sidfötter; dess **44 sidor** är den officiella sidräkningen från RFC Editor. Teckenantal (`chars`) är objektivt grundmått.

---

## Korpustabell — realiserad Korpus 2 (16 dokument)

### Kluster A — Nätverkssäkerhet

| Dokument | RFC | År | Källa | Motivering för inkludering | Sidor | Tecken |
|---|---|---|---|---|---|---|
| DNS Security Introduction and Requirements | 4033 | 2005 | rfc-editor (txt) | DNSSEC-ramverkets grund; säkerhetsmodell och hot | 21 | 52 439 |
| Resource Records for the DNS Security Extensions | 4034 | 2005 | rfc-editor (txt) | DNSSEC-postformat; tät normativ specifikation | 29 | 63 873 |
| TLS Extensions: Extension Definitions | 6066 | 2011 | rfc-editor (txt) | Transportlagersäkerhet; tillägg till TLS 1.2 | 25 | 55 073 |
| HTTP State Management Mechanism (Cookies) | 6265 | 2011 | rfc-editor (txt) | Cookie-semantik och säkerhetsöverväganden | 37 | 79 718 |
| HTTP Strict Transport Security (HSTS) | 6797 | 2012 | rfc-editor (txt) | Webbsäkerhetspolicy-mekanism | 46 | 103 548 |
| X.509 PKI Online Certificate Status Protocol (OCSP) | 6960 | 2013 | rfc-editor (txt) | Certifikatstatus/PKI; säkerhetsinfrastruktur | 41 | 82 031 |
| JSON Web Token (JWT) | 7519 | 2015 | rfc-editor (txt) | Token-baserad autentisering; kompakt claims-format | 30 | 63 033 |

### Kluster B — Kärnprotokolldesign

| Dokument | RFC | År | Källa | Motivering för inkludering | Sidor | Tecken |
|---|---|---|---|---|---|---|
| HTTP/1.1 | 9112 | 2022 | rfc-editor (txt) | Kärnprotokoll; meddelandesyntax och anslutningshantering | 44* | 109 905 |
| The Atom Syndication Format | 4287 | 2005 | rfc-editor (txt) | XML-baserat innehållsprotokoll; formell datamodell | 43 | 81 916 |

### Kluster C — Internetinfrastruktur

| Dokument | RFC | År | Källa | Motivering för inkludering | Sidor | Tecken |
|---|---|---|---|---|---|---|
| Dynamic Host Configuration Protocol (DHCP) | 2131 | 1997 | rfc-editor (txt) | Adresstilldelning; grundläggande nätverksinfrastruktur | 45 | 113 732 |
| RIP Version 2 | 2453 | 1998 | rfc-editor (txt) | Routingprotokoll; distansvektor | 39 | 98 456 |
| Dynamic Configuration of IPv4 Link-Local Addresses | 3927 | 2005 | rfc-editor (txt) | Länklokal adressering; autokonfiguration | 33 | 83 096 |
| IP Version 6 Addressing Architecture | 4291 | 2006 | rfc-editor (txt) | IPv6-adressmodell; textrepresentation | 25 | 52 891 |
| IPv6 Stateless Address Autoconfiguration | 4862 | 2007 | rfc-editor (txt) | IPv6 SLAAC; duplicate address detection | 30 | 72 476 |
| The Syslog Protocol | 5424 | 2009 | rfc-editor (txt) | Loggningsinfrastruktur; meddelandeformat | 38 | 85 156 |
| Internet Protocol, Version 6 (IPv6) Specification | 8200 | 2017 | rfc-editor (txt) | Kärn-IPv6-specifikation; header och extension headers | 42 | 93 156 |

\* RFC 9112 är opaginerad (v3-format); 44 sidor är RFC Editors officiella sidräkning. Verifierad komplett via "Authors' Addresses"-slut.

**Summa: 16 dokument · 568 sidor (524 från `[Page N]`-sidfötter + 44 för opaginerade RFC 9112) · 1 290 499 tecken.** Klarar kravet ≥ ~500 sidor.

---

## Exkluderade dokument (övervägda men uteslutna)

Dessa RFC:er övervägdes och hämtades men uteslöts. **Skäl redovisas öppet — inget tystades.**

| Dokument | RFC | Skäl för exkludering |
|---|---|---|
| Transmission Control Protocol (original TCP) | 793 | Avkortad av fetch-verktyget (~133 KB, slutade mitt i mening "Otherwise return error:"). Kunde inte fångas komplett; utesluten hellre än att lägga in en trunkerad fil. |
| Domain Name System (DNS) | 1035 | Avkortad (~120 KB, slutade mitt i referenslista). Grundläggande men ej komplett fångbar via tillgängligt verktyg. DNSSEC-RFC:erna (4033/4034) täcker DNS-domänen delvis. |
| Protocol Modifications for the DNS Security Extensions | 4035 | Avkortad (~95 KB, slutade mitt i ett zonexempel "ns2.b.examp"). Notera: trunkering skedde UNDER storleksgränsen — fångades endast av den innehållsbaserade kontrollen. |
| Internet Message Format | 5322 | Avkortad (~110 KB, slutade "2" mitt i appendixlista). |
| The WebSocket Protocol | 6455 | Avkortad (~114 KB, slutade mitt i mening i avsnitt 9.1). |
| JSON Web Signature (JWS) | 7515 | Avkortad vid sidan 39 av 59 (slutade mitt i en sidfot utan `[Page N]`). Hade felaktigt godkänts av en tidig storleksgrind; den strängare innehållskontrollen fångade den. |
| CMS (Cryptographic Message Syntax) | 5652 | Avkortad (~118 KB, slutade mitt i referens "[CMS3] Housley..."). |
| OAuth 2.0 Authorization Framework | 6749 | Avkortad (~128 KB, slutade "In order to prevent man-in-th..."). |
| ICMP (RFC 792), ARP (RFC 826), JSON (RFC 8259), ICMPv6 (RFC 4443) | — | Kompletta men **för små** — returnerades inline av fetch-verktyget utan att sparas till disk, och kunde därför inte relokeras till korpusmappen som fil. Uteslutna för att undvika manuell rekonstruktion. TLS 1.3 (RFC 8446), HTTP-semantik (RFC 9110) och QUIC (RFC 9000) uteslöts på samma trunkeringsgrund som ovan — alla > taket. |

---

## Problemlogg (öppet redovisad)

1. **Fetch-verktygets tak (~118–128 KB per dokument).** Det sanktionerade hämtningsverktyget kapar innehåll bortom ~118–128 KB och trunkerar tyst. Konsekvens: stora RFC:er (TLS 1.3, HTTP-semantik, TCP, DNS, OAuth 2.0) kunde inte fångas kompletta och uteslöts. Korpusen bygger därför på små-till-medelstora RFC:er (21–46 sidor styck).
2. **Storleksgrind var otillräcklig — bytte till innehållsbaserad verifiering.** En första grind ("filer < 115 KB = kompletta") visade sig FEL: minst två filer (RFC 4035 vid 95 KB, RFC 7515 vid 92 KB) trunkerades UNDER 115 KB eftersom taket är token- inte byte-baserat (täta base64-/tabelltunga RFC:er tokeniseras "dyrare"). Åtgärd: varje fil verifieras nu genom att sista icke-tomma raden är en `[Page N]`-sidfot eller ett Authors'-Addresses/Full-Copyright-block. Detta i enlighet med iteration 1:s princip *verifiera FÖRE godkännande, inte efteråt*.
3. **Små RFC:er returneras inline, ej till disk.** Fetch-verktyget visar små svar direkt i resultatet utan att spara en fil. Sådana RFC:er (792, 826, 8259, 4443) kunde inte relokeras till korpusmappen och uteslöts hellre än att rekonstrueras manuellt (rekonstruktionsfel-risk).
4. **Inga skannade PDF:er / OCR-artefakter** — ej relevant för denna korpus (ren plaintext från källan). Extraherbarhet är trivialt uppfylld.

---

## Avvikelser från ursprunglig plan

- **Planen nämnde ett tematiskt kluster (t.ex. nätverkssäkerhet).** Användaren begärde i stället alla tre klustren. Realiserat som ETT telekom-korpus över säkerhet + protokoll + infrastruktur. Klustertillhörighet anges per dokument ovan.
- **Flera "flaggskepps"-RFC:er (TLS 1.3, HTTP-semantik/HTTP-2/3, QUIC, TCP, DNS) saknas** p.g.a. fetch-takets trunkering, inte p.g.a. relevans. De ersattes av tematiskt närliggande, komplett fångbara RFC:er (DNSSEC för DNS-säkerhet; HTTP/1.1 + cookies + HSTS för HTTP; IPv6-sviten för kärninfrastruktur). Detta ändrar korpusens *ålders-* och *längdprofil* (fler klassiska, kortare RFC:er) men inte dess domänkaraktär.

---

*Negative Space · Korpus 2 (Telekom/RFC) · Manifest v1.0 · 2026-07-05*
