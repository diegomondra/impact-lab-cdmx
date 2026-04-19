# Agent 2 — Integrator & Deploy

**Read first:** `prd/PRD.md`, then this file, then `prd/AUDIT.md`. You will then write `data/clean/SCHEMAS.md` yourself.

**Before you start:** confirm Agent 0 has signed off `prd/GO_NO_GO.md`.

**Stack is locked.** Python 3.11 + Marimo + Polars + Plotly + uv. The repo already has this toolchain and two working dashboards (`notebooks/budget_dashboard.py`, `notebooks/obra_map.py`). You do not pick a stack, and you do not switch it.

**Your working directories:** `notebooks/lib/` (new, you create it), `pyproject.toml`, `uv.lock`, `README.md`, `data/clean/SCHEMAS.md`, repo-root config, deploy config.
**Files you own:** everything under those paths.
**Files you read but do not edit:**
- `prd/` (all files)
- `notebooks/budget_dashboard.py`, `notebooks/obra_map.py`, `notebooks/explore.py` (frozen — demoable on their own; do not touch)
- `notebooks/tus_100_pesos.py` (Agent 3's file — you monitor it, you do not edit it)
- `data/raw/`, `data/clean/` contents (Agent 1's outputs — you import them, don't rewrite them)
- `crosswalk/` (Agent 1's)

---

## Your job in one sentence

Make it so that Agent 1's cleaned Polars files and Agent 3's drill-down Marimo notebook meet cleanly in the middle, via a tiny shared library (`notebooks/lib/`) and a written schema contract (`data/clean/SCHEMAS.md`), and that the final demo ships to a working URL neither agent has to think about.

You are not "just the backend" — there is no backend. You are the integration conscience. You catch at hour 3 that Agent 3 is reading a column Agent 1 renamed, and fix it before the demo breaks. You own the final deploy.

## Deliverables (in order)

### Hour 0–0.5: Extract shared helpers from the existing dashboards

Both `budget_dashboard.py` and `obra_map.py` inline the same helpers. You extract them once, into `notebooks/lib/common.py`, so Agent 3 can import them cleanly. **Do not modify the two existing notebooks** — they still inline their own copies, and they stand as independent demoable artifacts. You are creating a separate, fresh library, not refactoring.

`notebooks/lib/common.py` must export:
- `fmt_mxn(v, short=True)` — peso formatter ($X mmdp, $X mdp, $X k, $X). Copy from `budget_dashboard.py`.
- `fmt_int(v)` — integer formatter with thousands separators.
- `PALETTE` — the CDMX-guinda-led palette from `budget_dashboard.py` / `obra_map.py`.
- `FONT = "Inter, -apple-system, system-ui, sans-serif"`
- `CDMX_GUINDA = "#9F2241"`, `CDMX_GUINDA_DARK = "#691C32"`
- `style_fig(fig, height=480, title=None)` — Plotly layout styler copied from `budget_dashboard.py`.
- `kpi_card(label, value, accent="#9F2241", sub=None)` — returns an HTML string for the KPI card pattern used in both existing dashboards.
- `hero_banner(kicker, title, subtitle)` — returns the HTML for the guinda gradient hero. Extract from the two existing notebooks.

Write `notebooks/lib/__init__.py` (can be empty).

### Hour 0.5–1: Write `data/clean/SCHEMAS.md` v1 + loaders with fixture fallback

`data/clean/SCHEMAS.md` is the written contract between Agent 1 and Agent 3. Document the exact shape of every file Agent 1 will emit. Be excessively specific — columns, types, example values, provenance.

Expected files (coordinate final column names with Agent 1):

```markdown
## budget_tree.parquet

Columns:
- source_id: str — crosswalk row id (stable across reruns)
- level: int — 1 or 2
- citizen_category: str — one of the ~12 canonical Level-1 buckets
- display_name: str — what the UI shows
- parent_id: str | null — null for Level 1; the Level-1 source_id for Level 2
- icon: str | null — emoji for Level 1; null for Level 2
- monto_aprobado: float64 — pesos, approved
- monto_ejercido: float64 | null — pesos, exercised (null until a trimestre dataset is chosen)
- per_100_of_total: float64 — percent of the citywide total this row represents
- per_100_of_parent: float64 | null — percent of the parent category (null for Level 1)
- rationale: str — short sentence from crosswalk.csv
- year: int — fiscal year this row describes

Provenance: crosswalk/crosswalk.csv joined to egresos_*.csv. One row per crosswalk row.
```

Draft similar sections for:
- `budget_by_alcaldia.parquet` (if alcaldía data is viable — mark as conditional)
- `income_sources.parquet`
- `source_links.csv`

Write `notebooks/lib/loaders.py` exposing:
- `load_budget_tree(year: int | None = None) -> pl.DataFrame`
- `load_budget_by_alcaldia() -> pl.DataFrame | None` (returns None gracefully if the file doesn't exist)
- `load_income_sources() -> pl.DataFrame`
- `load_source_links() -> dict[str, str]`
- `available_years() -> list[int]`

Every loader must **gracefully fall back to a small hardcoded fixture** if the real file isn't present yet, so Agent 3 can build from minute one. The fixtures live inline in `loaders.py` — not a separate folder. Log a warning to stderr when falling back so no one demos on fixtures by accident.

### Hour 1–2: Loaders stabilize; monitor Agent 1's emissions

As Agent 1 drops files into `data/clean/`, verify they match `SCHEMAS.md`. If they don't, first ping Agent 1 via `HANDOFFS.md` — don't silently reshape in the loader. The loader stays simple; the contract stays the contract.

### Hour 2–3: Integration watch + deploy decision

Every 20 minutes, cold-run both the new `tus_100_pesos.py` and the three existing notebooks, from a clean venv, to catch broken imports or missing files. Log regressions in `HANDOFFS.md`.

Pick the deploy target (one of):
- **Marimo Cloud** (https://marimo.io/cloud) — native Marimo hosting, fastest path.
- **Fly.io / Railway** — run `uv run marimo run notebooks/tus_100_pesos.py --host 0.0.0.0 --port $PORT` behind a Dockerfile.
- **Tailscale-exposed laptop** — cheap fallback if nothing else works; document the URL.

Document the chosen target and the exact deploy command in `README.md` under a new "Deploy" section.

### Hour 3–4: Deploy

Ship the first live URL by hour 4. Verify:
- `notebooks/tus_100_pesos.py` renders with real data.
- "Ver en datos oficiales" links on 10 random rows all resolve — if any 404, fix with Agent 1.
- All three existing notebooks are also accessible from the deploy (or at least don't break the build).

### Hour 4–5: Integration testing + DEMO_RUNBOOK

- Walk the full pitch path end-to-end on the deployed URL. Note any jank. Fix what you can without editing `notebooks/tus_100_pesos.py`; file the rest in `HANDOFFS.md` for Agent 3.
- Validate totals: Level-2 rows in a category sum to the Level-1 total, within rounding. If they don't, the crosswalk has a hole — ping Agent 1.
- Write `DEMO_RUNBOOK.md`:
  - Production URL
  - Fallback URL (if any)
  - How to kill and restart the demo
  - Known-issues-and-talking-points (what to say if a particular panel is blank)
  - Kill-switch for Agent 3's `?demo=1` pre-loaded state

### Hour 5–6: Production-ize

Lock the deploy. Monitor. Don't touch anything after hour 5:30 unless it's on fire.

## Rules of engagement

- **Schemas are law.** Once `SCHEMAS.md` v1 is committed, changes are append-only until hour 3. If a shape must change, write a migration note in `HANDOFFS.md`, ping Agents 1 and 3, fix in order.
- **No clever infrastructure.** No database. No caching layer. No queue. No auth. Static parquet + Marimo + a single deploy. If you catch yourself reaching for Postgres, stop.
- **Don't refactor the existing dashboards.** They ship as independent demos. Your library is additive.
- **Your latency budget is zero.** Agents and the lead come to you with unblocking questions. Answer within 2 minutes. If something takes longer, write the answer into `SCHEMAS.md` or `HANDOFFS.md` so it's durable.
- **Observe, don't hover.** You watch `notebooks/tus_100_pesos.py` for drift but do not edit it. Leave notes.
- **Don't add deps lightly.** Every `pyproject.toml` change must be justifiable in one sentence. `uv sync` is the lead's first move on a new machine — don't inflate that install.

## What "done" looks like

By hour 5:
- Live deployment URL
- `notebooks/lib/common.py` + `loaders.py` working and imported by `tus_100_pesos.py`
- `data/clean/SCHEMAS.md` accurate and current
- Loaders gracefully fall back to fixtures when real files are missing
- Every "Ver en datos oficiales" link resolves
- `DEMO_RUNBOOK.md` written
- Zero open BLOCKERs in `HANDOFFS.md`

## Don't do

- Don't write the drill-down UI. That's Agent 3. If you see something visually off, file a HANDOFFS note.
- Don't recompute what Agent 1 should have aggregated. If data arrives in a shape requiring heavy transforms in the loader, push back — the loader should be thin.
- Don't add features that aren't in the PRD. No user accounts, no program-wide search unless scoped, no "while we're at it" additions.
- Don't reintroduce Phase 2 or Phase 3 out-of-scope items.
- Don't let the pitch arrive with "just one more integration fix." Freeze at hour 5:30.
- Don't edit the three existing notebooks — they are frozen exhibits.
