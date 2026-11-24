<p align="center">
  <img src="assets/mark.svg" width="56" alt="The LeetCode Rank">
</p>

<h1 align="center">The LeetCode Rank</h1>

<p align="center">
  <em>243 live profiles. Ranks 1–1,983.<br>The problems they solve — and the ratings that barely track them.</em>
</p>

<p align="center">
  <a href="https://abhinav-prabhakar.github.io/LeetCodeRankStudy/"><img src="https://img.shields.io/badge/LIVE_SITE-VISIT-7C1F2E?style=for-the-badge&labelColor=141311" alt="Live site"></a>
  <img src="https://img.shields.io/badge/DATA-LIVE_GRAPHQL-141311?style=for-the-badge&labelColor=7C1F2E" alt="Live GraphQL data">
  <img src="https://img.shields.io/badge/CHART-D3-141311?style=for-the-badge&labelColor=7C1F2E" alt="D3 chart">
  <img src="https://img.shields.io/badge/LICENSE-MIT-141311?style=for-the-badge&labelColor=7C1F2E" alt="MIT license">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/profiles-243-7C1F2E?style=flat-square&labelColor=141311" alt="243 profiles">
  <img src="https://img.shields.io/badge/ranks-1%E2%80%931%2C983-7C1F2E?style=flat-square&labelColor=141311" alt="Ranks 1 to 1,983">
  <img src="https://img.shields.io/badge/solved-2%2C131%E2%80%934%2C123-7C1F2E?style=flat-square&labelColor=141311" alt="Solved 2,131 to 4,123">
  <img src="https://img.shields.io/badge/median_rating-2%2C479-7C1F2E?style=flat-square&labelColor=141311" alt="Median contest rating 2,479">
  <img src="https://img.shields.io/badge/rank_correlation-%E2%88%920.11-7C1F2E?style=flat-square&labelColor=141311" alt="Rank correlation −0.11">
  <img src="https://img.shields.io/badge/percentile-99.98th-7C1F2E?style=flat-square&labelColor=141311" alt="99.98th percentile">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.x-141311?style=flat-square&labelColor=7C1F2E&logo=python&logoColor=white" alt="Python 3">
  <img src="https://img.shields.io/badge/pages-live-141311?style=flat-square&labelColor=7C1F2E&logo=githubpages&logoColor=white" alt="GitHub Pages">
  <img src="https://img.shields.io/github/stars/Abhinav-Prabhakar/LeetCodeRankStudy?style=flat-square&label=stars&color=141311&labelColor=7C1F2E" alt="GitHub stars">
  <img src="https://img.shields.io/github/license/Abhinav-Prabhakar/LeetCodeRankStudy?style=flat-square&label=license&color=141311&labelColor=7C1F2E" alt="License">
</p>

<p align="center">
  <a href="https://abhinav-prabhakar.github.io/LeetCodeRankStudy/">
    <img src="assets/site-hero.png" alt="The LeetCode Rank — a live study of global profile rank and problems solved" width="100%">
  </a>
</p>

<table align="center">
  <tr>
    <td align="center"><strong>243</strong><br><sub>profiles</sub></td>
    <td align="center"><strong>1–1,983</strong><br><sub>global rank</sub></td>
    <td align="center"><strong>2,131–4,123</strong><br><sub>problems solved</sub></td>
    <td align="center"><strong>2,479</strong><br><sub>median rating</sub></td>
    <td align="center"><strong>99.98<sup>th</sup></strong><br><sub>at the cut-off</sub></td>
  </tr>
</table>

<br>

## The climb

<p align="center">
  <img src="assets/site-chart.png" alt="Interactive scatter plot of global profile rank versus problems solved, with a hovered profile" width="100%">
</p>

At the very top, the problem set runs out before the ambition does: rank 1 has solved all **4,123** problems. From there the bands compress: the median of the top 500 sits at **3,403** solved, the next 500 at **2,723**, the next at **2,421**, and the last at **2,216**.

By rank 2,000 the curve is almost flat. Between the 1,000th and 2,000th places, a thousand ranks separate users by about **500** problems — less a measure of effort than of time, attrition, and which problems LeetCode has added this month.

<br>

## The weighting

Profile rank counts every solved problem once. An easy is worth exactly as much as a hard — **1 : 1 : 1** — and the mix barely moves with rank: **24.9% easy, 53.0% medium, 22.1% hard** across all 243 profiles. The median profile is **25 / 53 / 22**; the top 500 is 24 / 53 / 23, the bottom 500 25 / 53 / 22.

<p align="center">
  <img src="assets/site-mix.png" alt="Difficulty mix — 24.9% easy, 53.0% medium, 22.1% hard" width="100%">
</p>

