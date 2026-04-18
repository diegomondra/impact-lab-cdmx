# impact-lab-cdmx

Quick CSV data exploration and beautiful visualizations. Built for fast iteration: drop a CSV into `data/`, open a Marimo notebook, and get interactive Plotly/Altair charts.

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
├── data/              # CSVs (gitignored)
├── notebooks/         # Marimo notebooks (.py files, git-friendly)
│   └── explore.py     # Starter notebook
├── pyproject.toml     # Dependencies
└── README.md
```
