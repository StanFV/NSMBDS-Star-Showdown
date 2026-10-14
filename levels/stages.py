"""De vijf nieuwe Mario vs Luigi stages.

Elke stage hoort bij een thema-archief van een originele stage en gebruikt
daardoor dezelfde tileset, achtergrond en vijanden:

  slot 0  Dat_Field     (basis J01)  ->  Heuvelrug
  slot 1  Dat_Basement  (basis J02)  ->  Steengroeve
  slot 2  Dat_Ice       (basis J03)  ->  IJsbaan
  slot 3  Dat_Pipe      (basis J04)  ->  Buizenstelsel
  slot 4  Dat_Fort      (basis J05)  ->  Kantelen

Coordinaten zijn in tegels van 16x16 pixels.
"""
from stagebuilder import (StageBuilder, T0, T1, BRICK, QBLOCK_COIN, QBLOCK_ITEM,
                          BRICK_ITEM, USED_BLOCK, STONE, PIPE)

# Terreinsets (tileset 1 objectnummers) die in de standaard "I_M" tilesets
# dezelfde betekenis hebben (gras, sneeuw).
STD_KIT = dict(tl=7, top=10, tr=9, left=6, right=8, fill=1, bl=12, bottom=11, br=13)


def _is(o, ts, num):
    return o.tileset == ts and o.num == num


def heuvelrug(base):
    """Grasland met een hoge centrale heuvel en twee verhoogde uiteinden."""
    b = StageBuilder(base,
                     keep_objects=lambda o: _is(o, T0, 2),           # onzichtbare hulpobjecten
                     keep_sprites=lambda s: s.type in (195, 196))    # wrap-markeringen
    k = STD_KIT
    # Grond (view is 64 x 18 tegels, onderste rij is y=17)
    b.box(0, 14, 11, 17, k, open_left=True)
    b.box(15, 16, 25, 17, k)
    b.box(28, 11, 35, 17, k)            # centrale heuvel
    b.box(38, 16, 48, 17, k)
    b.box(52, 14, 63, 17, k, open_right=True)
    # Zwevende blokken
    b.block_row(BRICK, 3, 10, 6).obj(T0, QBLOCK_ITEM, 5, 10).obj(T0, QBLOCK_COIN, 6, 10)
    b.block_row(BRICK, 17, 12, 3).obj(T0, QBLOCK_COIN, 20, 12).block_row(BRICK, 21, 12, 3)
    b.block_row(BRICK, 26, 7, 12).obj(T0, QBLOCK_ITEM, 31, 7).obj(T0, QBLOCK_ITEM, 32, 7)
    b.block_row(BRICK, 40, 12, 3).obj(T0, QBLOCK_COIN, 43, 12).block_row(BRICK, 44, 12, 3)
    b.block_row(BRICK, 55, 10, 6).obj(T0, QBLOCK_COIN, 57, 10).obj(T0, QBLOCK_ITEM, 58, 10)
    b.block_row(BRICK, 12, 6, 3).block_row(BRICK, 49, 6, 3)
    # Munten
    b.coins(4, 8, 4).coins(56, 8, 4).coins(29, 5, 6).coins(13, 4, 1).coins(50, 4, 1)
    b.coins(12, 12, 3).coins(49, 12, 3).coins(30, 9, 4)
    # Vijanden
    b.sprite(148, 20, 15).sprite(148, 43, 15).sprite(149, 8, 13).sprite(149, 56, 13)
    # Sterpunten
    for x, y in ((6, 8), (20, 10), (31, 5), (43, 10), (57, 8), (13, 4), (50, 4), (31, 10), (2, 13)):
        b.star(x, y)
    b.spawns((3, 13), (60, 13))
    return b


