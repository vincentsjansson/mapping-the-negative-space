# Lärdomar från Iteration 1 → Mapping the Negative Space

**Syfte med detta dokument:** en fristående brygga. Inte en sammanfattning av hela
"Embracing the Novelty of Noise" — bara det som faktiskt bär över till Negative Space.
Inga D-nummer, θ-värden, τ-värden eller korpusdetaljer från iteration 1 ska återanvändas
rakt av; de var kalibrerade mot en annan korpus och ett annat problem. Det som bär över är
**mönster**, inte siffror.

-----

## 0. Viktigast att veta innan ni börjar: ni har redan kört en pilot på detta

Iteration 1 innehöll en liten RAG-gap-detektionskohort (kallad "Reference Point 3" i
rapporten) som är i praktiken en föregångare till Negative Space. Resultatet:

- **20 agenter** fick var sin lokal, gles korpusregion (5–6 chunkar) och ombads formulera
  en täckningslucka.
- **18 av 20 (90 %)** hallucinerade — de påstod att något saknades fast det fanns någon
  annanstans i korpusen som agenten inte fick se.
- Endast **2 av 20** överlevde bred korpussökning (Nivå 1) + trivialitetsdomare (Nivå 2).
- Mänsklig bedömning (Nivå 3) gjordes **aldrig** — de två överlevande är kandidater, inte
  bekräftade luckor.
- En riktningsbugg hittades: θ_absens användes av misstag för att detektera täckning i
  stället för θ_match — gav 100 % hallucination innan den rättades till 90 %.
- En längd/format-confound hittades: korta enmenings-luckbeskrivningar fick systematiskt
  lägre cosine-similarity mot 400-tecken-chunkar än längre beskrivningar av samma
  sakinnehåll — riskerade att felklassa luckor som frånvarande enbart pga textlängd.

**Konsekvens för er nuvarande design:** er v3-prereg har redan Nivå 1 (bred
korpussökning) som obligatoriskt steg och en trivialitetsdomare i Nivå 2 — det är exakt
rätt, och pilotsiffran (90 % hallucination) är ett konkret argument för *varför* dessa
steg inte får hoppas över eller mjukas upp, även om det känns som onödig friktion när man
bygger. Räkna med en hög confabulationsrate som normalläge, inte avvikelse.

Er längdconfound-lärdom bör generaliseras: **jämför alltid embeddings av jämförbar
textlängd/granularitet**, oavsett om det är en luckbeskrivning mot en chunk eller ett
genererat scenario mot ett ankare. Bygg in en längdnormalisering eller ett diagnostiskt
expansionssteg tidigt i pipelinen, inte som en efterhandsfix.

-----

## 1. Det återkommande mönstret: konfabulering är strukturellt, inte ett buggfall

Tre helt olika instrument i iteration 1 — en frekvensbaserad rankningssignal (N(j)), en
perplexitetsbaserad novelty-detektor (H-S), och RAG-gap-kohorten ovan — visade **samma
underliggande fenomen**: en modell som opererar vid gränsen av sin kunskap producerar text
som är statistiskt likartad oavsett om innehållet är genuint nytt eller påhittat.

Konkret för H-S: minst två genuint novela ankarmeningar fick **högre** perplexitet än fem
av sex nonsensmeningar. Instrumentet kunde inte skilja "ovanligt och sant" från "ovanligt
och påhittat."

**Överförbart till Negative Space:** er mellanmjölks-fälla (A3) och er observation att
"kort avstånd ≠ bra lucka" är samma fenomen i en annan geometri. Det är bra att ni redan
har identifierat det själva och byggt in en tregradig tolkning + obligatorisk
domänadapter-kalibrering. En sak att lägga till: **en ren avstånds- eller
sannolikhetsbaserad signal kommer aldrig ensam kunna lösa koherens/nonsens-separationen.**
Det är inte ett implementationsproblem som mer data löser — det är en instrumentbegränsning
som visade sig upprepade gånger i tre olika former förra iterationen. Planera Nivå 2
(domänadaptern) som den faktiska bärande verifieringen, inte som ett efterhandsfilter på
en i övrigt tillräcklig geometrisk signal.

-----

## 2. Konkreta instrumentförslag för koherens/nonsens-separation (P1 i iteration 1:s "Inverse RAG v2"-skiss)

Rapporten identifierade explicit att koherens-instrumentet är den mest grundläggande
flaskhalsen och föreslog fyra alternativ till ren perplexitet, ingen av dem byggd eller
validerad:

1. **NLI-entailment mot bridge-ankare** — bedöm entailment mellan det genererade scenariot
   och de käll-chunkar det ska brygga mellan. Bedömdes som starkaste kandidaten eftersom
   den ger en domän-förankrad ground truth (ankarna själva) i stället för att luta sig mot
   en generell språkmodells okonditionerade sannolikhet.
2. **Perplexitets-kvot konditionerad på en relevant kontext-chunk** i stället för
   okonditionerad perplexitet — men ärver samma distributionsskifte-svaghet som H-S och bör
   valideras mot en NOVEL/NONSENSE-separationsuppgift innan den används.
3. **Zero-shot LLM-domare med låst rubrik** som specificerar vad intern konsistens betyder
   för just er typ av scenario.
