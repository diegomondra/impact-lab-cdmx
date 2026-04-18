# impact-lab-cdmx

Interactive dashboards for CDMX public data. Built at Claude Mexico City Lab 2026.

## Dashboards

- **`notebooks/budget_dashboard.py`** — *¿A dónde va el dinero público?* Budget allocation by purpose, agency, SDG alignment, and economic classification. Data from [datos.cdmx.gob.mx](https://datos.cdmx.gob.mx).
- **`notebooks/explore.py`** — Generic CSV explorer for any dataset dropped into `data/`.

## Quick start

```bash
uv sync                                 # install deps
bash scripts/download_data.sh           # fetch CDMX budget CSVs (~50MB)
uv run marimo run notebooks/budget_dashboard.py   # app mode
# or
uv run marimo edit notebooks/budget_dashboard.py  # reactive editing
```

Browser opens at `http://localhost:2718`.

## Stack

- **[Marimo](https://marimo.io)** — reactive Python notebooks that run as apps. Git-friendly (pure `.py` files).
- **[Polars](https://pola.rs)** — fast DataFrame library (use `pandas` too if you prefer).
- **[Plotly](https://plotly.com/python/)** — interactive, publication-quality charts.
- **[Altair](https://altair-viz.github.io)** — grammar-of-graphics for declarative viz.
- **[uv](https://docs.astral.sh/uv/)** — fast Python package manager.

## Setup

```bash
uv sync
```

That creates `.venv/` and installs everything. First run takes ~30s; afterwards it's instant.

## Run a notebook

Edit mode (reactive, live-coding):

```bash
uv run marimo edit notebooks/explore.py
```

App mode (clean UI, read-only, shareable):

```bash
uv run marimo run notebooks/explore.py
```

Browser opens at `http://localhost:2718`.

## Add data

Drop CSVs into `data/`. They're gitignored by default — add exceptions in `.gitignore` if you want to commit a specific file.

## New notebook

```bash
uv run marimo new notebooks/my_analysis.py
```

## Project structure

```
.
├── data/                       # CSVs (gitignored — run scripts/download_data.sh)
├── notebooks/
│   ├── budget_dashboard.py     # CDMX budget allocation dashboard
│   └── explore.py              # Generic CSV explorer
├── scripts/
│   └── download_data.sh        # Fetches CDMX datasets
├── pyproject.toml
└── README.md
```
