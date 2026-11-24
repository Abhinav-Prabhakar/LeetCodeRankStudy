import csv, base64, statistics, html, os, shutil, json
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(BASE, "assets")
DOCS = os.path.join(BASE, "docs")
os.makedirs(ASSETS, exist_ok=True)
os.makedirs(DOCS, exist_ok=True)

SITE = "https://abhinav-prabhakar.github.io/LeetCodeRankStudy/"
REPO = "https://github.com/Abhinav-Prabhakar/LeetCodeRankStudy"

# ------------------------------------------------------------------ data
rows = list(csv.DictReader(open(os.path.join(BASE, "data.csv"))))
for r in rows:
    for k in ("rank", "total", "easy", "medium", "hard"):
        r[k] = int(r[k])
rows.sort(key=lambda r: r["rank"])
N = len(rows)
MEDIAN = int(statistics.median(r["total"] for r in rows))

data_json = json.dumps(
    [{k: r[k] for k in ("rank", "username", "total", "easy", "medium", "hard", "country")} for r in rows],
    ensure_ascii=False, separators=(",", ":"),
).replace("</", "<\\/")

# ------------------------------------------------------------------ palette
INK    = (20, 19, 17)
BODY   = (47, 43, 38)
MUTED  = (107, 102, 94)
FAINT  = (154, 148, 138)
RULE   = (230, 226, 218)
GRID   = (242, 238, 231)
WASH   = (250, 248, 244)
PRIMARY = (124, 31, 46)

DIDOT  = "/System/Library/Fonts/Supplemental/Iowan Old Style.ttc"
CHARTER = "/System/Library/Fonts/Supplemental/Charter.ttc"


def F(path, size, index=0, scale=1):
    return ImageFont.truetype(path, int(size * scale), index=index)


def tracked(draw, xy, text, font, fill, tracking=0.0, anchor="l", scale=1):
    """Letter-spaced text. xy is top-left (or top-center/right); tracking in px."""
    widths = [draw.textlength(ch, font=font) for ch in text]
    gap = tracking * scale
    total = sum(widths) + gap * max(0, len(text) - 1)
    x, y = xy
    if anchor == "m":
        x -= total / 2
    elif anchor == "r":
        x -= total
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill, anchor="la")
        x += w + gap


def rolling(key, window=10):
    vals = [r[key] for r in rows]
    out = []
    for i, r in enumerate(rows):
        s = sorted(vals[max(0, i - window): min(len(vals), i + window + 1)])
        out.append({
            "rank": r["rank"],
            "lo": statistics.quantiles(s, n=4)[0] if len(s) > 3 else s[0],
            "mid": statistics.median(s),
            "hi": statistics.quantiles(s, n=4)[2] if len(s) > 3 else s[-1],
        })
    return out


# ------------------------------------------------------------------ static chart
def build_chart(path):
    S = 2
    W, H = 2000, 1100
    img = Image.new("RGB", (W * S, H * S), "#ffffff")
    d = ImageDraw.Draw(img, "RGBA")

    f_kicker = F(CHARTER, 11, 3, S)
    f_title  = F(DIDOT, 34, 0, S)
    f_meta   = F(CHARTER, 10, 0, S)
    f_axis   = F(CHARTER, 9.5, 3, S)
    f_tick   = F(CHARTER, 13, 0, S)
    f_note   = F(DIDOT, 14, 2, S)
    f_foot   = F(CHARTER, 10.5, 0, S)
    f_src    = F(CHARTER, 9.5, 1, S)

    L, R, T, B = 180, 90, 185, 130
    PW, PH = W - L - R, H - T - B
    XMIN, XMAX = 0, 2000
    YMIN, YMAX = 2000, 4200

    def px(x): return (L + (x - XMIN) / (XMAX - XMIN) * PW) * S
    def py(y): return (T + (YMAX - y) / (YMAX - YMIN) * PH) * S

    # running head
    tracked(d, (L * S, 58 * S), "PLATE I  ·  THE CLIMB", f_kicker, PRIMARY, 2.6, scale=S)
    d.text((L * S, 132 * S), "Problems solved by global profile rank", font=f_title, fill=INK, anchor="ls")
    tracked(d, ((W - R) * S, 82 * S), "LEETCODE  ·  24 NOVEMBER 2026", f_meta, MUTED, 1.8, "r", S)
    d.line([L * S, 152 * S, (W - R) * S, 152 * S], fill=RULE, width=1 * S)

    # grid + y labels
    for y in (2000, 2400, 2800, 3200, 3600, 4000):
        Y = py(y)
        if y != 2000:
            d.line([L * S, Y, (W - R) * S, Y], fill=GRID, width=1 * S)
        d.text(((L - 16) * S, Y), f"{y:,}", font=f_tick, fill=MUTED, anchor="rm")

    # x baseline + ticks
    y0 = py(2000)
    d.line([L * S, y0, (W - R) * S, y0], fill=(214, 208, 199), width=1 * S)
    for x in range(0, 2001, 250):
        X = px(x)
        d.line([X, y0, X, y0 + 6 * S], fill=(190, 183, 173), width=1 * S)
        d.text((X, y0 + 19 * S), "0" if x == 0 else f"{x:,}", font=f_tick, fill=MUTED, anchor="ma")

    # axis titles
    tracked(d, ((W - R) * S, (T - 24) * S), "PROBLEMS SOLVED", f_axis, MUTED, 2.4, "r", S)
    tracked(d, ((L + PW / 2) * S, 1006 * S), "GLOBAL PROFILE RANK", f_axis, MUTED, 2.4, "m", S)

    # rolling band + median
    roll = rolling("total")
    band = [(px(p["rank"]), py(p["hi"])) for p in roll] + \
           [(px(p["rank"]), py(p["lo"])) for p in reversed(roll)]
    d.polygon(band, fill=(124, 31, 46, 26))
    d.line([(px(p["rank"]), py(p["mid"])) for p in roll],
           fill=PRIMARY, width=int(1.8 * S), joint="curve")

    # dots
    for r in rows:
        X, Y = px(r["rank"]), py(r["total"])
        d.ellipse([X - 4.2 * S, Y - 4.2 * S, X + 4.2 * S, Y + 4.2 * S], fill=(20, 19, 17, 42))
        d.ellipse([X - 1.7 * S, Y - 1.7 * S, X + 1.7 * S, Y + 1.7 * S], fill=(20, 19, 17, 150))

    # annotations
    def note(x, y, label, dx, dy, align="left"):
        X, Y = px(x), py(y)
        tx, ty = X + dx * S, Y + dy * S
        d.line([X, Y, tx, ty + 4 * S], fill=(176, 168, 156, 160), width=max(1, int(0.9 * S)))
        d.ellipse([X - 4.6 * S, Y - 4.6 * S, X + 4.6 * S, Y + 4.6 * S], outline=PRIMARY, width=int(1.1 * S))
        d.text((tx, ty), label, font=f_note, fill=INK, anchor="rs" if align == "right" else "ls")

    note(1, 4123, "No. 1  ·  4,123", 58, -30)
    note(501, 2969, "No. 501  ·  2,969", 24, -34)
    note(997, 2540, "No. 997  ·  2,540", 24, -34)
    note(1983, 2131, "No. 1,983  ·  2,131", -26, -30, "right")

    # footer
    d.line([L * S, 1046 * S, (W - R) * S, 1046 * S], fill=RULE, width=1 * S)
    tracked(d, (L * S, 1068 * S), "243 PROFILES  ·  MEDIAN 2,579", f_foot, PRIMARY, 1.9, "l", S)
    tracked(d, ((W - R) * S, 1068 * S), "LEETCODE.COM/GRAPHQL", f_foot, MUTED, 1.9, "r", S)
    d.text((L * S, 1092 * S), "Profile rank reflects problems solved, not contest rating.", font=f_src, fill=FAINT, anchor="ls")

    img = img.resize((W, H), Image.LANCZOS)
    img.save(path, quality=95)
    return img


chart_img = build_chart(os.path.join(BASE, "chart.png"))
shutil.copyfile(os.path.join(BASE, "chart.png"), os.path.join(DOCS, "chart.png"))

# ------------------------------------------------------------------ favicon + mark
FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" fill="#ffffff"/>
<path d="M21 12.5V50.5H54" fill="none" stroke="#141311" stroke-width="3.4"/>
<circle cx="43.5" cy="25.5" r="5.6" fill="#7c1f2e"/>
</svg>
"""

MARK_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="The LeetCode Rank">
<path d="M21 12.5V50.5H54" fill="none" stroke="#7c1f2e" stroke-width="3.4"/>
<circle cx="43.5" cy="25.5" r="5.6" fill="#7c1f2e"/>
</svg>
"""

open(os.path.join(ASSETS, "favicon.svg"), "w").write(FAVICON_SVG)
open(os.path.join(ASSETS, "mark.svg"), "w").write(MARK_SVG)
open(os.path.join(DOCS, "favicon.svg"), "w").write(FAVICON_SVG)


