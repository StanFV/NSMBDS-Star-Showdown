"""Lezen en schrijven van NSMB DS levelbestanden (course/*.bin + *_bgdat.bin).

Formaat gebaseerd op NSMB Editor (Dirbaio e.a., GPLv3) en eigen analyse.
Een .bin bestaat uit 14 blokken met een header van 14 x (offset, grootte).
"""
import struct
from dataclasses import dataclass, field

BLOCK_COUNT = 14
# Blokindeling
B_SETTINGS, B_CAMERA, B_BG_BOTTOM, B_BG_TOP, B_BG_EXTRA, B_ENTRANCES, B_SPRITES, \
    B_VIEWS, B_ZONES, B_PROGPATHS, B_PATHS, B_PROGNODES, B_PATHNODES, B_SPRITESETS = range(14)


@dataclass
class Obj:
    tileset: int
    num: int
    x: int
    y: int
    w: int
    h: int

    def pack(self):
        return struct.pack('<HhhHH', self.num | (self.tileset << 12), self.x, self.y, self.w, self.h)


@dataclass
class Sprite:
    type: int
    x: int
    y: int
    data: bytes  # 6 bytes zoals in het bestand (ruwe volgorde)

    def pack(self):
        return struct.pack('<HHH', self.type, self.x, self.y) + bytes(self.data)


@dataclass
class Entrance:
    raw: bytearray  # 20 bytes

    @property
    def x(self): return struct.unpack_from('<H', self.raw, 0)[0]
    @property
    def y(self): return struct.unpack_from('<H', self.raw, 2)[0]
    @property
    def number(self): return self.raw[8]
    @property
    def type(self): return self.raw[14]

    def set(self, **kw):
        for k, v in kw.items():
            off, fmt = ENTRANCE_FIELDS[k]
            struct.pack_into(fmt, self.raw, off, v)
        return self


ENTRANCE_FIELDS = {
    'x': (0, '<H'), 'y': (2, '<H'), 'cam_x': (4, '<H'), 'cam_y': (6, '<H'),
    'number': (8, 'B'), 'dest_area': (9, 'B'), 'pipe_id': (10, 'B'),
    'dest_entrance': (12, 'B'), 'type': (14, 'B'), 'settings': (15, 'B'),
    'unk1': (16, 'B'), 'view': (18, 'B'), 'unk2': (19, 'B'),
}


@dataclass
class View:
    x: int
    y: int
    w: int
    h: int
    number: int
    cam: int
    music: int
    unk1: int
    unk2: int
    unk3: int
    lighting: int
    flagpole: int

    def pack(self):
        return struct.pack('<HHHHBBBBBBBB', self.x, self.y, self.w, self.h, self.number, self.cam,
                           self.music, self.unk1, self.unk2, self.unk3, self.lighting, self.flagpole)


@dataclass
class Zone:
    x: int
    y: int
    w: int
    h: int
    number: int
    rest: bytes  # 3 bytes

    def pack(self):
        return struct.pack('<HHHHB', self.x, self.y, self.w, self.h, self.number) + bytes(self.rest)


@dataclass
class Level:
    blocks: list
    objects: list = field(default_factory=list)
    sprites: list = field(default_factory=list)
    entrances: list = field(default_factory=list)
    views: list = field(default_factory=list)
    zones: list = field(default_factory=list)

    @classmethod
    def load(cls, bin_data: bytes, bgdat: bytes):
        blocks = []
        for i in range(BLOCK_COUNT):
            off, size = struct.unpack_from('<II', bin_data, i * 8)
            blocks.append(bytearray(bin_data[off:off + size]))
        lvl = cls(blocks)
        for i in range(0, len(bgdat) - 9, 10):
            t, x, y, w, h = struct.unpack_from('<HhhHH', bgdat, i)
            if t == 0xFFFF:
                break
            lvl.objects.append(Obj(t >> 12, t & 0xFFF, x, y, w, h))
        sb = blocks[B_SPRITES]
        for i in range(0, len(sb) - 11, 12):
            t, x, y = struct.unpack_from('<HHH', sb, i)
            if t == 0xFFFF:
                break
            lvl.sprites.append(Sprite(t, x, y, bytes(sb[i + 6:i + 12])))
        eb = blocks[B_ENTRANCES]
        lvl.entrances = [Entrance(bytearray(eb[i:i + 20])) for i in range(0, len(eb) - 19, 20)]
        vb = blocks[B_VIEWS]
        lvl.views = [View(*struct.unpack_from('<HHHHBBBBBBBB', vb, i)) for i in range(0, len(vb) - 15, 16)]
        zb = blocks[B_ZONES]
        lvl.zones = [Zone(*struct.unpack_from('<HHHHB', zb, i), bytes(zb[i + 9:i + 12])) for i in range(0, len(zb) - 11, 12)]
        return lvl

    def save(self):
        blocks = [bytearray(b) for b in self.blocks]
        blocks[B_SPRITES] = bytearray(b''.join(s.pack() for s in self.sprites) + b'\xff\xff\xff\xff')
        blocks[B_ENTRANCES] = bytearray(b''.join(bytes(e.raw) for e in self.entrances))
        blocks[B_VIEWS] = bytearray(b''.join(v.pack() for v in self.views))
        blocks[B_ZONES] = bytearray(b''.join(z.pack() for z in self.zones))
        out = bytearray()
        offs = 8 * BLOCK_COUNT
        hdr = bytearray()
        for b in blocks:
            hdr += struct.pack('<II', offs, len(b))
            offs += len(b)
        out = hdr + b''.join(blocks)
        bg = b''.join(o.pack() for o in self.objects) + b'\xff\xff'
        return bytes(out), bytes(bg)

    # handige accessors
    @property
    def tileset_id(self):
        return self.blocks[B_SETTINGS][0x0C]

    def camera_entries(self):
        cb = self.blocks[B_CAMERA]
        return [struct.unpack_from('<iiiiHHI', cb, i) for i in range(0, len(cb) - 23, 24)]
