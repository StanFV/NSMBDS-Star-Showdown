"""Minimale bewerker voor BMG-berichtbestanden (MESGbmg1, UTF-16).

Bestaande teksten blijven byte-voor-byte staan (ze kunnen escape-codes
bevatten). Een gewijzigd bericht wordt achteraan DAT1 toegevoegd en alleen
de pointer in INF1 wordt aangepast.
"""
import struct


class BMG:
    def __init__(self, data: bytes):
        assert data[:8] == b'MESGbmg1', 'geen BMG'
        self.header = bytearray(data[:0x20])
        self.sections = []
        pos = 0x20
        while pos + 8 <= len(data):
            magic = data[pos:pos + 4]
            size = struct.unpack_from('<I', data, pos + 4)[0]
            if size < 8:
                break
            self.sections.append([magic, bytearray(data[pos + 8:pos + size])])
            pos += size
        self.inf = self._sec(b'INF1')
        self.dat = self._sec(b'DAT1')
        self.count, self.entry_size = struct.unpack_from('<HH', self.inf, 0)

    def _sec(self, magic):
        return next(s[1] for s in self.sections if s[0] == magic)

    def _off(self, i):
        return struct.unpack_from('<I', self.inf, 8 + i * self.entry_size)[0]

    def get(self, i):
        """Tekst tot de eerste 0x0000 (alleen bedoeld voor gewone teksten)."""
        off, end = self._off(i), self._off(i)
        while end + 1 < len(self.dat) and self.dat[end:end + 2] != b'\0\0':
            end += 2
        return self.dat[off:end].decode('utf-16-le', errors='replace')

    def find(self, text):
        for i in range(self.count):
            if self.get(i) == text:
                return i
        raise KeyError(text)

    def set(self, i, text):
        # DAT1 eindigt mogelijk met opvulling; nieuwe tekst 2-byte uitgelijnd erachter
        while len(self.dat) % 2:
            self.dat.append(0)
        off = len(self.dat)
        self.dat += text.encode('utf-16-le') + b'\0\0'
        struct.pack_into('<I', self.inf, 8 + i * self.entry_size, off)

    def save(self):
        out = bytearray()
        for magic, body in self.sections:
            body = bytearray(body)
            while (len(body) + 8) % 32:
                body.append(0)
            out += magic + struct.pack('<I', len(body) + 8) + body
        hdr = bytearray(self.header)
        struct.pack_into('<I', hdr, 8, len(out) + 0x20)
        return bytes(hdr + out)
