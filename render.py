import csv, base64, statistics, html, json, os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(open(f"{BASE}/data.csv")))
for r in rows:
    for k in ("rank", "total", "easy", "medium", "hard"):
        r[k] = int(r[k])
rows.sort(key=lambda r: r["rank"])

# ---------- chart ----------
S = 2  # supersample
W, H = 1600 * S, 1000 * S
img = Image.new("RGB", (W, H), "#ffffff")
d = ImageDraw.Draw(img, "RGBA")

F = "/System/Library/Fonts/Supplemental/"
def font(name, size):
    return ImageFont.truetype(F + name, size * S)
f_title = font("Arial Bold.ttf", 42)
f_sub = font("Arial.ttf", 17)
f_tick = font("Arial.ttf", 13)
f_axis = font("Arial Bold.ttf", 14)
f_note = font("Arial.ttf", 12)
f_bold = font("Arial Bold.ttf", 14)
f_small = font("Arial.ttf", 11)

L, R, T, B = 120 * S, 50 * S, 170 * S, 140 * S
PW, PH = W - L - R, H - T - B
XMIN, XMAX = 0, 2000
YMIN, YMAX = 2000, 4200

def px(x): return L + (x - XMIN) / (XMAX - XMIN) * PW
def py(y): return T + (YMAX - y) / (YMAX - YMIN) * PH

# panel + grid
d.rectangle([L, T, L + PW, T + PH], fill="#fcfcfb", outline="#e7e5e4", width=2 * S)
for x in range(0, 2001, 200):
    X = px(x)
    d.line([X, T, X, T + PH], fill="#ececea", width=1 * S)
for y in range(2000, 4201, 200):
    Y = py(y)
    d.line([L, Y, L + PW, Y], fill="#ececea", width=1 * S)

# rolling quantiles over 21 nearest points by rank
vals = [r["total"] for r in rows]
xs = [r["rank"] for r in rows]
roll = []
w = 10
for i in range(len(rows)):
    lo, hi = max(0, i - w), min(len(rows), i + w + 1)
    s = sorted(vals[lo:hi])
    def q(p):
        k = (len(s) - 1) * p
        f, c = int(k), min(int(k) + 1, len(s) - 1)
        return s[f] + (s[c] - s[f]) * (k - f)
    roll.append((xs[i], q(.25), statistics.median(s), q(.75)))

# IQR band
band = [(px(x), py(hi)) for x, lo, mid, hi in roll] + \
       [(px(x), py(lo)) for x, lo, mid, hi in reversed(roll)]
d.polygon(band, fill=(37, 99, 235, 22))
# median line
line = [(px(x), py(mid)) for x, lo, mid, hi in roll]
d.line(line, fill="#111827", width=5 * S, joint="curve")

# scatter
for r in rows:
    X, Y = px(r["rank"]), py(r["total"])
    d.ellipse([X - 8 * S, Y - 8 * S, X + 8 * S, Y + 8 * S], fill=(37, 99, 235, 105))

# axes ticks / labels
for x in range(0, 2001, 200):
    X = px(x)
    d.line([X, T + PH, X, T + PH + 8 * S], fill="#a8a29e", width=2 * S)
    label = "1" if x == 0 else str(x)
    tw = d.textlength(label, font=f_tick)
    d.text((X - tw / 2, T + PH + 14 * S), label, font=f_tick, fill="#57534e")
for y in range(2000, 4201, 200):
    Y = py(y)
    d.line([L - 8 * S, Y, L, Y], fill="#a8a29e", width=2 * S)
    label = f"{y:,}"
    tw = d.textlength(label, font=f_tick)
    d.text((L - 16 * S - tw, Y - 9 * S), label, font=f_tick, fill="#57534e")

# axis titles
d.text((L + PW / 2 - d.textlength("Global profile rank", font=f_axis) / 2, H - 95 * S),
       "Global profile rank", font=f_axis, fill="#292524")
# rotate y title by drawing on a separate layer
yl = Image.new("RGBA", (300 * S, 30 * S), (0, 0, 0, 0))
yd = ImageDraw.Draw(yl)
yd.text((0, 0), "Problems solved (accepted)", font=f_axis, fill="#292524")
yl = yl.rotate(90, expand=True)
img.paste(yl, (30 * S, int(T + PH / 2 - yl.height / 2)), yl)

# title / subtitle
d.text((L, 52 * S), "LeetCode global rank vs. problems solved", font=f_title, fill="#0c0a09")
d.text((L, 108 * S), "243 live profiles · profile rank 1–1,983 · scraped 24 Nov 2026", font=f_sub, fill="#78716c")
d.text((L, 132 * S), "Dots are real users; line is a rolling median; band is the 25th–75th percentile.", font=f_note, fill="#a8a29e")

def callout(x, y, text, dx, dy, align="left"):
    X, Y = px(x), py(y)
    d.ellipse([X - 5 * S, Y - 5 * S, X + 5 * S, Y + 5 * S], fill="#ffffff", outline="#111827", width=2 * S)
    tx, ty = X + dx * S, Y + dy * S
    tw = d.textlength(text, font=f_note)
    if align == "right":
        tx -= tw
    pad = 5 * S
    d.rounded_rectangle([tx - pad, ty - pad, tx + tw + pad, ty + 18 * S + pad],
                        radius=4 * S, fill=(255, 255, 255, 235), outline=(231, 229, 228, 255), width=1 * S)
    d.text((tx, ty), text, font=f_note, fill="#292524")

