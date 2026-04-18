# PRD — Claude Impact Lab CDMX: "Tus 100 pesos"

**Event:** Claude Impact Lab CDMX hackathon, Saturday
**Track:** Sigue el Dinero
**Team:** 5 technical humans + 4 parallel Claude Code agents (1 orchestrator + 3 workers)
**Build time:** ~6 hours + final pitch

---

## 0. How this doc set works

All project docs live under `prd/` in the repo:

```
prd/
├── AGENT_0_ORCHESTRATOR.md   # runs first, calibrates everything below
├── PRD.md                    # this file — thesis, scope, success criteria
├── AGENT_1_DATA.md           # data & research worker
├── AGENT_2_ARCHITECT.md      # stack & integration worker
├── AGENT_3_BUILDER.md        # user-facing app worker
├── AUDIT.md                  # written by Agent 0 at run time
├── QUESTIONS_FOR_HUMAN.md    # written by Agent 0 at run time
├── CHANGELOG.md              # written by Agent 0 at run time
└── GO_NO_GO.md               # written by Agent 0 at run time
```

**Execution order:**
1. **Agent 0 (Orchestrator) runs first.** It audits the repo, verifies external data sources, and rewrites the three worker briefs to match current reality. It is allowed to edit every file in `prd/` except the thesis and success criteria of this PRD.
2. **Human team lead reviews `GO_NO_GO.md`** and approves.
3. **Agents 1, 2, 3 launch in parallel**, each reading its own brief (now calibrated) plus this PRD plus `CONTRACTS.md`.

If you are an agent reading this, you are probably not Agent 0. Confirm which brief you're supposed to execute before touching anything.

---

## 1. Problem

