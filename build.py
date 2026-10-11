#!/usr/bin/env python3
"""Build site/index.html from reasons.md and whatever is in site/photos/.

Edit reasons.md, drop photos into site/photos/, then run:  python3 build.py

Photos need no manifest and no naming scheme. Every image in the folder is
picked up automatically.
"""
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).parent
SITE = ROOT / "site"
EXTS = {".jpg", ".jpeg", ".png", ".webp", ".avif", ".gif"}
START = "2023-07-17"  # the Spain trip

# Password gate. She is asked on every visit; nothing is remembered.
# Matching ignores case, spaces, punctuation and a leading "the".
HINT = "Which restaurant in New York did we have our first date at?"
ANSWERS = ["Wayan", "Wayan NYC", "Wayan New York", "Wayan Nolita", "Wayan restaurant"]

# The song. Hosting the recording would be piracy; this sends
SONG_LABEL = "Hey There Delilah"
SONG_ID = "h_m-BjrxmgI"          # YouTube video id
SONG_BY = "Plain White T's"

# Map. Drawn as a diagram, no tiles and no API.
# (label, lat, lon, which side the label sits on)
HOMES = [
    ("Selma \u2014 Paris", 48.8566, 2.3522, "left"),
    ("Sufyan \u2014 Amman", 31.9454, 35.9284, "right"),
]
PLACES = [
    ("Marbella", 36.5101, -4.8824, "left"),
    ("New York", 40.7128, -74.0060, "left"),
    ("Miami", 25.7907, -80.1300, "below"),
    ("Los Angeles", 34.0736, -118.4004, "left"),
    ("Las Vegas", 36.1699, -115.1398, "right"),
    ("Dubai", 25.1972, 55.2744, "below"),
    ("Petra & Wadi Rum", 29.9000, 35.4300, "below"),
]

def _km(a, b):
    import math
    p = math.pi / 180
    h = (0.5 - math.cos((b[0] - a[0]) * p) / 2
         + math.cos(a[0] * p) * math.cos(b[0] * p) * (1 - math.cos((b[1] - a[1]) * p)) / 2)
    return 2 * 6371 * math.asin(math.sqrt(h))

APART = round(_km((HOMES[0][1], HOMES[0][2]), (HOMES[1][1], HOMES[1][2])))

reasons = [
    m.group(1)
    for m in (re.match(r"^\d+\.\s+(.*)$", l) for l in (ROOT / "reasons.md").read_text("utf-8").splitlines())
    if m
]
if not reasons:
    raise SystemExit("No numbered items found in reasons.md")

photos = sorted(
    p.name for p in (SITE / "photos").iterdir()
    if p.is_file() and p.suffix.lower() in EXTS and not p.name.startswith(".")
)

index_rows = "\n".join(
    f'      <li><a href="#{i}"><span class="n">{i}</span>'
    f'<span class="t">{html.escape(t)}</span></a></li>'
    for i, t in enumerate(reasons, 1)
)

hero_img = (
    f'<img id="hero" src="photos/{html.escape(photos[0])}" alt="Us">' if photos else ""
)


# --- Her dictionary. Counts are real, from three years of messages. ---
TALLY = {"together": 137446, "hers": 60375}
LEXICON = [
    ("bro",            861, "What you called me more than anything else."),
    ("\U0001F90D",      400, "Never a red one. Not once."),
    ("oki",            381, "Counting okii, okiii and the rest."),
    ("yess",           203, "More s's for bigger news."),
    ("don't worry",    196, "Said like a job you were taking on."),
    ("I love you",     181, "Out loud, in writing, where I could keep it."),
    ("no way",         152, "Pure unfiltered shock, every time."),
    ("khalas",         148, "End of discussion."),
    ("inchaallah",     134, "Hopefully. Eventually. We'll see."),
    ("ily",            128, "When you couldn't be bothered with the whole thing."),
    ("miss you",       110, "More often than I deserved."),
    ("hihi",           102, "When you were pleased with yourself."),
    ("exact",           87, "One word. Full agreement. Conversation closed."),
    ("wallah",          83, "I swear."),
    ("bisous",          72, "The temperature of the whole thing was in which one you picked."),
    ("good luck",       48, "Before every interview, every match, every time."),
    ("yallah",          46, "Let's go."),
    ("habibi",          39, "My love."),
    ("proud of you",    32, "About things that hadn't earned it yet."),
    ("sabah el nour",   10, "Good morning, the proper way."),
]

# --- Three years, short. Edit freely. ---
TIMELINE = [
    ("Jul 2023",            "Marbella",            "A ferry, and a lot of trouble. The good kind."),
    ("Oct 2024 \u2013 Sep 2025", "New York",            "The whole middle of it. Lunch breaks, the L train, walking everywhere."),
    ("Feb 2025",            "Paris",               "Your city. Your door, open."),
    ("May 2025",            "Miami",               "Sun, and you winking at the camera."),
    ("Jul 2025",            "Los Angeles & Las Vegas", "Beverly Hills, and whatever happened after."),
    ("Nov 2025",            "Amman",               "My people. You fit in like you had always been there."),
    ("Dec 2025",            "Dubai",               "New Year, the rooftop, all of us."),
    ("Aug 2026",            "Marbella",            "Where it started. The last time I saw you."),
]

# --- Open when... Replace every one of these with your own words. ---
LETTERS = [
    ("you miss me",
     "Then I'm missing you at the same time, which is most of the time. "
     "Go through the hundred. I meant all of them."),
    ("you can't sleep",
     "Put the song on. Read one reason, not all of them. "
     "You always fell asleep on the phone anyway."),
    ("you're annoyed with me",
     "You're probably right. You usually were, and I took too long to say so."),
    ("it's been a bad day",
     "Tell me about it properly, the long version, the way you do. "
     "I'll still be listening."),
    ("you forget how good you are",
     "Read number fifty again. You knew what you deserved before I did."),
]

# --- The dog. ---
THEO = ("Theo",
        "Born in M\u00e1laga, flown to Amman through Istanbul, and yours from "
        "the first photo. You still asked how he was months after everything.")

# What each part of her is for. (x, y on a 400x760 canvas, name, meaning)
PARTS = [
    (200,  60, "Your mind",      "the smartest person I have ever met"),
    (200, 112, "Your eyes",      "the first thing I noticed, every time"),
    (200, 154, "Your face",      "to kiss"),
    (200, 198, "Your voice",     "the one I fall asleep to"),
    (140, 238, "Your shoulders", "to lean on, when it is your turn"),
    (176, 292, "Your heart",     "soft, and better than mine"),
    (200, 334, "Your body",      "to cuddle"),
    (110, 332, "Your arms",      "to hug"),
    (96,  432, "Your hands",     "to hold"),
    (166, 548, "Your legs",      "to walk the world with"),
    (162, 668, "Your feet",      "that kept showing up at airports"),
]

# countries we were in together, drawn brighter than the rest
LIT = {"France", "Jordan", "Spain", "United States of America",
       "United Arab Emirates", "Morocco"}


