#!/usr/bin/env python3
"""Render the C-GAB gate exhibit as one self-contained HTML page.

Every image is embedded as a data URI, so the page carries its own evidence and cannot
silently lose it. `make_gab_exhibit.py` builds the plates and facts.json first; this only
lays them out. It states no verdict - see that module's docstring for what the exhibit
deliberately does not do.

Override the output path with EXHIBIT_OUT.
"""
import base64, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.join(HERE, "exhibit_cgab")
OUT = os.environ.get("EXHIBIT_OUT", os.path.join(E, "cgab_exhibit.html"))

def uri(name):
    with open(os.path.join(E, name), "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()

facts = json.load(open(os.path.join(E, "facts.json")))
img = {n: uri(n + ".png") for n in
       ("tile_1x", "tile_12x", "tiled_3x3_1x", "tiled_3x3_6x",
        "overlay_12x", "overlay_3x3_6x", "lit_capture")}

sides = facts["claimed_sides"]
rows = "".join(
    '<tr><td class="m">%s</td><td class="m num">%d of %d</td><td>%s</td></tr>' % (
        k, v["dark"], v["of"],
        "continuous" if v["dark"] == v["of"] else
        ("<strong>less than half present</strong>" if v["dark"] * 2 < v["of"] else "broken"))
    for k, v in sides.items())

HTML = """<title>The C-GAB Keyline Question</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Literata:ital,opsz,wght@0,7..72,400;0,7..72,600;1,7..72,400&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>
:root{
  --ground:#f1f1f4; --panel:#ffffff; --plate:#e7e7ec;
  --ink:#1a1a23; --ink-soft:#4a4a5c; --ink-mute:#71718a;
  --rule:#d6d6df; --rule-firm:#b9b9c6;
  --accent:#4a4a78; --accent-soft:#ecebf5;
  --present:#c0008f; --absent:#0083a8;
  --warn-bg:#f7f0e2; --warn-ink:#6b4e12; --warn-rule:#d8c48c;
  --shadow:0 1px 2px rgba(26,26,35,.06),0 8px 24px rgba(26,26,35,.06);
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --ground:#131319; --panel:#1b1b23; --plate:#23232d;
  --ink:#e8e8f0; --ink-soft:#b3b3c4; --ink-mute:#8888a0;
  --rule:#2e2e3a; --rule-firm:#3f3f4f;
  --accent:#a9a9e0; --accent-soft:#24243a;
  --present:#ff5cd0; --absent:#48d4f4;
  --warn-bg:#2a2415; --warn-ink:#e0c98a; --warn-rule:#5c4d24;
  --shadow:0 1px 2px rgba(0,0,0,.4),0 8px 24px rgba(0,0,0,.35);
}}
:root[data-theme="dark"]{
  --ground:#131319; --panel:#1b1b23; --plate:#23232d;
  --ink:#e8e8f0; --ink-soft:#b3b3c4; --ink-mute:#8888a0;
  --rule:#2e2e3a; --rule-firm:#3f3f4f;
  --accent:#a9a9e0; --accent-soft:#24243a;
  --present:#ff5cd0; --absent:#48d4f4;
  --warn-bg:#2a2415; --warn-ink:#e0c98a; --warn-rule:#5c4d24;
  --shadow:0 1px 2px rgba(0,0,0,.4),0 8px 24px rgba(0,0,0,.35);
}
*{box-sizing:border-box}
body{
  margin:0; background:var(--ground); color:var(--ink);
  font-family:"IBM Plex Sans",system-ui,sans-serif; font-size:16.5px; line-height:1.62;
  -webkit-font-smoothing:antialiased;
}
.wrap{max-width:1080px;margin:0 auto;padding:clamp(28px,5vw,64px) clamp(18px,4vw,40px) 96px}
.col{max-width:64ch}
.eyebrow{
  font-family:"IBM Plex Mono",ui-monospace,monospace; font-size:11.5px; font-weight:500;
  letter-spacing:.14em; text-transform:uppercase; color:var(--ink-mute); margin:0 0 14px;
}
h1{
  font-family:Literata,Georgia,serif; font-weight:600; font-size:clamp(30px,4.6vw,46px);
  line-height:1.14; letter-spacing:-.015em; text-wrap:balance; margin:0 0 18px;
}
h2{
  font-family:Literata,Georgia,serif; font-weight:600; font-size:clamp(20px,2.4vw,25px);
  line-height:1.24; text-wrap:balance; margin:0 0 6px; letter-spacing:-.008em;
}
p{margin:0 0 15px;color:var(--ink-soft)}
p.lede{font-size:18.5px;color:var(--ink)}
strong{color:var(--ink);font-weight:600}
a{color:var(--accent)}
hr{border:0;border-top:1px solid var(--rule);margin:56px 0}
.mono,.m{font-family:"IBM Plex Mono",ui-monospace,monospace}
.num{font-variant-numeric:tabular-nums}

.ask{
  margin:30px 0 8px; padding:26px 30px; border-radius:3px;
  background:var(--panel); border:1px solid var(--rule-firm);
  border-left:4px solid var(--accent); box-shadow:var(--shadow);
}
.ask .q{
  font-family:Literata,Georgia,serif; font-size:clamp(21px,3vw,29px); font-weight:600;
  line-height:1.28; margin:0; color:var(--ink); text-wrap:balance;
}
.ask .sub{margin:12px 0 0;font-size:15px;color:var(--ink-mute)}

.plate{margin:0 0 14px}
.plate-head{display:flex;align-items:baseline;gap:12px;margin:0 0 4px;flex-wrap:wrap}
.pnum{
  font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:12px;font-weight:500;
  color:var(--accent);letter-spacing:.1em;padding-top:5px;
}
.frame{
  background:var(--plate); border:1px solid var(--rule-firm); border-radius:3px;
  padding:clamp(16px,3vw,32px); display:flex; gap:clamp(18px,4vw,44px);
  align-items:flex-end; justify-content:center; flex-wrap:wrap; margin:18px 0 10px;
  overflow-x:auto;
}
.frame.tall{align-items:center}
.spec{display:flex;flex-direction:column;align-items:center;gap:10px}
.spec img{
  display:block; image-rendering:pixelated; image-rendering:crisp-edges;
  background:#8a8a96; border:1px solid var(--rule-firm); max-width:100%; height:auto;
}
.spec .cap{
  font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:11px;letter-spacing:.07em;
  text-transform:uppercase;color:var(--ink-mute);
}
.caption{font-size:14.5px;color:var(--ink-mute);margin:0;max-width:70ch}

blockquote.test{
  margin:20px 0; padding:0 0 0 20px; border-left:2px solid var(--rule-firm);
  font-family:Literata,Georgia,serif; font-style:italic; font-size:17px; color:var(--ink-soft);
}
blockquote.test b{font-style:normal;font-weight:600;color:var(--ink)}

.note{
  background:var(--warn-bg); border:1px solid var(--warn-rule); border-radius:3px;
  padding:16px 20px; margin:22px 0; font-size:14.5px; color:var(--warn-ink);
}
.note strong{color:var(--warn-ink)}

table{border-collapse:collapse;width:100%;margin:18px 0;font-size:14.5px}
caption{
  text-align:left;font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:11.5px;
  letter-spacing:.12em;text-transform:uppercase;color:var(--ink-mute);padding-bottom:10px;
}
th,td{text-align:left;padding:9px 14px 9px 0;border-bottom:1px solid var(--rule)}
th{
  font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:11px;font-weight:500;
  letter-spacing:.1em;text-transform:uppercase;color:var(--ink-mute);
}
td{color:var(--ink-soft)}
tr.split td{background:var(--accent-soft);color:var(--ink)}

.key{display:flex;gap:22px;flex-wrap:wrap;margin:14px 0 0;font-size:13.5px}
.key span{display:flex;align-items:center;gap:8px;color:var(--ink-soft)}
.chip{width:13px;height:13px;border-radius:2px;flex:none;border:1px solid rgba(0,0,0,.25)}

.foot{
  margin-top:56px;padding-top:22px;border-top:1px solid var(--rule);
  font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:11.5px;line-height:1.9;
  color:var(--ink-mute);word-break:break-all;
}
@media (max-width:640px){.frame{gap:20px}}
</style>

<div class="wrap">
<div class="col">
  <p class="eyebrow">Art bible &sect;5.5 &middot; routed by &sect;13.2 &middot; 2026-08-27</p>
  <h1>C-GAB is at the gate, and no instrument can settle it</h1>
  <p class="lede">Three blind seats judged this floor tile. Two called it clean stone. One called
  it a keyline &mdash; a dark line drawn round a shape <em>because it is a shape</em>, which
  &sect;12.1 bans outright. Same bytes, same lit capture, opposite readings.</p>
  <p>The tile is the <strong>primary style parent</strong>: everything the floor corpus generates
  from here inherits whatever it is. It keeps that status either way. What is unresolved is the
  clause underneath it &mdash; <em>&ldquo;carries no ring, at any value&rdquo;</em> &mdash; and
  the instrument that clause rests on has a measured blind spot shaped exactly like this tile.</p>
</div>

<div class="ask col">
  <p class="q">Crack through the stone, or frame around the tile?</p>
  <p class="sub">Your answer settles the &sect;5.5 corpus note. Nothing else in the round is
  waiting on it &mdash; screening carries on regardless, at the measured child rate.</p>
</div>

<hr>

<div class="col">
  <p class="eyebrow">Plate order is deliberate</p>
  <h2>The plain views come first</h2>
  <p>Plates 1&ndash;3 carry no marks of any kind. The annotated view is last, because drawing on
  the tile tells the eye where to look and that is the one influence this exhibit must not
  exert before you have read it yourself.</p>
</div>

<div class="plate">
  <div class="plate-head"><span class="pnum">PLATE 1</span><h2>One tile, alone</h2></div>
  <p class="caption">32&times;32 native, 8 colours. Left at true size; right at 12&times;,
  nearest-neighbour, no smoothing.</p>
  <div class="frame">
    <div class="spec"><img src="{tile_1x}" width="32" height="32" alt="C-GAB floor tile at true size, 32 by 32 pixels">
      <span class="cap">1&times; &mdash; 32px</span></div>
    <div class="spec"><img src="{tile_12x}" width="384" height="384" alt="The same tile magnified 12 times with nearest-neighbour scaling">
      <span class="cap">12&times;</span></div>
  </div>
</div>

<div class="col">
  <blockquote class="test">&ldquo;A joint marks where one stone stops and the next begins; it
  runs on across the floor from tile to tile. A keyline stops at one shape and rings it. If you
  cannot decide which you are looking at, ask: <b>does this line continue into the next tile
  along, or does it turn the corner and come back to where it started?</b>&rdquo;
  <br><span class="cap mono" style="font-size:11px">&mdash; the blind seat's own brief</span>
  </blockquote>
  <p>That test needs neighbours, and no seat was ever given them: the lit capture shows the tile
  <em>laid</em> among walls and shadow, and the PNG shows it <em>alone</em>. Plate 2 is the view
  that answers it.</p>
</div>

<div class="plate">
  <div class="plate-head"><span class="pnum">PLATE 2</span><h2>Nine of them, edge to edge</h2></div>
  <p class="caption">The same tile repeated 3&times;3 with no gap, at 6&times;. Follow any dark
  run to a tile boundary and see whether it crosses.</p>
  <div class="frame">
    <div class="spec"><img src="{tiled_3x3_6x}" width="576" height="576" alt="The C-GAB tile repeated in a three by three grid, magnified six times">
      <span class="cap">3&times;3 at 6&times;</span></div>
    <div class="spec"><img src="{tiled_3x3_1x}" width="96" height="96" alt="The same three by three grid at true size">
      <span class="cap">3&times;3 at 1&times;</span></div>
  </div>
</div>

<div class="plate">
  <div class="plate-head"><span class="pnum">PLATE 3</span><h2>What all three seats actually saw</h2></div>
  <p class="caption">The lit in-scene capture through the tier-0 rig, 750&times;1334, iPhone SE.
  Walls and light rig held constant; the floor is the only variable. This exact image produced
  all three verdicts &mdash; it re-derived byte-for-byte at two different commits.</p>
  <div class="frame tall">
    <div class="spec"><img src="{lit_capture}" width="375" alt="Lit in-scene capture of a corridor floored with the C-GAB tile">
      <span class="cap">lit capture &mdash; shown at half size</span></div>
  </div>
</div>

<hr>

<div class="col">
  <p class="eyebrow">Now the annotated view</p>
  <h2>The geometry in dispute</h2>
  <p>The dissenting seat named a specific rectangle: <em>&ldquo;a dark rectangle runs down col 9
  and col 23 from row 12 to row 20, closes along row 20 and dashes across row 9 &mdash; four
  sides, one value, returning on itself&hellip; the dashed top does not save it.&rdquo;</em></p>
  <p>Measured against the tile, three of those four sides are continuous and the fourth is not.
  <strong>Magenta marks claimed contour that is really there; cyan marks claimed contour where
  the tile has none.</strong></p>
  <div class="key">
    <span><i class="chip" style="background:var(--present)"></i> present &mdash; pixel is below the tile median</span>
    <span><i class="chip" style="background:var(--absent)"></i> absent &mdash; claimed, but the pixel is not dark</span>
  </div>
</div>

<div class="plate">
  <div class="plate-head"><span class="pnum">PLATE 4</span><h2>The claim, and its evidence</h2></div>
  <div class="frame">
    <div class="spec"><img src="{overlay_12x}" width="384" height="384" alt="The tile at 12x with the claimed contour marked, magenta where dark pixels exist and cyan where they do not">
      <span class="cap">single tile &mdash; 12&times;</span></div>
    <div class="spec"><img src="{overlay_3x3_6x}" width="576" height="576" alt="The marked tile repeated three by three">
      <span class="cap">3&times;3 &mdash; 6&times;</span></div>
  </div>
</div>

<div class="col">
<table>
  <caption>The four claimed sides, measured</caption>
  <thead><tr><th>side</th><th>dark pixels</th><th>reads as</th></tr></thead>
  <tbody>{rows}</tbody>
</table>

<table>
  <caption>What each instrument returned</caption>
  <thead><tr><th>instrument</th><th>verdict</th></tr></thead>
  <tbody>
    <tr><td>ring instrument &mdash; side coverage</td><td class="m num">0.791 against 0.90 required &rarr; CLEAN</td></tr>
    <tr><td>blind seat &mdash; remediation round A</td><td class="m">cull: none</td></tr>
    <tr><td>blind seat &mdash; parent-rate round CP</td><td class="m">cull: none &mdash; &ldquo;the best surface here by a distance&rdquo;</td></tr>
    <tr class="split"><td>blind seat &mdash; parent-rate round CS</td><td class="m"><strong>cull: keyline</strong></td></tr>
  </tbody>
</table>

<div class="note">
  <strong>Why the numbers cannot break the tie.</strong> &sect;12.1 holds that gaps do not
  excuse a keyline &mdash; <em>&ldquo;a border with a bite out of one corner, or one drawn as a
  dashed run of ticks, is still a keyline&rdquo;</em>. The ring instrument's own documented blind
  spot is precisely that case, and the threshold was deliberately not lowered to reach it
  <em>because this tile's 0.791 was taken to be a mortar joint network</em>. One seat now says it
  is not. Whether a side present in four pixels of nine is a broken keyline or an absent one is
  not a measurement, and building a number to decide it is the move &sect;13.4 forbids.
</div>

  <h2>What your answer does and does not do</h2>
  <p><strong>Settles:</strong> the &sect;5.5 corpus note, which currently records this as
  <em>flagged, unresolved by instrument</em>.</p>
  <p><strong>Does not touch:</strong> C-GAB's primary-parent status, which is retained either
  way; and screening, which stays the operative guard at the measured child rate &mdash; 5 of 20
  mechanically, 9 of 20 at the seat-adjusted upper bound.</p>
  <p>This is not an approval surface. &sect;13.1 is untouched: no candidate is ever approved from
  a sheet, and nothing here lands anything. The question is what the construction <em>is</em>,
  not whether the tile ships.</p>
</div>

<div class="foot col">
  tile &nbsp;{tilepath}<br>
  sha256 &nbsp;{tilesha}<br>
  lit capture &nbsp;{litpath}<br>
  sha256 &nbsp;{litsha}<br>
  built by &nbsp;tools/floor_remediation/make_gab_exhibit.py &middot; facts.json carries every figure above
</div>
</div>
"""

subs = dict(rows=rows, tilepath=facts["tile"], tilesha=facts["tile_sha256"],
            litpath=facts["lit_capture"], litsha=facts["lit_sha256"], **img)
html = HTML
for k, v in subs.items():
    html = html.replace("{" + k + "}", v)
open(OUT, "w").write(html)
print("written", OUT, os.path.getsize(OUT) // 1024, "KB")
