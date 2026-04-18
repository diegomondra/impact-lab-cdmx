import marimo

__generated_with = "0.23.1"
app = marimo.App(
    width="full",
    app_title="Impact Lab CDMX · Gasto Publico",
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=IBM+Plex+Sans:wght@400;500;600&display=swap');
        :root {
            --font-display: 'Sora', 'IBM Plex Sans', sans-serif;
            --font-body: 'IBM Plex Sans', -apple-system, system-ui, sans-serif;
            --text-strong: #0f172a;
            --text-muted: #64748b;
            --surface: #f6f8fb;
            --surface-card: #ffffff;
            --border-soft: #d9e2ec;
            --radius-lg: 16px;
            --radius-xl: 24px;
            --shadow-card: 0 10px 24px rgba(15, 23, 42, 0.06);
            --shadow-hero: 0 20px 48px rgba(15, 23, 42, 0.12);
            --budget: #2f6690;
            --works: #9f2241;
            --accent: #d97706;
        }
        body {
            background: linear-gradient(180deg, #f8fafc 0%, #f2f6fb 100%);
        }
        .hero {
            font-family: var(--font-display);
            padding: 36px 40px 30px;
            background:
                radial-gradient(1200px 280px at 100% -20%, rgba(47, 102, 144, 0.14), transparent 55%),
                linear-gradient(135deg, #ffffff 0%, #eef4fb 100%);
            color: var(--text-strong);
            border-radius: var(--radius-xl);
            border: 1px solid var(--border-soft);
            box-shadow: var(--shadow-hero);
            margin-bottom: 12px;
        }
        .note {
            margin: 10px 0 20px;
            padding: 14px 18px;
            background: #fff7e8;
            border: 1px solid #f3d58c;
            border-left: 5px solid var(--accent);
            border-radius: 12px;
            color: #7c3b07;
            font-family: var(--font-body);
            font-size: 13px;
            line-height: 1.6;
        }
        .card {
            background: var(--surface-card);
            border: 1px solid var(--border-soft);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-card);
            padding: 16px 18px;
        }
        .kpi-grid {
            display: flex;
            gap: 14px;
            flex-wrap: wrap;
            margin: 14px 0 22px;
        }
        .kpi {
            flex: 1;
            min-width: 210px;
            background: var(--surface-card);
            border: 1px solid var(--border-soft);
            border-radius: var(--radius-lg);
            padding: 18px 20px;
            box-shadow: var(--shadow-card);
        }
        .kpi-label {
            font-family: var(--font-body);
            font-size: 10px;
            color: var(--text-muted);
            letter-spacing: 1.2px;
            text-transform: uppercase;
            font-weight: 700;
        }
        .kpi-value {
            font-family: var(--font-display);
            font-size: 30px;
            font-weight: 800;
            color: var(--text-strong);
            margin-top: 8px;
            letter-spacing: -0.8px;
            line-height: 1.05;
        }
        .chip {
            display: inline-block;
            padding: 5px 9px;
            border-radius: 999px;
            font-size: 11px;
            font-family: var(--font-body);
            font-weight: 700;
            letter-spacing: 0.6px;
            text-transform: uppercase;
        }
        .chip-budget {
            background: rgba(47, 102, 144, 0.12);
            color: var(--budget);
        }
        .chip-works {
            background: rgba(159, 34, 65, 0.12);
            color: var(--works);
        }
        .story-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 14px;
            margin: 14px 0 20px;
        }
        .story-title {
            font-family: var(--font-display);
            font-size: 18px;
            font-weight: 700;
            color: var(--text-strong);
            margin-top: 8px;
        }
        .story-copy {
            font-family: var(--font-body);
            color: var(--text-muted);
            font-size: 13px;
            line-height: 1.55;
            margin-top: 6px;
        }
        </style>

        <div class="hero">
            <div style="font-size:12px;letter-spacing:2.4px;text-transform:uppercase;font-weight:700;color:#486581;">
                Ciudad de Mexico · Impact Lab · Producto unico
            </div>
            <div style="font-size:38px;font-weight:800;line-height:1.08;letter-spacing:-0.9px;margin-top:8px;max-width:900px;">
                Gasto publico de la CDMX, explicado sin forzar una sola base de datos
            </div>
            <div style="font-family:var(--font-body);font-size:15px;line-height:1.65;max-width:860px;color:#334155;margin-top:12px;">
                Esta app organiza dos vistas oficiales y complementarias dentro del mismo producto:
                una para leer el presupuesto y otra para inspeccionar obra publica georreferenciada.
            </div>
        </div>

        <div class="note">
            <b>Como leer este producto.</b> Aqui no se mezclan artificialmente dos datasets distintos.
            La vista de <b>Presupuesto</b> responde como se asigna y se ejerce el gasto; la vista de
            <b>Obra publica</b> responde donde estan los proyectos y cuanto avanzaron.
        </div>
        """
    )
    return


@app.cell
def _():
    import marimo as mo
    from pathlib import Path

    import plotly.express as px
    import plotly.graph_objects as go
    import polars as pl

    DATA_DIR = Path(__file__).parent.parent / "data"
    FONT = "Sora, IBM Plex Sans, -apple-system, system-ui, sans-serif"

    RAMO_PALETTE = {
        "Aportaciones Federales para Entidades Federativas y Municipios": "#23395B",
        "Provisiones Salariales y Economicas": "#2F6690",
        "Comunicaciones y Transportes": "#3A7CA5",
        "Medio Ambiente y Recursos Naturales": "#00A7A0",
        "Salud": "#C94C4C",
        "Educacion Publica": "#6D597A",
        "Gobernacion": "#264653",
        "Cultura": "#F4A259",
        "Desarrollo Agrario, Territorial y Urbano": "#2A9D8F",
    }

    def fmt_mxn(v, short=True):
        if v is None:
            return "-"
        v = float(v)
        sign = "-" if v < 0 else ""
        v = abs(v)
        if short:
            if v >= 1e9:
                return f"{sign}${v / 1e9:,.2f} mmdp"
            if v >= 1e6:
                return f"{sign}${v / 1e6:,.1f} mdp"
            if v >= 1e3:
                return f"{sign}${v / 1e3:,.0f} k"
            return f"{sign}${v:,.0f}"
        return f"{sign}${v:,.0f}"

    def fmt_int(v):
        if v is None:
            return "-"
        return f"{int(v):,}"

    def style_fig(fig, height=460):
        fig.update_layout(
            font=dict(family=FONT, size=13, color="#1E293B"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=18, r=18, t=40, b=16),
            height=height,
            hoverlabel=dict(
                bgcolor="#0f172a",
                bordercolor="#334155",
                font=dict(family=FONT, size=12, color="#f8fafc"),
            ),
            legend=dict(
                font=dict(family=FONT, size=11, color="#334155"),
                bgcolor="rgba(255,255,255,0.82)",
                bordercolor="#dbe7f3",
                borderwidth=1,
            ),
        )
        return fig

    return DATA_DIR, FONT, RAMO_PALETTE, fmt_int, fmt_mxn, go, mo, pl, px, style_fig


@app.cell
def _(DATA_DIR, pl):
    def load_budget(path):
        return pl.read_csv(
            path,
            infer_schema_length=10_000,
            null_values=["NA", ""],
            truncate_ragged_lines=True,
            schema_overrides={
                "monto_aprobado": pl.Float64,
                "monto_modificado": pl.Float64,
                "monto_ejercido": pl.Float64,
            },
        )

    budget_files = {
        "2018 · cuenta publica": DATA_DIR / "egresos_2018_cp.csv",
        "2019 Q1 · avance trimestral": DATA_DIR / "egresos_2019_01_trimestre.csv",
        "2019 Q2 · avance trimestral": DATA_DIR / "egresos_2019_02_trimestre.csv",
        "2019 Q3 · avance trimestral": DATA_DIR / "egresos_2019_03_trimestre.csv",
        "2023 Q3 · avance trimestral": DATA_DIR / "egresos_2023_03_trimestre.csv",
        "2018 · aprobado (planeacion)": DATA_DIR / "egresos_2018_aprobado.csv",
        "2019 · aprobado (planeacion)": DATA_DIR / "egresos_2019_aprobado.csv",
        "2024 · aprobado (planeacion)": DATA_DIR / "egresos_2024_aprobado.csv",
    }
    budget_files = {k: v for k, v in budget_files.items() if v.exists()}
    budget_datasets = {k: load_budget(v) for k, v in budget_files.items()}

    raw_obras = pl.read_csv(
        DATA_DIR / "rally_obras.csv",
        infer_schema_length=10_000,
        null_values=["NA", ""],
        truncate_ragged_lines=True,
        ignore_errors=True,
    )

    raw_obras = raw_obras.with_columns(
        [
            pl.col("latitud").cast(pl.Float64, strict=False),
            pl.col("longitud").cast(pl.Float64, strict=False),
            pl.col("monto_aprobado").cast(pl.Float64, strict=False).fill_null(0),
            pl.col("monto_ejercido").cast(pl.Float64, strict=False).fill_null(0),
            pl.col("avance_fisico").cast(pl.Float64, strict=False).fill_null(0),
        ]
    ).filter(
        pl.col("latitud").is_not_null()
        & pl.col("longitud").is_not_null()
        & (pl.col("latitud").is_between(19.0, 19.7))
        & (pl.col("longitud").is_between(-99.5, -98.9))
    )

    return budget_datasets, raw_obras


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        <div class="story-grid">
            <div class="card">
                <span class="chip chip-budget">Vista 1</span>
                <div class="story-title">Presupuesto</div>
                <div class="story-copy">
                    Sirve para entender asignacion, gasto ejercido y concentracion institucional.
                </div>
            </div>
            <div class="card">
                <span class="chip chip-works">Vista 2</span>
                <div class="story-title">Obra publica</div>
                <div class="story-copy">
                    Sirve para ver proyectos en el territorio, alcaldias, avance fisico y monto ejercido.
                </div>
            </div>
            <div class="card">
                <span class="chip">Regla de lectura</span>
                <div class="story-title">No comparar a la fuerza</div>
                <div class="story-copy">
                    El producto es unico por experiencia, no porque ambos datasets midan exactamente lo mismo.
                </div>
            </div>
        </div>
        """
    )
    return


