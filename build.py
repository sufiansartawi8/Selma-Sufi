#!/usr/bin/env python3
"""Build site/index.html from reasons.md and whatever is in site/photos/.

Edit reasons.md, drop photos into site/photos/, then run:  python3 build.py

Photos need no manifest and no naming scheme. Every image in the folder is
picked up, shown one at a time at the top of the page, and shuffled by the
button. Add or delete files and rebuild; nothing else to update.
"""
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).parent
SITE = ROOT / "site"
EXTS = {".jpg", ".jpeg", ".png", ".webp", ".avif", ".gif"}

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

if photos:
    shot = (
        '  <figure class="shot">\n'
        f'    <img id="shot" src="photos/{html.escape(photos[0])}" alt="Us">\n'
        '    <button id="newPhoto" type="button">Another photo</button>\n'
        "  </figure>\n"
    )
else:
    shot = ""

rows = "\n".join(
    f'      <li class="reason"><span class="n">{i}</span>'
    f'<span class="t">{html.escape(t)}</span></li>'
    for i, t in enumerate(reasons, 1)
)

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>100 Reasons for Selma</title>
<meta name="description" content="One hundred reasons, and one that shows up every day.">
<meta name="robots" content="noindex, nofollow">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Karla:wght@400;500;600&display=swap">
<style>
/* Layout: a quiet column - photo, one reason of the day, then all of them. */
:root{
  --bg:#F5F6FA; --surface:#FFFFFF; --ink:#191C2C; --muted:#656A84;
  --accent:#3647C4; --accent-soft:#E6E8F8; --rose:#C9798A; --rule:#DFE1EE;
  --display:'Instrument Serif',Georgia,'Times New Roman',serif;
  --body:'Karla','Helvetica Neue',Arial,sans-serif;
  color-scheme:light;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#0F1120; --surface:#171A2C; --ink:#ECEEF8; --muted:#9BA1BC;
  --accent:#8C98F2; --accent-soft:#232848; --rose:#E2A0AE; --rule:#272C47;
  color-scheme:dark;}}
:root[data-theme="dark"]{
  --bg:#0F1120; --surface:#171A2C; --ink:#ECEEF8; --muted:#9BA1BC;
  --accent:#8C98F2; --accent-soft:#232848; --rose:#E2A0AE; --rule:#272C47;
  color-scheme:dark;}

*{box-sizing:border-box}
html,body{margin:0}
img{max-width:100%}
body{background:var(--bg);color:var(--ink);font-family:var(--body);
  font-size:16px;line-height:1.6;-webkit-font-smoothing:antialiased}
.wrap{max-width:760px;margin:0 auto;padding-inline:20px;
  padding-block:calc(52px + env(safe-area-inset-top,0px)) calc(72px + env(safe-area-inset-bottom,0px))}

header{display:flex;flex-direction:column;gap:10px;margin-bottom:28px}
.eyebrow{font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:var(--muted);margin:0}
h1{font-family:var(--display);font-weight:400;font-size:clamp(44px,11vw,76px);
  line-height:1.02;margin:0;text-wrap:balance;letter-spacing:-.01em}
h1 em{font-style:italic;color:var(--accent)}
.sub{color:var(--muted);max-width:46ch;margin:0}

.shot{margin:0 0 34px;display:flex;flex-direction:column;gap:12px;align-items:flex-end}
.shot img{width:100%;border-radius:18px;display:block;aspect-ratio:3/2;
  object-fit:cover;background:var(--accent-soft);transition:opacity .22s ease}
.shot img.fading{opacity:.3}

button{font-family:var(--body);font-size:13px;font-weight:600;letter-spacing:.04em;
  color:var(--accent);background:var(--accent-soft);border:0;border-radius:999px;
  padding:9px 16px;cursor:pointer;transition:opacity .15s}
button:hover{opacity:.78}
button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}

.daily{background:var(--surface);border:1px solid var(--rule);border-radius:18px;
  padding:26px 24px 20px;display:flex;flex-direction:column;gap:14px;margin-bottom:52px}
