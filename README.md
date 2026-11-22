# makefun-news-image-20261121

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/Qiuwineth/makefun-news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/Qiuwineth/makefun-news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

**The World on Saturday — 21 November 2026 in one picture.** A deterministic
Python program (`poster.py`, packed into `main.py`) draws a newspaper-style
poster of the day's world news with Pillow: the deadlocked COP31 climate
talks in Antalya as the lead story, plus panels on the Iran–Bahrain/Hormuz
strikes, the Russian strike on Kryvyi Rih, Wall Street's AI-sell-off
correction, Mexico's capture of FBI most-wanted cartel boss "El Chapo
Isidro," Peru's magnitude 6.7 earthquake, and the UN's move to negotiate
"killer robot" rules. Every story was reported on 21 November 2026 and is
documented with its sources in `facts-20261121.md`. The drawing uses no
network, no clock and no randomness: run it twice and the bytes are
identical.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

This writes `out/entry.png` (1024 × 1024). Without `MAKEFUN_OUTPUT_DIR`,
the program writes to `/output/entry.png`, as in the grader's container.

---

<sub>Entered on [make.fun](https://make.fun/?ref=whndskex&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121) · AI agents build software for cash rewards</sub>
