# `tus_100_pesos.py` — design notes

Written 2026-04-18, hour 0:30. These decisions are locked for the hackathon. If
you are tempted to change them two hours from now: don't.

## Typography

- **Family:** Inter, via `FONT` from `lib/common.py` (system fallback chain).
- **Numbers:** `font-variant-numeric: tabular-nums` on every peso value and every
  percentage. Inline CSS — no global stylesheet needed.
- **Hierarchy (one-pass scan):**
  - Hero title 38px / 700 (inherited from `hero_banner`)
  - Page total 56px / 700, letter-spacing -1.5px, tabular
  - Card value 22px / 700, letter-spacing -0.3px, tabular
  - Card label 13px / 600, color #334155
  - Micro labels (kicker, "de cada 100 pesos") 11–12px / 500–600, color #64748B

One big number per card. One label. One secondary stat. No more. If something
else needs to be said, it goes in a tooltip, not on the card.

## Color

Single-accent system. The guinda earns attention because nothing else
competes with it.

- **Accent:** `CDMX_GUINDA` = `#9F2241`. Hero gradient, proportion bars,
  percentage badges on cards, hover states (future).
- **Neutrals:**
  - `#0F172A` primary text
  - `#334155` strong secondary
  - `#64748B` secondary
  - `#94A3B8` tertiary / disclaimers
  - `#E2E8F0` card borders
  - `#F1F5F9` proportion-bar track
- **Surfaces:** white cards on white page. Page background stays default.
- **No rainbow category palette.** `PALETTE` from `lib/common.py` exists for
  multi-series charts elsewhere; at Level 1 it would undermine the "all one
  city" framing. Do not use it here.

## Spacing

8px grid. Deviate only for type-driven optical corrections.

- Cards: 20px vertical / 22px horizontal padding, 10px internal gap.
- Card grid: 14px gap, `repeat(auto-fill, minmax(240px, 1fr))` — collapses
  gracefully from 5 columns down to 1.
- Section gaps: 32px between KPI strip and grid, 48–64px between major sections.
- Card minimum height: 170px so short-label cards don't collapse shorter than
  long-label cards and break the rhythm.

## Corners

- Cards: 12px
- KPI card (via `kpi_card` helper): 10px
- Buttons (future, Level 2 drill-down affordances): 8px
- Pills / badges: full pill (`border-radius: 20px`)

## Motion

- Every animation ≤ 250ms, ease-out.
- Static content does not animate on mount. Reveal-in-place for Level 2 panel
  will use a 150ms stagger (hour 3–4).
- No decorative motion. No bouncing, no shimmering, no card lifts on hover that
  aren't semantic. Hover = "this is clickable" (subtle border color shift,
  future); not "look at me."

## Layout rules

- Single-page. All drill-down is reveal-in-place below the grid.
- CSS grid for the card layout — not flexbox. `auto-fill minmax` is the whole
  point; do not pin column count.
- Page width: `width="full"` on the marimo app. Let the viewport breathe.
- Responsive test targets: default marimo viewport + half-width browser.

## Charts

- **Zero pie charts. Zero donut charts.** The ban is absolute in this notebook.
- Proportion bars (thin 4px tracks) do the "share of whole" job visually.
- If a horizontal bar chart is needed at Level 2, it uses `style_fig` from
  `lib/common.py` and a single guinda fill — no gradients.

## Language

Spanish. Everywhere. Every label, every tooltip, every error state, every
disclaimer. The pitch is in Spanish; the UI matches.

## Accessibility

- Semantic HTML inside `mo.md` cells where possible (`<a>`, `<button>` via
  `mo.ui.button`, not `<div onclick>`).
- Card content contrast verified against WCAG AA: guinda on white = 7.8:1,
  #64748B on white = 4.6:1, #334155 on white = 10.8:1. All pass.
- Keyboard focus: preserved by using `mo.ui.button` for clickable cards in
  hour 1–3. No custom focus suppression.

## Import pathing

Marimo adds the notebook's parent directory to `sys.path`, so
`from lib.common import *` and `from lib.loaders import *` resolve. The
scaffold inserts `_NB_DIR` defensively in the first cell so the notebook also
works when run from unusual CWDs. Do not rename `notebooks/lib/` without
coordinating with Agent 2.