.daily .cap{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin:0}
.daily .body{display:flex;gap:16px;align-items:baseline;min-height:96px}
.daily button{align-self:flex-start}
#dailyNum{font-family:var(--display);font-size:46px;line-height:1;color:var(--accent);
  font-variant-numeric:tabular-nums;flex:none}
#dailyText{font-family:var(--display);font-size:clamp(22px,5.2vw,30px);line-height:1.25;
  margin:0;min-width:0;text-wrap:balance}

.listhead{display:flex;align-items:center;gap:14px;margin-bottom:8px}
.listhead span{font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:var(--muted)}
.listhead .line{flex:1;height:1px;background:var(--rule)}

ol{list-style:none;margin:0;padding:0;display:flex;flex-direction:column}
.reason{display:flex;gap:18px;align-items:baseline;padding:13px 2px;
  border-bottom:1px solid var(--rule)}
.reason .n{font-family:var(--display);font-size:17px;color:var(--muted);
  font-variant-numeric:tabular-nums;min-width:2.1em;text-align:right;flex:none}
.reason .t{min-width:0}
.reason:last-child{border-bottom:0}
.reason:last-child .t{color:var(--accent)}

footer{margin-top:56px;text-align:center;color:var(--muted);font-size:14px}
footer .heart{color:var(--rose);font-size:18px;display:block;margin-bottom:8px}

@media (prefers-reduced-motion:reduce){.shot img{transition:none}}
@media (prefers-reduced-motion:no-preference){
  header,.shot,.daily{animation:rise .6s ease-out both}
  .shot{animation-delay:.06s} .daily{animation-delay:.12s}
  @keyframes rise{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <p class="eyebrow">Selma Esqalli</p>
    <h1>100 reasons <em>why I love you</em></h1>
    <p class="sub">All of them, in one place. One shows up here every day.</p>
  </header>

__SHOT__
  <section class="daily">
    <p class="cap">Today</p>
    <div class="body">
      <div id="dailyNum">1</div>
      <p id="dailyText">__FIRST__</p>
    </div>
    <button id="another" type="button">Show me another</button>
  </section>

  <div class="listhead"><span>All one hundred</span><div class="line"></div></div>
  <ol>
__ROWS__
  </ol>

  <footer><span class="heart">&#129293;</span>Always.</footer>
</div>

<script>
(function () {
  var reasons = __REASONS__;
  var numEl = document.getElementById('dailyNum');
  var txtEl = document.getElementById('dailyText');
  var current = Math.floor(Date.now() / 86400000) % reasons.length;
  function showReason(i) { numEl.textContent = i + 1; txtEl.textContent = reasons[i]; }
  showReason(current);
  document.getElementById('another').addEventListener('click', function () {
    var next = current;
    while (next === current) next = Math.floor(Math.random() * reasons.length);
    current = next;
    showReason(current);
  });

  var photos = __PHOTOS__;
  var img = document.getElementById('shot');
  var btn = document.getElementById('newPhoto');
  if (!img || !btn || photos.length < 2) { if (btn) btn.hidden = true; return; }

  var shown = Math.floor(Math.random() * photos.length);
  img.src = 'photos/' + photos[shown];

  function preload(i) { var p = new Image(); p.src = 'photos/' + photos[i]; }
  preload((shown + 1) % photos.length);

  btn.addEventListener('click', function () {
    var next = shown;
    while (next === shown) next = Math.floor(Math.random() * photos.length);
    shown = next;
    var loader = new Image();
    img.classList.add('fading');
    loader.onload = loader.onerror = function () {
      img.src = loader.src;
      img.classList.remove('fading');
      preload(Math.floor(Math.random() * photos.length));
    };
    loader.src = 'photos/' + photos[shown];
  });
})();
</script>
</body>
</html>
"""

out = (
    TEMPLATE.replace("__ROWS__", rows)
    .replace("__SHOT__", shot)
    .replace("__REASONS__", json.dumps(reasons, ensure_ascii=False))
    .replace("__PHOTOS__", json.dumps(photos, ensure_ascii=False))
    .replace("__FIRST__", html.escape(reasons[0]))
)
(SITE / "index.html").write_text(out, "utf-8")
print(f"built site/index.html - {len(reasons)} reasons, {len(photos)} photos")