def steengroeve(base):
    """Ondergrondse grot van stenen met symmetrische richels op vijf hoogtes."""
    b = StageBuilder(base,
                     keep_sprites=lambda s: s.type in (195, 196, 80))
    W = 32
    # Vloer (twee rijen) met een stenen verhoging in het midden
    b.block_row(BRICK, 0, 20, 12).block_row(BRICK, 20, 20, 12)
    b.obj(T0, BRICK, 0, 21, 12, 3).obj(T0, BRICK, 20, 21, 12, 3)
    b.obj(T1, 7, 12, 20).obj(T1, 10, 13, 20, 6, 1).obj(T1, 9, 19, 20)
    b.obj(T1, 6, 12, 21, 1, 3).obj(T1, 8, 19, 21, 1, 3).obj(T1, 3, 13, 21, 6, 3)
    # Pilaren naast het midden
    b.obj(T0, BRICK, 9, 17, 1, 3).obj(T0, BRICK, 22, 17, 1, 3)
    # Richels (spiegelbeeldig)
    b.block_row(BRICK, 2, 16, 5).block_row(BRICK, W - 7, 16, 5)
    b.obj(T0, QBLOCK_ITEM, 4, 16).obj(T0, QBLOCK_ITEM, W - 5, 16)
    b.block_row(BRICK, 10, 13, 12).obj(T0, QBLOCK_COIN, 14, 13).obj(T0, QBLOCK_COIN, 17, 13)
    b.block_row(BRICK, 0, 10, 6).block_row(BRICK, W - 6, 10, 6)   # loopt door over de wrap-rand
    b.obj(T0, BRICK_ITEM, 3, 10).obj(T0, BRICK_ITEM, W - 4, 10)
    b.block_row(BRICK, 12, 7, 8).obj(T0, QBLOCK_ITEM, 15, 7).obj(T0, QBLOCK_ITEM, 16, 7)
    b.block_row(BRICK, 6, 4, 3).block_row(BRICK, W - 9, 4, 3)
    # Munten
    b.coins(14, 18, 4).coins(3, 14, 3).coins(W - 6, 14, 3).coins(12, 11, 2).coins(18, 11, 2)
    b.coins(1, 8, 4).coins(W - 5, 8, 4).coins(14, 5, 4).coins(7, 2, 1).coins(W - 8, 2, 1)
    # Vijanden
    b.sprite(148, 5, 19).sprite(148, W - 6, 19).sprite(149, 15, 12, bytes([0, 0, 1, 0, 0, 0]))
    # Sterpunten
    for x, y in ((15, 18), (4, 14), (W - 5, 14), (15, 11), (2, 8), (W - 3, 8), (15, 5), (7, 2), (W - 8, 2)):
        b.star(x, y)
    b.spawns((4, 19), (W - 5, 19))
    return b


def ijsbaan(base):
    """Brede sneeuwvlakte met ijsplatforms en drie afgronden."""
    b = StageBuilder(base,
                     keep_objects=lambda o: _is(o, T0, 2),
                     keep_sprites=lambda s: s.type in (195, 196))
    k = STD_KIT
    ICE = 32
    # Grondstukken: (x0, x1, bovenkant)
    ground = [(0, 16, 25), (21, 36, 23), (37, 45, 25), (50, 61, 21), (62, 70, 25),
              (75, 89, 23), (90, 97, 25), (102, 114, 22), (115, 127, 25)]
    for i, (x0, x1, top) in enumerate(ground):
        b.box(x0, top, x1, 27, k, open_left=(x0 == 0), open_right=(x1 == 127))
    # Hoogteverschillen zonder gat: zijwand van het hogere stuk volstaat,
    # maar de lage buren beginnen direct naast de hogere stukken.
    # IJsplatforms
    for x, y, w in ((6, 21, 6), (25, 18, 7), (39, 15, 8), (53, 16, 6), (64, 20, 5),
                    (78, 18, 7), (92, 14, 6), (105, 17, 6), (119, 21, 5)):
        b.obj(T1, ICE, x, y, w, 1)
    # Blokken
    b.block_row(BRICK, 12, 17, 4).obj(T0, QBLOCK_ITEM, 13, 17)
    b.block_row(BRICK, 31, 12, 5).obj(T0, QBLOCK_COIN, 33, 12)
    b.block_row(BRICK, 55, 11, 3).obj(T0, QBLOCK_ITEM, 56, 11)
    b.block_row(BRICK, 70, 15, 4).obj(T0, QBLOCK_COIN, 71, 15)
    b.block_row(BRICK, 84, 12, 5).obj(T0, QBLOCK_ITEM, 86, 12)
    b.block_row(BRICK, 110, 12, 4).obj(T0, QBLOCK_COIN, 111, 12)
    # Munten
    for x, y, w in ((7, 19, 4), (26, 16, 5), (40, 13, 6), (54, 14, 4), (79, 16, 5),
                    (93, 12, 4), (106, 15, 4), (120, 19, 3), (18, 21, 2), (47, 21, 2),
                    (72, 21, 2), (99, 21, 2)):
        b.coins(x, y, w)
    # Vijanden (alleen types uit de originele ijsstage)
    b.sprite(149, 30, 22, bytes([0, 0, 1, 0, 0, 0])).sprite(149, 82, 22, bytes([0, 0, 1, 0, 0, 0]))
    b.sprite(149, 108, 21, bytes([0, 0, 3, 0, 0, 0]))
    # Sterpunten
    for x, y in ((9, 19), (28, 16), (43, 13), (56, 9), (66, 18), (81, 16), (95, 12),
                 (108, 15), (121, 19)):
        b.star(x, y)
    b.spawns((4, 24), (123, 24))
    return b


