# SCHEMAS — `data/clean/`

**Maintainer:** Agent 2 (Integrator). **Readers:** Agent 1 (emits these files), Agent 3 (consumes via `notebooks/lib/loaders.py`).

This is the contract. Columns, types, and semantics are frozen on publish. Append-only changes until hour 3; after that, schema changes require a `HANDOFFS.md` migration note and a sign-off from both Agents 1 and 3.

All parquet files are written by Agent 1 from `crosswalk/crosswalk.csv` joined to `data/egresos_*.csv`. All pesos are MXN nominal (no deflation). All percentages are stored as `float64` on the 0–100 scale (not 0–1).

Canonical ordering of citizen categories (used wherever the UI surfaces them): `Agua · Transporte público · Calles y banquetas · Basura y limpia · Parques y espacios públicos · Seguridad · Justicia · Salud · Educación · Apoyos sociales · Cultura y deporte · Medio ambiente · Alumbrado · Gobierno y administración · Deuda · Otros`.

---

## `budget_tree.parquet`

The backbone of the app. Level-1 (citizen category) + Level-2 (named program) rows for each fiscal year available.

**Columns**

| column | type | nullable | notes |
| --- | --- | --- | --- |
| `source_id` | `str` | no | stable crosswalk row id; unique within a `year`. Kebab-case slugs like `L1-transporte`, `L2-cablebus-l3`. |
| `level` | `int32` | no | 1 (citizen category) or 2 (named program). |
| `citizen_category` | `str` | no | one of the ~15 canonical Level-1 buckets (see ordering above). For Level-1 rows this is also the row's display identity. |
| `display_name` | `str` | no | what the UI renders. For Level 1 this equals `citizen_category`. For Level 2 this is a cleaned-up program name (e.g. "Cablebús Línea 3"). |
| `parent_id` | `str` | yes | null for Level 1; the Level-1 `source_id` for Level 2. |
| `icon` | `str` | yes | single emoji for Level 1; null for Level 2. |
| `monto_aprobado` | `float64` | no | pesos, approved. Sum of matched source rows from `egresos_<year>_aprobado.csv`. |
| `monto_ejercido` | `float64` | yes | pesos, exercised. Null if the chosen year has no trimestre dataset with `monto_ejercido`. |
| `per_100_of_total` | `float64` | no | percent of the citywide total for this `year`. Level-1 rows sum to ~100. |
| `per_100_of_parent` | `float64` | yes | percent of the parent's `monto_aprobado`. Null for Level 1. Level-2 rows sharing a `parent_id` sum to ~100 within rounding. |
| `rationale` | `str` | no | short sentence from `crosswalk.csv`. Required. |
| `year` | `int32` | no | fiscal year this row describes. |

**Invariants (Agent 2 will validate at hour 2 and again at hour 4)**

- Sum of `monto_aprobado` over all Level-1 rows for a given `year` matches the published CDMX headline within 0.5%.
- For every Level-2 row, `parent_id` resolves to a Level-1 row with the same `year` and `citizen_category`.
- Sum of `monto_aprobado` over Level-2 rows with the same `parent_id` is ≤ the parent's `monto_aprobado` (the remainder rolls up into an implicit "Otros" or is carried at Level 1 only).
- `per_100_of_total` values for Level-1 rows sum to between 99.0 and 101.0 within a year.

**Provenance.** One row per crosswalk row per year. Agent 1 rebuilds the file end-to-end on every crosswalk change; no incremental patches.

---

## `budget_by_alcaldia.parquet` *(conditional — only if alcaldía data proves viable)*

Alcaldía-axis slice of the same hierarchy. Viability decision is Agent 1's at hour 1 — the file may simply not exist, in which case `load_budget_by_alcaldia()` returns `None` and Agent 3 hides the filter.

**Columns**

| column | type | nullable | notes |
| --- | --- | --- | --- |
| `source_id` | `str` | no | matches a `source_id` in `budget_tree.parquet` (same year). |
| `level` | `int32` | no | 1 or 2. |
| `alcaldia` | `str` | no | alcaldía name, Title Case ("Iztapalapa", "Cuauhtémoc"). 16 canonical values. |
| `citizen_category` | `str` | no | mirrors `budget_tree`. |
| `display_name` | `str` | no | mirrors `budget_tree`. |
| `monto_aprobado` | `float64` | no | pesos attributable to this (source_id, alcaldía) pair. |
| `monto_ejercido` | `float64` | yes | pesos exercised, if available. |
| `per_100_of_alcaldia_total` | `float64` | no | percent of this alcaldía's citywide-budget slice. |
| `attribution_method` | `str` | no | `"recursos_transferidos"` \| `"heuristic_unidad_responsable"` \| `"modeled"`. For methodology disclosure. |
| `year` | `int32` | no | fiscal year. |

**Invariants**

- For a given `year`, sum of `monto_aprobado` over all (source_id, alcaldía) pairs is ≤ the `budget_tree.parquet` citywide total. Gaps are expected (non-attributable spend) and disclosed in `crosswalk/METHODOLOGY.md`.
- `alcaldia` values are from the 16 CDMX alcaldías — no "Sin alcaldía" category at this layer. Unattributable spend is excluded, not placed in a bucket.

---

## `income_sources.parquet`

Footer section — "¿De dónde viene el presupuesto?" — small table, not a full view.

**Columns**

| column | type | nullable | notes |
| --- | --- | --- | --- |
| `source_id` | `str` | no | stable id, e.g. `ING-isr-participaciones`. |
| `display_name` | `str` | no | human label (e.g. "ISR y participaciones federales"). |
| `category` | `str` | no | one of: `federal_participaciones`, `federal_aportaciones`, `impuestos_locales`, `derechos`, `aprovechamientos`, `productos`, `financiamiento`, `otros`. |
| `monto` | `float64` | no | pesos, ingreso recaudado (or estimado). |
| `per_100_of_total` | `float64` | no | percent of the total ingreso for the year. Sums to ~100. |
| `year` | `int32` | no | fiscal year. |

**Provenance.** Source: `data/raw/ingresos_cdmx_2018_2024.csv` (Agent 1). One row per aggregated category per year; rows are aggregated, not row-per-line-item — Agent 1 does the rollup in a documented script under `data/scripts/`.

---

## `source_links.csv`

Row-level traceability. Every Level-1 and Level-2 row in the UI renders a "Ver en datos oficiales" link sourced here.

**Columns**

| column | type | notes |
| --- | --- | --- |
| `source_id` | `str` | matches `budget_tree.parquet.source_id`. |
| `url` | `str` | canonical URL on `datos.cdmx.gob.mx`, `tudinero.cdmx.gob.mx`, or a direct CSV download. Must resolve (Agent 1 spot-tests 10 at hour 4). |
| `label` | `str` | short link text; optional display helper. |

**Loader shape.** `load_source_links()` returns a `dict[str, str]` mapping `source_id → url`. If multiple rows exist per `source_id`, the first wins; Agent 1 commits to one canonical URL per `source_id`.

---

## Fixture fallback (loader behavior)

Every loader in `notebooks/lib/loaders.py` falls back to a small inline fixture if the real file is not present, and prints a loud warning to stderr. Fixtures exist so Agent 3 can build against a stable shape from minute zero — they are **not** demo-safe, and the warning makes that obvious. See `notebooks/lib/loaders.py` for the fixture values.

## Change log

- **v1 — 2026-04-18 (hour 0–1)**: initial schemas authored by Agent 2 pre-data. Column names are best-guess; Agent 1 reviews on first emission and files drift in `HANDOFFS.md`.
