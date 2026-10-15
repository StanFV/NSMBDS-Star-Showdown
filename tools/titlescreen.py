"""Puts the Star Showdown logo on the title screen (top screen).

The game draws its logo with sprites at fixed places (see the tables below).
We clear the old logo tiles and draw our own art into two of those sprite
groups, each with its own 16-colour palette:
  * the star goes where the "New" badge was (palette 1);
  * the text goes where the dark outline layer was (palette 2).
The letter layer of the old logo (palette 0) is cleared. Palette 0 itself is
left alone because the "(c) 2006 Nintendo" line also uses it.
"""
import struct
from PIL import Image

NCG_FILES = [f'uiStudio/UI_O_menu_title_logo_o_u_ncg.bin.{l}' for l in ('EEN', 'EFR', 'EGE', 'EIT', 'ESP')]
NCL_FILE = 'uiStudio/d_2d_UI_O_menu_title_logo_o_u_ncl.bin'
UNIT = 128  # 1D sprite mapping with a 128-byte boundary

# (x, y, width, height, first unit) of the sprites of the old logo
STAR_SPRITES = [(31, 10, 64, 64, 0), (95, 10, 8, 32, 16), (95, 42, 8, 32, 17)]
TEXT_SPRITES = [(19, 24, 64, 64, 102), (83, 24, 64, 64, 118), (147, 24, 64, 64, 134), (211, 56, 16, 32, 150),
                (19, 88, 64, 32, 152), (83, 88, 64, 32, 160), (147, 88, 64, 32, 168), (211, 88, 16, 32, 176),
                (227, 88, 8, 32, 178), (235, 88, 32, 32, 98)]
OLD_LETTER_UNITS = range(18, 87)  # palette 0 letters ("SUPER", "MARIO BROS.")


def _quantize(img):
    """15 colours + transparency. Returns (index image, list of 15 RGB)."""
    rgba = img.convert('RGBA')
    alpha = rgba.getchannel('A')
    flat = Image.new('RGB', rgba.size, (0, 0, 0))
    flat.paste(rgba.convert('RGB'), (0, 0), alpha)
    q = flat.quantize(colors=15, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()[:45]
    pal += [0] * (45 - len(pal))
    return q, alpha, [tuple(pal[i * 3:i * 3 + 3]) for i in range(15)]


def _draw(tiles, img, sprites):
    q, alpha, pal = _quantize(img)
    px, ap = q.load(), alpha.load()
    for sx, sy, w, h, unit in sprites:
        base = unit * UNIT
        tw = w // 8
        for ty in range(h // 8):
            for tx in range(tw):
                off = base + (ty * tw + tx) * 32
                for y in range(8):
                    for x in range(0, 8, 2):
                        v = []
                        for dx in (0, 1):
                            X, Y = sx + tx * 8 + x + dx, sy + ty * 8 + y
                            inside = 0 <= X < 256 and 0 <= Y < 192
                            v.append(px[X, Y] + 1 if inside and ap[X, Y] else 0)
                        tiles[off + y * 4 + x // 2] = v[0] | (v[1] << 4)
    return pal


def _pal_bytes(pal):
    out = bytearray(32)
    for i, (r, g, b) in enumerate(pal):
        struct.pack_into('<H', out, 2 + i * 2, (r >> 3) | ((g >> 3) << 5) | ((b >> 3) << 10))
    return bytes(out)


def build(ncg: bytes, ncl: bytes, star_png: str, text_png: str):
    """Returns the new (ncg, ncl) data (both uncompressed)."""
    tiles = bytearray(ncg)
    for u in list(OLD_LETTER_UNITS) + list(range(0, 18)) + list(range(98, 180)):
        tiles[u * UNIT:(u + 1) * UNIT] = bytes(UNIT)
    pal_star = _draw(tiles, Image.open(star_png), STAR_SPRITES)
    pal_text = _draw(tiles, Image.open(text_png), TEXT_SPRITES)
    pals = bytearray(ncl)
    pals[32:64] = _pal_bytes(pal_star)
    pals[64:96] = _pal_bytes(pal_text)
    return bytes(tiles), bytes(pals)