def buizenstelsel(base):
    """Pijpenstage: plafond en zij-warppijpen van het origineel, nieuw middenveld
    met pijpen van verschillende hoogte, zwevende noppenblokken en twee
    piranhaplanten."""
    keep = lambda o: (o.tileset == T0 and (o.num in (101, 54, 82, 2)
                      or (o.num == 53 and o.x in (0, 62) and o.y == 0)))
    b = StageBuilder(base, keep_objects=keep, keep_sprites=lambda s: s.type == 24)
    # Alleen de spawnpunten (0,1) en de zij-warps (4,5) behouden
    b.lvl.entrances = [e for e in b.lvl.entrances if e.number in (0, 1, 4, 5)]
    GROUND = 53
    # Vloer met twee gaten
    b.obj(T0, GROUND, 2, 25, 14, 2).obj(T0, GROUND, 19, 25, 26, 2).obj(T0, GROUND, 48, 25, 14, 2)
    b.obj(T0, STONE, 4, 24, 6, 1).obj(T0, STONE, 54, 24, 6, 1)
    # Pijpen (breedte 2): (x, bovenkant)
    pipes = [(12, 21), (21, 19), (27, 22), (31, 16), (35, 22), (41, 19), (50, 21)]
    for x, top in pipes:
        b.obj(T0, PIPE, x, top, 2, 25 - top)
    b.sprite(23, 31, 16).sprite(23, 21, 19)
    # Zwevende noppenblokken en vraagtekenblokken
    b.obj(T0, STONE, 6, 18, 4, 1).obj(T0, STONE, 54, 18, 4, 1)
    b.obj(T0, STONE, 14, 14, 3, 1).obj(T0, STONE, 47, 14, 3, 1)
    b.obj(T0, STONE, 24, 12, 4, 1).obj(T0, STONE, 36, 12, 4, 1)
    b.obj(T0, QBLOCK_ITEM, 7, 14).obj(T0, QBLOCK_ITEM, 56, 14).obj(T0, QBLOCK_COIN, 31, 10)
    b.obj(T0, QBLOCK_COIN, 32, 10)
    # Munten
    b.coins(17, 22, 2).coins(45, 22, 2).coins(24, 10, 4).coins(36, 10, 4)
    b.coins(14, 12, 3).coins(47, 12, 3).coins(31, 14, 2).coins(6, 16, 4).coins(54, 16, 4)
    # Sterpunten
    for x, y in ((8, 16), (55, 16), (15, 12), (48, 12), (25, 10), (38, 10), (31, 8),
                 (28, 20), (36, 20)):
        b.star(x, y)
    b.spawns((5, 23), (57, 23))
    return b


def kantelen(base):
    """Kasteel met vier torens van oplopende hoogte en een brug in het midden.
    Plafond en hangende obstakels komen uit de originele kasteelstage."""
    keep_o = lambda o: (o.tileset == T1 and o.num in (94, 96) and o.y < 8) or _is(o, T0, 2)
    keep_s = lambda s: s.type in (195, 196) or (s.type == 298 and s.y == 6)
    b = StageBuilder(base, keep_objects=keep_o, keep_sprites=keep_s)
    FLOOR_Y = 18

    def tower(x0, x1, top):
        b.obj(T1, 26, x0, top).obj(T1, 25, x0 + 1, top, x1 - x0 - 1, 1).obj(T1, 27, x1, top)
        b.obj(T1, 23, x0, top + 1, 1, FLOOR_Y - top - 1).obj(T1, 24, x1, top + 1, 1, FLOOR_Y - top - 1)
        b.obj(T1, 96, x0 + 1, top + 1, x1 - x0 - 1, FLOOR_Y - top)
        b.obj(T1, 89, x0, FLOOR_Y).obj(T1, 90, x1, FLOOR_Y)

    towers = [(6, 9, 15), (17, 21, 12), (42, 46, 12), (54, 57, 15)]
    for t in towers:
        tower(*t)
    # Vloer tussen de torens
    edges = [0] + [v for t in towers for v in (t[0], t[1] + 1)] + [64]
    for a, c in zip(edges[0::2], edges[1::2]):
        b.obj(T1, 25, a, FLOOR_Y, c - a, 1)
    # Middenstuk: lage muur met brug erover
    tower(28, 35, 16)
    b.obj(T0, 92, 22, 12, 20, 1)            # brug tussen de twee hoge torens
    b.obj(T0, BRICK, 30, 9, 4, 1).obj(T0, QBLOCK_ITEM, 31, 9).obj(T0, QBLOCK_ITEM, 32, 9)
    b.obj(T0, BRICK, 1, 12, 3, 1).obj(T0, BRICK, 60, 12, 3, 1)
    b.obj(T0, QBLOCK_COIN, 12, 11).obj(T0, QBLOCK_COIN, 51, 11)
    # Munten
    b.coins(7, 13, 2).coins(55, 13, 2).coins(18, 10, 3).coins(43, 10, 3)
    b.coins(25, 10, 2).coins(37, 10, 2).coins(11, 16, 4).coins(49, 16, 4).coins(30, 14, 4)
    # Vijanden
    b.sprite(28, 13, 17).sprite(28, 50, 17)
    # Sterpunten
    for x, y in ((7, 13), (56, 13), (19, 10), (44, 10), (31, 14), (32, 7), (2, 10),
                 (61, 10), (13, 16)):
        b.star(x, y)
    b.spawns((2, 17), (61, 17))
    return b


