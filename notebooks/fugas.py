import marimo

__generated_with = "0.23.1"
app = marimo.App(
    width="full",
    app_title="Lo que no está en el dato · auditoría de la transparencia federal en CDMX",
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
            Auditoría de la transparencia · recursos federales en CDMX
        </div>
        <div style="font-size: 38px; font-weight: 700; margin-top: 6px; letter-spacing: -0.5px;">
            Lo que no está en el dato.
        </div>
        <div style="font-size: 18px; margin-top: 6px; opacity: 0.85; font-weight: 400;">
            El mapa te muestra qué se construyó. Este tablero te muestra lo que los datos
            públicos <em>no</em> pueden responder — y por qué importa.
        </div>
        <div style="font-size: 14px; margin-top: 16px; opacity: 0.75; max-width: 820px; line-height: 1.6;">
            Tres hallazgos verificables del Rally <em>¿Cómo van las obras?</em> (23,410 proyectos federales
            2013–2018). No son evidencia de corrupción — son los huecos en la información
            publicada que impiden auditar desde fuera del gobierno.
        </div>
        </div>
        <div style="
            margin: 8px 0 20px;
            padding: 14px 20px;
            background: #FEF3C7;
            border-left: 4px solid #D97706;
            border-radius: 8px;
            color: #78350F;
            font-size: 13px;
            line-height: 1.55;
        ">
        <b>Metodología.</b> Usamos únicamente columnas publicadas en el dataset oficial.
        Cada número tiene un criterio explícito abajo. Los hallazgos son sobre el
        <em>estado de la información</em>, no sobre la conducta de los servidores
        públicos. Dataset última actualización: <b>feb 2023</b> · corte para "planes vencidos".
        </div>
        """
    )
    return


@app.cell
def _():
    import marimo as mo
    from pathlib import Path
    from datetime import date
    import polars as pl
    import plotly.express as px
    import plotly.graph_objects as go

    DATA_DIR = Path(__file__).parent.parent / "data"
    FONT = "Inter, -apple-system, system-ui, sans-serif"

    RED = "#DC2626"
    AMBER = "#D97706"
    GREEN = "#059669"
    SLATE_900 = "#0F172A"
    SLATE_600 = "#475569"
    SLATE_400 = "#94A3B8"
    SLATE_100 = "#F1F5F9"

    DATASET_CUTOFF = date(2023, 2, 15)

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

    return AMBER, DATASET_CUTOFF, GREEN, RED, SLATE_100, SLATE_400, SLATE_600, SLATE_900, fmt_int, fmt_mxn, fmt_pct, go, mo, pl, px


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
        pl.col("avance_financiero").fill_null(-1),
        pl.col("poblacion_beneficiada").fill_null(0),
        pl.col("termino_proyecto").str.to_date(strict=False).alias("termino_dt"),
    ])
    return (raw,)


@app.cell(hide_code=True)
def _(DATASET_CUTOFF, fmt_mxn, fmt_pct, mo, pl, raw):
    _no_report_flag = (pl.col("contratista") == "La Unidad Responsable no reportó información")
    _no_report_rows = raw.filter(_no_report_flag).height
    _total_rows = raw.height
    _no_report_pct_rows = _no_report_rows / _total_rows * 100

    _overdue_stalled = raw.filter(
        (pl.col("avance_fisico") < 25)
        & (pl.col("monto_ejercido") > 100_000)
        & (pl.col("termino_dt") < DATASET_CUTOFF)
        & (pl.col("termino_dt").is_not_null())
    )
    _overdue_stalled_n = _overdue_stalled.height
    _overdue_stalled_monto = _overdue_stalled["monto_ejercido"].sum()
    _overdue_stalled_fin_med = (
        _overdue_stalled.filter(pl.col("avance_financiero") >= 0)["avance_financiero"].median() or 0
    )

    _pop_proxy = raw.filter(
        (pl.col("poblacion_beneficiada") > 500_000)
        & (pl.col("monto_ejercido") < 5_000_000)
    )
    _pop_proxy_n = _pop_proxy.height

    def _flag(emoji, number, label, caption, caveat, tone="#DC2626"):
        return f"""
        <div style="
            background: white;
            border: 1px solid #E2E8F0;
            border-left: 5px solid {tone};
            border-radius: 12px;
            padding: 20px 24px;
            flex: 1;
            min-width: 280px;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
            display:flex;flex-direction:column;
        ">
            <div style="font-size:26px;line-height:1;">{emoji}</div>
            <div style="font-size:30px;font-weight:800;color:{tone};margin-top:12px;letter-spacing:-0.5px;line-height:1;">{number}</div>
            <div style="font-size:12px;letter-spacing:1px;color:#0F172A;text-transform:uppercase;font-weight:700;margin-top:10px;line-height:1.35;">{label}</div>
            <div style="font-size:13px;color:#475569;margin-top:8px;line-height:1.55;">{caption}</div>
            <div style="margin-top:auto;padding-top:12px;font-size:11px;color:#94A3B8;font-style:italic;line-height:1.45;border-top:1px dashed #E2E8F0;">
            {caveat}
            </div>
        </div>
        """

    mo.md(f"""
    <div style="display:flex;gap:16px;flex-wrap:wrap;margin:18px 0 8px;">
    {_flag("🕳️", fmt_pct(_no_report_pct_rows, 0),
           "Proyectos sin contratista publicado",
           f"{_no_report_rows:,} de {_total_rows:,} registros tienen el campo 'contratista' lleno con la leyenda <em>'La Unidad Responsable no reportó información'</em>. Es un hueco en la publicación, no evidencia de ocultamiento — pero bloquea la fiscalización ciudadana.",
           "Fuente: conteo directo sobre el campo 'contratista' del CSV oficial. La publicación del nombre del contratista es obligación de la unidad responsable según los lineamientos de la SHCP.",
          )}
    {_flag("⏸️", fmt_mxn(_overdue_stalled_monto),
           "Ejercidos en proyectos que no cumplieron su plan",
           f"{_overdue_stalled_n:,} proyectos con fecha de término vencida, <25% de avance físico y >$100k ejercidos. Mediana de <b>avance financiero: {_overdue_stalled_fin_med:.0f}%</b> — el dinero fluyó; el concreto, no.",
           "Criterio: avance_fisico < 25 AND monto_ejercido > 100,000 AND termino_proyecto < 2023-02-15 (corte del dataset). Excluye proyectos mid-flight.",
           tone="#D97706",
          )}
    {_flag("👥", f"{_pop_proxy_n}",
           "Proyectos que reportan población como 'beneficiarios'",
           f"Casos donde <b>poblacion_beneficiada &gt; 500,000</b> pero el monto ejercido es &lt;$5M. Los números repiten la población de la alcaldía — la métrica no debe sumarse entre proyectos.",
           "Inspección manual: proyectos en Coyoacán, Benito Juárez, Álvaro Obregón reportan el mismo número (habitantes) en múltiples obras distintas.",
           tone="#475569",
          )}
    </div>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### ① El hueco de transparencia crece con el tiempo

        La fracción de proyectos sin contratista publicado aumentó de ~33% en 2016 a ~92% en 2018.
        Puede reflejar relajamiento en el cumplimiento de publicación, cambios en el flujo de reporte
        entre alcaldías y SHCP, o simplemente un campo opcional que dejó de llenarse. No lo sabemos
        desde el dataset — pero el patrón merece una explicación institucional.
        """
    )
    return


@app.cell
def _(GREEN, RED, go, pl, raw):
    _by_year = raw.with_columns(
        pl.when(pl.col("contratista") == "La Unidad Responsable no reportó información")
          .then(pl.lit("No publicado"))
          .otherwise(pl.lit("Con contratista"))
          .alias("transparencia")
    ).group_by(["ciclo", "transparencia"]).agg(pl.len().alias("n")).sort(["ciclo", "transparencia"]).to_pandas()

    _pvt = _by_year.pivot_table(index="ciclo", columns="transparencia", values="n", fill_value=0).reset_index()
    if "No publicado" not in _pvt.columns:
        _pvt["No publicado"] = 0
    if "Con contratista" not in _pvt.columns:
        _pvt["Con contratista"] = 0
    _pvt["total"] = _pvt["No publicado"] + _pvt["Con contratista"]
    _pvt["pct_oculto"] = _pvt["No publicado"] / _pvt["total"] * 100

    _fig = go.Figure()
    _fig.add_trace(go.Bar(
        x=_pvt["ciclo"], y=_pvt["Con contratista"],
        name="Con contratista publicado", marker=dict(color=GREEN),
        hovertemplate="<b>%{x}</b><br>Publicado: %{y}<extra></extra>",
    ))
    _fig.add_trace(go.Bar(
        x=_pvt["ciclo"], y=_pvt["No publicado"],
        name="Sin contratista publicado", marker=dict(color=RED),
        hovertemplate="<b>%{x}</b><br>No publicado: %{y}<extra></extra>",
    ))
    _fig.add_trace(go.Scatter(
        x=_pvt["ciclo"], y=_pvt["pct_oculto"],
        name="% sin publicar", yaxis="y2",
        mode="lines+markers+text",
        line=dict(color="#0F172A", width=3),
        marker=dict(size=10, color="#0F172A"),
        text=[f"{v:.0f}%" for v in _pvt["pct_oculto"]],
        textposition="top center",
        textfont=dict(size=12, color="#0F172A", family="Inter"),
        hovertemplate="<b>%{x}</b><br>%{y:.1f}% sin publicar<extra></extra>",
    ))
    _fig.update_layout(
        barmode="stack",
        height=420,
        xaxis=dict(title="Año", showgrid=False),
        yaxis=dict(title="Proyectos (barras)", showgrid=True, gridcolor="#F1F5F9"),
        yaxis2=dict(
            title="% sin publicar",
            overlaying="y", side="right",
            range=[0, 110], showgrid=False, ticksuffix="%",
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif", color="#1E293B"),
        margin=dict(l=60, r=60, t=40, b=40),
    )
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### ② Proyectos que no cumplieron su plan

        **Criterio estricto:** fecha de término anterior al corte del dataset (feb 2023),
        avance físico reportado &lt;25%, monto ejercido &gt;$500k.

        Cada fila es un proyecto concreto sobre el que se puede solicitar información pública.
        La columna *"Avance físico / financiero"* es el indicador más directo — cuando el dinero
        va por encima de la obra, merece una pregunta.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo, raw):
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
def _(DATASET_CUTOFF, df, fmt_mxn, mo, pl):
    _overdue = df.filter(
        (pl.col("avance_fisico") < 25)
        & (pl.col("monto_ejercido") > 500_000)
        & (pl.col("termino_dt") < DATASET_CUTOFF)
        & (pl.col("termino_dt").is_not_null())
    ).sort("monto_ejercido", descending=True).head(30)

    if _overdue.height == 0:
        mo.md("*Sin proyectos que cumplan el criterio con los filtros actuales.* 🎉")
    else:
        _rows = _overdue.to_pandas()
        _rows["nombre"] = _rows["nombre_proyecto"].fillna("(sin nombre)").str.slice(0, 80)
        _rows["alcaldia"] = _rows["desc_alcaldia"].fillna("—")
        _rows["ramo"] = _rows["desc_ramo"].fillna("—").str.slice(0, 50)
        _rows["termino"] = _rows["termino_dt"].astype(str)
        _rows["aprobado"] = _rows["monto_aprobado"].apply(fmt_mxn)
        _rows["ejercido"] = _rows["monto_ejercido"].apply(fmt_mxn)
        _rows["fis"] = _rows["avance_fisico"].apply(lambda v: f"{v:.0f}%")
        _rows["fin"] = _rows["avance_financiero"].apply(lambda v: f"{v:.0f}%" if v >= 0 else "—")

        _display = _rows[["nombre","alcaldia","ramo","termino","aprobado","ejercido","fis","fin"]].rename(columns={
            "nombre":"Proyecto","alcaldia":"Alcaldía","ramo":"Ramo","termino":"Término planeado",
            "aprobado":"Aprobado","ejercido":"Ejercido","fis":"Avance físico","fin":"Avance financiero",
        })
        mo.ui.table(_display, selection=None, page_size=12, show_column_summaries=False)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### ③ Concentración entre los que <em>sí</em> publicaron contratista

        Sólo el 12% de los proyectos publicó el nombre del contratista. Entre esos,
        estos son los 15 despachos que más dinero federal recibieron en CDMX.

        <div style="background:#EFF6FF;border-left:4px solid #3B82F6;padding:12px 16px;border-radius:8px;margin:12px 0;color:#1E3A8A;font-size:13px;line-height:1.55;">
        <b>Atención al sesgo de la muestra.</b> Esta concentración se calcula sobre los ~2,833 proyectos
        con contratista publicado — no es representativa del universo total.
        </div>
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
    _short = _top["contratista"].str.slice(0, 55)
    _top["short"] = [s + ("…" if len(c) > 55 else "") for s, c in zip(_short, _top["contratista"])]

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
        ### ④ La métrica de beneficiarios no es sumable

        Varias unidades responsables reportan el total de habitantes de su alcaldía como
        *"población beneficiada"* de proyectos individuales. Eso infla la cifra agregada
        sin necesariamente ser deshonesto — es una convención burocrática para proyectos
        de uso general (pavimentación, alumbrado, seguridad).

        **Implicación:** si ves un titular de *"el programa X benefició a 15 millones
        de personas"* basado en la suma de `poblacion_beneficiada`, sospecha. Los
        datos unitarios son reportes de *potencial* poblacional, no conteos de
        beneficiarios únicos.
        """
    )
    return


