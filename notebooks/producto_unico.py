import marimo

__generated_with = "0.23.1"
app = marimo.App(
    width="full",
    app_title="Impact Lab CDMX · Producto Unico",
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
            --text-muted: #57657a;
            --surface-card: linear-gradient(170deg, #ffffff 0%, #f8fbff 100%);
            --surface-soft: #f8fafc;
            --border-soft: #dbe7f3;
            --radius-lg: 14px;
            --radius-xl: 20px;
            --shadow-card: 0 10px 22px rgba(15, 23, 42, 0.08);
            --shadow-hero: 0 24px 56px rgba(13, 23, 39, 0.34);
            --brand-budget: #2f6690;
            --brand-obra: #9f2241;
            --brand-accent: #f4a259;
        }
        .hero {
            font-family: var(--font-display);
            padding: 40px 44px 34px;
            background:
                radial-gradient(1200px 260px at 10% -10%, rgba(244, 162, 89, 0.25), transparent 60%),
                radial-gradient(1000px 220px at 90% -20%, rgba(58, 124, 165, 0.26), transparent 60%),
                linear-gradient(125deg, #132337 0%, #1d3350 45%, #40223d 100%);
            color: #f8fafc;
            border-radius: var(--radius-xl);
            border: 1px solid rgba(255, 255, 255, 0.14);
            box-shadow: var(--shadow-hero);
            margin-bottom: 12px;
            position: relative;
            overflow: hidden;
        }
        .hero:after {
            content: '';
            position: absolute;
            inset: 0;
            background-image: linear-gradient(rgba(255,255,255,0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.08) 1px, transparent 1px);
            background-size: 28px 28px;
            opacity: 0.2;
            pointer-events: none;
        }
        .hero * {
            position: relative;
            z-index: 1;
        }
        .note {
            margin: 10px 0 20px;
            padding: 14px 18px;
            background: linear-gradient(120deg, #fff9e8 0%, #fff3d5 100%);
            border: 1px solid #f3d58c;
            border-left: 5px solid #d97706;
            border-radius: 12px;
            color: #7c3b07;
            font-family: var(--font-body);
            font-size: 13px;
            line-height: 1.55;
            box-shadow: 0 8px 18px rgba(217, 119, 6, 0.08);
        }
        .card {
            background: var(--surface-card);
            border: 1px solid var(--border-soft);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-card);
            padding: 14px 16px;
            transition: transform 200ms ease, box-shadow 200ms ease;
        }
        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 14px 28px rgba(15, 23, 42, 0.12);
        }
        .chip {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 999px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.6px;
            text-transform: uppercase;
        }
        .chip-budget {
            background: rgba(47, 102, 144, 0.15);
            color: var(--brand-budget);
        }
        .chip-obra {
            background: rgba(159, 34, 65, 0.12);
            color: var(--brand-obra);
        }
        @media (prefers-reduced-motion: reduce) {
            .card {
                transition: none;
            }
            .card:hover {
                transform: none;
                box-shadow: var(--shadow-card);
            }
        }
        </style>

        <div class="hero">
            <div style="font-size: 12px; letter-spacing: 2.8px; opacity: 0.88; text-transform: uppercase; font-weight: 700; color:#ffd8a1;">
                Ciudad de Mexico · Impact Lab · Entregable Unico
            </div>
            <div style="font-size: 40px; font-weight: 800; margin-top: 8px; letter-spacing: -0.9px; line-height:1.12; max-width: 920px;">
                Del presupuesto en papel a la obra en territorio
            </div>
            <div style="font-family:'IBM Plex Sans', sans-serif; font-size: 15px; margin-top: 12px; max-width: 860px; line-height: 1.65; color:#deecff;">
                Un solo producto para contar la historia completa: priorizacion presupuestal, ejecucion institucional
                y evidencia georreferenciada de proyectos federales en la CDMX.
            </div>
        </div>

        <div class="note">
            <b>Comparabilidad temporal:</b> el eje principal usa cortes 2018-2019 para conectar presupuesto y obra.
            Se mantiene referencia 2023-2024 para contexto reciente.
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

    PALETTE = [
        "#23395B",
        "#2F6690",
        "#3A7CA5",
        "#00A7A0",
        "#F4A259",
        "#C94C4C",
        "#6D597A",
        "#2A9D8F",
    ]

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
                bgcolor="rgba(255,255,255,0.74)",
                bordercolor="#dbe7f3",
                borderwidth=1,
            ),
        )
        return fig

    return (
        DATA_DIR,
        FONT,
        PALETTE,
        RAMO_PALETTE,
        fmt_int,
        fmt_mxn,
        go,
        mo,
        pl,
        px,
        style_fig,
    )


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
        "2018 · aprobado": DATA_DIR / "egresos_2018_aprobado.csv",
        "2018 · cuenta publica": DATA_DIR / "egresos_2018_cp.csv",
        "2019 · aprobado": DATA_DIR / "egresos_2019_aprobado.csv",
        "2019 Q1 · avance trimestral": DATA_DIR / "egresos_2019_01_trimestre.csv",
        "2019 Q2 · avance trimestral": DATA_DIR / "egresos_2019_02_trimestre.csv",
        "2019 Q3 · avance trimestral": DATA_DIR / "egresos_2019_03_trimestre.csv",
        "2023 Q3 · avance trimestral": DATA_DIR / "egresos_2023_03_trimestre.csv",
        "2024 · aprobado": DATA_DIR / "egresos_2024_aprobado.csv",
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
def _(budget_datasets, mo, raw_obras):
    year_picker = mo.ui.dropdown(
        options=list(budget_datasets.keys()),
        value=list(budget_datasets.keys())[0],
        label="Corte presupuestal",
    )

    alcaldias = sorted(raw_obras["desc_alcaldia"].drop_nulls().unique().to_list())
    alcaldia_filter = mo.ui.multiselect(
        options=alcaldias,
        value=[],
        label="Alcaldia (obra)",
    )

    ciclos = sorted(raw_obras["ciclo"].drop_nulls().unique().to_list())
    ciclo_filter = mo.ui.range_slider(
        start=min(ciclos),
        stop=max(ciclos),
        value=(min(ciclos), max(ciclos)),
        step=1,
        label="Anos (obra)",
        show_value=True,
        full_width=False,
    )

    mo.md(
        """
        <div class="card" style="margin: 8px 0 14px;">
            <div style="font-family: var(--font-body); font-size:11px; color: var(--text-muted); letter-spacing:1px; text-transform:uppercase; margin-bottom:8px; font-weight:700;">
                Controles del producto integrado
            </div>
        </div>
        """
    )
    mo.hstack(
        [year_picker, alcaldia_filter, ciclo_filter],
        justify="start",
        gap=1.2,
        wrap=True,
    )
    return alcaldia_filter, ciclo_filter, year_picker


