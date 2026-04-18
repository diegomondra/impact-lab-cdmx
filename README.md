# impact-lab-cdmx

Single integrated dashboard for Ciudad de Mexico public data, built at Claude Mexico City Lab 2026.

Follow public money from budget lines to projects on the street in one product.

Primary deliverable:

|Product|Story|Source|
|---|---|---|
|`notebooks/producto_unico.py`|Producto unico integrado: presupuesto + obra publica en una sola experiencia.|Presupuesto CDMX + Rally ¿Como van las obras?|

---

## Narrative flow

The deliverable follows one storytelling arc:

1. **Act 1 · Panorama integrado**: budget and execution at high level.
2. **Act 2 · Presupuesto**: where money is allocated and spent by function.
3. **Act 3 · Territorio**: where projects land in the city with georeferenced evidence.

This keeps demo and analysis in one coherent product and avoids switching between notebooks.

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

Open `notebooks/explore.py` and pick your file from the dropdown (optional support tool).

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
│   ├── budget_dashboard.py         # Legacy/support notebook
│   ├── obra_map.py                 # Legacy/support notebook
│   └── explore.py                  # Optional generic CSV explorer
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

## Legacy notebooks

`notebooks/budget_dashboard.py` and `notebooks/obra_map.py` are kept for backward compatibility and reference. The official deliverable for evaluation is `notebooks/producto_unico.py`.

---

## Troubleshooting

**`uv: command not found`** — install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh` (macOS/Linux) or [see Windows instructions](https://docs.astral.sh/uv/getting-started/installation/).

**Download script fails** — the CDMX portal is sometimes slow. Re-run `bash scripts/download_data.sh`. The curl commands will resume/overwrite.

**Output is too large error** — the map renders 23k points. The `output_max_bytes` cap is set in `pyproject.toml`. If you hit it, raise the value or add a filter to reduce points.

**Data looks old** — the Rally dataset used in the integrated product covers 2013–2018; this is what CDMX publishes with georeferencing.

---

*Licensed under the terms of the underlying public datasets. See [datos.cdmx.gob.mx](https://datos.cdmx.gob.mx) for source licensing.*