@app.cell(hide_code=True)
def _(budget_datasets, mo, raw_obras):
    view_selector = mo.ui.dropdown(
        options=["Presupuesto", "Obra publica"],
        value="Presupuesto",
        label="Vista",
    )
    budget_picker = mo.ui.dropdown(
        options=list(budget_datasets.keys()),
        value=list(budget_datasets.keys())[0],
        label="Corte presupuestal",
    )
    alcaldias = sorted(raw_obras["desc_alcaldia"].drop_nulls().unique().to_list())
    alcaldia_filter = mo.ui.multiselect(
        options=alcaldias,
        value=[],
        label="Alcaldia",
    )
    ciclos = sorted(raw_obras["ciclo"].drop_nulls().unique().to_list())
    ciclo_filter = mo.ui.range_slider(
        start=min(ciclos),
        stop=max(ciclos),
        value=(min(ciclos), max(ciclos)),
        step=1,
        label="Periodo",
        show_value=True,
        full_width=False,
    )

    mo.md(
        """
        <div class="card" style="margin: 8px 0 14px;">
            <div style="font-family:var(--font-body);font-size:11px;color:var(--text-muted);letter-spacing:1px;text-transform:uppercase;font-weight:700;margin-bottom:8px;">
                Controles
            </div>
        </div>
        """
    )
    return alcaldia_filter, budget_picker, ciclo_filter, view_selector


