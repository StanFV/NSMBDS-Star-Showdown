# NSMB DS Versus

Een rom hack van **New Super Mario Bros. (DS, Europese versie)** die volledig draait om de Mario vs Luigi modus. De hack voegt vijf nieuwe VS-stages toe en haalt de story mode eruit, waardoor de ROM bijna de helft kleiner wordt.

Deze repository bevat geen ROM en geen materiaal van Nintendo. Het bouwscript past alle wijzigingen toe op je eigen, legaal verkregen ROM.

## Wat zit erin

**Tien stages in Mario vs Luigi.** Het stagekeuzemenu heeft nu twee pagina's. Met **L** of **R** wissel je tussen de vijf originele stages en vijf nieuwe stages. De thumbnails wisselen mee en onder "Select a course." staat een hint. Elke nieuwe stage hoort bij het thema van de originele stage op dezelfde plek:

| Plek | Nieuwe stage | Thema | Kort ontwerp |
|---|---|---|---|
| 1 | Heuvelrug | gras | hoge centrale heuvel, twee verhoogde uiteinden, drie afgronden |
| 2 | Steengroeve | ondergronds | symmetrische grot met richels op vijf hoogtes |
| 3 | IJsbaan | ijs | brede sneeuwvlakte met ijsplatforms en hoogteverschillen |
| 4 | Buizenstelsel | pijpen | pijpen van verschillende hoogte, piranhaplanten, zij-warps |
| 5 | Kantelen | kasteel | vier torens, een lange brug en een lage middenmuur |

De instelling **Course: Random** kiest nu uit alle tien de stages. Wisselen en willekeurig kiezen blijven gesynchroniseerd tussen beide spelers.

**Geen story mode meer.** De knop "Mario Game" in het titelmenu start nu ook Mario vs Luigi. Alle bestanden die alleen door de story mode gebruikt worden (levels van wereld 1 tot en met 8, wereldkaart, eindfilmpje en aftiteling) zijn verwijderd. De ROM gaat daardoor van 33,5 MB naar ongeveer 18 MB. Minigames en Options werken gewoon.

## Bouwen

Je hebt nodig:

* Python 3.10 of nieuwer
* de Europese ROM `New Super Mario Bros. (Europe) (En,Fr,De,Es,It).nds` (SHA-1 `b0f7886720e842ed922569e1bb5c39c0fa090331`)
* optioneel `xdelta3` om ook een patchbestand te maken

```bash
pip install -r requirements.txt
python3 build.py "New Super Mario Bros. (Europe) (En,Fr,De,Es,It).nds"
```

Het resultaat komt in `out/`:

* `NSMB-DS-Versus.nds` is de gepatchte ROM
* `NSMB-DS-Versus.xdelta` is een patch om te delen (alleen als xdelta3 geinstalleerd is)
* `previews/` bevat een overzichtsafbeelding per stage en de thumbnails

Met `--keep-story` blijft de story mode staan; dan worden alleen de nieuwe stages toegevoegd.

## Spelen

Mario vs Luigi heeft twee DS-systemen nodig. Op een emulator gaat dat met melonDS: kies in het eerste venster *System → Multiplayer → Launch new instance* en laad de ROM ook in het tweede venster. Kies in beide "Mario Vs. Luigi" en daarna "Compete with another New Super Mario Bros. owner". De host kiest de stage en wisselt met L of R van pagina.

## Hoe het werkt

In VS-modus laadt de game stages niet uit de gewone mappen maar uit een archief per stage (`ARCHIVE/Dat_Field.narc`, `Dat_Basement`, `Dat_Ice`, `Dat_Pipe` en `Dat_Fort`). Zo'n archief bevat de tileset, de achtergrond en de levelbestanden. De nieuwe stages worden aan het archief van hun thema toegevoegd, zodat tileset en vijanden altijd beschikbaar zijn.

De code-aanpassingen (Europese versie):

| Adres | Wat |
|---|---|
| `0x0219A100` | extra autoload-sectie van de ARM9 met eigen code, de paginavariabele, de bestandstabellen en de thumbnails van beide pagina's; de heap begint daardoor iets later (literal op `0x02055EF8`) |
| `0x02029D54` | tabel met archieven; de bovengrens van de vijf stage-archieven is verhoogd |
| ov052 `0x02160E54` | einde van `getStage()`: schrijft de bestands-ID's van de gekozen pagina in de coursetabel (`0x0202C8C4` en `0x0202C5DC`) |
| ov052 `0x02161B30` | update van het stagekeuzescherm: L/R wisselt de pagina en de thumbnails worden in VRAM bijgewerkt |
| ov052 `0x02161FAC` en `0x02161FC4` | Random kiest uit tien in plaats van vijf |
| ov009 `0x020E5148` | knop "Mario Game" springt naar Mario vs Luigi |
| `menu_title_E??.narc` bericht 12 | hinttekst voor L/R in vijf talen |

De invoer in het stagekeuzemenu wordt tussen beide DS-systemen gesynchroniseerd, net als de toevalsgenerator. Daardoor komen beide spelers altijd in dezelfde stage terecht.

### Mappen

* `build.py` bouwt alles
* `levels/stages.py` bevat de ontwerpen van de vijf stages als Python-code
* `tools/nsmblevel.py` leest en schrijft het levelformaat van NSMB
* `tools/nsmbgfx.py` rendert levels naar PNG voor previews en thumbnails
* `tools/stagebuilder.py` bevat hulpfuncties voor het ontwerpen
* `tools/codepatch.py` bevat de ARM-assembly en de patches
* `tools/bmg.py` bewerkt berichtbestanden

## Getest

* Alle vijf nieuwe stages in een echte 2-speler sessie met twee melonDS-instanties (lokale draadloze verbinding), inclusief pagina wisselen en Random.
* De stages in DeSmuME in single-player om tegels, vijanden en blokken te controleren.
* Titelmenu, Minigames en Options na het verwijderen van de story mode.

Nog niet getest: echte hardware en DS Download Play (spelen met iemand zonder cartridge). De nieuwe stages staan in dezelfde archieven die Download Play gebruikt, dus het zou moeten werken.

## Bekende beperkingen

* Op de knop in het titelmenu staat nog "Mario Game".
* Het "Ready!"-scherm en het uitslagscherm tonen de naam en afbeelding van de originele stage op dezelfde plek.
* Alleen de Europese versie wordt ondersteund.

## Dank

Het levelformaat is gebaseerd op het werk van NSMB Editor (Dirbaio en anderen) en de NSMB Code Reference van het Mamma Mia Team.