CDMX publishes its budget on [tudinero.cdmx.gob.mx](https://tudinero.cdmx.gob.mx). Citizens don't read it. The data is there — but it's organized the way bureaucrats think (clasificación funcional, económica, administrativa), not the way a person experiences the city (el agua que sale de la llave, el camión que pasa, la luminaria que prende, el parque donde juegan los niños).

The existing portals stop at bureaucratic categories. Nobody has taken the budget all the way down to the level where a citizen can point at a specific thing — a named project, a known obra, a visible service — and say "yes, that's where my money is going."

## 2. What we're building

**A single-screen web app that reorganizes the CDMX budget around citizen experience, and lets any citizen drill down from the city total to specific named projects.**

One phase. Done deeply. Three levels of hierarchy:

1. **Level 1 — Citizen category** (~12 tangible categories): Agua, Transporte público, Calles y banquetas, Basura y limpia, Parques y espacios públicos, Seguridad, Justicia, Salud, Educación, Apoyos sociales, Cultura y deporte, Medio ambiente, Alumbrado, Gobierno y administración, Deuda.
2. **Level 2 — Program or named project:** "Cablebús Línea 3," "Pilares," "Sembrando Parques," "Mi Beca para Empezar," "Utopías," "SACMEX – Sectorización Iztapalapa." Every item at this level has a name a human could recognize or, if not, a specific program description.
3. **Level 3 — Specific obras or line items**, but only where they're recognizable, locatable, or otherwise citizen-legible. Examples: a specific school rehabilitation, a specific stretch of road, a specific pump station. Generic partidas específicas (material de oficina, servicios de energía eléctrica) are aggregated, not surfaced.

### The thesis

CDMX already publishes its budget. What nobody has done is make it legible. Our differentiator is not novelty of data — it's the editorial reframe and the depth of drill-down. We take a bureaucratic document and make it something a citizen can *read*, click, and recognize.

### The guiding rule for granularity

**Granular when citizens can recognize it. Aggregated when they can't.**

A line item gets its own row in the UI if and only if one of these is true:
- It has a named project or program citizens could plausibly have heard of
- It's geographically locatable (a specific obra at a specific address, a specific school, a specific health clinic)
- It's large enough to matter (above a configurable peso threshold) *and* has a descriptive label beyond the accounting code

Everything else rolls up to its parent. Don't expose "3411" to a user.

## 3. Non-goals (things we will not build)

- Complaint data (Locatel, 911, FGJ) — explicitly out of scope for this version
- Complaint-vs-budget comparison — explicitly out of scope
- Embeddings, clustering, any ML — not needed; this is a classification and visualization problem
- Multi-year time series — pick one year (see open questions)
- Login / user accounts
- Mobile-native — web-responsive only
- Tax incidence modeling ("your personal tax bill") — ruled out; we show spending, with an optional methodology note on "where does CDMX's money come from"
- Anything requiring scraping behind auth
- A chatbot, "ask the budget" interface, or any LLM-on-top feature

## 4. Success criteria

**Minimum (must ship):** One working screen. All ~12 citizen categories populated with Level 2 entries (named programs). Every peso amount traceable back to a specific line in the source budget CSV. 90-second pitch rehearsed.

**Target:** Full three-level hierarchy where the data supports it. At least half the Level 2 programs drill into Level 3 with named obras or specific items. A visible "Ver en datos oficiales" link per row, pointing back to the underlying record on tudinero or datos.cdmx.gob.mx. Methodology footnote explaining the crosswalk choices.

**Stretch:** Alcaldía filter (the whole tree refilters based on a selected alcaldía). A map view of geolocatable Level 3 items. A "compare alcaldías" side-by-side.

**Failure modes to avoid:**
- A prettier tudinero with no depth gain — if Level 2 doesn't contain recognizable names, we've built nothing new.
- Exposing raw accounting codes in the UI — if a user sees "3411" we've failed at editorial work.
- Numbers that don't add up — if the Level 1 totals don't sum to the published headline, a judge catches it in 30 seconds.

## 5. The editorial crosswalk (this is the project's spine)

We are not just visualizing the CDMX budget. We are **reorganizing** it around how citizens experience the city, and drilling as deep as the data legibly supports. That reorganization is opinionated work product and must be documented.

Deliverable: `crosswalk.csv` with columns `[source_id, source_label, source_parent, level, citizen_category, display_name, rationale]`.

- `source_id` = native ID in the budget CSV (programa presupuestario code or similar)
- `source_label` = raw name from the data
- `source_parent` = null for Level 1, category for Level 2, program for Level 3
- `level` ∈ {1, 2, 3}
- `citizen_category` = one of the ~12 Level 1 buckets
- `display_name` = what the user actually sees — often a cleaned-up version of `source_label`
- `rationale` = one short sentence. Required. No exceptions.

One human owns this file end-to-end. Every judge question about "why is X in Y" is answered from this file.

## 6. Demo narrative (the 90-second pitch)

1. **Hook (15s):** "CDMX ya publica su presupuesto. Nadie lo lee. No porque no importe — porque está escrito para contadores, no para ciudadanos."
2. **The reframe (20s):** Open the app. Grid of ~12 tangible categories. "De cada 100 pesos que gasta tu Ciudad en [año], así se reparten. No por 'clasificación funcional' — por lo que tú ves cuando sales de tu casa."
3. **The depth reveal (30s):** Click into "Transporte público." Show named programs: Cablebús L3, Metro mantenimiento, RTP renovación de flota. Click into one. Show specific obras with pesos and locations. "Esto es lo que nadie te muestra: el dinero no se gasta en categorías, se gasta en cosas. Aquí están las cosas."
4. **The accountability moment (15s):** Point to the "Ver en datos oficiales" link on any row. "Cada número aquí es trazable. No inventamos nada. Solo lo reorganizamos."
5. **Close (10s):** "Esta es la primera versión. Con más tiempo, cruzaremos esto con lo que la gente reporta a Locatel. Pero el primer paso era hacer que el presupuesto se pudiera leer."

If the pitch can't be delivered in 90 seconds by hour 5, the scope is still wrong.

Note the last line: it signals Phase 2/3 as a roadmap without committing to building them. This protects against the judge question "why no complaint data?"

## 7. Agent roles (Claude Code sessions)

Four agents total. Agent 0 runs first and alone. Agents 1, 2, 3 run in parallel afterward.

**Stack (locked 2026-04-18):** Python 3.11 + Marimo + Polars + Plotly + uv. The repo already has this toolchain and two working dashboards (`notebooks/budget_dashboard.py`, `notebooks/obra_map.py`) in the same problem space. No Next.js, no React, no separate API layer. See `prd/AUDIT.md`.

- **Agent 0 — Orchestrator** (`prd/`): audits repo, rewrites the three worker briefs to match reality, produces `GO_NO_GO.md`. Brief: `AGENT_0_ORCHESTRATOR.md`.
- **Agent 1 — Data & Research** (`data/`, `crosswalk/`, `scripts/download_data.sh`, `DATA_NOTES.md`): finds, downloads, cleans, documents all budget datasets; produces the `crosswalk.csv` and the Polars-ready files the UI consumes. Brief: `AGENT_1_DATA.md`.
- **Agent 2 — Integrator & Deploy** (`notebooks/lib/`, `data/clean/SCHEMAS.md`, `pyproject.toml`, `README.md`, deploy config): extracts shared helpers from the existing dashboards, documents the Polars shapes Agent 1 emits, owns dependency and deploy config, runs integration testing across all notebooks. Brief: `AGENT_2_ARCHITECT.md`.
- **Agent 3 — Builder** (`notebooks/tus_100_pesos.py`): builds the user-facing Marimo app — the hierarchical drill-down experience and pitch-ready polish. Reuses the guinda visual vocabulary from the existing dashboards. Brief: `AGENT_3_BUILDER.md`.

Each worker agent reads this PRD first, then its own brief (already calibrated by Agent 0), then `data/clean/SCHEMAS.md` (written by Agent 2 in the first 30 minutes).

## 8. Ownership & collision rules

Single human lead (not a 5-person crew — the PRD's "5 humans" language is superseded). The lead signs off on `GO_NO_GO.md`, resolves any `HANDOFFS.md` escalations, and presents the pitch.

| Path | Owner | Others can |
| --- | --- | --- |
| `prd/` (all files) | Agent 0 | read only after sign-off; human lead can edit anytime |
| `PRD.md` section 1 (problem) & 2 (scope) & 4 (success criteria) | human lead | Agent 0 cannot edit without sign-off |
| `data/raw/`, `data/clean/`, `crosswalk/`, `DATA_NOTES.md`, `scripts/download_data.sh` | Agent 1 | read only |
| `notebooks/lib/`, `pyproject.toml`, `uv.lock`, `README.md`, deploy config | Agent 2 | read only; propose changes via `HANDOFFS.md` |
| `data/clean/SCHEMAS.md` | Agent 2 | Agent 1 reviews schemas; Agent 3 reads |
| `notebooks/tus_100_pesos.py` | Agent 3 | read only |
| `notebooks/budget_dashboard.py`, `notebooks/obra_map.py`, `notebooks/explore.py` | existing (frozen) | all read-only — do not edit, they stand as independent demos |
| `HANDOFFS.md` at repo root | shared, append-only | all agents can append |

If an agent needs something outside its directory, it appends to `HANDOFFS.md` and does not modify. The human lead resolves.

## 9. Timeline (6 hours)

| Hour | Agent 1 | Agent 2 | Agent 3 |
| --- | --- | --- | --- |
| 0–1 | Run `scripts/download_data.sh`. Inspect live CSVs. Write `DATA_NOTES.md` with hour-0 depth assessment: citizen-recognizable program names in `desc_programa_presupuestario`, and whether any alcaldía field exists. | Extract shared helpers from existing notebooks into `notebooks/lib/common.py` (`fmt_mxn`, `style_fig`, `PALETTE`, `FONT`, CDMX guinda). Stub `notebooks/lib/loaders.py` with fixture fallbacks. Draft `data/clean/SCHEMAS.md` v1. | Read `budget_dashboard.py` + `obra_map.py` for visual vocabulary. Scaffold `notebooks/tus_100_pesos.py` with hero + empty Level-1 grid against a fixture dict from `loaders.py`. |
| 1–2 | Draft Level-1 citizen-category taxonomy. Map every budget row to exactly one citizen_category in `crosswalk/crosswalk.csv`. Emit `data/clean/budget_tree.parquet` v1 (Level 1 only). | Finalize loaders so Agent 3 reads real data with one line. Validate SCHEMAS.md matches reality. | Level-1 category grid rendered from loaders. Guinda hero, total pesos headline, "De cada 100 pesos…" copy. Responsive grid. |
| 2–3 | Populate Level-2 (`desc_programa_presupuestario`) in crosswalk. Rebuild `budget_tree.parquet` with 2-level hierarchy and cumulative percentages. | Pull Agent 1's real data into Marimo via `loaders.py`. Validate Level-1 totals sum to published headline within rounding. Update `README.md` to include the new notebook. | Level-2 drill-down: click a category card → reveal named programs as a ranked list. "Ver en datos oficiales" link per row. No pie/donut charts. |
| 3–4 | Evaluate alcaldía-level availability (Recursos Transferidos + heuristics). If viable, produce `data/clean/budget_by_alcaldia.parquet`. Build `data/clean/source_links.csv` mapping crosswalk rows to canonical URLs. | Help wire alcaldía filter. Pick and configure deploy target (Marimo Cloud / Fly.io / Railway / Tailscale demo). Smoke-test all four notebooks end-to-end. | Alcaldía filter on Level-1/2 if data supports. Add a linked sibling section pointing at `obra_map.py` ("¿Qué se construyó en tu calle?") so the demo has a tangible geographic moment. Implement row-level "Ver en datos oficiales." |
| 4–5 | Final `crosswalk.csv`. Write `crosswalk/METHODOLOGY.md` in Spanish. Validate totals across all levels. | Full integration pass. Deploy. Verify all notebooks render on the deployed target. Write `DEMO_RUNBOOK.md`. | Pitch polish: empty/loading/error states, hover microinteractions, `?demo=1` (via `mo.query_params()`) pre-loading Transporte → Cablebús or similar. Rehearse the 90s pitch with the lead. |
| 5–6 | Standby for Agent 3's data questions. | Monitor deployed URL for regressions. Document kill-switch + fallback URL in README. | Final pitch rehearsal. Freeze at hour 5:30. |

**Hard checkpoint at hour 1 (not hour 3):** if Agent 1's depth assessment says Level 3 is not achievable from live data (predicted in `AUDIT.md`), shift strict three-level drill-down into Level 1+2 + alcaldía filter + Rally sibling view. Don't ship a broken Level 3.

## 10. Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| datos.cdmx.gob.mx is down Saturday | Agent 1 downloads everything by hour 1 and commits to repo |
| Budget CSV doesn't contain named project info at Level 3 | Agent 1 checks this in hour 0 as the *first* thing. If Level 3 is not achievable from open data, demo leans harder on Level 1+2 depth and polish. |
| Crosswalk editorial work balloons past 2 hours | One human owns the file; hard cap at 4 hours total on crosswalk work; anything unmapped goes to "Otros" and is disclosed. |
| 3 agents race on same file | Ownership table above + working directories |
| "All technical" team means ugly UI | Agent 3 explicitly owns polish; one human pair-programs with Agent 3 on visual design |
| Demo looks like tudinero but worse | Level 2 and 3 named-project depth is the differentiator. If we can't show that depth, we don't have a demo. |
| Judge asks "why didn't you include Locatel?" | Pitch close explicitly names it as the next step. Honest answer: "We chose depth in transparency over breadth across phases." |

## 11. Open questions — RESOLVED 2026-04-18

1. **Year:** Agent 1 downloads everything available; final year chosen by lead after Agent 1's hour-0 depth assessment. Existing `budget_dashboard.py` already supports a year picker.
2. **Ingresos sidebar:** include as a small footer section (default).
3. **Deploy target:** Marimo-compatible — specific target (Marimo Cloud / Fly.io / Railway) chosen by Agent 2 at hour 3.
4. **Stack:** Python + Marimo + Polars + Plotly + uv — locked.
5. **Pitch presenter:** the human lead.
6. **Time budget:** "just go" — 6h planning stands, no hard cutoff.
7. **Workstreams:** single human lead + 3 worker agents. See §8.
8. **Level 3 fallback:** alcaldía filter (data-dependent) + linked `obra_map.py` sibling view. Strict three-level-per-program obra drill-down is not attempted given the budget CSV does not carry obra-level labels.