@app.cell(hide_code=True)
def _(alcaldia_filter, budget_picker, ciclo_filter, mo, view_selector):
    if view_selector.value == "Presupuesto":
        mo.hstack([view_selector, budget_picker], justify="start", gap=1.2, wrap=True)
    else:
        mo.hstack(
            [view_selector, alcaldia_filter, ciclo_filter],
            justify="start",
            gap=1.2,
            wrap=True,
        )
    return


@app.cell
def _(budget_datasets, budget_picker, pl):
    budget_df = budget_datasets[budget_picker.value]
    mod_sum = budget_df["monto_modificado"].fill_null(0).sum()
    spent_sum = budget_df["monto_ejercido"].fill_null(0).sum()

    if mod_sum > 0:
        budget_label = "Modificado"
        budget_base = "monto_modificado"
    else:
        budget_label = "Aprobado"
        budget_base = "monto_aprobado"

    has_spent = spent_sum > 0
    budget_df = budget_df.with_columns(
        [
            pl.col(budget_base).fill_null(0).alias("_budget"),
            pl.col("monto_ejercido").fill_null(0).alias("_spent"),
        ]
    )
    budget_df = budget_df.filter(
        pl.max_horizontal([pl.col("_budget"), pl.col("_spent")]) > 0
    )
    return budget_df, budget_label, has_spent