@app.cell
def _(fmt_mxn, go, pl, raw):
    _sample = raw.filter(
        (pl.col("poblacion_beneficiada") > 500_000)
        & (pl.col("monto_ejercido") < 5_000_000)
        & (pl.col("monto_ejercido") > 10_000)
    ).group_by("desc_alcaldia").agg([
        pl.col("poblacion_beneficiada").max().alias("pop_repetida"),
        pl.len().alias("n_proyectos"),
        pl.col("monto_ejercido").sum().alias("monto_total"),
    ]).sort("n_proyectos", descending=True).head(10).to_pandas()

    _sample["monto_str"] = _sample["monto_total"].apply(fmt_mxn)
    _sample["pop_str"] = _sample["pop_repetida"].apply(lambda v: f"{int(v):,}")

    if _sample.empty:
        _fig = go.Figure()
    else:
        _fig = go.Figure(
            go.Bar(
                x=_sample["n_proyectos"],
                y=_sample["desc_alcaldia"],
                orientation="h",
                marker=dict(color="#475569"),
                text=[f"  {n} proyectos · cada uno dice '{p} beneficiarios'" for n, p in zip(_sample["n_proyectos"], _sample["pop_str"])],
                textposition="outside",
                textfont=dict(size=11, color="#334155"),
                hovertemplate="<b>%{y}</b><br>%{x} proyectos reportaron %{customdata} beneficiarios cada uno<br>Monto combinado: %{text}<extra></extra>",
                customdata=_sample["pop_str"],
                cliponaxis=False,
            )
        )
        _fig.update_layout(
            height=420,
            margin=dict(l=10, r=260, t=10, b=30),
            xaxis=dict(showgrid=True, gridcolor="#F1F5F9", title="Número de proyectos distintos que repiten el mismo 'total de beneficiarios'"),
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
        <b style="color:#7F1D1D;">Estos no son hallazgos de corrupción. Son hallazgos sobre el estado de la información pública.</b>
        Cada uno es el punto de partida para una pregunta, no la conclusión.
        <ul style="margin:10px 0 0 20px;padding:0;">
            <li><b>Transparencia:</b> solicitar vía PNT (Plataforma Nacional de Transparencia) el desglose contractual de proyectos marcados <em>"no reportó información"</em>.</li>
            <li><b>Planes vencidos:</b> revisar la tabla, ir a la dirección del proyecto, contrastar con la realidad en campo.</li>
            <li><b>Contratistas recurrentes:</b> cruzar con padrones de ComprasMX y con el <em>Registro Único de Contratistas</em>.</li>
            <li><b>Beneficiarios:</b> no sumar la columna. Pedir a la unidad responsable la metodología específica por proyecto.</li>
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
