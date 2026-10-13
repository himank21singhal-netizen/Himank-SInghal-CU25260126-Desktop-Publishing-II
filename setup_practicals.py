#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_photoshop_practicals.py
=============================
Scaffolds the "Adobe-Photoshop-Practicals" GitHub repository for the
Desktop Publishing practical (UAC012P, COER University).

WHAT IT CREATES
---------------
Adobe-Photoshop-Practicals/
    README.md
    Practical-01 ... Practical-06/
        Practical_NN_HIMANK_SINGHAL_253026107.psd   (layered, 8-bit RGB)
        Practical_NN_HIMANK_SINGHAL_253026107.jpg   (.png for Practical 05)
        Before_After_Practical_02.jpg               (Practical 02 only)
        README.md

IMPORTANT - READ THIS
---------------------
Everything this script draws is a clearly watermarked PLACEHOLDER
("PLACEHOLDER - replace with your own Photoshop export" banner).  The
assignment asks for your own Photoshop work, so the files are scaffolding:
open each .psd in Photoshop, do the real task, then overwrite the .psd and the
exported .jpg/.png using the SAME file names.  The READMEs are only accurate
once you have done that.

WHAT THE PSD FILES CAN AND CANNOT CONTAIN
-----------------------------------------
psd-tools is mainly a *reader*; it cannot author text layers, layer masks,
adjustment layers or layer styles.  This script therefore ships its own small
PSD writer (struct + numpy).  The PSDs it produces have genuine, separately
named pixel layers (with blend modes / opacity where useful) and a correct
flattened preview, but text is rasterised and there are no live masks,
adjustment layers or layer styles - those are what YOU add in Photoshop.
If psd-tools is installed, the script also uses it to read every PSD back as a
verification step (optional - the script works without it).

REQUIREMENTS
------------
    Python 3.9+      pip install pillow numpy          (psd-tools optional)

USAGE
-----
    python build_photoshop_practicals.py                 # creates in current folder
    python build_photoshop_practicals.py --out D:\\Work   # creates in another folder
