"""ARM9 code patches for the European ROM (A2DP, EUR).

Adds extra pages to the Mario vs Luigi stage select menu:
  * R goes to the next page, L to the previous one;
  * the thumbnails and palettes are swapped live in VRAM;
  * when a stage loads, the stage files in the course table are switched;
  * the "Random" setting picks from the stages on all pages.

Our own code and data live in an extra autoload section at 0x0219A100.
The heap (arena) is moved up a little to make room for it.
"""
import struct
from keystone import Ks, KS_ARCH_ARM, KS_MODE_ARM

# ---- addresses (EUR) ---------------------------------------------------------
ARENA_LO_LITERAL = 0x02055EF8   # literal holding the start of the main arena
ARENA_LO = 0x0219A100
COURSE_BIN_J01 = 0x0202C8C4     # course table (.bin), index 181 = J01
COURSE_BGDAT_J01 = 0x0202C5DC   # course table (_bgdat), index 181 = J01
ARCHIVE_TABLE = 0x02029D54      # archive table (0x1C per row)
KEYS_PRESSED = 0x02099CB4       # synchronised input; +2 = newly pressed
PLAY_SE = 0x020128F8
SE_CURSOR = 0xE5

OV052_GETSTAGE_RET = 0x02160E54     # 'bx lr' of getStage()
OV052_STAGESEL_UPDATE = 0x02161B30  # 'push {r4,r5,r6,lr}' of state 6 (stage select)
OV052_RANDOM_MUL = 0x02161FAC       # 'mov r2, #5'
OV052_RANDOM_STORE = 0x02161FC4     # 'strb r2, [r1]'
OV009_TITLE_CASE0 = 0x020E5148      # 'b 0x20e5158' (Mario Game)
OV009_TITLE_CASE1_TARGET = 0x020E5178

THUMB_VRAM = 0x06600000 + 36 * 32   # sub-OBJ tiles of the five thumbnails
THUMB_TILES_SIZE = 5 * 36 * 32      # 5760 bytes
THUMB_PAL = 0x05000600 + 3 * 32     # sub-OBJ palettes 3, 5, 7, 9, 11
THUMB_PAGE_SIZE = THUMB_TILES_SIZE + 5 * 32

_ks = Ks(KS_ARCH_ARM, KS_MODE_ARM)


def asm(src, addr):
    enc, _ = _ks.asm(src, addr)
    return bytes(enc)


def branch(frm, to, link=False):
    off = (to - frm - 8) >> 2
    return struct.pack('<I', (0xEB if link else 0xEA) << 24 | (off & 0xFFFFFF))


def build_section(entries_pages, thumbs_pages, check_off):
    """Build the autoload section for N pages. Returns (bytes, symbols).

    entries_pages: per page 10 words (5x .bin, 5x _bgdat) for the course table.
    thumbs_pages: per page THUMB_PAGE_SIZE bytes (tiles + 5 palettes).
    check_off: offset in the tile data where all pages differ from each other.
    """
    npages = len(entries_pages)
    assert npages == len(thumbs_pages) and 2 <= npages <= 5
    base = ARENA_LO
    code_size = 0x200
    PAGE = base + code_size
    ENTRIES = PAGE + 4
    THUMBS = ENTRIES + 40 * npages
    funcs = [
        ('getstage_tail', f"""
        push {{r0, r4, r5, lr}}
        ldr r1, =0x{PAGE:x}
        ldrb r1, [r1]
        ldr r2, =0x{ENTRIES:x}
        mov r3, #40
        mla r2, r1, r3, r2
        ldr r3, =0x{COURSE_BIN_J01:x}
        ldm r2!, {{r0, r1, r4, r5, r12}}
        stm r3, {{r0, r1, r4, r5, r12}}
        ldr r3, =0x{COURSE_BGDAT_J01:x}
        ldm r2!, {{r0, r1, r4, r5, r12}}
        stm r3, {{r0, r1, r4, r5, r12}}
        pop {{r0, r4, r5, lr}}
        bx lr
        """),
        ('sync_vram', f"""
        push {{r4, r5, r6, r7, r8, lr}}
        ldr r0, =0x{PAGE:x}
        ldrb r0, [r0]
        ldr r4, =0x{THUMBS:x}
        ldr r1, =0x{THUMB_PAGE_SIZE:x}
        mla r4, r0, r1, r4
        ldr r5, =0x{THUMB_VRAM:x}
        ldr r1, =0x{check_off:x}
        ldr r2, [r4, r1]
        ldr r3, [r5, r1]
        cmp r2, r3
        beq done
        mov r6, #0x{THUMB_TILES_SIZE // 4:x}
    tiles:
        ldr r2, [r4], #4
        str r2, [r5], #4
        subs r6, r6, #1
        bne tiles
        ldr r5, =0x{THUMB_PAL:x}
        mov r7, #5
    pals:
        mov r6, #8
    words:
        ldr r2, [r4], #4
        str r2, [r5], #4
        subs r6, r6, #1
        bne words
        add r5, r5, #32
        subs r7, r7, #1
        bne pals
    done:
        pop {{r4, r5, r6, r7, r8, lr}}
        bx lr
        """),
        ('stagesel_hook', """
        push {{r0, r1, r2, r3, r12, lr}}
        ldr r1, =0x{KEYS:x}
        ldrh r1, [r1, #2]
        ldr r2, =0x{PAGE:x}
        ldrb r3, [r2]
        tst r1, #0x100
        beq notr
        add r3, r3, #1
        cmp r3, #{N}
        movge r3, #0
        b changed
    notr:
        tst r1, #0x200
        beq skip
        subs r3, r3, #1
        movmi r3, #{NM1}
    changed:
        strb r3, [r2]
        mov r0, #0x{SE:x}
        mov r1, #0
        bl #0x{PLAY_SE:x}
    skip:
        bl #0x{{sync_vram:x}}
        pop {{r0, r1, r2, r3, r12, lr}}
        push {{r4, r5, r6, lr}}
        b #0x{RET:x}
        """.format(KEYS=KEYS_PRESSED, PAGE=PAGE, SE=SE_CURSOR, PLAY_SE=PLAY_SE,
                   RET=OV052_STAGESEL_UPDATE + 4, N=npages, NM1=npages - 1)),
        ('random_hook', f"""
        ldr r3, =0x{PAGE:x}
        mov r12, #0
    loop:
        cmp r2, #5
        blt store
        sub r2, r2, #5
        add r12, r12, #1
        b loop
    store:
        strb r12, [r3]
        strb r2, [r1]
        bx lr
        """),
    ]
    code = bytearray()
    syms = {}
    for name, src in funcs:
        addr = base + len(code)
        syms[name] = addr
        src = src.replace('{sync_vram:x}', f"{syms.get('sync_vram', 0):x}")
        code += asm(src + '\n.ltorg\n', addr)
        while len(code) % 4:
            code += b'\0'
    assert len(code) <= code_size, hex(len(code))
    data = bytearray(code.ljust(code_size, b'\0'))
    data += b'\0' * 4  # PAGE
    for entries in entries_pages:
        assert len(entries) == 10
        for e in entries:
            data += struct.pack('<I', e)
    for t in thumbs_pages:
        assert len(t) == THUMB_PAGE_SIZE
        data += t
    while len(data) % 32:
        data += b'\0'
    syms['PAGE'] = PAGE
    syms['NPAGES'] = npages
    return bytes(data), syms


