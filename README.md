# EENX15-22-39 - Källkod till kandidatarbetet
## Struktur
Repon innehåller flera mappar varav Modular är den där utveckling fortsättningsvis sker.

LTSpice innehåller kretsscheman för förenklade kretsar. [ej aktiv]

PLECS innehåller ett kretsschema för en trefas växelriktare. [används ej]

PySpice innehåller de skript vi använde för att undersöka användningen av PySpice. Eftersom vi ej fick PySpice att fungera på ett pålitligt sätt utvecklas dessa program ej längre. [används ej]

SyncBuck och Trefas_exempel innehåller inget viktigt och kommer kanske tas bort. [används ej, borttagning?]

Modular är den mapp där utveckling sker för tillfället. Den beskrivs i större detalj nedan.

## Modular
Mappen modular innehåller tre python-filer som beskrivs nedan. 

### Modules.py
Här finns de olika modulerna i drivlinans kretsmodell. Varje modul är sitt eget objekt, inklusive kretsen som helhet. I den sparas alla parametervärden för kretsen, vilket kan utnyttjas i senare skede för maskininlärning. Varje modul har en funktion för att returnera en docstring med sin subcircuits netlist.

### Simulate.py
Detta skript skapar en netlist för hela simuleringen, med de simuleringsparametrar som ska användas. Denna sparas till en fil. Sedan skickar skriptet ett shellkommando till terminalen där Ngspice anropas med netlist-filen som input. Ngspice skriver simuleringsresultatet till en .raw-fil som specificeras av skriptet.

Efteråt kan en mängd olika funktioner för databehandling utföras, varefter önskade parametrar och resultat skrivs till en JSON-fil.

### Functions.py
Denna fil innehåller en mängd olika funktioner för att läsa in simuleringsdataa från en .raw-fil, och bearbeta den datan. Detta inkluderar frekvensanalys med fft, summering av energi i olika frekvensband och den funktion som sparar resultaten till en JSON-fil.

Framöver ska en funktion implementeras som tar de fem huvudsakliga strömmarna in i och ut ur växelriktaren och beräknar det resulterande magnetfältet i ett antal punkter runt drivlinan.

