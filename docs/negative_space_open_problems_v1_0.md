# Mapping the Negative Space — Prioriterade forskningsproblem & öppna kritiker

**Fristående dokument · v1.0 · gäller ENDAST "Mapping the Negative Space" (iteration 2)**

> **Notering:** Detta dokument är fristående från "Embracing the Novelty of Noise"
> (iteration 1). Ingen numrering, inga θ/τ/δ-värden eller D-beslut återanvänds därifrån.
> Där ett mönster från iteration 1 är relevant refereras det i löptext till
> `lardomar_iteration1_till_negative_space.md`, aldrig som ett bindande värde.
>
> Detta är ett *referens- och granskningsdokument*, inte ett normativt påståendedokument.
> Det normativa dokumentet är `rag_kohort_preregistrering_v3.md`. När en punkt löses,
> märk den RESOLVED med en enrads-motivering — radera aldrig, så att resonemangsspåret
> bevaras.
>
> **Severity-legend:** [CRITICAL] projekt-invaliderande · [HIGH] underminerar bidraget ·
> [MEDIUM] försvagar rigor · [LOW] polering.
>
> **Status vid skrivande:** Del A/B/C i `rag_kohort_preregistrering_v3.md` är FÖRSLAG,
> ej fattat, ej byggt. Detta dokument skrevs innan Steg 0 (commit) genomfördes.

-----

## TIER 1 — CRITICAL: GRUNDLÄGGANDE VALIDITET

### C1. [CRITICAL] Ingen extern ground truth — designen testar bara sig själv mot sig själv

Den pre-registrerade tolkningstabellen jämför gap-kohorten mot en slumpmässig
kontrollkohort — båda genererade av samma pipeline, mot samma korpus. Det visar om
geometrisk gleshet ger en HÖGRE äkthetsandel än slump, men det visar aldrig om systemet
faktiskt hittar en lucka som **verkligen finns och är värd att hitta**. Utan ett externt
ankare är bästa möjliga utfall "bättre än slump på vårt eget test," inte "hittar riktiga
blinda fläckar."

Jämför med iteration 1: SVB-backtestet gav ett oberoende, externt känt utfall att mäta
mot (även om det utfallet blev negativt — det var ändå en riktig fråga med ett riktigt
facit).

**REQUIRED:** ett leave-one-out-test. Ta bort ett dokument (eller en tydligt avgränsad
sektion) ur korpusen som *känt* täcker ett specifikt ämne. Kör Nivå 0–2 på den beskurna
korpusen. Kontrollera: (a) uppstår en gap-region där det borttagna dokumentets
embedding-grannskap satt, (b) klassar Nivå 2 det resulterande scenariot som icke-trivialt
(det ÄR ju en äkta lucka, konstruerad men verklig). Kostar inga extra API-anrop utöver
vad som redan är planerat — bara en extra körning på en beskuren korpus.

**Mätvärde som visar att C1 är stängd:** Minst ett leave-one-out-experiment dokumenterat
med resultat, oavsett utfall (positivt eller negativt är båda rapporterbara, i linje med
pre-registreringsprincipen).

> **STATUS: öppet.** Inte adresserat i v3. Bör läggas till som ett eget steg i Lager 1
> eller som ett tillägg till Steg 0.5, före produktionskörning.

### C2. [CRITICAL] Distance concentration i högdimensionellt rum — hotar hela Nivå 0

Lager 1 motiverar ball-tree med att KD-tree degraderar i 384 dimensioner — det är en
implementations-detalj, inte en lösning på ett djupare statistiskt fenomen: i
högdimensionella rum tenderar avstånd mellan punkter att **koncentreras** (skillnaden
mellan närmaste och längsta granne krymper som andel av det totala avståndet). Det är ett
annat fenomen än hubness/anisotropi (som redan är namngivet som ärvd risk från H7/H4 i
iteration 1) — det handlar inte om att vissa punkter blir populära grannar, utan om att
ALLA punkter riskerar att se ungefär lika långt bort ut från varandra, vilket urholkar
själva idén med en NN-distans-baserad "gap"-signal oavsett vilken sökalgoritm som används.

**REQUIRED:** karakterisera embedding-rummets faktiska avståndsfördelning empiriskt
(samma typ av övning som iteration 1:s embedding-karakterisering) INNAN percentiltröskeln
låses. Om avstånden är starkt koncentrerade (liten spridning runt medelvärdet) är
90:e-percentil-regeln ett svagt signal-till-brus-mått, och det bör vägas in eller
kompenseras (t.ex. genom att normalisera avstånd mot den lokala tätheten, inte bara mot
ett globalt percentiltak).

