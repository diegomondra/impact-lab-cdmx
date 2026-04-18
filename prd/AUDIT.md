---
name: Audit
description: Repo + external-world inventory produced by Agent 0 on 2026-04-18.
type: reference
---

# AUDIT — 2026-04-18

Scratch inventory. Bullets, not prose.

## Repo state (working dir: `impact-lab-cdmx/`, branch `dev/manu`)

**Top-level files**
- `README.md` — "Claude Mexico City Lab 2026" landing page. Already names three dashboards: `obra_map.py`, `budget_dashboard.py`, `explore.py`. Onboarding via `uv sync` + `bash scripts/download_data.sh` + `uv run marimo run …`.
- `pyproject.toml` — Python ≥3.11, deps: marimo ≥0.10, polars ≥1.0, pandas ≥2.2, plotly ≥5.24, altair ≥5.4, pyarrow ≥18, numpy/scipy/scikit-learn.
- `uv.lock` present.
- `.gitignore` — `data/*` ignored except `.gitkeep` and `README.md`. Outputs/PNGs ignored. `.claude/` ignored.

**Directories**
- `data/` — empty (`.gitkeep`, `README.md`). No CSVs downloaded yet. Contents are gitignored.
- `db/` — empty. Purpose unclear (sqlite scratch? unused?).
- `notebooks/` — three Marimo apps already built:
  - `budget_dashboard.py` (~550 lines) — loads `egresos_2023/2024_aprobado.csv` + `egresos_2023_03_trimestre.csv`. UI: KPI cards, top-15 funciones horizontal bars (budget vs ejercido), top-15 unidades, ODS breakdown, **capítulo donut chart (PRD explicitly bans donuts)**, free-text search. CDMX guinda branding `#9F2241`, Inter font, hero gradient.
  - `obra_map.py` (~560 lines) — loads `rally_obras.csv`. Filters: alcaldía, ramo federal, ciclo (2013–2018), status. Plotly scatter_map of 23k points. Detail card on click (name, address, monto aprobado/ejercido/pagado, contratista, contract PDF link).
  - `explore.py` — generic CSV explorer.
- `scripts/download_data.sh` — `curl`s 4 CSVs: `egresos_2024_aprobado.csv`, `egresos_2023_aprobado.csv`, `egresos_2023_03_trimestre.csv`, `rally_obras.csv`. URLs fresh as of 2026-04-18.
- `prd/` — PRD + 4 agent briefs (this doc added to it).

**Not present (expected by briefs but missing)**
- `/api/` — nothing
- `/web/` — nothing
- `package.json`, `node_modules/`, `next.config.*` — nothing
- `CONTRACTS.md`, `HANDOFFS.md`, `DATA_NOTES.md`, `/crosswalk/` — nothing
- `.env*` — nothing

**Git history (`git log --all --oneline`)**
```
ad53ffd Rewrite README as a 3-command onboarding path
9bf31b1 Add interactive map of federal investment projects in CDMX
6dcc91a Add CDMX budget allocation dashboard
77a5b1d Initial scaffold: Marimo + Polars + Plotly for CSV exploration
```
Branches: `main`, `origin/main`, `origin/dev`, `dev/manu` (checked out).

## Budget CSV schema (inferred from `budget_dashboard.py`)