@app.cell
def _(budget_datasets, pl, year_picker):
    budget_df = budget_datasets[year_picker.value]

    mod_sum = budget_df["monto_modificado"].fill_null(0).sum()
    spent_sum = budget_df["monto_ejercido"].fill_null(0).sum()
    if mod_sum > 0:
        budget_col, budget_label = "monto_modificado", "Modificado"
    else:
        budget_col, budget_label = "monto_aprobado", "Aprobado"

    has_spent = spent_sum > 0

    budget_df = budget_df.with_columns(
        [
            pl.col(budget_col).fill_null(0).alias("_budget"),
            pl.col("monto_ejercido").fill_null(0).alias("_spent"),
        ]
    )
    budget_df = budget_df.with_columns(
        pl.max_horizontal([pl.col("_budget"), pl.col("_spent")]).alias("_amount")
    ).filter(pl.col("_amount") > 0)
    return budget_col, budget_df, budget_label, has_spent


@app.cell
def _(alcaldia_filter, ciclo_filter, pl, raw_obras):
    obra_df = raw_obras.filter(pl.col("ciclo").is_between(*ciclo_filter.value))
    if alcaldia_filter.value:
        obra_df = obra_df.filter(pl.col("desc_alcaldia").is_in(alcaldia_filter.value))
    return (obra_df,)


