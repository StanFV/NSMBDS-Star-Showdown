"""Helpers for building new Mario vs Luigi stages.

A new stage starts as a copy of the original VS stage from the same archive
(same tileset, background and sprite sets). The objects, sprites and start
positions are then replaced with a new design.
"""
import copy
from nsmblevel import Level, Obj, Sprite, Entrance

T0, T1 = 0, 1  # tileset numbers used in objects

# Shared blocks from tileset 0 (jyotyu)
BRICK = 44
QBLOCK_COIN = 30
QBLOCK_ITEM = 37
BRICK_ITEM = 48
COIN = 20
USED_BLOCK = 13
STONE = 93
PIPE = 102


class StageBuilder:
    def __init__(self, base: Level, keep_objects=lambda o: False, keep_sprites=lambda s: False):
        self.lvl = copy.deepcopy(base)
        self.lvl.objects = [o for o in base.objects if keep_objects(o)]
        self.lvl.sprites = [copy.deepcopy(s) for s in base.sprites if keep_sprites(s)]
        self.star_id = 1

    # ---- objects ------------------------------------------------------
    def obj(self, ts, num, x, y, w=1, h=1):
        if w > 0 and h > 0:
            self.lvl.objects.append(Obj(ts, num, x, y, w, h))
        return self

    def block_row(self, num, x, y, w):
        return self.obj(T0, num, x, y, w, 1)

    def coins(self, x, y, w=1, h=1):
        return self.obj(T0, COIN, x, y, w, h)

    def box(self, x0, y0, x1, y1, kit, open_left=False, open_right=False, bottom=False):
        """Rectangular block of terrain with edges.

        kit: dict of object numbers (tileset 1) for tl, top, tr, left,
        right, fill and optionally bl, bottom, br.
        open_left/open_right leave out the side edge (for the wrap edge)."""
        w = x1 - x0 + 1
        lx = x0 if open_left else x0 + 1
        rx = x1 if open_right else x1 - 1
        if not open_left:
            self.obj(T1, kit['tl'], x0, y0)
        if not open_right:
            self.obj(T1, kit['tr'], x1, y0)
        self.obj(T1, kit['top'], lx, y0, rx - lx + 1, 1)
        body_bottom = y1 - 1 if bottom else y1
        if y1 > y0:
            if not open_left:
                self.obj(T1, kit['left'], x0, y0 + 1, 1, body_bottom - y0)
            if not open_right:
                self.obj(T1, kit['right'], x1, y0 + 1, 1, body_bottom - y0)
            self.obj(T1, kit['fill'], lx, y0 + 1, rx - lx + 1, body_bottom - y0)
            if bottom:
                if not open_left:
                    self.obj(T1, kit['bl'], x0, y1)
                if not open_right:
                    self.obj(T1, kit['br'], x1, y1)
                self.obj(T1, kit['bottom'], lx, y1, rx - lx + 1, 1)
        return self

    # ---- sprites -------------------------------------------------------
    def sprite(self, typ, x, y, data=b'\0' * 6):
        self.lvl.sprites.append(Sprite(typ, x, y, bytes(data)))
        return self

    # ---- hazards and moving objects that Mario vs Luigi can load ---------
    # VS mode only has the enemy models of ARCHIVE/Dat_enemy.narc, so only
    # these work in every theme.
    def lift(self, x, y):
        """Lift spawner (sprite 80): wooden platforms that keep rising from
        (x, y) to the top of the stage. Platform is about 4 tiles wide."""
        return self.sprite(80, x, y, bytes([0, 0, 0, 0, 0, 0x10]))

    def cannon(self, x, ground):
        """Bullet Bill blaster (sprite 27), 3 tiles tall, standing on row `ground`."""
        self.sprite_set(5, 1)
        return self.sprite(27, x, ground - 1, bytes([0, 0, 0x10, 0, 0, 0]))

    def bobomb(self, x, y):
        self.sprite_set(5, 1)
        return self.sprite(28, x, y)

    def flying_block(self, x, y):
        """Flying question block (sprite 45) that drops an item when hit."""
        return self.sprite(45, x, y, bytes([0, 0, 0x20, 0x11, 0, 0]))

    def goomba(self, x, y):
        return self.sprite(148, x, y)

    def koopa(self, x, y, red=False):
        return self.sprite(149, x, y, bytes([0, 0, 1 if red else 0, 0, 0, 0]))

    def star(self, x, y):
        """Spawn point for the Big Star (sprite 210), numbered automatically."""
        self.sprite(210, x, y, bytes([0, 0, self.star_id, 0, 0, 0]))
        self.star_id += 1
        return self

    def spawns(self, p1, p2):
        """Start positions (in tiles) for player 1 and 2. y = the row above the ground."""
        for e, (x, y) in zip(self.lvl.entrances[:2], (p1, p2)):
            e.set(x=x * 16, y=y * 16)
        return self

    def sprite_set(self, n, value):
        """Choose value for sprite set n (1..16); this decides which enemy
        and platform graphics the stage loads (e.g. set 1 = 3 for castle enemies)."""
        self.lvl.blocks[13][n - 1] = value
        return self

    def view_size(self, w, h, y=None):
        """Change the camera view (in tiles)."""
        v = self.lvl.views[0]
        v.w, v.h = w * 16, h * 16
        if y is not None:
            v.y = y * 16
        return self

    def build(self):
        return self.lvl.save()
