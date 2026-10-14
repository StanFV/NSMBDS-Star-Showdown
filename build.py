#!/usr/bin/env python3
"""Bouwt NSMB DS Versus uit een eigen, legaal verkregen Europese ROM.

Gebruik:
    python3 build.py "New Super Mario Bros. (Europe) (En,Fr,De,Es,It).nds"

Uitvoer:
    out/NSMB-DS-Versus.nds          de gepatchte ROM
    out/NSMB-DS-Versus.xdelta       xdelta3-patch (alleen als xdelta3 beschikbaar is)
    out/previews/*.png              previews van de nieuwe stages
"""
import argparse
import hashlib
import os
import re
import shutil
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, 'tools'), os.path.join(HERE, 'levels')]

import ndspy.code
import ndspy.lz10
import ndspy.narc
import ndspy.rom
from PIL import Image

import codepatch
from bmg import BMG
import stages
from nsmbgfx import LevelRenderer
from nsmblevel import Level

ORIGINAL_SHA1 = 'b0f7886720e842ed922569e1bb5c39c0fa090331'
FILE_OFFSET = 135  # bestands-ID's in de tabellen zijn relatief
THUMB_AREA = 192  # uitsnede in pixels voor een thumbnail (48x48)

# Elke pagina heeft vijf plekken; plek k gebruikt altijd het thema-archief van
# originele stage k (zelfde tileset, achtergrond en vijanden).
SLOTS = [
    # basisstage, archief, achtergrondkleur voor previews
    ('J01_1', 'Dat_Field', (92, 148, 252)),
    ('J02_1', 'Dat_Basement', (20, 24, 48)),
    ('J03_1', 'Dat_Ice', (168, 208, 248)),
    ('J04_1', 'Dat_Pipe', (48, 60, 40)),
    ('J05_1', 'Dat_Fort', (40, 48, 104)),
]

# Per pagina vijf stages: (ontwerpfunctie, thumbnail-uitsnede in tegels)
PAGES = [
    [(stages.heuvelrug, (23, 8)), (stages.steengroeve, (6, 7)), (stages.ijsbaan, (36, 14)),
     (stages.buizenstelsel, (22, 11)), (stages.kantelen, (14, 9))],
    [(stages.zweefeilanden, (20, 10)), (stages.doolhof, (8, 6)), (stages.glijbaan, (54, 14)),
     (stages.pijpenorgel, (14, 11)), (stages.kerker, (22, 6))],
    [(stages.trappenpiramide, (22, 4)), (stages.muntenkluis, (8, 8)), (stages.bevrorenmeer, (54, 8)),
     (stages.riool, (16, 10)), (stages.torenspits, (22, 4))],
]

# Op pagina 2 worden de stages ook als gewoon bestand opgeslagen (J06..J10),
# handig voor tests in single-player.
FAT_COPIES = ['J06_1', 'J07_1', 'J08_1', 'J09_1', 'J10_1']

# Extra regel onder "Kies een stage" (bericht 12 in menu_title_*.narc[20])
LR_HINT = {
    'EEN': 'L/R: more courses',
    'EFR': 'L/R : autres niveaux',
    'EGE': 'L/R: weitere Arenen',
    'EIT': 'L/R: altri livelli',
    'ESP': 'L/R: más escenarios',
}
MSG_SELECT_COURSE = 12

# Bestanden die alleen door de story mode gebruikt worden
STORY_ONLY = re.compile(r'^(demo|demoM|ending|map)/|^course/[A-H]\d\d_')


def log(msg):
    print('  ' + msg)


# ---------------------------------------------------------------------------
# Hulpfuncties voor ARM9
# ---------------------------------------------------------------------------
def arm9_patch(arm9, addr, fmt, value, expect=None):
    for s in arm9.sections:
        if s.ramAddress <= addr < s.ramAddress + len(s.data):
            d = bytearray(s.data)
            o = addr - s.ramAddress
            if expect is not None:
                got = struct.unpack_from(fmt, d, o)[0]
                assert got == expect, f'{addr:#x}: {got:#x} != {expect:#x}'
            struct.pack_into(fmt, d, o, value)
            s.data = bytes(d)
            return
    raise KeyError(hex(addr))


