"""Generate a bilingual proposal-preview site from a JSON shop file.

Usage: python tools/make_pitch.py shops/<slug>.json [...]
Writes pitches/<slug>/index.html

Each shop picks a "theme" (layout + fonts + decoration) and an "art" (line
illustration); "colors" sets the palette: bg, ink, accent, soft, pop.
"""
import html
import json
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
esc = html.escape


def both(ja, en, tag="span"):
    return f'<{tag} class="ja">{esc(ja)}</{tag}><{tag} class="en">{esc(en)}</{tag}>'


def both_br(ja, en):
    # Keep each Japanese line whole; on phones it shrinks to fit (see --n in BASE_CSS).
    lines = ja.split("\n")
    j = "<br>".join(f'<span class="l">{esc(s)}</span>' for s in lines)
    e = "<br>".join(esc(s) for s in en.split("\n"))
    n = max(len(s) for s in lines)
    return f'<span class="ja" style="--n:{n}">{j}</span><span class="en">{e}</span>'


# ---------------------------------------------------------------- line art
ART = {
    "cup": '<ellipse cx="100" cy="150" rx="62" ry="12"/><path d="M58 92h84v22a42 42 0 0 1-84 0z"/><path d="M142 100h8a14 14 0 0 1 0 28h-12"/><path d="M84 78c-8-10 8-16 0-28M102 78c-8-10 8-16 0-28M120 78c-8-10 8-16 0-28"/>',
    "leaf": '<path d="M100 170C40 140 40 60 100 30c60 30 60 110 0 140z"/><path d="M100 170V40M100 80l-22-16M100 110l24-18M100 138l-20-14"/>',
    "bike": '<circle cx="52" cy="132" r="34"/><circle cx="148" cy="132" r="34"/><path d="M52 132l30-52h50l16 52M82 80l28 52h38M110 132l22-52M76 68h18M126 66l12-6"/><circle cx="110" cy="132" r="5"/>',
    "espresso": '<path d="M62 96h76l-8 58H70z"/><path d="M138 108h10a12 12 0 0 1 0 24h-14"/><ellipse cx="100" cy="164" rx="52" ry="8"/><path d="M60 40h80v26H60zM100 66v18"/>',
    "plate": '<circle cx="100" cy="104" r="64"/><circle cx="100" cy="104" r="44"/><path d="M100 104c0-8 12-8 12 0s-20 14-22 0 26-24 34-4-18 38-40 20"/><path d="M26 50v40M20 50v18a6 6 0 0 0 12 0V50M174 50c-10 10-10 30 0 40v70"/>',
    "bread": '<path d="M30 130c0-44 32-70 70-70s70 26 70 70v12H30z"/><path d="M70 82l-10 26M100 74v30M130 82l10 26"/><path d="M20 152h160"/>',
    "flower": '<circle cx="100" cy="96" r="12"/><ellipse cx="100" cy="56" rx="18" ry="28"/><ellipse cx="100" cy="136" rx="18" ry="28"/><ellipse cx="60" cy="96" rx="28" ry="18"/><ellipse cx="140" cy="96" rx="28" ry="18"/><path d="M100 164v26"/>',
    "record": '<circle cx="100" cy="100" r="76"/><circle cx="100" cy="100" r="58"/><circle cx="100" cy="100" r="42"/><circle cx="100" cy="100" r="18"/><circle cx="100" cy="100" r="3"/>',
    "wave": '<path d="M10 90c30-24 60-24 90 0s60 24 90 0M10 120c30-24 60-24 90 0s60 24 90 0M10 150c30-24 60-24 90 0s60 24 90 0"/><circle cx="150" cy="46" r="18"/>',
    "moto": '<circle cx="48" cy="140" r="26"/><circle cx="154" cy="140" r="26"/><path d="M48 140l34-40h44l28 40M82 100l-8-16h-18M126 100l14-26h18M92 100v18h40"/><path d="M100 84h26"/>',
    "toast": '<path d="M52 170V96c-18-4-22-36 0-46 14-8 34-8 48-6 14-2 34-2 48 6 22 10 18 42 0 46v74z"/><rect x="78" y="108" width="44" height="30" rx="4"/>',
    "cake": '<path d="M44 120h112v50H44z"/><path d="M44 144h112"/><path d="M44 120c10-12 22-12 28 0 6-12 22-12 28 0 6-12 22-12 28 0 6-12 22-12 28 0"/><path d="M100 104V84"/><path d="M100 84c-6-6-2-14 0-18 2 4 6 12 0 18z"/>',
    "bamboo": '<path d="M70 190V20M110 190V40M150 190V60"/><path d="M63 70h14M63 130h14M103 90h14M103 150h14M143 110h14M143 160h14"/><path d="M70 60c14-12 30-12 42-6M110 80c14-12 34-10 44-2M70 110c-14-10-30-10-42-2M150 100c-12-10-26-10-36-4"/>',
    "dog": '<circle cx="100" cy="104" r="46"/><path d="M62 80c-16-4-26 18-18 40M138 80c16-4 26 18 18 40"/><circle cx="84" cy="98" r="4"/><circle cx="116" cy="98" r="4"/><path d="M92 116h16l-8 8z"/><path d="M100 124v8c-4 6-12 6-16 2M100 132c4 6 12 6 16 2"/>',
    "bowl": '<path d="M30 100h140c0 40-30 66-70 66s-70-26-70-66z"/><path d="M70 172h60"/><path d="M118 36l40 54M140 30l32 58"/><path d="M76 88c-6-10 6-16 0-26M100 88c-6-10 6-16 0-26"/>',
    "wine": '<path d="M70 28h60c0 52-10 72-30 72s-30-20-30-72z"/><path d="M100 100v62M72 168h56"/><path d="M72 62h56"/>',
    "roll": '<circle cx="100" cy="104" r="62"/><path d="M100 104c0-8 12-8 12 0 0 16-28 16-28 0 0-24 44-24 44 0 0 32-60 32-60 0 0-40 76-40 76 0"/>',
    "banana": '<path d="M40 70c10 70 70 100 130 70-40 10-90-10-110-70z"/><path d="M40 70c-4-10 0-20 8-22l6 14"/><path d="M60 96c20 30 50 44 86 40"/>',
    "river": '<path d="M60 118l40-34 40 34"/><path d="M68 112v38h64v-38"/><path d="M94 150v-20h12v20"/><circle cx="158" cy="98" r="18"/><path d="M158 116v34"/><path d="M40 150h130"/><path d="M28 168c16-7 32-7 48 0s32 7 48 0 32-7 48 0M48 184c16-7 32-7 48 0s32 7 48 0"/>',
}


