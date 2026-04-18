# impact-lab-cdmx

Single integrated dashboard for Ciudad de Mexico public data, built at Claude Mexico City Lab 2026.

Follow public money in one product, without forcing different datasets into a fake single metric story.

Primary deliverable:

|Product|Story|Source|
|---|---|---|
|`notebooks/producto_unico.py`|Producto unico con dos vistas claras: Presupuesto y Obra publica.|Presupuesto CDMX + Rally ¿Como van las obras?|

---

## Product logic

The deliverable is a single app with two complementary views:

1. **Presupuesto**: how money is allocated and, when available, how much has been exercised.
2. **Obra publica**: where projects are located, how much they exercised, and their physical progress.
3. **Shared frame**: one visual language and one product shell, without pretending both datasets measure the same thing.

This keeps the delivery coherent while avoiding misleading comparisons.

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

1. Open `notebooks/producto_unico.py`.
2. Start in the `Presupuesto` view and explain allocation, execution, and concentration by function or agency.
3. Switch to the `Obra publica` view and explain where projects are located and how much progress they report.
4. Close by stressing that the product is unified by experience, not by forcing incompatible datasets into one metric.

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
