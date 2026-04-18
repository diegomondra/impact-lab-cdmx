# impact-lab-cdmx

Interactive dashboards for Ciudad de México public data — built at Claude Mexico City Lab 2026.

Four dashboards with official data from [datos.cdmx.gob.mx](https://datos.cdmx.gob.mx):

| Dashboard | Story | Source |
|---|---|---|
| `notebooks/ruta_del_peso.py` | **La ruta de tu peso** — 3-act narrative: ① ingresos entran → ② egresos se prometen → ③ contratistas aterrizan. Filterable por año (2018–2024) y alcaldía. | Ingresos + Egresos CP 2018–2022 + Rally |
| `notebooks/obra_map.py` | *¿Qué se construyó en tu calle?* — interactive map of 23k georeferenced federal projects (2013–2018). Click any dot for project detail. | Rally ¿Cómo van las obras? |
| `notebooks/budget_dashboard.py` | *¿A dónde va el dinero público?* — CDMX budget by purpose, agency, SDG, chapter. Plan-vs-actual. | Presupuesto de egresos |
| `notebooks/explore.py` | Generic CSV explorer — drop any CSV into `data/`, get instant charts. | — |

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
bash scripts/download_data.sh        # downloads ~220MB of CDMX open data
uv run marimo run notebooks/ruta_del_peso.py   # featured 3-act narrative
```

Browser opens at **http://localhost:2718**.

To run a different dashboard, swap the last line:

```bash
uv run marimo run notebooks/obra_map.py
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
│   ├── ruta_del_peso.py            # 3-act narrative: ingresos → egresos → contratistas
│   ├── obra_map.py                 # Map of federal projects in CDMX
│   ├── budget_dashboard.py         # CDMX budget allocation dashboard
│   └── explore.py                  # Generic CSV explorer
├── scripts/
│   └── download_data.sh            # Fetches CDMX open data (~220MB)
├── pyproject.toml                  # Dependencies + marimo config
└── README.md
```

---

## Troubleshooting

**`uv: command not found`** — install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh` (macOS/Linux) or [see Windows instructions](https://docs.astral.sh/uv/getting-started/installation/).

**Download script fails** — the CDMX portal is sometimes slow. Re-run `bash scripts/download_data.sh`. The curl commands will resume/overwrite.

**Output is too large error** — the map renders 23k points. The `output_max_bytes` cap is set in `pyproject.toml`. If you hit it, raise the value or add a filter to reduce points.

**Data looks old** — the Rally dataset (obra_map.py) covers 2013–2018; this is what CDMX publishes with georeferencing. The dashboard banner makes this explicit.

---

*Licensed under the terms of the underlying public datasets. See [datos.cdmx.gob.mx](https://datos.cdmx.gob.mx) for source licensing.*
