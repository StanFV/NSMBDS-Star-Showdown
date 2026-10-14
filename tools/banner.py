"""Updates the banner shown in the DS menu (title and 32x32 icon)."""
import struct
from PIL import Image


def crc16(data):
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return crc


def set_banner(banner: bytes, title: str, icon: Image.Image = None) -> bytes:
    b = bytearray(banner)
    assert struct.unpack_from('<H', b, 2)[0] == crc16(b[0x20:0x840]), 'unknown banner format'
    enc = title.encode('utf-16-le')
    assert len(enc) <= 0xFE, 'title too long'
    for lang in range(6):
        off = 0x240 + lang * 0x100
        b[off:off + 0x100] = enc.ljust(0x100, b'\0')
    if icon is not None:
        im = icon.convert('RGBA').resize((32, 32), Image.LANCZOS)
        flat = Image.new('RGB', (32, 32), (255, 0, 255))
        alpha = im.getchannel('A').point(lambda a: 255 if a >= 128 else 0)
        flat.paste(im.convert('RGB'), (0, 0), alpha)
        q = flat.quantize(colors=15, method=Image.Quantize.MEDIANCUT)
        pal = q.getpalette()[:45]
        px, ap = q.load(), alpha.load()
        tiles = bytearray(512)
        for ty in range(4):
            for tx in range(4):
                for y in range(8):
                    for x in range(0, 8, 2):
                        v = []
                        for dx in (0, 1):
                            X, Y = tx * 8 + x + dx, ty * 8 + y
                            v.append(px[X, Y] + 1 if ap[X, Y] else 0)
                        tiles[(ty * 4 + tx) * 32 + y * 4 + x // 2] = v[0] | (v[1] << 4)
        palb = bytearray(32)
        for i in range(15):
            r, g, bb = pal[i * 3:i * 3 + 3] if i * 3 + 2 < len(pal) else (0, 0, 0)
            struct.pack_into('<H', palb, 2 + i * 2, (r >> 3) | ((g >> 3) << 5) | ((bb >> 3) << 10))
        b[0x20:0x220] = tiles
        b[0x220:0x240] = palb
    struct.pack_into('<H', b, 2, crc16(b[0x20:0x840]))
    return bytes(b)