> **STATUS: öppet.** Bör göras som en del av Steg 0.5 (instans-kalibrering), inte antas
> bort genom valet av sökstruktur.

### C3. [CRITICAL] Fas 2:s "tydlig fasövergång"-bedömning är okvantifierad

Regeln för att låsa de tre temperaturvärdena bygger på att identifiera en "böjningspunkt"
i förändringstakten av svar↔käll-avstånd. Men vad som räknas som en tillräckligt "tydlig"
böjningspunkt (för att inte falla tillbaka på 0,2/0,5/0,9) är inte definierat matematiskt
— det lämnas åt att bedöma kurvan visuellt. Detta är exakt den typ av efterhandstolkning
pre-registrering ska förhindra: två personer kan se samma kurva och dra olika slutsatser,
och ingen av dem bryter mot någon regel eftersom ingen regel finns.

**REQUIRED:** ersätt "tydlig fasövergång, ögonmått" med ett objektivt, förutbestämt
kriterium — t.ex. en tröskel på andraderivatans absolutvärde, eller ett formellt
change-point-detection-test (t.ex. PELT eller ett Bayesianskt brytpunktstest) med en
förutbestämd signifikansnivå. Kriteriet ska låsas INNAN pilotsvepets kurva ses, inte
anpassas efter att kurvan är genererad.

**Mätvärde som visar att C3 är stängd:** Ett explicit, numeriskt formulerat kriterium
skrivet in i Lager 2 (Fas 2) i `rag_kohort_preregistrering_v3.md`, före pilotkörning.

> **STATUS: öppet.** Direkt blockerande för Steg 0.5 (Temperatur-pilot/-låsning) —
> bör lösas innan Fas 1 körs, inte efteråt.

-----

## TIER 2 — HIGH: VETENSKAPLIGT BIDRAG & METOD

### H1. [HIGH] Domänadaptern (Nivå 2) är en LLM som dömer LLM-genererat innehåll — samma konfabuleringsrisk flyttad en nivå upp

Att döpa till "trivialitetsdomare, kalibrerad med mellanmjölks-exempel" löser inte
strukturellt att domaren själv kan konfabulera ett övertygande men felaktigt omdöme —
precis det mönster som redan visat sig upprepade gånger i iteration 1 (H-S kunde inte
skilja novelt från nonsens; RAG-pilotens 90 % hallucinationsrate). Ett enskilt few-shot-
kalibreringsexempel räcker inte för att strukturellt utesluta detta.

**REQUIRED:** en billig inter-rater-kontroll redan i PoC-skedet — låt en andra, oberoende
domare (annan modell, eller en liten handfull manuellt granskade fall) bedöma samma
delmängd av Nivå 2-utfall. Om de två domarna systematiskt är oense indikerar det att
domänadaptern själv är instabil, inte bara att enskilda fall är svåra.

> **STATUS: öppet.** Kräver inga nya genereringar — kan läggas till som en analys av
> redan planerade Nivå 2-utfall.

### H2. [HIGH] Endast ETT obligatoriskt kalibreringsexempel (mellanmjölk) — täcker sannolikt inte alla failure modes

Mellanmjölks-fällan är en specifik, namngiven failure mode. Det finns sannolikt fler:
generisk floskel utan mellanmjölks-geometri, överdrivet självsäkert men innehållslöst
påstående, korrekt-låtande men i själva verket allmänt känd branschkunskap. Ett enda
few-shot-exempel riskerar att kalibrera domänadaptern mot just den ena fällan och lämna
de andra okontrollerade.

**REQUIRED:** utöka det obligatoriska kalibreringsexemplet till 2–3 exempel som täcker
distinkta typer av falska positiva, inte bara mellanmjölk.

> **STATUS: öppet.**

### H3. [HIGH] Längdnormalisering är en identifierad lärdom men inte explicit inskriven i Nivå 1:s spec

`lardomar_iteration1_till_negative_space.md` flaggar att jämförelser mellan text av olika
längd/granularitet (kort luckbeskrivning mot lång chunk) systematiskt kan ge missvisande
cosine-similarity. Detta ledde till konkreta felklassningar i iteration 1:s RAG-pilot. Men
Nivå 1 ("sök hela C, verkligen frånvarande?") i v3-byggspecen nämner ingen
längd-/granularitetssäkring — den antas implicit täckas av "generell försiktighet."

**REQUIRED:** skriv in en explicit längdnormaliseringsprocedur (eller ett diagnostiskt
expansionssteg) i Steg 5 (Nivå 1) i byggspecen, inte som en efterhandsfix om problemet
väl upptäcks.

