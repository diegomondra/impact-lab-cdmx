import marimo

__generated_with = "0.23.1"
app = marimo.App(
    width="full",
    app_title="Las fugas · ¿dónde se perdió el dinero público?",
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        <div style="
            padding: 36px 40px 28px;
            background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
            color: white;
            border-radius: 14px;
            margin-bottom: 8px;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.3);
            border-left: 5px solid #DC2626;
        ">
        <div style="font-size: 13px; letter-spacing: 3px; opacity: 0.75; text-transform: uppercase; font-weight: 600; color:#FCA5A5;">
            Auditoría ciudadana · recursos federales en CDMX
        </div>
        <div style="font-size: 38px; font-weight: 700; margin-top: 6px; letter-spacing: -0.5px;">
            Las fugas.
        </div>
        <div style="font-size: 18px; margin-top: 6px; opacity: 0.85; font-weight: 400;">
            El mapa te muestra qué se construyó. Esto te muestra dónde se perdió el dinero.
        </div>
        <div style="font-size: 14px; margin-top: 16px; opacity: 0.75; max-width: 820px; line-height: 1.6;">
            Usando los mismos datos públicos (23,410 proyectos federales 2013–2018),
            este tablero no celebra obras — rastrea tres patrones incómodos: dinero
            ejercido sin obra terminada, concentración de contratistas, y números
            de beneficiarios inverosímiles.
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
    FONT = "Inter, -apple-system, system-ui, sans-serif"

    RED = "#DC2626"
    AMBER = "#D97706"
    SLATE_900 = "#0F172A"
    SLATE_600 = "#475569"
    SLATE_400 = "#94A3B8"
    SLATE_100 = "#F1F5F9"

    def fmt_mxn(v):
        if v is None or (isinstance(v, float) and (v != v)) or v == 0:
            return "—"
        v = float(v)
        if v >= 1e9:
            return f"${v/1e9:,.2f} mmdp"
        if v >= 1e6:
            return f"${v/1e6:,.1f} mdp"
        if v >= 1e3:
            return f"${v/1e3:,.0f} k"
        return f"${v:,.0f}"

    def fmt_int(v):
        if v is None or v == 0:
            return "—"
        return f"{int(v):,}"

    def fmt_pct(v, digits=0):
        if v is None:
            return "—"
        return f"{v:.{digits}f}%"

    return AMBER, DATA_DIR, FONT, RED, SLATE_100, SLATE_400, SLATE_600, SLATE_900, fmt_int, fmt_mxn, fmt_pct, go, mo, pl, px


@app.cell
def _(DATA_DIR, pl):
    raw = pl.read_csv(
        DATA_DIR / "rally_obras.csv",
        infer_schema_length=10_000,
        null_values=["NA", ""],
        truncate_ragged_lines=True,
        ignore_errors=True,
    )
    raw = raw.with_columns([
        pl.col("latitud").cast(pl.Float64, strict=False),
        pl.col("longitud").cast(pl.Float64, strict=False),
        pl.col("monto_aprobado").fill_null(0),
        pl.col("monto_ejercido").fill_null(0),
        pl.col("monto_pagado").fill_null(0),
        pl.col("avance_fisico").fill_null(0),
        pl.col("avance_financiero").fill_null(0),
        pl.col("poblacion_beneficiada").fill_null(0),
    ])
    return (raw,)