"""
from __future__ import annotations

import argparse
import os
import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Tuple

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont

# --------------------------------------------------------------------------- #
# 1. CONFIGURATION - student / institution details (single source of truth)
# --------------------------------------------------------------------------- #
STUDENT = {
    "name": "HIMANK SINGHAL",
    "roll": "253026107",
    "course": "BCA",
    "semester": "3rd Sem",
    "university": "COER University",
    "course_code": "UAC012P",
}
ROOT_NAME = "Adobe-Photoshop-Practicals"
NAME_TOKEN = STUDENT["name"].replace(" ", "_")          # HIMANK_SINGHAL
PLACEHOLDER_TAG = "PLACEHOLDER - replace with your own Photoshop export"

Size = Tuple[int, int]
RGB = Tuple[int, int, int]


# --------------------------------------------------------------------------- #
# 2. PRACTICAL DEFINITIONS (titles / objectives / tools come from the syllabus)
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Practical:
    number: int
    title: str
    module: str
    skills: str                      # "Main Skills" column of the assessment table
    objective: str
    tools: Tuple[str, ...]
    ext: str                         # "jpg" or "png"
    extra_files: Tuple[str, ...] = field(default_factory=tuple)

    @property
    def tag(self) -> str:
        return f"{self.number:02d}"

    @property
    def folder(self) -> str:
        return f"Practical-{self.tag}"

    @property
    def stem(self) -> str:
        return f"Practical_{self.tag}_{NAME_TOKEN}_{STUDENT['roll']}"

    @property
    def psd_name(self) -> str:
        return f"{self.stem}.psd"

    @property
    def out_name(self) -> str:
        return f"{self.stem}.{self.ext}"

    @property
    def expected_files(self) -> List[str]:
        return [self.psd_name, self.out_name, *self.extra_files, "README.md"]


PRACTICALS: List[Practical] = [
    Practical(
        1, "Photoshop Interface and Basic Tools", "Module 1", "Interface & Basic Tools",
        "To understand the Adobe Photoshop workspace and practice basic editing tools by "
        "creating a 1200 x 800 pixel document that uses basic shapes (at least three), "
        "the Move, Marquee, Lasso, Brush, Eraser, Crop and Shape tools, two different "
        "colors, and text containing the student's name, roll number and course.",
        ("Photoshop workspace (Toolbar, Options Bar, Layers Panel, Properties Panel, Menu Bar)",
         "Move Tool", "Rectangular and Elliptical Marquee Tools", "Lasso Tool", "Brush Tool",
         "Eraser Tool", "Crop Tool", "Shape Tools (Rectangle, Ellipse, Polygon)",
         "Horizontal Type Tool"),
        "jpg"),
    Practical(
        2, "Photo Editing and Basic Retouching", "Module 1", "Photo Editing & Retouching",
        "To perform basic photo editing and retouching on an ordinary photograph: cropping "
        "and straightening the image, adjusting Brightness/Contrast, correcting Color "
        "Balance/Saturation, and removing at least three unwanted spots or objects using the "
        "Spot Healing Brush, Healing Brush or Clone Stamp, then preparing Before and After "
        "versions.",
        ("Crop Tool (with Straighten)", "Brightness/Contrast Adjustment",
         "Color Balance Adjustment", "Hue/Saturation Adjustment", "Spot Healing Brush Tool",
         "Healing Brush Tool", "Clone Stamp Tool", "Layers Panel and History Panel"),
        "jpg", ("Before_After_Practical_02.jpg",)),
    Practical(
        3, "Layers, Masks and Creative Composition", "Module 2", "Layers & Masks",
        "To understand layers and layer masks by creating a travel poster composite using at "
        "least three photographs, each on its own renamed layer, blended with layer masks, "
        "positioned with the Move and Transform tools, on a suitable background with a title, "
        "supporting text and at least one layer style such as Drop Shadow or Outer Glow.",
        ("Layers Panel (separate, renamed layers)", "Layer Masks with the Brush and Gradient Tools",
         "Move Tool", "Free Transform (Edit > Free Transform)",
         "Layer Styles (Drop Shadow / Stroke / Outer Glow)", "Horizontal Type Tool",
         "Gradient Tool (background)"),
        "jpg"),
    Practical(
        4, "Advanced Selection, Color Correction and Adjustment Layers", "Module 2",
        "Selection & Color Correction",
        "To practice advanced selection techniques and non-destructive color correction: "
        "selecting the main subject with the Quick Selection Tool or Magic Wand, refining the "
        "edges, applying at least two adjustment layers (such as Curves, Levels or "
        "Hue/Saturation) and using layer masks to control where each adjustment applies, "
        "ending with a composition that shows the original and edited versions.",
        ("Quick Selection Tool", "Magic Wand Tool", "Lasso Tool",
         "Select and Mask (edge refinement)",
         "Adjustment Layers (Curves, Levels, Hue/Saturation)", "Layer Masks",
         "Properties Panel"),
        "jpg"),
    Practical(
        5, "Filters, Effects, Custom Brushes and Blending Modes", "Module 2",
        "Filters, Brushes & Effects",
        "To apply filters, effects, custom brushes and blending modes in a 1200 x 800 pixel "
        "document using two Photoshop filters, a custom brush, layer styles and two blending "
        "modes such as Multiply and Overlay, with separate layers for major design elements "
        "and creative typography. The final artwork is exported as a PNG file.",
        ("Filter Menu (Gaussian Blur, Add Noise)",
         "Custom Brush (Edit > Define Brush Preset, Brush Settings Panel)",
         "Blending Modes (Multiply, Overlay)", "Layer Styles", "Gradient Tool",
         "Horizontal Type Tool", "Layers Panel"),
        "png"),
    Practical(
        6, "Complete Photoshop Project - Promotional Poster", "Module 1 + Module 2",
        "Integrated Photoshop Project",
        "To integrate the skills of Module 1 and Module 2 in a complete promotional poster for "
        "a Hackathon or College Event, using at least three layers, a layer mask, adjustment "
        "layers, advanced selections, filters, blending modes, layer styles, custom brushes "
        "and a structured, meaningfully named layer organization.",
        ("Layers Panel (named and grouped layers)", "Layer Masks", "Adjustment Layers",
         "Quick Selection / Lasso Tools (advanced selections)", "Filters",
         "Blending Modes", "Layer Styles", "Custom Brushes", "Horizontal Type Tool",
         "Shape Tools"),
        "jpg"),
]


# --------------------------------------------------------------------------- #
# 3. MARKDOWN GENERATION
# --------------------------------------------------------------------------- #
def practical_readme(p: Practical) -> str:
    """Per-practical README, following the prescribed template exactly."""
    tools = "\n".join(f"- {t}" for t in p.tools)
    files = (f"- **PSD Source:** `{p.psd_name}`\n"
             f"- **Output:** `{p.out_name}`")
    for extra in p.extra_files:
        files += f"\n- **Before/After Comparison:** `{extra}`"
    return f"""# Practical {p.tag} - {p.title}

## Student Details
- **Name:** {STUDENT['name']}
- **Roll Number:** {STUDENT['roll']}
- **Course:** {STUDENT['course']}
- **Semester:** {STUDENT['semester']}

## Objective
{p.objective}

## Tools Used
{tools}

## Output
The final artwork was created using Adobe Photoshop and exported as {p.ext.upper()}.

## Files Included
{files}
"""


def root_readme() -> str:
    """Root README: details, outline, assessment table, structure and Git LFS notes."""
    rows = "\n".join(
        f"| [Practical {p.tag}]({p.folder}/) | {p.skills} | 05 |" for p in PRACTICALS)
    index = "\n".join(f"- [Practical {p.tag} - {p.title}]({p.folder}/) ({p.module})"
                      for p in PRACTICALS)
    tree_lines = [f"{ROOT_NAME}/", "|-- README.md"]
    for p in PRACTICALS:
        tree_lines.append(f"|-- {p.folder}/")
        for f in p.expected_files:
            tree_lines.append(f"|   |-- {f}")
    tree = "\n".join(tree_lines)
    return f"""# LabSheet-1 Desktop Publishing- II (Photoshop)

## Student Details
- **Name:** {STUDENT['name']}
- **Roll Number:** {STUDENT['roll']}
- **Course:** {STUDENT['course']}
- **Semester:** {STUDENT['semester']}
- **University:** {STUDENT['university']}
- **Course Code:** {STUDENT['course_code']}

## Course Outline

### Module 1: Introduction to Adobe Photoshop
- Overview of Adobe Photoshop interface.
- Understanding raster graphics.
- Basic tools and their functions: selection, brush, eraser, etc.
- Creating and saving a new document.
- Basic photo editing and retouching.

