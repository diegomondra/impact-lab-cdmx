# impact-lab-cdmx

Interactive dashboards for Ciudad de México public data — built at Claude Mexico City Lab 2026.

Follow public money from budget lines to projects on the street.

The project uses official datasets from [datos.cdmx.gob.mx](https://datos.cdmx.gob.mx) and is now explicitly aligned around **2018-2019** for cross-dashboard comparability:

|Dashboard|Story|Source|
|---|---|---|
|`notebooks/producto_unico.py`|*Producto único integrado* — una sola experiencia con presupuesto + obra pública para demo y entrega final.|Presupuesto CDMX + Rally ¿Cómo van las obras?|
|`notebooks/obra_map.py`|*¿Qué se construyó en tu calle?* — 23k georeferenced federal projects (2013-2018). Includes execution, completion, contractor, and territorial distribution.|Rally ¿Cómo van las obras?|
|`notebooks/budget_dashboard.py`|*¿A dónde va el dinero público?* — budget allocation and execution by function, agency, SDG, and spending chapter. Prioritizes 2018-2019 cuts (with 2023-2024 as recent reference).|Presupuesto de egresos 2018/2019/2023/2024|
|`notebooks/explore.py`|Generic CSV explorer — drop any CSV into `data/` and get instant charts.|—|

---

## Narrative flow

The primary deliverable (`notebooks/producto_unico.py`) follows a single storytelling arc:

1. **Act 1 · Panorama integrado**: budget and execution at high level.
2. **Act 2 · Presupuesto**: where money is allocated and spent by function.
3. **Act 3 · Territorio**: where projects land in the city with georeferenced evidence.

This keeps demo and analysis in one coherent product.

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
bash scripts/download_data.sh        # downloads ~290MB of CDMX open data
uv run marimo run notebooks/producto_unico.py
```

Browser opens at **<http://localhost:2718>**.

To run a different dashboard, swap the last line:

```bash
uv run marimo run notebooks/budget_dashboard.py
uv run marimo run notebooks/obra_map.py
uv run marimo run notebooks/explore.py
```

### Edit mode (live-coding)

```bash
uv run marimo edit notebooks/producto_unico.py
```

Changes to the code re-run reactively in the browser. This is how you iterate on the dashboard.

### Port already in use?

```bash
uv run marimo run notebooks/producto_unico.py --port 2719
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

```text
.
├── data/                           # CSVs (gitignored — run scripts/download_data.sh)
├── notebooks/
│   ├── producto_unico.py           # Single integrated deliverable (budget + territory)
│   ├── obra_map.py                 # Map of federal projects in CDMX
│   ├── budget_dashboard.py         # Budget dashboard aligned to 2018-2019 narrative
│   └── explore.py                  # Generic CSV explorer
├── scripts/
│   └── download_data.sh            # Fetches CDMX open data (~290MB)
├── pyproject.toml                  # Dependencies + marimo config
└── README.md
```

---

## Demo script (3-5 min)

1. Open `notebooks/producto_unico.py` and select a 2018 or 2019 budget cut.
2. In Act 1, explain the integrated KPI story (budget + execution + project progress).
3. In Act 2, show concentration by budget function and execution gap.
4. In Act 3, connect the same story to map evidence and territorial distribution.

---

## Troubleshooting

**`uv: command not found`** — install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh` (macOS/Linux) or [see Windows instructions](https://docs.astral.sh/uv/getting-started/installation/).

**Download script fails** — the CDMX portal is sometimes slow. Re-run `bash scripts/download_data.sh`. The curl commands will resume/overwrite.

**Output is too large error** — the map renders 23k points. The `output_max_bytes` cap is set in `pyproject.toml`. If you hit it, raise the value or add a filter to reduce points.

**Data looks old** — the Rally dataset (obra_map.py) covers 2013–2018; this is what CDMX publishes with georeferencing. The dashboard banner makes this explicit.

---

*Licensed under the terms of the underlying public datasets. See [datos.cdmx.gob.mx](https://datos.cdmx.gob.mx) for source licensing.*