@app.cell(hide_code=True)
def _(fmt_mxn, fmt_pct, mo, pl, raw):
    _total_ejer = raw["monto_ejercido"].sum()

    _stalled = raw.filter((pl.col("avance_fisico") < 25) & (pl.col("monto_ejercido") > 100_000))
    _stalled_monto = _stalled["monto_ejercido"].sum()
    _stalled_pct = _stalled_monto / _total_ejer * 100 if _total_ejer else 0

    _no_report = raw.filter(pl.col("contratista") == "La Unidad Responsable no reportó información")
    _no_report_monto = _no_report["monto_ejercido"].sum()
    _disclosed_monto = raw.filter(pl.col("contratista").is_not_null() & (pl.col("contratista") != "La Unidad Responsable no reportó información"))["monto_ejercido"].sum()
    _opacity_pct = _no_report_monto / (_no_report_monto + _disclosed_monto) * 100 if (_no_report_monto + _disclosed_monto) else 0

    _benef_sus = raw.filter(
        (pl.col("poblacion_beneficiada") > 0)
        & (pl.col("monto_ejercido") > 10_000)
        & ((pl.col("monto_ejercido") / pl.col("poblacion_beneficiada")) < 1)
    )
    _benef_sus_n = _benef_sus.height
    _claimed_benef = _benef_sus["poblacion_beneficiada"].sum()

    def _flag(emoji, number, label, caption, tone="#DC2626"):
        return f"""
        <div style="
            background: white;
            border: 1px solid #E2E8F0;
            border-left: 5px solid {tone};
            border-radius: 12px;
            padding: 20px 24px;
            flex: 1;
            min-width: 260px;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        ">
            <div style="font-size:28px;line-height:1;">{emoji}</div>
            <div style="font-size:32px;font-weight:800;color:{tone};margin-top:10px;letter-spacing:-0.5px;line-height:1;">{number}</div>
            <div style="font-size:12px;letter-spacing:1px;color:#0F172A;text-transform:uppercase;font-weight:600;margin-top:8px;">{label}</div>
            <div style="font-size:13px;color:#64748B;margin-top:6px;line-height:1.5;">{caption}</div>
        </div>
        """

    mo.md(f"""
    <div style="display:flex;gap:16px;flex-wrap:wrap;margin:18px 0 28px;">
    {_flag("🕳️", fmt_pct(_opacity_pct, 0), "Dinero sin contratista identificado",
           f"{fmt_mxn(_no_report_monto)} ejercidos a proveedores marcados <em>'no reportó información'</em>. Es {fmt_pct(_opacity_pct, 0)} de todo el dinero con contrato reportado.")}
    {_flag("⏸️", fmt_mxn(_stalled_monto), "Dinero en proyectos rezagados",
           f"{_stalled.height:,} proyectos con avance físico &lt;25% y &gt;$100k ejercidos. Representan {fmt_pct(_stalled_pct, 1)} de todo el gasto federal en CDMX.", tone="#D97706")}
    {_flag("👥", f"{int(_claimed_benef):,}", "Beneficiarios inverosímiles",
           f"{_benef_sus_n} proyectos afirman beneficiar personas por menos de $1 cada una — sumados, más que toda la población de la CDMX.")}
    </div>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### Fuga #1 · El hueco de transparencia

        El campo **`contratista`** está marcado como *"La Unidad Responsable no reportó información"*
        en la mayoría de los proyectos. Cuando una obra se paga sin dejar constancia pública
        de quién cobró, la fiscalización civil se vuelve imposible.
        """
    )
    return