callout(1, 4123, "cpcs · 4,123 solved", 20, -34)
callout(103, 3710, "rank 100 · ~3,710", 24, -30)
callout(253, 3291, "rank 250 · ~3,290", 24, -28)
callout(501, 2969, "rank 500 · ~2,970", 24, -28)
callout(997, 2540, "rank 1,000 · ~2,540", 24, -28)
callout(1500, 2287, "rank 1,500 · ~2,287", 24, -40)
callout(1983, 2131, "rank 1,983 · 2,131", -20, -44, align="right")

# top-right annotation
d.text((px(1990), py(4178)), "4,123 = the entire current problem set", font=f_small, fill="#a8a29e", anchor="ra")

# footer
d.line([L, H - 65 * S, L + PW, H - 65 * S], fill="#e7e5e4", width=1 * S)
d.text((L, H - 54 * S), "Source: leetcode.com/graphql (live) · Rank is the profile “Rank” (solved-count based), not contest rating.", font=f_note, fill="#78716c")
d.text((L, H - 34 * S), "Candidates harvested from LeetCode contest leaderboards, so this is a sample of ranks 1–1,983, not the complete rank list.", font=f_note, fill="#a8a29e")

img = img.resize((1600, 1000), Image.LANCZOS)
img.save(f"{BASE}/chart.png", quality=95)

# ---------- summary bins ----------
bins = []
for lo in range(0, 2000, 100):
    s = [r for r in rows if lo < r["rank"] <= lo + 100]
    if not s: continue
    bins.append({
        "range": f"{lo+1:,}–{lo+100:,}",
        "n": len(s),
        "median": int(statistics.median([r["total"] for r in s])),
        "min": min(r["total"] for r in s),
        "max": max(r["total"] for r in s),
    })

# ---------- html ----------
png64 = base64.b64encode(open(f"{BASE}/chart.png", "rb").read()).decode()
table_rows = "\n".join(
    f'<tr><td class="num">{r["rank"]:,}</td>'
    f'<td><a href="https://leetcode.com/u/{html.escape(r["username"])}/" target="_blank" rel="noopener">{html.escape(r["username"])}</a></td>'
    f'<td class="num strong">{r["total"]:,}</td>'
    f'<td class="num">{r["easy"]:,}</td><td class="num">{r["medium"]:,}</td><td class="num">{r["hard"]:,}</td>'
    f'<td class="muted">{html.escape(r["country"] or "—")}</td></tr>'
    for r in rows
)
bin_rows = "\n".join(
    f'<tr><td>{b["range"]}</td><td class="num">{b["n"]}</td><td class="num strong">{b["median"]:,}</td>'
    f'<td class="num">{b["min"]:,}</td><td class="num">{b["max"]:,}</td></tr>' for b in bins
)

report = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>LeetCode global rank vs. problems solved</title>
<style>
  :root {{ --ink:#1c1917; --muted:#78716c; --line:#e7e5e4; --bg:#fafaf9; --accent:#2563eb; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--ink); font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; }}
  main {{ max-width:1180px; margin:0 auto; padding:44px 28px 80px; }}
  h1 {{ font-size:34px; letter-spacing:-.03em; margin:0 0 6px; }}
  .sub {{ color:var(--muted); margin:0 0 28px; }}
  .card {{ background:#fff; border:1px solid var(--line); border-radius:14px; padding:18px; margin:22px 0; box-shadow:0 1px 2px rgba(0,0,0,.03); }}
  .chart {{ padding:10px; }}
  .chart img {{ width:100%; height:auto; display:block; border-radius:8px; }}
  .stats {{ display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin:24px 0; }}
  .stat {{ background:#fff; border:1px solid var(--line); border-radius:12px; padding:14px 16px; }}
  .stat .k {{ font-size:12px; text-transform:uppercase; letter-spacing:.08em; color:var(--muted); }}
  .stat .v {{ font-size:26px; font-weight:700; letter-spacing:-.02em; margin-top:2px; }}
  h2 {{ font-size:20px; margin:38px 0 12px; letter-spacing:-.01em; }}
  p {{ color:#44403c; max-width:78ch; }}
  table {{ width:100%; border-collapse:collapse; font-size:14px; }}
  th, td {{ text-align:left; padding:9px 10px; border-bottom:1px solid #f0efed; }}
  th {{ font-size:11px; text-transform:uppercase; letter-spacing:.07em; color:var(--muted); position:sticky; top:0; background:#fff; cursor:pointer; user-select:none; }}
  tbody tr:hover {{ background:#fafaf9; }}
  .num {{ text-align:right; font-variant-numeric:tabular-nums; }}
  .strong {{ font-weight:700; }}
  .muted {{ color:var(--muted); }}
  a {{ color:var(--accent); text-decoration:none; }}
  a:hover {{ text-decoration:underline; }}
  .toolbar {{ display:flex; gap:12px; align-items:center; margin:0 0 12px; flex-wrap:wrap; }}
  input[type=search] {{ font:inherit; padding:9px 12px; border:1px solid var(--line); border-radius:9px; width:280px; outline:none; }}
  input[type=search]:focus {{ border-color:#93c5fd; box-shadow:0 0 0 3px #dbeafe; }}
  .hint {{ color:var(--muted); font-size:12px; }}
  .scroll {{ max-height:620px; overflow:auto; border:1px solid var(--line); border-radius:10px; }}
  .scroll table {{ margin:0; }}
  .foot {{ margin-top:30px; color:var(--muted); font-size:12px; }}
  @media (max-width:720px) {{ .stats {{ grid-template-columns:1fr 1fr; }} h1 {{ font-size:27px; }} }}
</style>
</head>
<body>
<main>
  <h1>LeetCode global rank vs. problems solved</h1>
  <p class="sub">Live sample of 243 profiles with profile rank 1–1,983 · scraped 24 November 2026</p>

  <div class="card chart"><img src="data:image/png;base64,{png64}" alt="Scatter plot of LeetCode global profile rank versus problems solved"></div>

  <div class="stats">
    <div class="stat"><div class="k">Profiles</div><div class="v">243</div></div>
    <div class="stat"><div class="k">Rank range</div><div class="v">1–1,983</div></div>
    <div class="stat"><div class="k">Solved range</div><div class="v">2,131–4,123</div></div>
    <div class="stat"><div class="k">Median @ rank 1,000</div><div class="v">2,540</div></div>
  </div>

  <h2>What this is (and isn’t)</h2>
  <p>LeetCode has no public leaderboard for the profile “Rank” shown under your username. The only enumerable public list is the contest leaderboard, whose nodes expose each user’s profile rank. I scanned 4,500 contest profiles (pages 1–180 of <code>globalRanking</code>) and kept every user whose profile rank was ≤ 2,000, then fetched their live solved totals from <code>matchedUser.submitStatsGlobal</code>. That yields the 243 real users below. It is a <strong>sample</strong> of ranks 1–1,983, not a complete census: users who never joined a contest are invisible to this method.</p>
  <p>The shape is consistent with LeetCode’s definition: profile rank is driven by problems solved, while the separate “Global Ranking” on the profile is contest rating. At the very top the solved count saturates at 4,123 (the whole problem set), so ties there are effectively arbitrary.</p>

  <h2>Median solved by rank band</h2>
  <div class="card" style="padding:8px 12px">
  <table>
    <thead><tr><th>Rank band</th><th class="num">Users</th><th class="num">Median solved</th><th class="num">Min</th><th class="num">Max</th></tr></thead>
    <tbody>{bin_rows}</tbody>
  </table>
  </div>

  <h2>All 243 data points</h2>
  <div class="toolbar">
    <input id="q" type="search" placeholder="Filter username or country…">
    <span class="hint" id="count">243 rows</span>
    <span class="hint">Click a column header to sort.</span>
  </div>
  <div class="scroll">
  <table id="t">
    <thead><tr><th data-type="num">Rank</th><th>User</th><th data-type="num">Solved</th><th data-type="num">Easy</th><th data-type="num">Medium</th><th data-type="num">Hard</th><th>Country</th></tr></thead>
    <tbody>{table_rows}</tbody>
  </table>
  </div>

  <p class="foot">Source: leetcode.com/graphql (live). Profile rank and solved counts fetched 2026-11-24. Chart and table generated locally. Usernames link to their LeetCode profiles.</p>
</main>
<script>
const q = document.getElementById('q');
const t = document.getElementById('t');
const rows = [...t.tBodies[0].rows];
const count = document.getElementById('count');
q.addEventListener('input', () => {{
  const v = q.value.trim().toLowerCase();
  let n = 0;
  for (const r of rows) {{
    const ok = !v || r.innerText.toLowerCase().includes(v);
    r.style.display = ok ? '' : 'none';
    if (ok) n++;
  }}
  count.textContent = n + ' row' + (n === 1 ? '' : 's');
}});
let dir = {{}};
t.querySelectorAll('th').forEach((th, i) => {{
  th.addEventListener('click', () => {{
    dir[i] = !dir[i];
    const type = th.dataset.type;
    rows.sort((a, b) => {{
      let x = a.cells[i].innerText.replace(/,/g, '');
      let y = b.cells[i].innerText.replace(/,/g, '');
      if (type === 'num') {{ x = +x; y = +y; }}
      return (x > y ? 1 : x < y ? -1 : 0) * (dir[i] ? 1 : -1);
    }});
    rows.forEach(r => t.tBodies[0].appendChild(r));
  }});
}});
</script>
</body>
</html>"""
open(f"{BASE}/report.html", "w").write(report)

# compact csv of bins
with open(f"{BASE}/summary-by-100.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["range", "n", "median", "min", "max"])
    w.writeheader(); w.writerows(bins)

print("chart.png", img.size)
print("report.html", len(report) // 1024, "KB")
print("bins", len(bins))