# ===========================================================================
# Pagina 3 en 4: experimentelere ontwerpen
# ===========================================================================

def _mirror(x, w, W):
    return W - x - w


def zweefeilanden(base):
    """Geen grond: zwevende graseilanden boven een bodemloze lucht.
    Hogere view (28 tegels) zodat er ruimte is om tussen eilanden te springen."""
    b = StageBuilder(base, keep_objects=lambda o: _is(o, T0, 2))
    b.view_size(64, 28)
    k = STD_KIT
    W = 64
    b.box(0, 22, 7, 24, k, open_left=True, bottom=True)
    b.box(56, 22, 63, 24, k, open_right=True, bottom=True)
    for x0, y0, w, h in ((12, 18, 8, 3), (4, 11, 6, 2), (14, 7, 6, 2), (24, 24, 4, 2)):
        b.box(x0, y0, x0 + w - 1, y0 + h - 1, k, bottom=True)
        m = _mirror(x0, w, W)
        b.box(m, y0, m + w - 1, y0 + h - 1, k, bottom=True)
    b.box(24, 14, 39, 16, k, bottom=True)          # groot middeneiland
    b.box(28, 4, 35, 5, k, bottom=True)            # topeiland
    # Wrap-markeringen ter hoogte van de starteilanden
    b.sprite(195, 0, 22).sprite(196, 63, 22)
    # Blokken
    b.block_row(BRICK, 29, 10, 6).obj(T0, QBLOCK_ITEM, 31, 10).obj(T0, QBLOCK_ITEM, 32, 10)
    b.obj(T0, QBLOCK_COIN, 6, 7).obj(T0, QBLOCK_COIN, 57, 7)
    b.block_row(BRICK, 14, 14, 3).block_row(BRICK, 47, 14, 3)
    # Munten in bogen tussen de eilanden
    for x, y in ((9, 20), (10, 19), (11, 18), (21, 15), (22, 14), (23, 13), (11, 9), (12, 8), (21, 5), (22, 4)):
        b.coins(x, y).coins(_mirror(x, 1, W), y)
    b.coins(30, 2, 4).coins(28, 22, 8)
    # Vijanden op het middeneiland
    b.sprite(148, 27, 13).sprite(148, 36, 13)
    for x, y in ((3, 20), (60, 20), (15, 16), (48, 16), (31, 12), (6, 9), (57, 9), (31, 2), (31, 22)):
        b.star(x, y)
    b.spawns((3, 21), (60, 21))
    return b


def trappenpiramide(base):
    """Een reusachtige trappiramide in het midden met een blokkenkroon."""
    b = StageBuilder(base, keep_objects=lambda o: _is(o, T0, 2),
                     keep_sprites=lambda s: s.type in (195, 196))
    k = STD_KIT
    W = 64
    b.box(0, 15, 9, 17, k, open_left=True)
    b.box(54, 15, 63, 17, k, open_right=True)
    b.box(13, 17, 17, 17, k).box(46, 17, 50, 17, k)
    # Treden van de piramide: (x0, x1, bovenkant)
    for x0, x1, top in ((18, 21, 15), (22, 25, 12), (26, 29, 9), (30, 33, 6),
                        (34, 37, 9), (38, 41, 12), (42, 45, 15)):
        b.box(x0, top, x1, 17, k)
    # Kroon van vraagtekenblokken boven de top
    b.obj(T0, QBLOCK_ITEM, 31, 2).obj(T0, QBLOCK_ITEM, 32, 2)
    b.obj(T0, QBLOCK_COIN, 28, 4).obj(T0, QBLOCK_COIN, 35, 4)
    # Zwevende stenen aan de zijkanten
    b.block_row(BRICK, 3, 11, 4).block_row(BRICK, 57, 11, 4)
    b.block_row(BRICK, 10, 8, 3).block_row(BRICK, 51, 8, 3)
    b.obj(T0, QBLOCK_ITEM, 11, 8).obj(T0, QBLOCK_ITEM, 52, 8)
    # Munten op elke trede
    for x0, top in ((18, 15), (22, 12), (26, 9), (34, 9), (38, 12), (42, 15)):
        b.coins(x0 + 1, top - 2, 2)
    b.coins(4, 9, 2).coins(58, 9, 2).coins(14, 15, 3).coins(47, 15, 3)
    # Een leger Goomba's op de treden
    for x, y in ((20, 14), (24, 11), (39, 11), (43, 14), (15, 16), (48, 16)):
        b.sprite(148, x, y)
    for x, y in ((31, 4), (5, 9), (58, 9), (11, 6), (52, 6), (23, 10), (40, 10), (15, 15), (48, 15)):
        b.star(x, y)
    b.spawns((3, 14), (60, 14))
    return b


