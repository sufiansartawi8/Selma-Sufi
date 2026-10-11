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

strip = "\n".join(
    f'      <button type="button" class="thumb" data-i="{i}" aria-label="Photo {i + 1}">'
    f'<img src="photos/{html.escape(p)}" alt="" loading="lazy" decoding="async"></button>'
    for i, p in enumerate(photos)
)

hero_img = (
    f'<img id="hero" src="photos/{html.escape(photos[0])}" alt="Us">' if photos else ""
)

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

/* ---- hero ---- */
.hero{position:relative;min-height:62svh;display:flex;align-items:flex-end;
  overflow:hidden;background:var(--raise)}
.hero img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;
  filter:saturate(.92) contrast(1.04)}
.hero::after{content:"";position:absolute;inset:0;
  background:linear-gradient(to top,var(--bg) 2%,rgba(19,17,16,.82) 32%,rgba(19,17,16,.18) 68%,rgba(19,17,16,.45))}
.hero .inner{position:relative;z-index:1;width:100%;max-width:980px;margin:0 auto;
  padding:0 24px calc(40px + env(safe-area-inset-bottom,0px));
  padding-top:calc(48px + env(safe-area-inset-top,0px))}
.kicker{font-size:11px;letter-spacing:.3em;text-transform:uppercase;color:var(--brass);
  margin:0 0 14px;font-weight:600}
h1{font-family:var(--display);font-weight:400;font-size:clamp(46px,13vw,104px);
  line-height:.92;margin:0;letter-spacing:-.02em}
h1 .it{font-style:italic;display:block;color:var(--brass)}
.since{margin:18px 0 0;font-size:13.5px;color:var(--dim);
  font-variant-numeric:tabular-nums}

/* ---- the one ---- */
.deck{max-width:760px;margin:0 auto;padding:clamp(48px,9vw,86px) 24px}
.deck-top{display:flex;align-items:baseline;gap:14px;margin-bottom:26px}
.deck-top .label{font-size:11px;letter-spacing:.28em;text-transform:uppercase;
  color:var(--faint);font-weight:600}
.deck-top .line{flex:1;height:1px;background:var(--rule)}
.card{min-height:clamp(180px,34vw,240px);display:flex;gap:clamp(18px,4vw,34px);
  align-items:flex-start}
.card .num{font-family:var(--display);font-size:clamp(52px,13vw,92px);line-height:.82;
  color:var(--brass);font-variant-numeric:lining-nums tabular-nums;flex:none;
  opacity:.9}
.card .say{font-family:var(--display);font-size:clamp(23px,5.4vw,36px);line-height:1.22;
  margin:0;min-width:0;padding-top:.12em;text-wrap:pretty}
