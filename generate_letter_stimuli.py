"""
generate_letter_stimuli.py
==========================
Generates 1000×1000 px PNG stimulus images for a letter-recognition experiment.

Each letter is rendered in Arial on a white background and saved under
``letter_stimuli/<letter>/``.  The following variants are produced:

* **Baseline** – centered, normal size, upright
* **Large** – centered, large size, upright
* **Rotated** – 90° clockwise, centered, normal size
* **Flip H / Flip V** – horizontal / vertical mirror *(unambiguous letters only)*

Mirror-ambiguous letters (b, d, p, q) are skipped for flip variants because
their mirrors are other valid members of the set, already present as
independent stimuli.

Expected output: 4 ambiguous × 3 + 7 unambiguous × 5 = 47 images.
"""

from PIL import Image, ImageDraw, ImageFont
import os

# ── Configuration ─────────────────────────────────────────────────────────

image_size = (1000, 1000)
background_color = 'white'
text_color = 'black'

font_size_default = 500
font_size_large = 750

# Mirror-ambiguous quad: mirrors are other valid letters, so no flip variants
no_flip_letters = ['b', 'd', 'p', 'q']

# Full letter set: 4 ambiguous + 7 unambiguous
letters = ['b', 'd', 'p', 'q', 'f', 'h', 'e', 'a', 'k', 'r']

output_dir = 'letter_stimuli'
os.makedirs(output_dir, exist_ok=True)

for letter in letters:
    os.makedirs(os.path.join(output_dir, letter), exist_ok=True)

# ── Font loading ──────────────────────────────────────────────────────────

try:
    font_default = ImageFont.truetype("arial.ttf", font_size_default)
    font_large   = ImageFont.truetype("arial.ttf", font_size_large)
except OSError:
    print("Warning: arial.ttf not found, falling back to default font.")
    font_default = ImageFont.load_default()
    font_large   = ImageFont.load_default()

# ── Core helpers ──────────────────────────────────────────────────────────

def create_letter_image(letter, font_size="normal", position=None,
                        rotation=0, flip_h=False, flip_v=False):
    """Create a 1000×1000 stimulus image for a given letter and transformation.

    Parameters
    ----------
    letter    : str  – single character to render
    font_size : str  – ``"normal"`` or ``"large"``
    position  : str  – ``None`` (centre), ``"top_left"``, or ``"bottom_right"``
    rotation  : int  – clockwise degrees (e.g. 0 or 90)
    flip_h    : bool – horizontal mirror (left–right)
    flip_v    : bool – vertical mirror (top–bottom)

    Returns
    -------
    PIL.Image.Image
    """
    img  = Image.new('RGB', image_size, background_color)
    draw = ImageDraw.Draw(img)

    font = font_large if font_size == "large" else font_default

    bbox        = draw.textbbox((0, 0), letter, font=font)
    text_width  = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    w, h        = image_size

    if position is None:
        x = (w - text_width)  // 2 - bbox[0]
        y = (h - text_height) // 2 - bbox[1]
    elif position == 'top_left':
        x = w // 4 - text_width  // 2 - bbox[0]
        y = h // 4 - text_height // 2 - bbox[1]
    elif position == 'bottom_right':
        x = 3 * w // 4 - text_width  // 2 - bbox[0]
        y = 3 * h // 4 - text_height // 2 - bbox[1]
    else:
        raise ValueError(f"Unknown position: {position!r}")

    draw.text((x, y), letter, font=font, fill=text_color)

    if flip_h:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    if flip_v:
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
    if rotation:
        # PIL rotate() is counter-clockwise; negate for clockwise
        img = img.rotate(-rotation, expand=False, fillcolor=background_color)

    return img


def build_filename(letter, font_size="normal", position=None,
                   rotation=0, flip_h=False, flip_v=False):
    """Return the output path for a stimulus with the given parameters.

    Parameters
    ----------
    letter, font_size, position, rotation, flip_h, flip_v
        Same semantics as :func:`create_letter_image`.

    Returns
    -------
    str – path relative to the working directory
    """
    parts = [letter, font_size]
    if position is not None: parts.append(position)
    if rotation:             parts.append(f"rot{rotation}")
    if flip_h:               parts.append("flip_h")
    if flip_v:               parts.append("flip_v")
    return os.path.join(output_dir, letter, "_".join(parts) + ".png")


def save_stimulus(counter, **kwargs):
    """Create, save, and log a single stimulus image.

    Parameters
    ----------
    counter : int   – running index for the log line
    **kwargs        – forwarded to :func:`create_letter_image` and
                      :func:`build_filename` (same signature)

    Returns
    -------
    int – ``counter + 1``
    """
    path = build_filename(**kwargs)
    create_letter_image(**kwargs).save(path)
    counter += 1
    print(f"[{counter:02d}] {path}")
    return counter


# ── Stimulus generation ───────────────────────────────────────────────────

counter = 0

for letter in letters:
    is_ambiguous = letter in no_flip_letters

    counter = save_stimulus(counter, letter=letter)                    # baseline
    counter = save_stimulus(counter, letter=letter, font_size="large") # large
    counter = save_stimulus(counter, letter=letter, rotation=90)       # 90° CW

    if not is_ambiguous:
        counter = save_stimulus(counter, letter=letter, flip_h=True)   # mirror H
        counter = save_stimulus(counter, letter=letter, flip_v=True)   # mirror V

    n    = 3 if is_ambiguous else 5
    kind = 'ambiguous' if is_ambiguous else 'unambiguous'
    print(f"     → {letter} ({kind}): {n} stimuli\n")

# ── Summary ───────────────────────────────────────────────────────────────

print("=" * 50)
print(f"Done! {counter} images created in '{output_dir}/'")