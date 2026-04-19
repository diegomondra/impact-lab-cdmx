# impact-lab-cdmx

Interactive dashboards for Ciudad de México public data — built at Claude Mexico City Lab 2026.

Five dashboards with official data from [datos.cdmx.gob.mx](https://datos.cdmx.gob.mx):

| Dashboard | Story | Source |
|---|---|---|
| `notebooks/ruta_del_peso.py` | **La ruta de tu peso** — flagship narrative in 8 tabs: ① Flujo · ② Entran · ③ Se prometen · ④ Aterrizan · ⑤ Explora · ⑥ Ciudadano (12 categorías) · ⑦ Emblemáticos (Cablebús, Pilares, Mi Beca, Utopías…) · ⑧ Pregunta (chat con Claude). | Ingresos + Egresos CP 2018–2022 + Aprobado 2024 + Rally + Paquete Económico 2024 |
| `notebooks/tus_100_pesos.py` | **Tus 100 pesos** — citizen-category drill-down: 12 cards → click for Level-2 named programs. URL-state (`?cat=L1-transporte`) + alcaldía zoom. Demo target. | `data/clean/budget_tree.parquet` |
| `notebooks/obra_map.py` | *¿Qué se construyó en tu calle?* — interactive map of 23k georeferenced federal projects (2013–2018). Click any dot for project detail. | Rally ¿Cómo van las obras? |
| `notebooks/budget_dashboard.py` | *¿A dónde va el dinero público?* — CDMX budget by purpose, agency, SDG, chapter. Plan-vs-actual. | Presupuesto de egresos |
| `notebooks/explore.py` | Generic CSV explorer — drop any CSV into `data/`, get instant charts. | — |

**Sibling branch** — `red-team-accountability` carries `notebooks/proveedores.py`, a forensic supplier/direct-assignment audit (only 6.2 % of projects publish modalidad + contratista, IR3 concentration, convocante favorites). Same data, adversarial POV. See [`RED_TEAM.md`](https://github.com/diegomondra/impact-lab-cdmx/blob/red-team-accountability/RED_TEAM.md) on that branch.

---

## Prerequisites

- **[uv](https://docs.astral.sh/uv/getting-started/installation/)** (Python package manager — one-line install)
- **bash** (on Windows: use Git Bash, which ships with [Git for Windows](https://git-scm.com/download/win))
- **git**, **curl**

You don't need to install Python yourself — `uv` handles that.

## Run it (3 commands)

```bash
git clone git@github.com:diegomondra/impact-lab-cdmx.git
cd impact-lab-cdmx
uv sync                              # installs Python + all deps (~30s first time)
bash scripts/download_data.sh        # downloads ~200MB of CDMX open data (idempotent)
uv run marimo run notebooks/ruta_del_peso.py   # 8-tab flagship narrative
```

Browser opens at **http://localhost:2718**.

To run a different dashboard, swap the last line:

```bash
uv run marimo run notebooks/tus_100_pesos.py     # citizen-category drill-down
uv run marimo run notebooks/obra_map.py
uv run marimo run notebooks/budget_dashboard.py
uv run marimo run notebooks/explore.py
```

### Enable the chat tab (⑧ Pregunta)

The conversational agent in `ruta_del_peso.py` calls Claude. Drop your key
into a `.env` at the repo root:

```bash
echo 'ANTHROPIC_API_KEY=sk-ant-...' > .env
```

`.env` is gitignored. Without a key the rest of the dashboard works normally;
tab ⑧ just renders an inert "API key required" hint.

### Edit mode (live-coding)

```bash
uv run marimo edit notebooks/obra_map.py
```

Changes to the code re-run reactively in the browser. This is how you iterate on the dashboard.

### Port already in use?

```bash
uv run marimo run notebooks/obra_map.py --port 2719
```

---

## Add your own data

Drop a CSV into `data/`. Everything in `data/` is gitignored except the README, so sensitive files stay local.

Open `notebooks/explore.py` and pick your file from the dropdown.

## New notebook from scratch

```bash
uv run marimo new notebooks/my_analysis.py
```

---

## Stack

- **[Marimo](https://marimo.io)** — reactive Python notebooks that double as web apps. Pure `.py` files, git-friendly.
- **[Polars](https://pola.rs)** — fast DataFrames.
- **[Plotly](https://plotly.com/python/)** — interactive charts and maps.
- **[Anthropic SDK](https://docs.anthropic.com/)** — powers the ⑧ Pregunta chat tab.
- **[uv](https://docs.astral.sh/uv/)** — Python + dependency management.

## Project structure

```
.
├── data/                           # raw CSVs (gitignored — fetched by download_data.sh)
│   └── clean/                      # pre-aggregated parquets (committed — UI boots without re-download)
├── crosswalk/                      # editorial spine: 19,453 rows → 12 citizen categories
│   ├── crosswalk.csv               # row-level mapping with rationale
│   ├── named_programs_2024.csv     # 81 flagship programs (Cablebús, Pilares, Mi Beca…)
│   ├── citizen_categories.md       # taxonomy with icons + descriptions
│   └── METHODOLOGY.md              # Spanish methodology footnote
├── notebooks/
│   ├── ruta_del_peso.py            # 8-tab flagship narrative
│   ├── tus_100_pesos.py            # 12-card citizen drill-down (deploy target)
│   ├── obra_map.py                 # map of federal projects in CDMX
│   ├── budget_dashboard.py         # CDMX budget allocation dashboard
│   ├── explore.py                  # generic CSV explorer
│   └── lib/                        # shared loaders + style helpers
├── mcp/src/cdmx_data/              # MCP server: 7 dashboard tools + Presupuesto domain
├── scripts/
│   ├── download_data.sh            # 7-tier idempotent fetcher (~200 MB)
│   └── smoke_notebooks.sh          # py_compile + boot sanity check
├── docs/DEV_MANU_HANDOFF.md        # what dev-manu landed and why
├── DATA_NOTES.md                   # data-quality audit + published-headline gate
├── prd/                            # hackathon orchestration docs (PRD, agent briefs, audit)
├── Dockerfile + fly.toml           # Fly.io fallback deploy
├── pyproject.toml                  # dependencies + marimo runtime config
└── README.md
```

---

## Deploy

The primary demo target is the hackathon app `notebooks/tus_100_pesos.py`.
Two paths are supported, with a third as emergency fallback.

### Primary — Marimo Cloud

Zero-infrastructure option. Connect this repo in the [Marimo Cloud](https://marimo.io/cloud)
dashboard, pick `notebooks/tus_100_pesos.py` as the entry, deploy. Marimo handles
HTTPS, the public URL, and restarts on push. This is the fastest path and the
one rehearsed for the pitch.

### Fallback — Fly.io

Scaffolding is committed (`Dockerfile`, `fly.toml`) so a redeploy is one command:

```bash
flyctl launch --copy-config --no-deploy   # first time: claim the app name
flyctl deploy                              # build + push the image
flyctl open                                # opens the live URL
```

The image serves whichever notebook `MARIMO_NOTEBOOK` points at (defaults to
`notebooks/tus_100_pesos.py` via `fly.toml`). To serve a different notebook
in place — for example, to swap to `budget_dashboard.py` while the main app
is being fixed:

```bash
flyctl secrets set MARIMO_NOTEBOOK=notebooks/budget_dashboard.py
flyctl deploy
```

The Dockerfile bundles `data/clean/` (parquet contract committed to git per the
Agent 1 ↔ Agent 2 handoff) but not `data/*.csv` — those remain reproducible
via `scripts/download_data.sh` on a fresh machine.

### Emergency fallback — Tailscale Funnel

If both of the above are blocked at pitch time, expose the lead's laptop:

```bash
uv run marimo run notebooks/tus_100_pesos.py --host 0.0.0.0 --port 2718 --headless --no-token
tailscale funnel 2718
```

The Funnel URL (`https://<host>.<tailnet>.ts.net`) works for judges without
Tailscale auth. Document the URL in `DEMO_RUNBOOK.md` at hour 4–5.

### The other notebooks

`budget_dashboard.py`, `obra_map.py`, and `explore.py` remain standalone demos.
They run locally via `uv run marimo run notebooks/<name>.py`. They are not part
of the deployed bundle in order to keep the primary URL a single surface — if
judges ask to see them, the lead runs them locally from the same repo.

---

## Troubleshooting

**`uv: command not found`** — install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh` (macOS/Linux) or [see Windows instructions](https://docs.astral.sh/uv/getting-started/installation/).

**Download script fails** — the CDMX portal is sometimes slow. Re-run `bash scripts/download_data.sh`. The curl commands will resume/overwrite.

**Output is too large error** — the map renders 23k points. The `output_max_bytes` cap is set in `pyproject.toml`. If you hit it, raise the value or add a filter to reduce points.

**Data looks old** — the Rally dataset (obra_map.py) covers 2013–2018; this is what CDMX publishes with georeferencing. The dashboard banner makes this explicit.

**⑧ Pregunta says "ANTHROPIC_API_KEY no está configurada"** — your shell may have an empty `ANTHROPIC_API_KEY=` set (common in inherited terminals). The loader treats empty as absent and reads `.env`; if you still see the warning, restart the marimo server in a fresh shell after writing `.env`.

**The 2024 budget total** — the `egresos_2024_aprobado.csv` sums to MXN 267,965,350,437, the exact number in the Decreto de Presupuesto de Egresos 2024. See `DATA_NOTES.md` for the validation gate.

---

## Data provenance & methodology

- **`crosswalk/METHODOLOGY.md`** — bucket choices, classification axis, overhead handling, alcaldía attribution, and known limitations (Spanish).
- **`DATA_NOTES.md`** — hour-0 inventory, depth assessment, schema stability across 7 years, ingresos vs egresos coverage.
- **`docs/DEV_MANU_HANDOFF.md`** — integration map describing what each dev-manu artifact unlocks for the flagship.
- **`data/clean/SCHEMAS.md`** — Polars contract for the parquet files consumed by `tus_100_pesos.py` and the ⑥ Ciudadano tab.

---

*Licensed under the terms of the underlying public datasets. See [datos.cdmx.gob.mx](https://datos.cdmx.gob.mx) for source licensing.*