.card.turn .num,.card.turn .say{animation:turn .32s ease-out}
@keyframes turn{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
@media (prefers-reduced-motion:reduce){.card.turn .num,.card.turn .say{animation:none}}

.controls{display:flex;align-items:center;gap:8px;margin-top:34px;
  padding-top:20px;border-top:1px solid var(--rule)}
.controls button{appearance:none;background:none;border:1px solid var(--rule);
  color:var(--ink);font-family:var(--ui);font-size:14px;font-weight:500;
  width:44px;height:44px;border-radius:50%;cursor:pointer;
  display:grid;place-items:center;transition:border-color .18s,color .18s}
.controls button:hover{border-color:var(--brass);color:var(--brass)}
.controls .count{margin-left:auto;font-size:12.5px;color:var(--faint);
  letter-spacing:.1em;font-variant-numeric:tabular-nums}
.controls .shuffle{width:auto;padding:0 20px;border-radius:999px;letter-spacing:.02em}

/* ---- film strip ---- */
.strip{display:flex;gap:10px;overflow-x:auto;padding:0 24px clamp(40px,8vw,72px);
  max-width:1120px;margin:0 auto;scroll-snap-type:x proximity;
  scrollbar-width:thin;scrollbar-color:var(--rule) transparent}
.thumb{flex:none;width:clamp(92px,24vw,132px);aspect-ratio:1;padding:0;border:0;
  background:var(--raise);border-radius:3px;overflow:hidden;cursor:pointer;
  scroll-snap-align:start;opacity:.46;transition:opacity .22s}
.thumb img{width:100%;height:100%;object-fit:cover}
.thumb:hover,.thumb[aria-current="true"]{opacity:1}

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

footer{border-top:1px solid var(--rule);max-width:1120px;margin:0 auto;
  padding:34px 24px calc(50px + env(safe-area-inset-bottom,0px));
  display:flex;justify-content:space-between;align-items:center;gap:16px;
  font-size:12.5px;color:var(--faint);letter-spacing:.04em}
footer .mark{color:var(--brass);font-size:15px}
</style>
</head>
<body>

<header class="hero">
  __HERO__
  <div class="inner">
    <p class="kicker">For Selma</p>
    <h1>One hundred<span class="it">reasons</span></h1>
    <p class="since" id="since"></p>
  </div>
</header>

<section class="deck">
  <div class="deck-top"><span class="label" id="deckLabel">Today</span><span class="line"></span></div>
  <div class="card" id="card">
    <div class="num" id="num">1</div>
    <p class="say" id="say">__FIRST__</p>
  </div>
  <div class="controls">
    <button type="button" id="prev" aria-label="Previous reason">&#8592;</button>
    <button type="button" id="next" aria-label="Next reason">&#8594;</button>
    <button type="button" id="shuffle" class="shuffle">Surprise me</button>
    <span class="count" id="count"></span>
  </div>
</section>

<div class="strip" id="strip">
__STRIP__
</div>

<section class="index">
  <h2>All of them</h2>
  <p class="sub">In order. Tap any one to bring it up above.</p>
  <ol>
__ROWS__
  </ol>
</section>

<footer>
  <span>Still true</span>
  <span class="mark">&#9829;</span>
</footer>

<script>
(function () {
  var reasons = __REASONS__;
  var photos  = __PHOTOS__;
  var START   = "__START__";

  var num = document.getElementById('num');
  var say = document.getElementById('say');
  var card = document.getElementById('card');
  var count = document.getElementById('count');
  var label = document.getElementById('deckLabel');

  var today = Math.floor(Date.now() / 86400000) % reasons.length;
  var at = today;

  function show(i, how) {
    at = (i + reasons.length) % reasons.length;
    num.textContent = at + 1;
    say.textContent = reasons[at];
    count.textContent = (at + 1) + ' of ' + reasons.length;
    label.textContent = (at === today && how !== 'picked') ? 'Today' : 'One of them';
    card.classList.remove('turn');
    void card.offsetWidth;
    card.classList.add('turn');
  }

  // days together, counted from the first trip
  var since = document.getElementById('since');
  var days = Math.floor((Date.now() - Date.parse(START)) / 86400000);
  var started = new Date(START).toLocaleDateString('en-GB',
    { day: 'numeric', month: 'long', year: 'numeric' });
  since.textContent = started + ' — ' + days.toLocaleString() + ' days ago';

  document.getElementById('prev').addEventListener('click', function () { show(at - 1, 'picked'); });
  document.getElementById('next').addEventListener('click', function () { show(at + 1, 'picked'); });
  document.getElementById('shuffle').addEventListener('click', function () {
    var n = at;
    while (n === at && reasons.length > 1) n = Math.floor(Math.random() * reasons.length);
    show(n, 'picked');
  });

  document.addEventListener('keydown', function (e) {
    if (e.target.closest('input,textarea')) return;
    if (e.key === 'ArrowLeft') show(at - 1, 'picked');
    if (e.key === 'ArrowRight') show(at + 1, 'picked');
  });

  // swipe the card on a phone
  var x0 = null;
  card.addEventListener('touchstart', function (e) { x0 = e.changedTouches[0].clientX; }, { passive: true });
  card.addEventListener('touchend', function (e) {
    if (x0 === null) return;
    var dx = e.changedTouches[0].clientX - x0;
    if (Math.abs(dx) > 48) show(at + (dx < 0 ? 1 : -1), 'picked');
    x0 = null;
  }, { passive: true });

  // #47 in the URL opens on that reason
  function fromHash() {
    var n = parseInt((location.hash || '').slice(1), 10);
    if (n >= 1 && n <= reasons.length) show(n - 1, 'picked');
  }
  window.addEventListener('hashchange', fromHash);

  document.querySelectorAll('.index a').forEach(function (a) {
    a.addEventListener('click', function (e) {
      e.preventDefault();
      var n = parseInt(a.getAttribute('href').slice(1), 10);
      history.replaceState(null, '', '#' + n);
      show(n - 1, 'picked');
      document.querySelector('.deck').scrollIntoView({ block: 'center' });
    });
  });

  // film strip swaps the photograph at the top
  var hero = document.getElementById('hero');
  if (hero && photos.length) {
    var thumbs = Array.prototype.slice.call(document.querySelectorAll('.thumb'));
    var shown = Math.floor(Math.random() * photos.length);
    function paint(i) {
      shown = i;
      hero.src = 'photos/' + photos[i];
      thumbs.forEach(function (t, k) { t.setAttribute('aria-current', k === i ? 'true' : 'false'); });
    }
    thumbs.forEach(function (t) {
      t.addEventListener('click', function () { paint(+t.dataset.i); });
    });
    paint(shown);
  }

  show(at);
  if (location.hash) fromHash();
})();
</script>
</body>
</html>
"""

out = (
    TEMPLATE.replace("__ROWS__", index_rows)
    .replace("__STRIP__", strip)
    .replace("__HERO__", hero_img)
    .replace("__REASONS__", json.dumps(reasons, ensure_ascii=False))
    .replace("__PHOTOS__", json.dumps(photos, ensure_ascii=False))
    .replace("__START__", START)
    .replace("__FIRST__", html.escape(reasons[0]))
)
(SITE / "index.html").write_text(out, "utf-8")
print(f"built site/index.html - {len(reasons)} reasons, {len(photos)} photos")
