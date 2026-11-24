# LeetCode global profile rank vs. problems solved

Live sample scraped **24 November 2026** from LeetCode's public GraphQL API.

- **243 real users** with profile rank between **1 and 1,983**
- Solved counts between **2,131 and 4,123**
- The full problem set at scrape time was **4,123** problems

## Files

| File | What it is |
| --- | --- |
| `report.html` | Interactive report: chart + all 243 rows, sortable/filterable |
| `chart.png` | 1600×1000 chart (scatter + rolling median + IQR band) |
| `data.csv` | The raw 243-row dataset |
| `summary-by-100.csv` | Median/min/max solved for each 100-rank band |
| `render.py` | Regenerates the chart and HTML from `data.csv` |

## Why this is not a ready-made leaderboard

LeetCode has **two different rankings**:

1. **Profile "Rank"** — the number under your username on your profile. It is driven by problems solved.
2. **Contest "Global Ranking"** — based on contest rating. This is what LeetCode's `/ranking/` page and the `globalRanking` GraphQL query expose.

There is **no public endpoint that lists users in profile-rank order**. The profile-rank leaderboard does not exist as a page, so no repo or site can simply mirror it.

The workaround used here:

1. Enumerate the contest leaderboard, which *does* expose each contestant's **profile rank**:
   ```graphql
   query($page: Int!) {
     globalRanking(page: $page) {
       rankingNodes {
         user {
           username
           profile { ranking }
         }
       }
     }
   }
   ```
2. Keep every user whose `profile.ranking` is between 1 and 2,000.
3. Fetch their live solved totals:
   ```graphql
   query($username: String!) {
     matchedUser(username: $username) {
       profile { ranking }
       submitStatsGlobal {
         acSubmissionNum { difficulty count }
       }
     }
   }
   ```

Pages 1–180 of the contest leaderboard were scanned (4,500 contestants), producing 243 unique users with profile rank ≤ 2,000.

## Caveats

- **This is a sample, not a census.** Users who have never entered a contest are invisible to this method, which is why the rank column has gaps (rank 2, 4, 5, 6, 8–12, etc. were not in the scanned contest pool). Every row is a real, live profile.
- **The top saturates.** At 4,123 solved a user has solved the entire problem set, so ranks at the very top are ties broken by LeetCode internally. A few top users may show slightly stale solved counts.
- **Profile rank is not a pure function of solved count.** Adjacent users with similar solved totals can straddle each other; contest rating, reputation, and the timing of solves can affect the exact position. The rolling median in the chart is the useful signal.
- **The data moves.** LeetCode adds problems weekly/monthly. Re-scrape before citing exact numbers.

## Key numbers from this snapshot

| Rank | User | Solved |
| ---: | --- | ---: |
| 1 | `cpcs` | 4,123 |
| 3 | `SupremeChicken` | 4,118 |
| 7 | `reddyhemanth694` | 4,123 |
| 20 | `Ante_` | 4,123 |
| 103 | `skywalkert` | 3,710 |
| 253 | `tin_le` | 3,291 |
| 501 | `Henry_cc` | 2,969 |
| 997 | `alex_salcianciu` | 2,540 |
| 1,500 | `alkonaesc` | 2,287 |
| 1,983 | `Aman_j1` | 2,131 |

Band medians:

| Rank band | Median solved |
| --- | ---: |
| 1–200 | 3,752 |
| 201–400 | 3,229 |
| 401–600 | 2,911 |
| 601–800 | 2,765 |
| 801–1,000 | 2,580 |
| 1,001–1,200 | 2,482 |
| 1,201–1,400 | 2,393 |
| 1,401–1,600 | 2,281 |
| 1,601–1,800 | 2,222 |
| 1,801–2,000 | 2,152 |

For context: **2,000 solved** sits just beyond the last sampled point (rank 1,983 = 2,131 solved), which is consistent with a rank around **2,500–2,900** as the curve flattens. The user-reported point of ~2,000 solved / rank ~2,800 falls on that tail.

## Related projects that do *not* solve this

- `JacobLinCool/LeetCode-Query`, `its-bismay/leetcode-stats-api`, `chandandanjo/LeetcodeScraper` — wrappers around the same GraphQL API; useful for per-user stats, but `globalRanking` is contest rating.
- `mintutu/leetcode-country-ranking`, `chiehmin/leetcode-ranking-search` — contest-ranking tools.
- `codolio.com` leaderboard, `clist.by` — contest-rating leaderboards.
- `cc189.github.io/leetcode` — top users by reputation, not solved count.

None of them expose a list ordered by the profile "Rank".

## Regenerate

```bash
python3 render.py
open report.html
```

## Disclaimer

Not affiliated with LeetCode. All data is from public profile and contest-ranking fields. Usernames and solved counts are shown as-is for research/visualization; remove or correct anything on request.