def doolhof(base):
    """Doolhof van stenen met gangen op vier verdiepingen en verspringende openingen."""
    b = StageBuilder(base, keep_sprites=lambda s: s.type in (195, 196, 80))
    W = 32
    b.obj(T0, BRICK, 0, 20, W, 4)                 # vloer
    # Horizontale muren met openingen die per verdieping verspringen
    floors = {16: [(0, 6), (10, 12), (26, 6)], 12: [(3, 10), (19, 10)], 8: [(0, 4), (8, 16), (28, 4)],
              4: [(4, 8), (20, 8)]}
    for y, parts in floors.items():
        for x, w in parts:
            b.block_row(BRICK, x, y, w)
    # Verticale tussenmuren
    for x, y, h in ((7, 13, 3), (24, 13, 3), (15, 9, 3), (16, 9, 3), (2, 5, 3), (29, 5, 3)):
        b.obj(T0, BRICK, x, y, 1, h)
    b.obj(T0, QBLOCK_ITEM, 15, 16).obj(T0, QBLOCK_ITEM, 16, 16)
    b.obj(T0, BRICK_ITEM, 6, 8).obj(T0, BRICK_ITEM, 25, 8)
    b.obj(T0, QBLOCK_COIN, 11, 4).obj(T0, QBLOCK_COIN, 20, 4)
    # Munten in de gangen
    b.coins(1, 18, 4).coins(27, 18, 4).coins(9, 14, 5).coins(18, 14, 5)
    b.coins(4, 10, 3).coins(25, 10, 3).coins(12, 6, 3).coins(17, 6, 3).coins(14, 2, 4)
    b.sprite(148, 12, 19).sprite(148, 19, 19).sprite(148, 5, 11).sprite(148, 26, 11)
    for x, y in ((3, 18), (28, 18), (15, 14), (11, 10), (20, 10), (1, 6), (30, 6), (15, 2), (15, 18)):
        b.star(x, y)
    b.spawns((2, 19), (29, 19))
    return b


def muntenkluis(base):
    """Een kluis vol muntblokken in het midden; ingang alleen via het dak."""
    b = StageBuilder(base, keep_sprites=lambda s: s.type in (195, 196, 80))
    W = 32
    COINBRICK = 45
    b.obj(T0, BRICK, 0, 20, 12, 4).obj(T0, BRICK, 20, 20, 12, 4)
    b.obj(T0, BRICK, 12, 22, 8, 2)                # verlaagde vloer in de kluis
    # Kluismuren
    b.obj(T0, BRICK, 11, 9, 1, 11).obj(T0, BRICK, 20, 9, 1, 11)
    b.block_row(BRICK, 11, 9, 3).block_row(BRICK, 18, 9, 3)   # dak met opening x14..17
    # Inhoud van de kluis
    b.obj(T0, COINBRICK, 13, 18, 6, 1).obj(T0, QBLOCK_ITEM, 15, 14).obj(T0, QBLOCK_ITEM, 16, 14)
    b.coins(13, 20, 6).coins(13, 12, 6)
    # Trappen naar het dak aan beide kanten
    for i in range(4):
        b.block_row(BRICK, 6 - i, 17 - 2 * i, 3).block_row(BRICK, _mirror(6 - i, 3, W), 17 - 2 * i, 3)
    b.block_row(BRICK, 0, 6, 4).block_row(BRICK, 28, 6, 4)
    b.obj(T0, QBLOCK_COIN, 1, 6).obj(T0, QBLOCK_COIN, 30, 6)
    b.coins(0, 4, 3).coins(29, 4, 3).coins(14, 6, 4)
    b.sprite(148, 4, 19).sprite(148, 27, 19).sprite(149, 15, 21, bytes([0, 0, 1, 0, 0, 0]))
    for x, y in ((15, 20), (15, 11), (7, 15), (24, 15), (4, 11), (27, 11), (1, 4), (30, 4), (15, 6)):
        b.star(x, y)
    b.spawns((2, 19), (29, 19))
    return b


