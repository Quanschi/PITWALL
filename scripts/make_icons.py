"""Generates Pitwall PWA icons (carbon background, amber monogram) with Pillow."""
import os
from PIL import Image, ImageDraw, ImageFont

CARBON = (17, 19, 23, 255)
AMBER = (255, 176, 32, 255)
TEAL = (62, 214, 196, 255)

OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'icons')
os.makedirs(OUT_DIR, exist_ok=True)

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\arialbd.ttf",
    r"C:\Windows\Fonts\seguisb.ttf",
    r"C:\Windows\Fonts\calibrib.ttf",
]

def load_font(size):
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def draw_base(size, safe_ratio):
    img = Image.new('RGBA', (size, size), CARBON)
    d = ImageDraw.Draw(img)

    # racing line accent near the bottom
    line_y = int(size * 0.72)
    d.line(
        [(int(size*0.12), line_y), (int(size*0.4), line_y),
         (int(size*0.46), int(size*0.62)), (int(size*0.58), int(size*0.82)),
         (int(size*0.64), line_y), (int(size*0.88), line_y)],
        fill=AMBER, width=max(2, size // 60), joint='curve'
    )

    # monogram letter "P" centered within the safe zone
    letter_size = int(size * safe_ratio * 0.62)
    font = load_font(letter_size)
    text = "P"
    bbox = d.textbbox((0, 0), text, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    x = (size - tw)/2 - bbox[0]
    y = (size - th)/2 - bbox[1] - size*0.04
    d.text((x, y), text, font=font, fill=(233, 231, 225, 255))

    return img

def save(img, name):
    path = os.path.join(OUT_DIR, name)
    img.save(path, 'PNG')
    print('wrote', path)

# Standard icons (content can touch edges more)
save(draw_base(192, 0.9), 'icon-192.png')
save(draw_base(512, 0.9), 'icon-512.png')

# Maskable icon needs generous padding (safe zone ~ center 80% circle)
save(draw_base(512, 0.6), 'icon-maskable-512.png')
