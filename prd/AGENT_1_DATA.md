# Agent 1 — Data & Research

**Read first:** `prd/PRD.md`, then this file, then `data/clean/SCHEMAS.md` (written by Agent 2 in the first 30 minutes — wait for it, then collaborate on it).

**Before you start:** confirm Agent 0 has signed off `prd/GO_NO_GO.md`.

**Your working directories:** `data/`, `crosswalk/`, plus `DATA_NOTES.md` at repo root and `scripts/download_data.sh`.
**Files you own:** everything under those paths.
**Files you read but do not edit:** `prd/` (all files), `notebooks/` (including `notebooks/lib/`), `pyproject.toml`.

---

## Your job in one sentence

Get every budget dataset this project needs, clean it into Polars-friendly shapes the Marimo UI can consume, and produce the editorial crosswalk that maps raw budget lines to citizen-facing categories and named programs.

You are the project's spine. The whole demo depends on the depth you can pull out of the budget data. If Level 2 is thin or alcaldía data is unusable, the whole team has to adjust — and it's your job to tell them early.

## The data depth you can expect (from AUDIT.md — confirm once data is live)

- **Level 1 (citizen categories):** achievable. Clean editorial mapping from `desc_funcion` / `desc_unidad_responsable` into ~12 buckets.
- **Level 2 (named programs):** achievable via `desc_programa_presupuestario`. Spot-check on 20 rows whether the names are citizen-legible (Pilares, Cablebús, Mi Beca, etc.) or purely bureaucratic ("Servicios de apoyo administrativo") — your hour-0 job.
- **Level 3 (specific obras with names and locations):** NOT achievable from the main budget CSV. The PRD's strict-three-level ambition has been reshaped (see `prd/GO_NO_GO.md`) to: Level 1 + Level 2 + alcaldía filter (data-dependent) + `obra_map.py` as a linked sibling view ("¿Qué se construyó en tu calle?" using Rally 2013–2018 federal data).
- **Alcaldía:** the approved-budget CSVs likely do not carry an alcaldía column. Alcaldía-level slicing depends on the separate Recursos Transferidos dataset, which covers transfers only. Confirm at hour 0.

## Deliverables (in order)

### Hour 0–1: Data acquisition, inventory, and depth assessment

Run the existing `scripts/download_data.sh` — it already curls:
- `egresos_2024_aprobado.csv`
- `egresos_2023_aprobado.csv`
- `egresos_2023_03_trimestre.csv` (has `monto_ejercido`)
- `rally_obras.csv` (2013–2018 georeferenced federal projects)

