import marimo

__generated_with = "0.10.0"
app = marimo.App(width="medium", app_title="CSV Explorer")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        # CSV Explorer

        Drop a CSV in `data/` and pick it below. Everything is reactive — change a
        filter or column and the charts update instantly.
        """
    )
    return


@app.cell
def _():
    import marimo as mo
    from pathlib import Path
    import polars as pl
    import plotly.express as px
    import plotly.graph_objects as go

    DATA_DIR = Path(__file__).parent.parent / "data"
    return DATA_DIR, Path, go, mo, pl, px


@app.cell(hide_code=True)
def _(DATA_DIR, mo):
    csv_files = sorted(DATA_DIR.glob("*.csv"))
    file_picker = mo.ui.dropdown(
        options={f.name: f for f in csv_files} if csv_files else {"(no CSVs found)": None},
        label="CSV file",
        value=csv_files[0].name if csv_files else "(no CSVs found)",
    )
    file_picker
    return (file_picker,)


@app.cell
def _(file_picker, mo, pl):
    mo.stop(file_picker.value is None, mo.md("**Add a CSV to `data/` to get started.**"))

    df = pl.read_csv(file_picker.value, infer_schema_length=10_000)
    mo.md(f"**{df.height:,} rows × {df.width} columns** from `{file_picker.value.name}`")
    return (df,)


@app.cell(hide_code=True)
def _(df, mo):
    mo.ui.table(df.head(50).to_pandas(), selection=None, page_size=10)
    return


@app.cell(hide_code=True)
def _(df, mo):
    mo.md("## Schema")
    schema_rows = [
        {"column": name, "dtype": str(dtype), "nulls": df[name].null_count(), "unique": df[name].n_unique()}
        for name, dtype in zip(df.columns, df.dtypes)
    ]
    mo.ui.table(schema_rows, selection=None, page_size=20)
    return


@app.cell(hide_code=True)
def _(df, mo, pl):
    numeric_cols = [c for c, t in zip(df.columns, df.dtypes) if t.is_numeric()]
    categorical_cols = [
        c for c, t in zip(df.columns, df.dtypes)
        if t == pl.Utf8 or (df[c].n_unique() <= 50 and df[c].n_unique() > 1)
    ]

    chart_type = mo.ui.dropdown(
        options=["histogram", "scatter", "bar (count)", "box", "line"],
        value="histogram",
        label="Chart",
    )
    x_col = mo.ui.dropdown(options=df.columns, label="X", value=df.columns[0])
    y_col = mo.ui.dropdown(
        options=["(none)"] + numeric_cols,
        label="Y",
        value=numeric_cols[0] if numeric_cols else "(none)",
    )
    color_col = mo.ui.dropdown(
        options=["(none)"] + categorical_cols,
        label="Color",
        value="(none)",
    )

    mo.md("## Build a chart")
    return categorical_cols, chart_type, color_col, numeric_cols, x_col, y_col


@app.cell(hide_code=True)
def _(chart_type, color_col, mo, x_col, y_col):
    mo.hstack([chart_type, x_col, y_col, color_col], justify="start", gap=1)
    return


@app.cell
def _(chart_type, color_col, df, mo, px, x_col, y_col):
    pdf = df.to_pandas()
    color = color_col.value if color_col.value != "(none)" else None
    y = y_col.value if y_col.value != "(none)" else None

    template = "plotly_white"
    common = dict(template=template, color=color, height=480)

    match chart_type.value:
        case "histogram":
            fig = px.histogram(pdf, x=x_col.value, **common, nbins=40, marginal="box")
        case "scatter":
            mo.stop(y is None, mo.md("*Pick a Y column for scatter.*"))
            fig = px.scatter(pdf, x=x_col.value, y=y, **common, opacity=0.7, trendline="ols")
        case "bar (count)":
            counts = pdf[x_col.value].value_counts().reset_index().head(30)
            counts.columns = [x_col.value, "count"]
            fig = px.bar(counts, x=x_col.value, y="count", template=template, height=480)
        case "box":
            mo.stop(y is None, mo.md("*Pick a Y column for box plot.*"))
            fig = px.box(pdf, x=x_col.value, y=y, **common)
        case "line":
            mo.stop(y is None, mo.md("*Pick a Y column for line chart.*"))
            fig = px.line(pdf.sort_values(x_col.value), x=x_col.value, y=y, **common)

    fig.update_layout(
        font=dict(family="Inter, system-ui, sans-serif", size=13),
        margin=dict(l=40, r=20, t=40, b=40),
        hoverlabel=dict(bgcolor="white", font_size=12),
    )
    fig
    return


@app.cell(hide_code=True)
def _(df, mo, numeric_cols, px):
    mo.md("## Correlations")
    if len(numeric_cols) >= 2:
        corr = df.select(numeric_cols).to_pandas().corr()
        fig = px.imshow(
            corr,
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1,
            aspect="auto",
            template="plotly_white",
            height=500,
        )
        fig.update_layout(
            font=dict(family="Inter, system-ui, sans-serif", size=13),
            margin=dict(l=60, r=20, t=40, b=60),
        )
        fig
    else:
        mo.md("*Need at least two numeric columns for a correlation heatmap.*")
    return


if __name__ == "__main__":
    app.run()