def patch_overlay52(data, ram, syms):
    d = bytearray(data)

    def put(addr, b):
        d[addr - ram:addr - ram + len(b)] = b

    def expect(addr, word):
        got = struct.unpack_from('<I', d, addr - ram)[0]
        assert got == word, f'ov052 {addr:#x}: {got:#x} != {word:#x}'

    expect(OV052_GETSTAGE_RET, 0xE12FFF1E)
    put(OV052_GETSTAGE_RET, branch(OV052_GETSTAGE_RET, syms['getstage_tail']))
    expect(OV052_STAGESEL_UPDATE, 0xE92D4070)
    put(OV052_STAGESEL_UPDATE, branch(OV052_STAGESEL_UPDATE, syms['stagesel_hook']))
    expect(OV052_RANDOM_MUL, 0xE3A02005)
    put(OV052_RANDOM_MUL, asm(f"mov r2, #{5 * syms['NPAGES']}", OV052_RANDOM_MUL))
    expect(OV052_RANDOM_STORE, 0xE5C12000)
    put(OV052_RANDOM_STORE, branch(OV052_RANDOM_STORE, syms['random_hook'], link=True))
    return bytes(d)


def patch_overlay9_title(data, ram):
    """Make the 'Mario Game' button in the title menu start Mario vs Luigi."""
    d = bytearray(data)
    o = OV009_TITLE_CASE0 - ram
    assert d[o:o + 4] == branch(OV009_TITLE_CASE0, 0x020E5158), 'unknown ov009'
    d[o:o + 4] = branch(OV009_TITLE_CASE0, OV009_TITLE_CASE1_TARGET)
    return bytes(d)


# ---- title menu: only "Mario Vs. Luigi" and "Options" ----------------------
# Buttons: 0 Mario Game, 1 Mario Vs. Luigi, 2 Minigames, 3 Options.
OV009_PATCHES = [
    # (address, original instruction, new instruction)
    (0x020E18E0, 'mov r8, #0', 'mov r8, #1'),            # draw loop starts at button 1
    (0x020E18E4, 'mov fp, r8', 'mov fp, #0'),            # (r8 was also used as a zero)
    (0x020E18E8, 'mov r5, r8', 'mov r5, #0'),
    (0x020E1980, 'add r8, r8, #1', 'add r8, r8, #2'),    # ... and draws buttons 1 and 3
    (0x020E52B0, 'cmp r7, #3', 'tst r7, #1'),            # touch: only buttons 1 and 3 count
    (0x020E52B4, 'bgt #0x20e538c', 'beq #0x20e538c'),
    (0x020E5364, 'addne r1, r1, #1', 'addne r1, r1, #2'),  # d-pad down: 1 -> 3
    (0x020E5378, 'cmp r4, #0', 'cmp r4, #1'),            # d-pad up: 3 -> 1
    (0x020E5384, 'subne r1, r1, #1', 'subne r1, r1, #2'),
    (0x020E5924, 'moveq r1, #2', 'moveq r1, #1'),        # default selection: button 1
    (0x020E5934, 'mov r1, #0', 'mov r1, #1'),
]


def patch_overlay9_single_button(data, ram):
    """Show only the "Mario Vs. Luigi" and "Options" buttons on the title menu."""
    d = bytearray(data)
    for addr, old, new in OV009_PATCHES:
        o = addr - ram
        if old is not None:
            assert d[o:o + 4] == asm(old, addr), f'ov009 {addr:#x}: unexpected code'
        d[o:o + 4] = asm(new, addr)
    return bytes(d)
