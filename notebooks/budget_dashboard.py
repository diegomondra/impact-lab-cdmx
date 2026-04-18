import marimo

__generated_with = "0.23.1"
app = marimo.App(
    width="full",
    app_title="Presupuesto CDMX · ¿A dónde va el dinero?",
    css_file="",
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        <div style="
            padding: 36px 40px 28px;
            background: linear-gradient(135deg, #9F2241 0%, #691C32 100%);
            color: white;
            border-radius: 14px;
            margin-bottom: 8px;
            box-shadow: 0 8px 24px rgba(159, 34, 65, 0.25);
        ">
        <div style="font-size: 13px; letter-spacing: 3px; opacity: 0.85; text-transform: uppercase; font-weight: 600;">
            Ciudad de México · Presupuesto de Egresos
        </div>
        <div style="font-size: 38px; font-weight: 700; margin-top: 6px; letter-spacing: -0.5px;">
            ¿A dónde va el dinero público?
        </div>
        <div style="font-size: 15px; margin-top: 10px; opacity: 0.9; max-width: 780px; line-height: 1.55;">
            Explora cómo se asigna cada peso del presupuesto de la CDMX. Datos oficiales del
            <a href="https://datos.cdmx.gob.mx" style="color:#FFCCD5; text-decoration: underline;">Portal de Datos Abiertos</a>.
        </div>
        </div>
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

    PALETTE = [
        "#9F2241", "#E3007E", "#EC6730", "#00A489", "#00B7CD",
        "#6C4A7E", "#D6A461", "#3D5A80", "#C14953", "#2A9D8F",
    ]

    FONT = "Inter, -apple-system, system-ui, sans-serif"

    def fmt_mxn(v, short=True):
        if v is None:
            return "—"
        v = float(v)
        sign = "-" if v < 0 else ""
        v = abs(v)
        if short:
            if v >= 1e9:
                return f"{sign}${v/1e9:,.2f} mmdp"
            if v >= 1e6:
                return f"{sign}${v/1e6:,.1f} mdp"
            if v >= 1e3:
                return f"{sign}${v/1e3:,.1f} k"
            return f"{sign}${v:,.0f}"
        return f"{sign}${v:,.0f}"

    def style_fig(fig, height=480, title=None):
        fig.update_layout(
            font=dict(family=FONT, size=13, color="#1E293B"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=50 if title else 20, b=20),
            height=height,
            hoverlabel=dict(
                bgcolor="white",
                bordercolor="#E2E8F0",
                font=dict(family=FONT, size=12, color="#1E293B"),
            ),
            title=dict(
                text=title,
                font=dict(size=16, color="#0F172A", family=FONT),
                x=0.01, xanchor="left",
            ) if title else None,
        )
        return fig

    return DATA_DIR, FONT, PALETTE, fmt_mxn, go, mo, pl, px, style_fig


@app.cell
def _(DATA_DIR, pl):
    def load(path):
        return pl.read_csv(
            path,
            infer_schema_length=10_000,
            null_values=["NA", ""],
            truncate_ragged_lines=True,
            schema_overrides={"monto_aprobado": pl.Float64, "monto_modificado": pl.Float64, "monto_ejercido": pl.Float64},
        )

    files = {
        "2024 (aprobado)": DATA_DIR / "egresos_2024_aprobado.csv",
        "2023 (aprobado)": DATA_DIR / "egresos_2023_aprobado.csv",
        "2023 Q3 (ejercido)": DATA_DIR / "egresos_2023_03_trimestre.csv",
    }
    files = {k: v for k, v in files.items() if v.exists()}
    datasets = {k: load(v) for k, v in files.items()}
    return (datasets,)


@app.cell(hide_code=True)
def _(datasets, mo):
    year_picker = mo.ui.dropdown(
        options=list(datasets.keys()),
        value=list(datasets.keys())[0],
        label="Año / corte",
    )
    mo.hstack([year_picker], justify="start")
    return (year_picker,)


@app.cell
def _(datasets, pl, year_picker):
    df = datasets[year_picker.value]
    amount_col = "monto_ejercido" if "ejercido" in year_picker.value else "monto_aprobado"
    df = df.with_columns(pl.col(amount_col).fill_null(0).alias("_amount"))
    df = df.filter(pl.col("_amount") > 0)
    return amount_col, df


@app.cell(hide_code=True)
def _(amount_col, df, fmt_mxn, mo):
    _total = df["_amount"].sum()
    _n_programs = df["desc_programa_presupuestario"].n_unique()
    _n_agencies = df["desc_unidad_responsable"].n_unique()
    _n_records = df.height

    _has_ejercido = "monto_ejercido" in df.columns and df["monto_ejercido"].sum() > 0
    _exec_rate = None
    if _has_ejercido and amount_col == "monto_ejercido":
        _aprobado_total = df["monto_aprobado"].fill_null(0).sum()
        if _aprobado_total > 0:
            _exec_rate = float(df["monto_ejercido"].fill_null(0).sum()) / float(_aprobado_total) * 100

    def _kpi(label, value, accent="#9F2241", sub=None):
        _sub_html = f'<div style="font-size:11px;color:#64748B;margin-top:4px;letter-spacing:0.5px;text-transform:uppercase;">{sub}</div>' if sub else ""
        return f"""
        <div style="
            background: white;
            border: 1px solid #E2E8F0;
            border-left: 4px solid {accent};
            border-radius: 10px;
            padding: 20px 22px;
            flex: 1;
            min-width: 200px;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        ">
            <div style="font-size:11px;color:#64748B;letter-spacing:1.5px;text-transform:uppercase;font-weight:600;">{label}</div>
            <div style="font-size:28px;font-weight:700;color:#0F172A;margin-top:8px;letter-spacing:-0.5px;">{value}</div>
            {_sub_html}
        </div>
        """

    _cards = [
        _kpi("Presupuesto total", fmt_mxn(_total), "#9F2241"),
        _kpi("Unidades responsables", f"{_n_agencies:,}", "#00A489"),
        _kpi("Programas presupuestarios", f"{_n_programs:,}", "#00B7CD"),
        _kpi("Partidas registradas", f"{_n_records:,}", "#EC6730"),
    ]
    if _exec_rate is not None:
        _cards.append(_kpi("Tasa de ejecución", f"{_exec_rate:.1f}%", "#6C4A7E", sub="ejercido / aprobado"))

    mo.md(f'<div style="display:flex;gap:14px;flex-wrap:wrap;margin:16px 0 24px;">{"".join(_cards)}</div>')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## Cómo se reparte el gasto

        Jerarquía: **Finalidad → Función → Subfunción**. El tamaño de cada bloque representa el monto asignado.
        Haz clic para explorar en profundidad.
        """
    )
    return


@app.cell
def _(PALETTE, df, fmt_mxn, pl, px, style_fig):
    tree_df = (
        df.group_by(["desc_finalidad", "desc_funcion", "desc_subfuncion"])
        .agg(pl.col("_amount").sum())
        .filter(pl.col("_amount") > 0)
        .sort("_amount", descending=True)
        .to_pandas()
    )
    tree_df = tree_df.fillna({"desc_finalidad": "Sin clasificar", "desc_funcion": "Sin clasificar", "desc_subfuncion": "Sin clasificar"})

    _fig = px.sunburst(
        tree_df,
        path=["desc_finalidad", "desc_funcion", "desc_subfuncion"],
        values="_amount",
        color="desc_finalidad",
        color_discrete_sequence=PALETTE,
        branchvalues="total",
    )
    _fig.update_traces(
        hovertemplate="<b>%{label}</b><br>%{customdata}<br>%{percentParent:.1%} del padre<extra></extra>",
        customdata=[fmt_mxn(v) for v in tree_df["_amount"]],
        insidetextorientation="radial",
    )
    style_fig(_fig, height=620)
    _fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("## Top unidades responsables")
    return


@app.cell
def _(df, fmt_mxn, pl, px, style_fig):
    _top_n = 15
    _top_agencies = (
        df.group_by("desc_unidad_responsable")
        .agg(pl.col("_amount").sum())
        .sort("_amount", descending=True)
        .head(_top_n)
        .to_pandas()
    )
    _total = df["_amount"].sum()
    _top_agencies["pct"] = _top_agencies["_amount"] / _total * 100
    _top_agencies["label"] = _top_agencies["_amount"].apply(fmt_mxn)

    _fig = px.bar(
        _top_agencies.sort_values("_amount"),
        x="_amount",
        y="desc_unidad_responsable",
        orientation="h",
        text="label",
        color="_amount",
        color_continuous_scale=[[0, "#F8BBD0"], [1, "#9F2241"]],
    )
    _fig.update_traces(
        textposition="outside",
        textfont=dict(size=12, color="#334155"),
        hovertemplate="<b>%{y}</b><br>%{text}<extra></extra>",
        cliponaxis=False,
    )
    _fig.update_layout(
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9", title="", tickformat=".2s"),
        yaxis=dict(title="", tickfont=dict(size=12)),
        coloraxis_showscale=False,
    )
    style_fig(_fig, height=560)
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## Alineación con los Objetivos de Desarrollo Sostenible

        Cuánto presupuesto se asigna a cada ODS de la Agenda 2030.
        """
    )
    return


@app.cell
def _(df, fmt_mxn, pl, px, style_fig):
    sdg_colors = {
        1: "#E5243B", 2: "#DDA63A", 3: "#4C9F38", 4: "#C5192D", 5: "#FF3A21",
        6: "#26BDE2", 7: "#FCC30B", 8: "#A21942", 9: "#FD6925", 10: "#DD1367",
        11: "#FD9D24", 12: "#BF8B2E", 13: "#3F7E44", 14: "#0A97D9", 15: "#56C02B",
        16: "#00689D", 17: "#19486A",
    }

    sdg = (
        df.group_by(["objetivo_desarrollo_sostenible", "desc_objetivo_desarrollo_sostenible"])
        .agg(pl.col("_amount").sum())
        .filter(pl.col("_amount") > 0)
        .sort("_amount", descending=True)
        .to_pandas()
    )
    sdg["label"] = sdg["_amount"].apply(fmt_mxn)
    sdg["color"] = sdg["objetivo_desarrollo_sostenible"].map(sdg_colors).fillna("#94A3B8")
    sdg["name"] = sdg.apply(
        lambda r: f"ODS {int(r['objetivo_desarrollo_sostenible'])}: {r['desc_objetivo_desarrollo_sostenible']}"
        if r["desc_objetivo_desarrollo_sostenible"] else "Sin ODS asignado",
        axis=1,
    )

    _fig = px.bar(
        sdg.sort_values("_amount"),
        x="_amount",
        y="name",
        orientation="h",
        text="label",
        color="name",
        color_discrete_sequence=sdg["color"].tolist()[::-1],
    )
    _fig.update_traces(
        textposition="outside",
        textfont=dict(size=11, color="#334155"),
        hovertemplate="<b>%{y}</b><br>%{text}<extra></extra>",
        cliponaxis=False,
    )
    _fig.update_layout(
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9", title="", tickformat=".2s"),
        yaxis=dict(title=""),
        showlegend=False,
    )
    style_fig(_fig, height=max(420, 40 * len(sdg)))
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## Clasificación económica del gasto

        ¿En qué se gasta? Sueldos, obra pública, transferencias, materiales. (Capítulos del gasto)
        """
    )
    return


@app.cell
def _(PALETTE, df, fmt_mxn, go, pl, style_fig):
    cap = (
        df.group_by("desc_capitulo")
        .agg(pl.col("_amount").sum())
        .filter(pl.col("_amount") > 0)
        .sort("_amount", descending=True)
        .to_pandas()
    )
    cap["label"] = cap["_amount"].apply(fmt_mxn)

    _fig = go.Figure(
        go.Pie(
            labels=cap["desc_capitulo"],
            values=cap["_amount"],
            hole=0.55,
            marker=dict(colors=PALETTE[: len(cap)], line=dict(color="white", width=2)),
            textinfo="percent",
            textfont=dict(size=13, color="white", family="Inter"),
            hovertemplate="<b>%{label}</b><br>%{customdata}<br>%{percent}<extra></extra>",
            customdata=cap["label"],
            sort=False,
        )
    )
    _fig.update_layout(
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02,
            font=dict(size=12),
        ),
        annotations=[
            dict(
                text=f"<b style='font-size:22px;color:#0F172A'>{fmt_mxn(cap['_amount'].sum())}</b><br><span style='font-size:11px;color:#64748B;letter-spacing:1px'>TOTAL</span>",
                x=0.5, y=0.5, showarrow=False, align="center",
            )
        ],
    )
    style_fig(_fig, height=480)
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## Busca un programa o dependencia

        Escribe parte del nombre — por ejemplo, *"seguridad"*, *"metro"*, *"salud"*, *"educación"*.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    search = mo.ui.text(
        placeholder="Buscar unidad responsable, programa o partida...",
        full_width=True,
    )
    search
    return (search,)


@app.cell
def _(df, fmt_mxn, mo, pl, search):
    q = (search.value or "").strip().lower()
    mo.stop(len(q) < 2, mo.md("*Escribe al menos 2 caracteres...*"))

    mask = (
        pl.col("desc_unidad_responsable").str.to_lowercase().str.contains(q, literal=True)
        | pl.col("desc_programa_presupuestario").str.to_lowercase().str.contains(q, literal=True)
        | pl.col("desc_funcion").str.to_lowercase().str.contains(q, literal=True)
        | pl.col("desc_partida_especifica").str.to_lowercase().str.contains(q, literal=True)
    )
    matches = df.filter(mask)
    mo.md(f"**{matches.height:,} coincidencias** · total: **{fmt_mxn(matches['_amount'].sum())}**")
    return (matches,)


@app.cell(hide_code=True)
def _(fmt_mxn, matches, mo, pl):
    display = (
        matches.group_by(["desc_unidad_responsable", "desc_programa_presupuestario"])
        .agg(pl.col("_amount").sum())
        .sort("_amount", descending=True)
        .head(50)
        .with_columns(pl.col("_amount").map_elements(fmt_mxn, return_dtype=pl.Utf8).alias("Monto"))
        .rename({"desc_unidad_responsable": "Unidad", "desc_programa_presupuestario": "Programa"})
        .select(["Unidad", "Programa", "Monto"])
        .to_pandas()
    )
    mo.ui.table(display, selection=None, page_size=15)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ---

        <div style="text-align:center;color:#64748B;font-size:12px;padding:16px 0 32px;">
        Fuente: <a href="https://datos.cdmx.gob.mx" style="color:#9F2241;">Portal de Datos Abiertos de la Ciudad de México</a>
        · Construido con Marimo + Plotly · Claude Mexico City Lab 2026
        </div>
        """
    )
    return


if __name__ == "__main__":
    app.run()
