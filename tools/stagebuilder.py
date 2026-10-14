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

    def view_size(self, w, h, y=None):
        """Change the camera view (in tiles)."""
        v = self.lvl.views[0]
        v.w, v.h = w * 16, h * 16
        if y is not None:
            v.y = y * 16
        return self

    def build(self):
        return self.lvl.save()