4. **Mänsklig annotering av ett kalibreringsset** — ger samtidigt ground truth för att
   utvärdera de automatiserade alternativen.

Detta är direkt relevant för er domänadapter (Nivå 2) i v3 — särskilt alternativ 1 och 3
är kompatibla med er "prompt-/few-shot ENDAST"-begränsning och kan stärka
mellanmjölks-kalibreringen konkret.

-----

## 3. Geometrisk confounder-mönster (H7) — redan namngivet hos er, här är hur det stängdes delvis

Iteration 1:s starkaste positiva fynd (en resample-instabilitetssignal) hade en olöst
confounder: korrelationen kunde vara driven av ytlig textstatistik (ordlängd, ovanliga ord,
meningskomplexitet) snarare än begreppsmässig nyhet — eftersom embedding-rummet är
ojämnt befolkat av rent formmässiga skäl.

**Vad som gjordes:** en billig, snabb kontroll — regressera/korrelera instabilitets- (eller
i ert fall: gap-) måttet mot enkel textstatistik (ordantal, medelordlängd, meningsantal,
andel sällsynta ord). I iteration 1 var alla sådana korrelationer |ρ| < 0.15 — vilket
uteslöt den enklaste versionen av confoundern men INTE de djupare (embedding-modellspecifik
geometri, mänskligt bedömd nyhet).

**Rekommendation för Negative Space:** kör samma billiga kontroll på era gap-mått (lokalt
gap, kant/outlier) innan ni lägger för mycket vikt vid dem — ni har redan namngett att det
är "samma confounder-klass som H7" (A1b), så lägg till den konkreta, billiga
textstatistik-kontrollen som ett explicit steg snarare än att bara flagga risken. Den kostar
inga API-anrop (ren textstatistik på redan genererat material).

-----

## 4. Pre-registrerings-disciplin som faktiskt höll — värt att kopiera rakt av

Tre praktiker ur iteration 1 fungerade konkret och bör ärvas som standard-arbetssätt, inte
bara som princip:

- **Fel rättades före tolkning, aldrig efter.** En tröskel-riktningsbugg och en
  längd-confound i RAG-pipelinen hittades och rättades innan hallucinationsraten
  beräknades — inte efter att man sett ett obekvämt resultat. Båda tillstånden (före/efter
  rättning) redovisades öppet i stället för att bara visa det korrigerade.
- **Inga hyperparametrar justerades i efterhand för att jaga ett bättre resultat**, även
  när resultaten var svaga (N(j) fick behålla sina låsta värden trots att den till slut
  retirerades).
- **Negativa/inkonklusiva resultat behölls och rapporterades som substantiella fynd**, inte
  som brus att gömma. Det gav faktiskt mer trovärdighet, inte mindre.

Er v3-prereg har redan explicita fallback-regler (t.ex. temperatur-pilotens
böjningspunkt-regel) — bra. Se till att samma disciplin gäller **δ-känslighet** och
**perkentiltröskeln** i Lager 1: om ni testar flera värden, lås regeln för vilket värde som
väljs INNAN ni ser hur många luckor respektive tröskel ger.

-----

## 5. Vad som INTE ska föras över

- Inga konkreta θ-, τ-, δ- eller α/β/k-värden — de var kalibrerade mot en annan
  embedding-geometri och en annan korpus.
- Inget av N(j)-apparaten (frekvens/skevhet-baserad rankning) — den föll strukturellt i
  iteration 1 av skäl som inte är korpus-specifika (den mäter ensemble-beteende, inte
  semantiskt avstånd). Om Negative Space frestas att bygga en liknande
  "ensemble-intern lucka-popularitet"-signal: var medveten om att den typen av mått redan
  visat sig inte spåra det tänkta målet.
- Inga specifika korpusbeslut (Basel III-exkludering, ISO/COSO-provisoriska filer etc.) —
  helt irrelevanta för en ny korpus.

-----

## 6. En öppen fråga värd att ärva medvetet

Iteration 1:s rapport landade i en ospecificerad men namngiven arkitektur-skiss
("Inverse RAG v2") som beskriver nästan exakt Negative Space: kartlägg geometriska luckor
FÖRE generering, generera riktat mot dem, verifiera på två strukturellt oberoende axlar
(avstånd × koherens), och använd RAG retrospektivt för förklaring snarare än detektion.
Den skissen var uttryckligen ovaliderad och spekulativ. Ni bygger nu den skissen på riktigt
— vilket betyder att era Lager 1/Lager 2-beslut i praktiken är det första empiriska testet
av en idé som tidigare bara var teoretisk. Det är värt att hålla i minnet när ni skriver er
egen diskussion: ni testar inte bara "fungerar gap-detektion", ni testar också om den
spekulativa arkitekturskissen från iteration 1 höll.

-----

*Fristående lärdomsdokument. Bygger på `Embracing_the_Novelty_of_Noise_DRAFT_v2.md`
(Vincent Jansson, 2026), avsnitt 3.5, 4.1, 4.2, 4.3 och 4.6. Inga D-nummer eller
projektspecifika värden återges här i normativ mening — se originalrapporten om exakta
siffror behövs.*
