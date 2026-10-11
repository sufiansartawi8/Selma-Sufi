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
START = "2023-07-17"            # the first Marbella trip
LAST  = "2026-08-18T15:00:00+02:00"   # Marbella again, the last time

# Password gate. She is asked on every visit; nothing is remembered.
# Matching ignores case, spaces, punctuation and a leading "the".
HINT = "The restaurant in New York where we had our first date."
ANSWERS = ["Wayan", "Wayan NYC", "Wayan New York", "Wayan Nolita", "Wayan restaurant"]

# The song. Hosting the recording would be piracy; this sends
SONG_LABEL = "Hey There Delilah"
SONG_ID = "h_m-BjrxmgI"          # YouTube video id
SONG_BY = "Plain White T's"

# Map. Drawn as a diagram, no tiles and no API.
# (label, lat, lon, which side the label sits on)
HOMES = [
    ("Selma \u2014 Paris", 48.8566, 2.3522, "left"),
    ("Sufyan \u2014 Amman", 31.9454, 35.9284, "above"),
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

def lit(t):
    """*starred* words come through in red."""
    out, bits = [], re.split(r"\*([^*]+)\*", t)
    for k, b in enumerate(bits):
        out.append(f'<em>{html.escape(b)}</em>' if k % 2 else html.escape(b))
    return "".join(out)


def plain(t):
    return t.replace("*", "")


index_rows = "\n".join(
    f'      <li><a href="#{i}"><span class="n">{i}</span>'
    f'<span class="t">{lit(t)}</span></a></li>'
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
     "Then I'm missing you at the same time, which is most of the time, and "
     "usually at the stupid hours. Go through the list. I meant every one of "
     "them when I wrote it and I mean them now."),
    ("you can't sleep",
     "Put the song on. Read one reason, not all of them \u2014 you'll be asleep "
     "before the end. You always fell asleep on the phone anyway, mid-sentence, "
     "and I never once minded."),
    ("you're annoyed with me",
     "You're probably right. You usually were, and I took far too long to say "
     "so out loud. Be annoyed. It never made me love you less and it never "
     "will."),
    ("it's been a bad day",
     "Tell me about it properly. The long version, the one with the timeline "
     "and the part about what the person actually said. I'll still be listening "
     "the way I should have been listening all along."),
    ("you forget how good you are",
     "Read number fifty again, then read it twice. You knew what you deserved "
     "long before I understood it. That wasn't you being difficult. That was "
     "you being right."),
    ("you're about to do something big",
     "Interview, presentation, first day, hard conversation \u2014 you walk in "
     "and the room adjusts to you. It always has. My grandmother noticed it in "
     "a hallway in ten seconds."),
    ("you're in Paris and it's raining",
     "Make the tea. Put something terrible on, the kind of thing you'd watch "
     "and send me screenshots of at midnight. Not every day has to be useful."),
    ("someone is lucky to have you",
     "They will be, and they should know it faster than I did. I hope he books "
     "the table before you have to ask. That was never a big thing to want."),
    ("you want to know if it was real",
     "Three years, a hundred and one reasons, ninety-nine photographs, a "
     "hundred and thirty-seven thousand messages. It was real. There's no "
     "version of this where it wasn't."),
    ("it's been a long time",
     "Then I hope you're happy, and I hope it's the uncomplicated kind. This "
     "page doesn't need anything from you. It's just here, and it stays here."),
]