> **STATUS: öppet.**

-----

## TIER 3 — MEDIUM: RIGOR, GENERALISERBARHET, MÄTNING

### M1. [MEDIUM] k-formeln (k = max(3, round(0,5 · ln(N)))) är en omotiverad heuristik

Formen (logaritmisk skalning, koefficient 0,5) är rimlig-låtande men inte härledd ur
något — varken en teoretisk grund eller en empirisk känslighetsanalys.

**REQUIRED:** antingen en kort motivering för valet av funktionsform och koefficient,
eller en snabb känslighetsanalys mot ett par alternativa k-värden innan formeln låses
permanent i Lager 1.

> **STATUS: öppet.**

### M2. [MEDIUM] Ingen minsta korpusstorlek pre-registrerad

Om Negative Space ska demonstrera domänagnosticism kommer det sannolikt att köras på
mindre, verkliga företagskorpusar — betydligt mindre än BCM-fallback-korpusens 7 000+
chunkar. Percentiltrösklar och NN-baserade mått blir statistiskt svagare och mer
brusiga vid låg N (jämförbart med hur top-20-overlappets chans-golv i iteration 1 blev
ett problem vid små urval).

**REQUIRED:** pre-registrera antingen en minsta korpusstorlek för att metoden ska anses
tillförlitlig, eller ett explicit varningskriterium som triggas vid låg N och som
rapporteras tillsammans med resultatet.

> **STATUS: öppet.**

### M3. [MEDIUM] Fallback-korpusen (BCM, D-018) ärver kända brister som måste omflaggas, inte antas lösta

Om instans #1 blir BCM-korpusen (fallback vid saknad extern korpus) följer dess kända
begränsningar med: ISO/COSO på provisoriska filer, oklart dokumentantal (9 vs. 10). Dessa
är redan dokumenterade i iteration 1, men måste flaggas explicit på nytt i Negative
Space-rapporten om den korpusen används — inte tyst ärvas som "redan löst."

> **STATUS: villkorat öppet** — relevant endast om BCM-fallbacken faktiskt aktiveras.

-----

## TIER 4 — LOW: FRAMING, POSITIONERING, DEFENSIVE DEPTH

### L1. [LOW] Inget eget litet glossar ännu

Negative Space har redan välformade begrepp (lokalt gap, kant/outlier, mellanmjölk,
äkta lucka) men de är spridda över Del A/B i prereg-dokumentet snarare än samlade i en
egen auktoritativ ordlista. Ett kort glossar tidigt minskar risken att "lucka" eller
"blind fläck" glider in i formell text som bekräftat faktum innan Nivå 3 är gjord — ett
mönster som redan medvetet undviks i A1, men som är lättare att hålla konsekvent med ett
skrivet referensdokument.

> **STATUS: öppet, låg prioritet.**

### L2. [LOW] "Mest säljbara produktriktningen"-framing bör hanteras försiktigt

Precis som N(j) och H-I i iteration 1 inte fick beskrivas som validerade förrän de var
empiriskt testade, bör Negative Space inte beskrivas som produktklart förrän minst
leave-one-out-testet (C1) och helst Nivå 3 finns med. Detta är en skrivdisciplin-fråga,
inte ett tekniskt problem.

> **STATUS: hålls i minnet, ingen åtgärd krävs förrän rapportskrivning.**

-----

## SAMMANFATTNING — VAD SOM BLOCKERAR VAD

- **C3 blockerar Steg 0.5** (Temperatur-pilot/-låsning) direkt — bör lösas innan Fas 1.
- **C2 bör göras som en del av Steg 0.5** (instans-kalibrering) parallellt med θ_absens-
  omkalibrering.
- **C1 kräver ett extra experiment** men inga nya arkitekturbeslut — kan läggas in i
  Lager 1 eller köras separat efter Steg 0.5.
- **H1–H3** kräver inga nya genereringar utöver vad som redan planeras — analyser av
  redan producerat material.
- **M1–M3** är låg-kostnad att lösa men bör beslutas innan respektive tröskel/formel
  låses permanent, i linje med pre-registreringsdisciplinen.

Ingen av dessa kräver att v3-designens grundstruktur (Nivå 0–3, tvålagers-prereg,
tregradig avståndstolkning) skrivs om. De är skärpningar av en redan solid design, inte
invändningar mot dess kärna.

-----

*Mapping the Negative Space · Prioriterade forskningsproblem & öppna kritiker · v1.0 ·
Fristående från Embracing the Novelty of Noise. Skrivet före Steg 0 (commit).*