@app.cell
def _(alcaldia_filter, ciclo_filter, pl, raw_obras):
    obra_df = raw_obras.filter(pl.col("ciclo").is_between(*ciclo_filter.value))
    if alcaldia_filter.value:
        obra_df = obra_df.filter(pl.col("desc_alcaldia").is_in(alcaldia_filter.value))
    return (obra_df,)


@app.cell(hide_code=True)
def _(mo, view_selector):
    if view_selector.value == "Presupuesto":
        mo.md(
            """
            <div class="card" style="margin: 6px 0 12px; font-family:var(--font-body); color:var(--text-muted); line-height:1.6;">
                <b>Vista activa: Presupuesto.</b> Aqui la pregunta es como se distribuye y se ejerce el gasto.
                No se intenta inferir obra publica a partir de esta tabla.
            </div>
            """
        )
    else:
        mo.md(
            """
            <div class="card" style="margin: 6px 0 12px; font-family:var(--font-body); color:var(--text-muted); line-height:1.6;">
                <b>Vista activa: Obra publica.</b> Aqui la pregunta es donde estan los proyectos,
                cuanto dinero ejercieron y que avance fisico reportan.
            </div>
            """
        )
    return


@app.cell(hide_code=True)
def _(budget_df, budget_label, fmt_mxn, has_spent, mo, view_selector):
    mo.stop(view_selector.value != "Presupuesto")
    budget_total = budget_df["_budget"].sum()
    spent_total = budget_df["_spent"].sum()
    exec_rate = (
        (spent_total / budget_total * 100) if has_spent and budget_total > 0 else None
    )

    def _kpi(label, value):
        return f"""
        <div class="kpi">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """

    _cards = [
        _kpi(f"Presupuesto {budget_label.lower()}", fmt_mxn(budget_total)),
        _kpi("Ejercido", fmt_mxn(spent_total) if has_spent else "No disponible"),
        _kpi(
            "Ejecucion",
            f"{exec_rate:.1f}%" if exec_rate is not None else "No disponible",
        ),
        _kpi("Filas con gasto", f"{budget_df.height:,}"),
    ]

    mo.md(
        f"""
        ## Presupuesto

        <div class="kpi-grid">{"".join(_cards)}</div>
        """
    )
    return


@app.cell(hide_code=True)
def _(budget_label, has_spent, mo, view_selector):
    mo.stop(view_selector.value != "Presupuesto")
    copy = (
        f"Cada barra muestra el presupuesto <b>{budget_label.lower()}</b> y lo ejercido reportado."
        if has_spent
        else f"Este corte solo muestra presupuesto <b>{budget_label.lower()}</b>; no incluye ejercicio reportado."
    )
    mo.md(
        f"""
        <div class="card" style="margin: 8px 0 12px; font-family:var(--font-body); font-size:13px; color:var(--text-muted); line-height:1.6;">
            {copy}
        </div>
        """
    )
    return