# --- The dog. ---
THEO = ("You're Theo's mama",
        "Born in M\u00e1laga, flown to Amman through Istanbul, and yours from the "
        "very first photo. You still asked how he was months after everything else "
        "had gone quiet. He misses you.")

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
           '<stop offset="0" stop-color="#D7CFBE"/><stop offset="1" stop-color="#CFC6B2"/>'
           '</linearGradient>'
           '<linearGradient id="soil" x1="0" y1="0" x2="0" y2="1">'
           '<stop offset="0" stop-color="#C3BAA4"/><stop offset="1" stop-color="#BAB099"/>'
           '</linearGradient>'
           '<linearGradient id="ours" x1="0" y1="0" x2="0" y2="1">'
           '<stop offset="0" stop-color="#A89C80"/><stop offset="1" stop-color="#9E9175"/>'
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
    svg.append('<g stroke="#CBC2AF" stroke-width="1">' + "".join(g) + "</g>")

    svg.append(f'<g fill="url(#soil)" stroke="#AEA48C" stroke-width="1" '
               f'vector-effect="non-scaling-stroke"><path d="{" ".join(land)}"/></g>')
    svg.append(f'<g fill="url(#ours)" stroke="#7E7254" stroke-width="1.3" '
               f'vector-effect="non-scaling-stroke"><path d="{" ".join(lit)}"/></g>')

    ax, ay = X(HOMES[0][2]), Y(HOMES[0][1])
    bx, by = X(HOMES[1][2]), Y(HOMES[1][1])
    mx, my = (ax + bx) / 2, (ay + by) / 2 - abs(bx - ax) * 0.45
    arc = f'M{ax:.1f},{ay:.1f} Q{mx:.1f},{my:.1f} {bx:.1f},{by:.1f}'
    svg.append(f'<path d="{arc}" fill="none" stroke="#8A3A33" stroke-width="7" '
               f'opacity=".12" filter="url(#warm)" vector-effect="non-scaling-stroke"/>')
    svg.append(f'<path class="flight" d="{arc}" fill="none" stroke="#8A3A33" '
               f'stroke-width="2.4" stroke-dasharray="3 11" stroke-linecap="round" '
               f'opacity=".95" vector-effect="non-scaling-stroke"/>')
    for p, colour, r in ([(q, "#2E4A57", 5) for q in PLACES] +
                         [(q, "#8A3A33", 7) for q in HOMES]):
        cx, cy = X(p[2]), Y(p[1])
        svg.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r*2.6:.1f}" fill="{colour}" '
                   f'opacity=".10"/>')
        svg.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r*1.7:.1f}" fill="none" '
                   f'stroke="{colour}" stroke-width="1" opacity=".4" '
                   f'vector-effect="non-scaling-stroke"/>')
        svg.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{colour}" '
                   f'stroke="#DCD4C4" stroke-width="1.6"/>')
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
           '<stop offset="0" stop-color="#8A3A33" stop-opacity=".07"/>'
           '<stop offset="1" stop-color="#8A3A33" stop-opacity="0"/>'
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
        f'r="{_r.choice([0.8, 1, 1.3]):.1f}" fill="#8A3A33" opacity="{_r.uniform(.1, .26):.2f}"/>'
        for _ in range(80))
    out.append(dust)

    out.append('<g stroke="#A89C80" stroke-width="1" stroke-linecap="round" opacity=".85">' +
               "".join(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}"/>'
                       for a, b in bones) + "</g>")

    # every joint gets a small star
    for x, y in stars:
        out.append(f'<g filter="url(#twinkle)"><circle cx="{x}" cy="{y}" r="2.6" '
                   f'fill="#8A3A33" opacity=".75"/></g>')

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
<title>Slimi</title>
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#E7E1D5">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,300..600;1,6..72,300..500&family=Courier+Prime:ital,wght@0,400;0,700;1,400&display=swap">
<style>
/* An album, not an interface. Warm paper, photographs printed on it,
   one serif used properly, typewriter for anything that came off a transcript. */
