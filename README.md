# The World Gazette — Thursday, November 19, 2026

[![bounty](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/hajilok/world-gazette-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/hajilok/world-gazette-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119)

One image that sums up the world's news of **Thursday 19 November 2026** — an entry
for make.fun's [news-image-20261119](https://make.fun/bounty/news-image-20261119) bounty.

A broadsheet front page drawn entirely by code: the APEC Shenzhen trilateral
(Trump, Xi, Putin) leads, above a 12-card grid — Anthropic's record $107.3B IPO,
GTA VI's launch after 13 years, the Crimean Bridge attack, Israel's Gaza incursion,
Myanmar's genocide verdict at the UN court, Van Gogh's $190.4M record, hawkish Fed
minutes, South Florida floods, Jeffries' Speaker nomination, Musk's midterm regret,
the Palantir spy arrest and Bangladesh's violence — plus a 12-brief world ticker.
25 stories, six continents, every picture drawn with PIL primitives: no photographs,
no external assets, no garbled generated text.

## Files

- `main.ts` — the entry program (Node 22, standard library only): validates
  `entry.png` (PNG signature, IHDR, 1024×1024 and 1 MiB caps, IEND) and copies it
  byte for byte to `/output/entry.png`. Deterministic: two runs, identical bytes.
- `entry.png` — the edition itself, 1024×1024.
- `render.py` — the deterministic renderer that draws `entry.png` from `stories.json`.
- `stories.json` — the day's curated stories, each from Reuters/AP/BBC wire reports.

## Run

```sh
# the entry program, as the grader runs it:
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

# redraw the edition from the story data (needs Python 3 + Pillow):
python3 render.py
```

## License

MIT — see [LICENSE](LICENSE). The image is original work drawn by the renderer;
news facts are from wire reports of 19 November 2026.