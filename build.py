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
    ("Los Angeles", 34.0736, -118.4004, "right"),
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


def chart():
    """The two of you and everywhere you went, plotted to scale.

    Latitude is stretched so the panel is a usable shape on a phone; the
    relative positions and the ordering are true.
    """
    pts = HOMES + PLACES
    lons = [p[2] for p in pts]; lats = [p[1] for p in pts]
    x0, x1 = min(lons) - 22, max(lons) + 22
    y0, y1 = min(lats) - 7, max(lats) + 9

    def X(lon): return (lon - x0) / (x1 - x0) * 100.0      # percent
    def Y(lat): return (y1 - lat) / (y1 - y0) * 100.0

    W, H = 1000.0, 520.0                                   # viewBox, 16:8.3
    sx, sy = W / 100.0, H / 100.0

    svg = [f'<svg viewBox="0 0 {W:.0f} {H:.0f}" preserveAspectRatio="none" '
           f'aria-hidden="true" xmlns="http://www.w3.org/2000/svg">']
    g = []
    lon = -180
    while lon <= 180:
        if x0 < lon < x1:
            g.append(f'<line x1="{X(lon)*sx:.1f}" y1="0" x2="{X(lon)*sx:.1f}" y2="{H:.0f}"/>')
        lon += 20
    lat = -80
    while lat <= 80:
        if y0 < lat < y1:
            g.append(f'<line x1="0" y1="{Y(lat)*sy:.1f}" x2="{W:.0f}" y2="{Y(lat)*sy:.1f}"/>')
        lat += 10
    svg.append('<g stroke="#232020" stroke-width="1.2">' + "".join(g) + '</g>')

    ax, ay = X(HOMES[0][2]) * sx, Y(HOMES[0][1]) * sy
    bx, by = X(HOMES[1][2]) * sx, Y(HOMES[1][1]) * sy
    mx, my = (ax + bx) / 2, (ay + by) / 2 - abs(bx - ax) * 0.42
    svg.append(f'<path d="M{ax:.1f},{ay:.1f} Q{mx:.1f},{my:.1f} {bx:.1f},{by:.1f}" '
               f'fill="none" stroke="#C7A75F" stroke-width="2.5" stroke-dasharray="4 10" '
               f'opacity=".8" vector-effect="non-scaling-stroke"/>')
    for p, colour, r in ([(p, "#7EA8B8", 7) for p in PLACES] +
                         [(p, "#C7A75F", 11) for p in HOMES]):
        svg.append(f'<circle cx="{X(p[2])*sx:.1f}" cy="{Y(p[1])*sy:.1f}" r="{r}" '
                   f'fill="{colour}" fill-opacity=".95"/>')
    svg.append('</svg>')

    # labels are real text, so they stay readable at any width
    tags = []
    for p, cls in ([(p, "there") for p in PLACES] + [(p, "home") for p in HOMES]):
        label, lat_, lon_, side = p
        tags.append(f'<span class="pin {cls} {side}" '
                    f'style="left:{X(lon_):.2f}%;top:{Y(lat_):.2f}%">'
                    f'{html.escape(label)}</span>')
    arc = (f'<span class="pin gap" style="left:{(X(HOMES[0][2])+X(HOMES[1][2]))/2:.2f}%;'
           f'top:{min(Y(HOMES[0][1]),Y(HOMES[1][1])) - 13:.2f}%">{APART:,} km</span>')
    return '<div class="plot">' + "".join(svg) + "".join(tags) + arc + '</div>'


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
.tune{max-width:820px;margin:0 auto;padding:0 24px clamp(44px,8vw,78px)}
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
.atlas{max-width:1120px;margin:0 auto;padding:0 24px clamp(44px,8vw,78px)}
.atlas-top{display:flex;align-items:baseline;gap:14px;margin-bottom:20px;flex-wrap:wrap}
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

<header class="plate">
  __HERO__
  <p class="tally"><span id="tally"></span><span class="tap">tap for the next</span></p>
</header>

<div class="title">
  <p class="kicker">For Selma</p>
  <h1>One hundred<span class="it">reasons</span></h1>
  <p class="since" id="since"></p>
</div>

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

<section class="tune">
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

<section class="atlas">
  <div class="atlas-top">
    <h2>Where we are</h2>
    <div class="gap">__APART__ km<small>apart</small></div>
  </div>
  <figure>__CHART__</figure>
  <p class="legend">
    <span><i style="background:#C7A75F"></i>The two of us</span>
    <span><i style="background:#7EA8B8"></i>Places we went together</span>
  </p>
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
    .replace("__ANSWERS__", json.dumps(ANSWERS))
    .replace("__FIRST__", html.escape(reasons[0]))
)
(SITE / "index.html").write_text(out, "utf-8")
print(f"built site/index.html - {len(reasons)} reasons, {len(photos)} photos")