<br>

## The other ranking

Profile rank is a tally of problems solved. Contest rating is something else: speed, under a clock, against everyone else in the room. We pulled both.

Across all 243 profiles the two are nearly unrelated — **Pearson r = −0.11**, **Spearman ρ = −0.13**. The top 500 has a median rating of **2,479**; the last 500, **2,452**. The highest rating in the sample, **3,589**, belongs to No. 1,577. The second-highest, **3,365**, belongs to No. 1,964. Every profile carries a Guardian badge.

<p align="center">
  <img src="assets/site-rating.png" alt="The same profiles plotted by contest rating, showing a nearly flat relationship with global profile rank" width="100%">
</p>

| Median rating | Range | Correlation with rank |
|:--:|:--:|:--:|
| **2,479** | **2,304–3,589** | **−0.11** |

The caveat is range restriction. Everyone here is already in the top 2,000 by solved count, so the near-zero correlation describes the elite, not LeetCode as a whole. Across the full population, the relationship is surely stronger. Switch the chart to **Rating** on the live site to inspect any dot.

<br>

## The register

<p align="center">
  <img src="assets/site-register.png" alt="The searchable register of all 243 profiles" width="100%">
</p>

Every sampled profile, searchable by username, country or solved count. Toggle **Contest ratings** to add the second number. The gaps are real: they are users who never appear in the contest leaderboards used to enumerate candidates.

<p align="center">
  <a href="https://abhinav-prabhakar.github.io/LeetCodeRankStudy/"><img src="https://img.shields.io/badge/OPEN_THE_REGISTER-7C1F2E?style=for-the-badge&labelColor=141311" alt="Open the register"></a>
  <a href="data.csv"><img src="https://img.shields.io/badge/DOWNLOAD-data.csv-141311?style=for-the-badge&logo=download&logoColor=white" alt="Download data.csv"></a>
  <a href="summary-by-100.csv"><img src="https://img.shields.io/badge/DOWNLOAD-band_summary-141311?style=for-the-badge&logo=download&logoColor=white" alt="Download band summary"></a>
  <a href="ratings.csv"><img src="https://img.shields.io/badge/DOWNLOAD-ratings.csv-141311?style=for-the-badge&logo=download&logoColor=white" alt="Download ratings.csv"></a>
</p>

<br>

## Method, in three lines

**Scan.** Pages 1–180 of LeetCode’s `globalRanking` query — 4,500 contestants.

**Filter.** Keep every node whose `user.profile.ranking` is 2,000 or better.

**Fetch.** Pull live `submitStatsGlobal` totals for the 243 that remain — and `userContestRanking` ratings for the same usernames.

<p align="center">
  <img src="assets/site-method.png" alt="Method and caveats" width="100%">
</p>

It is a sample, not a census. Users who never entered a contest are invisible, which is why the register has gaps at ranks 2, 4, 5 and elsewhere. Profile rank is solved-count rank — the separate “Global Ranking” on LeetCode is contest rating. The near-zero rating correlation is range-restricted: every profile here is already elite by volume. Captured **24 November 2026**; the numbers move as LeetCode adds problems.

<br>

## Files

| | |
|:--|:--|
| [`data.csv`](data.csv) | 243 profiles · rank, username, total / easy / medium / hard, country |
| [`ratings.csv`](ratings.csv) | The same 243 · contest rating, contests, global rank, top %, badge |
| [`summary-by-100.csv`](summary-by-100.csv) | 20 rank bands · count, median, min, max |
| [`chart.png`](chart.png) | The 2000 × 1100 plate, ready to print or embed |
| [`report.html`](report.html) | Self-contained report with the chart embedded |
| [`render.py`](render.py) | Rebuilds the plate, report, social card, favicons, and `docs/` |
| [`docs/`](docs/) | The GitHub Pages build served from `main` / `docs` |

<br>

## Run it

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install pillow
python3 render.py
open docs/index.html
```

`render.py` reads `data.csv` and joins the optional `ratings.csv` by username; remove the ratings file to build the solved-only edition. It writes `chart.png`, `report.html`, and the complete `docs/` site. Commit `docs/` to publish.

<br>

<p align="center">
  <sub>Newsreader &amp; Inter · D3 · Python / Pillow · LeetCode GraphQL<br>
  Not affiliated with LeetCode · Data captured 24 November 2026</sub>
</p>

<p align="center">
  <a href="https://github.com/Abhinav-Prabhakar/LeetCodeRankStudy">GitHub</a> ·
  <a href="https://abhinav-prabhakar.github.io/LeetCodeRankStudy/">Live site</a> ·
  <a href="data.csv">CSV</a> ·
  <a href="ratings.csv">Ratings</a>
</p>
