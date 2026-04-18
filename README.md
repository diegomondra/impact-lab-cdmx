# impact-lab-cdmx

Interactive dashboards for Ciudad de México public data — built at Claude Mexico City Lab 2026.

Three dashboards tell three stories with official data from [datos.cdmx.gob.mx](https://datos.cdmx.gob.mx):

| Dashboard | Story | Source |
|---|---|---|
| `notebooks/obra_map.py` | *¿Qué se construyó en tu calle?* — 23k georeferenced federal projects (2013–2018). Click any dot to see cost flow, beneficiaries, contractor, and contract PDF. | Rally ¿Cómo van las obras? |
| `notebooks/budget_dashboard.py` | *¿A dónde va el dinero público?* — CDMX budget by purpose, agency, SDG, and chapter. Plan-vs-actual execution view. | Presupuesto de egresos 2023/2024 |
| `notebooks/explore.py` | Generic CSV explorer — drop any CSV into `data/` and get instant charts. | — |

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
bash scripts/download_data.sh        # downloads ~85MB of CDMX open data
uv run marimo run notebooks/obra_map.py
```

Browser opens at **http://localhost:2718**.

To run a different dashboard, swap the last line:

```bash
uv run marimo run notebooks/budget_dashboard.py
uv run marimo run notebooks/explore.py
```

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
- **[uv](https://docs.astral.sh/uv/)** — Python + dependency management.

## Project structure

```
.
├── data/                           # CSVs (gitignored — run scripts/download_data.sh)
├── notebooks/
│   ├── obra_map.py                 # Map of federal projects in CDMX
│   ├── budget_dashboard.py         # CDMX budget allocation dashboard
│   └── explore.py                  # Generic CSV explorer
├── scripts/
│   └── download_data.sh            # Fetches CDMX open data (~85MB)
├── pyproject.toml                  # Dependencies + marimo config
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

---

*Licensed under the terms of the underlying public datasets. See [datos.cdmx.gob.mx](https://datos.cdmx.gob.mx) for source licensing.*