**Extend `scripts/download_data.sh`** to add:
- CDMX Ingresos (https://datos.cdmx.gob.mx/dataset/ingresos) — "Ingresos de la Ciudad (2018-2024)" CSV
- Recursos Transferidos a Alcaldías — grab the CSV from datos.cdmx.gob.mx linked from https://tudinero.cdmx.gob.mx/informacion/recursos_transferidos_alcaldias_v. Confirm year coverage.
- Data dictionaries for any of the above where available (`.pdf` or `.csv`). Save into `data/raw/dictionaries/`.
- Opportunistic: if CDMX has published a 2024 trimestre with ejercido since this morning, grab it.

**Hour 0 depth-check, non-negotiable.** Within 30 minutes of touching the main CSV, answer in `DATA_NOTES.md`:
- How many rows in each dataset?
- What columns are present? Confirm or deny the schema inferred in `prd/AUDIT.md`.
- Sample 20 rows from different `desc_funcion` values — how many `desc_programa_presupuestario` values are citizen-recognizable? Paste the 20 rows' `desc_programa_presupuestario` values directly into `DATA_NOTES.md`.
- Is there an alcaldía / `cve_alcaldia` / geographic field in any egresos CSV?
- What's the total `monto_aprobado` for 2024? It should roughly match the CDMX published headline (confirm in `DATA_NOTES.md` — mismatches > 1% are a BLOCKER).

If Level 2 names turn out to be mostly bureaucratic junk, notify the team lead and Agent 3 via `HANDOFFS.md` immediately. The demo reshapes around whatever depth is actually there.

**Output by end of hour 1** — `DATA_NOTES.md` at repo root:
- One section per dataset: URL, file size, row count, date range, key columns.
- Published-headline check.
- DEPTH ASSESSMENT section with the hour-0 findings.
- ALCALDÍA AVAILABILITY section.
- BLOCKERS section.

### Hour 1–2: Level 1 — Citizen-category taxonomy + crosswalk

Produce `crosswalk/citizen_categories.md` listing the ~12 categories with:
- Category name (Spanish)
- One-sentence citizen-facing description ("El agua que llega a tu casa")
- Expected programs / dependencies that map here
- Display icon (emoji)

Starting taxonomy from the PRD — refine based on live data:
Agua · Transporte público · Calles y banquetas · Basura y limpia · Parques y espacios públicos · Seguridad · Justicia · Salud · Educación · Apoyos sociales · Cultura y deporte · Medio ambiente · Alumbrado · Gobierno y administración · Deuda

Then populate `crosswalk/crosswalk.csv`. Every row in the source budget CSV should map to exactly one citizen_category (or "other"). Columns:

```
source_id, source_label, source_parent, level, citizen_category, display_name, rationale
```

- `source_id` — the native budget-row key (combine `cve_programa_presupuestario` + `cve_unidad_responsable` if necessary; document the convention in `crosswalk/citizen_categories.md`)
- `source_label` — raw name from the CSV
- `source_parent` — null for Level 1, citizen_category for Level 2
- `level` — 1 or 2 (Level 3 is not attempted; see hour 3 for the alcaldía/obra_map path)
- `citizen_category` — one of the ~12 Level-1 buckets
- `display_name` — what the user sees (cleaned-up)
- `rationale` — one short sentence, REQUIRED, no exceptions

Emit `data/clean/budget_tree.parquet` v1 containing Level-1 aggregates per citizen_category with total `monto_aprobado` (and `monto_ejercido` if the chosen year has it). Exact schema: coordinate with Agent 2 via `data/clean/SCHEMAS.md`.

### Hour 2–3: Level 2 — Named programs

For every citizen_category, identify the named programs / dependencies that are citizen-recognizable. Examples:

- Agua → SACMEX Operación, Sectorización Iztapalapa, Drenaje profundo
- Transporte → Metro mantenimiento, Cablebús L3, RTP, Metrobús
- Apoyos sociales → Mi Beca para Empezar, Pensión adultos mayores, Pilares

Add these as Level-2 rows in `crosswalk.csv`. `display_name` is human-friendly. `rationale` is required.

A row is Level 2 if and only if: it has a name a citizen could plausibly recognize, or it's a large enough aggregate that citizens would want to know about it. Everything smaller rolls up to "Otros" within its citizen_category.

Rebuild `data/clean/budget_tree.parquet` with the 2-level hierarchy plus cumulative percentages. Confirm the updated schema with Agent 2.

### Hour 3–4: Alcaldía filter + source links + sibling map

**Alcaldía:** using Recursos Transferidos (or heuristics from `desc_unidad_responsable` if that's all we have), produce `data/clean/budget_by_alcaldia.parquet`. Document any assumptions in `crosswalk/METHODOLOGY.md`. If alcaldía data is unusable, declare in `HANDOFFS.md` and drop the filter — Agent 3 will hide it.

**Source links:** produce `data/clean/source_links.csv`:
```
source_id, url, label
```
Every crosswalk row that appears in the UI should have at least one link that resolves to a canonical record on datos.cdmx.gob.mx or tudinero.cdmx.gob.mx. Spot-test 10 links — if any 404, fix or drop.

**Rally sibling view:** you don't build the UI, but confirm `rally_obras.csv` is clean and that `obra_map.py` still runs against it (it should — no code changes required by you). If the Rally dataset has moved or schema-drifted, flag in `HANDOFFS.md`.

### Hour 4–5: Ingresos + methodology

**Ingresos:** clean the downloaded ingresos CSV into `data/clean/income_sources.parquet`. Aggregate to a digestible top-level breakdown (ISR federal participaciones, impuestos locales, derechos, aprovechamientos, etc.). This feeds the footer, not a full view.

**Methodology:** write `crosswalk/METHODOLOGY.md` — 1 page, Spanish, covers:
- How the 12 citizen categories were chosen
- Which classification axis (functional / administrative / programmatic) was the primary
- How "Gobierno y administración" was handled (don't let overhead hide)
- How alcaldía attribution was done (if done)
- Line items excluded, and why
- Known limitations — include the explicit "Level 3 not attempted because source data does not carry obra-level labels" note

### Hour 5–6: Standby

Sit next to Agent 3 and answer data questions in real time. Most common: "what's the display_name for X?" and "why is Y in Z category?" — both findable in `crosswalk.csv`'s `rationale` column.

## Rules of engagement

- **Commit early, commit often.** Raw CSVs go into `data/raw/` within 30 minutes of downloading. Never keep data local-only — `data/` contents are gitignored by default, so either carve an exception in `.gitignore` for `data/clean/` and `data/raw/` (coordinate with Agent 2 via HANDOFFS.md) or push as a data-bundle artifact. The team lead's laptop dying mid-hackathon must not end the project.
- **No cleaning without a trail.** Every transformation lives in a script under `scripts/` or `data/scripts/`, with a comment explaining why. No stealth mutations.
- **Flag blockers loudly.** If a dataset is missing, broken, or the depth-check fails, prefix your line in `HANDOFFS.md` with `BLOCKER:`. The lead reads HANDOFFS, not your head.
- **Don't editorialize alone.** Crosswalk judgment calls benefit from a one-minute chat with the lead. `rationale` is a conversation, not a monologue.
- **Column names are load-bearing.** Don't rename columns between v1 and v2 of a parquet file without telling Agent 2 — they maintain `SCHEMAS.md` which Agent 3 reads.
- **Traceability is a product feature.** Every row in `budget_tree.parquet` must trace back to specific rows in the source CSV via `source_id`, and map to a URL in `source_links.csv`.

## What "done" looks like

By hour 5:
- Download script extended; 6+ datasets committed under `data/raw/`
- `crosswalk.csv` with Level-1 and Level-2 rows, every row with a rationale
- `crosswalk/citizen_categories.md` with human descriptions + emojis
- `data/clean/budget_tree.parquet`, `budget_by_alcaldia.parquet` (if viable), `income_sources.parquet`
- `data/clean/source_links.csv` with working URLs
- `crosswalk/METHODOLOGY.md` in Spanish
- `DATA_NOTES.md` up to date
- 0 open BLOCKERS

## Don't do

- Don't scrape anything behind auth.
- Don't try to model tax incidence — explicitly ruled out.
- Don't chase Locatel, FGJ, or any complaint data — out of scope.
- Don't invent data. If a program doesn't have a name, either find it in a supplementary source or roll it up to "Otros" with a rationale.
- Don't rebuild Agent 3's aggregation logic. You own the Polars pipelines; they own the Marimo cells.
- Don't spend more than 20 minutes on any single dataset before asking for help.
- Don't expose raw accounting codes in `display_name`. If all you have is "3411," the row shouldn't exist at Level 2 — roll it up.
- Don't edit `notebooks/` — you read, you don't write there.
