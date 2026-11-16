"""Draws the Star Showdown logo (original design, font Lilita One, OFL).

Usage: python3 tools/make_logo.py path/to/LilitaOne-Regular.ttf docs/ assets/
"""
import math
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SS = 3  # supersampling
RED, GREEN = (229, 37, 33), (67, 176, 71)
GOLD, GOLD_DARK = (255, 210, 63), (232, 150, 20)
NAVY = (24, 28, 66)
WHITE = (255, 255, 255)


def star_points(cx, cy, r_out, r_in, rot=-90):
    pts = []
    for i in range(10):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 36)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def draw_star(img, cx, cy, r):
    """Star with a red (Mario) and a green (Luigi) half, with white and dark outlines."""
    d = ImageDraw.Draw(img)
    outer = star_points(cx, cy, r * 1.16, r * 0.5 * 1.16)
    d.polygon(outer, fill=NAVY)
    mid = star_points(cx, cy, r * 1.07, r * 0.5 * 1.07)
    d.polygon(mid, fill=WHITE)
    pts = star_points(cx, cy, r, r * 0.5)
    mask_l = Image.new('L', img.size, 0)
    ImageDraw.Draw(mask_l).polygon(pts, fill=255)
    left = Image.new('L', img.size, 0)
    ImageDraw.Draw(left).polygon([(0, 0), (cx + r * 0.08, 0), (cx - r * 0.08, img.size[1]), (0, img.size[1])], fill=255)
    red = Image.new('RGBA', img.size, RED + (255,))
    green = Image.new('RGBA', img.size, GREEN + (255,))
    from PIL import ImageChops
    img.paste(green, (0, 0), mask_l)
    img.paste(red, (0, 0), ImageChops.multiply(mask_l, left))
    # shine
    gl = star_points(cx - r * 0.12, cy - r * 0.15, r * 0.45, r * 0.22)
    hl = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(hl).polygon(gl, fill=(255, 255, 255, 70))
    img.alpha_composite(hl)
    # lightning split, only inside the star
    bolt = Image.new('L', img.size, 0)
    ImageDraw.Draw(bolt).line([(cx + r * 0.10, cy - r * 1.1), (cx - r * 0.06, cy - r * 0.12),
                               (cx + r * 0.09, cy + r * 0.02), (cx - r * 0.10, cy + r * 1.0)],
                              fill=255, width=int(r * 0.08), joint='curve')
    from PIL import ImageChops
    img.paste(Image.new('RGBA', img.size, WHITE + (255,)), (0, 0), ImageChops.multiply(bolt, mask_l))


def text_layer(size, text, font, fill_top, fill_bottom, stroke, sw):
    """Text with a vertical gradient and a thick outline."""
    W, H = size
    mask = Image.new('L', size, 0)
    ImageDraw.Draw(mask).text((W // 2, H // 2), text, font=font, anchor='mm', fill=255)
    outline = Image.new('L', size, 0)
    ImageDraw.Draw(outline).text((W // 2, H // 2), text, font=font, anchor='mm', fill=255,
                                 stroke_width=sw, stroke_fill=255)
    grad = Image.new('RGBA', size)
    bbox = mask.getbbox()
    top, bot = bbox[1], bbox[3]
    gd = ImageDraw.Draw(grad)
    for y in range(H):
        t = min(1, max(0, (y - top) / max(1, bot - top)))
        c = tuple(int(fill_top[i] * (1 - t) + fill_bottom[i] * t) for i in range(3))
        gd.line([(0, y), (W, y)], fill=c + (255,))
    out = Image.new('RGBA', size, (0, 0, 0, 0))
    shadow = Image.new('RGBA', size, (0, 0, 0, 0))
    shadow.paste(Image.new('RGBA', size, (0, 0, 0, 110)), (int(sw * 0.6), int(sw * 0.9)), outline)
    out.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(sw * 0.4)))
    out.paste(Image.new('RGBA', size, stroke + (255,)), (0, 0), outline)
    out.paste(grad, (0, 0), mask)
    return out


def make_logo(font_path, out_dir):
    W, H = 1200 * SS, 420 * SS
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw_star(img, int(200 * SS), int(205 * SS), int(165 * SS))
    big = ImageFont.truetype(font_path, 150 * SS)
    mid = ImageFont.truetype(font_path, 118 * SS)
    small = ImageFont.truetype(font_path, 40 * SS)
    t1 = text_layer((820 * SS, 190 * SS), 'STAR', big, (255, 236, 120), GOLD_DARK, NAVY, 14 * SS)
    t2 = text_layer((820 * SS, 160 * SS), 'SHOWDOWN', mid, (255, 255, 255), (190, 214, 255), NAVY, 13 * SS)
    img.alpha_composite(t1, (330 * SS, 10 * SS))
    img.alpha_composite(t2, (330 * SS, 175 * SS))
    tag = text_layer((820 * SS, 70 * SS), '20 MARIO VS LUIGI ARENAS', small, WHITE, WHITE, RED, 7 * SS)
    img.alpha_composite(tag, (330 * SS, 330 * SS))
    logo = img.resize((W // SS, H // SS), Image.LANCZOS)
    logo = logo.crop(logo.getbbox())
    logo.save(f'{out_dir}/logo.png')
    # square icon
    ic = Image.new('RGBA', (512 * SS, 512 * SS), (0, 0, 0, 0))
    draw_star(ic, 256 * SS, 266 * SS, 200 * SS)
    ic.resize((512, 512), Image.LANCZOS).save(f'{out_dir}/icon.png')
    return logo




def make_title_art(font_path, out_dir):
    """Art for the title screen (256x192, top screen), split into two layers.

    The game draws its logo with sprites in fixed places, so the art has to fit
    those areas: the star goes where the old "New" badge was (palette 1) and
    the text goes where the old outline layer was (palette 2)."""
    S = 4
    star = Image.new('RGBA', (256 * S, 192 * S), (0, 0, 0, 0))
    draw_star(star, int(66 * S), int(44 * S), int(29 * S))
    text = Image.new('RGBA', (256 * S, 192 * S), (0, 0, 0, 0))
    big = ImageFont.truetype(font_path, 46 * S)
    mid = ImageFont.truetype(font_path, 34 * S)
    t1 = text_layer((120 * S, 60 * S), 'STAR', big, (255, 236, 120), GOLD_DARK, NAVY, 5 * S)
    t2 = text_layer((256 * S, 56 * S), 'SHOWDOWN', mid, (255, 255, 255), (190, 214, 255), NAVY, 5 * S)
    text.alpha_composite(t1, (94 * S, 20 * S))
    text.alpha_composite(t2, (-5 * S, 72 * S))
    for name, layer in (('title_star', star), ('title_text', text)):
        small = layer.resize((256, 192), Image.LANCZOS)
        a = small.getchannel('A').point(lambda v: 255 if v >= 110 else 0)
        small.putalpha(a)
        small.save(f'{out_dir}/{name}.png')


if __name__ == '__main__':
    print(make_logo(sys.argv[1], sys.argv[2]).size)
    make_title_art(sys.argv[1], sys.argv[3] if len(sys.argv) > 3 else sys.argv[2])