:root{
  --paper:#E7E1D5; --leaf:#DED7C9; --ink:#22201C; --soft:#6F6859; --faint:#9A9282;
  --rule:#C9C0AE; --deep:#2E4A57; --red:#8A3A33;
  --serif:'Newsreader',Georgia,'Times New Roman',serif;
  --type:'Courier Prime','Courier New',monospace;
  color-scheme:light;
}
*{box-sizing:border-box}
html,body{margin:0}
img{max-width:100%;display:block}
body{background:var(--paper);color:var(--ink);font-family:var(--serif);
  font-size:17.5px;line-height:1.62;font-optical-sizing:auto;
  -webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
::selection{background:var(--deep);color:var(--paper)}
:focus-visible{outline:2px solid var(--deep);outline-offset:3px}
a{color:var(--deep)}

.shell{max-width:1080px;margin:0 auto;padding-inline:clamp(20px,5vw,56px)}

/* ---- the plate at the head ---- */
.title{padding-block:clamp(44px,7vw,78px) clamp(14px,2vw,20px)}
.kicker{margin:0 0 clamp(16px,3vw,26px);font-family:var(--type);font-size:12.5px;
  color:var(--soft);letter-spacing:.01em}
h1{font-weight:300;font-size:clamp(50px,13vw,112px);line-height:.88;margin:0;
  letter-spacing:-.025em;max-width:11ch}
h1 .it{font-style:italic;display:block;color:var(--red);font-weight:300;
  margin-left:.09em}
.since,.apart{margin:0;font-family:var(--type);font-size:12.5px;color:var(--soft)}
.since{margin-top:clamp(22px,4vw,34px)}
.apart{margin-top:5px;color:var(--red)}
.apart b{font-weight:700}

/* ---- the song ---- */
.tune{padding-block:clamp(28px,4vw,42px)}
.tune .lead{margin:0 0 16px;font-style:italic;font-size:clamp(18px,3.4vw,23px);
  color:var(--ink);max-width:34ch}
.tune .frame{max-width:560px}
.tune .screen{position:relative;aspect-ratio:16/9;background:#1A1814;
  box-shadow:0 2px 0 rgba(34,32,28,.1),0 18px 38px -26px rgba(34,32,28,.6)}
.tune .screen iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
.tune .poster{position:absolute;inset:0;width:100%;height:100%;padding:0;border:0;
  cursor:pointer;background:#1A1814;display:grid;place-items:center}
.tune .poster img{width:100%;height:100%;object-fit:cover;opacity:.72;
  transition:opacity .3s}
.tune .poster:hover img{opacity:.9}
.tune .play{position:absolute;width:56px;height:56px;border-radius:50%;
  background:var(--paper);display:grid;place-items:center;color:var(--ink);
  font-size:17px;padding-left:4px}
.tune .bar{display:flex;align-items:baseline;gap:10px;padding:11px 1px 0;
  font-family:var(--type);font-size:12.5px;color:var(--soft)}
.tune .bar .t{font-family:var(--serif);font-size:17px;color:var(--ink)}
.tune .bar .cue{margin-left:auto;color:var(--red)}

/* ---- contents, not a tab bar ---- */
.tabs{position:sticky;top:0;z-index:20;background:var(--paper);
  border-bottom:1px solid var(--rule);padding-top:env(safe-area-inset-top,0px)}
.tabrow{position:relative;max-width:1080px;margin:0 auto;
  padding-inline:clamp(20px,5vw,56px);display:flex;gap:clamp(14px,3vw,30px);
  overflow-x:auto;scrollbar-width:none}
.tabrow::-webkit-scrollbar{display:none}
.tab{appearance:none;background:none;border:0;cursor:pointer;flex:none;
  font-family:var(--serif);font-size:16.5px;color:var(--soft);
  padding:15px 0 13px;white-space:nowrap;position:relative;
  transition:color .2s}
.tab:hover{color:var(--ink)}
.tab[aria-selected="true"]{color:var(--ink);font-style:italic}
.tab[aria-selected="true"]::after{content:"";position:absolute;left:0;right:0;
  bottom:-1px;height:2px;background:var(--red)}
.ink{display:none}

#stage{max-width:1080px;margin:0 auto;
  padding:clamp(34px,6vw,58px) clamp(20px,5vw,56px)
          calc(70px + env(safe-area-inset-bottom,0px))}
.panel{display:none}
.panel.on{display:block;animation:ease-in .5s ease both}
@keyframes ease-in{from{opacity:0}to{opacity:1}}
@media (prefers-reduced-motion:reduce){.panel.on{animation:none}}

/* ---- a reason, set like a page ---- */
.book-top{display:none}
.page{position:relative;min-height:clamp(230px,40vw,300px);
  display:flex;flex-direction:column;justify-content:center;
  padding-left:clamp(0px,8vw,96px)}
.leaf{display:block}
.leaf .num{font-family:var(--type);font-size:13px;color:var(--red);
  margin-bottom:clamp(14px,2.5vw,22px)}
.leaf .say{font-size:clamp(28px,6.4vw,52px);line-height:1.14;margin:0;
  font-weight:300;letter-spacing:-.015em;max-width:17ch;text-wrap:pretty}
.leaf .say em{font-style:normal;color:var(--red)}
.index .t em{font-style:normal;color:var(--red)}
.index a:hover .t em{color:var(--ink)}
.folio{display:none}
.page.out-fwd,.page.in-fwd,.page.out-back,.page.in-back{animation:none}
.page{transition:opacity .2s ease}
.page.fading{opacity:0}

.controls{display:flex;align-items:center;gap:22px;
  margin-top:clamp(34px,6vw,54px);padding-left:clamp(0px,8vw,96px)}
.controls button{appearance:none;background:none;border:0;cursor:pointer;
  font-family:var(--serif);font-size:21px;color:var(--soft);padding:4px 2px;
  transition:color .2s}
.controls button:hover{color:var(--red)}
.controls .shuffle{font-size:16.5px;font-style:italic;color:var(--deep)}
.controls .hint{margin-left:auto;font-family:var(--type);font-size:11.5px;
  color:var(--faint)}

/* ---- index ---- */
.index{margin-top:clamp(46px,8vw,78px);border-top:1px solid var(--rule)}
.index details{border:0}
.index summary{list-style:none;cursor:pointer;padding:20px 0;display:flex;
  align-items:baseline;gap:12px}
.index summary::-webkit-details-marker{display:none}
.index summary h2{font-weight:300;font-style:italic;font-size:clamp(21px,3.6vw,27px);
  margin:0}
.index summary .meta{margin-left:auto;font-family:var(--type);font-size:12px;
  color:var(--soft)}
.index details[open] summary .meta::after{content:"  \2212"}
.index details:not([open]) summary .meta::after{content:"  +"}
.index .panel-inner{padding-bottom:26px}
.index ol{list-style:none;margin:0;padding:0;columns:1;column-gap:clamp(30px,5vw,60px)}
@media (min-width:820px){.index ol{columns:2}}
.index li{break-inside:avoid}
.index a{display:flex;gap:13px;align-items:baseline;padding:7px 0;
  color:var(--ink);text-decoration:none;transition:color .16s}
.index a:hover{color:var(--red)}
.index .n{font-family:var(--type);font-size:11.5px;color:var(--faint);
  min-width:2.4em;text-align:right;flex:none}
.index a:hover .n{color:var(--red)}
.index .t{min-width:0;font-size:16px;line-height:1.4}

/* ---- photographs, printed ---- */
.plate{margin:0;cursor:pointer;position:relative;background:var(--leaf);
  padding:clamp(12px,2.4vw,20px) clamp(12px,2.4vw,20px) clamp(42px,6vw,56px);
  box-shadow:0 1px 0 rgba(34,32,28,.08),0 24px 46px -34px rgba(34,32,28,.5)}
.plate img{width:100%;height:min(66svh,660px);object-fit:cover;
  transition:opacity .26s ease;background:var(--rule)}
@media (max-width:620px){.plate img{height:min(56svh,470px)}}
.plate img.swapping{opacity:.2}
.tally{position:absolute;left:clamp(12px,2.4vw,20px);right:clamp(12px,2.4vw,20px);
  bottom:clamp(14px,2.2vw,20px);margin:0;display:flex;justify-content:space-between;
  align-items:baseline;font-family:var(--type);font-size:11.5px;color:var(--soft);
  pointer-events:none}
.tally .tap{color:var(--faint)}
.shotnav{display:flex;gap:26px;margin-top:22px;padding-left:clamp(12px,2.4vw,20px)}
.shotnav button{appearance:none;background:none;border:0;cursor:pointer;
  font-family:var(--serif);font-size:21px;color:var(--soft);padding:2px;
  transition:color .2s}
.shotnav button:hover{color:var(--red)}

/* ---- headings in the quieter panels ---- */
.atlas-top{display:flex;align-items:baseline;gap:14px;flex-wrap:wrap;
  margin-bottom:clamp(20px,3.4vw,30px)}
.atlas-top h2{font-weight:300;font-style:italic;font-size:clamp(23px,4.2vw,32px);
  margin:0}
.atlas-top.spaced{margin-top:clamp(52px,8vw,86px)}
.atlas-top .gap{margin-left:auto;font-family:var(--type);font-size:clamp(15px,2.6vw,19px);
  color:var(--red);text-align:right;line-height:1.25}
.atlas-top .gap small{display:block;font-size:11px;color:var(--soft)}
.panel .sub{margin:0 0 18px;color:var(--soft);font-size:15.5px;max-width:50ch}

/* ---- three years ---- */
.tl{list-style:none;margin:0;padding:0}
.tl li{display:grid;grid-template-columns:clamp(74px,13vw,118px) 1fr;
  gap:clamp(14px,3vw,28px);padding:15px 0;border-top:1px solid var(--rule)}
.tl li:last-child{border-bottom:1px solid var(--rule)}
.tl .when{font-family:var(--type);font-size:11.5px;color:var(--soft);padding-top:7px}
.tl .dot{display:none}
.tl .what{min-width:0;font-size:14.5px;color:var(--soft);line-height:1.5}
.tl .what b{display:block;font-family:var(--serif);font-weight:300;
  font-size:clamp(21px,3.8vw,29px);color:var(--ink);line-height:1.15;
  margin-bottom:4px;letter-spacing:-.01em}

/* ---- the map ---- */
.mapfig{margin:0}
.plot{position:relative;width:100%;aspect-ratio:16/8.3;background:#DCD4C4}
@media (max-width:620px){.plot{aspect-ratio:16/11}}
.plot svg{position:absolute;inset:0;width:100%;height:100%}
.plot::after{display:none}
.pin{position:absolute;font-family:var(--type);font-size:clamp(9.5px,1.3vw,12px);
  white-space:nowrap;pointer-events:none;line-height:1;color:var(--soft)}
.pin.home{color:var(--red)}
.pin.left{transform:translate(calc(-100% - 11px),-50%)}
.pin.right{transform:translate(11px,-50%)}
.pin.below{transform:translate(-50%,15px)}
.pin.above{transform:translate(-50%,calc(-100% - 12px))}
.pin.gap{font-family:var(--serif);font-style:italic;
  font-size:clamp(14px,2.4vw,22px);transform:translate(-50%,-50%);color:var(--red)}
@media (prefers-reduced-motion:no-preference){
  .flight{animation:fly 11s linear infinite}
  @keyframes fly{to{stroke-dashoffset:-140}}}
.legend{display:flex;gap:22px;flex-wrap:wrap;margin:14px 0 0;
  font-family:var(--type);font-size:11.5px;color:var(--soft)}
.legend i{width:7px;height:7px;border-radius:50%;display:inline-block;
  margin-right:7px;vertical-align:1px}

.clocks{display:flex;align-items:flex-end;gap:clamp(26px,6vw,56px);
  margin-top:clamp(28px,5vw,44px);flex-wrap:wrap}
.clock .city{margin:0;font-family:var(--type);font-size:11.5px;color:var(--soft)}
.clock .now{margin:3px 0 1px;font-family:var(--type);font-weight:700;
  font-size:clamp(26px,5.4vw,38px);line-height:1;color:var(--ink)}
.clock .zone{margin:0;font-family:var(--type);font-size:11px;color:var(--faint)}
.apartby{margin:0 0 3px;font-style:italic;font-size:14.5px;color:var(--red)}

/* ---- her dictionary ---- */
.tallyline{margin:0 0 clamp(20px,3.4vw,30px);font-family:var(--type);
  font-size:12.5px;color:var(--soft);max-width:46ch;line-height:1.7}
.lex{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:1fr}
@media (min-width:780px){.lex{grid-template-columns:1fr 1fr;
  column-gap:clamp(32px,5vw,64px)}}
.lex li{display:grid;grid-template-columns:1fr auto;column-gap:14px;row-gap:2px;
  align-items:baseline;padding:13px 0;border-top:1px solid var(--rule)}
.lex .w{font-size:clamp(20px,3.6vw,26px);font-weight:300;letter-spacing:-.01em}
.lex .c{font-family:var(--type);font-size:13px;color:var(--red)}
.lex .g{grid-column:1/-1;font-size:13.5px;color:var(--soft);line-height:1.5;
  font-style:italic}

/* ---- open when ---- */
.envs{display:grid}
.env{border:0;border-top:1px solid var(--rule)}
.env:last-child{border-bottom:1px solid var(--rule)}
.env summary{list-style:none;cursor:pointer;padding:17px 0;
  font-size:clamp(19px,3.4vw,25px);font-weight:300;display:flex;
  align-items:baseline;gap:11px;transition:color .18s}
.env summary::-webkit-details-marker{display:none}
.env summary:hover{color:var(--red)}
.env .seal{color:var(--red);font-size:12px}
.env[open] summary{font-style:italic;padding-bottom:3px}
.env p{margin:0;padding:0 0 20px 25px;font-style:italic;
  font-size:clamp(16px,3vw,20px);line-height:1.5;color:var(--soft);max-width:48ch}

/* ---- what you are made of ---- */
.fig{display:flex;gap:clamp(24px,5vw,62px);align-items:center;flex-wrap:wrap;
  background:none;border:0;padding:0}
.figwrap{flex:0 0 auto;width:clamp(170px,30vw,240px);margin:0 auto}
.figsvg{display:block;width:100%;height:auto;overflow:visible}
.figsvg .node{fill:var(--red);fill-opacity:0;stroke:var(--red);stroke-width:1;
  stroke-opacity:.2;cursor:pointer;transition:fill-opacity .22s,stroke-opacity .22s}
.figsvg .node:hover{fill-opacity:.12;stroke-opacity:.6}
.figsvg .node.on{fill-opacity:.3;stroke-opacity:1}
.figsay{flex:1 1 250px;min-width:0}
.figsay .what{font-style:italic;font-size:clamp(23px,4.4vw,34px);color:var(--red);
  margin:0 0 5px;line-height:1.1;font-weight:300}
.figsay .why{font-size:clamp(17px,3.2vw,23px);margin:0 0 24px;line-height:1.35;
  color:var(--ink);font-weight:300}
.chips{display:flex;flex-wrap:wrap;gap:4px 16px}
.chip{font-family:var(--type);font-size:11.5px;color:var(--faint);background:none;
  border:0;padding:3px 0;cursor:pointer;transition:color .16s}
.chip:hover,.chip.on{color:var(--red)}

/* ---- theo ---- */
.theowrap{display:flex;flex-direction:column;align-items:center;
  gap:clamp(26px,4.5vw,42px);background:none;border:0;padding:0;
  max-width:620px;margin:0 auto;text-align:center}
.film{margin:0;width:100%;background:var(--leaf);
  padding:clamp(12px,2.2vw,18px) clamp(12px,2.2vw,18px) clamp(34px,4.5vw,46px);
  box-shadow:0 1px 0 rgba(34,32,28,.08),0 26px 50px -34px rgba(34,32,28,.55)}
.film video{width:100%;height:auto;max-height:68svh;object-fit:contain;
  background:#1A1814}
.paw{width:30px;color:var(--red);margin:0 auto 14px}
.paw svg{width:100%;height:auto}
.pupsay{max-width:44ch}
.pupsay h2{font-weight:300;font-style:italic;font-size:clamp(25px,4.6vw,36px);
  margin:0 0 9px}
.pupsay p{margin:0;color:var(--soft);font-size:16px;line-height:1.6}

/* ---- say something ---- */
textarea{width:100%;background:var(--leaf);border:0;border-left:2px solid var(--rule);
  color:var(--ink);font-family:var(--serif);font-size:17px;line-height:1.6;
  padding:16px 18px;resize:vertical}
textarea::placeholder{color:var(--faint);font-style:italic}
.postrow{display:flex;align-items:center;gap:22px;margin-top:16px;flex-wrap:wrap}
.postrow button{font-family:var(--serif);font-style:italic;font-size:17px;
  color:var(--deep);background:none;border:0;padding:0;cursor:pointer}
.postrow button:hover{color:var(--red)}
.postrow a{color:var(--soft);font-size:15px;text-decoration:none;font-style:italic}
.postrow a:hover{color:var(--red)}
.postrow .said{font-family:var(--type);font-size:11.5px;color:var(--faint)}

/* ---- the gate ---- */
#gate{position:fixed;inset:0;z-index:50;background:var(--paper);display:grid;
  place-items:center;padding:30px}
#gate[hidden]{display:none}
#gate .box{width:100%;max-width:440px}
#gate .mark{font-size:26px;color:var(--red);margin:0 0 30px}
#gate p.q{font-size:clamp(30px,6.4vw,44px);line-height:1.05;margin:0 0 16px;
  font-weight:300;letter-spacing:-.025em}
#gate .clue{margin:0 0 32px;font-size:clamp(17px,3.2vw,21px);font-style:italic;
  color:var(--soft);line-height:1.4;text-wrap:pretty}