def chart():
    """A real map: coastlines from Natural Earth, then our points on top.

    Latitude is stretched a little so the panel is a usable shape on a phone.
    """
    import json as _json
    world = _json.loads((ROOT / "data" / "world.geo.json").read_text("utf-8"))

    pts = HOMES + PLACES
    lons = [p[2] for p in pts]; lats = [p[1] for p in pts]
    x0, x1 = min(lons) - 22, max(lons) + 22
    y0, y1 = min(lats) - 7, max(lats) + 9
    W, H = 1000.0, 520.0

    def X(lon): return (lon - x0) / (x1 - x0) * W
    def Y(lat): return (y1 - lat) / (y1 - y0) * H
    def PX(lon): return (lon - x0) / (x1 - x0) * 100.0
    def PY(lat): return (y1 - lat) / (y1 - y0) * 100.0

    def rings(geom):
        if geom["type"] == "Polygon":
            return [geom["coordinates"][0]]
        if geom["type"] == "MultiPolygon":
            return [poly[0] for poly in geom["coordinates"]]
        return []

    land, lit = [], []
    for f in world["features"]:
        name = f["properties"]["name"]
        for ring in rings(f["geometry"]):
            if len(ring) < 4:
                continue
            if not any(x0 - 25 < c[0] < x1 + 25 and y0 - 25 < c[1] < y1 + 25 for c in ring):
                continue
            d, last = [], None
            for lon, lat in ring:
                x, y = X(lon), Y(lat)
                if last and abs(x - last[0]) < 1.1 and abs(y - last[1]) < 1.1:
                    continue          # thin out dense coastline
                d.append(f"{'M' if not last else 'L'}{x:.1f},{y:.1f}")
                last = (x, y)
            if len(d) > 3:
                (lit if name in LIT else land).append("".join(d) + "Z")

    svg = [f'<svg viewBox="0 0 {W:.0f} {H:.0f}" preserveAspectRatio="none" '
           f'aria-hidden="true" xmlns="http://www.w3.org/2000/svg">',
           '<defs>'
           '<linearGradient id="sea" x1="0" y1="0" x2="0" y2="1">'
           '<stop offset="0" stop-color="#0D1316"/><stop offset="1" stop-color="#0A0C0D"/>'
           '</linearGradient>'
           '<linearGradient id="soil" x1="0" y1="0" x2="0" y2="1">'
           '<stop offset="0" stop-color="#232019"/><stop offset="1" stop-color="#1A1814"/>'
           '</linearGradient>'
           '<linearGradient id="ours" x1="0" y1="0" x2="0" y2="1">'
           '<stop offset="0" stop-color="#3A352A"/><stop offset="1" stop-color="#2A261E"/>'
           '</linearGradient>'
           '<filter id="warm" x="-25%" y="-25%" width="150%" height="150%">'
           '<feGaussianBlur stdDeviation="7" result="b"/>'
           '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>'
           '</filter>'
           '</defs>',
           f'<rect width="{W:.0f}" height="{H:.0f}" fill="url(#sea)"/>']

    g = []
    lon = -180
    while lon <= 180:
        if x0 < lon < x1: g.append(f'<line x1="{X(lon):.1f}" y1="0" x2="{X(lon):.1f}" y2="{H:.0f}"/>')
        lon += 20
    lat = -80
    while lat <= 80:
        if y0 < lat < y1: g.append(f'<line x1="0" y1="{Y(lat):.1f}" x2="{W:.0f}" y2="{Y(lat):.1f}"/>')
        lat += 10
    svg.append('<g stroke="#15191B" stroke-width="1">' + "".join(g) + "</g>")

    svg.append(f'<g fill="url(#soil)" stroke="#342F27" stroke-width="1" '
               f'vector-effect="non-scaling-stroke"><path d="{" ".join(land)}"/></g>')
    svg.append(f'<g fill="url(#ours)" stroke="#8A7A52" stroke-width="1.3" '
               f'vector-effect="non-scaling-stroke"><path d="{" ".join(lit)}"/></g>')

    ax, ay = X(HOMES[0][2]), Y(HOMES[0][1])
    bx, by = X(HOMES[1][2]), Y(HOMES[1][1])
    mx, my = (ax + bx) / 2, (ay + by) / 2 - abs(bx - ax) * 0.45
    arc = f'M{ax:.1f},{ay:.1f} Q{mx:.1f},{my:.1f} {bx:.1f},{by:.1f}'
    svg.append(f'<path d="{arc}" fill="none" stroke="#C7A75F" stroke-width="7" '
               f'opacity=".16" filter="url(#warm)" vector-effect="non-scaling-stroke"/>')
    svg.append(f'<path class="flight" d="{arc}" fill="none" stroke="#C7A75F" '
               f'stroke-width="2.4" stroke-dasharray="3 11" stroke-linecap="round" '
               f'opacity=".95" vector-effect="non-scaling-stroke"/>')
    for p, colour, r in ([(q, "#7EA8B8", 6) for q in PLACES] +
                         [(q, "#C7A75F", 8) for q in HOMES]):
        cx, cy = X(p[2]), Y(p[1])
        svg.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r*2.6:.1f}" fill="{colour}" '
                   f'opacity=".10"/>')
        svg.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r*1.7:.1f}" fill="none" '
                   f'stroke="{colour}" stroke-width="1" opacity=".4" '
                   f'vector-effect="non-scaling-stroke"/>')
        svg.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{colour}" '
                   f'stroke="#0A0C0D" stroke-width="1.6"/>')
    svg.append("</svg>")

    tags = [f'<span class="pin {cls} {p[3]}" style="left:{PX(p[2]):.2f}%;top:{PY(p[1]):.2f}%">'
            f'{html.escape(p[0])}</span>'
            for p, cls in ([(q, "there") for q in PLACES] + [(q, "home") for q in HOMES])]
    tags.append(f'<span class="pin gap" style="left:{(PX(HOMES[0][2])+PX(HOMES[1][2]))/2:.2f}%;'
                f'top:{min(PY(HOMES[0][1]),PY(HOMES[1][1])) - 13:.2f}%">{APART:,} km</span>')
    return '<div class="plot">' + "".join(svg) + "".join(tags) + "</div>"


