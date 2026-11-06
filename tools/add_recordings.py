#!/usr/bin/env python3
"""Add Abbey Trip recordings (audio/video/slides on Google Drive) to the Trip hub.

Usage:
  python3 tools/add_recordings.py YEAR FILES_JSON

FILES_JSON is a JSON file with a list of Drive files: [{"id": ..., "title": ..., "mimeType": ...}, ...]
(the "files" list from a Drive search is fine). Files already listed (by id) are skipped.
Titles are cleaned (file extension removed). Slides/PDFs show as a document viewer,
everything else as an audio player. Writes abbey-trip/recordings.json.
"""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "abbey-trip", "recordings.json")
OK = ("audio/", "video/", "application/pdf", "presentation", "application/vnd.google-apps.presentation")

def main(year, files_json):
    data = json.load(open(P)) if os.path.exists(P) else {}
    files = json.load(open(files_json))
    if isinstance(files, dict): files = files.get("files", [])
    have = {r["id"] for y in data.values() for r in y}
    lst = data.setdefault(year, [])
    added = 0
    for f in sorted(files, key=lambda f: f.get("title", "")):
        mt = f.get("mimeType", "")
        if f["id"] in have or not any(k in mt for k in OK): continue
        title = re.sub(r"\.(m4a|mp3|wav|aac|mp4|mov|pdf|pptx?|key)$", "", f["title"], flags=re.I).strip()
        typ = "slides" if ("pdf" in mt or "presentation" in mt) else "audio"
        lst.append({"id": f["id"], "title": title, "type": typ}); added += 1
    if not lst: data.pop(year)
    data = dict(sorted(data.items(), reverse=True))
    json.dump(data, open(P, "w"), indent=1, ensure_ascii=False)
    print(f"added {added} recording(s) to {year}; years now: {list(data)}")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