#gate .clue span{display:block;font-family:var(--type);font-style:normal;
  font-size:11.5px;color:var(--red);margin-bottom:6px}
#gate form{display:flex;flex-direction:column;gap:16px;align-items:flex-start}
#gate input{width:100%;font-family:var(--serif);font-size:19px;color:var(--ink);
  background:none;border:0;border-bottom:1px solid var(--rule);padding:9px 2px}
#gate input::placeholder{color:var(--faint);font-style:italic}
#gate input:focus{outline:0;border-bottom-color:var(--red)}
#gate button{font-family:var(--serif);font-style:italic;font-size:18px;
  color:var(--deep);background:none;border:0;padding:0;cursor:pointer}
#gate button:hover{color:var(--red)}
#gate .no{min-height:20px;font-family:var(--type);font-size:12px;color:var(--red);
  margin:10px 0 0}
body.locked{overflow:hidden}

footer{border-top:1px solid var(--rule);max-width:1080px;margin:0 auto;
  padding:26px clamp(20px,5vw,56px) calc(46px + env(safe-area-inset-bottom,0px));
  display:flex;justify-content:space-between;align-items:baseline;gap:16px;
  font-family:var(--type);font-size:11.5px;color:var(--faint)}
footer .mark{color:var(--red);font-size:13px}
</style>
</head>
<body>

