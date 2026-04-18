---
name: Questions for Human Team Lead
description: Unblocking questions Agent 0 surfaced, with answers received 2026-04-18.
type: project
---

# QUESTIONS_FOR_HUMAN — 2026-04-18 (resolved)

All BLOCKING questions answered. Agent 0 proceeded with Step 4 (rewrite briefs).

---

## Q0 — Stack paradigm ✅ A — Keep Marimo

**Answer:** **A. Keep Marimo.** Restructure agent roles to match.

**Implications baked into the rewrites:**
- Agent 2 repurposed from "API architect" to "Integrator & Deploy" (shared Python library + deploy config).
- No `/api/`, no `/web/`, no `CONTRACTS.md`. Instead: `notebooks/lib/` + `data/clean/SCHEMAS.md`.
- Agent 3 builds `notebooks/tus_100_pesos.py` as a single Marimo notebook, reusing guinda vocabulary from existing dashboards.
- The three existing notebooks (`budget_dashboard.py`, `obra_map.py`, `explore.py`) are frozen — no agent edits them.

---

## Q1 — Fiscal year ✅ decide post-hour-0

**Answer:** Not blocking. Agent 1 downloads everything, hour-0 assessment drives the call. Existing `budget_dashboard.py` already has a year dropdown; `tus_100_pesos.py` may expose the same or fix a single year after the depth check.

---

## Q2 — Alcaldía filter ✅ data-dependent

**Answer:** Try to have. Scope depends on what Agent 1 can extract from Recursos Transferidos + heuristics. If the data is unusable, the filter is cut and the UI hides the control (Agent 3's loader-returns-None pattern).

---

## Q3 — Deploy target ✅ Marimo-compatible

**Answer:** A — Marimo. Specific target (Marimo Cloud vs Fly.io vs Railway vs Tailscale-exposed laptop) picked by Agent 2 at hour 3.

---

## Q4 — Stack overrides ✅ skipped

Resolved by Q0.

---

## Q5 — Pitch presenter ✅ lead presents

**Answer:** Does not matter (team lead presents by default).

---

## Q6 — Time budget ✅ just go

**Answer:** Just go. 6h planning stands, no hard cutoff enforced.

---

## Q7 — Human workstreams ✅ single lead

**Answer:** Single human lead (the user). Don't try to organize a team — agents read briefs, lead dispatches and adjudicates `HANDOFFS.md`. The PRD's "5 humans" language is superseded.

---

## Q8 — Ingresos sidebar ✅ include

**Answer:** include (default). Agent 1 adds the ingresos CSV to `scripts/download_data.sh` and produces `data/clean/income_sources.parquet`.

---

## Q9 — Level 3 fallback ✅ Rally sibling view + alcaldía filter

**Answer (Agent 0 decided per implicit "just go" authorization):** Level 3 strict drill-down per program is NOT attempted — the main budget CSV does not carry obra-level labels (see `AUDIT.md`). The demo carries depth through:
1. An alcaldía filter on Levels 1 and 2 (if Agent 1 can produce `budget_by_alcaldia.parquet`).
2. A linked sibling view — `notebooks/obra_map.py` — already built, covering Rally 2013–2018 georeferenced federal projects, clearly labeled. `tus_100_pesos.py` surfaces a card that deep-links into it.

This respects the PRD's existing "hard checkpoint" language ("if Level 3 data is thin, shift into Level 1+2 polish + alcaldía filter") and reuses the existing `obra_map.py` artifact.

---

All clear. Agent 0 has rewritten briefs and the preliminary `GO_NO_GO.md` is now superseded by the final one.