def figure():
    """A constellation of her: a star chart, each star tappable."""
    twins = {(290, 332): "Your arms", (304, 432): "Your hands",
             (234, 548): "Your legs", (238, 668): "Your feet",
             (260, 238): "Your shoulders"}
    bones = [
        ((200, 60), (200, 112)), ((200, 112), (200, 154)),
        ((200, 154), (200, 198)), ((200, 198), (140, 238)),
        ((200, 198), (260, 238)), ((140, 238), (110, 332)),
        ((260, 238), (290, 332)), ((110, 332), (96, 432)),
        ((290, 332), (304, 432)), ((140, 238), (176, 292)),
        ((176, 292), (200, 334)), ((260, 238), (200, 334)),
        ((200, 334), (200, 424)), ((200, 424), (166, 548)),
        ((200, 424), (234, 548)), ((166, 548), (162, 668)),
        ((234, 548), (238, 668)), ((140, 238), (260, 238)),
    ]
    stars = [(x, y) for x, y, _, _ in PARTS] + list(twins) + [(200, 424)]

    out = ['<svg viewBox="-30 10 460 790" class="figsvg" '
           'xmlns="http://www.w3.org/2000/svg" aria-label="Tap any point">',
           '<defs>'
           '<radialGradient id="halo" cx="50%" cy="46%" r="52%">'
           '<stop offset="0" stop-color="#C7A75F" stop-opacity=".12"/>'
           '<stop offset="1" stop-color="#C7A75F" stop-opacity="0"/>'
           '</radialGradient>'
           '<filter id="twinkle" x="-70%" y="-70%" width="240%" height="240%">'
           '<feGaussianBlur stdDeviation="5" result="b"/>'
           '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>'
           '</filter>'
           '</defs>',
           '<rect x="-30" y="10" width="460" height="790" fill="url(#halo)"/>']

    # faint scatter so it reads as sky, not a diagram
    import random as _r
    _r.seed(17)
    dust = "".join(
        f'<circle cx="{_r.uniform(-20, 420):.0f}" cy="{_r.uniform(20, 780):.0f}" '
        f'r="{_r.choice([0.8, 1, 1.3]):.1f}" fill="#C7A75F" opacity="{_r.uniform(.07, .2):.2f}"/>'
        for _ in range(80))
    out.append(dust)

    out.append('<g stroke="#6B5F42" stroke-width="1" stroke-linecap="round" opacity=".7">' +
               "".join(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}"/>'
                       for a, b in bones) + "</g>")

    # every joint gets a small star
    for x, y in stars:
        out.append(f'<g filter="url(#twinkle)"><circle cx="{x}" cy="{y}" r="2.6" '
                   f'fill="#F3EEE4" opacity=".85"/></g>')

    # the tappable ones get a ring
    for x, y in list(twins):
        out.append(f'<circle class="node" cx="{x}" cy="{y}" r="21" '
                   f'data-part="{html.escape(twins[(x, y)])}" tabindex="0" role="button"/>')
    for x, y, name, _ in PARTS:
        out.append(f'<circle class="node" cx="{x}" cy="{y}" r="21" '
                   f'data-part="{html.escape(name)}" tabindex="0" role="button"/>')
    out.append("</svg>")

    say = "".join(
        f'<button type="button" class="chip" data-part="{html.escape(n)}">{html.escape(n)}</button>'
        for _, _, n, _ in PARTS)
    data = json.dumps({n: w for _, _, n, w in PARTS}, ensure_ascii=False)
    return ('<div class="fig"><div class="figwrap">' + "".join(out) +
            '</div><div class="figsay"><p class="what" id="partName">Tap a star</p>'
            '<p class="why" id="partWhy">Every part of you is for something.</p>'
            '<div class="chips">' + say + '</div></div></div>'
            '<script type="application/json" id="partData">' + data + '</script>')


def lexicon():
    rows = "".join(
        f'<li><span class="w">{html.escape(w)}</span>'
        f'<span class="c">{n:,}</span>'
        f'<span class="g">{html.escape(g)}</span></li>'
        for w, n, g in LEXICON)
    return f'''<p class="tallyline">{TALLY["together"]:,} messages between us.
      {TALLY["hers"]:,} of them yours.</p><ul class="lex">{rows}</ul>'''


def timeline():
    return "".join(
        f'<li><span class="when">{html.escape(w)}</span>'
        f'<span class="dot"></span>'
        f'<span class="what"><b>{html.escape(t)}</b>{html.escape(d)}</span></li>'
        for w, t, d in TIMELINE)


def letters():
    return "".join(
        f'<details class="env"><summary><span class="seal">&#9829;</span>'
        f'Open when {html.escape(when)}</summary>'
        f'<p>{html.escape(body)}</p></details>'
        for when, body in LETTERS)


TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>One Hundred Reasons</title>
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#131110">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,opsz,wght@0,6..96,400..700;1,6..96,400&family=Hanken+Grotesk:wght@400;500;600&display=swap">
<style>
/* Single-theme by intention: a photo book read in the evening. Full-bleed
   photograph, then one reason at a time, then the whole index. */
:root{
  --bg:#131110; --raise:#1C1917; --ink:#F3EEE4; --dim:#9C9389; --faint:#6A635C;
  --brass:#C7A75F; --rule:#2B2724; --shadow:0 18px 50px rgba(0,0,0,.45);
  --display:'Bodoni Moda',Didot,'Playfair Display',Georgia,serif;
  --ui:'Hanken Grotesk','Helvetica Neue',Arial,sans-serif;
  color-scheme:dark;
}
*{box-sizing:border-box}
html,body{margin:0}
html{scroll-behavior:smooth}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
img{max-width:100%;display:block}
body{background:var(--bg);color:var(--ink);font-family:var(--ui);
  font-size:16px;line-height:1.6;-webkit-font-smoothing:antialiased;
  text-rendering:optimizeLegibility}
