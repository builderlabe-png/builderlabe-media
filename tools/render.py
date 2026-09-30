"""Render builderlabe carousel slides (1080x1350) from simple slide specs."""
import json, sys, pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).parent.parent
FONTS = pathlib.Path("/home/claude/fonts/package/files")

CSS = f"""
@font-face {{ font-family: Inter; font-weight: 400; src: url('file://{FONTS}/inter-latin-400-normal.woff2'); }}
@font-face {{ font-family: Inter; font-weight: 500; src: url('file://{FONTS}/inter-latin-500-normal.woff2'); }}
@font-face {{ font-family: Inter; font-weight: 600; src: url('file://{FONTS}/inter-latin-600-normal.woff2'); }}
@font-face {{ font-family: Inter; font-weight: 700; src: url('file://{FONTS}/inter-latin-700-normal.woff2'); }}
@font-face {{ font-family: Inter; font-weight: 800; src: url('file://{FONTS}/inter-latin-800-normal.woff2'); }}
@font-face {{ font-family: Inter; font-weight: 900; src: url('file://{FONTS}/inter-latin-900-normal.woff2'); }}
:root {{ --cream:#F7F5F0; --ink:#0F1B3D; --blue:#316BE7; --muted:#6B7280; --line:#E4E0D6; }}
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ width:1080px; height:1350px; font-family:Inter, sans-serif; background:var(--cream); color:var(--ink); }}
.slide {{ position:relative; width:1080px; height:1350px; padding:110px 96px; display:flex; flex-direction:column; }}
.slide.dark {{ background:var(--ink); color:#fff; }}
.slide.blue {{ background:var(--blue); color:#fff; }}
.top {{ display:flex; justify-content:space-between; font-size:26px; font-weight:600; color:var(--muted); letter-spacing:.02em; }}
.dark .top, .blue .top {{ color:rgba(255,255,255,.6); }}
.body {{ flex:1; display:flex; flex-direction:column; justify-content:center; }}
.kicker {{ font-size:30px; font-weight:700; color:var(--blue); text-transform:uppercase; letter-spacing:.08em; margin-bottom:36px; }}
.dark .kicker {{ color:#8FB0FF; }} .blue .kicker {{ color:rgba(255,255,255,.75); }}
h1 {{ font-size:104px; font-weight:900; line-height:.98; letter-spacing:-.045em; }}
h2 {{ font-size:78px; font-weight:800; line-height:1.02; letter-spacing:-.04em; }}
h1 em, h2 em {{ font-style:normal; color:var(--blue); }}
.dark h1 em, .dark h2 em {{ color:#8FB0FF; }}
.blue h1 em, .blue h2 em {{ color:#FFFFFF; opacity:.6; }}
p.lead {{ font-size:38px; font-weight:500; line-height:1.4; margin-top:44px; color:#374151; letter-spacing:-.01em; }}
.dark p.lead, .blue p.lead {{ color:rgba(255,255,255,.85); }}
ul.pts {{ list-style:none; margin-top:52px; display:flex; flex-direction:column; gap:26px; }}
ul.pts li {{ font-size:36px; font-weight:600; line-height:1.3; padding:30px 34px; background:#fff; border:2px solid var(--line); border-radius:24px; display:flex; gap:22px; }}
ul.pts li b {{ color:var(--blue); font-weight:800; min-width:44px; }}
.dark ul.pts li {{ background:rgba(255,255,255,.07); border-color:rgba(255,255,255,.14); }}
.dark ul.pts li b {{ color:#8FB0FF; }}
.foot {{ display:flex; justify-content:space-between; align-items:center; font-size:26px; font-weight:600; color:var(--muted); }}
.dark .foot, .blue .foot {{ color:rgba(255,255,255,.6); }}
.swipe {{ font-weight:800; color:var(--blue); }}
.dark .swipe {{ color:#8FB0FF; }} .blue .swipe {{ color:#fff; }}
.big {{ font-size:230px; font-weight:900; letter-spacing:-.06em; line-height:.9; color:var(--blue); }}
.tweet {{ background:#fff; border-radius:36px; padding:64px 60px; box-shadow:0 30px 80px rgba(15,27,61,.12); border:1px solid var(--line); }}
.tw-head {{ display:flex; align-items:center; gap:24px; margin-bottom:40px; }}
.av {{ width:96px; height:96px; border-radius:50%; background:var(--ink); color:#fff; display:flex; align-items:center; justify-content:center; font-size:46px; font-weight:900; letter-spacing:-.05em; }}
.av span {{ color:var(--blue); }}
.nm {{ font-size:36px; font-weight:800; letter-spacing:-.02em; }}
.hd {{ font-size:30px; color:#6B7280; font-weight:500; }}
.tw-text {{ font-size:46px; font-weight:500; line-height:1.38; letter-spacing:-.015em; color:#0F1419; }}
.tw-text p + p {{ margin-top:34px; }}
.tw-meta {{ margin-top:44px; padding-top:30px; border-top:1px solid #EFF3F4; font-size:28px; color:#6B7280; display:flex; gap:40px; }}
.tw-meta b {{ color:#0F1419; }}
.cta {{ margin-top:60px; display:inline-flex; align-self:flex-start; background:var(--ink); color:#fff; font-size:34px; font-weight:800; padding:30px 48px; border-radius:999px; letter-spacing:-.01em; }}
.blue .cta {{ background:#fff; color:var(--blue); }}
.dark .cta {{ background:var(--blue); }}
.stack {{ display:flex; flex-direction:column; gap:22px; margin-top:44px; }}
"""

