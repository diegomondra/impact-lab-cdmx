---
name: Go / No-Go
description: Agent 0's final one-page readout for the human lead. Green-light issued 2026-04-18.
type: project
---

# Go/No-Go — 2026-04-18 (final)

**Status: GREEN.** Launch Agents 1, 2, 3 in parallel whenever ready.

## What changed since the preliminary version

Human lead answered the blocking questions:
- **Q0: Keep Marimo** (Option A). No Next.js. Existing `budget_dashboard.py` + `obra_map.py` remain in the repo as frozen exhibits.
- **Q7: Single lead** (no 5-person crew). Agent 2's "monitor human teammates" section is gone.
- **Q6: Just go.** Launch when ready.

Briefs fully rewritten. See `prd/CHANGELOG.md`.

## Green lights

- Stack locked: Python 3.11 + Marimo + Polars + Plotly + uv. Repo already scaffolded. `uv sync` + `bash scripts/download_data.sh` is the start line.
- Two working reference dashboards (`budget_dashboard.py`, `obra_map.py`) provide the guinda visual vocabulary Agent 3 inherits via `notebooks/lib/common.py`.
- Budget-CSV schema supports Level 1 + Level 2 ambition. `desc_programa_presupuestario` is the Level-2 name field.
- Rally obras CSV already wired in `obra_map.py` — powers the "¿Qué se construyó en tu calle?" sibling moment.
- CDMX open-data portal reachable. 2024 aprobado, 2023 aprobado, 2023 Q3 trimestre, ingresos, recursos transferidos all available.
- Three-agent parallelism is preserved: Data / Integrator / Builder. File-level turf is clean (see PRD §8).

## Yellow — proceed with caveats

- **Level 3 strict drill-down is dropped.** Agent 0 decided per "just go" authorization. Replaced with (a) alcaldía filter — data-dependent — and (b) linked `obra_map.py` sibling view. This is reflected in Agent 1's and Agent 3's briefs and in PRD §11 (question Q9 resolution). If the lead disagrees, flag now.
- **Alcaldía filter is conditional on Agent 1's hour-0 finding.** The approved-budget CSV likely has no alcaldía column; viability depends on Recursos Transferidos or `desc_unidad_responsable` heuristics. Loader returns None if cut; Agent 3 hides the control.
- **Year choice deferred** to Agent 1's hour-0 output. Existing dashboards already support a year picker. Pitch narrative can ride either 2024 aprobado (promises) or 2023 Q3 (real ejercido).
- **`data/` is gitignored.** Agent 1 must coordinate with Agent 2 (via `HANDOFFS.md`) on whether to carve a `data/clean/` exception so the deployed demo ships the files, or whether the deploy target runs the download script on build.
- **Dataset URLs in `download_data.sh` not HEAD-probed today.** Agent 1's literal first move is to run the script and flag any 404s.
- **The existing `budget_dashboard.py` has a donut chart.** Agent 3's new notebook does not — the pie/donut ban applies to `tus_100_pesos.py` only. The existing file is frozen; don't edit it.

## Red — blockers

**None.** Greenlight issued.

## Depth achievability

- **Level 1 (citizen categories):** achievable.
- **Level 2 (named programs):** achievable via `desc_programa_presupuestario`, pending Agent 1's hour-0 name-legibility spot-check on 20 rows.
- **Level 3 (specific obras):** NOT attempted. Reshape: alcaldía filter (if viable) + Rally sibling view.

## Recommended start order

1. **Agent 2 starts first** (hour 0:00). First 30 minutes: extract shared helpers from existing dashboards → `notebooks/lib/common.py`, write `data/clean/SCHEMAS.md` v1, stub `notebooks/lib/loaders.py` with fixture fallbacks.
2. **Agent 1 starts in parallel** (hour 0:00). First 30 minutes: run `scripts/download_data.sh`, hour-0 depth check on live CSVs, write `DATA_NOTES.md`.
3. **Agent 3 starts at 0:30** once SCHEMAS.md and loaders stub exist. Builds against loader fixture fallbacks until real files land.

No agent blocks on any other for its first move.

## One-line dispatch prompts

For when the lead launches each worker session:

- **Agent 1:** "You are Agent 1 — Data & Research. Read `prd/PRD.md`, then `prd/AGENT_1_DATA.md`, then `prd/AUDIT.md`. Start with `scripts/download_data.sh` and the hour-0 depth check."
- **Agent 2:** "You are Agent 2 — Integrator & Deploy. Read `prd/PRD.md`, then `prd/AGENT_2_ARCHITECT.md`. Start by extracting shared helpers from `notebooks/budget_dashboard.py` and `notebooks/obra_map.py` into `notebooks/lib/common.py`. Do NOT edit the two source notebooks."
- **Agent 3:** "You are Agent 3 — Builder. Read `prd/PRD.md`, then `prd/AGENT_3_BUILDER.md`, then skim `notebooks/budget_dashboard.py` and `notebooks/obra_map.py` for visual vocabulary. Wait for `data/clean/SCHEMAS.md` before writing code. Build `notebooks/tus_100_pesos.py`."

## Files produced this pass

- `prd/AUDIT.md` (Step 1 + 2 output)
- `prd/QUESTIONS_FOR_HUMAN.md` (now resolved)
- `prd/CHANGELOG.md` (every edit logged)
- `prd/GO_NO_GO.md` (this file, final)
- `prd/PRD.md` edited §7, §8, §9, §11 — sections 1, 2, 4 preserved intact
- `prd/AGENT_1_DATA.md` rewritten for Marimo + parquet outputs
- `prd/AGENT_2_ARCHITECT.md` rewritten for Integrator & Deploy role
- `prd/AGENT_3_BUILDER.md` rewritten for Marimo drill-down