@app.cell(hide_code=True)
def _(budget_df, budget_label, fmt_int, fmt_mxn, has_spent, mo, obra_df, pl):
    budget_total = budget_df["_budget"].sum()
    spent_total = budget_df["_spent"].sum()
    exec_rate = (
        (spent_total / budget_total * 100) if has_spent and budget_total > 0 else None
    )

    obras_total = obra_df.height
    obras_monto = obra_df["monto_ejercido"].sum()
    obras_done = obra_df.filter(pl.col("avance_fisico") >= 95).height
    obras_done_rate = (obras_done / obras_total * 100) if obras_total else 0

    def kpi(label, value, chip):
        return f"""
        <div class="card" style="flex:1;min-width:220px;">
            <div class="chip {chip}">{label}</div>
            <div style="font-size:30px;font-weight:800;color:var(--text-strong);margin-top:8px;letter-spacing:-0.7px;line-height:1.1;">{value}</div>
        </div>
        """

    mo.md(
        f"""
        ## Acto 1 · Panorama integrado

        <div style="display:flex;gap:14px;flex-wrap:wrap;margin:12px 0 22px;">
            {kpi(f"Presupuesto {budget_label.lower()}", fmt_mxn(budget_total), "chip-budget")}
            {kpi("Ejecucion presupuestal", f"{exec_rate:.1f}%" if exec_rate is not None else "No disponible", "chip-budget")}
            {kpi("Proyectos de obra", fmt_int(obras_total), "chip-obra")}
            {kpi("Inversion en obra", fmt_mxn(obras_monto), "chip-obra")}
            {kpi("Obras terminadas", f"{obras_done_rate:.1f}%", "chip-obra")}
        </div>
        """
    )
    return


@app.cell(hide_code=True)
def _(budget_label, has_spent, mo):
    _copy = (
        f"Top funciones por presupuesto <b>{budget_label.lower()}</b> y comparacion contra lo ejercido."
        if has_spent
        else f"Top funciones por presupuesto <b>{budget_label.lower()}</b>. Este corte no incluye ejercicio reportado."
    )
    mo.md(
        f"""
        ## Acto 2 · Presupuesto

        <div class="card" style="margin: 6px 0 12px; font-family: var(--font-body); font-size: 13px; color: var(--text-muted); line-height: 1.55;">
            {_copy}
        </div>
        """
    )
    return


