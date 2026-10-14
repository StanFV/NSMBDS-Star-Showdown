"""Renderer voor NSMB DS levels (alleen voor previews tijdens het ontwerpen).

Gebaseerd op de tileset- en objectlogica van NSMB Editor (GPLv3).
Rendert de objectlagen (tileset 0, 1 en 2) naar een PIL-afbeelding.
Sprites worden als gekleurde markeringen getekend.
"""
import struct
import ndspy.lz10
from PIL import Image, ImageDraw

FILE_OFFSET_EU = 135
# Objecten uit tileset 0 waarvan de graphics niet in de basistileset zitten
# (pijpen); die worden in previews benaderd.
PIPE_OBJECTS = {53, 54, 78, 79, 82, 101, 102}
# Offsets van de tilesettabellen in overlay 0 (EU)
TABLES_EU = {
    'UNT_HD': 0x2F0F8, 'UNT': 0x2F228, 'CHK': 0x2F358, 'NCG': 0x306B8,
    'NCL': 0x30CA8, 'PNL': 0x30F08,
}


def _lz(data):
    try:
        return ndspy.lz10.decompress(data)
    except Exception:
        return data


def _palettes(raw):
    raw = _lz(raw)
    pals = []
    for p in range(len(raw) // 512):
        pal = []
        for i in range(256):
            c = struct.unpack_from('<H', raw, p * 512 + i * 2)[0]
            r, g, b = (c & 31) << 3, ((c >> 5) & 31) << 3, ((c >> 10) & 31) << 3
            pal.append((r | r >> 5, g | g >> 5, b | b >> 5, 0 if i == 0 else 255))
        pals.append(pal)
    return pals


class Tileset:
    def __init__(self, ncg, ncl, pnl, unt, unt_hd, number):
        self.number = number
        self.gfx = _lz(ncg)
        self.pals = _palettes(ncl)
        self.map16 = pnl
        self.tile_off = {0: 0, 1: 192, 2: 640}[number]
        self.pal_off = {0: 0, 1: 2, 2: 6}[number]
        self.objdef_off = {0: 0, 1: 1, 2: 4}[number]
        self._cache = {}
        self.objects = self._load_objects(unt, unt_hd)

    def _load_objects(self, unt, hd):
        objs = []
        for i in range(0, len(hd) - 3, 4):
            off = struct.unpack_from('<H', hd, i)[0]
            rows, row = [], []
            p = off
            while p < len(unt):
                c = unt[p]
                if c == 0xFF:
                    break
                if c == 0xFE:
                    rows.append(row); row = []; p += 1; continue
                if c & 0x80:
                    row.append((c, None)); p += 1; continue
                a, b = unt[p + 1], unt[p + 2]
                tid = a + ((b - self.objdef_off) << 8)
                if c & 0x40:
                    tid += 768
                if a == 0 and b == 0:
                    tid = -1
                row.append((c, tid)); p += 3
            if row:
                rows.append(row)
            objs.append(rows)
        return objs

    def tile16(self, t):
        """Render map16 tegel t (16x16) als RGBA."""
        if t in self._cache:
            return self._cache[t]
        img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
        if 0 <= t and t * 8 + 8 <= len(self.map16):
            px = img.load()
            for q in range(4):
                u = struct.unpack_from('<H', self.map16, t * 8 + q * 2)[0]
                num = (u & 0x3FF) - self.tile_off
                if num < 0 or (num + 1) * 64 > len(self.gfx):
                    continue
                hf, vf = (u >> 10) & 1, (u >> 11) & 1
                pal = (u >> 12) - self.pal_off
                if not 0 <= pal < len(self.pals):
                    continue
                P = self.pals[pal]
                ox, oy = (q & 1) * 8, (q >> 1) * 8
                for y in range(8):
                    for x in range(8):
                        ci = self.gfx[num * 64 + y * 8 + x]
                        if ci == 0:
                            continue
                        dx = 7 - x if hf else x
                        dy = 7 - y if vf else y
                        px[ox + dx, oy + dy] = P[ci]
        self._cache[t] = img
        return img

    # ---- objecten -----------------------------------------------------
    def render_object(self, num, w, h):
        dest = [[-2] * w for _ in range(h)]
        if num >= len(self.objects) or not self.objects[num]:
            return dest
        rows = [r for r in self.objects[num] if r]
        if not rows:
            return dest
        if rows[0][0][0] & 0x80:
            return self._render_slope(rows, w, h)
        before, inr, after = [], [], []
        found = False
        for r in rows:
            if r[0][0] & 2:
                found = True; inr.append(r)
            elif found:
                after.append(r)
            else:
                before.append(r)
        for y in range(h):
            if not inr:
                row = before[y % len(before)]
            elif y < len(before):
                row = before[y]
            elif y > h - len(after) - 1:
                row = after[y - h + len(after)]
            else:
                row = inr[(y - len(before)) % len(inr)]
            self._render_row(dest, row, y, w)
        return dest

    @staticmethod
    def _render_row(dest, row, y, w):
        before, inr, after = [], [], []
        found = False
        for c, t in row:
            if c & 1:
                found = True; inr.append(t)
            elif found:
                after.append(t)
            else:
                before.append(t)
        for x in range(w):
            if not inr:
                dest[y][x] = before[x % len(before)]
            elif x < len(before):
                dest[y][x] = before[x]
            elif x > w - len(after) - 1:
                dest[y][x] = after[x - w + len(after)]
            else:
                dest[y][x] = inr[(x - len(before)) % len(inr)]

    def _render_slope(self, rows, w, h):
        dest = [[-2] * w for _ in range(h)]
        sections, cur = [], None
        for r in rows:
            if r[0][0] & 0x80:
                if cur is not None:
                    sections.append(cur)
                cur = []
            cur.append([t for c, t in r if not (c & 0x80)])
        if cur is not None:
            sections.append(cur)
        sections = [[r for r in s] for s in sections]
        main = sections[0]
        sub = sections[1] if len(sections) > 1 else None
        ctrl = rows[0][0][0]
        go_left, go_down = bool(ctrl & 1), bool(ctrl & 2)
        mw = max(len(r) for r in main) or 1
        mh = len(main)
        x = w - mw if go_left else 0
        y = 0 if go_down else h - mh
        xi = -mw if go_left else mw
        yi = mh if go_down else -mh

        def put(xo, yo, block):
            put_any = False
            for yy, r in enumerate(block):
                for xx, t in enumerate(r):
                    X, Y = xo + xx, yo + yy
                    if 0 <= X < w and 0 <= Y < h:
                        put_any = True
                        dest[Y][X] = t
            return put_any

        for _ in range(512):
            p = put(x, y, main)
            if sub:
                sw = max(len(r) for r in sub) or 1
                xb = x + mw - sw if go_left else x
                p |= put(xb, y - len(sub) if go_down else y + mh, sub)
            if not p:
                break
            x += xi; y += yi
        return dest


def _pipe_tile(col, width):
    """Benadering van een groene pijptegel voor previews."""
    img = Image.new('RGBA', (16, 16), (40, 152, 40, 255))
    d = ImageDraw.Draw(img)
    if col == 0:
        d.rectangle([0, 0, 1, 15], fill=(16, 64, 16, 255))
        d.rectangle([3, 0, 6, 15], fill=(136, 224, 104, 255))
    if col == width - 1:
        d.rectangle([14, 0, 15, 15], fill=(16, 64, 16, 255))
        d.rectangle([10, 0, 12, 15], fill=(24, 104, 24, 255))
    return img


class LevelRenderer:
    def __init__(self, rom):
        self.rom = rom
        self.ov0 = rom.loadArm9Overlays([0])[0].data
        self._ts1 = {}
        f = rom.getFileByName
        self.ts0 = Tileset(f('BG_ncg/d_2d_A_J_jyotyu_ncg.bin'), f('BG_ncl/d_2d_A_J_jyotyu_ncl.bin'),
                           f('BG_pnl/d_2d_PA_A_J_jyotyu.bin'), f('BG_unt/A_J_jyotyu.bin'),
                           f('BG_unt/A_J_jyotyu_hd.bin'), 0)
        self.ts2 = Tileset(f('BG_ncg/d_2d_I_S_tikei_nohara_ncg.bin'), f('BG_ncl/d_2d_I_S_tikei_nohara_ncl.bin'),
                           f('BG_pnl/d_2d_PA_I_S_nohara.bin'), f('BG_unt/I_S_nohara.bin'),
                           f('BG_unt/I_S_nohara_hd.bin'), 2)

    def table_file(self, table, idx):
        fid = struct.unpack_from('<H', self.ov0, TABLES_EU[table] + idx * 4)[0] + FILE_OFFSET_EU
        return self.rom.files[fid]

    def ts1(self, tid):
        if tid not in self._ts1:
            t = lambda k: self.table_file(k, tid)
            self._ts1[tid] = Tileset(t('NCG'), t('NCL'), t('PNL'), t('UNT'), t('UNT_HD'), 1)
        return self._ts1[tid]

    def render(self, level, sprites=True, bg=(92, 148, 252), crop=None):
        ts = [self.ts0, self.ts1(level.tileset_id), self.ts2]
        maxx = max([o.x + o.w for o in level.objects] + [v.x // 16 + v.w // 16 for v in level.views] + [16])
        maxy = max([o.y + o.h for o in level.objects] + [v.y // 16 + v.h // 16 for v in level.views] + [12])
        maxx, maxy = min(maxx, 512), min(maxy, 256)
        grid = {}
        for o in level.objects:
            if o.tileset == 0 and o.num == 0:
                for yy in range(o.h):
                    for xx in range(o.w):
                        grid[(o.x + xx, o.y + yy)] = None
                continue
            tiles = ts[o.tileset].render_object(o.num, o.w, o.h)
            for yy in range(o.h):
                for xx in range(o.w):
                    t = tiles[yy][xx]
                    if t == -2:
                        continue
                    if o.tileset == 0 and (t >= 768 or o.num in PIPE_OBJECTS):
                        # speciale (geanimeerde) tegels zoals pijpen: benaderen
                        grid[(o.x + xx, o.y + yy)] = ('pipe', xx, o.w)
                        continue
                    grid[(o.x + xx, o.y + yy)] = (o.tileset, max(t, 0))
        img = Image.new('RGBA', (maxx * 16, maxy * 16), bg + (255,))
        for (x, y), v in grid.items():
            if v is None or not (0 <= x < maxx and 0 <= y < maxy):
                continue
            if v[0] == 'pipe':
                img.alpha_composite(_pipe_tile(v[1], v[2]), (x * 16, y * 16))
                continue
            tsi, t = v
            img.alpha_composite(ts[tsi].tile16(t), (x * 16, y * 16))
        d = ImageDraw.Draw(img)
        for v in level.views:
            d.rectangle([v.x, v.y, v.x + v.w - 1, v.y + v.h - 1], outline=(255, 255, 0, 255))
        if sprites:
            for s in level.sprites:
                X, Y = s.x * 16, s.y * 16
                col = (255, 215, 0, 255) if s.type == 210 else (255, 0, 255, 255)
                d.rectangle([X + 2, Y + 2, X + 13, Y + 13], outline=col, width=2)
                d.text((X + 1, Y - 9), str(s.type), fill=col)
            for e in level.entrances:
                d.rectangle([e.x, e.y, e.x + 15, e.y + 15], outline=(0, 255, 0, 255), width=2)
                d.text((e.x + 2, e.y + 2), str(e.number), fill=(0, 255, 0, 255))
        if crop:
            img = img.crop(crop)
        return img.convert('RGB')
