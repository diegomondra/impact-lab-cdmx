# HANDOFFS

Append-only cross-agent escalation log. Newest entries at the top.
Prefix blockers with `BLOCKER:` and unblock requests with `UNBLOCK:`.

---

## 2026-04-18 — Agent 3 → lead — RESOLVED: card grid + consolidation

Swapped the `mo.ui.button` + `mo.hstack(wrap=True)` grid for one `mo.md`
CSS-grid block (`repeat(auto-fill, minmax(232px, 1fr))`) with `<a
class="tcp-card" href="?cat=...">` cards, driven by `mo.query_params().get("cat")`
— `notebooks/tus_100_pesos.py` query-param cell at L69–73, `.tcp-card`
grid at L235–345, Volver link at `?cat=` L466. Hero KPI now year-filters
to max(`available_years()`) so city total locks to 2024's $267.96 mmdp
(L82–96, L117–139); alcaldía selection renders a guinda zoom panel below
the hero (L143–182) and the filtered cards show a secondary
`per_100_of_total` line labelled "X.XX% del gasto total de la ciudad"
(L252–260). Smoke green (3/3 HTTP 200); `/?cat=L1-transporte` deep-link
serves HTTP 200. Browser-eyeball verification (overlap / click-through
/ Volver round-trip) still pending the lead's pass at `:27100`.

Minor correction worth flagging: the illustrative "$6.84 mmdp (2.6%)"
for AO in the original UNBLOCK entry sums 2022+2024; with year-filtered
2024 data the zoom panel now renders $3.63 mmdp (1.4%), consistent with
the 2024 city headline Agent 2 validated. No schema changes, no lib
changes, no data/clean changes.

---

## 2026-04-18 — Agent 2 → Agent 3 — UNBLOCK: Level-1 card grid renders mangled + consolidation concept

Two things, one from the lead's eyeball pass on the live notebook at
`http://127.0.0.1:2718`.

### 1. Card grid layout is broken under marimo 0.23.1

**Symptom (screenshots in `img/`).** Each category card's top strip
(icon + percentage) renders as one horizontal ribbon across the row,
and the rest of the card (display_name, amount, progress bar) flows
below in a tangled column. Cards do not maintain their 232 px width;
content overlaps across adjacent cards. Unusable as a pitch surface.

**Root cause (hypothesis).** `mo.ui.button(label=<rich HTML with
width:232px flex-column>)` wrapped in `mo.hstack(wrap=True, gap=0.75)`.
Marimo's `<button>` wrapper isn't enforcing the 232 px intrinsic width
of the label div; the flex layout inside the label reflows into the
hstack row instead of staying inside its button container. This
worked in 0.10.0 but marimo 0.23 tightened button layout.

**Three fix paths, cheapest first:**

1. **CSS-grid via `mo.md` + `mo.query_params` for state.** Drop
   `mo.ui.button` entirely. Render the whole grid as one
   `mo.md(...)` block using `display: grid; grid-template-columns:
   repeat(auto-fill, minmax(232px, 1fr)); gap: 12px;`. Each card is
   an `<a href="?cat=L1-transporte">` — click updates the URL, a
   reactive cell reads `mo.query_params()["cat"]`. Loses the `mo.state`
   flow but gains guaranteed layout. ~40 lines diff.

2. **Keep `mo.ui.button`, force width via wrapper.** Change the
   label template so the outermost div has `display:block;
   width:232px; box-sizing:border-box;` and render the button grid
   inside a raw `<div style="display:grid; ...">` via `mo.Html` (not
   `mo.hstack`). `mo.hstack` is the culprit — its wrap layout
   interacts badly with button content. ~10 lines diff but success
   is marimo-version-dependent.

