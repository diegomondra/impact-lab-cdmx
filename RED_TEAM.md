# Red team · "Las fugas"

> The counter-thesis to `notebooks/obra_map.py`.
> Same data, adversarial lens: where did the money *not* go?

## Run side-by-side with the main map

This repo is designed so both dashboards can run simultaneously on different ports, letting you flip between the two narratives in your browser.

### With git worktrees (recommended)

```bash
# From the main working copy
git worktree add ../impact-lab-cdmx-redteam -b red-team-accountability origin/red-team-accountability
cd ../impact-lab-cdmx-redteam
cp ../impact-lab-cdmx/data/*.csv data/     # reuse already-downloaded data
uv sync
uv run marimo run notebooks/fugas.py --port 2720 --host 127.0.0.1
```

Then in the main copy:

```bash
cd ../impact-lab-cdmx
uv run marimo run notebooks/obra_map.py --port 2718 --host 127.0.0.1
```

Open **http://localhost:2718** (warm story) and **http://localhost:2720** (red team) in two tabs.

### Without worktrees (branch switching)

If you only want to see the red-team dashboard, check out the branch directly:

```bash
git checkout red-team-accountability
uv sync
bash scripts/download_data.sh
uv run marimo run notebooks/fugas.py --port 2720
```

⚠️ Switching branches hides `notebooks/obra_map.py` — the worktree approach keeps both visible.

## Port convention

| Port | Dashboard | Branch |
|------|-----------|--------|
| 2718 | `notebooks/obra_map.py` — *Sigue tu peso* | `main` |
| 2720 | `notebooks/fugas.py` — *Las fugas* | `red-team-accountability` |

**Why not 2719?** That port is commonly taken by a second local marimo instance (e.g. an edit session). The red team sits on 2720 to avoid collisions with typical dev setups. Override with `--port <N>` if needed.

## The counter-thesis in three numbers

| Signal | Magnitude |
|--------|----------:|
| Share of contract money going to recipients marked *"no reportó información"* | **~86%** |
| Federal money ejercido in projects stuck <25% avance físico | **~$25.4 mmdp (36.7%)** |
| Beneficiarios claimed by projects costing <$1 per person | **~15.9 million** |

## Design intent

`obra_map` is **resident-facing** — warm palette, map-as-hero, drill-down on your street.
`fugas` is **journalist-facing** — dark palette, watchlist-as-hero, red flags first.

Both dashboards are honest about the same data window (2013–2018). They differ only in what they choose to highlight.

## When to run which

- **Community demo, policy pitch, citizen engagement** → `obra_map`
- **Accountability deep-dive, FOI letter drafting, journalist briefing** → `fugas`

---

Back to main README: [`README.md`](./README.md)
