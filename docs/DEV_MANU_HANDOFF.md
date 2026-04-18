# Handoff: dev/manu → main

**Date:** 2026-04-18
**Status:** dev/manu is done. This document explains how `notebooks/ruta_del_peso.py` (main's product) can absorb what dev/manu produced.

**TL;DR.** Main's dashboard is the product. dev/manu added data, a crosswalk, a depth audit, and editorial enrichment for flagship programs whose names don't surface in the CSV. Take what's useful, leave the rest.

---

## 1. What you can actually use

Five artifacts, in order of expected pitch-impact:

| Artifact | Path | What it unlocks |
|---|---|---|
| Editorial crosswalk | `crosswalk/crosswalk.csv` | Groups all 19,453 budget rows into 12 citizen-facing categories (Agua, Transporte público, Seguridad, …) with per-row rationale. Give Acto III a citizen-readable axis. |
| Named-programs supplement | `crosswalk/named_programs_2024.csv` | 81 flagship programs with pesos (Cablebús, Utopías, Pilares, Mi Beca, Altépetl, Cosecha de Lluvia, Comedores para el Bienestar, …) that do NOT surface as `desc_programa_presupuestario`. Extracted from Paquete Económico 2024 PDFs. Fixes the "where's Cablebús?" judge question. |
| Data-quality audit | `DATA_NOTES.md` | Published-headline gate PASSES (2024 aprobado = MXN 267,965,350,437 exact vs Decreto). Depth verdicts, schema stability across 7 years, alcaldía availability, gap disclosure. Trust-building content for a judge Q&A. |
| Clean Polars contract | `data/clean/*.parquet` + `data/clean/SCHEMAS.md` | Pre-aggregated `budget_tree`, `budget_by_alcaldia`, `income_sources`, `source_links` — ready-to-plot, with invariants documented. |
| Methodology note | `crosswalk/METHODOLOGY.md` | Spanish methodology (bucket choice, classification axis, overhead handling, alcaldía attribution, limitations). Reference when a judge asks "why is X in Y." |

---

## 2. Data that `scripts/download_data.sh` now fetches (post-merge)

Main's 9-dataset baseline PLUS dev/manu's enrichment. Everything idempotent (skips on re-run):

**Tier 1 (consumed by notebooks):** `egresos_2024_aprobado`, `egresos_2023_aprobado`, `egresos_2023_03_trimestre`, `rally_obras`.

**Tier 2 (Cuenta Pública 2018–2022 at `data/`):** `egresos_{2018..2022}_cp.csv`. Used by `ruta_del_peso.py` `EGRESOS_FILE_MAP`.

**Tier 3 (Ingresos):** `ingresos_main.csv` at `data/` (main's path) + `data/raw/ingresos_fuentes.csv` and `data/raw/ingresos_treemap.csv` (pre-aggregated citizen views — the source tudinero uses).

**Tier 4 (enrichment, `data/raw/`):** `egresos_2022_aprobado`, `egresos_2023_01_trimestre`, `egresos_2023_02_trimestre`, plus tudinero's own `a_donde_va`, `treemap_unidad`, `treemap_capitulo`, `como_cambia` pre-aggregates.

**Tier 5 (transferidos + federal obras):** `recursos_transferidos_alcaldias.xlsx`, `proyectos_federales_transferidos_2013_2022t1.csv` (23k → 115k georef'd obras superset of `rally_obras.csv`, adds 2019-2022), `entes_publicos_cdmx_2024.xlsx` (unidad-responsable catalog).

**Tier 6:** three XLSX data dictionaries.

**Tier 7:** 7 Paquete Económico 2024 PDFs that feed `crosswalk/named_programs_2024.csv`.

---

## 3. Insights the main product should know

### 3.1 Published-headline gate PASSES
`egresos_2024_aprobado.csv` sums to **MXN 267,965,350,437** — exact match to the CDMX Decreto de Presupuesto de Egresos 2024. No drift. Safe to display the total without a rounding disclaimer. See `DATA_NOTES.md` §2.

### 3.2 Alcaldía filter has two regimes
Main's current filter uses `desc_unidad_responsable.str.starts_with("Alcaldía")` — that covers **18.38% of the budget (MXN 49.25B across 16 alcaldías)**. The other ~82% is centralized (SEMOVI, SACMEX, SSC, etc.) and doesn't carry an alcaldía attribution in the row itself.

If you want a fuller alcaldía story: `data/clean/budget_by_alcaldia.parquet` attributes via `desc_unidad_responsable` heuristics and carries an `attribution_method` column per row (`"recursos_transferidos"` | `"heuristic_unidad_responsable"` | `"modeled"`) for honest disclosure. See `crosswalk/METHODOLOGY.md` §"Alcaldía."

### 3.3 Schema is stable across 7 years of egresos
2018 CP through 2024 aprobado share the same 63-column schema. One Polars loader covers all of them. This is why `ruta_del_peso.py`'s `EGRESOS_FILE_MAP` works.

### 3.4 Level 2 has 169 named programs, ~70–80% citizen-legible
`desc_programa_presupuestario` has 169 distinct values in 2024. About 120–135 are immediately citizen-legible (Mi Beca para Empezar, Servicio de Agua Potable, Programa Pilares, Sistema Penitenciario, …). The rest are bureaucratic (Servicios de apoyo administrativo, Operación) and should be rolled up or suppressed in Acto III's drilldown.

### 3.5 Flagship programs DO NOT surface at Level 2
**This is the gap `crosswalk/named_programs_2024.csv` fills.** "Cablebús," "Utopías," "Sembrando Parques" are not `desc_programa_presupuestario` values — they live at partida or anexo level. A judge asking "dónde está Cablebús" against `ruta_del_peso` as-is gets "no sale con ese nombre." The supplement has pesos for these from the Paquete Económico narrative.

### 3.6 Level 3 (specific obras with locations) is not in the main CSV
Confirmed not attempted — the egresos CSV does not carry obra-level names or coordinates. The only georef'd obra data is Rally 2013–2018 (now superseded by `proyectos_federales_transferidos_2013_2022t1.csv` through 2022). Different pot (federal), different years. Use as a labeled sibling view, not Level 3 of the current budget.

---

## 4. Concrete integration suggestions for `ruta_del_peso.py`

Ordered by ratio of pitch-impact to implementation cost. All numbered references are to line ranges in `notebooks/ruta_del_peso.py`.

### S1. Add "Proyectos emblemáticos" callout near Acto III (30 min)
**Why:** solves the "where's Cablebús?" gap. Biggest pitch-narrative win for least code.
**How:** new cell after Acto III's program bars (line ~659). Read `crosswalk/named_programs_2024.csv`, render top ~10 rows as a side panel: `display_name` · `ente_ejecutor` · `fmt_mxn(monto_aprobado_mxn)` · `section`. Link each to the Paquete Económico PDF (`source` column points at the file). Label the panel: "Estos programas no aparecen con ese nombre en la CSV oficial — vienen del Paquete Económico 2024."

### S2. Color programs in Acto III by citizen category (45 min)
**Why:** gives the program list a legible axis beyond monto.
**How:** left-join `ruta_del_peso.py`'s Acto III groupby (`desc_programa_presupuestario` → `budget`, `spent`) to `crosswalk/crosswalk.csv` on `desc_programa_presupuestario` → `display_name` (or `source_label`). Map `citizen_category` → a 12-color palette (one per bucket). Now the horizontal bars at line ~608 get a categorical color dimension matching the 12 buckets.

### S3. Display trust-badge total (10 min)
**Why:** cheap credibility win.
**How:** a small "✓ Suma exacta al Decreto: MXN 267,965,350,437" line near the Acto II kicker. See `DATA_NOTES.md` §2 for the exact number.

### S4. Add rationale tooltips to program rows (20 min)
**Why:** answers "why is X in Y" in-line.
**How:** Acto III's `_progs` dataframe (line ~588) joins to `crosswalk.csv` to pick up `rationale`. Pass `rationale` as `customdata` on the Plotly trace (line ~608), reference it in `hovertemplate`.

### S5. "Ver en datos oficiales" per row (20 min)
**Why:** traceability — the same "every number is clickable" affordance the PRD demanded.
**How:** `data/clean/source_links.csv` maps `source_id` → canonical URL. Render as a small `↗` icon after each program row. When a judge clicks, it opens the datos.cdmx.gob.mx record that backed that row.

### S6. Use `data/clean/budget_tree.parquet` as a shortcut for Acto III (60 min)
**Why:** skips the groupby + per_100 calculation at runtime.
**How:** it's pre-aggregated Level-1 (citizen_category) + Level-2 (named program) with `per_100_of_total`, `per_100_of_parent` computed. Add a "citizen-category view" toggle to Acto III that switches the axis from `desc_programa_presupuestario` to `citizen_category`, reading directly from this parquet. Contract documented in `data/clean/SCHEMAS.md`.

### S7. Expand alcaldía filter to full budget with disclosure (90 min, harder)
**Why:** moves alcaldía coverage from 18% to ~100% with honest caveats.
**How:** `data/clean/budget_by_alcaldia.parquet` carries attribution for the centralized ~82% via `attribution_method`. When `alcaldia_pick` is non-empty, swap the filter from `desc_unidad_responsable.starts_with("Alcaldía")` to a merge on `budget_by_alcaldia`. Render `attribution_method` somewhere visible so the judge knows this is attributed, not raw.

### S8. Bring in the federal-obras superset (optional)
**Why:** 115k geolocated obras 2013–2022 vs. the current 23k 2013–2018.
**How:** `data/raw/proyectos_federales_transferidos_2013_2022t1.csv` has the same schema as `rally_obras.csv`. `notebooks/obra_map.py` can point at it (or union both).

---

## 5. Files to consume

**Must-adopt (small, high-value):**
```
crosswalk/crosswalk.csv             # 19,453 rows → 12 citizen buckets
crosswalk/named_programs_2024.csv   # 81 flagship programs, pesos from PDFs
crosswalk/citizen_categories.md     # taxonomy with emojis + descriptions
crosswalk/METHODOLOGY.md            # Spanish methodology footnote
DATA_NOTES.md                       # data-quality audit (reference)
data/clean/SCHEMAS.md               # Polars contract
data/clean/*.parquet                # pre-aggregated outputs
data/clean/source_links.csv         # traceability
scripts/download_data.sh            # unified 7-tier superset (already merged)
```

**Optional (archive from dev/manu — keep or drop):**
```
notebooks/tus_100_pesos.py          # our parallel drill-down; overlaps Acto II/III
notebooks/lib/common.py + loaders.py  # shared helpers + Polars loaders with fixture fallback
notebooks/DESIGN_NOTES.md           # visual vocabulary (mirrors existing dashboards)
prd/                                # hackathon orchestration docs (internal process)
HANDOFFS.md                         # append-only log from the agent run
Dockerfile + fly.toml               # Marimo deploy configs
scripts/smoke_notebooks.sh          # py_compile sanity check
```

---

## 6. Known limits

- **No 2024 ejercido** — datos.cdmx.gob.mx has not published Q1/Q2/Q3 2024 trimestres as of 2026-04-18. Most recent real ejercido corpus is Cuenta Pública 2022.
- **No 2025 aprobado** on datos.cdmx.
- **Flagship pesos from PDFs are approximate** — some were extracted from narrative tables, some from prose. The `notes` column in `named_programs_2024.csv` cites page numbers.
- **Alcaldía attribution for the centralized 82%** is a modeling choice, not raw data. `METHODOLOGY.md` §"Alcaldía" documents it.
- **`data/clean/budget_tree.parquet` fixtures vs. reality** — file on disk is real Agent-1 output; `notebooks/lib/loaders.py` also ships an inline fixture for demos without the file. When the file is present it wins; a stderr warning fires if the loader falls back.

---

## 7. What dev/manu does NOT touch

- `mcp/` — main's data hub. No integration needed; orthogonal layer.
- `notebooks/obra_map.py` — main modified this (+103 lines). dev/manu didn't touch it.
- `notebooks/budget_dashboard.py`, `notebooks/explore.py` — frozen exhibits on both branches.

---

## 8. Re-running everything from scratch

```bash
git clone git@github.com:diegomondra/impact-lab-cdmx.git
cd impact-lab-cdmx
uv sync
bash scripts/download_data.sh                          # ~200 MB
uv run marimo run notebooks/ruta_del_peso.py           # main's product
```

`data/clean/*.parquet` is committed so the UI boots even if datos.cdmx.gob.mx is unreachable on pitch day.
