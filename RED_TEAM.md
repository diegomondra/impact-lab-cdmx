# Red-team branch · "Patrones extraños"

> A forensic audit of the CDMX open-data files themselves.
> Curiosity-driven, not accusatory. Every finding comes with plausible innocent readings.

## What this branch adds

`notebooks/patrones.py` examines the same dataset (`rally_obras.csv`) used by the main map, but asks a different question: **does the published data hold together under its own rules?**

Four patterns surface. None is proof of wrongdoing — each is a starting point for a reporter's follow-up:

| Pattern | What we observe | Why it might be innocent | What a reporter would verify |
|---|---|---|---|
| **Benford deviation** | First digit *7* appears 15.6% of the time vs. 5.8% expected (+9.8pp) | Standard program amounts centered at $7M / $70k | Are these amounts clustered in one programa_presupuestario? |
| **Round-number clustering** | 12.6% of >$100k amounts are exactly divisible by $1M | Decreed ceilings, formulaic distribution | Is there a priced expediente técnico behind each? |
| **Coordinate duplicates** | 49 lat/long points host ≥3 distinct projects, totaling $61.5B | Default captures at alcaldía offices | Are these admin addresses or real worksites? |
| **Impossible dates** | 3,195 projects have completion < start date | Capture errors, DD-MM vs. MM-DD swaps | Does the system validate ranges at entry? |

## Run side-by-side with the main map

```bash
# Main branch
cd impact-lab-cdmx
uv run marimo run notebooks/obra_map.py --port 2718

# This branch (separate worktree)
git worktree add ../impact-lab-cdmx-redteam -b red-team-accountability origin/red-team-accountability
cd ../impact-lab-cdmx-redteam
cp ../impact-lab-cdmx/data/*.csv data/
uv sync
uv run marimo run notebooks/patrones.py --port 2720
```

Open **http://localhost:2718** (the warm map) and **http://localhost:2720** (the forensic view) in adjacent tabs.

## Design intent

`obra_map` is **resident-facing** — warm palette, map-as-hero, drill-down on your street.
`patrones` is **reporter-facing** — navy/gold palette, pattern-as-hero, explicit criteria for every claim, innocent readings alongside each finding.

Both dashboards are built on the same dataset. They differ in the questions they ask.

## Methodology

All analyses use only the published CSV file. No external data, no imputation.
Exact numeric criteria are in the notebook; reopen with `uv run marimo edit notebooks/patrones.py` to inspect or modify the thresholds.

Back to main README: [`README.md`](./README.md)