def glijbaan(base):
    """Twee enorme trappen die naar een ijsvallei afdalen. Wie te hard glijdt,
    belandt in het gat onder de smalle ijsbrug."""
    b = StageBuilder(base, keep_objects=lambda o: _is(o, T0, 2),
                     keep_sprites=lambda s: s.type in (195, 196))
    k = STD_KIT
    ICE = 32
    W = 128
    steps = [(0, 7, 13), (8, 15, 15), (16, 23, 17), (24, 31, 19), (32, 39, 21), (40, 47, 23)]
    for x0, x1, top in steps:
        b.box(x0, top, x1, 27, k, open_left=(x0 == 0))
        m0 = _mirror(x0, x1 - x0 + 1, W)
        b.box(m0, top, m0 + x1 - x0, 27, k, open_right=(x1 == 7))
    b.box(48, 25, 59, 27, k).box(68, 25, 79, 27, k)
    b.obj(T1, ICE, 61, 25, 6, 1)                 # smalle ijsbrug, met een gat aan elke kant
    # IJs op elke trede zodat je doorglijdt
    for x0, x1, top in steps[1:]:
        b.obj(T1, ICE, x0, top, x1 - x0 + 1, 1)
        m0 = _mirror(x0, x1 - x0 + 1, W)
        b.obj(T1, ICE, m0, top, x1 - x0 + 1, 1)
    # Zwevende platforms boven de vallei
    for x, y, w in ((52, 19, 5), (71, 19, 5), (60, 14, 8), (56, 9, 4), (68, 9, 4)):
        b.obj(T1, ICE, x, y, w, 1)
    b.block_row(BRICK, 61, 4, 6).obj(T0, QBLOCK_ITEM, 63, 4).obj(T0, QBLOCK_ITEM, 64, 4)
    for x0, x1, top in steps:
        b.coins(x0 + 3, top - 2, 2).coins(_mirror(x0 + 3, 2, W), top - 2, 2)
    b.coins(61, 23, 6).coins(61, 12, 6)
    b.sprite(149, 54, 24, bytes([0, 0, 1, 0, 0, 0])).sprite(149, 73, 24, bytes([0, 0, 1, 0, 0, 0]))
    for x, y in ((4, 11), (123, 11), (27, 17), (100, 17), (54, 17), (73, 17), (63, 12), (63, 2), (63, 23)):
        b.star(x, y)
    b.spawns((3, 12), (124, 12))
    return b


def bevrorenmeer(base):
    """Een volledig bevroren meer: alles is glad ijs, met sneeuwrotsen als obstakels."""
    b = StageBuilder(base, keep_objects=lambda o: _is(o, T0, 2),
                     keep_sprites=lambda s: s.type in (195, 196))
    k = STD_KIT
    ICE = 32
    W = 128
    b.obj(T1, ICE, 0, 24, W, 1)
    b.obj(T1, k['fill'], 0, 25, W, 3)
    for x0, x1, top in ((18, 23, 20), (40, 43, 22), (58, 69, 18), (84, 87, 22), (104, 109, 20)):
        b.box(x0, top, x1, 23, k)
    for x, y, w in ((8, 19, 5), (28, 16, 6), (46, 13, 6), (61, 11, 6), (76, 13, 6), (92, 16, 6), (115, 19, 5)):
        b.obj(T1, ICE, x, y, w, 1)
    b.block_row(BRICK, 62, 6, 4).obj(T0, QBLOCK_ITEM, 63, 6).obj(T0, QBLOCK_ITEM, 64, 6)
    b.block_row(BRICK, 30, 11, 3).obj(T0, QBLOCK_COIN, 31, 11)
    b.block_row(BRICK, 94, 11, 3).obj(T0, QBLOCK_COIN, 95, 11)
    for x, y, w in ((9, 17, 3), (29, 14, 4), (47, 11, 4), (62, 9, 4), (77, 11, 4), (93, 14, 4), (116, 17, 3),
                    (2, 22, 6), (120, 22, 6), (50, 22, 6), (72, 22, 6)):
        b.coins(x, y, w)
    for x in (12, 36, 52, 75, 98, 120):
        b.sprite(149, x, 23, bytes([0, 0, 1, 0, 0, 0]))
    for x, y in ((10, 17), (30, 14), (48, 11), (63, 9), (78, 11), (94, 14), (117, 17), (63, 16), (2, 22)):
        b.star(x, y)
    b.spawns((4, 23), (123, 23))
    return b