def mark_png(size, path):
    s = 4
    n = size * s
    im = Image.new("RGB", (n, n), "#ffffff")
    dr = ImageDraw.Draw(im)
    lw = max(2, int(n * 0.052))
    dr.line([(21 / 64) * n, (12.5 / 64) * n, (21 / 64) * n, (50.5 / 64) * n],
            fill=INK, width=lw)
    dr.line([(21 / 64) * n, (50.5 / 64) * n, (54 / 64) * n, (50.5 / 64) * n],
            fill=INK, width=lw)
    r = (5.6 / 64) * n
    cx, cy = (43.5 / 64) * n, (25.5 / 64) * n
    dr.ellipse([cx - r, cy - r, cx + r, cy + r], fill=PRIMARY)
    im.resize((size, size), Image.LANCZOS).save(path)


for sz in (32, 180):
    mark_png(sz, os.path.join(ASSETS, f"favicon-{sz}.png"))
    mark_png(sz, os.path.join(DOCS, f"favicon-{sz}.png"))

# ------------------------------------------------------------------ social card
def build_og(path):
    S = 2
    W, H = 1200, 630
    im = Image.new("RGB", (W * S, H * S), "#ffffff")
    d = ImageDraw.Draw(im, "RGBA")

    f_micro  = F(CHARTER, 8.5, 3, S)
    f_title  = F(DIDOT, 86, 0, S)
    f_titlei = F(DIDOT, 86, 2, S)
    f_deck   = F(DIDOT, 19, 2, S)
    f_label  = F(CHARTER, 8, 0, S)
    f_value  = F(DIDOT, 30, 0, S)
    f_foot   = F(CHARTER, 8, 0, S)

    # frame
    d.rectangle([36 * S, 36 * S, (W - 36) * S, (H - 36) * S], outline=RULE, width=1 * S)

    # mark + wordmark
    mx, my, ms = 62 * S, 58 * S, 30 * S
    d.line([mx, my, mx, my + ms], fill=INK, width=2 * S)
    d.line([mx, my + ms, mx + ms * .95, my + ms], fill=INK, width=2 * S)
    d.ellipse([mx + ms * .68 - 2.6 * S, my + ms * .32 - 2.6 * S,
               mx + ms * .68 + 2.6 * S, my + ms * .32 + 2.6 * S], fill=PRIMARY)
    tracked(d, (104 * S, 62 * S), "THE LEETCODE RANK", f_micro, INK, 2.0, "l", S)
    tracked(d, ((W - 72) * S, 62 * S), "VOL. I  ·  MMXXVI", f_micro, MUTED, 1.8, "r", S)

    # headline
    d.text((72 * S, 236 * S), "The LeetCode", font=f_title, fill=INK, anchor="ls")
    d.text((72 * S, 318 * S), "Rank", font=f_titlei, fill=INK, anchor="ls")
    d.rectangle([72 * S, 344 * S, 118 * S, 344 * S], fill=PRIMARY)

    d.text((72 * S, 386 * S), "243 live profiles between rank one and rank two thousand —", font=f_deck, fill=BODY, anchor="ls")
    d.text((72 * S, 414 * S), "and the problems solved at each altitude.", font=f_deck, fill=BODY, anchor="ls")

    # stats
    stats = [("PROFILES", "243"), ("RANK RANGE", "1–1,983"), ("PROBLEMS SOLVED", "2,131–4,123")]
    x = 72 * S
    widths = [206, 218, 240]
    for i, (k, v) in enumerate(stats):
        if i:
            d.line([x - 18 * S, 486 * S, x - 18 * S, 552 * S], fill=RULE, width=1 * S)
        tracked(d, (x, 486 * S), k, f_label, MUTED, 1.7, "l", S)
        d.text((x, 536 * S), v, font=f_value, fill=INK, anchor="ls")
        x += widths[i] * S

    # mini chart
    bx, by, bw, bh = 792, 170, 330, 300
    ch = rolling("total")
    ymin, ymax = 2000, 4200
    cx = lambda rank: bx + rank / 2000 * bw
    cy = lambda val: by + (ymax - val) / (ymax - ymin) * bh
    d.line([bx * S, (by + bh) * S, (bx + bw) * S, (by + bh) * S], fill=(214, 208, 199), width=1 * S)
    band = [(cx(p["rank"]) * S, cy(p["hi"]) * S) for p in ch] + \
           [(cx(p["rank"]) * S, cy(p["lo"]) * S) for p in reversed(ch)]
    d.polygon(band, fill=(124, 31, 46, 24))
    d.line([(cx(p["rank"]) * S, cy(p["mid"]) * S) for p in ch], fill=PRIMARY, width=2 * S, joint="curve")
    for r in rows:
        X, Y = cx(r["rank"]) * S, cy(r["total"]) * S
        d.ellipse([X - 2.2 * S, Y - 2.2 * S, X + 2.2 * S, Y + 2.2 * S], fill=(20, 19, 17, 90))
    tracked(d, (bx * S, (by + bh + 26) * S), "GLOBAL PROFILE RANK  ·  1–1,983", f_label, MUTED, 1.6, "l", S)
    tracked(d, ((bx + bw) * S, (by + bh + 26) * S), "2,131–4,123 SOLVED", f_label, MUTED, 1.6, "r", S)

    # footer
    d.line([72 * S, 578 * S, (W - 72) * S, 578 * S], fill=RULE, width=1 * S)
    tracked(d, (72 * S, 594 * S), "A STUDY IN SOLVED PROBLEMS", f_foot, PRIMARY, 1.7, "l", S)
    tracked(d, ((W - 72) * S, 594 * S), "LIVE GRAPHQL DATA  ·  24 NOVEMBER 2026", f_foot, MUTED, 1.7, "r", S)

    im = im.resize((W, H), Image.LANCZOS)
    im.save(path, quality=95)


build_og(os.path.join(ASSETS, "og.png"))
shutil.copyfile(os.path.join(ASSETS, "og.png"), os.path.join(DOCS, "og.png"))


# ------------------------------------------------------------------ table rows
def esc(s):
    return html.escape(str(s), quote=True)


table_rows = "\n".join(
    f'<tr data-user="{esc(r["username"])}">'
    f'<td class="rank num">{r["rank"]:,}</td>'
    f'<td class="user"><a href="https://leetcode.com/u/{esc(r["username"])}/" target="_blank" rel="noopener">{esc(r["username"])}</a></td>'
    f'<td class="num solved">{r["total"]:,}</td>'
    f'<td class="num">{r["easy"]:,}</td>'
    f'<td class="num">{r["medium"]:,}</td>'
    f'<td class="num">{r["hard"]:,}</td>'
    f'<td class="country">{esc(r["country"] or "—")}</td>'
    f'</tr>'
    for r in rows
)

# ------------------------------------------------------------------ band summary
bins = []
for lo in range(0, 2000, 100):
    s = [r for r in rows if lo < r["rank"] <= lo + 100]
    if not s:
        continue
    bins.append({
        "range": f"{lo + 1:,}–{lo + 100:,}",
        "n": len(s),
        "median": int(statistics.median([r["total"] for r in s])),
        "min": min(r["total"] for r in s),
        "max": max(r["total"] for r in s),
    })
with open(os.path.join(BASE, "summary-by-100.csv"), "w", newline="") as f:
    wr = csv.DictWriter(f, fieldnames=["range", "n", "median", "min", "max"])
    wr.writeheader()
    wr.writerows(bins)
shutil.copyfile(os.path.join(BASE, "summary-by-100.csv"), os.path.join(DOCS, "summary-by-100.csv"))
shutil.copyfile(os.path.join(BASE, "data.csv"), os.path.join(DOCS, "data.csv"))