### Module 2: Advanced Techniques in Adobe Photoshop
- Working with layers and masks.
- Using color correction and adjustment layers.
- Advanced selection techniques: Quick Selection, Magic Wand, and Lasso.
- Applying filters and effects.
- Text handling and formatting.
- Creating and using custom brushes.
- Working with blending modes and layer styles.

## Practical Index
{index}

## Assessment Pattern

| Practical | Main Skills | Marks |
|-----------|-------------|-------|
{rows}
| -- | GitHub Repository, README & File Organization | -- |
| **Total** | **All Components** | **30** |

## Repository Structure
```text
{tree}
```

## Pushing Large PSD Files with Git LFS
Photoshop PSD files grow quickly. GitHub's browser upload accepts files up to 25 MiB,
warns above 50 MiB on `git push`, and blocks any normal Git file above 100 MiB. Use
**Git Large File Storage (Git LFS)** so that large PSD files are not rejected.

1. Install Git LFS from <https://git-lfs.com> and enable it once per computer:
   ```bash
   git lfs install
   ```
2. Inside the repository, tell Git LFS to track PSD files **before** adding them:
   ```bash
   git lfs track "*.psd"
   git add .gitattributes
   ```
3. Add, commit and push as usual:
   ```bash
   git add .
   git commit -m "Add Photoshop practicals"
   git push origin main
   ```
4. If a PSD was already committed and the push is rejected, convert the history:
   ```bash
   git lfs migrate import --include="*.psd"
   git push --force-with-lease origin main
   ```
5. Do not use the browser "Upload files" button for PSDs larger than 25 MiB; push from
   the command line instead.

Confirm the instructions with your faculty/IT support before submitting the repository
link through the LMS/ERP portal.
"""


# --------------------------------------------------------------------------- #
# 4. DRAWING HELPERS (Pillow + numpy)
# --------------------------------------------------------------------------- #
_BOLD_FONTS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf", "DejaVuSans-Bold.ttf", "arialbd.ttf",
]
_REG_FONTS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "C:/Windows/Fonts/arial.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial.ttf", "DejaVuSans.ttf", "arial.ttf",
]


def get_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    """Try common system fonts, then fall back to Pillow's built-in scalable font."""
    for candidate in (_BOLD_FONTS if bold else _REG_FONTS):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=size)      # Pillow >= 10.1
    except TypeError:
        return ImageFont.load_default()


def fit_font(text: str, max_w: int, start: int, bold: bool = True, min_size: int = 10):
    """Largest font (<= start) for which `text` fits inside `max_w` pixels."""
    size = start
    while size > min_size:
        font = get_font(size, bold)
        if font.getlength(text) <= max_w:
            return font
        size -= 2
    return get_font(min_size, bold)


def new_layer(size: Size) -> Image.Image:
    return Image.new("RGBA", size, (0, 0, 0, 0))


def solid(size: Size, rgb: RGB) -> Image.Image:
    return Image.new("RGBA", size, rgb + (255,))


def vertical_gradient(size: Size, top: RGB, bottom: RGB) -> Image.Image:
    w, h = size
    t = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None, None]
    arr = np.array(top, np.float32) * (1 - t) + np.array(bottom, np.float32) * t   # (h,1,3)
    arr = np.repeat(arr, w, axis=1).astype(np.uint8)
    return Image.fromarray(arr).convert("RGBA")


def horizontal_gradient(size: Size, left: RGB, right: RGB) -> Image.Image:
    return vertical_gradient((size[1], size[0]), left, right).transpose(
        Image.Transpose.ROTATE_90).transpose(Image.Transpose.FLIP_TOP_BOTTOM)


def synthetic_photo(size: Size, seed: int,
                    sky: Tuple[RGB, RGB] = ((70, 130, 200), (250, 210, 160)),
                    hills: Tuple[RGB, ...] = ((60, 110, 85), (35, 75, 60), (20, 45, 42))
                    ) -> Image.Image:
    """Procedural landscape used as a stand-in 'photograph'."""
    rng = np.random.default_rng(seed)
    w, h = size
    img = vertical_gradient(size, *sky).convert("RGB")
    d = ImageDraw.Draw(img)
    r = int(min(w, h) * 0.09)
    cx, cy = int(w * rng.uniform(0.2, 0.8)), int(h * rng.uniform(0.18, 0.32))
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 244, 205))
    xs = np.arange(0, w + 4, 4)
    for i, colour in enumerate(hills):
        base = h * (0.52 + 0.13 * i)
        amp = h * 0.06 * (len(hills) - i)
        phase, freq = rng.uniform(0, 6.28), rng.uniform(1.5, 3.0) + i
        ys = (base + amp * np.sin(xs / w * freq * 2 * np.pi + phase)
              + 0.35 * amp * np.sin(xs / w * freq * 5.3 + phase * 2))
        d.polygon([(0, h)] + list(zip(xs.tolist(), ys.tolist())) + [(w, h)], fill=colour)
    arr = np.asarray(img).astype(np.int16)
    arr += rng.normal(0, 3.5, arr.shape).astype(np.int16)            # film grain
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def feathered(img: Image.Image, left=0, right=0, top=0, bottom=0) -> Image.Image:
    """RGB -> RGBA whose alpha ramps to 0 on the chosen edges (a soft-edge blend)."""
    w, h = img.size
    a = np.ones((h, w), np.float32)
    if left:
        a[:, :left] *= np.linspace(0, 1, left, dtype=np.float32)[None, :]
    if right:
        a[:, w - right:] *= np.linspace(1, 0, right, dtype=np.float32)[None, :]
    if top:
        a[:top, :] *= np.linspace(0, 1, top, dtype=np.float32)[:, None]
    if bottom:
        a[h - bottom:, :] *= np.linspace(1, 0, bottom, dtype=np.float32)[:, None]
    rgba = img.convert("RGBA")
    rgba.putalpha(Image.fromarray((a * 255).astype(np.uint8)))
    return rgba