3. **Invisible-click trick.** Render the grid as pure HTML via
   `mo.md`, and below it render `mo.ui.array([mo.ui.button(f"Ver {c}",
   ...)])` that's visually hidden (`display:none`). Keyboard
   accessibility preserved via the real buttons; click is triggered
   from the HTML grid with `onclick` shims. Complex and fragile —
   do not pick unless (1) and (2) both fail.

**Agent 2 recommends (1)** — cheapest, most robust, URL-state as a
bonus (deep-link to a category).

### 2. Consolidate "Tus 100 pesos" with the full-city budget

**Problem.** Today the hero headline swaps between
`$267,965,350,437` (full city) and `$6,842,652,091` (Álvaro Obregón
atribuible) when the alcaldía filter changes. The "100 pesos" frame
breaks: the 100-peso anchor silently shifts from "every peso CDMX
spends" to "every peso CDMX spends in AO." Viewer loses scale.

**Proposed fix (editorial, not code-heavy).**

Hero always shows the full-city total. Alcaldía filter becomes a
*zoom*, not a *replace*:

```
PRESUPUESTO DE EGRESOS · 2024
$267,965,350,437
Así se reparten de cada 100 pesos.

┌─── Filtrado: Álvaro Obregón ─────────────────────────┐
│ De esos $267.97 mmdp, unos $6.84 mmdp (2.6%) se     │
│ atribuyen a programas que tocan Álvaro Obregón.     │
│ Abajo: cómo se reparten esos pesos dentro de la     │
│ alcaldía.                                             │
└───────────────────────────────────────────────────────┘
```

Card percentages in filtered mode: keep
`per_100_of_alcaldia_total` as the primary number (natural within a
slice) but add a secondary small number next to it —
`per_100_of_total` — labeled "(X% de la ciudad)". Preserves both
frames.

No schema change needed. `budget_tree.parquet` already has
`per_100_of_total` city-wide; `budget_by_alcaldia.parquet` already
has `per_100_of_alcaldia_total`. Both are already in the data you
load.

### Lead sign-off needed

Lead, please thumbs-up or redirect these two items before Agent 3
picks them up. Filing before hour 2 so Agent 3 has context when they
next sweep HANDOFFS.

---

## 2026-04-18 — Agent 2 → Agent 1 — RESOLVED: parquet contract validated, 0 drift

First parquet drop at ~16:10. All contract invariants pass against
`data/clean/SCHEMAS.md`:

| check | result |
| --- | --- |
| `budget_tree.parquet` column set | exact match, 0 drift |
| 2024 L1 rows | 16 (12 canonical + 4 extras — "Otros" + untyped) |
| 2024 L2 rows | 169 |
| `sum(L1 per_100_of_total)` | **100.0000** (exact) |
| All 169 L2 `parent_id` resolve to L1 `source_id` | **169 / 169** |
| L2 `per_100_of_parent` oversums | **0** |
| `sum(L1 monto_aprobado)` vs published 2024 headline | **267,965,350,437** vs `267,965,350,437` — Δ 0.00% |
| `budget_by_alcaldia` alcaldía coverage | all 16 ✓ |
| Álvaro Obregón L1 sum | matches live screenshot to the peso |
| `attribution_method` diversity | only `heuristic_unidad_responsable` — fine, documented in METHODOLOGY |
| `source_links.csv` coverage | **0** `source_id`s missing a link |

Minor observation (not a blocker): `income_sources.parquet` is
per-year, and each year's `per_100_of_total` sums to 97.86 / 98.06 /
100.00. My SCHEMAS.md said "Sums to ~100" without specifying
per-year — your per-year reading is the right one. Consider
appending a quick note to METHODOLOGY that 2022/2023 are ≈98%
because some ingreso buckets weren't classified; shouldn't block
anything.

You are clear to continue emitting. Next contract-review checkpoint
is when you add the Level-3 obras placeholders (if any) or touch
the alcaldía attribution method.

---

## 2026-04-18 — Agent 2 → lead — NOTE: `notebooks/explore.py` parked

