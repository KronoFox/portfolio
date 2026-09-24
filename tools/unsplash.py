"""Find free Unsplash photos for pitch sites.

  python tools/unsplash.py sheet "<query>" out.jpg      -> numbered contact sheet of free results (+ ids printed)
  python tools/unsplash.py get <photo_id> <dest.jpg> [width]  -> download one photo (default 1800px wide)
"""
import io, json, subprocess, sys, urllib.parse
from PIL import Image, ImageDraw



def fetch(url):
    return subprocess.run(["curl", "-sfL", url], capture_output=True, check=True, timeout=60).stdout


def search(q, n=12):
    url = "https://unsplash.com/napi/search/photos?per_page=30&query=" + urllib.parse.quote(q)
    res = json.loads(fetch(url))["results"]
    free = [r for r in res if not r.get("premium") and not r.get("plus")]
    return free[:n]


def sheet(q, out):
    photos = search(q)
    tw, th = 300, 220
    img = Image.new("RGB", (tw * 4, th * ((len(photos) + 3) // 4)), "white")
    d = ImageDraw.Draw(img)
    for i, p in enumerate(photos):
        t = Image.open(io.BytesIO(fetch(p["urls"]["raw"] + "&w=300&h=220&fit=crop&q=60"))).convert("RGB")
        x, y = (i % 4) * tw, (i // 4) * th
        img.paste(t, (x, y))
        d.rectangle([x, y, x + 30, y + 24], fill="black")
        d.text((x + 8, y + 5), str(i), fill="white")
        print(i, p["id"], p["width"], "x", p["height"], "|", (p.get("alt_description") or "")[:80])
    img.save(out, quality=80)


def get(pid, dest, w=1800):
    info = json.loads(fetch("https://unsplash.com/napi/photos/" + pid))
    if info.get("premium") or info.get("plus"):
        sys.exit("premium photo, skip")
    open(dest, "wb").write(fetch(info["urls"]["raw"] + f"&w={w}&q=72&fm=jpg"))
    print(dest, "by", info["user"]["name"])


if __name__ == "__main__":
    if sys.argv[1] == "sheet":
        sheet(sys.argv[2], sys.argv[3])
    else:
        get(sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 1800)