def pijpenorgel(base):
    """Rijen pijpen waarvan de hoogtes een golf vormen, als de pijpen van een orgel."""
    import math
    keep = lambda o: (o.tileset == T0 and (o.num in (101, 54, 82, 2)
                      or (o.num == 53 and o.x in (0, 62) and o.y == 0)))
    b = StageBuilder(base, keep_objects=keep, keep_sprites=lambda s: s.type == 24)
    b.lvl.entrances = [e for e in b.lvl.entrances if e.number in (0, 1, 4, 5)]
    b.obj(T0, 53, 2, 25, 60, 2)
    tops = []
    for i, x in enumerate(range(8, 56, 3)):
        top = int(round(19 - 4 * math.sin(i * math.pi / 5)))
        tops.append((x, top))
        b.obj(T0, PIPE, x, top, 2, 25 - top)
        if i % 2 == 0:
            b.coins(x, top - 2, 2)
    # Piranhaplanten in de twee laagste pijpen
    lows = sorted(tops, key=lambda t: -t[1])[:2]
    for x, top in lows:
        b.sprite(23, x, top)
    b.obj(T0, STONE, 4, 18, 3, 1).obj(T0, STONE, 57, 18, 3, 1)
    b.obj(T0, STONE, 18, 10, 4, 1).obj(T0, STONE, 42, 10, 4, 1).obj(T0, STONE, 29, 7, 6, 1)
    b.obj(T0, QBLOCK_ITEM, 31, 7).obj(T0, QBLOCK_ITEM, 32, 7)
    b.coins(18, 8, 4).coins(42, 8, 4).coins(4, 16, 3).coins(57, 16, 3)
    for i, (x, top) in enumerate(tops[::2]):
        b.star(x, top - 3)
        if i >= 6:
            break
    b.star(31, 5).star(5, 16)
    b.spawns((4, 24), (58, 24))
    return b


def riool(base):
    """Twee verdiepingen: een lage rioolbuis onderin en een stenen loopbrug erboven,
    verbonden door gaten in de brug."""
    keep = lambda o: (o.tileset == T0 and (o.num in (101, 54, 82, 2)
                      or (o.num == 53 and o.x in (0, 62) and o.y == 0)))
    b = StageBuilder(base, keep_objects=keep, keep_sprites=lambda s: s.type == 24)
    b.lvl.entrances = [e for e in b.lvl.entrances if e.number in (0, 1, 4, 5)]
    b.obj(T0, 53, 2, 25, 60, 2)
    # Loopbrug van noppenblokken met drie gaten
    for x, w in ((4, 12), (19, 10), (33, 12), (48, 12)):
        b.obj(T0, STONE, x, 17, w, 1)
    # Korte pijpen in de buis onderin
    for x, top in ((10, 22), (24, 23), (38, 23), (52, 22)):
        b.obj(T0, PIPE, x, top, 2, 25 - top)
    b.sprite(23, 24, 23).sprite(23, 38, 23)
    # Bovenverdieping
    b.obj(T0, PIPE, 30, 13, 2, 4)
    b.obj(T0, STONE, 8, 12, 4, 1).obj(T0, STONE, 50, 12, 4, 1).obj(T0, STONE, 26, 9, 10, 1)
    b.obj(T0, QBLOCK_ITEM, 30, 9).obj(T0, QBLOCK_ITEM, 31, 9)
    b.obj(T0, QBLOCK_COIN, 17, 13).obj(T0, QBLOCK_COIN, 46, 13)
    b.coins(5, 23, 4).coins(44, 23, 4).coins(17, 20, 2).coins(31, 20, 2)
    b.coins(8, 10, 4).coins(50, 10, 4).coins(27, 7, 8)
    for x, y in ((6, 15), (56, 15), (22, 15), (40, 15), (9, 10), (51, 10), (30, 7), (18, 23), (32, 23)):
        b.star(x, y)
    b.spawns((5, 24), (57, 24))
    return b