@app.cell
def _(RED, SLATE_400, fmt_mxn, go, pl, raw):
    _split = raw.with_columns(
        pl.when(pl.col("contratista") == "La Unidad Responsable no reportó información")
          .then(pl.lit("No reportó información"))
          .when(pl.col("contratista").is_null())
          .then(pl.lit("Sin dato"))
          .otherwise(pl.lit("Contratista identificado"))
          .alias("transparencia")
    ).group_by("transparencia").agg(
        pl.col("monto_ejercido").sum().alias("monto"),
        pl.len().alias("proyectos"),
    ).sort("monto", descending=True).to_pandas()

    _split["label"] = _split["monto"].apply(fmt_mxn)
    _split["pct"] = _split["monto"] / _split["monto"].sum() * 100
    _split["pct_str"] = _split["pct"].apply(lambda v: f"{v:.1f}%")
    _split["color"] = _split["transparencia"].map({
        "No reportó información": RED,
        "Contratista identificado": "#059669",
        "Sin dato": SLATE_400,
    })

    _fig = go.Figure(
        go.Bar(
            x=_split["monto"], y=_split["transparencia"],
            orientation="h",
            marker=dict(color=_split["color"]),
            text=[f"  {pct}  · {lbl}" for pct, lbl in zip(_split["pct_str"], _split["label"])],
            textposition="outside",
            textfont=dict(size=13, family="Inter", color="#0F172A"),
            hovertemplate="<b>%{y}</b><br>%{customdata[0]} · %{customdata[1]:,} proyectos<extra></extra>",
            customdata=_split[["label", "proyectos"]].values,
            cliponaxis=False,
        )
    )
    _fig.update_layout(
        height=260,
        margin=dict(l=10, r=180, t=10, b=30),
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9", tickformat=".2s", title=""),
        yaxis=dict(title="", tickfont=dict(size=13, color="#0F172A")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif"),
        showlegend=False,
    )
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### Fuga #2 · Dinero ejercido, obra que no avanzó

        Proyectos donde **el dinero salió pero la obra no se terminó**. Ordenados por monto.
        Un avance físico de 0% con millones ejercidos es una luz roja.
        """
    )
    return


@app.cell(hide_code=True)
def _(raw, mo, pl):
    alcaldia_filter = mo.ui.multiselect(
        options=sorted(raw["desc_alcaldia"].drop_nulls().unique().to_list()),
        value=[],
        label="Filtrar por alcaldía",
    )
    ramo_filter = mo.ui.multiselect(
        options=sorted(raw["desc_ramo"].drop_nulls().unique().to_list()),
        value=[],
        label="Filtrar por ramo federal",
    )
    mo.hstack([alcaldia_filter, ramo_filter], justify="start", gap=1.5, wrap=True)
    return alcaldia_filter, ramo_filter


@app.cell
def _(alcaldia_filter, pl, ramo_filter, raw):
    df = raw
    if alcaldia_filter.value:
        df = df.filter(pl.col("desc_alcaldia").is_in(alcaldia_filter.value))
    if ramo_filter.value:
        df = df.filter(pl.col("desc_ramo").is_in(ramo_filter.value))
    return (df,)


@app.cell
def _(df, fmt_int, fmt_mxn, mo, pl):
    _stalled = df.filter(
        (pl.col("avance_fisico") < 25) & (pl.col("monto_ejercido") > 500_000)
    ).sort("monto_ejercido", descending=True).head(30)

    if _stalled.height == 0:
        mo.md("*Sin proyectos rezagados con los filtros actuales.* 🎉")
    else:
        _rows = _stalled.to_pandas()
        _rows["nombre"] = _rows["nombre_proyecto"].fillna("(sin nombre)").str.slice(0, 80)
        _rows["alcaldia"] = _rows["desc_alcaldia"].fillna("—")
        _rows["ramo"] = _rows["desc_ramo"].fillna("—").str.slice(0, 60)
        _rows["ejercido"] = _rows["monto_ejercido"].apply(fmt_mxn)
        _rows["aprobado"] = _rows["monto_aprobado"].apply(fmt_mxn)
        _rows["avance"] = _rows["avance_fisico"].apply(lambda v: f"{v:.0f}%")
        _rows["año"] = _rows["ciclo"].astype(int).astype(str)
        _rows["contratista"] = _rows["contratista"].fillna("—").str.slice(0, 50)

        _display = _rows[["nombre", "alcaldia", "ramo", "año", "aprobado", "ejercido", "avance", "contratista"]].rename(columns={
            "nombre": "Proyecto",
            "alcaldia": "Alcaldía",
            "ramo": "Ramo federal",
            "año": "Año",
            "aprobado": "Aprobado",
            "ejercido": "Ejercido",
            "avance": "Avance físico",
            "contratista": "Contratista",
        })
        mo.ui.table(_display, selection=None, page_size=12, show_column_summaries=False)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### Fuga #3 · Concentración de contratistas

        Excluyendo los proyectos sin contratista reportado, estos son los 15 despachos que
        más dinero federal recibieron en CDMX. **Haz click en una barra para ver sus proyectos.**
        """
    )
    return