@app.cell
def _(budget_df, fmt_mxn, go, has_spent, mo, pl, style_fig, view_selector):
    mo.stop(view_selector.value != "Presupuesto")

    top_funciones = (
        budget_df.with_columns(pl.col("desc_funcion").fill_null("Sin clasificar"))
        .group_by("desc_funcion")
        .agg(
            [
                pl.col("_budget").sum().alias("budget"),
                pl.col("_spent").sum().alias("spent"),
            ]
        )
        .sort("budget", descending=True)
        .head(12)
        .to_pandas()
        .iloc[::-1]
        .reset_index(drop=True)
    )

    fig_budget_functions = go.Figure()
    fig_budget_functions.add_trace(
        go.Bar(
            y=top_funciones["desc_funcion"],
            x=top_funciones["budget"],
            orientation="h",
            marker=dict(color="#D9E7F5"),
            name="Presupuesto",
            hovertemplate="<b>%{y}</b><br>Presupuesto: %{customdata}<extra></extra>",
            customdata=[fmt_mxn(v) for v in top_funciones["budget"]],
        )
    )
    if has_spent:
        fig_budget_functions.add_trace(
            go.Bar(
                y=top_funciones["desc_funcion"],
                x=top_funciones["spent"],
                orientation="h",
                marker=dict(color="#2F6690"),
                name="Ejercido",
                hovertemplate="<b>%{y}</b><br>Ejercido: %{customdata}<extra></extra>",
                customdata=[fmt_mxn(v) for v in top_funciones["spent"]],
            )
        )

    fig_budget_functions.update_layout(
        barmode="overlay",
        bargap=0.35,
        xaxis=dict(showgrid=True, gridcolor="#EDF2F7", tickformat=".2s", title=""),
        yaxis=dict(title="", automargin=True),
        legend=dict(orientation="h", y=1.02, x=0),
    )
    style_fig(fig_budget_functions, height=560)
    fig_budget_functions
    return


@app.cell
def _(budget_df, fmt_mxn, mo, px, pl, style_fig, view_selector):
    mo.stop(view_selector.value != "Presupuesto")

    top_dependencias = (
        budget_df.group_by("desc_unidad_responsable")
        .agg(pl.col("_budget").sum().alias("budget"))
        .sort("budget", descending=True)
        .head(12)
        .to_pandas()
    )
    top_dependencias["label"] = top_dependencias["budget"].apply(fmt_mxn)

    fig_budget_agencies = px.bar(
        top_dependencias.sort_values("budget"),
        x="budget",
        y="desc_unidad_responsable",
        orientation="h",
        text="label",
        color="budget",
        color_continuous_scale=[[0, "#dbe7f3"], [1, "#2f6690"]],
    )
    fig_budget_agencies.update_traces(
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>%{text}<extra></extra>",
        cliponaxis=False,
    )
    fig_budget_agencies.update_layout(
        xaxis=dict(showgrid=True, gridcolor="#EDF2F7", title="", tickformat=".2s"),
        yaxis=dict(title=""),
        coloraxis_showscale=False,
    )
    style_fig(fig_budget_agencies, height=520)
    fig_budget_agencies
    return


@app.cell(hide_code=True)
def _(fmt_int, fmt_mxn, mo, obra_df, pl, view_selector):
    mo.stop(view_selector.value != "Obra publica")
    total_projects = obra_df.height
    total_investment = obra_df["monto_ejercido"].sum()
    total_alcaldias = obra_df["desc_alcaldia"].n_unique()
    completed = obra_df.filter(pl.col("avance_fisico") >= 95).height
    completion_rate = (completed / total_projects * 100) if total_projects else 0

    def _kpi(label, value):
        return f"""
        <div class="kpi">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """

    cards = [
        _kpi("Proyectos", fmt_int(total_projects)),
        _kpi("Inversion ejercida", fmt_mxn(total_investment)),
        _kpi("Alcaldias con obra", fmt_int(total_alcaldias)),
        _kpi("Proyectos terminados", f"{completion_rate:.1f}%"),
    ]
    mo.md(
        f"""
        ## Obra publica

        <div class="kpi-grid">{"".join(cards)}</div>
        """
    )
    return


@app.cell(hide_code=True)
def _(mo, view_selector):
    mo.stop(view_selector.value != "Obra publica")
    mo.md(
        """
        <div class="card" style="margin: 8px 0 12px; font-family:var(--font-body); font-size:13px; color:var(--text-muted); line-height:1.6;">
            Cada punto representa un proyecto federal georreferenciado. Usa los filtros de alcaldia y periodo para reducir el mapa.
        </div>
        """
    )
    return