def tweet_html(t):
    paras = "".join(f"<p>{x}</p>" for x in t["text"])
    return f"""<div class="tweet"><div class="tw-head"><div class="av">b<span>.</span></div>
    <div><div class="nm">Abdo · builderlabe</div><div class="hd">@builderlabe</div></div></div>
    <div class="tw-text">{paras}</div>
    <div class="tw-meta"><span>{t.get('meta','9:41 AM · Oct 2026')}</span></div></div>"""

def slide_html(s, i, n):
    theme = s.get("theme", "")
    parts = []
    if s.get("kicker"): parts.append(f'<div class="kicker">{s["kicker"]}</div>')
    if s.get("big"): parts.append(f'<div class="big">{s["big"]}</div>')
    if s.get("h1"): parts.append(f'<h1>{s["h1"]}</h1>')
    if s.get("h2"): parts.append(f'<h2>{s["h2"]}</h2>')
    if s.get("lead"): parts.append(f'<p class="lead">{s["lead"]}</p>')
    if s.get("points"):
        lis = "".join(f"<li><b>{k}</b><span>{v}</span></li>" for k, v in s["points"])
        parts.append(f'<ul class="pts">{lis}</ul>')
    if s.get("tweets"):
        parts.append('<div class="stack">' + "".join(tweet_html(t) for t in s["tweets"]) + "</div>")
    if s.get("cta"): parts.append(f'<div class="cta">{s["cta"]}</div>')
    swipe = "Swipe →" if i < n and n > 1 else ""
    counter = f"{i}/{n}" if n > 1 else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
    <div class="slide {theme}"><div class="top"><span>@builderlabe</span><span>{counter}</span></div>
    <div class="body">{''.join(parts)}</div>
    <div class="foot"><span>{s.get('foot','')}</span><span class="swipe">{swipe}</span></div></div></body></html>"""

def render(spec_path):
    spec = json.loads(pathlib.Path(spec_path).read_text())
    out = ROOT / "out" / spec["id"]; out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width":1080, "height":1350})
        n = len(spec["slides"])
        for i, s in enumerate(spec["slides"], 1):
            pg.set_content(slide_html(s, i, n)); pg.wait_for_timeout(250)
            pg.screenshot(path=str(out / f"{i:02d}.png"), type="png")
        b.close()
    print(spec["id"], n, "slides ->", out)

if __name__ == "__main__":
    for a in sys.argv[1:]: render(a)