def kerker(base):
    """Lage kerker vol korte pilaren en oranje loopbruggen op twee hoogtes."""
    keep_o = lambda o: (o.tileset == T1 and o.num in (94, 96) and o.y < 8) or _is(o, T0, 2)
    keep_s = lambda s: s.type in (195, 196) or (s.type == 298 and s.y == 6)
    b = StageBuilder(base, keep_objects=keep_o, keep_sprites=keep_s)
    FLOOR_Y = 18

    def pillar(x0, x1, top):
        b.obj(T1, 26, x0, top).obj(T1, 25, x0 + 1, top, x1 - x0 - 1, 1).obj(T1, 27, x1, top)
        if FLOOR_Y - top - 1 > 0:
            b.obj(T1, 23, x0, top + 1, 1, FLOOR_Y - top - 1).obj(T1, 24, x1, top + 1, 1, FLOOR_Y - top - 1)
        b.obj(T1, 96, x0 + 1, top + 1, x1 - x0 - 1, FLOOR_Y - top)
        b.obj(T1, 89, x0, FLOOR_Y).obj(T1, 90, x1, FLOOR_Y)

    pillars = [(5, 7, 16), (13, 15, 15), (21, 23, 16), (29, 34, 14), (40, 42, 16), (48, 50, 15), (56, 58, 16)]
    for p in pillars:
        pillar(*p)
    edges = [0] + [v for p in pillars for v in (p[0], p[1] + 1)] + [64]
    for a, c in zip(edges[0::2], edges[1::2]):
        if c > a:
            b.obj(T1, 25, a, FLOOR_Y, c - a, 1)
    # Bruggen op twee hoogtes
    for x, w in ((8, 5), (24, 5), (35, 5), (51, 5)):
        b.obj(T0, 92, x, 13, w, 1)
    for x, w in ((14, 15), (35, 15)):
        b.obj(T0, 92, x, 10, w, 1)
    b.obj(T0, QBLOCK_ITEM, 31, 9).obj(T0, QBLOCK_ITEM, 32, 9)
    b.obj(T0, BRICK, 1, 14, 3, 1).obj(T0, BRICK, 60, 14, 3, 1)
    b.coins(9, 11, 3).coins(25, 11, 3).coins(36, 11, 3).coins(52, 11, 3)
    b.coins(16, 8, 5).coins(43, 8, 5).coins(9, 16, 3).coins(52, 16, 3)
    b.sprite(28, 18, 17).sprite(28, 45, 17).sprite(28, 31, 13)
    for x, y in ((10, 11), (53, 11), (18, 8), (45, 8), (31, 12), (2, 12), (61, 12), (26, 11), (37, 11)):
        b.star(x, y)
    b.spawns((2, 17), (61, 17))
    return b


def torenspits(base):
    """Kasteel zonder plafond: een hoge middentoren met zijtorens en bruggen.
    Experimentele, hogere view van 28 tegels."""
    keep_o = lambda o: _is(o, T0, 2) and o.y > 30
    b = StageBuilder(base, keep_objects=keep_o, keep_sprites=lambda s: s.type in (195, 196))
    b.view_size(64, 28)
    FLOOR_Y = 27
    for s in b.lvl.sprites:
        s.y = FLOOR_Y

    def tower(x0, x1, top):
        b.obj(T1, 26, x0, top).obj(T1, 25, x0 + 1, top, x1 - x0 - 1, 1).obj(T1, 27, x1, top)
        b.obj(T1, 23, x0, top + 1, 1, FLOOR_Y - top - 1).obj(T1, 24, x1, top + 1, 1, FLOOR_Y - top - 1)
        b.obj(T1, 96, x0 + 1, top + 1, x1 - x0 - 1, FLOOR_Y - top)
        b.obj(T1, 89, x0, FLOOR_Y).obj(T1, 90, x1, FLOOR_Y)

    towers = [(4, 7, 22), (13, 17, 17), (28, 35, 8), (46, 50, 17), (56, 59, 22)]
    for t in towers:
        tower(*t)
    edges = [0] + [v for t in towers for v in (t[0], t[1] + 1)] + [64]
    for a, c in zip(edges[0::2], edges[1::2]):
        if c > a:
            b.obj(T1, 25, a, FLOOR_Y, c - a, 1)
    for x, y, w in ((8, 20, 5), (51, 20, 5), (18, 13, 10), (36, 13, 10), (20, 22, 8), (36, 22, 8)):
        b.obj(T0, 92, x, y, w, 1)
    b.obj(T0, QBLOCK_ITEM, 31, 4).obj(T0, QBLOCK_ITEM, 32, 4)
    b.obj(T0, BRICK, 22, 8, 3, 1).obj(T0, BRICK, 39, 8, 3, 1)
    b.coins(5, 20, 2).coins(57, 20, 2).coins(14, 15, 4).coins(46, 15, 4).coins(29, 6, 6)
    b.coins(19, 11, 8).coins(37, 11, 8).coins(21, 20, 6).coins(37, 20, 6)
    b.sprite(28, 10, 26).sprite(28, 53, 26).sprite(28, 24, 21)
    for x, y in ((5, 20), (58, 20), (15, 15), (48, 15), (31, 6), (23, 11), (40, 11), (23, 6), (40, 6)):
        b.star(x, y)
    b.spawns((2, 26), (61, 26))
    return b