@app.cell
def _(RED, SLATE_100, df, fmt_mxn, go, pl):
    _top = (
        df.filter(
            pl.col("contratista").is_not_null()
            & (pl.col("contratista") != "La Unidad Responsable no reportó información")
        )
        .group_by("contratista")
        .agg([
            pl.col("monto_ejercido").sum().alias("monto"),
            pl.len().alias("n_contratos"),
        ])
        .sort("monto", descending=True)
        .head(15)
        .to_pandas()
        .iloc[::-1]
        .reset_index(drop=True)
    )
    _top["label"] = _top["monto"].apply(fmt_mxn) + " · " + _top["n_contratos"].astype(str) + " contratos"
    _top["short"] = _top["contratista"].str.slice(0, 55) + (_top["contratista"].str.len() > 55).map({True: "…", False: ""})

    _fig = go.Figure(
        go.Bar(
            x=_top["monto"], y=_top["short"],
            orientation="h",
            marker=dict(color=_top["monto"], colorscale=[[0, "#FCA5A5"], [1, RED]], showscale=False),
            text=_top["label"], textposition="outside",
            textfont=dict(size=11, color="#334155"),
            hovertemplate="<b>%{customdata}</b><br>%{text}<extra></extra>",
            customdata=_top["contratista"],
            cliponaxis=False,
        )
    )
    _fig.update_layout(
        height=560,
        margin=dict(l=10, r=180, t=10, b=30),
        xaxis=dict(showgrid=True, gridcolor=SLATE_100, tickformat=".2s", title=""),
        yaxis=dict(title="", tickfont=dict(size=11, color="#0F172A")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif"),
    )
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### Fuga #4 · El chequeo de beneficiarios

        Cada punto es un proyecto. El eje X es el monto ejercido; el eje Y, las personas
        beneficiadas (declaradas por la unidad responsable). Puntos rojos: proyectos que
        afirman costar menos de **$1 por persona**. Puntos naranjas: más de **$1 millón
        por persona**. Ambos extremos son dudosos.
        """
    )
    return


@app.cell
def _(AMBER, RED, SLATE_400, df, go, pl):
    _pts = df.filter(
        (pl.col("poblacion_beneficiada") > 0) & (pl.col("monto_ejercido") > 0)
    ).with_columns(
        (pl.col("monto_ejercido") / pl.col("poblacion_beneficiada")).alias("per_persona")
    ).to_pandas()

    def _cat(v):
        if v < 1:
            return "Menos de $1/persona"
        if v > 1_000_000:
            return "Más de $1 mdp/persona"
        return "Rango razonable"

    _pts["flag"] = _pts["per_persona"].apply(_cat)
    _pts["name"] = _pts["nombre_proyecto"].fillna("").str.slice(0, 70)
    _pts["alc"] = _pts["desc_alcaldia"].fillna("")
    _colors = {"Rango razonable": SLATE_400, "Menos de $1/persona": RED, "Más de $1 mdp/persona": AMBER}

    _fig = go.Figure()
    for _cat_name, _sub in _pts.groupby("flag"):
        _fig.add_trace(go.Scatter(
            x=_sub["monto_ejercido"], y=_sub["poblacion_beneficiada"],
            mode="markers",
            name=_cat_name,
            marker=dict(
                color=_colors[_cat_name],
                size=7 if _cat_name != "Rango razonable" else 4,
                opacity=0.85 if _cat_name != "Rango razonable" else 0.35,
                line=dict(color="white", width=0.5),
            ),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>%{customdata[1]}<br>"
                "Ejercido: $%{x:,.0f}<br>Beneficiarios: %{y:,}<extra></extra>"
            ),
            customdata=_sub[["name", "alc"]].values,
        ))
    _fig.update_layout(
        height=520,
        xaxis=dict(type="log", title="Monto ejercido (MXN)", showgrid=True, gridcolor="#F1F5F9", tickformat="$,.0s"),
        yaxis=dict(type="log", title="Personas beneficiadas (declaradas)", showgrid=True, gridcolor="#F1F5F9", tickformat=",.0s"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif", size=12, color="#1E293B"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=60, r=20, t=40, b=50),
    )
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### ¿Y ahora qué?

        <div style="
            background: #FEF2F2;
            border-left: 4px solid #DC2626;
            border-radius: 10px;
            padding: 18px 24px;
            margin: 16px 0;
            line-height: 1.7;
            font-size: 14px;
            color: #450A0A;
        ">
        <b style="color:#7F1D1D;">Los datos públicos son el punto de partida, no la conclusión.</b>
        Cada fila en la tabla de rezagados y cada punto rojo en el gráfico de beneficiarios
        merece una pregunta formal: <em>¿qué pasó con ese dinero?</em> La CDMX publica el URL
        del contrato cuando está disponible — úsalo.
        <ul style="margin:10px 0 0 20px;padding:0;">
            <li>Presenta una solicitud de información pública (Plataforma Nacional de Transparencia)</li>
            <li>Verifica en campo: ¿la obra existe? ¿está operando?</li>
            <li>Contrasta con el registro de contratistas (ComprasMX)</li>
        </ul>
        </div>
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ---
        <div style="text-align:center;color:#64748B;font-size:12px;padding:14px 0 28px;">
        Fuente: <a href="https://datos.cdmx.gob.mx/dataset/rally-como-van-las-obras-cdmx" style="color:#DC2626;">Rally ¿Cómo van las obras? · Portal de Datos Abiertos CDMX</a>
        · Claude Mexico City Lab 2026 · Branch <code>red-team-accountability</code>
        </div>
        """
    )
    return


if __name__ == "__main__":
    app.run()
