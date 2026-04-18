# Red-team branch · "Patrones extraños"

> A forensic audit of the CDMX open-data files themselves.
> Curiosity-driven, not accusatory. Every finding comes with plausible innocent readings.

## What this branch adds

`notebooks/proveedores.py` examines the same dataset (`rally_obras.csv`) through a
supplier-and-procurement lens: **who got the contracts, how were they awarded, and
how concentrated is the spend?**

Four patterns surface. None is proof of wrongdoing — each is a starting point for a
reporter's follow-up:

| Pattern | What we observe | Why it might be innocent | What a reporter would verify |
|---|---|---|---|
| **The auditable universe** | Only 1,455 of 23,410 projects (6.2%) publish both modalidad de contratación and contratista | Data pipeline gap, not willful opacity | Why has disclosure degraded over time? Is the requirement enforced? |
| **Award modality mix** | Of the auditable 6%: 56% licitación pública, 32% adjudicación directa, 12% invitación a 3 | Legal mix permissible under LOPSRM for different amount tiers | Are AD amounts respecting legal ceilings? Where are the dictámenes de excepción? |
| **IR3 is a small club** | 170 invitation-only contracts went to just 12 unique suppliers; top 5 captured 98.4% | Few firms pre-qualified for the technical niche | Are the "3 invited" always the same? Who curates the eligible list? |
| **Convocante favorites** | 10+ convocantes concentrated ≥50% of their spend in a single supplier (Benito Juárez → ZM Construcción = 77 contracts, $362M, 57.9%) | Specialty suppliers, continuity contracts | Does the supplier also win for other convocantes? Any conflicts of interest? |

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
uv run marimo run notebooks/proveedores.py --port 2720
```

Open **http://localhost:2718** (the warm map) and **http://localhost:2720** (the forensic view) in adjacent tabs.

## Design intent

`obra_map` is **resident-facing** — warm palette, map-as-hero, drill-down on your street.
`patrones` is **reporter-facing** — navy/gold palette, pattern-as-hero, explicit criteria for every claim, innocent readings alongside each finding.

Both dashboards are built on the same dataset. They differ in the questions they ask.

## Methodology

All analyses use only the published CSV file. No external data, no imputation.
Exact numeric criteria are in the notebook; reopen with `uv run marimo edit notebooks/proveedores.py` to inspect or modify the thresholds.

Back to main README: [`README.md`](./README.md)