def art(name, cls="art"):
    return (f'<svg class="{cls}" viewBox="0 0 200 200" fill="none" stroke="currentColor" '
            f'stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ART[name]}</svg>')


# ---------------------------------------------------------------- themes
FONTS = {
    "editorial": "Shippori+Mincho+B1:wght@500;700;800&family=Zen+Kaku+Gothic+New:wght@400;500",
    "poster": "Dela+Gothic+One&family=Zen+Kaku+Gothic+New:wght@400;700",
    "tropical": "M+PLUS+Rounded+1c:wght@400;500;800",
    "noir": "Cormorant+Garamond:ital,wght@0,500;1,500;1,600&family=Shippori+Mincho:wght@400;600",
    "showa": "RocknRoll+One&family=Zen+Kaku+Gothic+New:wght@400;500;700",
    "breeze": "Kaisei+Opti:wght@500;700&family=Zen+Maru+Gothic:wght@400;500",
}

BASE_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body { background: var(--bg); color: var(--ink); line-height: 1.85; -webkit-font-smoothing: antialiased; }
a { color: inherit; }
img, svg { display: block; }
.wrap { max-width: 1080px; margin: 0 auto; padding: 0 20px; }
.proposal { background: #fff4c2; color: #5a4a00; font: 500 .78rem/1.5 system-ui, sans-serif; text-align: center; padding: 7px 16px; }
header { position: sticky; top: 0; z-index: 20; background: color-mix(in srgb, var(--bg) 90%, transparent); backdrop-filter: blur(10px); }
.nav { display: flex; align-items: center; justify-content: space-between; height: 64px; gap: 12px; }
.logo { text-decoration: none; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.nav ul { display: flex; gap: 26px; list-style: none; font-size: .88rem; }
.nav ul a { text-decoration: none; opacity: .7; }
.nav ul a:hover { opacity: 1; color: var(--accent); }
.lang { border: 1.5px solid currentColor; background: transparent; color: var(--ink); border-radius: 999px; padding: 3px 13px; font: inherit; font-size: .78rem; cursor: pointer; flex: none; }
.btn { display: inline-block; text-decoration: none; font-weight: 500; padding: 13px 30px; border-radius: 999px; background: var(--accent); color: var(--bg); transition: transform .15s; }
.btn:hover { transform: translateY(-2px); }
.btn.ghost { background: transparent; color: var(--accent); box-shadow: inset 0 0 0 1.5px var(--accent); }
.btns { display: flex; gap: 12px; flex-wrap: wrap; }
section { padding: 88px 0; }
.note { opacity: .65; font-size: .8rem; margin-top: 28px; }
.info { display: grid; grid-template-columns: 1fr 1fr; gap: 40px; align-items: start; }
.info dl { display: grid; grid-template-columns: 104px 1fr; gap: 12px 18px; }
.info dt { opacity: .6; font-size: .88rem; }
.map { overflow: hidden; min-height: 300px; }
.map iframe { width: 100%; min-height: 300px; height: 100%; border: 0; }
footer { padding: 32px 0; font-size: .8rem; text-align: center; opacity: .7; }
[data-lang="en"] .ja, [data-lang="ja"] .en { display: none !important; }
.l { white-space: nowrap; }
@media (max-width: 760px) {
  h1 .ja { font-size: min(1em, calc((100vw - 44px) / (var(--n) * 1.16))) !important; }
  .nav ul { display: none; }
  .info { grid-template-columns: 1fr; }
  section { padding: 64px 0; }
}
"""


def menu_items(d):
    return d["items"]


# ---- editorial: vertical Japanese headline, numbered menu, hairlines
def editorial(d):
    css = """
body { font-family: "Zen Kaku Gothic New", sans-serif; }
.logo, h1, h2, .num, .quote { font-family: "Shippori Mincho B1", serif; }
.logo { font-weight: 700; font-size: 1.15rem; letter-spacing: .06em; }
header { border-bottom: 1px solid color-mix(in srgb, var(--ink) 14%, transparent); }
.hero { display: grid; grid-template-columns: auto 1fr; gap: 64px; align-items: center; padding: 72px 20px 96px; }
.hero h1 { font-weight: 800; font-size: clamp(2.2rem, 5vw, 3.6rem); line-height: 1.5; letter-spacing: .12em; }
.hero h1 .ja { writing-mode: vertical-rl; display: block; font-size: .85em; }
.hero h1 .en { line-height: 1.2; letter-spacing: 0; max-width: 9ch; display: block; }
.hero .side { border-left: 1px solid color-mix(in srgb, var(--ink) 18%, transparent); padding-left: 48px; }
.eyebrow { font-size: .75rem; letter-spacing: .32em; color: var(--accent); }
.hero .art-wrap { color: var(--accent); background: var(--soft); border-radius: 50%; width: min(280px, 70vw); aspect-ratio: 1; display: grid; place-items: center; margin: 22px 0 28px; }
.hero .art { width: 62%; }
.hero p { max-width: 460px; opacity: .8; margin-bottom: 28px; }
.rating { font-size: .85rem; opacity: .75; margin-bottom: 26px; }
.rating b { font-family: "Shippori Mincho B1", serif; font-size: 1.5rem; color: var(--accent); margin-right: 4px; }
.about { background: var(--soft); }
.quote { font-size: clamp(1.5rem, 3.6vw, 2.3rem); font-weight: 700; line-height: 1.6; max-width: 820px; margin-bottom: 26px; }
.quote::before { content: "— "; color: var(--accent); }
.about p { max-width: 640px; opacity: .85; }
h2 { font-size: 1.9rem; font-weight: 700; letter-spacing: .08em; margin-bottom: 36px; display: flex; align-items: baseline; gap: 18px; }
h2 small { font-family: "Zen Kaku Gothic New", sans-serif; font-size: .72rem; letter-spacing: .3em; color: var(--accent); }
.list { display: grid; grid-template-columns: 1fr 1fr; column-gap: 56px; }
.row { display: grid; grid-template-columns: 48px 1fr; padding: 22px 0; border-top: 1px solid color-mix(in srgb, var(--ink) 15%, transparent); }
.num { color: var(--accent); font-size: 1.1rem; }
.row h3 { font-weight: 500; font-size: 1.05rem; }
.row p { opacity: .65; font-size: .88rem; }
.visit { background: var(--soft); }
.map { border-radius: 4px; }
footer { border-top: 1px solid color-mix(in srgb, var(--ink) 14%, transparent); }
@media (max-width: 760px) {
  .hero { grid-template-columns: 1fr; gap: 24px; padding: 48px 20px 64px; }
  .hero h1 .ja { height: auto; writing-mode: horizontal-tb; }
  .hero .side { border: 0; padding: 0; }
  .list { grid-template-columns: 1fr; }
}
"""
    items = "".join(
        f'<div class="row"><span class="num">{i + 1:02d}</span><div><h3>{both(it["ja"], it["en"])}</h3>'
        f'<p>{both(it.get("dja", ""), it.get("den", ""))}</p></div></div>'
        for i, it in enumerate(menu_items(d)))
    body = f"""
<div class="wrap hero">
  <h1>{both_br(d["h1_ja"], d["h1_en"])}</h1>
  <div class="side">
    <div class="eyebrow">{esc(d["eyebrow"])}</div>
    <div class="art-wrap">{art(d["art"])}</div>
    <p>{both(d["lead_ja"], d["lead_en"])}</p>
    {rating_html(d)}
    <div class="btns"><a class="btn" href="#menu">{both(d["menu_ja"] + "を見る", "See the " + d["menu_en"].lower())}</a><a class="btn ghost" href="#info">{both("アクセス", "Visit")}</a></div>
  </div>
</div>
<section id="about" class="about"><div class="wrap">
  <p class="quote">{both(d["about_sub_ja"], d["about_sub_en"])}</p>
  <p>{both(d["about_ja"], d["about_en"])}</p>
</div></section>
<section id="menu"><div class="wrap">
  <h2>{both(d["menu_ja"], d["menu_en"])}<small>MENU</small></h2>
  <div class="list">{items}</div>
  {note()}
</div></section>
<section id="info" class="visit"><div class="wrap">
  <h2>{both("営業時間・アクセス", "Hours & access")}<small>ACCESS</small></h2>
  {info_html(d)}
</div></section>"""
    return css, body


# ---- poster: bold display type, stripes, rating badge, ticker, hard shadows
def poster(d):
    css = """
body { font-family: "Zen Kaku Gothic New", sans-serif; }
.logo, h1, h2, .badge, .ticker, .card h3 { font-family: "Dela Gothic One", sans-serif; font-weight: 400; }
.logo { font-size: 1.2rem; }
header { border-bottom: 3px solid var(--ink); }
.hero { position: relative; overflow: hidden; background: repeating-linear-gradient(-45deg, var(--soft) 0 18px, var(--bg) 18px 36px); border-bottom: 3px solid var(--ink); }
.hero .wrap { display: grid; grid-template-columns: 1.3fr 1fr; gap: 32px; align-items: center; padding-top: 72px; padding-bottom: 80px; }
.eyebrow { display: inline-block; background: var(--ink); color: var(--bg); font-weight: 700; font-size: .75rem; letter-spacing: .2em; padding: 4px 12px; margin-bottom: 20px; }
.hero h1 { font-size: clamp(2.1rem, 5.4vw, 4.2rem); line-height: 1.2; margin-bottom: 22px; text-wrap: balance; }
.hero h1 .ja { font-size: .82em; }
.hero h1 .en { text-transform: uppercase; letter-spacing: -.01em; }
.hero p { max-width: 480px; background: var(--bg); border: 3px solid var(--ink); padding: 16px 20px; margin-bottom: 28px; box-shadow: 6px 6px 0 var(--ink); }
.btn { border-radius: 0; border: 3px solid var(--ink); box-shadow: 5px 5px 0 var(--ink); color: var(--bg); }
.btn.ghost { background: var(--bg); color: var(--ink); box-shadow: 5px 5px 0 var(--ink); }
.visual { position: relative; justify-self: center; width: min(360px, 80vw); aspect-ratio: 1; background: var(--accent); border: 3px solid var(--ink); border-radius: 50%; display: grid; place-items: center; color: var(--bg); box-shadow: 8px 8px 0 var(--ink); }
.visual .art { width: 70%; }
.badge { position: absolute; top: -10px; right: -10px; width: 112px; height: 112px; border-radius: 50%; background: var(--pop); color: var(--ink); border: 3px solid var(--ink); display: grid; place-items: center; text-align: center; line-height: 1.1; font-size: 1.7rem; transform: rotate(12deg); }
.badge small { display: block; font-family: "Zen Kaku Gothic New", sans-serif; font-weight: 700; font-size: .62rem; letter-spacing: .08em; }
.ticker { background: var(--ink); color: var(--bg); overflow: hidden; white-space: nowrap; font-size: 1.05rem; padding: 12px 0; }
.ticker div { display: inline-block; animation: slide 28s linear infinite; }
.ticker span { margin: 0 22px; }
.ticker span::after { content: "✦"; margin-left: 44px; color: var(--pop); }
@keyframes slide { to { transform: translateX(-50%); } }
@media (prefers-reduced-motion: reduce) { .ticker div { animation: none; } }
h2 { font-size: clamp(1.8rem, 4vw, 2.6rem); margin-bottom: 36px; }
h2 .en { text-transform: uppercase; }
.about { background: var(--accent); color: var(--bg); border-bottom: 3px solid var(--ink); }
.about .wrap { display: grid; grid-template-columns: 1fr 1.4fr; gap: 48px; align-items: center; }
.about h2 { margin: 0; }
.about p.big { font-weight: 700; font-size: 1.15rem; margin-bottom: 12px; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 22px; }
.card { background: var(--bg); border: 3px solid var(--ink); padding: 22px; box-shadow: 6px 6px 0 var(--ink); transition: transform .15s, box-shadow .15s; }
.card:hover { transform: translate(-3px, -3px); box-shadow: 9px 9px 0 var(--accent); }
.card h3 { font-size: 1.15rem; margin-bottom: 6px; }
.card p { font-size: .88rem; opacity: .75; }
.card .tag { display: inline-block; font-size: .7rem; font-weight: 700; background: var(--pop); border: 2px solid var(--ink); padding: 0 8px; margin-bottom: 10px; }
.visit { background: var(--soft); border-top: 3px solid var(--ink); }
.map { border: 3px solid var(--ink); box-shadow: 6px 6px 0 var(--ink); }
footer { background: var(--ink); color: var(--bg); opacity: 1; }
@media (max-width: 760px) {
  .hero .wrap, .about .wrap { grid-template-columns: 1fr; }
  .badge { width: 92px; height: 92px; font-size: 1.4rem; }
}
"""
    names = "".join(f"<span>{both(it['ja'], it['en'])}</span>" for it in menu_items(d))
    items = "".join(
        f'<div class="card"><span class="tag">No.{i + 1}</span><h3>{both(it["ja"], it["en"])}</h3>'
        f'<p>{both(it.get("dja", ""), it.get("den", ""))}</p></div>'
        for i, it in enumerate(menu_items(d)))
    badge = (f'<div class="badge"><div>★{d["rating"]}<small>GOOGLE</small></div></div>' if d.get("rating") else "")
    body = f"""
<div class="hero"><div class="wrap">
  <div>
    <span class="eyebrow">{esc(d["eyebrow"])}</span>
    <h1>{both_br(d["h1_ja"], d["h1_en"])}</h1>
    <p>{both(d["lead_ja"], d["lead_en"])}</p>
    <div class="btns"><a class="btn" href="#menu">{both(d["menu_ja"] + "を見る", "See the " + d["menu_en"].lower())}</a><a class="btn ghost" href="#info">{both("アクセス", "Visit")}</a></div>
  </div>
  <div class="visual">{art(d["art"])}{badge}</div>
</div></div>
<div class="ticker" aria-hidden="true"><div>{names}{names}</div></div>
<section id="about" class="about"><div class="wrap">
  <h2>{both("お店について", "About us")}</h2>
  <div><p class="big">{both(d["about_sub_ja"], d["about_sub_en"])}</p><p>{both(d["about_ja"], d["about_en"])}</p></div>
</div></section>
<section id="menu"><div class="wrap">
  <h2>{both(d["menu_ja"], d["menu_en"])}</h2>
  <div class="grid">{items}</div>
  {note()}
</div></section>
<section id="info" class="visit"><div class="wrap">
  <h2>{both("営業時間・アクセス", "Hours & access")}</h2>
  {info_html(d)}
</div></section>"""
    return css, body


# ---- tropical: rounded type, blobs, wave dividers, pill cards
def tropical(d):
    css = """
body { font-family: "M PLUS Rounded 1c", sans-serif; }
.logo, h1, h2 { font-weight: 800; }
.logo { font-size: 1.2rem; color: var(--accent); }
.hero { position: relative; overflow: hidden; background: linear-gradient(170deg, var(--soft), var(--bg) 75%); text-align: center; padding: 88px 0 150px; }
.blob { position: absolute; border-radius: 42% 58% 60% 40% / 45% 40% 60% 55%; opacity: .5; filter: blur(2px); }
.blob.a { width: 340px; height: 340px; background: var(--pop); top: -80px; left: -90px; }
.blob.b { width: 260px; height: 260px; background: var(--accent); opacity: .22; bottom: 40px; right: -60px; border-radius: 60% 40% 45% 55% / 50% 60% 40% 50%; }
.hero .wrap { position: relative; }
.hero .art-wrap { width: 128px; height: 128px; margin: 0 auto 18px; border-radius: 50%; background: var(--bg); color: var(--accent); display: grid; place-items: center; box-shadow: 0 12px 30px color-mix(in srgb, var(--accent) 25%, transparent); }
.hero .art { width: 70%; }
.eyebrow { color: var(--accent); font-weight: 800; letter-spacing: .25em; font-size: .78rem; }
.hero h1 { font-size: clamp(2.2rem, 6vw, 3.8rem); line-height: 1.3; margin: 10px 0 18px; }
.hero p { max-width: 540px; margin: 0 auto 22px; opacity: .8; }
.rating { display: inline-block; background: var(--bg); border-radius: 999px; padding: 6px 18px; font-size: .88rem; margin-bottom: 26px; box-shadow: 0 4px 14px rgba(0,0,0,.06); }
.rating b { color: var(--accent); }
.btns { justify-content: center; }
.btn { box-shadow: 0 8px 20px color-mix(in srgb, var(--accent) 35%, transparent); }
.wave { position: absolute; left: 0; right: 0; bottom: -1px; width: 100%; height: 90px; color: var(--bg); }
h2 { font-size: clamp(1.7rem, 4vw, 2.3rem); text-align: center; margin-bottom: 12px; }
.sub { text-align: center; opacity: .65; margin-bottom: 40px; }
.about .wrap { max-width: 760px; text-align: center; }
.about .lead { font-weight: 800; font-size: 1.2rem; color: var(--accent); margin-bottom: 12px; }
.pills { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 18px; }
.pill { background: var(--bg); border-radius: 26px; padding: 22px 24px; display: flex; gap: 16px; align-items: center; box-shadow: 0 6px 24px rgba(0,0,0,.07); }
.dot { flex: none; width: 46px; height: 46px; border-radius: 50%; background: var(--soft); color: var(--accent); display: grid; place-items: center; font-weight: 800; }
.pill h3 { font-size: 1rem; font-weight: 800; }
.pill p { font-size: .85rem; opacity: .7; }
#menu { background: color-mix(in srgb, var(--soft) 55%, var(--bg)); border-radius: 48px 48px 0 0; }
.visit .map { border-radius: 28px; }
.visit dl { background: color-mix(in srgb, var(--soft) 55%, var(--bg)); border-radius: 28px; padding: 28px; }
"""
    items = "".join(
        f'<div class="pill"><span class="dot">{i + 1}</span><div><h3>{both(it["ja"], it["en"])}</h3>'
        f'<p>{both(it.get("dja", ""), it.get("den", ""))}</p></div></div>'
        for i, it in enumerate(menu_items(d)))
    wave = ('<svg class="wave" viewBox="0 0 1440 90" preserveAspectRatio="none" aria-hidden="true">'
            '<path fill="currentColor" d="M0 50c180-40 360-40 540 0s360 40 540 0 270-30 360-20v60H0z"/></svg>')
    body = f"""
<div class="hero"><span class="blob a"></span><span class="blob b"></span><div class="wrap">
  <div class="art-wrap">{art(d["art"])}</div>
  <div class="eyebrow">{esc(d["eyebrow"])}</div>
  <h1>{both_br(d["h1_ja"], d["h1_en"])}</h1>
  <p>{both(d["lead_ja"], d["lead_en"])}</p>
  {rating_html(d)}
  <div class="btns"><a class="btn" href="#menu">{both(d["menu_ja"] + "を見る", "See the " + d["menu_en"].lower())}</a><a class="btn ghost" href="#info">{both("アクセス", "Visit")}</a></div>
</div>{wave}</div>
<section id="about" class="about"><div class="wrap">
  <h2>{both("お店について", "About us")}</h2>
  <p class="lead">{both(d["about_sub_ja"], d["about_sub_en"])}</p>
  <p>{both(d["about_ja"], d["about_en"])}</p>
</div></section>
<section id="menu"><div class="wrap">
  <h2>{both(d["menu_ja"], d["menu_en"])}</h2>
  <p class="sub">{both("人気のメニュー", "Customer favorites")}</p>
  <div class="pills">{items}</div>
  {note()}
</div></section>
<section id="info" class="visit"><div class="wrap">
  <h2>{both("営業時間・アクセス", "Hours & access")}</h2>
  <p class="sub">{both(d["info_sub_ja"], d["info_sub_en"])}</p>
  {info_html(d)}
</div></section>"""
    return css, body


# ---- noir: dark, gold hairlines, italic serif, spinning record, wine-list menu
def noir(d):
    css = """
body { font-family: "Shippori Mincho", serif; }
.logo, h1 .en, h2 .en, .eyebrow, .script { font-family: "Cormorant Garamond", serif; }
.logo { font-style: italic; font-weight: 600; font-size: 1.45rem; color: var(--accent); }
header { border-bottom: 1px solid color-mix(in srgb, var(--accent) 35%, transparent); }
.hero { position: relative; text-align: center; padding: 80px 0 100px; }
.frame { position: absolute; inset: 24px; border: 1px solid color-mix(in srgb, var(--accent) 40%, transparent); pointer-events: none; }
.frame::after { content: ""; position: absolute; inset: 8px; border: 1px solid color-mix(in srgb, var(--accent) 20%, transparent); }
.hero .art { width: 170px; color: var(--accent); margin: 0 auto 30px; }
.hero .art.spin { animation: spin 14s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
@media (prefers-reduced-motion: reduce) { .hero .art.spin { animation: none; } }
.eyebrow { font-style: italic; color: var(--accent); letter-spacing: .3em; font-size: .95rem; }
.hero h1 { font-weight: 600; font-size: clamp(2rem, 5.4vw, 3.4rem); line-height: 1.5; margin: 14px 0 20px; }
.hero h1 .en { font-style: italic; font-weight: 500; line-height: 1.2; }
.hero p { max-width: 520px; margin: 0 auto 26px; opacity: .75; }
.rating { font-size: .88rem; opacity: .8; margin-bottom: 30px; }
.rating b { color: var(--accent); }
.btns { justify-content: center; }
.btn { border-radius: 0; background: var(--accent); color: var(--bg); letter-spacing: .1em; }
.btn.ghost { color: var(--accent); }
h2 { text-align: center; font-weight: 600; font-size: 1.9rem; margin-bottom: 8px; }
h2 .en { font-style: italic; font-weight: 500; font-size: 2.3rem; }
.orn { text-align: center; color: var(--accent); letter-spacing: .6em; margin-bottom: 44px; font-size: .8rem; }
.about { background: var(--soft); }
.about .wrap { max-width: 720px; text-align: center; }
.script { font-style: italic; font-size: 1.6rem; color: var(--accent); margin-bottom: 18px; line-height: 1.4; }
.about p { opacity: .82; }
.wine { max-width: 720px; margin: 0 auto; }
.wine .row { padding: 18px 0; }
.wine .top { display: flex; align-items: baseline; gap: 12px; }
.wine h3 { font-weight: 600; font-size: 1.1rem; white-space: nowrap; }
.wine .lead { flex: 1; border-bottom: 1px dotted color-mix(in srgb, var(--accent) 60%, transparent); transform: translateY(-5px); }
.wine .no { font-family: "Cormorant Garamond", serif; font-style: italic; color: var(--accent); }
.wine p { opacity: .6; font-size: .88rem; }
.note { text-align: center; }
.visit { background: var(--soft); }
.map { border: 1px solid color-mix(in srgb, var(--accent) 40%, transparent); padding: 8px; }
.map iframe { filter: grayscale(.6) contrast(1.05); }
footer { border-top: 1px solid color-mix(in srgb, var(--accent) 30%, transparent); }
@media (max-width: 760px) { .frame { inset: 10px; } .wine h3 { white-space: normal; } }
"""
    items = "".join(
        f'<div class="row"><div class="top"><h3>{both(it["ja"], it["en"])}</h3><span class="lead"></span>'
        f'<span class="no">No.{i + 1}</span></div><p>{both(it.get("dja", ""), it.get("den", ""))}</p></div>'
        for i, it in enumerate(menu_items(d)))
    body = f"""
<div class="hero"><span class="frame"></span><div class="wrap">
  {art(d["art"], "art spin" if d["art"] == "record" else "art")}
  <div class="eyebrow">{esc(d["eyebrow"])}</div>
  <h1>{both_br(d["h1_ja"], d["h1_en"])}</h1>
  <p>{both(d["lead_ja"], d["lead_en"])}</p>
  {rating_html(d)}
  <div class="btns"><a class="btn" href="#menu">{both(d["menu_ja"] + "を見る", "See the " + d["menu_en"].lower())}</a><a class="btn ghost" href="#info">{both("アクセス", "Visit")}</a></div>
</div></div>
<section id="about" class="about"><div class="wrap">
  <h2>{both("お店について", "About")}</h2><p class="orn">✦ ✦ ✦</p>
  <p class="script">{both(d["about_sub_ja"], d["about_sub_en"])}</p>
  <p>{both(d["about_ja"], d["about_en"])}</p>
</div></section>
<section id="menu"><div class="wrap">
  <h2>{both(d["menu_ja"], d["menu_en"])}</h2><p class="orn">✦ ✦ ✦</p>
  <div class="wine">{items}</div>
  {note()}
</div></section>
<section id="info" class="visit"><div class="wrap">
  <h2>{both("営業時間・アクセス", "Hours & Access")}</h2><p class="orn">✦ ✦ ✦</p>
  {info_html(d)}
</div></section>"""
    return css, body


# ---- breeze: airy sea-and-sand, animated layered waves, postcard menu
def breeze(d):
    css = """
body { font-family: "Zen Maru Gothic", sans-serif; }
.logo, h1, h2, .pc h3 { font-family: "Kaisei Opti", serif; font-weight: 700; }
.logo { font-size: 1.2rem; }
.hero { position: relative; overflow: hidden; background: linear-gradient(180deg, var(--soft) 0%, var(--bg) 100%); padding: 90px 0 190px; }
.hero .wrap { display: grid; grid-template-columns: 1.2fr 1fr; gap: 40px; align-items: center; position: relative; z-index: 2; }
.eyebrow { font-size: .78rem; letter-spacing: .3em; color: var(--accent); }
.hero h1 { font-size: clamp(2.1rem, 5.6vw, 3.6rem); line-height: 1.4; margin: 12px 0 18px; }
.hero p { max-width: 480px; opacity: .8; margin-bottom: 22px; }
.rating { font-size: .88rem; margin-bottom: 26px; opacity: .8; }
.rating b { color: var(--accent); font-size: 1.2rem; }
.sun { justify-self: center; width: min(300px, 70vw); aspect-ratio: 1; border-radius: 50%; background: radial-gradient(circle at 35% 35%, var(--bg), var(--pop)); display: grid; place-items: center; color: var(--accent); }
.sun .art { width: 62%; }
.seas { position: absolute; left: 0; right: 0; bottom: 0; height: 170px; }
.seas svg { position: absolute; bottom: 0; width: 200%; height: 100%; }
.seas .s1 { color: color-mix(in srgb, var(--accent) 25%, var(--bg)); animation: drift 18s linear infinite; }
.seas .s2 { color: color-mix(in srgb, var(--accent) 45%, var(--bg)); animation: drift 12s linear infinite reverse; height: 75%; }
.seas .s3 { color: var(--bg); height: 45%; animation: drift 22s linear infinite; }
@keyframes drift { to { transform: translateX(-50%); } }
@media (prefers-reduced-motion: reduce) { .seas svg { animation: none !important; } }
h2 { font-size: clamp(1.7rem, 4vw, 2.3rem); margin-bottom: 10px; }
.sub { opacity: .65; margin-bottom: 40px; }
.about .wrap { display: grid; grid-template-columns: 1fr 1.5fr; gap: 48px; }
.about .lead { font-family: "Kaisei Opti", serif; font-size: 1.3rem; color: var(--accent); line-height: 1.6; }
.pcs { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 26px; }
.pc { background: #fffdf8; color: #2a2a2a; padding: 24px; border: 1px solid rgba(0,0,0,.06); box-shadow: 0 10px 30px rgba(20,60,90,.09); position: relative; transform: rotate(var(--r)); transition: transform .2s; }
.pc:hover { transform: rotate(0) translateY(-4px); }
.pc::after { content: ""; position: absolute; top: 14px; right: 14px; width: 38px; height: 46px; border: 2px dashed var(--accent); border-radius: 3px; opacity: .6; }
.pc h3 { font-size: 1.05rem; margin-bottom: 6px; padding-right: 48px; }
.pc p { font-size: .86rem; opacity: .7; }
#menu { background: color-mix(in srgb, var(--soft) 50%, var(--bg)); }
.map { border-radius: 20px; }
@media (max-width: 760px) { .hero .wrap, .about .wrap { grid-template-columns: 1fr; } }
"""
    rots = ["-1.2deg", "0.8deg", "-0.4deg", "1.3deg", "-0.9deg", "0.5deg"]
    items = "".join(
        f'<div class="pc" style="--r:{rots[i % len(rots)]}"><h3>{both(it["ja"], it["en"])}</h3>'
        f'<p>{both(it.get("dja", ""), it.get("den", ""))}</p></div>'
        for i, it in enumerate(menu_items(d)))
    wave_path = "M0 60c120-40 240-40 360 0s240 40 360 0 240-40 360 0 240 40 360 0v100H0z"
    sea = "".join(f'<svg class="{c}" viewBox="0 0 1440 160" preserveAspectRatio="none" aria-hidden="true">'
                  f'<path fill="currentColor" d="{wave_path}"/></svg>' for c in ("s1", "s2", "s3"))
    body = f"""
<div class="hero"><div class="wrap">
  <div>
    <div class="eyebrow">{esc(d["eyebrow"])}</div>
    <h1>{both_br(d["h1_ja"], d["h1_en"])}</h1>
    <p>{both(d["lead_ja"], d["lead_en"])}</p>
    {rating_html(d)}
    <div class="btns"><a class="btn" href="#menu">{both(d["menu_ja"] + "を見る", "See the " + d["menu_en"].lower())}</a><a class="btn ghost" href="#info">{both("アクセス", "Visit")}</a></div>
  </div>
  <div class="sun">{art(d["art"])}</div>
</div><div class="seas">{sea}</div></div>
<section id="about" class="about"><div class="wrap">
  <div><h2>{both("お店について", "About us")}</h2><p class="lead">{both(d["about_sub_ja"], d["about_sub_en"])}</p></div>
  <p>{both(d["about_ja"], d["about_en"])}</p>
</div></section>
<section id="menu"><div class="wrap">
  <h2>{both(d["menu_ja"], d["menu_en"])}</h2>
  <p class="sub">{both("季節ごとのお楽しみも", "Seasonal treats, too")}</p>
  <div class="pcs">{items}</div>
  {note()}
</div></section>
<section id="info" class="visit"><div class="wrap">
  <h2>{both("営業時間・アクセス", "Hours & access")}</h2>
  <p class="sub">{both(d["info_sub_ja"], d["info_sub_en"])}</p>
  {info_html(d)}
</div></section>"""
    return css, body



# ---- showa: 70s kissaten stripes, rounded retro type, signboard menu
def showa(d):
    css = """
body { font-family: "Zen Kaku Gothic New", sans-serif; }
.logo, h1, h2, .board h3, .stamp { font-family: "RocknRoll One", sans-serif; }
.logo { font-size: 1.15rem; color: var(--accent); }
.stripes { height: 14px; background: linear-gradient(var(--pop) 0 33%, var(--accent) 33% 66%, var(--ink) 66%); }
.hero { position: relative; overflow: hidden; padding: 80px 0 90px; background: radial-gradient(circle at 80% 30%, var(--soft), transparent 60%); }
.hero .wrap { display: grid; grid-template-columns: 1.25fr 1fr; gap: 40px; align-items: center; }
.eyebrow { display: inline-block; border: 2px solid var(--accent); color: var(--accent); border-radius: 999px; padding: 2px 16px; font-size: .78rem; font-weight: 700; letter-spacing: .15em; margin-bottom: 18px; }
.hero h1 { font-size: clamp(2.1rem, 5.6vw, 3.8rem); line-height: 1.35; margin-bottom: 18px; color: var(--ink); }
.hero h1 .ja { font-size: .9em; }
.hero p { max-width: 470px; opacity: .85; margin-bottom: 22px; }
.rating { font-size: .88rem; margin-bottom: 24px; }
.rating b { color: var(--accent); }
.sun { position: relative; justify-self: center; width: min(320px, 75vw); aspect-ratio: 1; border-radius: 50%;
  background: repeating-conic-gradient(var(--pop) 0 10deg, var(--soft) 10deg 20deg); display: grid; place-items: center; }
.sun .disc { width: 66%; aspect-ratio: 1; border-radius: 50%; background: var(--bg); border: 4px solid var(--ink); display: grid; place-items: center; color: var(--accent); }
.sun .art { width: 66%; }
.stamp { position: absolute; bottom: 4%; left: -4%; background: var(--accent); color: var(--bg); border-radius: 12px; padding: 8px 14px; font-size: .95rem; transform: rotate(-8deg); box-shadow: 3px 3px 0 var(--ink); }
.btn { border-radius: 14px; box-shadow: 0 4px 0 var(--ink); }
.btn.ghost { box-shadow: inset 0 0 0 2px var(--accent), 0 4px 0 var(--ink); background: var(--bg); }
h2 { font-size: clamp(1.7rem, 4vw, 2.3rem); margin-bottom: 30px; text-align: center; }
h2::after { content: ""; display: block; width: 90px; height: 8px; margin: 12px auto 0; background: linear-gradient(90deg, var(--pop) 0 33%, var(--accent) 33% 66%, var(--ink) 66%); border-radius: 4px; }
.about { background: var(--soft); }
.about .wrap { max-width: 760px; text-align: center; }
.about .lead { font-weight: 700; font-size: 1.2rem; color: var(--accent); margin-bottom: 12px; }
.board { max-width: 760px; margin: 0 auto; background: var(--ink); color: var(--bg); border-radius: 22px; padding: 38px 40px; border: 6px solid var(--accent); box-shadow: 0 0 0 4px var(--ink), 0 18px 40px rgba(0,0,0,.18); }
.board .row { display: flex; gap: 16px; align-items: baseline; padding: 14px 0; border-bottom: 1px dashed color-mix(in srgb, var(--bg) 30%, transparent); }
.board .row:last-child { border: 0; }
.board h3 { font-size: 1.1rem; font-weight: 400; color: var(--pop); white-space: nowrap; }
.board p { font-size: .88rem; opacity: .8; }
.note { text-align: center; }
.visit { background: color-mix(in srgb, var(--soft) 60%, var(--bg)); }
.map { border-radius: 18px; border: 4px solid var(--ink); }
footer { background: var(--ink); color: var(--bg); opacity: 1; }
@media (max-width: 760px) { .hero .wrap { grid-template-columns: 1fr; } .board { padding: 26px 22px; } .board .row { flex-direction: column; gap: 2px; } .board h3 { white-space: normal; } }
"""
    items = "".join(
        f'<div class="row"><h3>{both(it["ja"], it["en"])}</h3><p>{both(it.get("dja", ""), it.get("den", ""))}</p></div>'
        for it in menu_items(d))
    stamp = f'<span class="stamp">★ {d["rating"]}</span>' if d.get("rating") else ""
    body = f"""
<div class="stripes"></div>
<div class="hero"><div class="wrap">
  <div>
    <span class="eyebrow">{esc(d["eyebrow"])}</span>
    <h1>{both_br(d["h1_ja"], d["h1_en"])}</h1>
    <p>{both(d["lead_ja"], d["lead_en"])}</p>
    {rating_html(d)}
    <div class="btns"><a class="btn" href="#menu">{both(d["menu_ja"] + "を見る", "See the " + d["menu_en"].lower())}</a><a class="btn ghost" href="#info">{both("アクセス", "Visit")}</a></div>
  </div>
  <div class="sun"><div class="disc">{art(d["art"])}</div>{stamp}</div>
</div></div>
<section id="about" class="about"><div class="wrap">
  <h2>{both("お店について", "About us")}</h2>
  <p class="lead">{both(d["about_sub_ja"], d["about_sub_en"])}</p>
  <p>{both(d["about_ja"], d["about_en"])}</p>
</div></section>
<section id="menu"><div class="wrap">
  <h2>{both(d["menu_ja"], d["menu_en"])}</h2>
  <div class="board">{items}</div>
  {note()}
</div></section>
<section id="info" class="visit"><div class="wrap">
  <h2>{both("営業時間・アクセス", "Hours & access")}</h2>
  {info_html(d)}
</div></section>"""
    return css, body


THEMES = {"showa": showa, "editorial": editorial, "poster": poster, "tropical": tropical, "noir": noir, "breeze": breeze}


# ---------------------------------------------------------------- shared bits
def rating_html(d):
    if not d.get("rating"):
        return ""
    return (f'<div class="rating"><b>★ {d["rating"]}</b> '
            f'{both("Googleクチコミ " + d["reviews_ja"], d["reviews_en"] + " Google reviews")}</div>')


def note():
    return f'<p class="note">{both("※ 価格・内容は正式公開時にお店の情報に合わせて掲載します。", "Prices and items will be confirmed with the shop before launch.")}</p>'


def info_html(d):
    rows = [(("住所", "Address"), both(d["address_ja"], d["address_en"])),
            (("営業時間", "Hours"), both(d["hours_ja"], d["hours_en"]))]
    if d.get("phone"):
        rows.append((("電話", "Phone"), f'<a href="tel:{d["phone"].replace("-", "")}">{d["phone"]}</a>'))
    for key, label, url in (("instagram", "Instagram", "https://www.instagram.com/{}/"),
                            ("x", "X", "https://x.com/{}"),
                            ("facebook", "Facebook", "https://www.facebook.com/{}")):
        if d.get(key):
            rows.append(((label, label), f'<a href="{url.format(d[key])}" target="_blank" rel="noopener">{"Facebookページ" if key == "facebook" else "@" + esc(d[key])}</a>'))
    if d.get("info_sub_ja"):
        rows.append((("ポイント", "Good to know"), both(d["info_sub_ja"], d["info_sub_en"])))
    dl = "".join(f"<dt>{both(*k)}</dt><dd>{v}</dd>" for k, v in rows)
    q = quote(d["map_query"])
    return (f'<div class="info"><dl>{dl}</dl><div class="map"><iframe loading="lazy" title="Map" '
            f'src="https://www.google.com/maps?q={q}&output=embed"></iframe></div></div>')


def render(d):
    c = d["colors"]
    css, body = THEMES[d["theme"]](d)
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{esc(d["name"])} | {esc(d["area_ja"])}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family={FONTS[d["theme"]]}&display=swap" rel="stylesheet">
<style>
:root {{ --bg: {c["bg"]}; --ink: {c["ink"]}; --accent: {c["accent"]}; --soft: {c["soft"]}; --pop: {c.get("pop", c["soft"])}; }}
{BASE_CSS}
{css}
</style>
</head>
<body data-lang="ja">
<div class="proposal">{both("※ こちらはご提案用のサンプルページです（非公開・検索エンジン非表示）", "Proposal preview: not an official site, hidden from search engines")}</div>
<header><div class="wrap nav">
  <a class="logo" href="#">{esc(d["name"])}</a>
  <ul>
    <li><a href="#about">{both("お店について", "About")}</a></li>
    <li><a href="#menu">{both(d["menu_ja"], d["menu_en"])}</a></li>
    <li><a href="#info">{both("アクセス", "Visit")}</a></li>
  </ul>
  <button class="lang" id="langBtn" aria-label="Switch language">EN</button>
</div></header>
<main>{body}</main>
<footer>© {esc(d["name"])}</footer>
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
        print(f"wrote {out.relative_to(ROOT)}  [{data['theme']}]")