Columns confirmed present in `egresos_*_aprobado.csv` and `egresos_2023_03_trimestre.csv`:
- `desc_funcion` (functional classification, e.g. "Protección Social")
- `desc_unidad_responsable` (agency name)
- **`desc_programa_presupuestario`** (programmatic name — the Level-2 candidate)
- `desc_capitulo` (chapter: sueldos / obra pública / transferencias / etc.)
- `desc_partida_especifica` (accounting partida — **PRD says don't expose this level**)
- `objetivo_desarrollo_sostenible`, `desc_objetivo_desarrollo_sostenible`
- `monto_aprobado`, `monto_modificado`, `monto_ejercido`

**No alcaldía column in the approved-budget CSVs.** (Not inferred from code — will need to confirm once data is downloaded, but dashboard code does not reference one.)

## Rally obras CSV schema (from `obra_map.py`)

- `id`, `nombre_proyecto`, `desc_ramo` (federal source), `desc_alcaldia`, `desc_localidad`, `direccion_proyecto`
- `monto_aprobado`, `monto_ejercido`, `monto_pagado`
- `avance_fisico`, `poblacion_beneficiada`
- `latitud`, `longitud`, `ciclo`
- `contratista`, `url_contrato`, `justificacion`

**23k rows, 2013–2018 only.** Federal money flowing into CDMX — not the city's own approved budget. Different pot, different years.

## Dataset status (external-world probe, 2026-04-18)

- `[OK]` datos.cdmx.gob.mx/dataset/presupuesto-de-egresos — 2024 aprobado CSV published 2024-02-13. `¿A dónde va?` by sectores / unidad / capítulo also available. **No 2024 modificado, no 2024 ejercido, no Cuenta Pública 2024, no 2025 data.**
- `[OK]` datos.cdmx.gob.mx/dataset/ingresos — "Ingresos de la Ciudad (2018-2024)" last updated 2024-08-06. Two "¿De dónde viene el presupuesto?" resources.
- `[OK]` tudinero.cdmx.gob.mx/informacion/recursos_transferidos_alcaldias_v — page reachable, redirects to datos.cdmx for the dataset download. Format/year coverage not yet verified at the resource level.
- `[UNVERIFIED]` download script URLs — unique resource UUIDs; not HEAD-probed. Script is from today's initial scaffold so presumed live.

## DEPTH ACHIEVABILITY

Tight conclusion from the budget CSV schema as used in `budget_dashboard.py`:

- **Level 1 — Citizen categories (~12 buckets): ACHIEVABLE.** `desc_funcion` + `desc_unidad_responsable` give enough signal to crosswalk into citizen categories. Clean mapping is editorial work (Agent 1), not a data-availability problem.
- **Level 2 — Named programs: ACHIEVABLE.** `desc_programa_presupuestario` is the right field. Dashboard's search UI already hits it. Expect to find recognizable names (Pilares, Mi Beca, Cablebús, Metro mantenimiento, etc.) — needs hour-0 spot-check once the CSV is downloaded.
- **Level 3 — Specific obras with names and locations: NOT ACHIEVABLE from the main budget CSV.** The next level below `desc_programa_presupuestario` is `desc_partida_especifica` — accounting-level ("material de oficina," "servicios de energía eléctrica"). PRD §2 explicitly says "Don't expose '3411' to a user." No obra-name field, no geolocation field, no address field.
- **Level 3 via Rally `rally_obras.csv`: PARTIALLY ACHIEVABLE BUT MISLEADING.** Rally has 23k named, geolocated projects with `monto_ejercido` and contract URLs. But it's federal money, 2013–2018, not CDMX's own current-year budget. Splicing it under the 2024 approved budget misrepresents which pesos funded which obra. Use only as a clearly-labeled sibling view ("¿Qué se construyó en tu calle? — obras federales 2013–2018"), not as Level 3.

**Recommendation:** reshape Level 3 from "specific obras under every program" to "alcaldía filter as the depth axis" — re-query the Level 1 grid filtered to spending associable with a selected alcaldía. This is the PRD's stretch goal; it becomes the primary differentiator if Level 3 is cut. Caveat: the approved budget CSV likely does not carry an alcaldía column, so alcaldía-level slicing requires the separate Recursos Transferidos a Alcaldías dataset, which is about transfers (not the whole budget). Needs hour-0 schema confirmation.

## Stack conflict (CRITICAL — requires human sign-off)

The PRD defaults and Agent 2's brief assume Next.js 14 + TypeScript + Tailwind + shadcn/ui + Vercel, no DB, everything as static JSON served by Next API routes. The three-agent topology (Data / API / Builder) relies on a clean API seam.

The repo is Python 3.11 + Marimo + Polars + Plotly + uv. Marimo apps are single-file reactive Python notebooks with no separate API/frontend. Two working dashboards already ship with editorial polish (`budget_dashboard.py`, `obra_map.py`) in the same problem space.

The two paradigms don't compose cleanly:
- Switching to Next.js throws away ~1,100 lines of running Marimo code, the download script, and the entire uv toolchain — bad opportunity cost given a 6h budget.
- Keeping Marimo collapses the three-agent topology: no API seam, no separate `/web/`, nothing for Agent 3 to build against Agent 2's fixtures.
- Hybrid (Python builds `/data/clean/*.json`, Next.js serves it, Marimo retained only for exploration) preserves the three-agent shape but adds a second toolchain and a second deploy target under time pressure.

This is not Agent 0's decision. Escalating to the human team lead via `QUESTIONS_FOR_HUMAN.md` and `GO_NO_GO.md`.

## Data-not-downloaded caveat

`data/` is empty. Every depth assertion above that depends on row-level content (actual program names, presence or absence of alcaldía column) is inferred from the existing dashboard code, not from the live CSV. Agent 1's hour-0 depth-check must confirm.

## Open follow-ups

- Confirm `desc_programa_presupuestario` values include citizen-recognizable names on a 20-row sample (hour 0).
- Confirm whether `egresos_*_aprobado.csv` carries any alcaldía / geographic field.
- Inspect `db/` directory — empty today but present with an odd name; may be a placeholder the humans will fill.
- Verify `scripts/download_data.sh` URLs actually resolve when run on Saturday morning.
- Decide whether to add `egresos_2024_03_trimestre.csv` or similar if CDMX has published a 2024 trimestre with ejercido.
