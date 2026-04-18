# Agent 3 — Builder

**Read first:** `prd/PRD.md`, then this file, then `data/clean/SCHEMAS.md` (Agent 2 writes it in the first 30 minutes — wait for it, don't build against guesses), then skim `notebooks/budget_dashboard.py` and `notebooks/obra_map.py` for the visual vocabulary you inherit.

**Before you start:** confirm Agent 0 has signed off `prd/GO_NO_GO.md`.

**Your working directory:** `notebooks/tus_100_pesos.py` — the single Marimo file that IS the demo.
**Files you own:** `notebooks/tus_100_pesos.py`.
**Files you read but do not edit:**
- `prd/` (all files)
- `data/clean/SCHEMAS.md` and `data/clean/` (read via `notebooks/lib/loaders.py`)
- `notebooks/lib/common.py`, `notebooks/lib/loaders.py` (Agent 2's)
- `notebooks/budget_dashboard.py`, `notebooks/obra_map.py`, `notebooks/explore.py` (existing — reference for style, not for edit)
- `crosswalk/` (reference)

---

## Your job in one sentence

Build the single Marimo notebook that makes a skeptical judge say "oh, that's different from tudinero" within 15 seconds of loading, and keeps them engaged as they drill down from the whole city to a specific named program — then hands them off to `obra_map.py` for a tangible geographic moment.

You are the only agent a judge will actually see. The data is invisible. The library is invisible. The notebook is the product.

## The hardest thing about your job

Marimo is Python, not React. Every UI pattern you know from Next.js / shadcn / Tailwind has a different shape here. Your tools:
- `mo.md("...")` for HTML/Markdown cells (the guinda hero, KPI strips, custom cards — all HTML-in-a-string)
- `mo.ui.button`, `mo.ui.dropdown`, `mo.ui.multiselect`, `mo.ui.text` for inputs
- `mo.ui.array` / `mo.ui.dictionary` for a grid of clickable cards (each a button with custom HTML)
- `mo.state` for sharing drill-down state across cells
- `mo.query_params()` for URL-driven state (powers `?demo=1`)
- `mo.hstack`, `mo.vstack` for layout
- Plotly via `plotly.graph_objects` / `plotly.express` for charts
- Reactive cells: when an input changes, downstream cells re-run. This is how you implement the drill-down — clicking a category sets a state var, which a downstream cell reads and re-renders as Level 2.

The two existing notebooks are your reference implementations for all of the above. Read them first. The KPI strip pattern in `obra_map.py`, the hero gradient in `budget_dashboard.py`, the detail-card pattern in `obra_map.py` — all directly reusable.

The second-hardest thing: tudinero exists. If the Level-1 grid doesn't immediately feel sharper, more tangible, more readable than tudinero, the pitch is dead before the drill-down starts.

## Deliverables (in order)

### Hour 0–1: Setup and visual vocabulary

- Wait for `data/clean/SCHEMAS.md` v1 and `notebooks/lib/{common,loaders}.py` to exist (should land by 0:30).
- Scaffold `notebooks/tus_100_pesos.py` with the standard Marimo app preamble (`import marimo; app = marimo.App(width="full", app_title="Tus 100 pesos · Presupuesto CDMX")`).
- First cell: import `mo`, `polars as pl`, Plotly, and `from notebooks.lib.common import *`, `from notebooks.lib.loaders import *`. (The Marimo run-dir makes `notebooks/lib` importable when running from the repo root.)
- Second cell: the guinda hero — reuse `hero_banner(...)` from `lib/common`. Copy: kicker "Ciudad de México · Presupuesto ciudadano" / title "Tus 100 pesos" / subtitle "De cada 100 pesos que gasta tu Ciudad, así se reparten. Haz clic en cualquier categoría."
- Third cell: total-pesos KPI card (single number, tabular nums, `fmt_mxn`).
- Fourth cell: empty Level-1 grid placeholder rendered from a fixture (loader will inject it).

Write `notebooks/DESIGN_NOTES.md` in 10 minutes — typography, color, spacing, motion decisions. **Two hours from now you will be tempted to change them. Don't.**

### Hour 1–3: Level 1 — The category grid

This is the first thing a judge sees. It must feel tangibly different from tudinero's donut chart.

**Layout:**
- Hero (done).
- Total pesos, large and proud, tabular numerals.
- A grid of ~12–14 category cards. Each card: emoji icon, category name, large peso number, "X de cada 100 pesos" secondary text, thin proportion bar.
- Card implementation: each card is an `mo.ui.button` styled via an HTML label; clicking a card writes the category id to a shared `mo.state`. A downstream cell reads that state and re-renders the Level-2 view below.

**Design guardrails:**
- No pie charts. No donut charts anywhere in this notebook. (The existing `budget_dashboard.py` has a donut for capítulos; you do not copy that pattern here.)
- Typography hierarchy: one big number per card, one label, one secondary stat. No more.
- Color: guinda accent + neutrals. No rainbow-colored category palette.
- Responsive: test at the default Marimo viewport and at a half-width browser.
- Empty states: if a category has zero programs, the card still works — show "Datos en consolidación."

Ship Level 1 by hour 3. It must be demoable alone if Level 2 ends up thin.

### Hour 3–4: Level 2 — Named programs

When a category card is clicked, a Level-2 panel appears below the grid (don't navigate away — this is one page, reveal-in-place is the pattern).

**Each program row:**
- `display_name`
- Pesos, tabular, right-aligned
- Percent of this category
- Thin proportion bar
- Rationale tooltip on hover (`title` attribute on the HTML is fine for MVP)
- "Ver en datos oficiales" secondary link — opens `source_links` URL in a new tab

**Ordering:** by `monto_aprobado` descending. Always. No sort options — we're surfacing importance, not building a spreadsheet.

**Aggregation disclosure:** at the bottom, a subtle note: "Y [N] partidas más consolidadas en 'Otros'. Total: [$X]." — read from the crosswalk's "Otros" bucket. This is honesty as a feature and heads off the "what about the rest?" judge question.

**Back affordance:** a small "← Volver" to clear the state and return to the grid only.

### Hour 4–5: Alcaldía filter + sibling map link + polish

**Alcaldía filter (conditional):** if `load_budget_by_alcaldia()` returns non-None, add a top-of-page `mo.ui.dropdown` that re-queries the Level-1 grid filtered to the selected alcaldía. If it returns None, hide the selector — don't stub it.

**Sibling link to `obra_map.py`:** at the bottom of any Level-2 view, a small call-to-action card:
> "¿Y qué se construyó? Cada proyecto federal entre 2013 y 2018 en un mapa. → `obra_map.py`"

The existing `obra_map.py` already has a guinda-branded landing; deep-linking to it from here gives the demo a tangible geographic moment without needing to build a new map. Use an `<a href>` to the deployed URL / route for `obra_map.py` — Agent 2 confirms the path.

**`?demo=1` pre-loaded state:** via `mo.query_params()`, detect `demo=1` and pre-click a known-good category (Transporte público → show Cablebús L3 prominently). The presenter can open the demo URL + `?demo=1` and skip the fumble.

**Polish:**
- Empty/loading states on every view.
- "Ver en datos oficiales" tested on 10 random rows — flag any 404 to Agent 2.
- Page title, Spanish throughout.

### Hour 5–6: Pitch rehearsal, kill bugs

- Walk the 90-second pitch with the human lead. Three times minimum.
- Remove any half-built feature that can't be defended. "We were going to…" is a losing answer.
- Freeze at hour 5:30.

## Rules of engagement

- **Fixtures first, real data second.** `lib/loaders.py` falls back to fixtures until Agent 1 ships real files. You never block on Agent 1.
- **One delightful detail per level.** Not a dozen. Pick one micro-interaction per screen. Examples:
  - Level 1: numbers animate up from zero on first render (Plotly traces or CSS transition — Marimo allows inline CSS in `mo.md` cells).
  - Level 2: the rows slide in with a 150ms stagger when a category is selected.
- **Spanish, everywhere.** Every label, every tooltip, every error state. The pitch is Spanish.
- **Don't debate schemas with Agent 2.** If a column doesn't work for your UI, write a HANDOFFS note with the specific need and a proposed alternative. Agent 2 decides in <5 min. Then move.
- **The "Ver en datos oficiales" link is not optional.** Style it subtly — it shouldn't distract — but it must be there, every Level-2 row.
- **Accessibility, scoped.** Semantic HTML in your `mo.md` cells. Keyboard focus on the cards. Color contrast passes WCAG AA. No full ARIA gymnastics.
- **Don't touch the three existing notebooks.** They're frozen exhibits. Copy patterns, don't modify source.

## Visual design cheat sheet

Inherited from `budget_dashboard.py` + `obra_map.py`. Use `lib/common.py` constants:

- **Typeface:** Inter — `FONT` from `common.py`. Browser default monospace for numbers (tabular nums via `font-variant-numeric: tabular-nums;` in inline CSS).
- **Numbers:** tabular, right-aligned, thousands separators. `fmt_mxn(v)` everywhere.
- **Colors:** `CDMX_GUINDA = #9F2241` for accent, neutrals `#0F172A/#64748B/#E2E8F0/#F1F5F9` for text and surfaces. `PALETTE` available if you need a second accent.
- **Spacing:** 8px grid. Cards: 20–24px internal padding. Section gap: 48–64px.
- **Corners:** 10–12px on cards, 8px on buttons.
- **No gradients** (except the inherited hero), **no heavy shadows**, **no neon**.

## What "done" looks like

By hour 5:
- `notebooks/tus_100_pesos.py` running against real data via `lib/loaders.py`
- Guinda hero + total KPI + 12–14 category cards + click-through to Level-2 program list
- Alcaldía filter (if Agent 1 shipped `budget_by_alcaldia.parquet`)
- `obra_map.py` sibling link
- "Ver en datos oficiales" on every Level-2 row, all resolving
- `?demo=1` pre-loaded path works
- Pitch rehearsed, under 90 seconds
- Zero error cells, zero broken states

## Don't do

- Don't build a complaint map. Out of scope.
- Don't build a comparison view between budget and anything else. Out of scope.
- Don't add search — the drill-down is the navigation.
- Don't add a chatbot, auth, or "share on Twitter."
- Don't use pie or donut charts anywhere in this notebook.
- Don't skip pitch rehearsal. A gorgeous UI with a fumbled pitch still loses.
- Don't over-animate. Every animation ≤250ms and functional, not decorative.
- Don't edit `lib/common.py` or `lib/loaders.py` — file a HANDOFFS note if you need a change.