# ------------------------------------------------------------------ page
HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The LeetCode Rank — 243 profiles, ranks 1–1,983</title>
<meta name="description" content="A live study of LeetCode’s global profile rank: 243 real profiles from rank 1 to 1,983, and the number of problems solved at each altitude.">
<meta name="author" content="Abhinav Prabhakar">
<meta name="theme-color" content="#ffffff">
<meta name="color-scheme" content="light">
<link rel="canonical" href="@@SITE@@">
<meta property="og:type" content="website">
<meta property="og:site_name" content="The LeetCode Rank">
<meta property="og:title" content="The LeetCode Rank — A study in solved problems">
<meta property="og:description" content="243 live profiles. Ranks 1–1,983. 2,131–4,123 problems solved. A study in what it takes to reach the top of LeetCode.">
<meta property="og:url" content="@@SITE@@">
<meta property="og:image" content="@@OGURL@@">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="The LeetCode Rank — 243 profiles, ranks 1 to 1,983">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="The LeetCode Rank">
<meta name="twitter:description" content="243 live profiles. Ranks 1–1,983. 2,131–4,123 problems solved.">
<meta name="twitter:image" content="@@OGURL@@">
<link rel="icon" href="@@FAVICON@@" type="image/svg+xml">
<link rel="icon" href="@@FAVICON32@@" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="@@APPLE@@">
@@MANIFEST@@
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500&amp;family=Newsreader:ital,opsz,wght@0,6..72,300;0,6..72,400;0,6..72,500;1,6..72,300;1,6..72,400&amp;display=swap" rel="stylesheet">
<style>
  :root {
    --ink: #141311;
    --body: #2f2b26;
    --muted: #6b665e;
    --faint: #9a948a;
    --rule: #e6e2da;
    --grid: #f1ede6;
    --wash: #faf8f4;
    --primary: #7c1f2e;
    --serif: "Newsreader", "Iowan Old Style", "Charter", Georgia, serif;
    --sans: "Inter", -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif;
    color-scheme: light;
  }
  * { box-sizing: border-box; }
  html { scroll-behavior: smooth; }
  body {
    margin: 0;
    background: #fff;
    color: var(--ink);
    font-family: var(--serif);
    font-size: 19px;
    line-height: 1.62;
    font-optical-sizing: auto;
    font-variant-numeric: lining-nums proportional-nums;
    -webkit-font-smoothing: antialiased;
    text-rendering: optimizeLegibility;
  }
  ::selection { background: #f4e6e8; color: var(--ink); }
  a { color: inherit; }
  .wrap { width: 100%; max-width: 1200px; margin: 0 auto; padding: 0 48px; }
  section[id] { scroll-margin-top: 82px; }
  .skip { position: absolute; left: -9999px; top: 0; background: #fff; color: var(--ink); padding: 12px 16px; z-index: 100; }
  .skip:focus { left: 12px; top: 12px; }

  /* ---------------------------------------------------------------- topbar */
  .topbar {
    position: sticky; top: 0; z-index: 50;
    background: rgba(255,255,255,.92);
    -webkit-backdrop-filter: saturate(150%) blur(12px);
    backdrop-filter: saturate(150%) blur(12px);
    border-bottom: 1px solid var(--rule);
  }
  .topbar-inner { display: flex; align-items: center; justify-content: space-between; height: 64px; }
  .brand {
    display: inline-flex; align-items: center; gap: 11px;
    font-family: var(--sans); font-size: 9.5px; font-weight: 500;
    letter-spacing: .18em; text-transform: uppercase; text-decoration: none; color: var(--ink);
  }
  .brand svg { width: 21px; height: 21px; display: block; }
  .nav { display: flex; align-items: center; gap: 28px; font-family: var(--sans); font-size: 10px; letter-spacing: .14em; text-transform: uppercase; }
  .nav a { color: var(--muted); text-decoration: none; padding: 6px 0; border-bottom: 1px solid transparent; }
  .nav a:hover { color: var(--ink); border-bottom-color: var(--primary); }
  .nav .cta { color: var(--ink); border-bottom-color: var(--rule); }
  .nav .cta span { color: var(--primary); margin-left: 3px; }

  /* ---------------------------------------------------------------- hero */
  .hero { display: grid; grid-template-columns: minmax(0,1fr) 330px; gap: 48px; align-items: end; padding-top: 88px; padding-bottom: 58px; }
  .eyebrow {
    display: flex; align-items: center; gap: 9px;
    margin: 0 0 22px; font-family: var(--sans); font-size: 9.5px; font-weight: 500;
    letter-spacing: .22em; text-transform: uppercase; color: var(--primary);
  }
  .eyebrow .dot { width: 5px; height: 5px; border-radius: 50%; background: var(--primary); flex: none; }
  h1 {
    margin: 0; font-weight: 400; font-size: clamp(62px, 8.8vw, 118px);
    line-height: .84; letter-spacing: -.047em;
  }
  h1 em { font-style: italic; font-weight: 300; letter-spacing: -.02em; }
  .hero-side { padding-bottom: 4px; }
  .deck { margin: 0 0 26px; font-size: 21px; line-height: 1.44; font-style: italic; color: #3a3630; letter-spacing: -.005em; }
  .hero-meta { display: flex; flex-wrap: wrap; gap: 8px 18px; border-top: 1px solid var(--rule); padding-top: 15px;
    font-family: var(--sans); font-size: 8px; letter-spacing: .16em; text-transform: uppercase; color: var(--faint); }

  /* ---------------------------------------------------------------- ledger */
  .ledger { display: grid; grid-template-columns: repeat(4, 1fr); border-top: 1px solid var(--ink); border-bottom: 1px solid var(--rule); }
  .ledger .cell { display: flex; flex-direction: column; gap: 7px; padding: 22px 26px 25px 0; border-right: 1px solid var(--rule); }
  .ledger .cell:last-child { border-right: 0; padding-right: 0; }
  .ledger .label { font-family: var(--sans); font-size: 9px; font-weight: 500; letter-spacing: .2em; text-transform: uppercase; color: var(--muted); }
  .ledger .value { font-size: clamp(32px, 3.6vw, 49px); line-height: 1; letter-spacing: -.03em; }
  .ledger .value small { font-size: .4em; letter-spacing: .02em; vertical-align: super; }
  .ledger .note { font-size: 13.5px; font-style: italic; line-height: 1.3; color: var(--faint); }

  /* ---------------------------------------------------------------- plate */
  .plate { padding-top: 82px; }
  .section-head { display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap; gap: 24px; padding-bottom: 18px; border-bottom: 1px solid var(--ink); }
  .section-head .eyebrow { margin-bottom: 8px; }
  h2 { margin: 0; font-weight: 400; font-size: clamp(34px, 4.4vw, 54px); line-height: 1.02; letter-spacing: -.032em; }
  .metric { display: flex; align-items: center; gap: 19px; font-family: var(--sans); font-size: 9.5px; letter-spacing: .14em; text-transform: uppercase; }
  .metric .metric-label { color: var(--faint); margin-right: 2px; }
  .metric button { appearance: none; background: none; border: 0; padding: 4px 0; border-bottom: 1px solid transparent;
    font: inherit; letter-spacing: inherit; text-transform: inherit; color: var(--faint); cursor: pointer; }
  .metric button:hover { color: var(--ink); }
  .metric button[aria-pressed="true"] { color: var(--ink); border-bottom-color: var(--primary); }
  figure { margin: 26px 0 0; }
  .chart-shell { position: relative; width: 100%; min-height: 400px; }
  .chart-shell .chart-fallback { display: block; width: 100%; height: auto; }
  .chart-shell svg { display: block; width: 100%; height: auto; overflow: visible; touch-action: pan-y; animation: chartIn .8s cubic-bezier(.2,.7,.2,1) both; }
  @keyframes chartIn { from { opacity: 0; transform: translateY(7px); } to { opacity: 1; transform: none; } }
  .axis text { font-family: var(--sans); font-size: 10px; fill: var(--muted); }
  .axis .domain { stroke: #d6d0c7; }
  .axis .tick line { stroke: #c6bfb4; }
  .y-axis .domain { display: none; }
  .axis-unit { font-family: var(--sans); font-size: 8px; letter-spacing: .18em; fill: var(--muted); }
  .chart-foot {
    display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;
    margin-top: 10px; padding-top: 12px; border-top: 1px solid var(--rule);
    font-family: var(--sans); font-size: 9px; letter-spacing: .14em; text-transform: uppercase; color: var(--muted);
  }
  .legend { display: flex; flex-wrap: wrap; gap: 18px; }
  .legend i { display: inline-block; vertical-align: middle; margin-right: 6px; }
  .k-dot { width: 5px; height: 5px; border-radius: 50%; background: var(--ink); opacity: .5; }
  .k-line { width: 17px; height: 1px; background: var(--primary); }
  .k-band { width: 17px; height: 7px; background: rgba(124,31,46,.17); }
  .chart-actions { display: flex; align-items: center; gap: 18px; }
  .chart-actions a { color: var(--ink); text-decoration: none; border-bottom: 1px solid var(--rule); }
  .chart-actions a:hover { border-bottom-color: var(--primary); }
  .chart-actions span { color: var(--faint); }
  figcaption { margin: 16px 0 0; max-width: 760px; font-size: 14px; font-style: italic; line-height: 1.55; color: var(--muted); }

  /* chart tooltip */
  .chart-tip {
    position: absolute; z-index: 6; width: 262px; padding: 15px 17px 14px;
    background: #fff; border: 1px solid var(--rule);
    box-shadow: 0 18px 50px rgba(20,19,17,.09);
    opacity: 0; transform: translateY(5px); pointer-events: none;
    transition: opacity .16s ease, transform .16s ease;
  }
  .chart-tip.is-on { opacity: 1; transform: none; pointer-events: auto; }
  .tip-top { display: flex; justify-content: space-between; gap: 12px; font-family: var(--sans); font-size: 7.5px; letter-spacing: .15em; text-transform: uppercase; color: var(--primary); }
  .tip-top span:last-child { color: var(--faint); }
  .tip-name { margin-top: 1px; font-size: 24px; line-height: 1.1; letter-spacing: -.015em; word-break: break-word; }
  .tip-value { margin-top: 11px; font-size: 28px; line-height: 1; letter-spacing: -.02em; }
  .tip-value em { font-size: 13px; font-style: italic; letter-spacing: 0; color: var(--muted); }
  .tip-split { margin-top: 8px; font-size: 12.5px; line-height: 1.5; color: var(--muted); }
  .tip-split b { font-weight: 500; color: var(--ink); }
  .tip-country { font-size: 13px; font-style: italic; color: var(--muted); }
  .tip-links { display: flex; justify-content: space-between; gap: 10px; margin-top: 13px; padding-top: 10px; border-top: 1px solid var(--rule); }
  .tip-links a { font-family: var(--sans); font-size: 7.5px; letter-spacing: .12em; text-transform: uppercase; text-decoration: none; color: var(--ink); border-bottom: 1px solid var(--rule); white-space: nowrap; }
  .tip-links a:hover { border-bottom-color: var(--primary); }


  /* ---------------------------------------------------------------- mix */
  .mix { padding-top: 88px; }
  .mix-grid { display: grid; grid-template-columns: 330px minmax(0,1fr); gap: 64px; align-items: end; padding-top: 26px; }
  .mix-copy p { margin: 22px 0 0; font-size: 16.5px; line-height: 1.6; color: var(--body); }
  .mix-copy strong { font-weight: 500; }
  .mix-bar { display: flex; height: 106px; border: 1px solid var(--rule); border-top: 2px solid var(--primary); overflow: hidden; }
  .mix-seg { display: flex; flex-direction: column; justify-content: space-between; min-width: 0; padding: 14px 16px 13px; }
  .mix-seg .k { font-family: var(--sans); font-size: 8px; font-weight: 500; letter-spacing: .18em; text-transform: uppercase; }
  .mix-seg .v { font-size: clamp(22px, 2.4vw, 33px); line-height: 1; letter-spacing: -.02em; }
  .mix-easy { background: #eae4da; color: var(--ink); }
  .mix-medium { background: #27221d; color: #fff; }
  .mix-hard { background: #b9ad9c; color: var(--ink); }
  .mix-stats { display: grid; grid-template-columns: repeat(3, 1fr); border-top: 1px solid var(--rule); margin-top: 14px; }
  .mix-stats > div { padding: 14px 16px 0 0; border-right: 1px solid var(--rule); }
  .mix-stats > div:last-child { border-right: 0; padding-right: 0; }
  .mix-stats .k { font-family: var(--sans); font-size: 8px; letter-spacing: .16em; text-transform: uppercase; color: var(--muted); }
  .mix-stats .v { margin-top: 4px; font-size: 27px; line-height: 1; letter-spacing: -.02em; }
  .mix-stats .n { margin-top: 3px; font-size: 13px; font-style: italic; color: var(--faint); }
  .mix-stats > div:first-child .n { white-space: nowrap; }
  .mix-note { margin: 16px 0 0; font-size: 14px; font-style: italic; line-height: 1.5; color: var(--muted); }

  /* ---------------------------------------------------------------- reading */
  .reading { display: grid; grid-template-columns: 170px minmax(0, 700px); justify-content: center; gap: 64px; padding-top: 112px; }
  .rail { position: sticky; top: 100px; align-self: start; }
  .rail .num { font-family: var(--sans); font-size: 9.5px; letter-spacing: .2em; color: var(--primary); }
  .rail .name { margin-top: 5px; font-family: var(--sans); font-size: 9.5px; letter-spacing: .18em; text-transform: uppercase; color: var(--muted); }
  .prose p { margin: 0 0 24px; font-size: 19.5px; line-height: 1.68; color: var(--body); }
  .prose .lead { font-size: 25px; line-height: 1.47; letter-spacing: -.012em; color: var(--ink); }
  blockquote {
    margin: 46px 0; padding: 4px 0 4px 28px; border-left: 1px solid var(--primary);
    font-size: clamp(26px, 3.1vw, 34px); line-height: 1.26; letter-spacing: -.018em;
    font-style: italic; color: #3a3530;
  }

  /* ---------------------------------------------------------------- register */
  .register { padding-top: 112px; }
  .section-note { max-width: 370px; margin: 0; font-size: 15px; font-style: italic; line-height: 1.55; color: var(--muted); }
  .toolbar { display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap; gap: 20px; margin-top: 28px; padding-bottom: 11px; border-bottom: 1px solid var(--rule); }
  .search span { display: block; margin-bottom: 3px; font-family: var(--sans); font-size: 8.5px; letter-spacing: .2em; text-transform: uppercase; color: var(--muted); }
  .search input {
    width: 320px; max-width: 100%; padding: 4px 0 9px; border: 0; border-bottom: 1px solid var(--rule);
    background: transparent; color: var(--ink); font: inherit; font-size: 18px; outline: none;
  }
  .search input:focus { border-bottom-color: var(--primary); }
  .search input::placeholder { color: var(--faint); font-style: italic; }
  .meta { display: flex; align-items: center; flex-wrap: wrap; gap: 8px 18px; font-family: var(--sans); font-size: 9px; letter-spacing: .13em; text-transform: uppercase; color: var(--muted); }
  .meta #count { color: var(--faint); }
  .meta a { color: var(--ink); text-decoration: none; border-bottom: 1px solid var(--rule); padding-bottom: 2px; }
  .meta a:hover { border-bottom-color: var(--primary); }
  .table-wrap { position: relative; max-height: 744px; overflow: auto; border-bottom: 1px solid var(--rule); }
  table { width: 100%; border-collapse: collapse; font-size: 15px; }
  thead th { position: sticky; top: 0; z-index: 3; background: #fff; border-bottom: 1px solid var(--ink); padding: 0; text-align: left; }
  thead th button {
    width: 100%; display: flex; align-items: center; gap: 6px; padding: 14px 10px 11px;
    appearance: none; background: none; border: 0; cursor: pointer;
    font-family: var(--sans); font-size: 9px; font-weight: 500; letter-spacing: .17em;
    text-transform: uppercase; color: var(--muted); text-align: inherit;
  }
  thead th.num button { justify-content: flex-end; }
  thead th:first-child button { justify-content: flex-end; }
  thead th button:hover { color: var(--ink); }
  .arrow { font-size: 10px; line-height: 1; color: var(--primary); opacity: 0; }
  th[aria-sort] .arrow { opacity: 1; }
  tbody td { padding: 10px; border-bottom: 1px solid #f1ede6; vertical-align: middle; }
  tbody tr:hover { background: var(--wash); }
  tbody tr.is-active { background: #fbf1f2; box-shadow: inset 2px 0 0 var(--primary); }
  td.num { text-align: right; font-variant-numeric: tabular-nums; font-size: 16px; }
  td.rank { color: var(--muted); font-size: 14px; }
  td.user a { font-size: 17px; color: var(--ink); text-decoration: none; border-bottom: 1px solid transparent; }
  td.user a:hover { border-bottom-color: var(--primary); }
  td.country { font-size: 14.5px; font-style: italic; color: var(--muted); }
  .empty { margin: 0; padding: 46px 0; text-align: center; font-style: italic; color: var(--muted); }
  .empty span { color: var(--ink); }

  /* ---------------------------------------------------------------- method */
  .method { margin-top: 112px; padding-top: 44px; border-top: 1px solid var(--rule); }
  .method-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 64px; }
  .method h3 { margin: 0 0 18px; font-family: var(--sans); font-size: 9.5px; font-weight: 500; letter-spacing: .2em; text-transform: uppercase; color: var(--muted); }
  .method p, .method li { font-size: 16px; line-height: 1.62; color: #4a453e; }
  .method p { margin: 0 0 18px; }
  .method ul { list-style: none; margin: 0; padding: 0; }
  .method li { margin: 0 0 15px; padding: 0 0 15px; border-bottom: 1px solid var(--rule); }
  .method li:last-child { border-bottom: 0; padding-bottom: 0; margin-bottom: 0; }
  code { font-family: "SFMono-Regular", "Cascadia Mono", Menlo, Consolas, monospace; font-size: .84em; letter-spacing: -.01em; background: var(--wash); padding: 1px 4px; }

  /* ---------------------------------------------------------------- footer */
  footer { margin-top: 112px; border-top: 1px solid var(--rule); }
  .footer-inner { display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 26px; padding: 28px 0 0; }
  .footer-brand { display: flex; align-items: center; gap: 11px; font-family: var(--sans); font-size: 9.5px; letter-spacing: .16em; text-transform: uppercase; color: var(--muted); }
  .footer-brand svg { width: 19px; height: 19px; }
  .footer-links { display: flex; flex-wrap: wrap; gap: 22px; font-family: var(--sans); font-size: 9px; letter-spacing: .14em; text-transform: uppercase; }
  .footer-links a { color: var(--ink); text-decoration: none; border-bottom: 1px solid var(--rule); padding-bottom: 2px; }
  .footer-links a:hover { border-bottom-color: var(--primary); }
  .footer-note {
    display: flex; justify-content: space-between; flex-wrap: wrap; gap: 10px 20px;
    margin-top: 26px; padding: 14px 0 40px; border-top: 1px solid var(--rule);
    font-family: var(--sans); font-size: 8.5px; letter-spacing: .12em; text-transform: uppercase; color: var(--faint);
  }

  @keyframes rise { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: none; } }
  .hero h1, .hero-side, .ledger { animation: rise .8s cubic-bezier(.2,.7,.2,1) both; }
  .hero-side { animation-delay: .07s; }
  .ledger { animation-delay: .13s; }

  @media (max-width: 1000px) {
    .wrap { padding: 0 32px; }
    .hero { grid-template-columns: minmax(0,1fr) 300px; gap: 36px; padding-top: 68px; }
    .reading { grid-template-columns: 130px minmax(0, 640px); gap: 40px; }
    .method-grid { gap: 40px; }
  }
  @media (max-width: 820px) {
    .hero { grid-template-columns: 1fr; gap: 34px; align-items: start; padding-top: 54px; padding-bottom: 42px; }
    .hero-side { max-width: 560px; }
    h1 { font-size: clamp(58px, 14vw, 104px); }
    .ledger { grid-template-columns: 1fr 1fr; }
    .ledger .cell { border-bottom: 1px solid var(--rule); }
    .ledger .cell:nth-child(2) { border-right: 0; }
    .ledger .cell:nth-child(n+3) { border-bottom: 0; }
    .mix-grid { grid-template-columns: 1fr; gap: 30px; }
    .mix { padding-top: 76px; }
    .reading { grid-template-columns: 1fr; gap: 20px; padding-top: 82px; }
    .rail { position: static; display: flex; gap: 10px; align-items: baseline; }
    .rail .name { margin-top: 0; }
    .method-grid { grid-template-columns: 1fr; }
    .section-note { max-width: 100%; margin-top: 4px; }
    .nav a:not(.cta) { display: none; }
  }
  @media (max-width: 600px) {
    .wrap { padding: 0 20px; }
    body { font-size: 18px; }
    .topbar-inner { height: 58px; }
    .hero { padding-top: 44px; }
    .deck { font-size: 19px; }
    .ledger .cell { padding: 18px 16px 20px 0; }
    .plate, .register, .reading { padding-top: 76px; }
    .section-head { align-items: flex-start; gap: 18px; }
    .metric { gap: 14px; }
    .chart-shell { min-height: 340px; }
    .chart-foot { gap: 10px; }
    .legend { gap: 10px 14px; }
    .mix-bar { height: 92px; }
    .mix-seg { padding: 11px 10px 10px; }
    .mix-seg .v { font-size: 21px; }
    .mix-stats .v { font-size: 21px; }
    .mix-stats .n { font-size: 11.5px; }
    .chart-actions span { display: none; }
    .reading .prose p { font-size: 18.5px; }
    .prose .lead { font-size: 22px; }
    blockquote { padding-left: 20px; margin: 36px 0; }
    thead th button { padding: 12px 6px 10px; font-size: 7.5px; }
    tbody td { padding: 9px 6px; }
    td.user a { font-size: 15.5px; }
    td.num { font-size: 14.5px; }
    thead th:nth-child(4), thead th:nth-child(5), thead th:nth-child(6),
    tbody td:nth-child(4), tbody td:nth-child(5), tbody td:nth-child(6) { display: none; }
    table { table-layout: fixed; }
    thead th:nth-child(1), tbody td:nth-child(1) { width: 15%; }
    thead th:nth-child(2), tbody td:nth-child(2) { width: 39%; }
    thead th:nth-child(3), tbody td:nth-child(3) { width: 22%; }
    thead th:nth-child(4), tbody td:nth-child(4) { width: 24%; white-space: nowrap; }
    td.country { display: table-cell; font-size: 12px; }
    td.user a { display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 14.5px; }
    .table-wrap { max-height: 620px; }
    .method { margin-top: 82px; }
    footer { margin-top: 82px; }
  }
  @media (max-width: 430px) {
    .brand span { letter-spacing: .12em; font-size: 8.5px; }
    .metric { width: 100%; justify-content: space-between; }
    .metric .metric-label { display: none; }
    h1 { font-size: 58px; }
  }
  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { animation: none !important; transition: none !important; }
    html { scroll-behavior: auto; }
  }
</style>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>

<header class="topbar">
  <div class="wrap topbar-inner">
    <a class="brand" href="./" aria-label="The LeetCode Rank, home">
      <svg viewBox="0 0 64 64" aria-hidden="true"><path d="M21 12.5V50.5H54" fill="none" stroke="currentColor" stroke-width="3.4"/><circle cx="43.5" cy="25.5" r="5.6" fill="#7c1f2e"/></svg>
      <span>The LeetCode Rank</span>
    </a>
    <nav class="nav" aria-label="Primary">
      <a href="#plate">Chart</a>
      <a href="#mix">Mix</a>
      <a href="#reading">Reading</a>
      <a href="#register">Register</a>
      <a href="#method">Method</a>
      <a class="cta" href="data.csv" download>Data <span>↓</span></a>
    </nav>
  </div>
</header>

<main id="main">
  <section class="hero wrap">
    <div class="hero-main">
      <p class="eyebrow"><span class="dot"></span>A study in solved problems</p>
      <h1>The LeetCode<br><em>Rank</em></h1>
    </div>
    <aside class="hero-side">
      <p class="deck">243 live profiles, from rank 1 to rank 1,983 — and the problem count it takes to stand among them.</p>
      <div class="hero-meta">
        <span>Vol. I</span>
        <span>24 November 2026</span>
        <span>Public GraphQL</span>
      </div>
    </aside>
  </section>

  <section class="ledger wrap" aria-label="Key figures">
    <div class="cell"><span class="label">Profiles</span><span class="value">243</span><span class="note">of 4,500 contestants scanned</span></div>
    <div class="cell"><span class="label">Rank range</span><span class="value">1–1,983</span><span class="note">global profile rank</span></div>
    <div class="cell"><span class="label">Problems solved</span><span class="value">2,131–4,123</span><span class="note">median 2,579</span></div>
    <div class="cell"><span class="label">At the cut-off</span><span class="value">99.98<small>th</small></span><span class="note">≈ top 1 in 5,000</span></div>
  </section>

  <section class="plate wrap" id="plate">
    <header class="section-head">
      <div>
        <p class="eyebrow">Plate I — The climb</p>
        <h2>Every rank, plotted.</h2>
      </div>
      <div class="metric" role="group" aria-label="Chart metric">
        <span class="metric-label">Show</span>
        <button type="button" data-metric="total" aria-pressed="true">Solved</button>
        <button type="button" data-metric="easy" aria-pressed="false">Easy</button>
        <button type="button" data-metric="medium" aria-pressed="false">Medium</button>
        <button type="button" data-metric="hard" aria-pressed="false">Hard</button>
      </div>
    </header>

    <figure>
      <div class="chart-shell" id="chart">
        <img class="chart-fallback" src="@@CHART@@" alt="Scatter plot of LeetCode global profile rank versus problems solved">
        <div class="chart-tip" id="chart-tip" role="status" aria-live="polite"></div>
      </div>
      <div class="chart-foot">
        <div class="legend">
          <span><i class="k-dot"></i>Profiles</span>
          <span><i class="k-line"></i>Rolling median</span>
          <span><i class="k-band"></i>25–75th percentile</span>
        </div>
        <div class="chart-actions">
          <a href="chart.png" download>Download plate</a>
          <span>Hover to inspect · click to open</span>
        </div>
      </div>
      <figcaption>Each dot is a real profile. The line is a rolling median; the pale band marks the 25th to 75th percentile. Switch the metric above to see how easy, medium and hard totals behave at the same ranks.</figcaption>
    </figure>
  </section>


  <section class="mix wrap" id="mix" aria-labelledby="mix-title">
    <div class="mix-grid">
      <div class="mix-copy">
        <p class="eyebrow">Plate II — The mix</p>
        <h2 id="mix-title">Difficulty, by the numbers.</h2>
        <p>Profile rank counts every solved problem once. A hard is worth exactly as much as an easy — <strong>1 : 1 : 1</strong>. And the mix is remarkably stable: about a quarter easy, half medium, a fifth hard, at every altitude.</p>
      </div>
      <div class="mix-panel">
        <div class="mix-bar" role="img" aria-label="Easy 24.9 percent, medium 53 percent, hard 22.1 percent of all problems solved by the sample">
          <div class="mix-seg mix-easy" style="width:24.9%"><span class="k">Easy</span><span class="v">24.9%</span></div>
          <div class="mix-seg mix-medium" style="width:53.0%"><span class="k">Medium</span><span class="v">53.0%</span></div>
          <div class="mix-seg mix-hard" style="width:22.1%"><span class="k">Hard</span><span class="v">22.1%</span></div>
        </div>
        <div class="mix-stats">
          <div><div class="k">Median profile</div><div class="v">25 / 53 / 22</div><div class="n">easy / med / hard</div></div>
          <div><div class="k">Top 500</div><div class="v">24 / 53 / 23</div><div class="n">ranks 1–500</div></div>
          <div><div class="k">Bottom 500</div><div class="v">25 / 53 / 22</div><div class="n">ranks 1,501–1,983</div></div>
        </div>
        <p class="mix-note">Medium dominates because most of LeetCode’s catalogue is medium. The hard share slips only slightly as rank rises; easy and medium stay almost fixed.</p>
      </div>
    </div>
  </section>

  <section class="reading wrap" id="reading">
    <div class="rail">
      <span class="num">01</span>
      <span class="name">The reading</span>
    </div>
    <div class="prose">
      <p class="lead">LeetCode’s profile rank is not a contest rating. It is a tally of problems solved — a number that rises when you finish a question, and barely moves when you don’t.</p>
      <p>Rank 1 has solved all 4,123 problems. From there the bands compress: the median of the top 500 sits at 3,403 solved, the next 500 at 2,723, the next at 2,421, and the last at 2,216.</p>
      <blockquote>“At the top, the problem set runs out before the ambition does.”</blockquote>
      <p>By rank 2,000 the curve is almost flat. Between the 1,000th and 2,000th places, a thousand ranks separate users by about 500 problems. At this altitude, rank is less a measure of effort than of time and attrition — and of which problems LeetCode has added this month.</p>
    </div>
  </section>

  <section class="register wrap" id="register">
    <header class="section-head">
      <div>
        <p class="eyebrow">02 — The register</p>
        <h2>All 243, in order.</h2>
      </div>
      <p class="section-note">The gaps are not errors: they are users who do not appear in the contest leaderboards used to enumerate candidates.</p>
    </header>

    <div class="toolbar">
      <label class="search" for="q">
        <span>Filter the register</span>
        <input id="q" type="search" placeholder="Username, country or solved count" autocomplete="off">
      </label>
      <div class="meta">
        <span id="count">243 entries</span>
        <a href="data.csv" download>data.csv ↓</a>
        <a href="summary-by-100.csv" download>summary-by-100.csv ↓</a>
      </div>
    </div>

    <div class="table-wrap">
      <table id="t">
        <thead>
          <tr>
            <th scope="col" class="num" aria-sort="ascending"><button type="button" data-type="num">Rank <span class="arrow">↑</span></button></th>
            <th scope="col"><button type="button" data-type="text">Profile <span class="arrow"></span></button></th>
            <th scope="col" class="num"><button type="button" data-type="num">Solved <span class="arrow"></span></button></th>
            <th scope="col" class="num"><button type="button" data-type="num">Easy <span class="arrow"></span></button></th>
            <th scope="col" class="num"><button type="button" data-type="num">Medium <span class="arrow"></span></button></th>
            <th scope="col" class="num"><button type="button" data-type="num">Hard <span class="arrow"></span></button></th>
            <th scope="col"><button type="button" data-type="text">Country <span class="arrow"></span></button></th>
          </tr>
        </thead>
        <tbody>
@@ROWS@@
        </tbody>
      </table>
      <p class="empty" id="empty" hidden>No profiles match <span id="q-echo"></span>.</p>
    </div>
  </section>

  <section class="method wrap" id="method">
    <header class="section-head">
      <div>
        <p class="eyebrow">03 — Method &amp; caveats</p>
        <h2>How this was made.</h2>
      </div>
    </header>
    <div class="method-grid" style="margin-top:34px">
      <div>
        <h3>Method</h3>
        <p>LeetCode publishes no leaderboard for the profile rank shown under a username. The only enumerable public list is the contest leaderboard, whose nodes carry each user’s profile rank.</p>
        <p>I scanned pages 1–180 of the <code>globalRanking</code> query — 4,500 contestants — kept the 243 with a profile rank of 2,000 or better, then fetched their live solved totals from <code>matchedUser.submitStatsGlobal</code>.</p>
        <p>Captured 24 November 2026. The full pipeline lives in <code>render.py</code>; the dataset is <code>data.csv</code>.</p>
      </div>
      <div>
        <h3>Caveats</h3>
        <ul>
          <li>This is a sample, not a census. Users who never entered a contest are invisible to this method, which is why gaps appear at ranks 2, 4, 5 and elsewhere.</li>
          <li>Profile rank reflects problems solved. The separate “Global Ranking” on a LeetCode profile is contest rating; the two are not the same.</li>
          <li>At the top, solved counts saturate at 4,123 — the full problem set — so ties are effectively arbitrary.</li>
          <li>The data moves as LeetCode adds problems. Every figure here is a snapshot.</li>
        </ul>
      </div>
    </div>
  </section>
</main>

<footer>
  <div class="wrap">
    <div class="footer-inner">
      <div class="footer-brand">
        <svg viewBox="0 0 64 64" aria-hidden="true"><path d="M21 12.5V50.5H54" fill="none" stroke="currentColor" stroke-width="3.4"/><circle cx="43.5" cy="25.5" r="5.6" fill="#7c1f2e"/></svg>
        <span>The LeetCode Rank · Vol. I</span>
      </div>
      <nav class="footer-links" aria-label="Footer">
        <a href="@@REPO@@" target="_blank" rel="noopener">GitHub</a>
        <a href="https://leetcode.com/" target="_blank" rel="noopener">LeetCode</a>
        <a href="data.csv" download>CSV</a>
        <a href="#register">Register</a>
      </nav>
    </div>
    <div class="footer-note">
      <span>Compiled 24 November 2026 · Not affiliated with LeetCode</span>
      <span>Profile rank ≠ contest rating</span>
    </div>
  </div>
</footer>

<script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
<script>window.LEETCODE_DATA=@@DATA@@;</script>
<script>
(function () {
  'use strict';
  var data = window.LEETCODE_DATA || [];
  var q = document.getElementById('q');
  var table = document.getElementById('t');
  var tbody = table.tBodies[0];
  var rows = [].slice.call(tbody.rows);
  var count = document.getElementById('count');
  var empty = document.getElementById('empty');
  var qEcho = document.getElementById('q-echo');
  var total = rows.length;

  function apply() {
    var v = q.value.trim().toLowerCase();
    var n = 0;
    var matched = new Set();
    rows.forEach(function (r) {
      var ok = !v || r.innerText.toLowerCase().indexOf(v) !== -1;
      r.style.display = ok ? '' : 'none';
      if (ok) { n++; matched.add(r.dataset.user); }
    });
    if (v) {
      count.textContent = n + ' of ' + total + ' entries';
      qEcho.textContent = '“' + q.value.trim() + '”';
    } else {
      count.textContent = total + ' entries';
    }
    empty.hidden = n !== 0;
    tbody.hidden = n === 0;
    if (window.__rankChart) window.__rankChart.highlight(v ? matched : null);
  }

  q.addEventListener('input', apply);

  var headers = [].slice.call(table.querySelectorAll('th'));
  headers.forEach(function (th) {
    var btn = th.querySelector('button');
    btn.addEventListener('click', function () {
      var i = th.cellIndex;
      var type = btn.dataset.type;
      var asc = th.getAttribute('aria-sort') !== 'ascending';
      headers.forEach(function (h) {
        h.removeAttribute('aria-sort');
        var a = h.querySelector('.arrow');
        if (a) a.textContent = '';
      });
      th.setAttribute('aria-sort', asc ? 'ascending' : 'descending');
      th.querySelector('.arrow').textContent = asc ? '↑' : '↓';
      rows.sort(function (a, b) {
        var x = a.cells[i].innerText.replace(/,/g, '').trim();
        var y = b.cells[i].innerText.replace(/,/g, '').trim();
        if (type === 'num') { x = +x; y = +y; }
        return (x > y ? 1 : x < y ? -1 : 0) * (asc ? 1 : -1);
      });
      rows.forEach(function (r) { tbody.appendChild(r); });
    });
  });

  document.addEventListener('locate-profile', function (e) {
    var name = e.detail;
    if (q.value) { q.value = ''; apply(); }
    var row = rows.filter(function (r) { return r.dataset.user === name; })[0];
    if (!row) return;
    var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    row.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'center' });
    row.classList.add('is-active');
    setTimeout(function () { row.classList.remove('is-active'); }, 2800);
  });

  if (location.hash.indexOf('#u=') === 0) {
    var user = decodeURIComponent(location.hash.slice(3));
    setTimeout(function () { document.dispatchEvent(new CustomEvent('locate-profile', { detail: user })); }, 350);
  }
})();

(function () {
  'use strict';
  var data = window.LEETCODE_DATA || [];
  var shell = document.getElementById('chart');
  var tip = document.getElementById('chart-tip');
  if (!window.d3 || !shell || !tip || !data.length) return;

  var d3 = window.d3;
  var fmt = d3.format(',');
  var INK = '#141311', MUTED = '#6b665e', PRIMARY = '#7c1f2e', RULE = '#e6e2da';
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var METRICS = {
    total:  { label: 'Solved', unit: 'PROBLEMS SOLVED', domain: [2000, 4200], ticks: [2000, 2400, 2800, 3200, 3600, 4000] },
    easy:   { label: 'Easy',   unit: 'EASY SOLVED',     domain: [150, 1000],  ticks: [200, 400, 600, 800, 1000] },
    medium: { label: 'Medium', unit: 'MEDIUM SOLVED',   domain: [950, 2200],  ticks: [1000, 1200, 1400, 1600, 1800, 2000, 2200] },
    hard:   { label: 'Hard',   unit: 'HARD SOLVED',     domain: [150, 1050],  ticks: [200, 400, 600, 800, 1000] }
  };
  var metric = 'total';
  var width, height, mobile, m, x, y;
  var svg, gGrid, gY, gX, bandPath, linePath, dots, ann, annGroups;
  var guide, ring, overlay, active = null, hideTimer = null, lastWidth = 0, roFrame = null;
  var highlightSet = null;

  var ROLL = {};
  Object.keys(METRICS).forEach(function (key) {
    var vals = data.map(function (d) { return d[key]; });
    ROLL[key] = data.map(function (d, i) {
      var s = vals.slice(Math.max(0, i - 10), Math.min(vals.length, i + 11)).sort(d3.ascending);
      return { rank: d.rank, lo: d3.quantileSorted(s, .25), mid: d3.quantileSorted(s, .5), hi: d3.quantileSorted(s, .75) };
    });
  });

  function measure() {
    width = Math.max(300, Math.round(shell.clientWidth));
    mobile = width < 700;
    height = mobile ? 424 : Math.max(500, Math.min(650, Math.round(width * 0.5)));
    m = mobile
      ? { top: 28, right: 16, bottom: 50, left: 44 }
      : { top: 34, right: 24, bottom: 56, left: 68 };
  }

  function nearest(rank) {
    return data.reduce(function (a, b) {
      return Math.abs(b.rank - rank) < Math.abs(a.rank - rank) ? b : a;
    }, data[0]);
  }

  function build() {
    measure();
    d3.select(shell).selectAll('svg').remove();
    var fallback = shell.querySelector('.chart-fallback');
    if (fallback) fallback.style.display = 'none';

    svg = d3.select(shell).insert('svg', '.chart-tip')
      .attr('viewBox', '0 0 ' + width + ' ' + height)
      .attr('width', width)
      .attr('height', height)
      .attr('role', 'img')
      .attr('aria-label', 'Scatter plot of LeetCode global profile rank versus problems solved');

    x = d3.scaleLinear().domain([0, 2000]).range([m.left, width - m.right]);
    y = d3.scaleLinear().domain(METRICS[metric].domain).range([height - m.bottom, m.top]);

    gGrid = svg.append('g');
    gGrid.selectAll('line').data(METRICS[metric].ticks).join('line')
      .attr('x1', m.left).attr('x2', width - m.right)
      .attr('y1', function (d) { return y(d); }).attr('y2', function (d) { return y(d); })
      .attr('stroke', '#f1ede6').attr('stroke-width', 1);
    gY = svg.append('g').attr('class', 'axis y-axis').attr('transform', 'translate(' + m.left + ',0)');
    gX = svg.append('g').attr('class', 'axis').attr('transform', 'translate(0,' + (height - m.bottom) + ')');

    svg.append('text').attr('class', 'axis-unit js-unit')
      .attr('x', width - m.right).attr('y', m.top - 13).attr('text-anchor', 'end');
    svg.append('text').attr('class', 'axis-unit')
      .attr('x', m.left + (width - m.left - m.right) / 2).attr('y', height - 9)
      .attr('text-anchor', 'middle').text('GLOBAL PROFILE RANK');

    gX.call(d3.axisBottom(x)
      .tickValues(d3.range(0, 2001, 250))
      .tickSize(6).tickPadding(9)
      .tickFormat(function (d) { return d === 0 ? '0' : fmt(d); }));

    var area0 = d3.area()
      .x(function (d) { return x(d.rank); })
      .y0(function (d) { return y(d.lo); })
      .y1(function (d) { return y(d.hi); })
      .curve(d3.curveMonotoneX);
    var line0 = d3.line()
      .x(function (d) { return x(d.rank); })
      .y(function (d) { return y(d.mid); })
      .curve(d3.curveMonotoneX);
    bandPath = svg.append('path').attr('fill', PRIMARY).attr('opacity', .09)
      .attr('d', area0(ROLL[metric]));
    linePath = svg.append('path').attr('fill', 'none').attr('stroke', PRIMARY)
      .attr('stroke-width', 1.7).attr('stroke-linecap', 'round').attr('stroke-linejoin', 'round')
      .attr('d', line0(ROLL[metric]));

    dots = svg.append('g').selectAll('circle').data(data, function (d) { return d.username; }).join('circle')
      .attr('cx', function (d) { return x(d.rank); })
      .attr('cy', function (d) { return y(d[metric]); })
      .attr('r', mobile ? 2.2 : 2.8)
      .attr('fill', INK)
      .attr('opacity', .4)
      .attr('pointer-events', 'none');

    ann = svg.append('g');
    var targets = mobile ? [data[0], data[data.length - 1]] : [data[0], nearest(500), nearest(1000), data[data.length - 1]];
    annGroups = ann.selectAll('g').data(targets).join('g').attr('class', 'ann');
    annGroups.append('line').attr('stroke', '#b7afa3').attr('stroke-width', .8).attr('opacity', .75);
    annGroups.append('circle').attr('r', 4.6).attr('fill', 'none').attr('stroke', PRIMARY).attr('stroke-width', 1);
    annGroups.append('text').attr('font-family', 'var(--serif)').attr('font-style', 'italic')
      .attr('font-size', mobile ? 10.5 : 12).attr('fill', INK);

    var hover = svg.append('g').attr('pointer-events', 'none');
    guide = hover.append('line').attr('y1', m.top).attr('y2', height - m.bottom)
      .attr('stroke', PRIMARY).attr('stroke-dasharray', '2 4').attr('opacity', 0);
    ring = hover.append('circle').attr('r', 6.4).attr('fill', 'none')
      .attr('stroke', PRIMARY).attr('stroke-width', 1.2).attr('opacity', 0);

    overlay = svg.append('rect')
      .attr('x', m.left).attr('y', m.top)
      .attr('width', Math.max(1, width - m.left - m.right))
      .attr('height', Math.max(1, height - m.top - m.bottom))
      .attr('fill', 'transparent')
      .attr('tabindex', 0)
      .attr('role', 'application')
      .attr('aria-label', 'Interactive scatter plot. Use left and right arrow keys to inspect profiles; press Enter to open one.')
      .style('cursor', 'crosshair')
      .on('pointermove', onMove)
      .on('pointerleave', scheduleHide)
      .on('click', onClick)
      .on('keydown', onKey)
      .on('focus', function () { if (active === null) select(0); })
      .on('blur', scheduleHide);

    update(false);
    lastWidth = Math.round(shell.clientWidth);
  }

  function update(animate) {
    var cfg = METRICS[metric];
    y.domain(cfg.domain);
    var dur = animate && !reduced ? 620 : 0;
    var t = svg.transition().duration(dur).ease(d3.easeCubicOut);

    svg.select('.js-unit').text(cfg.unit);

    gGrid.selectAll('line').data(cfg.ticks, function (d) { return d; }).join('line')
      .attr('x1', m.left).attr('x2', width - m.right)
      .attr('stroke', '#f1ede6').attr('stroke-width', 1)
      .transition(t)
      .attr('y1', function (d) { return y(d); })
      .attr('y2', function (d) { return y(d); });

    var axis = d3.axisLeft(y)
      .tickValues(cfg.ticks).tickSize(0).tickPadding(12)
      .tickFormat(d3.format(','));
    gY.transition(t).call(axis);

    var area = d3.area()
      .x(function (d) { return x(d.rank); })
      .y0(function (d) { return y(d.lo); })
      .y1(function (d) { return y(d.hi); })
      .curve(d3.curveMonotoneX);
    bandPath.datum(ROLL[metric]).transition(t).attr('d', area);

    var line = d3.line()
      .x(function (d) { return x(d.rank); })
      .y(function (d) { return y(d.mid); })
      .curve(d3.curveMonotoneX);
    linePath.datum(ROLL[metric]).transition(t).attr('d', line);

    styleDots();
    dots.transition(t).attr('cy', function (d) { return y(d[metric]); });

    var offsets = mobile
      ? [{ dx: 18, dy: -15, a: 'start' }, { dx: -6, dy: -44, a: 'end' }]
      : [{ dx: 22, dy: -18, a: 'start' }, { dx: 20, dy: -24, a: 'start' }, { dx: 20, dy: -24, a: 'start' }, { dx: -22, dy: -19, a: 'end' }];

    annGroups.each(function (d, i) {
      var X = x(d.rank), Y = y(d[metric]);
      var o = offsets[i] || offsets[offsets.length - 1];
      var g = d3.select(this);
      var tx = X + o.dx, ty = Math.max(14, Y + o.dy);
      g.select('line').transition(t).attr('x1', X).attr('y1', Y).attr('x2', tx).attr('y2', ty + 3);
      g.select('circle').transition(t).attr('cx', X).attr('cy', Y);
      g.select('text').transition(t).attr('x', tx).attr('y', ty)
        .attr('text-anchor', o.a).text('No. ' + fmt(d.rank) + ' · ' + fmt(d[metric]));
    });

    if (active) {
      var d = active;
      guide.attr('x1', x(d.rank)).attr('x2', x(d.rank));
      ring.attr('cx', x(d.rank)).attr('cy', y(d[metric]));
      show(d, true);
    }
  }

  function styleDots() {
    dots.attr('fill', function (d) { return highlightSet && highlightSet.has(d.username) ? PRIMARY : INK; })
      .attr('opacity', function (d) {
        if (!highlightSet) return .4;
        return highlightSet.has(d.username) ? .95 : .07;
      })
      .attr('r', function (d) {
        var base = mobile ? 2.2 : 2.8;
        return highlightSet && highlightSet.has(d.username) ? base + 1.1 : base;
      });
  }

  function show(d, fromKeyboard) {
    active = d;
    var cfg = METRICS[metric];
    var split = ['easy', 'medium', 'hard'].map(function (k) {
      return (k === metric ? '<b>' : '') + fmt(d[k]) + ' ' + k + (k === metric ? '</b>' : '');
    }).join(' · ');

    tip.innerHTML =
      '<div class="tip-top"><span>No. ' + fmt(d.rank) + '</span><span>global profile rank</span></div>' +
      '<div class="tip-name">' + esc(d.username) + '</div>' +
      '<div class="tip-value">' + fmt(d.total) + ' <em>solved</em></div>' +
      '<div class="tip-split">' + split + '</div>' +
      '<div class="tip-country">' + esc(d.country || '—') + '</div>' +
      '<div class="tip-links"><a href="https://leetcode.com/u/' + encodeURIComponent(d.username) + '/" target="_blank" rel="noopener">Profile ↗</a><a href="#" data-locate="' + esc(d.username) + '">Find in register</a></div>';

    guide.attr('x1', x(d.rank)).attr('x2', x(d.rank)).attr('opacity', .5);
    ring.attr('cx', x(d.rank)).attr('cy', y(d[metric])).attr('opacity', 1);
    tip.classList.add('is-on');

    var tw = tip.offsetWidth, th = tip.offsetHeight;
    var left = x(d.rank) + 18;
    var top = y(d[metric]) - th / 2;
    if (left + tw > width - 8) left = x(d.rank) - tw - 18;
    if (top + th > height - 8) top = height - th - 8;
    if (top < 8) top = 8;
    if (left < 8) left = 8;
    tip.style.left = Math.round(left) + 'px';
    tip.style.top = Math.round(top) + 'px';
  }

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c];
    });
  }

  function onMove(event) {
    var p = d3.pointer(event, svg.node());
    var best = null, bd = Infinity;
    for (var i = 0; i < data.length; i++) {
      var dx = x(data[i].rank) - p[0], dy = y(data[i][metric]) - p[1];
      var dist = dx * dx + dy * dy;
      if (dist < bd) { bd = dist; best = data[i]; }
    }
    if (best && bd <= (mobile ? 40 : 34) * (mobile ? 40 : 34)) {
      clearTimeout(hideTimer);
      show(best);
    } else {
      hideNow();
    }
  }

  function onClick(event) {
    var p = d3.pointer(event, svg.node());
    var best = null, bd = Infinity;
    for (var i = 0; i < data.length; i++) {
      var dx = x(data[i].rank) - p[0], dy = y(data[i][metric]) - p[1];
      var dist = dx * dx + dy * dy;
      if (dist < bd) { bd = dist; best = data[i]; }
    }
    if (best && bd <= (mobile ? 40 : 34) * (mobile ? 40 : 34)) {
      window.open('https://leetcode.com/u/' + encodeURIComponent(best.username) + '/', '_blank', 'noopener');
    }
  }

  function onKey(event) {
    if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') {
      event.preventDefault();
      var i = active === null ? 0 : activeIndex() + (event.key === 'ArrowRight' ? 1 : -1);
      select(Math.max(0, Math.min(data.length - 1, i)));
    } else if ((event.key === 'Enter' || event.key === ' ') && active) {
      event.preventDefault();
      window.open('https://leetcode.com/u/' + encodeURIComponent(active.username) + '/', '_blank', 'noopener');
    } else if (event.key === 'Escape') {
      hideNow();
      overlay.node().blur();
    }
  }

  function activeIndex() {
    return Math.max(0, data.indexOf(active));
  }

  function select(i) {
    active = data[i];
    show(active, true);
  }

  function scheduleHide() {
    clearTimeout(hideTimer);
    hideTimer = setTimeout(hideNow, 190);
  }

  function hideNow() {
    active = null;
    tip.classList.remove('is-on');
    if (guide) guide.attr('opacity', 0);
    if (ring) ring.attr('opacity', 0);
  }

  tip.addEventListener('mouseenter', function () { clearTimeout(hideTimer); });
  tip.addEventListener('mouseleave', scheduleHide);
  tip.addEventListener('click', function (event) {
    var a = event.target.closest('[data-locate]');
    if (!a) return;
    event.preventDefault();
    document.dispatchEvent(new CustomEvent('locate-profile', { detail: a.getAttribute('data-locate') }));
    hideNow();
  });

  d3.selectAll('.metric button').on('click', function () {
    var next = this.getAttribute('data-metric');
    if (!METRICS[next] || next === metric) return;
    metric = next;
    d3.selectAll('.metric button').attr('aria-pressed', function () {
      return this.getAttribute('data-metric') === metric ? 'true' : 'false';
    });
    update(true);
  });

  var ro = new ResizeObserver(function () {
    var now = Math.round(shell.clientWidth);
    if (Math.abs(now - lastWidth) < 2) return;
    if (roFrame) cancelAnimationFrame(roFrame);
    roFrame = requestAnimationFrame(build);
  });
  ro.observe(shell);

  window.__rankChart = {
    highlight: function (set) {
      highlightSet = set && set.size ? set : null;
      styleDots();
    }
  };

  build();
})();
</script>
</body>
</html>"""

# ------------------------------------------------------------------ render pages
def page(docs=False):
    out = (
        HTML
        .replace("@@ROWS@@", table_rows)
        .replace("@@DATA@@", data_json)
        .replace("@@SITE@@", SITE)
        .replace("@@REPO@@", REPO)
        .replace("@@OGURL@@", SITE + "og.png")
        .replace("@@FAVICON@@", "favicon.svg" if docs else "assets/favicon.svg")
        .replace("@@FAVICON32@@", "favicon-32.png" if docs else "assets/favicon-32.png")
        .replace("@@APPLE@@", "favicon-180.png" if docs else "assets/favicon-180.png")
        .replace("@@MANIFEST@@", '<link rel="manifest" href="site.webmanifest">' if docs else "")
    )
    if docs:
        out = out.replace("@@CHART@@", "chart.png")
    else:
        b64 = base64.b64encode(open(os.path.join(BASE, "chart.png"), "rb").read()).decode()
        out = out.replace("@@CHART@@", "data:image/png;base64," + b64)
    return out


report = page(False)
open(os.path.join(BASE, "report.html"), "w").write(report)

docs_html = page(True)
open(os.path.join(DOCS, "index.html"), "w").write(docs_html)
open(os.path.join(DOCS, ".nojekyll"), "w").close()

# ------------------------------------------------------------------ site extras
open(os.path.join(DOCS, "robots.txt"), "w").write(
    "User-agent: *\nAllow: /\n\nSitemap: " + SITE + "sitemap.xml\n"
)
open(os.path.join(DOCS, "sitemap.xml"), "w").write(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    '  <url>\n'
    '    <loc>' + SITE + '</loc>\n'
    '    <lastmod>2026-11-24</lastmod>\n'
    '    <changefreq>monthly</changefreq>\n'
    '    <priority>1.0</priority>\n'
    '  </url>\n'
    '</urlset>\n'
)
open(os.path.join(DOCS, "site.webmanifest"), "w").write(json.dumps({
    "name": "The LeetCode Rank",
    "short_name": "LeetCode Rank",
    "description": "A live study of LeetCode global profile rank versus problems solved.",
    "start_url": "/LeetCodeRankStudy/",
    "scope": "/LeetCodeRankStudy/",
    "display": "standalone",
    "background_color": "#ffffff",
    "theme_color": "#ffffff",
    "icons": [
        {"src": "favicon.svg", "sizes": "any", "type": "image/svg+xml"},
        {"src": "favicon-180.png", "sizes": "180x180", "type": "image/png"},
    ],
}, indent=2) + "\n")

# ------------------------------------------------------------------ schema.org
schema = {
    "@context": "https://schema.org",
    "@type": "Dataset",
    "name": "LeetCode global profile rank vs. problems solved",
    "alternateName": "The LeetCode Rank",
    "description": "243 live LeetCode profiles between global profile rank 1 and 1,983, with total, easy, medium and hard problem counts.",
    "url": SITE,
    "creator": {
        "@type": "Person",
        "name": "Abhinav Prabhakar",
        "url": "https://github.com/Abhinav-Prabhakar",
    },
    "datePublished": "2026-11-24",
    "dateModified": "2026-11-24",
    "license": "https://opensource.org/licenses/MIT",
    "isAccessibleForFree": True,
    "keywords": ["LeetCode", "global ranking", "problems solved", "competitive programming", "dataset"],
    "variableMeasured": [
        {"@type": "PropertyValue", "name": "Global profile rank", "unitText": "rank"},
        {"@type": "PropertyValue", "name": "Problems solved", "unitText": "problems"},
    ],
    "distribution": [{
        "@type": "DataDownload",
        "encodingFormat": "text/csv",
        "contentUrl": SITE + "data.csv",
    }],
}
schema_json = json.dumps(schema, indent=2, ensure_ascii=False).replace("</", "<\\/")
for name in ("report.html", os.path.join("docs", "index.html")):
    p = os.path.join(BASE, name)
    s = open(p).read()
    s = s.replace("</head>", '<script type="application/ld+json">\n' + schema_json + '\n</script>\n</head>')
    open(p, "w").write(s)

print("chart.png", chart_img.size)
print("favicon 32/180, mark.svg, og.png")
print("report.html", len(open(os.path.join(BASE, "report.html")).read()) // 1024, "KB")
print("docs/index.html", len(docs_html) // 1024, "KB")
print("rows", N, "median", MEDIAN, "bins", len(bins))