def arm9_read(arm9, addr, fmt):
    for s in arm9.sections:
        if s.ramAddress <= addr < s.ramAddress + len(s.data):
            return struct.unpack_from(fmt, s.data, addr - s.ramAddress)[0]
    raise KeyError(hex(addr))


# ---------------------------------------------------------------------------
# Thumbnails (sub-OBJ, 4bpp, 48x48 uit 4 sprites)
# ---------------------------------------------------------------------------
def thumb_to_obj(img, template):
    """Zet een 48x48 RGB-afbeelding om naar 36 tegels (1152 bytes) + palet (32 bytes).

    Een thumbnail bestaat uit vier sprites: 32x32 (tegel 0-15), 16x32 rechts
    (16-23), 32x16 onder (24-31) en 16x16 rechtsonder (32-35)."""
    q = img.convert('RGB').quantize(colors=15, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()[:45]
    px = q.load()
    out = bytearray(template)

    def tile(unit, ox, oy):
        for y in range(8):
            for x in range(0, 8, 2):
                a = px[ox + x, oy + y] + 1
                b = px[ox + x + 1, oy + y] + 1
                out[unit * 32 + y * 4 + x // 2] = a | (b << 4)

    for ty in range(4):
        for tx in range(4):
            tile(ty * 4 + tx, tx * 8, ty * 8)
    for ty in range(4):
        for tx in range(2):
            tile(16 + ty * 2 + tx, 32 + tx * 8, ty * 8)
    for ty in range(2):
        for tx in range(4):
            tile(24 + ty * 4 + tx, tx * 8, 32 + ty * 8)
    for ty in range(2):
        for tx in range(2):
            tile(32 + ty * 2 + tx, 32 + tx * 8, 32 + ty * 8)
    palb = bytearray(32)
    for i in range(15):
        r, g, b = pal[i * 3:i * 3 + 3] if i * 3 + 2 < len(pal) else (0, 0, 0)
        struct.pack_into('<H', palb, 2 + i * 2, (r >> 3) | ((g >> 3) << 5) | ((b >> 3) << 10))
    return bytes(out), bytes(palb)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('rom', help='originele Europese NSMB ROM (.nds)')
    ap.add_argument('-o', '--out', default=os.path.join(HERE, 'out'))
    ap.add_argument('--keep-story', action='store_true', help='story-bestanden niet verwijderen')
    ap.add_argument('--no-verify', action='store_true', help='SHA-1 van de ROM niet controleren')
    args = ap.parse_args()

    raw = open(args.rom, 'rb').read()
    sha1 = hashlib.sha1(raw).hexdigest()
    if sha1 != ORIGINAL_SHA1 and not args.no_verify:
        sys.exit(f'Onverwachte ROM (SHA-1 {sha1}).\nVerwacht: New Super Mario Bros. (Europe) (En,Fr,De,Es,It), '
                 f'SHA-1 {ORIGINAL_SHA1}')
    os.makedirs(os.path.join(args.out, 'previews'), exist_ok=True)

    rom = ndspy.rom.NintendoDSRom(raw)
    arm9 = rom.loadArm9()
    ovs = rom.loadArm9Overlays()
    renderer = LevelRenderer(rom)

    # ---- 1. nieuwe stages ------------------------------------------------
    print('Nieuwe stages bouwen')
    entries_orig = [arm9_read(arm9, codepatch.COURSE_BIN_J01 + 4 * i, '<I') for i in range(5)] + \
                   [arm9_read(arm9, codepatch.COURSE_BGDAT_J01 + 4 * i, '<I') for i in range(5)]
    entries_pages = [entries_orig]
    thumbs_pages = []
    narcs = {}
    for page_no, page in enumerate(PAGES, start=2):
        entries = [0] * 10
        thumbs = []
        for slot, (design, crop) in enumerate(page):
            base, archive, bgcol = SLOTS[slot]
            base_lvl = Level.load(rom.getFileByName(f'course/{base}.bin'),
                                  rom.getFileByName(f'course/{base}_bgdat.bin'))
            lvl_bin, lvl_bg = design(base_lvl).build()

            # a) gewoon bestand (alleen pagina 2), anders verwijst de cartridge-ID naar de basisstage
            if page_no == 2:
                target = FAT_COPIES[slot]
                rom.setFileByName(f'course/{target}.bin', lvl_bin)
                rom.setFileByName(f'course/{target}_bgdat.bin', lvl_bg)
            else:
                target = base
            fat_bin = rom.filenames.idOf(f'course/{target}.bin')
            fat_bg = rom.filenames.idOf(f'course/{target}_bgdat.bin')

            # b) in het VS-archief (wordt in Mario vs Luigi gebruikt)
            arc_hi = entries_orig[slot] >> 24                  # bv. 0xC2 voor a02
            if archive not in narcs:
                narcs[archive] = (arc_hi, ndspy.narc.NARC(rom.getFileByName(f'ARCHIVE/{archive}.narc')))
            narc = narcs[archive][1]
            idx_bin = len(narc.files)
            narc.files += [lvl_bin, lvl_bg]
            entries[slot] = ((arc_hi << 8 | idx_bin) << 16) | (fat_bin - FILE_OFFSET)
            entries[5 + slot] = ((arc_hi << 8 | (idx_bin + 1)) << 16) | (fat_bg - FILE_OFFSET)

            # c) preview en thumbnail
            lvl = Level.load(lvl_bin, lvl_bg)
            v = lvl.views[0]
            full = renderer.render(lvl, sprites=False, bg=bgcol, crop=(v.x, v.y, v.x + v.w, v.y + v.h))
            full.save(os.path.join(args.out, 'previews', f'p{page_no}_{slot + 1}_{design.__name__}.png'))
            cx, cy = crop[0] * 16, crop[1] * 16
            th = renderer.render(lvl, sprites=False, bg=bgcol).crop((cx, cy, cx + THUMB_AREA, cy + THUMB_AREA))
            thumbs.append(th.resize((48, 48), Image.LANCZOS))
            log(f'pagina {page_no}: {design.__name__:15s} -> {archive}[{idx_bin}]  '
                f'({len(lvl_bin)}+{len(lvl_bg)} bytes)')
        entries_pages.append(entries)
        thumbs_pages.append(thumbs)

    # archieven opslaan en hun bovengrens in de archieftabel ophogen
    for archive, (arc_hi, narc) in narcs.items():
        rom.setFileByName(f'ARCHIVE/{archive}.narc', narc.save())
        for i in range(0x30):
            row = codepatch.ARCHIVE_TABLE + i * 0x1C
            lo = arm9_read(arm9, row + 0x0C, '<H')
            if lo == arc_hi << 8:
                hi = arm9_read(arm9, row + 0x0E, '<H')
                arm9_patch(arm9, row + 0x0E, '<H', lo + len(narc.files), expect=hi)
                break
        else:
            raise RuntimeError(f'archief {arc_hi:#x} niet gevonden')

    # ---- 2. thumbnails ----------------------------------------------------
    print('Thumbnails maken')
    tiles0 = ndspy.lz10.decompress(ndspy.narc.NARC(rom.getFileByName('ARCHIVE/menu_title_EEN.narc')).files[9])
    tiles0 = bytes(tiles0[36 * 32:36 * 32 + codepatch.THUMB_TILES_SIZE])
    pals_all = ndspy.lz10.decompress(ndspy.narc.NARC(rom.getFileByName('ARCHIVE/menu_title.narc')).files[12])
    pals0 = b''.join(bytes(pals_all[(3 + 2 * k) * 32:(4 + 2 * k) * 32]) for k in range(5))
    page_data = [tiles0 + pals0]
    for thumbs in thumbs_pages:
        tiles, pals = b'', b''
        for k, img in enumerate(thumbs):
            t, p = thumb_to_obj(img, tiles0[k * 1152:(k + 1) * 1152])
            tiles += t
            pals += p
        page_data.append(tiles + pals)
    sheet = Image.new('RGB', (5 * 52, 52 * len(thumbs_pages)), (255, 255, 255))
    for row, thumbs in enumerate(thumbs_pages):
        for k, img in enumerate(thumbs):
            sheet.paste(img, (k * 52 + 2, row * 52 + 2))
    sheet.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST).save(
        os.path.join(args.out, 'previews', 'thumbnails.png'))
    # een woord waarop alle pagina's van elkaar verschillen (om VRAM te controleren)
    check_off = next(i for i in range(0, codepatch.THUMB_TILES_SIZE, 4)
                     if len({d[i:i + 4] for d in page_data}) == len(page_data))

    # ---- 2b. hinttekst in het menu ---------------------------------------
    for lang, hint in LR_HINT.items():
        name = f'ARCHIVE/menu_title_{lang}.narc'
        narc = ndspy.narc.NARC(rom.getFileByName(name))
        msgs = BMG(bytes(narc.files[20]))
        msgs.set(MSG_SELECT_COURSE, msgs.get(MSG_SELECT_COURSE) + '\n' + hint)
        narc.files[20] = msgs.save()
        rom.setFileByName(name, narc.save())

    # ---- 3. code -----------------------------------------------------------
    print('Code patchen')
    section, syms = codepatch.build_section(entries_pages, page_data, check_off)
    arm9.sections.insert(len(arm9.sections) - 1,
                         ndspy.code.MainCodeFile.Section(section, codepatch.ARENA_LO, 0))
    arm9_patch(arm9, codepatch.ARENA_LO_LITERAL, '<I', codepatch.ARENA_LO + len(section),
               expect=codepatch.ARENA_LO)
    log(f'{len(entries_pages)} pagina\'s, extra code/data: {len(section)} bytes op {codepatch.ARENA_LO:#x}')

    ov52 = ovs[52]
    ov52.data = codepatch.patch_overlay52(ov52.data, ov52.ramAddress, syms)
    patched = [52]
    if not args.keep_story:
        ov9 = ovs[9]
        ov9.data = codepatch.patch_overlay9_title(ov9.data, ov9.ramAddress)
        patched.append(9)
    for i in patched:
        rom.files[ovs[i].fileID] = ovs[i].save(compress=False)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
    rom.arm9 = arm9.save(compress=False)

    # ---- 4. story mode verwijderen -----------------------------------------
    if not args.keep_story:
        print('Story mode verwijderen')
        removed = 0
        for fid in range(len(rom.files)):
            name = rom.filenames.filenameOf(fid) or ''
            if STORY_ONLY.match(name):
                removed += len(rom.files[fid])
                rom.files[fid] = b''
        log(f'{removed / 1e6:.1f} MB aan story-bestanden verwijderd')

    # ---- 5. opslaan ---------------------------------------------------------
    rom.name = bytearray(b'NSMB VERSUS')
    out_rom = os.path.join(args.out, 'NSMB-DS-Versus.nds')
    rom.saveToFile(out_rom)
    print(f'Klaar: {out_rom} ({os.path.getsize(out_rom) / 1e6:.1f} MB)')

    if shutil.which('xdelta3'):
        patch = os.path.join(args.out, 'NSMB-DS-Versus.xdelta')
        if os.path.exists(patch):
            os.remove(patch)
        subprocess.run(['xdelta3', '-e', '-9', '-S', 'djw', '-s', args.rom, out_rom, patch], check=True)
        print(f'Patch: {patch} ({os.path.getsize(patch) / 1e3:.0f} kB)')


if __name__ == '__main__':
    main()