def place(size: Size, img: Image.Image, xy: Tuple[int, int]) -> Image.Image:
    """Put `img` on a transparent full-size canvas at `xy` (pixels copied incl. alpha)."""
    canvas = new_layer(size)
    canvas.paste(img.convert("RGBA"), xy)
    return canvas


def shadow_layer(size: Size, box: Tuple[int, int, int, int], offset=(10, 12),
                 blur=16, alpha=120) -> Image.Image:
    layer = new_layer(size)
    x0, y0, x1, y1 = box
    ImageDraw.Draw(layer).rectangle((x0 + offset[0], y0 + offset[1],
                                     x1 + offset[0], y1 + offset[1]), fill=(0, 0, 0, alpha))
    return layer.filter(ImageFilter.GaussianBlur(blur))


def text_block(size: Size, lines: List[str], x: int, y: int, start: int, fill,
               max_w: int, gap: float = 1.3, bold: bool = True) -> Image.Image:
    """Left-aligned block; one common font size so the widest line fits `max_w`."""
    layer, d = new_layer(size), None
    d = ImageDraw.Draw(layer)
    widest = max(lines, key=len)
    font = fit_font(widest, max_w, start, bold)
    step = int(getattr(font, "size", start) * gap)
    for i, line in enumerate(lines):
        d.text((x, y + i * step), line, font=font, fill=fill, anchor="la")
    return layer