<div id="gate" hidden>
  <div class="box">
    <p class="mark">&#9829;</p>
    <p class="q">Password</p>
    <p class="clue"><span>Hint</span>__HINT__</p>
    <form id="gateForm" autocomplete="off">
      <input id="gateInput" type="text" placeholder="Type it here" aria-label="Password"
             autocapitalize="off" autocorrect="off" spellcheck="false">
      <button type="submit">Open</button>
    </form>
    <p class="no" id="gateNo" role="status"></p>
  </div>
</div>

<div class="title shell">
  <p class="kicker">To Slimi, from Sufi, with love</p>
  <h1>Reasons<span class="it">why I love you</span></h1>
  <p class="since" id="since"></p>
  <p class="apart" id="apart"></p>
</div>

<section class="tune shell">
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

<nav class="tabs" id="tabs" aria-label="Sections">
  <div class="tabrow">
    <button type="button" class="tab" data-panel="p-reasons">Reasons</button>
    <button type="button" class="tab" data-panel="p-photos">Photos</button>
    <button type="button" class="tab" data-panel="p-years">Three years</button>
    <button type="button" class="tab" data-panel="p-map">Where we are</button>
    <button type="button" class="tab" data-panel="p-words">Your words</button>
    <button type="button" class="tab" data-panel="p-you">You</button>
    <button type="button" class="tab" data-panel="p-letters">Open when</button>
    <button type="button" class="tab" data-panel="p-theo">Theo</button>
    <button type="button" class="tab" data-panel="p-say">Say something</button>
    <span class="ink" id="ink" aria-hidden="true"></span>
  </div>