@app.cell
def _(FONT, RAMO_PALETTE, fmt_mxn, mo, obra_df, px, view_selector):
    mo.stop(view_selector.value != "Obra publica")
    import math

    obras_pdf = (
        obra_df.select(
            [
                "latitud",
                "longitud",
                "desc_ramo",
                "monto_ejercido",
                "nombre_proyecto",
                "desc_alcaldia",
                "ciclo",
            ]
        )
        .to_pandas()
        .copy()
    )

    obras_pdf["desc_ramo"] = obras_pdf["desc_ramo"].fillna("Sin clasificar")
    obras_pdf["_name"] = (
        obras_pdf["nombre_proyecto"].fillna("(sin nombre)").str.slice(0, 90)
    )
    obras_pdf["_size"] = obras_pdf["monto_ejercido"].apply(
        lambda v: max(math.sqrt(max(v, 0)) / 700, 4)
    )

    def hover(row):
        return (
            f"<b>{row['_name']}</b><br>"
            f"{row['desc_alcaldia']} · {int(row['ciclo'])}<br>"
            f"Ejercido <b>{fmt_mxn(row['monto_ejercido'])}</b><br>"
            f"<span style='color:#9F2241'>{row['desc_ramo']}</span>"
        )

    obras_pdf["_hover"] = obras_pdf.apply(hover, axis=1)
    ramos_present = sorted(obras_pdf["desc_ramo"].unique())
    color_seq = [RAMO_PALETTE.get(r, "#94A3B8") for r in ramos_present]

    fig_obra_map = px.scatter_map(
        obras_pdf,
        lat="latitud",
        lon="longitud",
        color="desc_ramo",
        color_discrete_sequence=color_seq,
        size="_size",
        size_max=25,
        custom_data=["_hover"],
        zoom=9.7,
        center={"lat": 19.38, "lon": -99.15},
        map_style="carto-positron",
        opacity=0.74,
    )
    fig_obra_map.update_traces(hovertemplate="%{customdata[0]}<extra></extra>")
    fig_obra_map.update_layout(
        height=620,
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255,255,255,0.92)",
            bordercolor="#dbe7f3",
            borderwidth=1,
            font=dict(size=11, family=FONT),
            title=dict(text="<b>Ramo federal</b>", font=dict(size=12)),
        ),
        paper_bgcolor="white",
        hoverlabel=dict(
            bgcolor="#0f172a",
            bordercolor="#334155",
            font=dict(family=FONT, size=12, color="#f8fafc"),
        ),
    )
    mo.ui.plotly(fig_obra_map)
    return


@app.cell
def _(FONT, fmt_mxn, go, mo, obra_df, pl, view_selector):
    mo.stop(view_selector.value != "Obra publica")

    top_alcaldias = (
        obra_df.group_by("desc_alcaldia")
        .agg(
            [
                pl.col("monto_ejercido").sum().alias("monto"),
                pl.len().alias("proyectos"),
            ]
        )
        .sort("monto", descending=True)
        .head(12)
        .to_pandas()
        .iloc[::-1]
        .reset_index(drop=True)
    )
    top_alcaldias["desc_alcaldia"] = top_alcaldias["desc_alcaldia"].fillna(
        "Sin alcaldia"
    )
    top_alcaldias["label"] = top_alcaldias["monto"].apply(fmt_mxn)

    fig_obra_alcaldias = go.Figure(
        go.Bar(
            x=top_alcaldias["monto"],
            y=top_alcaldias["desc_alcaldia"],
            orientation="h",
            marker=dict(color="#9F2241"),
            text=top_alcaldias["label"],
            textposition="outside",
            textfont=dict(size=11, color="#334155"),
            hovertemplate="<b>%{y}</b><br>%{text} · %{customdata} proyectos<extra></extra>",
            customdata=top_alcaldias["proyectos"],
            cliponaxis=False,
        )
    )
    fig_obra_alcaldias.update_layout(
        height=420,
        margin=dict(l=10, r=60, t=20, b=20),
        xaxis=dict(showgrid=True, gridcolor="#EDF2F7", tickformat=".2s", title=""),
        yaxis=dict(title="", tickfont=dict(size=12)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, size=12, color="#1E293B"),
        hoverlabel=dict(
            bgcolor="#0f172a",
            bordercolor="#334155",
            font=dict(family=FONT, size=12, color="#f8fafc"),
        ),
    )
    fig_obra_alcaldias
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ---
        <div style="text-align:center;color:#64748B;font-size:12px;padding:12px 0 30px;">
        Fuentes: Portal de Datos Abiertos CDMX · Presupuesto de egresos + Rally Como van las obras
        <br>
        Producto unico construido como una sola experiencia con dos vistas complementarias.
        </div>
        """
    )
    return


if __name__ == "__main__":
    app.run()