::selection{background:var(--brass);color:#131110}
:focus-visible{outline:2px solid var(--brass);outline-offset:3px}

/* ---- the photograph, uncovered ---- */
.plate{width:100%;background:var(--raise);cursor:pointer;position:relative;
  padding-top:env(safe-area-inset-top,0px)}
.plate img{width:100%;height:min(66svh,660px);object-fit:cover;display:block}
@media (max-width:620px){.plate img{height:min(54svh,460px)}}
.tally{position:absolute;left:0;right:0;bottom:0;margin:0;
  display:flex;justify-content:space-between;align-items:baseline;
  padding:0 20px 14px;font-size:11px;letter-spacing:.22em;text-transform:uppercase;
  color:rgba(243,238,228,.78);text-shadow:0 1px 10px rgba(0,0,0,.85);
  font-variant-numeric:tabular-nums;pointer-events:none}
.tally .tap{color:var(--brass);opacity:.9}

/* ---- titles ---- */
.title{max-width:980px;margin:0 auto;padding:clamp(34px,6vw,58px) 24px clamp(10px,2vw,16px)}
.kicker{font-size:11px;letter-spacing:.3em;text-transform:uppercase;color:var(--brass);
  margin:0 0 14px;font-weight:600}
h1{font-family:var(--display);font-weight:400;font-size:clamp(44px,12vw,94px);
  line-height:.94;margin:0;letter-spacing:-.02em}
h1 .it{font-style:italic;display:block;color:var(--brass)}
.since{margin:18px 0 0;font-size:13.5px;color:var(--dim);
  font-variant-numeric:tabular-nums}

/* ---- the book ---- */
.book{max-width:820px;margin:0 auto;padding:clamp(44px,8vw,80px) 24px;perspective:2000px}
.book-top{display:flex;align-items:baseline;gap:14px;margin-bottom:22px}
.book-top .label{font-size:11px;letter-spacing:.28em;text-transform:uppercase;
  color:var(--faint);font-weight:600}
.book-top .line{flex:1;height:1px;background:var(--rule)}

.page{position:relative;background:
   linear-gradient(104deg,#201C19 0%,#1B1816 26%,#1A1715 100%);
  border:1px solid var(--rule);border-radius:3px 10px 10px 3px;
  box-shadow:inset 16px 0 28px -20px #000, inset -1px 0 0 rgba(255,255,255,.02), var(--shadow);
  padding:clamp(32px,6vw,54px) clamp(26px,5vw,52px) clamp(56px,7vw,64px);
  min-height:clamp(260px,48vw,330px);display:flex;flex-direction:column;
  transform-origin:left center;transform-style:preserve-3d;backface-visibility:hidden}
.page::before{content:"";position:absolute;left:7px;top:14px;bottom:14px;width:1px;
  background:linear-gradient(to bottom,transparent,rgba(199,167,95,.22),transparent)}
.leaf{display:flex;gap:clamp(16px,3.6vw,30px);align-items:flex-start;flex:1}
.leaf .num{font-family:var(--display);font-size:clamp(46px,11vw,80px);line-height:.82;
  color:var(--brass);font-variant-numeric:lining-nums tabular-nums;flex:none;opacity:.9}
.leaf .say{font-family:var(--display);font-size:clamp(22px,5vw,34px);line-height:1.24;
  margin:0;min-width:0;padding-top:.14em;text-wrap:pretty}
.folio{position:absolute;left:0;right:0;bottom:clamp(20px,3vw,26px);text-align:center;
  font-size:11.5px;letter-spacing:.22em;color:var(--faint);
  font-variant-numeric:tabular-nums;margin:0}

@keyframes leaf-out-fwd{to{transform:rotateY(-26deg) translateX(-3%);opacity:0}}
@keyframes leaf-in-fwd{from{transform:rotateY(22deg) translateX(3%);opacity:0}}
@keyframes leaf-out-back{to{transform:rotateY(22deg) translateX(3%);opacity:0}}
@keyframes leaf-in-back{from{transform:rotateY(-26deg) translateX(-3%);opacity:0}}
.page.out-fwd{animation:leaf-out-fwd .2s ease-in forwards}
.page.in-fwd{animation:leaf-in-fwd .28s ease-out}
.page.out-back{animation:leaf-out-back .2s ease-in forwards}
.page.in-back{animation:leaf-in-back .28s ease-out}
@media (prefers-reduced-motion:reduce){
  .page.out-fwd,.page.in-fwd,.page.out-back,.page.in-back{animation:none}}

.controls{display:flex;align-items:center;gap:8px;margin-top:22px}
.controls button{appearance:none;background:none;border:1px solid var(--rule);
  color:var(--ink);font-family:var(--ui);font-size:15px;font-weight:500;
  width:44px;height:44px;border-radius:50%;cursor:pointer;
  display:grid;place-items:center;transition:border-color .18s,color .18s}
.controls button:hover{border-color:var(--brass);color:var(--brass)}
.controls .shuffle{width:auto;padding:0 20px;border-radius:999px;font-size:14px}
.controls .hint{margin-left:auto;font-size:12px;color:var(--faint);letter-spacing:.06em}


/* ---- index ---- */
.index{max-width:1120px;margin:0 auto;
  padding:0 24px calc(90px + env(safe-area-inset-bottom,0px))}
.index h2{font-family:var(--display);font-weight:400;font-style:italic;
  font-size:clamp(26px,5vw,38px);margin:0 0 4px}
.index .sub{margin:0 0 30px;color:var(--faint);font-size:13.5px}
.index ol{list-style:none;margin:0;padding:0;columns:1;column-gap:54px}
@media (min-width:860px){.index ol{columns:2}}
.index li{break-inside:avoid}
.index a{display:flex;gap:16px;align-items:baseline;padding:11px 0;
  border-bottom:1px solid var(--rule);color:var(--ink);text-decoration:none;
  transition:color .16s}
.index a:hover{color:var(--brass)}
.index .n{font-family:var(--display);font-size:13px;color:var(--faint);
  font-variant-numeric:lining-nums tabular-nums;min-width:2.3em;text-align:right;flex:none}
.index a:hover .n{color:var(--brass)}
.index .t{min-width:0;font-size:15.5px;line-height:1.45}

.index details{border-top:1px solid var(--rule);border-bottom:1px solid var(--rule)}
.index summary{list-style:none;cursor:pointer;padding:26px 0;display:flex;
  align-items:baseline;gap:14px}
.index summary::-webkit-details-marker{display:none}
.index summary h2{font-family:var(--display);font-weight:400;font-style:italic;
  font-size:clamp(24px,4.4vw,34px);margin:0}
.index summary .meta{margin-left:auto;font-size:12px;letter-spacing:.2em;
  text-transform:uppercase;color:var(--faint);white-space:nowrap}
.index details[open] summary .meta::after{content:" \2014 close"}
.index details:not([open]) summary .meta::after{content:" \2014 open"}
.index .panel{padding-bottom:30px}

/* ---- the song ---- */
.tune{max-width:820px;margin:0 auto;padding:0 24px clamp(40px,7vw,64px)}
.tune .lead{margin:0 0 16px;font-family:var(--display);font-style:italic;
  font-size:clamp(17px,3.4vw,22px);color:var(--brass)}
.tune .frame{border:1px solid var(--rule);border-radius:4px;overflow:hidden;
  background:var(--raise);box-shadow:var(--shadow)}
.tune .screen{position:relative;aspect-ratio:16/9;background:#000}
.tune .screen iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
.tune .poster{position:absolute;inset:0;width:100%;height:100%;padding:0;border:0;
  cursor:pointer;background:#000;display:grid;place-items:center}
.tune .poster img{width:100%;height:100%;object-fit:cover;opacity:.62;
  transition:opacity .25s}
.tune .poster:hover img{opacity:.78}
.tune .play{position:absolute;width:62px;height:62px;border-radius:50%;
  background:rgba(19,17,16,.72);border:1px solid var(--brass);display:grid;
  place-items:center;color:var(--brass);font-size:19px;padding-left:4px;
  backdrop-filter:blur(2px)}
.tune .bar{display:flex;align-items:baseline;gap:12px;padding:15px 18px}
.tune .bar .t{font-family:var(--display);font-size:17px}
.tune .bar .by{font-size:12.5px;color:var(--faint)}
.tune .bar .cue{margin-left:auto;font-size:11px;letter-spacing:.2em;
  text-transform:uppercase;color:var(--brass)}

/* ---- the map ---- */
.atlas{max-width:1120px;margin:0 auto;padding:0 24px clamp(46px,7.5vw,80px)}
.atlas-top{display:flex;align-items:baseline;gap:14px;margin-bottom:22px;flex-wrap:wrap;
  padding-bottom:14px;border-bottom:1px solid var(--rule)}
.atlas-top h2{font-family:var(--display);font-weight:400;font-style:italic;
  font-size:clamp(24px,4.4vw,34px);margin:0}
.atlas-top .gap{margin-left:auto;font-family:var(--display);font-size:clamp(20px,4vw,28px);
  color:var(--brass);font-variant-numeric:tabular-nums}
.atlas-top .gap small{font-family:var(--ui);font-size:11px;letter-spacing:.2em;
  text-transform:uppercase;color:var(--faint);display:block;text-align:right;
  margin-top:2px}
.atlas figure{margin:0;border:1px solid var(--rule);border-radius:4px;
  overflow:hidden;background:#0E0C0B}
.plot{position:relative;width:100%;aspect-ratio:16/8.3}
@media (max-width:620px){.plot{aspect-ratio:16/11}}
.plot svg{position:absolute;inset:0;width:100%;height:100%}
.plot::after{content:"";position:absolute;inset:0;pointer-events:none;
  background:radial-gradient(130% 110% at 50% 50%,transparent 52%,rgba(8,9,10,.72) 100%)}
@media (prefers-reduced-motion:no-preference){
  .flight{stroke-dashoffset:0;animation:fly 9s linear infinite}
  @keyframes fly{to{stroke-dashoffset:-140}}}
.pin{position:absolute;font-size:clamp(10.5px,1.5vw,14px);letter-spacing:.02em;
  white-space:nowrap;text-shadow:0 1px 8px #0E0C0B,0 0 14px #0E0C0B;
  pointer-events:none;line-height:1}
.pin.there{color:#9FC3D1}
.pin.home{color:var(--brass);font-weight:600}
.pin.left{transform:translate(calc(-100% - 13px),-50%)}
.pin.right{transform:translate(13px,-50%)}
.pin.below{transform:translate(-50%,16px)}
.pin.gap{color:var(--brass);font-family:var(--display);
  font-size:clamp(15px,2.8vw,26px);transform:translate(-50%,-50%);
  font-variant-numeric:tabular-nums;text-shadow:0 1px 10px #0E0C0B}
.legend{display:flex;gap:22px;flex-wrap:wrap;margin-top:16px;font-size:12.5px;
  color:var(--dim)}
.legend i{width:9px;height:9px;border-radius:50%;display:inline-block;
  margin-right:8px;vertical-align:1px}

/* ---- say something back ---- */
.post{max-width:820px;margin:0 auto;padding:0 24px clamp(46px,7.5vw,80px)}
.post h2{font-family:var(--display);font-weight:400;font-style:italic;
  font-size:clamp(24px,4.4vw,34px);margin:0 0 6px;padding-bottom:14px;
  border-bottom:1px solid var(--rule)}
.post h2 + .sub{margin-top:14px}
.post .sub{margin:0 0 18px;color:var(--faint);font-size:13.5px;max-width:52ch}
.post textarea{width:100%;background:var(--raise);border:1px solid var(--rule);
  border-radius:4px;color:var(--ink);font-family:var(--ui);font-size:16px;
  line-height:1.6;padding:16px;resize:vertical}
.post textarea::placeholder{color:var(--faint)}
.postrow{display:flex;align-items:center;gap:16px;margin-top:14px;flex-wrap:wrap}
.postrow button{font-family:var(--ui);font-size:14px;font-weight:600;
  color:#131110;background:var(--brass);border:0;border-radius:999px;
  padding:12px 22px;cursor:pointer}
.postrow a{color:var(--brass);font-size:13.5px;text-decoration:none;
  border-bottom:1px solid rgba(199,167,95,.3);padding-bottom:2px}
.postrow a:hover{border-bottom-color:var(--brass)}
.postrow .said{font-size:13px;color:var(--dim)}

/* ---- what you are made of ---- */
.parts{max-width:1120px;margin:0 auto;padding:0 24px clamp(46px,7.5vw,80px)}
.fig{display:flex;gap:clamp(22px,5vw,60px);align-items:center;flex-wrap:wrap;
  border:1px solid var(--rule);border-radius:4px;background:#0C0B0A;
  padding:clamp(22px,4vw,40px)}
.figwrap{flex:0 0 auto;width:clamp(190px,36vw,280px);margin:0 auto}
.figsvg{display:block;width:100%;height:auto;overflow:visible}
.figsvg .node{fill:#C7A75F;fill-opacity:.05;stroke:#C7A75F;stroke-width:1.1;
  stroke-opacity:.3;cursor:pointer;
  transition:fill-opacity .22s,stroke-opacity .22s,r .22s}
.figsvg .node:hover{fill-opacity:.2;stroke-opacity:.8}
.figsvg .node.on{fill-opacity:.42;stroke-opacity:1;stroke-width:1.6}
.fig{background:radial-gradient(120% 80% at 30% 20%,#17150F 0%,#0B0A09 72%)}
.figsay{flex:1 1 260px;min-width:0}
.figsay .what{font-family:var(--display);font-size:clamp(24px,5vw,38px);
  color:var(--brass);margin:0 0 6px;line-height:1.1}
.figsay .why{font-family:var(--display);font-style:italic;
  font-size:clamp(18px,3.6vw,25px);margin:0 0 24px;line-height:1.3;color:var(--ink)}
.chips{display:flex;flex-wrap:wrap;gap:8px}
.chip{font-family:var(--ui);font-size:12.5px;color:var(--dim);background:none;
  border:1px solid var(--rule);border-radius:999px;padding:7px 14px;cursor:pointer;
  transition:color .16s,border-color .16s}
.chip:hover,.chip.on{color:var(--brass);border-color:var(--brass)}

/* ---- how you talk ---- */
.lexicon{max-width:1120px;margin:0 auto;padding:0 24px clamp(46px,7.5vw,80px)}
.tallyline{margin:0 0 24px;color:var(--faint);font-size:13.5px;
  font-variant-numeric:tabular-nums;max-width:48ch}
.lex{list-style:none;margin:0;padding:0;display:grid;gap:1px;
  background:var(--rule);border:1px solid var(--rule);border-radius:4px;
  overflow:hidden;grid-template-columns:1fr}
@media (min-width:760px){.lex{grid-template-columns:1fr 1fr}}
.lex li{background:#141211;display:grid;grid-template-columns:auto 1fr;
  column-gap:16px;row-gap:3px;align-items:baseline;padding:15px 20px}
.lex .w{font-family:var(--display);font-size:clamp(19px,3.6vw,25px);color:var(--ink)}
.lex .c{font-family:var(--display);font-size:clamp(17px,3vw,21px);color:var(--brass);
  font-variant-numeric:tabular-nums;text-align:right}
.lex .g{grid-column:1/-1;font-size:12.5px;color:var(--faint);line-height:1.45}

/* ---- three years ---- */
.years{max-width:820px;margin:0 auto;padding:0 24px clamp(46px,7.5vw,80px)}
.tl{list-style:none;margin:0;padding:0}
.tl li{display:grid;grid-template-columns:auto 18px 1fr;align-items:start;
  column-gap:14px;position:relative;padding-bottom:26px}
.tl li:last-child{padding-bottom:0}
.tl .when{font-size:12px;letter-spacing:.14em;text-transform:uppercase;
  color:var(--faint);padding-top:4px;white-space:nowrap}
.tl .dot{width:9px;height:9px;border-radius:50%;background:var(--brass);
  margin:6px auto 0;position:relative}
.tl li:not(:last-child) .dot::after{content:"";position:absolute;left:50%;top:13px;
  width:1px;height:calc(100% + 30px);background:var(--rule);transform:translateX(-50%)}
.tl .what{min-width:0}
.tl .what b{display:block;font-family:var(--display);font-weight:400;
  font-size:clamp(20px,4vw,27px);margin-bottom:3px}
.tl .what{font-size:14px;color:var(--dim);line-height:1.5}

/* ---- clocks ---- */
.clocks{display:flex;align-items:flex-end;gap:clamp(24px,6vw,54px);
  margin-top:26px;flex-wrap:wrap}
.clock .city{margin:0;font-size:11px;letter-spacing:.26em;text-transform:uppercase;
  color:var(--faint)}
.clock .now{margin:5px 0 2px;font-family:var(--display);
  font-size:clamp(30px,6.5vw,46px);line-height:1;color:var(--brass);
  font-variant-numeric:tabular-nums}
.clock .zone{margin:0;font-size:12px;color:var(--faint)}
.apartby{margin:0 0 4px;font-size:13px;color:var(--dim);font-style:italic}

/* ---- open when ---- */
.mail{max-width:820px;margin:0 auto;padding:0 24px clamp(46px,7.5vw,80px)}
.envs{display:grid;gap:10px}
.env{border:1px solid var(--rule);border-radius:4px;background:var(--raise)}
.env summary{list-style:none;cursor:pointer;padding:17px 20px;
  font-family:var(--display);font-size:clamp(18px,3.6vw,24px);
  display:flex;align-items:baseline;gap:12px;transition:color .16s}
.env summary::-webkit-details-marker{display:none}
.env summary:hover{color:var(--brass)}
.env .seal{color:var(--brass);font-size:14px}
.env[open] summary{color:var(--brass);padding-bottom:4px}
.env p{margin:0;padding:0 20px 20px 46px;font-family:var(--display);
  font-style:italic;font-size:clamp(16px,3.2vw,20px);line-height:1.45;
  color:var(--ink);max-width:54ch}

/* ---- theo ---- */
.theo{max-width:960px;margin:0 auto;padding:0 24px clamp(46px,7.5vw,80px);
  display:flex;align-items:center;gap:clamp(22px,5vw,46px);flex-wrap:wrap}
.film{margin:0;flex:0 0 auto;width:clamp(200px,42vw,300px);
  border:1px solid var(--rule);border-radius:6px;overflow:hidden;
  background:#000;box-shadow:var(--shadow)}
.film video{display:block;width:100%;height:auto}
.paw{display:block;width:34px;color:var(--brass);margin-bottom:10px}
.paw svg{width:100%;height:auto;display:block}
.pupsay{flex:1 1 260px;min-width:0}
.pupsay h2{font-family:var(--display);font-weight:400;font-style:italic;
  font-size:clamp(24px,4.4vw,34px);margin:0 0 6px}
.pupsay p{margin:0;color:var(--dim);font-size:14.5px;line-height:1.55;max-width:46ch}

footer{border-top:1px solid var(--rule);max-width:1120px;margin:0 auto;
  padding:34px 24px calc(50px + env(safe-area-inset-bottom,0px));
  display:flex;justify-content:space-between;align-items:center;gap:16px;
  font-size:12.5px;color:var(--faint);letter-spacing:.04em}
footer .mark{color:var(--brass);font-size:15px}

/* ---- gate ---- */
#gate{position:fixed;inset:0;z-index:50;background:var(--bg);display:grid;
  place-items:center;padding:28px}
#gate[hidden]{display:none}
#gate .box{width:100%;max-width:430px;text-align:center}
#gate .mark{font-family:var(--display);font-size:34px;color:var(--brass);margin:0 0 26px}
#gate p.q{font-family:var(--display);font-size:clamp(21px,5vw,28px);line-height:1.3;
  margin:0 0 28px;text-wrap:pretty}
#gate form{display:flex;flex-direction:column;gap:12px}
#gate input{font-family:var(--ui);font-size:16px;color:var(--ink);background:var(--raise);
  border:1px solid var(--rule);border-radius:4px;padding:14px 16px;text-align:center}
#gate input::placeholder{color:var(--faint)}
#gate button{font-family:var(--ui);font-size:14px;font-weight:600;letter-spacing:.04em;
  color:#131110;background:var(--brass);border:0;border-radius:999px;
  padding:14px 22px;cursor:pointer}
#gate .no{min-height:20px;font-size:13px;color:var(--dim);margin:4px 0 0}
body.locked{overflow:hidden}
</style>
</head>
<body>

<div id="gate" hidden>
  <div class="box">
    <p class="mark">&#9829;</p>
    <p class="q">__HINT__</p>
    <form id="gateForm" autocomplete="off">
      <input id="gateInput" type="text" placeholder="Type it here" aria-label="Answer"
             autocapitalize="off" autocorrect="off" spellcheck="false">
      <button type="submit">Open</button>
    </form>
    <p class="no" id="gateNo" role="status"></p>
  </div>
</div>

<div class="title">
  <p class="kicker">For Selma</p>
  <h1>One hundred<span class="it">reasons</span></h1>
  <p class="since" id="since"></p>
</div>

<section class="tune">
  <p class="lead">Press play first. Then read the rest with it on.</p>
  <div class="frame">
    <div class="screen" id="screen">
      <button type="button" class="poster" id="poster" aria-label="Play the song">
        <img src="https://i.ytimg.com/vi/__SONG_ID__/maxresdefault.jpg" alt=""
             onerror="this.src='https://i.ytimg.com/vi/__SONG_ID__/hqdefault.jpg'">
        <span class="play">&#9654;</span>
      </button>
    </div>
    <div class="bar">
      <span class="t">__SONG_LABEL__</span>
      <span class="by">__SONG_BY__</span>
      <span class="cue">Press play</span>
    </div>
  </div>
</section>

<header class="plate">
  __HERO__
  <p class="tally"><span id="tally"></span><span class="tap">tap for the next</span></p>
</header>

<section class="book">
  <div class="book-top"><span class="label" id="deckLabel">Today</span><span class="line"></span></div>
  <article class="page" id="page">
    <div class="leaf">
      <div class="num" id="num">1</div>
      <p class="say" id="say">__FIRST__</p>
    </div>
    <p class="folio" id="folio"></p>
  </article>
  <div class="controls">
    <button type="button" id="prev" aria-label="Previous page">&#8592;</button>
    <button type="button" id="next" aria-label="Next page">&#8594;</button>
    <button type="button" id="shuffle" class="shuffle">Surprise me</button>
    <span class="hint">swipe, or use &#8592; &#8594;</span>
  </div>
</section>

<section class="index">
  <details id="allOfThem">
    <summary><h2>All of them</h2><span class="meta">100</span></summary>
    <div class="panel">
      <ol>
__ROWS__
      </ol>
    </div>
  </details>
</section>

<section class="post">
  <h2>Say something back</h2>
  <p class="sub">Write it here, then send it to me. Nothing on this page can reach
    me on its own.</p>
  <textarea id="note" rows="5" placeholder="Whatever you want."></textarea>
  <div class="postrow">
    <button type="button" id="copyNote">Copy it</button>
    <a id="mailNote" href="#">Open it in mail</a>
    <span class="said" id="said" role="status"></span>
  </div>
</section>

<section class="lexicon">
  <div class="atlas-top"><h2>How you talk</h2></div>
  __LEXICON__
</section>

<section class="years">
  <div class="atlas-top"><h2>Three years</h2></div>
  <ol class="tl">
__TIMELINE__
  </ol>
</section>

<section class="parts">
  <div class="atlas-top"><h2>What you are made of</h2></div>
  __FIGURE__
</section>

<section class="atlas">
  <div class="atlas-top">
    <h2>Where we are</h2>
    <div class="gap">__APART__ km<small>apart</small></div>
  </div>
  <figure>__CHART__</figure>
  <p class="legend">
    <span><i style="background:#C7A75F"></i>The two of us</span>
    <span><i style="background:#7EA8B8"></i>Everywhere we went together</span>
  </p>
  <div class="clocks">
    <div class="clock"><p class="city">Paris</p><p class="now" id="clkParis">&mdash;</p>
      <p class="zone" id="zParis"></p></div>
    <div class="clock"><p class="city">Amman</p><p class="now" id="clkAmman">&mdash;</p>
      <p class="zone" id="zAmman"></p></div>
    <p class="apartby" id="apartBy"></p>
  </div>
</section>

<section class="mail">
  <div class="atlas-top"><h2>Open when&hellip;</h2></div>
  <div class="envs">
__LETTERS__
  </div>
</section>

<section class="theo">
  <figure class="film">
    <video id="theoFilm" src="media/theo.mp4" poster="media/theo.jpg"
           preload="none" playsinline controls loop></video>
  </figure>
  <div class="pupsay">
    <span class="paw" aria-hidden="true">
      <svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
        <ellipse cx="60" cy="76" rx="21" ry="18" fill="currentColor" opacity=".95"/>
        <ellipse cx="39" cy="46" rx="10" ry="13" fill="currentColor" opacity=".8"
          transform="rotate(-22 39 46)"/>
        <ellipse cx="60" cy="38" rx="10" ry="13" fill="currentColor" opacity=".8"/>
        <ellipse cx="81" cy="46" rx="10" ry="13" fill="currentColor" opacity=".8"
          transform="rotate(22 81 46)"/>
      </svg>
    </span>
    <h2>__THEO_NAME__</h2>
    <p>__THEO_WHY__</p>
  </div>
</section>

<footer>
  <span>Still true</span>
  <span class="mark">&#9829;</span>
</footer>

<script>
(function () {
  var reasons = __REASONS__;
  var photos  = __PHOTOS__;
  var ANSWERS = __ANSWERS__;
  var START   = "__START__";
  var HOMES   = __HOMES__;
  var PLACES  = __PLACES__;
  var SONG    = "__SONG_ID__";
  var KEY     = 'sx.open';

  // #lock in the address bar forgets the answer again (handy for testing)
  if (location.hash === '#lock') {
    try { localStorage.removeItem(KEY); } catch (e) {}
    history.replaceState(null, '', location.pathname);
  }

  /* ---------- the gate ---------- */
  function tidy(v) {
    return String(v).toLowerCase().normalize('NFD')
      .replace(/[̀-ͯ]/g, '')
      .replace(/[^a-z0-9]/g, '')
      .replace(/^the/, '');
  }
  // asked fresh on every visit, on purpose - nothing is remembered
  function already() { return false; }
  function remember() {
    try { localStorage.removeItem(KEY); } catch (e) {}
  }
  var gate = document.getElementById('gate');
  function open_() {
    gate.hidden = true;
    document.body.classList.remove('locked');
  }
  if (!ANSWERS.length || already()) {
    open_();
  } else {
    gate.hidden = false;
    document.body.classList.add('locked');
    var tries = 0;
    document.getElementById('gateForm').addEventListener('submit', function (e) {
      e.preventDefault();
      var said = tidy(document.getElementById('gateInput').value);
      var ok = ANSWERS.some(function (a) { return tidy(a) === said; });
      if (ok) { remember(); open_(); return; }
      tries++;
      document.getElementById('gateNo').textContent =
        tries < 3 ? 'Not it. Try again.' : 'Still not it. Think about where we ate.';
      document.getElementById('gateInput').select();
    });
    setTimeout(function () { document.getElementById('gateInput').focus(); }, 80);
  }

  /* ---------- turning pages ---------- */
  var page  = document.getElementById('page');
  var num   = document.getElementById('num');
  var say   = document.getElementById('say');
  var folio = document.getElementById('folio');
  var label = document.getElementById('deckLabel');

  var today = Math.floor(Date.now() / 86400000) % reasons.length;
  var at = today;
  var busy = false;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function paintLeaf(i, picked) {
    at = (i + reasons.length) % reasons.length;
    num.textContent = at + 1;
    say.textContent = reasons[at];
    folio.textContent = (at + 1) + ' ⁄ ' + reasons.length;
    label.textContent = (at === today && !picked) ? 'Today' : 'One of them';
  }

  function turn(i, dir, picked) {
    if (busy) { return; }
    if (reduce || dir === 0) { paintLeaf(i, picked); return; }
    busy = true;
    var outC = dir > 0 ? 'out-fwd' : 'out-back';
    var inC  = dir > 0 ? 'in-fwd'  : 'in-back';
    page.classList.add(outC);
    setTimeout(function () {
      paintLeaf(i, picked);
      page.classList.remove(outC);
      page.classList.add(inC);
      setTimeout(function () { page.classList.remove(inC); busy = false; }, 290);
    }, 200);
  }

  document.getElementById('prev').addEventListener('click', function () { turn(at - 1, -1, true); });
  document.getElementById('next').addEventListener('click', function () { turn(at + 1, 1, true); });

  var bag = [];
  document.getElementById('shuffle').addEventListener('click', function () {
    if (!bag.length) {
      for (var k = 0; k < reasons.length; k++) { if (k !== at) bag.push(k); }
      for (var j = bag.length - 1; j > 0; j--) {
        var r = Math.floor(Math.random() * (j + 1)), t = bag[j]; bag[j] = bag[r]; bag[r] = t;
      }
    }
    var n = bag.pop();
    turn(n, n > at ? 1 : -1, true);
  });

  document.addEventListener('keydown', function (e) {
    if (!gate.hidden) return;
    if (e.target.closest('input,textarea')) return;
    if (e.key === 'ArrowLeft')  turn(at - 1, -1, true);
    if (e.key === 'ArrowRight') turn(at + 1, 1, true);
  });

  var x0 = null;
  page.addEventListener('touchstart', function (e) { x0 = e.changedTouches[0].clientX; }, { passive: true });
  page.addEventListener('touchend', function (e) {
    if (x0 === null) return;
    var dx = e.changedTouches[0].clientX - x0;
    if (Math.abs(dx) > 48) turn(at + (dx < 0 ? 1 : -1), dx < 0 ? 1 : -1, true);
    x0 = null;
  }, { passive: true });

  /* ---------- since ---------- */
  var days = Math.floor((Date.now() - Date.parse(START)) / 86400000);
  document.getElementById('since').textContent =
    new Date(START).toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' })
    + ' — ' + days.toLocaleString() + ' days ago';

  /* ---------- #47 opens on 47 ---------- */
  function fromHash() {
    var n = parseInt((location.hash || '').slice(1), 10);
    if (n >= 1 && n <= reasons.length) paintLeaf(n - 1, true);
  }
  window.addEventListener('hashchange', fromHash);

  document.querySelectorAll('.index a').forEach(function (a) {
    a.addEventListener('click', function (e) {
      e.preventDefault();
      var n = parseInt(a.getAttribute('href').slice(1), 10);
      history.replaceState(null, '', '#' + n);
      turn(n - 1, n - 1 > at ? 1 : -1, true);
      document.querySelector('.book').scrollIntoView({ block: 'center' });
    });
  });

  /* ---------- tap the photograph for the next one ---------- */
  var hero = document.getElementById('hero');
  var tally = document.getElementById('tally');
  if (hero && photos.length > 1) {
    var shot = Math.floor(Math.random() * photos.length);
    function paintHero(i) {
      shot = (i + photos.length) % photos.length;
      hero.src = 'photos/' + photos[shot];
      if (tally) tally.textContent = (shot + 1) + ' / ' + photos.length;
    }
    document.querySelector('.plate').addEventListener('click', function () {
      paintHero(shot + 1);
    });
    paintHero(shot);
  } else if (tally) {
    tally.hidden = true;
  }

  /* ---------- the song ---------- */
  var poster = document.getElementById('poster');
  if (poster) {
    poster.addEventListener('click', function () {
      var f = document.createElement('iframe');
      f.src = 'https://www.youtube-nocookie.com/embed/' + SONG +
              '?autoplay=1&rel=0&modestbranding=1';
      f.title = 'Hey There Delilah';
      f.allow = 'accelerometer; autoplay; encrypted-media; picture-in-picture';
      f.referrerPolicy = 'strict-origin-when-cross-origin';
      f.allowFullscreen = true;
      document.getElementById('screen').replaceChildren(f);
    });
  }

  /* ---------- say something back ---------- */
  var note = document.getElementById('note');
  var said = document.getElementById('said');
  if (note) {
    document.getElementById('copyNote').addEventListener('click', function () {
      var text = note.value.trim();
      if (!text) { note.focus(); return; }
      function fallback() {
        note.select();
        try { document.execCommand('copy'); said.textContent = 'Copied.'; }
        catch (e) { said.textContent = 'Select it and copy.'; }
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text)
          .then(function () { said.textContent = 'Copied. Now send it to me.'; })
          .catch(fallback);
      } else { fallback(); }
    });
    document.getElementById('mailNote').addEventListener('click', function (e) {
      e.preventDefault();
      window.location.href = 'mailto:sufiansartawi8@gmail.com'
        + '?subject=' + encodeURIComponent('Back at you')
        + '&body=' + encodeURIComponent(note.value);
    });
  }

  /* ---------- what you are made of ---------- */
  var meanings = {};
  try { meanings = JSON.parse(document.getElementById('partData').textContent); }
  catch (e) {}
  var partName = document.getElementById('partName');
  var partWhy = document.getElementById('partWhy');
  var allHits = Array.prototype.slice.call(document.querySelectorAll('[data-part]'));
  function pick(name) {
    if (!meanings[name]) return;
    partName.textContent = name;
    partWhy.textContent = meanings[name];
    allHits.forEach(function (el) {
      el.classList.toggle('on', el.dataset.part === name);
    });
  }
  allHits.forEach(function (el) {
    el.addEventListener('click', function () { pick(el.dataset.part); });
    el.addEventListener('keydown', function (ev) {
      if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); pick(el.dataset.part); }
    });
  });

  /* ---------- two clocks ---------- */
  function tz(city, zone, elId, zoneId) {
    var t = document.getElementById(elId);
    if (!t) return null;
    function face() {
      try {
        t.textContent = new Intl.DateTimeFormat('en-GB', {
          timeZone: zone, hour: '2-digit', minute: '2-digit', hour12: false
        }).format(new Date());
        var z = document.getElementById(zoneId);
        if (z) {
          var nm = new Intl.DateTimeFormat('en-GB', {
            timeZone: zone, timeZoneName: 'short'
          }).formatToParts(new Date()).find(function (q) { return q.type === 'timeZoneName'; });
          z.textContent = (nm ? nm.value : zone);
        }
      } catch (e) { t.textContent = '--:--'; }
    }
    face();
    return face;
  }
  var faces = [tz('Paris', 'Europe/Paris', 'clkParis', 'zParis'),
               tz('Amman', 'Asia/Amman', 'clkAmman', 'zAmman')].filter(Boolean);
  if (faces.length) {
    setInterval(function () { faces.forEach(function (f) { f(); }); }, 10000);
    var by = document.getElementById('apartBy');
    if (by) {
      try {
        var now = new Date();
        function off(zone) {
          var s_ = new Intl.DateTimeFormat('en-GB', {
            timeZone: zone, hour: 'numeric', hour12: false
          }).format(now);
          return parseInt(s_, 10);
        }
        var d = off('Asia/Amman') - off('Europe/Paris');
        if (d < -12) d += 24; if (d > 12) d -= 24;
        by.textContent = d === 0 ? 'the same hour'
          : Math.abs(d) + (Math.abs(d) === 1 ? ' hour apart' : ' hours apart');
      } catch (e) {}
    }
  }

  paintLeaf(at, false);
  if (location.hash && location.hash !== '#lock') fromHash();
})();
</script>
</body>
</html>
"""

out = (
    TEMPLATE.replace("__ROWS__", index_rows)
    .replace("__HERO__", hero_img)
    .replace("__REASONS__", json.dumps(reasons, ensure_ascii=False))
    .replace("__PHOTOS__", json.dumps(photos, ensure_ascii=False))
    .replace("__START__", START)
    .replace("__HINT__", html.escape(HINT))
    .replace("__SONG_LABEL__", html.escape(SONG_LABEL))
    .replace("__SONG_ID__", html.escape(SONG_ID))
    .replace("__SONG_BY__", html.escape(SONG_BY))
    .replace("__HOMES__", json.dumps(HOMES, ensure_ascii=False))
    .replace("__PLACES__", json.dumps(PLACES, ensure_ascii=False))
    .replace("__APART__", f"{APART:,}")
    .replace("__CHART__", chart())
    .replace("__FIGURE__", figure())
    .replace("__LEXICON__", lexicon())
    .replace("__TIMELINE__", timeline())
    .replace("__LETTERS__", letters())
    .replace("__THEO_NAME__", html.escape(THEO[0]))
    .replace("__THEO_WHY__", html.escape(THEO[1]))
    .replace("__ANSWERS__", json.dumps(ANSWERS))
    .replace("__FIRST__", html.escape(reasons[0]))
)
(SITE / "index.html").write_text(out, "utf-8")
print(f"built site/index.html - {len(reasons)} reasons, {len(photos)} photos")
