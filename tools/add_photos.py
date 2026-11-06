#!/usr/bin/env python3
"""Add Abbey Trip photos to the gallery.

Usage:
  python3 tools/add_photos.py YEAR SRC_DIR [SRC_DIR ...]

SRC_DIR holds the original photos downloaded from Drive, each saved as
<drive_file_id>__<original name>. Photos already added (tracked by Drive file id
in img/gallery/YEAR/sources.json) are skipped, so re-running is safe.
Then the year buttons and photo list in gallery/index.html are rebuilt from
whatever is in img/gallery/.
"""
import json, os, re, sys
from PIL import Image, ImageOps
try:
    from pillow_heif import register_heif_opener; register_heif_opener()
except ImportError:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAL = os.path.join(ROOT, "img", "gallery")
PAGE = os.path.join(ROOT, "gallery", "index.html")
EXT = (".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp")

def add(year, srcs):
    d = os.path.join(GAL, year); os.makedirs(d, exist_ok=True)
    sp = os.path.join(d, "sources.json")
    seen = json.load(open(sp)) if os.path.exists(sp) else {}
    nums = [int(f[:-5]) for f in os.listdir(d) if re.fullmatch(r"\d+\.webp", f)]
    n = max(nums, default=0)
    added = []
    for src in srcs:
        for f in sorted(os.listdir(src)):
            if not f.lower().endswith(EXT): continue
            fid = f.split("__", 1)[0]
            if fid in seen: continue
            try:
                im = ImageOps.exif_transpose(Image.open(os.path.join(src, f))).convert("RGB")
            except Exception as e:
                print("skip (unreadable):", f, e); continue
            n += 1
            big = im.copy(); big.thumbnail((1400, 1400)); big.save(f"{d}/{n}.webp", "WEBP", quality=66, method=6)
            th = im.copy(); th.thumbnail((520, 520)); th.save(f"{d}/{n}_t.webp", "WEBP", quality=60, method=6)
            seen[fid] = n; added.append(f)
    json.dump(seen, open(sp, "w"), indent=1)
    return added

def rebuild():
    man = {}
    for y in sorted(os.listdir(GAL)):
        d = os.path.join(GAL, y)
        if not (os.path.isdir(d) and y.isdigit()): continue
        items = []
        for f in os.listdir(d):
            m = re.fullmatch(r"(\d+)_t\.webp", f)
            if m:
                w, h = Image.open(os.path.join(d, f)).size
                items.append([int(m.group(1)), w, h])
        if items: man[y] = sorted(items)
    html = open(PAGE).read()
    html = re.sub(r"const GAL=\{.*?\};", "const GAL=" + json.dumps(man) + ";", html, count=1, flags=re.S)
    years = sorted(man, reverse=True)
    btns = "".join(f'<button data-y="{y}" aria-selected="{str(i==0).lower()}">{y}</button>' for i, y in enumerate(years))
    html = re.sub(r'(<div class="ytabs" id="ytabs">).*?(</div>)', lambda m: m.group(1) + btns + m.group(2), html, count=1, flags=re.S)
    words = {5: "Five", 6: "Six", 7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten"}
    html = re.sub(r"\w+ years of Abbey Trips", f"{words.get(len(years), len(years))} years of Abbey Trips", html, count=1)
    open(PAGE, "w").write(html)
    return {y: len(v) for y, v in man.items()}

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        added = add(sys.argv[1], sys.argv[2:])
        print(f"added {len(added)} new photo(s) to {sys.argv[1]}")
    print("gallery now:", rebuild())
