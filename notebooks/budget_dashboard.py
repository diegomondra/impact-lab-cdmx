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
        "2023 Q3 · avance trimestral": DATA_DIR / "egresos_2023_03_trimestre.csv",
        "2024 · aprobado": DATA_DIR / "egresos_2024_aprobado.csv",
        "2023 · aprobado": DATA_DIR / "egresos_2023_aprobado.csv",
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

    _mod_sum = df["monto_modificado"].fill_null(0).sum()
    _apr_sum = df["monto_aprobado"].fill_null(0).sum()
    _ejr_sum = df["monto_ejercido"].fill_null(0).sum()

    if _mod_sum > 0:
        budget_col, budget_label = "monto_modificado", "Modificado"
    else:
        budget_col, budget_label = "monto_aprobado", "Aprobado"

    has_spent = _ejr_sum > 0

    df = df.with_columns([
        pl.col(budget_col).fill_null(0).alias("_budget"),
        pl.col("monto_ejercido").fill_null(0).alias("_spent"),
    ])
    df = df.with_columns(
        pl.max_horizontal([pl.col("_budget"), pl.col("_spent")]).alias("_amount")
    )
    df = df.filter(pl.col("_amount") > 0)
    amount_col = budget_col
    return amount_col, budget_label, df, has_spent


@app.cell(hide_code=True)
def _(budget_label, df, fmt_mxn, has_spent, mo):
    _budget_total = df["_budget"].sum()
    _spent_total = df["_spent"].sum()
    _n_programs = df["desc_programa_presupuestario"].n_unique()
    _n_agencies = df["desc_unidad_responsable"].n_unique()

    _exec_rate = (_spent_total / _budget_total * 100) if has_spent and _budget_total > 0 else None

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
        _kpi(f"Presupuesto {budget_label.lower()}", fmt_mxn(_budget_total), "#9F2241"),
    ]
    if has_spent:
        _cards.append(_kpi("Ejercido a la fecha", fmt_mxn(_spent_total), "#00A489"))
        _cards.append(_kpi("Tasa de ejecución", f"{_exec_rate:.1f}%", "#6C4A7E", sub=f"ejercido / {budget_label.lower()}"))
    _cards.append(_kpi("Unidades responsables", f"{_n_agencies:,}", "#00B7CD"))
    _cards.append(_kpi("Programas presupuestarios", f"{_n_programs:,}", "#EC6730"))

    mo.md(f'<div style="display:flex;gap:14px;flex-wrap:wrap;margin:16px 0 24px;">{"".join(_cards)}</div>')
    return


@app.cell(hide_code=True)
def _(budget_label, has_spent, mo):
    _subtitle = (
        f"Cada barra muestra el **presupuesto {budget_label.lower()}** (gris) vs lo **ejercido** (guinda). "
        "La etiqueta indica el porcentaje ejecutado. Color: verde > 85%, ámbar 60–85%, rojo < 60%."
        if has_spent
        else f"Top funciones por presupuesto {budget_label.lower()}. Selecciona un corte trimestral para ver la ejecución real."
    )
    mo.md(
        f"""
        ## Presupuesto vs. Ejercido — por función

        {_subtitle}
        """
    )
    return


@app.cell
def _(df, fmt_mxn, go, has_spent, pl, style_fig):
    _top = (
        df.with_columns(pl.col("desc_funcion").fill_null("Sin clasificar"))
        .group_by("desc_funcion")
        .agg([
            pl.col("_budget").sum().alias("budget"),
            pl.col("_spent").sum().alias("spent"),
        ])
        .sort("budget", descending=True)
        .head(15)
        .to_pandas()
        .iloc[::-1]
        .reset_index(drop=True)
    )
    _top["exec_pct"] = (_top["spent"] / _top["budget"].where(_top["budget"] > 0, 1) * 100).fillna(0)

    def _exec_color(pct):
        if pct >= 85:
            return "#059669"
        if pct >= 60:
            return "#D97706"
        return "#DC2626"

    _fig = go.Figure()

    _fig.add_trace(go.Bar(
        y=_top["desc_funcion"], x=_top["budget"], orientation="h",
        marker=dict(color="#E2E8F0"), width=0.78,
        name="Presupuesto",
        hovertemplate="<b>%{y}</b><br>Presupuesto: %{customdata}<extra></extra>",
        customdata=[fmt_mxn(v) for v in _top["budget"]],
    ))

    if has_spent:
        _fig.add_trace(go.Bar(
            y=_top["desc_funcion"], x=_top["spent"], orientation="h",
            marker=dict(color=[_exec_color(p) for p in _top["exec_pct"]]),
            width=0.42,
            name="Ejercido",
            hovertemplate="<b>%{y}</b><br>Ejercido: %{customdata}<extra></extra>",
            customdata=[fmt_mxn(v) for v in _top["spent"]],
        ))

        _fig.add_trace(go.Scatter(
            y=_top["desc_funcion"],
            x=_top["budget"],
            mode="text",
            text=[f"  {p:.0f}%" for p in _top["exec_pct"]],
            textposition="middle right",
            textfont=dict(size=12, family="Inter",
                          color=[_exec_color(p) for p in _top["exec_pct"]]),
            showlegend=False,
            hoverinfo="skip",
            cliponaxis=False,
        ))

    _max_x = float(_top["budget"].max())
    _fig.update_layout(
        barmode="overlay",
        bargap=0.35,
        xaxis=dict(
            showgrid=True, gridcolor="#F1F5F9",
            tickformat=".2s", title="",
            range=[0, _max_x * 1.12],
        ),
        yaxis=dict(title="", tickfont=dict(size=12), automargin=True),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, xanchor="left",
                    bgcolor="rgba(0,0,0,0)"),
    )
    style_fig(_fig, height=620)
    _fig.update_layout(margin=dict(l=10, r=40, t=40, b=20))
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