</nav>

<main id="stage">

<div class="panel" id="p-reasons" role="tabpanel">
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
      <summary><h2>All of them</h2><span class="meta">__COUNT__</span></summary>
      <div class="panel-inner">
        <ol>
__ROWS__
        </ol>
      </div>
    </details>
  </section>
</div>

<div class="panel" id="p-photos" role="tabpanel">
  <figure class="plate">
    __HERO__
    <figcaption class="tally">
      <span id="tally"></span><span class="tap">tap for the next</span>
    </figcaption>
  </figure>
  <div class="shotnav">
    <button type="button" id="shotPrev" aria-label="Previous photo">&#8592;</button>
    <button type="button" id="shotNext" aria-label="Next photo">&#8594;</button>
  </div>
</div>

<div class="panel" id="p-years" role="tabpanel">
  <div class="atlas-top"><h2>Three years</h2></div>
  <ol class="tl">
__TIMELINE__
  </ol>
</div>

<div class="panel" id="p-map" role="tabpanel">
  <div class="atlas-top">
    <h2>Where we are</h2>
    <div class="gap">__APART__ km<small>apart</small></div>
  </div>
  <figure class="mapfig">__CHART__</figure>
  <p class="legend">
    <span><i style="background:#8A3A33"></i>The two of us</span>
    <span><i style="background:#2E4A57"></i>Everywhere we went together</span>
  </p>
  <div class="clocks">
    <div class="clock"><p class="city">Paris</p><p class="now" id="clkParis">&mdash;</p>
      <p class="zone" id="zParis"></p></div>
    <div class="clock"><p class="city">Amman</p><p class="now" id="clkAmman">&mdash;</p>
      <p class="zone" id="zAmman"></p></div>
    <p class="apartby" id="apartBy"></p>
  </div>