@app.cell
def _(budget_df, fmt_mxn, go, has_spent, pl, style_fig):
    top = (
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

    _fig_budget = go.Figure()
    _fig_budget.add_trace(
        go.Bar(
            y=top["desc_funcion"],
            x=top["budget"],
            orientation="h",
            marker=dict(color="#E2E8F0"),
            name="Presupuesto",
            hovertemplate="<b>%{y}</b><br>Presupuesto: %{customdata}<extra></extra>",
            customdata=[fmt_mxn(v) for v in top["budget"]],
        )
    )

    if has_spent:
        _fig_budget.add_trace(
            go.Bar(
                y=top["desc_funcion"],
                x=top["spent"],
                orientation="h",
                marker=dict(color="#9F2241"),
                name="Ejercido",
                hovertemplate="<b>%{y}</b><br>Ejercido: %{customdata}<extra></extra>",
                customdata=[fmt_mxn(v) for v in top["spent"]],
            )
        )

    _fig_budget.update_layout(
        barmode="overlay",
        bargap=0.35,
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9", tickformat=".2s", title=""),
        yaxis=dict(title="", tickfont=dict(size=12), automargin=True),
        legend=dict(orientation="h", y=1.02, x=0),
    )
    style_fig(_fig_budget, height=560)
    _fig_budget
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## Acto 3 · Territorio

        <div class="card" style="margin: 6px 0 12px; font-family: var(--font-body); font-size: 13px; color: var(--text-muted); line-height: 1.55;">
            El mapa conecta la evidencia territorial con la historia presupuestal: cada punto es un proyecto federal georreferenciado.
        </div>
        """
    )
    return


@app.cell
def _(RAMO_PALETTE, FONT, fmt_mxn, mo, obra_df, px):
    import math

    pdf = (
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

    pdf["desc_ramo"] = pdf["desc_ramo"].fillna("Sin clasificar")
    pdf["_name"] = pdf["nombre_proyecto"].fillna("(sin nombre)").str.slice(0, 90)
    pdf["_size"] = pdf["monto_ejercido"].apply(
        lambda v: max(math.sqrt(max(v, 0)) / 700, 4)
    )

    def hover(row):
        return (
            f"<b>{row['_name']}</b><br>"
            f"{row['desc_alcaldia']} · {int(row['ciclo'])}<br>"
            f"Ejercido <b>{fmt_mxn(row['monto_ejercido'])}</b><br>"
            f"<span style='color:#9F2241'>{row['desc_ramo']}</span>"
        )

    pdf["_h"] = pdf.apply(hover, axis=1)

    ramos_present = sorted(pdf["desc_ramo"].unique())
    color_seq = [RAMO_PALETTE.get(r, "#94A3B8") for r in ramos_present]

    _fig_map = px.scatter_map(
        pdf,
        lat="latitud",
        lon="longitud",
        color="desc_ramo",
        color_discrete_sequence=color_seq,
        size="_size",
        size_max=25,
        custom_data=["_h"],
        zoom=9.7,
        center={"lat": 19.38, "lon": -99.15},
        map_style="carto-positron",
        opacity=0.74,
    )
    _fig_map.update_traces(hovertemplate="%{customdata[0]}<extra></extra>")
    _fig_map.update_layout(
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
            itemsizing="constant",
        ),
        paper_bgcolor="white",
        hoverlabel=dict(
            bgcolor="#0f172a",
            bordercolor="#334155",
            font=dict(family=FONT, size=12, color="#f8fafc"),
        ),
    )
    mo.ui.plotly(_fig_map)
    return


@app.cell
def _(FONT, fmt_mxn, go, obra_df, pl):
    alc = (
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
    alc["desc_alcaldia"] = alc["desc_alcaldia"].fillna("Sin alcaldia")
    alc["label"] = alc["monto"].apply(fmt_mxn)

    _fig_alcaldia = go.Figure(
        go.Bar(
            x=alc["monto"],
            y=alc["desc_alcaldia"],
            orientation="h",
            marker=dict(color="#2F6690"),
            text=alc["label"],
            textposition="outside",
            textfont=dict(size=11, color="#334155"),
            hovertemplate="<b>%{y}</b><br>%{text} · %{customdata} proyectos<extra></extra>",
            customdata=alc["proyectos"],
            cliponaxis=False,
        )
    )
    _fig_alcaldia.update_layout(
        height=420,
        margin=dict(l=10, r=60, t=20, b=20),
        xaxis=dict(showgrid=True, gridcolor="#e8eff7", tickformat=".2s", title=""),
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
    _fig_alcaldia
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ---
        <div style="text-align:center;color:#64748B;font-size:12px;padding:12px 0 30px;">
        Fuentes: Portal de Datos Abiertos CDMX · Presupuesto de egresos + Rally Como van las obras
        <br>
        Producto unico construido con Marimo + Plotly · Impact Lab CDMX 2026
        </div>
        """
    )
    return


if __name__ == "__main__":
    app.run()
