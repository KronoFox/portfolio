"""Generate a bilingual proposal-preview site from a JSON shop file.

Usage: python tools/make_pitch.py shops/<slug>.json
Writes pitches/<slug>/index.html
"""
import html
import json
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent


def both(ja, en, tag="span"):
    return f'<{tag} class="ja">{html.escape(ja)}</{tag}><{tag} class="en">{html.escape(en)}</{tag}>'


def both_br(ja, en):
    # Headings may contain "\n" for a line break.
    j = "<br>".join(html.escape(s) for s in ja.split("\n"))
    e = "<br>".join(html.escape(s) for s in en.split("\n"))
    return f'<span class="ja">{j}</span><span class="en">{e}</span>'


def render(d):
    items = "\n".join(
        f'<div class="card"><h3>{both(i["ja"], i["en"])}</h3><p>{both(i.get("dja", ""), i.get("den", ""))}</p></div>'
        for i in d["items"]
    )
    rows = [
        (("住所", "Address"), both(d["address_ja"], d["address_en"])),
        (("営業時間", "Hours"), both(d["hours_ja"], d["hours_en"])),
    ]
    if d.get("phone"):
        rows.append((("電話", "Phone"), f'<a href="tel:{d["phone"].replace("-", "")}">{d["phone"]}</a>'))
    if d.get("instagram"):
        ig = d["instagram"]
        rows.append((("Instagram", "Instagram"), f'<a href="https://www.instagram.com/{ig}/" target="_blank" rel="noopener">@{ig}</a>'))
    if d.get("x"):
        rows.append((("X（Twitter）", "X (Twitter)"), f'<a href="https://x.com/{d["x"]}" target="_blank" rel="noopener">@{d["x"]}</a>'))
    dl = "\n".join(f"<dt>{both(k[0], k[1])}</dt><dd>{v}</dd>" for k, v in rows)
    rating = ""
    if d.get("rating"):
        rating = (f'<div class="rating">★ <b>{d["rating"]}</b> · '
                  f'{both("Googleクチコミ " + d["reviews_ja"], d["reviews_en"] + " Google reviews")}</div><br>')
    c = d["colors"]
    map_q = quote(d["map_query"])
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{html.escape(d["name"])} | {html.escape(d["area_ja"])}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;600&family=Noto+Sans+JP:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: {c["bg"]}; --surface: #ffffff; --ink: #24211c; --muted: #6b645a;
    --accent: {c["accent"]}; --accent-soft: {c["soft"]}; --line: #ddd8cc; --banner: #fff4c2; --banner-ink: #5a4a00;
  }}
  @media (prefers-color-scheme: dark) {{
    :root:not([data-theme="light"]) {{
      --bg: #181816; --surface: #23221f; --ink: #efece6; --muted: #aba699;
      --accent: {c["accent_dark"]}; --accent-soft: #2b2a26; --line: #38362f; --banner: #3d3510; --banner-ink: #f3e3a0;
    }}
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html {{ scroll-behavior: smooth; }}
  body {{ background: var(--bg); color: var(--ink); font-family: "Noto Sans JP", system-ui, sans-serif; line-height: 1.8; }}
  a {{ color: inherit; }}
  .wrap {{ max-width: 1040px; margin: 0 auto; padding: 0 20px; }}
  .proposal {{ background: var(--banner); color: var(--banner-ink); font-size: .8rem; text-align: center; padding: 6px 16px; }}
  header {{ position: sticky; top: 0; z-index: 10; background: color-mix(in srgb, var(--bg) 88%, transparent); backdrop-filter: blur(8px); border-bottom: 1px solid var(--line); }}
  .nav {{ display: flex; align-items: center; justify-content: space-between; height: 60px; gap: 12px; }}
  .logo {{ font-family: "Noto Serif JP", serif; font-weight: 600; font-size: 1.1rem; text-decoration: none; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
  .nav ul {{ display: flex; gap: 22px; list-style: none; font-size: .9rem; }}
  .nav ul a {{ text-decoration: none; color: var(--muted); }}
  .nav ul a:hover {{ color: var(--accent); }}
  .lang {{ border: 1px solid var(--line); background: var(--surface); color: var(--ink); border-radius: 999px; padding: 4px 12px; font: inherit; font-size: .8rem; cursor: pointer; flex: none; }}
  .hero {{ padding: 96px 0 80px; text-align: center; }}
  .hero .eyebrow {{ color: var(--accent); letter-spacing: .2em; font-size: .8rem; }}
  .hero h1 {{ font-family: "Noto Serif JP", serif; font-size: clamp(2rem, 6vw, 3.2rem); font-weight: 600; margin: 12px 0 16px; line-height: 1.35; }}
  .hero p {{ color: var(--muted); max-width: 560px; margin: 0 auto 32px; }}
  .rating {{ display: inline-block; margin-bottom: 28px; font-size: .9rem; color: var(--muted); }}
  .rating b {{ color: var(--ink); }}
  .btn {{ display: inline-block; background: var(--accent); color: var(--bg); padding: 12px 28px; border-radius: 999px; text-decoration: none; font-weight: 500; }}
  .btn.ghost {{ background: transparent; color: var(--accent); border: 1px solid var(--accent); margin-left: 8px; }}
  section {{ padding: 72px 0; }}
  section h2 {{ font-family: "Noto Serif JP", serif; font-size: 1.7rem; font-weight: 600; margin-bottom: 8px; }}
  section .sub {{ color: var(--muted); margin-bottom: 36px; }}
  .alt {{ background: var(--accent-soft); }}
  .about {{ max-width: 720px; }}
  .menu {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; }}
  .card {{ background: var(--surface); border: 1px solid var(--line); border-radius: 14px; padding: 22px; }}
  .card h3 {{ font-size: 1rem; font-weight: 500; }}
  .card p {{ color: var(--muted); font-size: .88rem; margin-top: 6px; }}
  .note {{ color: var(--muted); font-size: .8rem; margin-top: 20px; }}
  .info {{ display: grid; grid-template-columns: 1fr 1fr; gap: 32px; }}
  .info dl {{ display: grid; grid-template-columns: 110px 1fr; gap: 10px 16px; }}
  .info dt {{ color: var(--muted); font-size: .9rem; }}
  .map {{ border-radius: 14px; border: 1px solid var(--line); overflow: hidden; min-height: 280px; }}
  .map iframe {{ width: 100%; height: 100%; min-height: 280px; border: 0; display: block; }}
  footer {{ border-top: 1px solid var(--line); padding: 28px 0; color: var(--muted); font-size: .8rem; text-align: center; }}
  [data-lang="en"] .ja, [data-lang="ja"] .en {{ display: none; }}
  @media (max-width: 720px) {{
    .nav ul {{ display: none; }}
    .info {{ grid-template-columns: 1fr; }}
    .hero {{ padding: 64px 0 56px; }}
    .btn.ghost {{ margin: 12px 0 0; }}
  }}
</style>
</head>
<body data-lang="ja">
<div class="proposal">{both("※ こちらはご提案用のサンプルページです（非公開・検索エンジン非表示）", "Proposal preview: not an official site, hidden from search engines")}</div>
<header>
  <div class="wrap nav">
    <a class="logo" href="#">{html.escape(d["name"])}</a>
    <ul>
      <li><a href="#about">{both("お店について", "About")}</a></li>
      <li><a href="#menu">{both(d["menu_ja"], d["menu_en"])}</a></li>
      <li><a href="#info">{both("アクセス", "Visit")}</a></li>
    </ul>
    <button class="lang" id="langBtn" aria-label="Switch language">EN</button>
  </div>
</header>
<main>
  <div class="hero wrap">
    <div class="eyebrow">{html.escape(d["eyebrow"])}</div>
    <h1>{both_br(d["h1_ja"], d["h1_en"])}</h1>
    <p>{both(d["lead_ja"], d["lead_en"])}</p>
    {rating}
    <a class="btn" href="#menu">{both(d["menu_ja"] + "を見る", "See the " + d["menu_en"].lower())}</a>
    <a class="btn ghost" href="#info">{both("アクセス", "How to find us")}</a>
  </div>
  <section id="about" class="alt">
    <div class="wrap about">
      <h2>{both("お店について", "About")}</h2>
      <p class="sub">{both(d["about_sub_ja"], d["about_sub_en"])}</p>
      <p>{both(d["about_ja"], d["about_en"])}</p>
    </div>
  </section>
  <section id="menu">
    <div class="wrap">
      <h2>{both(d["menu_ja"], d["menu_en"])}</h2>
      <p class="sub">{both("人気のメニュー", "Customer favorites")}</p>
      <div class="menu">
{items}
      </div>
      <p class="note">{both("※ 価格・内容は正式公開時にお店の情報に合わせて掲載します。", "Prices and items will be confirmed with the shop before launch.")}</p>
    </div>
  </section>
  <section id="info" class="alt">
    <div class="wrap">
      <h2>{both("営業時間・アクセス", "Hours & access")}</h2>
      <p class="sub">{both(d["info_sub_ja"], d["info_sub_en"])}</p>
      <div class="info">
        <dl>
{dl}
        </dl>
        <div class="map"><iframe loading="lazy" title="Map" src="https://www.google.com/maps?q={map_q}&output=embed"></iframe></div>
      </div>
    </div>
  </section>
</main>
<footer>© {html.escape(d["name"])}</footer>
<script>
  const btn = document.getElementById('langBtn');
  btn.addEventListener('click', () => {{
    const l = document.body.dataset.lang === 'ja' ? 'en' : 'ja';
    document.body.dataset.lang = l;
    document.documentElement.lang = l;
    btn.textContent = l === 'ja' ? 'EN' : '日本語';
  }});
</script>
</body>
</html>
"""


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        data = json.loads(Path(arg).read_text(encoding="utf-8"))
        out = ROOT / "pitches" / data["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render(data), encoding="utf-8")
        print(f"wrote {out.relative_to(ROOT)}")