</div>

<div class="panel" id="p-words" role="tabpanel">
  <div class="atlas-top"><h2>How you talk</h2></div>
  __LEXICON__
</div>

<div class="panel" id="p-you" role="tabpanel">
  <div class="atlas-top"><h2>What you are made of</h2></div>
  __FIGURE__
</div>

<div class="panel" id="p-letters" role="tabpanel">
  <div class="atlas-top"><h2>Open when&hellip;</h2></div>
  <p class="sub">Ten of them. Each one opens.</p>
  <div class="envs">
__LETTERS__
  </div>
</div>

<div class="panel" id="p-theo" role="tabpanel">
  <div class="theowrap">
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
  </div>
</div>

<div class="panel" id="p-say" role="tabpanel">
  <div class="atlas-top"><h2>Say something back</h2></div>
  <p class="sub">Write it here, then send it to me. Nothing on this page can reach
    me on its own.</p>
  <textarea id="note" rows="6" placeholder="Whatever you want."></textarea>
  <div class="postrow">
    <button type="button" id="copyNote">Copy it</button>
    <a id="mailNote" href="#">Open it in mail</a>
    <span class="said" id="said" role="status"></span>
  </div>
</div>

</main>

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
  var LAST    = "__LAST__";
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
    say.innerHTML = reasons[at];
    folio.textContent = (at + 1) + ' ⁄ ' + reasons.length;
    label.textContent = (at === today && !picked) ? 'Today' : 'One of them';
  }

  function turn(i, dir, picked) {
    if (busy) { return; }
    if (reduce || dir === 0) { paintLeaf(i, picked); return; }
    busy = true;
    page.classList.add('fading');
    setTimeout(function () {
      paintLeaf(i, picked);
      page.classList.remove('fading');
      busy = false;
    }, 190);
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

  /* ---------- since the last time ---------- */
  var apartEl = document.getElementById('apart');
  if (apartEl) {
    var since = Date.parse(LAST);
    function tick() {
      var ms = Date.now() - since;
      if (ms < 0) { apartEl.textContent = ''; return; }
      var d = Math.floor(ms / 86400000);
      var h = Math.floor(ms / 3600000) % 24;
      var m = Math.floor(ms / 60000) % 60;
      var sec = Math.floor(ms / 1000) % 60;
      apartEl.innerHTML = 'Since Marbella, 18 August \u2014 <b>' + d + '</b> days, '
        + h + 'h ' + m + 'm ' + sec + 's';
    }
    tick();
    setInterval(tick, 1000);
  }

  /* ---------- #47 opens on 47 ---------- */
  function fromHash() {
    var n = parseInt((location.hash || '').slice(1), 10);
    if (n >= 1 && n <= reasons.length) {
      openPanel('p-reasons', false);
      paintLeaf(n - 1, true);
    }
  }
  window.addEventListener('hashchange', fromHash);

  document.querySelectorAll('.index a').forEach(function (a) {
    a.addEventListener('click', function (e) {
      e.preventDefault();
      var n = parseInt(a.getAttribute('href').slice(1), 10);
      history.replaceState(null, '', '#' + n);
      turn(n - 1, n - 1 > at ? 1 : -1, true);
      var det = document.getElementById('allOfThem');
      if (det) det.open = false;
      document.querySelector('.book').scrollIntoView({ block: 'center', behavior: 'smooth' });
    });
  });

  /* ---------- photographs ---------- */
  var hero = document.getElementById('hero');
  var tally = document.getElementById('tally');
  var shot = 0;
  function preloadNeighbours() {}
  if (hero && photos.length) {
    shot = Math.floor(Math.random() * photos.length);
    preloadNeighbours = function () {
      [1, -1].forEach(function (d) {
        var k = (shot + d + photos.length) % photos.length;
        var im = new Image(); im.src = 'photos/' + photos[k];
      });
    };
    function paintHero(i) {
      shot = (i + photos.length) % photos.length;
      hero.classList.add('swapping');
      var loader = new Image();
      loader.onload = loader.onerror = function () {
        hero.src = loader.src;
        hero.classList.remove('swapping');
        preloadNeighbours();
      };
      loader.src = 'photos/' + photos[shot];
      if (tally) tally.textContent = (shot + 1) + ' / ' + photos.length;
    }
    var plate = document.querySelector('.plate');
    if (plate) plate.addEventListener('click', function () { paintHero(shot + 1); });
    var sp = document.getElementById('shotPrev');
    var sn = document.getElementById('shotNext');
    if (sp) sp.addEventListener('click', function () { paintHero(shot - 1); });
    if (sn) sn.addEventListener('click', function () { paintHero(shot + 1); });
    var px = null;
    if (plate) {
      plate.addEventListener('touchstart', function (e) {
        px = e.changedTouches[0].clientX;
      }, { passive: true });
      plate.addEventListener('touchend', function (e) {
        if (px === null) return;
        var dx = e.changedTouches[0].clientX - px;
        if (Math.abs(dx) > 48) paintHero(shot + (dx < 0 ? 1 : -1));
        px = null;
      }, { passive: true });
    }
    hero.src = 'photos/' + photos[shot];
    if (tally) tally.textContent = (shot + 1) + ' / ' + photos.length;
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

  /* ---------- tabs ---------- */
  var tabs = Array.prototype.slice.call(document.querySelectorAll('.tab'));
  var ink = document.getElementById('ink');
  var row = document.querySelector('.tabrow');
  var current = null;

  function slideInk(btn) {
    if (!ink || !btn) return;
    ink.style.width = btn.offsetWidth + 'px';
    ink.style.transform = 'translateX(' + btn.offsetLeft + 'px)';
  }

  function openPanel(id, push) {
    tabs.forEach(function (t) {
      var on = t.dataset.panel === id;
      t.setAttribute('aria-selected', on ? 'true' : 'false');
      if (on) {
        slideInk(t);
        if (row) {
          var want = t.offsetLeft - (row.clientWidth - t.offsetWidth) / 2;
          row.scrollTo({ left: Math.max(0, want), behavior: 'smooth' });
        }
      }
    });
    document.querySelectorAll('.panel').forEach(function (pn) {
      pn.classList.toggle('on', pn.id === id);
    });
    current = id;
    if (push) {
      try { history.replaceState(null, '', '#' + id.replace('p-', '')); } catch (e) {}
    }
    if (id === 'p-photos') { try { preloadNeighbours(); } catch (e) {} }
  }

  tabs.forEach(function (t) {
    t.setAttribute('role', 'tab');
    t.addEventListener('click', function () { openPanel(t.dataset.panel, true); });
  });
  window.addEventListener('resize', function () {
    var on = document.querySelector('.tab[aria-selected="true"]');
    if (on) slideInk(on);
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

  var wanted = (location.hash || '').slice(1);
  var known = tabs.map(function (t) { return t.dataset.panel.replace('p-', ''); });
  if (known.indexOf(wanted) !== -1) {
    openPanel('p-' + wanted, false);
  } else {
    openPanel('p-reasons', false);
    if (location.hash && location.hash !== '#lock') fromHash();
  }
  requestAnimationFrame(function () {
    var on = document.querySelector('.tab[aria-selected="true"]');
    if (on) slideInk(on);
  });
})();
</script>
</body>
</html>
"""

out = (
    TEMPLATE.replace("__ROWS__", index_rows)
    .replace("__HERO__", hero_img)
    .replace("__REASONS__", json.dumps([lit(t) for t in reasons], ensure_ascii=False))
    .replace("__PHOTOS__", json.dumps(photos, ensure_ascii=False))
    .replace("__START__", START)
    .replace("__LAST__", LAST)
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
    .replace("__COUNT__", str(len(reasons)))
    .replace("__FIRST__", lit(reasons[0]))
)
(SITE / "index.html").write_text(out, "utf-8")
print(f"built site/index.html - {len(reasons)} reasons, {len(photos)} photos")