def centered_text(size: Size, text: str, y: int, start: int, fill, bold: bool = True,
                  margin: float = 0.08) -> Image.Image:
    layer = new_layer(size)
    font = fit_font(text, int(size[0] * (1 - 2 * margin)), start, bold)
    ImageDraw.Draw(layer).text((size[0] // 2, y), text, font=font, fill=fill, anchor="mt")
    return layer


def star_points(cx, cy, r_out, r_in, n=5, rot=-np.pi / 2):
    pts = []
    for i in range(n * 2):
        r = r_out if i % 2 == 0 else r_in
        ang = rot + i * np.pi / n
        pts.append((cx + r * np.cos(ang), cy + r * np.sin(ang)))
    return pts


def brush_strokes(size: Size, seed: int, colours: List[RGB], y_frac=0.5, amp=120,
                  cycles=1.5, soft=1.5) -> Image.Image:
    """Dabs of varying size along a wavy path + star stamps = 'custom brush' stand-in."""
    rng = np.random.default_rng(seed)
    w, h = size
    layer = new_layer(size)
    d = ImageDraw.Draw(layer)
    for i, t in enumerate(np.linspace(0, 1, 90)):
        x = 60 + t * (w - 120)
        y = h * y_frac + amp * np.sin(t * 2 * np.pi * cycles) + rng.normal(0, 10)
        r = rng.uniform(6, 26)
        col = colours[i % len(colours)] + (225,)
        d.ellipse((x - r, y - r, x + r, y + r), fill=col)
        if i % 6 == 0:
            d.polygon(star_points(x, y + rng.uniform(-70, 70), r * 1.8, r * 0.7),
                      fill=colours[(i + 1) % len(colours)] + (235,))
    return layer.filter(ImageFilter.GaussianBlur(soft))


def circuit_art(size: Size, seed: int) -> Image.Image:
    """Abstract 'circuit board' picture used as a poster hero image."""
    rng = np.random.default_rng(seed)
    w, h = size
    img = Image.new("RGB", size, (8, 12, 34))
    d = ImageDraw.Draw(img)
    for _ in range(46):
        x, y = int(rng.integers(0, w)), int(rng.integers(0, h))
        for _ in range(int(rng.integers(2, 5))):
            if rng.random() < 0.5:
                nx, ny = x + int(rng.integers(-160, 160)), y
            else:
                nx, ny = x, y + int(rng.integers(-160, 160))
            d.line((x, y, nx, ny), fill=(0, 190, 255), width=3)
            x, y = nx, ny
        d.ellipse((x - 7, y - 7, x + 7, y + 7), outline=(255, 190, 0), width=3)
    return img


def credit_layer(size: Size) -> Image.Image:
    """Footer bar with the student's name / roll number / course (own PSD layer)."""
    w, h = size
    text = (f"{STUDENT['name']}  |  Roll No: {STUDENT['roll']}  |  "
            f"{STUDENT['course']}  |  {STUDENT['semester']}")
    font = fit_font(text, int(w * 0.92), max(14, h // 40))
    bar = int(getattr(font, "size", 16) * 2.2)
    layer = new_layer(size)
    d = ImageDraw.Draw(layer)
    d.rectangle((0, h - bar, w, h), fill=(0, 0, 0, 150))
    d.text((w // 2, h - bar // 2), text, font=font, fill=(255, 255, 255, 255), anchor="mm")
    return layer


def placeholder_layer(size: Size) -> Image.Image:
    """Red banner so a placeholder can never be mistaken for finished work."""
    w, h = size
    bar = max(30, h // 28)
    layer = new_layer(size)
    d = ImageDraw.Draw(layer)
    d.rectangle((0, 0, w, bar), fill=(190, 25, 25, 235))
    font = fit_font(PLACEHOLDER_TAG, int(w * 0.94), int(bar * 0.62))
    d.text((w // 2, bar // 2), PLACEHOLDER_TAG, font=font, fill=(255, 255, 255, 255), anchor="mm")
    return layer


# --------------------------------------------------------------------------- #
# 5. LAYER MODEL, COMPOSITING AND THE MINIMAL PSD WRITER
# --------------------------------------------------------------------------- #
@dataclass
class Layer:
    name: str
    image: Image.Image            # full-canvas RGBA, straight (non-premultiplied) alpha
    blend: str = "norm"           # PSD blend key: norm | mul  | scrn | over
    opacity: int = 255            # 0-255
    visible: bool = True


BLEND_KEYS = {"norm", "mul ", "scrn", "over"}


def flatten(size: Size, layers: List[Layer]) -> np.ndarray:
    """Composite bottom -> top (supports normal/multiply/screen/overlay); returns uint8 RGB."""
    w, h = size
    assert layers[0].image.getchannel("A").getextrema() == (255, 255), \
        "bottom layer must be fully opaque"
    base = np.zeros((h, w, 3), np.float32)
    for lyr in layers:
        if not lyr.visible:
            continue
        src = np.asarray(lyr.image, np.float32) / 255.0
        rgb, a = src[..., :3], src[..., 3:4] * (lyr.opacity / 255.0)
        if lyr.blend == "mul ":
            res = base * rgb
        elif lyr.blend == "scrn":
            res = 1 - (1 - base) * (1 - rgb)
        elif lyr.blend == "over":
            res = np.where(base <= 0.5, 2 * base * rgb, 1 - 2 * (1 - base) * (1 - rgb))
        else:
            res = rgb
        base = base * (1 - a) + res * a
    return np.clip(base * 255 + 0.5, 0, 255).astype(np.uint8)


def _pascal(name: str, pad: int = 4) -> bytes:
    raw = name.encode("ascii", "replace")[:31]
    data = bytes([len(raw)]) + raw
    return data + b"\x00" * ((-len(data)) % pad)


def _unicode_name_block(name: str) -> bytes:
    """'luni' block: full-length Unicode layer name (the Pascal name is capped at 31 chars)."""
    payload = struct.pack(">I", len(name)) + name.encode("utf-16-be")
    payload += b"\x00" * ((-len(payload)) % 4)
    return b"8BIM" + b"luni" + struct.pack(">I", len(payload)) + payload


def write_psd(path: Path, size: Size, layers: List[Layer]) -> None:
    """
    Write an 8-bit RGB Photoshop (.psd) file with named pixel layers.
    Layout: header | colour-mode data | image resources | layer & mask info |
            flattened image data (raw, planar).  Layers are stored bottom -> top.
    """
    w, h = size
    records, pixel_data = bytearray(), bytearray()
    for lyr in layers:
        rgba = lyr.image
        bbox = rgba.getchannel("A").getbbox() or (0, 0, 1, 1)      # crop to content
        left, top, right, bottom = bbox
        arr = np.asarray(rgba.crop(bbox), np.uint8)
        channels = [(0, arr[..., 0]), (1, arr[..., 1]), (2, arr[..., 2]), (-1, arr[..., 3])]

        rec = struct.pack(">iiiiH", top, left, bottom, right, len(channels))
        for cid, plane in channels:
            blob = struct.pack(">H", 0) + plane.tobytes()           # 0 = raw compression
            rec += struct.pack(">hI", cid, len(blob))
            pixel_data += blob
        assert lyr.blend in BLEND_KEYS
        assert len(lyr.name) <= 31, f"layer name too long for classic PSD readers: {lyr.name}"
        flags = 8 if lyr.visible else 10                            # bit1 = hidden
        extra = (struct.pack(">I", 0) + struct.pack(">I", 0) + _pascal(lyr.name)
                 + _unicode_name_block(lyr.name))
        rec += b"8BIM" + lyr.blend.encode("ascii")
        rec += struct.pack(">BBBB", lyr.opacity, 0, flags, 0)
        rec += struct.pack(">I", len(extra)) + extra
        records += rec

    layer_info = struct.pack(">h", len(layers)) + bytes(records) + bytes(pixel_data)
    layer_info += b"\x00" * ((-len(layer_info)) % 4)
    layer_mask_section = struct.pack(">I", len(layer_info)) + layer_info + struct.pack(">I", 0)

    # Image resource 1005: ResolutionInfo (72 dpi)
    res_data = struct.pack(">IHHIHH", 72 << 16, 1, 1, 72 << 16, 1, 1)
    resources = b"8BIM" + struct.pack(">H", 1005) + b"\x00\x00" + struct.pack(">I", len(res_data)) + res_data

    composite = flatten(size, layers)
    planar = b"".join(composite[..., c].tobytes() for c in range(3))

    with open(path, "wb") as fh:
        fh.write(b"8BPS" + struct.pack(">H6xHIIHH", 1, 3, h, w, 8, 3))   # header: RGB, 8-bit
        fh.write(struct.pack(">I", 0))                                     # colour mode data
        fh.write(struct.pack(">I", len(resources)) + resources)           # image resources
        fh.write(struct.pack(">I", len(layer_mask_section)) + layer_mask_section)
        fh.write(struct.pack(">H", 0) + planar)                            # merged image


# --------------------------------------------------------------------------- #
# 6. PLACEHOLDER ARTWORK FOR EACH PRACTICAL
#    Each builder returns (canvas_size, layers bottom->top, {extra_file: image})
# --------------------------------------------------------------------------- #
Built = Tuple[Size, List[Layer], Dict[str, Image.Image]]


def build_p1() -> Built:
    size = (1200, 800)                               # strictly 1200 x 800
    amber, teal = (255, 176, 0), (0, 196, 170)       # two different colours
    rect, ell, tri = new_layer(size), new_layer(size), new_layer(size)
    ImageDraw.Draw(rect).rectangle((90, 200, 430, 460), fill=amber + (255,))
    ImageDraw.Draw(ell).ellipse((470, 170, 790, 490), fill=teal + (255,))
    ImageDraw.Draw(tri).polygon([(830, 470), (1110, 470), (970, 200)], fill=amber + (255,))
    details = [f"Name: {STUDENT['name']}", f"Roll No: {STUDENT['roll']}",
               f"Course: {STUDENT['course']}"]
    layers = [
        Layer("Background - Solid Colour", solid(size, (22, 34, 56))),
        Layer("Shape - Rectangle", rect),
        Layer("Shape - Ellipse", ell),
        Layer("Shape - Triangle", tri),
        Layer("Text - Title", centered_text(size, "PRACTICAL 01 - PHOTOSHOP BASICS", 60, 54,
                                            (255, 255, 255, 255))),
        Layer("Text - Name Roll No Course",
              text_block(size, details, 90, 540, 46, (255, 255, 255, 255), 1000)),
        Layer("PLACEHOLDER banner", placeholder_layer(size)),
    ]
    return size, layers, {}


def build_p2() -> Built:
    size = (1500, 1000)
    clean = synthetic_photo(size, seed=2)
    # BEFORE: dull, slightly tilted, three dust spots.
    before = ImageEnhance.Brightness(ImageEnhance.Color(
        ImageEnhance.Contrast(clean).enhance(0.7)).enhance(0.6)).enhance(0.92)
    d = ImageDraw.Draw(before)
    for (sx, sy, r) in [(380, 330, 15), (1010, 480, 12), (700, 700, 18)]:
        d.ellipse((sx - r, sy - r, sx + r, sy + r), fill=(40, 34, 30))
    before = before.rotate(-3, resample=Image.Resampling.BICUBIC, fillcolor=(30, 30, 30))
    # AFTER: straightened, spots healed, contrast/colour corrected.
    after = ImageEnhance.Brightness(ImageEnhance.Color(
        ImageEnhance.Contrast(clean).enhance(1.15)).enhance(1.2)).enhance(1.05)

    # Side-by-side comparison image
    pw, ph, gap, head = 800, 533, 30, 70
    sheet = Image.new("RGB", (pw * 2 + gap * 3, ph + head + gap), (24, 24, 28))
    sd = ImageDraw.Draw(sheet)
    for i, (label, im) in enumerate((("BEFORE", before), ("AFTER", after))):
        x = gap + i * (pw + gap)
        sheet.paste(im.resize((pw, ph), Image.Resampling.LANCZOS), (x, head))
        sd.text((x + pw // 2, head // 2), label, font=get_font(40), fill=(255, 255, 255),
                anchor="mm")
    foot = f"{STUDENT['name']}  |  Roll No: {STUDENT['roll']}  |  {PLACEHOLDER_TAG}"
    sd.text((sheet.width // 2, sheet.height - 14), foot, font=fit_font(foot, 1400, 20),
            fill=(255, 120, 120), anchor="mm")

    layers = [
        Layer("Original Photo (Before)", before.convert("RGBA")),
        Layer("Retouched Photo (After)", after.convert("RGBA")),
        Layer("Text - Name and Roll No", credit_layer(size)),
        Layer("PLACEHOLDER banner", placeholder_layer(size)),
    ]
    return size, layers, {"Before_After_Practical_02.jpg": sheet}


def build_p3() -> Built:
    size = (1400, 900)
    specs = [   # name, box(x,y,w,h), seed, sky, hills, feather kwargs
        ("Photo 1 - Mountains", (50, 220, 700, 430), 31,
         ((60, 110, 190), (240, 215, 180)), ((90, 100, 120), (60, 80, 90), (35, 55, 60)),
         dict(right=100)),
        ("Photo 2 - Beach", (650, 220, 700, 430), 32,
         ((40, 140, 210), (250, 230, 190)), ((230, 200, 140), (40, 150, 170), (20, 100, 130)),
         dict(left=100)),
        ("Photo 3 - Old Town", (350, 600, 700, 240), 33,
         ((220, 130, 90), (250, 200, 140)), ((140, 80, 60), (100, 55, 45), (60, 35, 35)),
         dict(top=70)),
    ]
    layers = [Layer("Background - Gradient", vertical_gradient(size, (14, 40, 90), (240, 140, 70)))]
    for i, (name, (x, y, w, h), seed, sky, hills, feather) in enumerate(specs, 1):
        layers.append(Layer(f"Shadow - Photo {i}", shadow_layer(size, (x, y, x + w, y + h))))
        photo = feathered(synthetic_photo((w, h), seed, sky, hills), **feather)
        layers.append(Layer(name, place(size, photo, (x, y))))
    layers += [
        Layer("Text - Title", centered_text(size, "DISCOVER THE WORLD", 50, 96, (255, 255, 255, 255))),
        Layer("Text - Supporting", centered_text(size, "Mountains  |  Beaches  |  Heritage Towns",
                                                 148, 40, (255, 225, 170, 255))),
        Layer("Text - Name and Roll No", credit_layer(size)),
        Layer("PLACEHOLDER banner", placeholder_layer(size)),
    ]
    return size, layers, {}


def build_p4() -> Built:
    size = (1600, 860)
    pw, ph = 760, 690
    photo = synthetic_photo((pw, ph), seed=4)
    # Subject: hot-air balloon (clearly identifiable) + exact mask for it
    cx, cy, rx, ry = pw // 2, int(ph * 0.40), 150, 200
    subj = photo.copy()
    sd, mask = ImageDraw.Draw(subj), Image.new("L", (pw, ph), 0)
    md = ImageDraw.Draw(mask)
    for dr in (sd, md):
        fill = (225, 85, 40) if dr is sd else 255
        dr.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=fill)
        dr.rectangle((cx - 28, cy + ry + 55, cx + 28, cy + ry + 100),
                     fill=(120, 80, 40) if dr is sd else 255)
        for dx in (-22, 22):
            dr.line((cx + dx * 4, cy + ry - 30, cx + dx, cy + ry + 55),
                    fill=(60, 40, 30) if dr is sd else 255, width=4)
    sd.ellipse((cx - 70, cy - ry + 10, cx + 70, cy + ry - 10), fill=(250, 200, 50))
    sd.ellipse((cx - 22, cy - ry + 10, cx + 22, cy + ry - 10), fill=(225, 85, 40))
    photo.paste(subj, (0, 0), mask)

    # EDITED version: recoloured background + boosted subject through the mask
    bg_edit = ImageChops.multiply(ImageEnhance.Color(photo).enhance(0.25),
                                  Image.new("RGB", (pw, ph), (190, 210, 255)))
    subj_edit = ImageEnhance.Brightness(ImageEnhance.Color(photo).enhance(1.45)).enhance(1.08)
    subj_rgba = subj_edit.convert("RGBA")
    subj_rgba.putalpha(mask.filter(ImageFilter.GaussianBlur(1.2)))        # 'refined' edge

    left_xy, right_xy = (20, 100), (820, 100)
    labels = new_layer(size)
    ld = ImageDraw.Draw(labels)
    ld.text((left_xy[0] + pw // 2, 66), "ORIGINAL", font=get_font(40), fill=(255, 255, 255, 255), anchor="mm")
    ld.text((right_xy[0] + pw // 2, 66), "EDITED", font=get_font(40), fill=(255, 255, 255, 255), anchor="mm")
    layers = [
        Layer("Background - Solid Colour", solid(size, (28, 28, 34))),
        Layer("Original Photo", place(size, photo, left_xy)),
        Layer("Edited - Background Recolour", place(size, bg_edit, right_xy)),
        Layer("Edited - Subject Boost", place(size, subj_rgba, right_xy)),
        Layer("Text - Panel Labels", labels),
        Layer("Text - Name and Roll No", credit_layer(size)),
        Layer("PLACEHOLDER banner", placeholder_layer(size)),
    ]
    return size, layers, {}


def build_p5() -> Built:
    size = (1200, 800)                               # strictly 1200 x 800
    rng = np.random.default_rng(5)
    noise = np.clip(rng.normal(128, 45, (size[1], size[0])), 0, 255).astype(np.uint8)
    noise_img = Image.fromarray(noise).convert("RGBA")
    strokes = brush_strokes(size, 55, [(255, 64, 160), (64, 220, 255), (255, 210, 70)])
    glow = strokes.filter(ImageFilter.GaussianBlur(16))
    title = centered_text(size, "PIXEL STORM", 235, 150, (255, 255, 255, 255))
    sub = centered_text(size, "Filters  |  Brushes  |  Blending Modes", 420, 44, (255, 225, 170, 255))
    layers = [
        Layer("Background - Solid Colour", solid(size, (70, 46, 130))),
        Layer("Colour Wash (Multiply)", horizontal_gradient(size, (150, 90, 230), (60, 190, 200)),
              blend="mul ", opacity=230),
        Layer("Texture Noise (Overlay)", noise_img, blend="over", opacity=150),
        Layer("Brush Strokes", strokes),
        Layer("Brush Glow (Screen)", glow, blend="scrn", opacity=200),
        Layer("Text - Title", title),
        Layer("Text - Subtitle", sub),
        Layer("Text - Name and Roll No", credit_layer(size)),
        Layer("PLACEHOLDER banner", placeholder_layer(size)),
    ]
    return size, layers, {}


def build_p6() -> Built:
    size = (1000, 1414)
    hero_d = 560
    hero = circuit_art((hero_d, hero_d), seed=6).convert("RGBA")
    circ = Image.new("L", (hero_d, hero_d), 0)
    ImageDraw.Draw(circ).ellipse((6, 6, hero_d - 6, hero_d - 6), fill=255)
    hero.putalpha(circ.filter(ImageFilter.GaussianBlur(4)))
    ring = new_layer(size)
    ImageDraw.Draw(ring).ellipse((210, 190, 790, 770), outline=(0, 200, 255, 255), width=14)
    panel = new_layer(size)
    ImageDraw.Draw(panel).rounded_rectangle((80, 1105, 920, 1290), radius=26, fill=(0, 0, 0, 130))
    details = ["Date: 21-22 November 2026", "Time: 9:00 AM onwards",
               "Venue: Main Auditorium, COER University",
               "Organizer: Department of Computer Applications"]
    layers = [
        Layer("BG - Gradient", vertical_gradient(size, (14, 10, 40), (80, 22, 120))),
        Layer("FX - Brush Splatter", brush_strokes(size, 66, [(255, 64, 160), (64, 220, 255)],
                                                   y_frac=0.28, amp=200, cycles=1.0, soft=2.5)),
        Layer("IMG - Hero Circuit Circle", place(size, hero, (220, 200))),
        Layer("FX - Hero Ring Glow (Screen)", ring.filter(ImageFilter.GaussianBlur(10)),
              blend="scrn", opacity=220),
        Layer("Text - Event Title", centered_text(size, "COER HACKATHON", 800, 96, (255, 255, 255, 255))),
        Layer("Text - Year", centered_text(size, "2026", 905, 120, (255, 196, 0, 255))),
        Layer("Text - Tagline", centered_text(size, "24 HOURS  |  CODE  |  CREATE  |  COMPETE",
                                              1042, 36, (160, 235, 255, 255))),
        Layer("Shape - Details Panel", panel),
        Layer("Text - Event Details",
              text_block(size, details, 120, 1125, 30, (255, 255, 255, 255), 760, gap=1.4, bold=False)),
        Layer("Text - Name and Roll No", credit_layer(size)),
        Layer("PLACEHOLDER banner", placeholder_layer(size)),
    ]
    return size, layers, {}


BUILDERS: Dict[int, Callable[[], Built]] = {
    1: build_p1, 2: build_p2, 3: build_p3, 4: build_p4, 5: build_p5, 6: build_p6}


# --------------------------------------------------------------------------- #
# 7. ORCHESTRATION AND VERIFICATION
# --------------------------------------------------------------------------- #
def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8", newline="\n")


def build_repository(out_dir: Path) -> Path:
    root = out_dir / ROOT_NAME
    os.makedirs(root, exist_ok=True)
    write_text(root / "README.md", root_readme())
    print(f"[root] {root}")

    for p in PRACTICALS:
        folder = root / p.folder
        os.makedirs(folder, exist_ok=True)
        size, layers, extras = BUILDERS[p.number]()

        composite = Image.fromarray(flatten(size, layers))
        if p.ext == "png":
            composite.save(folder / p.out_name, "PNG", optimize=True, dpi=(72, 72))
        else:
            composite.save(folder / p.out_name, "JPEG", quality=92, dpi=(72, 72))
        for fname, img in extras.items():
            img.convert("RGB").save(folder / fname, "JPEG", quality=92)
        write_psd(folder / p.psd_name, size, layers)
        write_text(folder / "README.md", practical_readme(p))
        print(f"[{p.folder}] {len(layers):>2} layers, {size[0]}x{size[1]}  ->  "
              f"{p.psd_name}, {p.out_name}" + (f", {', '.join(extras)}" if extras else ""))
    return root


def verify_repository(root: Path) -> bool:
    """Check presence, naming, required sizes, and that every PSD re-opens."""
    try:
        from psd_tools import PSDImage                      # optional
    except ImportError:
        PSDImage = None
    ok = True
    print("\nVerification")
    print("-" * 78)
    for p in PRACTICALS:
        folder = root / p.folder
        for fname in p.expected_files:
            fp = folder / fname
            if not fp.is_file() or os.path.getsize(fp) == 0:
                print(f"  MISSING/EMPTY: {fp}")
                ok = False
        with Image.open(folder / p.out_name) as im:
            if p.number in (1, 5) and im.size != (1200, 800):
                print(f"  WRONG SIZE for Practical {p.tag}: {im.size}")
                ok = False
            out_size = im.size
        psd_path = folder / p.psd_name
        with open(psd_path, "rb") as fh:
            sig, ver, ch, h, w, depth, mode = struct.unpack(">4sH6xHIIHH", fh.read(26))
        if sig != b"8BPS" or (w, h) != out_size or depth != 8 or mode != 3:
            print(f"  BAD PSD HEADER: {psd_path}")
            ok = False
        with Image.open(psd_path) as pim:                   # Pillow's PSD reader
            n_layers = len(getattr(pim, "layers", []) or [])
        extra = ""
        if PSDImage is not None:
            psd = PSDImage.open(psd_path)
            extra = f", psd-tools sees {len(list(psd))} layers"
        print(f"  {p.folder}: PSD {os.path.getsize(psd_path)/1e6:5.1f} MB, "
              f"{n_layers} layers (Pillow){extra}; output {out_size[0]}x{out_size[1]} "
              f"{p.ext.upper()} {os.path.getsize(folder / p.out_name)/1e3:6.0f} KB")
    print("-" * 78)
    print("All checks passed." if ok else "Some checks FAILED - see messages above.")
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description="Scaffold the Adobe-Photoshop-Practicals repository.")
    ap.add_argument("--out", type=Path, default=Path.cwd(),
                    help="parent folder in which to create %s (default: current folder)" % ROOT_NAME)
    args = ap.parse_args()
    root = build_repository(args.out)
    ok = verify_repository(root)
    print("\nNEXT STEP: every image/PSD above is a watermarked placeholder. Do the real work in\n"
          "Photoshop and overwrite the files (same names) before you push to GitHub.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