`explore.py` fails to boot under marimo 0.23.1: `critical[multiple-definitions]`
for the variable `fig`, defined in both the chart-type `match` cell (line 129)
and the correlation-heatmap cell (line 145). Pre-existing bug; notebook was
generated at marimo 0.10.0 when the rule was less strict.

**Decision (lead, via Agent 2 at hour 1):** park, don't patch. `explore.py` is
a generic internal CSV tool — not part of the "Tus 100 pesos" pitch surface.
Fixing it would violate the freeze on existing notebooks for no pitch benefit.

**Consequence.** Removed from `scripts/smoke_notebooks.sh` smoke loop.
`tus_100_pesos.py`, `budget_dashboard.py`, `obra_map.py` all boot clean.
Two-line fix (`fig` → `_fig` in both cells) if we ever want it back.

---

## 2026-04-18 — Agent 2 → Agent 1 — RESOLVED: Option 2 accepted

Carved a `data/clean/` exception into `.gitignore`:

```
data/*
!data/.gitkeep
!data/README.md
!data/clean/
!data/clean/**
```

Verified with `git check-ignore -v`:

- `data/clean/*.parquet`, `data/clean/*.md`, `data/clean/*.csv` → tracked
- `data/egresos_*.csv` (Tier 1 raw) → still ignored
- `data/raw/**` → still ignored
- `data/raw/dictionaries/**` → still ignored

**Action for Agent 1:** `git add data/clean/*.parquet data/clean/*.csv` is
safe. Raw CSVs and dictionaries stay reproducible via
`scripts/download_data.sh`.

**Commit message convention:** prefix data-contract commits with
`data(clean): …` so it's greppable. The decision rationale belongs in
this entry, not repeated in each commit.

Closing this thread.

---

## 2026-04-18 — Agent 1 → Agent 2 — data/ gitignore exception

**Decision needed:** whether to commit the downloaded CSVs (or any subset)
alongside the repo, or keep `data/` fully gitignored and rely on
`scripts/download_data.sh` to repopulate at deploy time.

### Context

- `.gitignore` currently keeps `data/*` out of git (only `.gitkeep` and
  `data/README.md` are tracked).
- Agent 1's brief (`prd/AGENT_1_DATA.md`) says the lead's laptop dying
  mid-hackathon must not end the project, and requests coordination here.
- Post-hour-0 footprint on disk:

  ```
  data/                 ~84 MB  (4 CSVs — Tier 1, consumed by notebooks)
  data/raw/            ~120 MB  (13 CSVs/XLSX — Tier 2-6, Agent 1 discovered)
  data/raw/dictionaries/  ~185 KB  (3 XLSX schema dictionaries)
  data/clean/         (future)  (Polars parquets emitted by Agent 1)
  ```

  Breakdown in `DATA_NOTES.md` §1.

### Three options — please pick one

1. **Fully gitignored.** Deploy target must run
   `bash scripts/download_data.sh` on build. Fastest now, fragile if
   datos.cdmx.gob.mx is unreachable Saturday morning.
2. **Commit `data/clean/` parquets only** (exception: `!data/clean/`).
   Raw CSVs stay out of git; UI contract travels with the repo. Keeps
   commits small. Resilient to a CDMX portal outage.
3. **Commit `data/clean/` + `data/raw/`** (exceptions for both). Most
   resilient for a hackathon. ~200 MB of CSV/XLSX in git. Fine for a
   short-lived repo; not great long-term.

### Agent 1 recommendation

**Option 2.** Clean parquets are the real UI contract — small,
regenerable, and they protect against a Saturday-morning portal outage.
Raw CSVs stay reproducible via the download script but don't bloat git.

### Action requested

- Agent 2 edits `.gitignore` accordingly.
- Mention the choice in the commit message so Agent 1 knows what to
  commit under `data/clean/`.
- Until decided: Agent 1 does not `git add` anything under `data/`.

---
