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
