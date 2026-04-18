import marimo

__generated_with = "0.23.1"
app = marimo.App(
    width="full",
    app_title="Sigue tu peso · proyectos con dinero federal en CDMX",
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
            Ciudad de México · Inversión con recursos federales
        </div>
        <div style="font-size: 38px; font-weight: 700; margin-top: 6px; letter-spacing: -0.5px;">
            Sigue tu peso — de Hacienda a tu calle
        </div>
        <div style="font-size: 15px; margin-top: 10px; opacity: 0.92; max-width: 860px; line-height: 1.55;">
            Hacienda mandó <b>$69 mmdp</b> a CDMX. Se volvieron <b>23,400 obras</b>.
            Pero <b>1 de cada 5 nunca pasó del 25% de avance</b>. Aquí están, en tu colonia.
        </div>
        </div>
        <div style="
            margin: 8px 0 18px;
            padding: 12px 18px;
            background: #FEF3C7;
            border-left: 4px solid #D97706;
            border-radius: 8px;
            color: #78350F;
            font-size: 13px;
            line-height: 1.5;
        ">
        <b>Datos 2013–2018.</b> Son los más recientes publicados por la CDMX con georreferencia
        completa. Fuente: <a href="https://datos.cdmx.gob.mx/dataset/rally-como-van-las-obras-cdmx"
        style="color:#78350F;text-decoration:underline;">Rally ¿Cómo van las obras? · Portal de Datos Abiertos CDMX</a>.
        </div>
        """
    )
    return


@app.cell
def _():
    import marimo as mo
    from pathlib import Path
    import math
    import polars as pl
    import plotly.express as px
    import plotly.graph_objects as go

    DATA_DIR = Path(__file__).parent.parent / "data"

    BUCKET_COLORS = {
        "Aportaciones (municipales)": "#9F2241",
        "Provisiones (estratégicas)": "#EC6730",
        "Sectoriales (otros)":        "#00A489",
    }
    STATUS_COLORS = {
        "Terminado": "#059669",
        "En curso":  "#D97706",
        "Rezagado":  "#DC2626",
        "Sin dato":  "#94A3B8",
    }
    ALCALDIA_PALETTE = [
        "#9F2241", "#E3007E", "#EC6730", "#00A489", "#00B7CD",
        "#6C4A7E", "#D6A461", "#3D5A80", "#C14953", "#2A9D8F",
        "#8B5CF6", "#F472B6", "#FBBF24", "#14B8A6", "#0EA5E9",
        "#F87171", "#A78BFA", "#34D399",
    ]

    def fmt_mxn(v):
        if v is None or v == 0:
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
        if v is None:
            return "—"
        return f"{int(v):,}"

    def bucketize_ramo(r):
        if not r:
            return "Sectoriales (otros)"
        if "Aportaciones" in r:
            return "Aportaciones (municipales)"
        if "Provisiones" in r:
            return "Provisiones (estratégicas)"
        return "Sectoriales (otros)"

    def bucketize_status(v):
        if v is None:
            return "Sin dato"
        if v >= 95:
            return "Terminado"
        if v >= 25:
            return "En curso"
        return "Rezagado"

    return (
        ALCALDIA_PALETTE, BUCKET_COLORS, DATA_DIR, STATUS_COLORS,
        bucketize_ramo, bucketize_status, fmt_int, fmt_mxn,
        go, math, mo, pl, px,
    )


@app.cell
def _(DATA_DIR, bucketize_ramo, bucketize_status, pl):
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
        pl.col("poblacion_beneficiada").fill_null(0),
    ]).filter(
        pl.col("latitud").is_not_null()
        & pl.col("longitud").is_not_null()
        & pl.col("latitud").is_between(19.0, 19.7)
        & pl.col("longitud").is_between(-99.5, -98.9)
    ).with_columns([
        pl.col("desc_ramo")
          .map_elements(bucketize_ramo, return_dtype=pl.Utf8)
          .alias("_bucket"),
        pl.col("avance_fisico")
          .map_elements(bucketize_status, return_dtype=pl.Utf8)
          .alias("_status"),
    ])
    return (raw,)


@app.cell(hide_code=True)
def _(mo):
    step = mo.ui.tabs(
        {
            "① Fuente":    mo.md('<div style="padding:10px 4px;color:#64748B;font-size:13px;">La fuente federal del dinero. Casi todo viene de dos ramos.</div>'),
            "② Dónde":     mo.md('<div style="padding:10px 4px;color:#64748B;font-size:13px;">Dónde aterrizó. Iztapalapa y GAM concentran buena parte.</div>'),
            "③ Avance":    mo.md('<div style="padding:10px 4px;color:#64748B;font-size:13px;">¿Se construyó? Cuántos proyectos llegaron al 100%.</div>'),
            "④ Explora":   mo.md('<div style="padding:10px 4px;color:#64748B;font-size:13px;">Tu turno — filtra libremente.</div>'),
        },
        value="① Fuente",
    )
    step
    return (step,)


@app.cell(hide_code=True)
def _(mo, raw):
    _alcaldias = sorted(raw["desc_alcaldia"].drop_nulls().unique().to_list())
    alcaldia_pick = mo.ui.dropdown(
        options=["Todas las alcaldías"] + _alcaldias,
        value="Todas las alcaldías",
        label="🎯 Enfocar alcaldía",
    )
    alcaldia_pick
    return (alcaldia_pick,)


@app.cell(hide_code=True)
def _(mo, raw):
    _buckets_list = ["Aportaciones (municipales)", "Provisiones (estratégicas)", "Sectoriales (otros)"]
    _years = sorted(raw["ciclo"].drop_nulls().unique().to_list())
    bucket_filter = mo.ui.multiselect(options=_buckets_list, value=[], label="Fuente federal")
    year_range = mo.ui.range_slider(
        start=min(_years), stop=max(_years),
        value=(min(_years), max(_years)), step=1,
        label="Año", show_value=True, full_width=False,
    )
    status_filter = mo.ui.dropdown(
        options=["Todos", "Terminado", "En curso", "Rezagado"],
        value="Todos", label="Estatus",
    )
    return bucket_filter, status_filter, year_range


@app.cell(hide_code=True)
def _(bucket_filter, mo, status_filter, step, year_range):
    if step.value == "④ Explora":
        _out = mo.hstack(
            [bucket_filter, year_range, status_filter],
            justify="start", gap=1.5, wrap=True,
        )
    else:
        _out = mo.md("")
    _out
    return


@app.cell
def _(alcaldia_pick, bucket_filter, pl, raw, status_filter, step, year_range):
    df = raw

    if alcaldia_pick.value and alcaldia_pick.value != "Todas las alcaldías":
        df = df.filter(pl.col("desc_alcaldia") == alcaldia_pick.value)

    if step.value == "④ Explora":
        if bucket_filter.value:
            df = df.filter(pl.col("_bucket").is_in(bucket_filter.value))
        df = df.filter(pl.col("ciclo").is_between(*year_range.value))
        if status_filter.value != "Todos":
            df = df.filter(pl.col("_status") == status_filter.value)
    return (df,)


@app.cell(hide_code=True)
def _(df, fmt_int, fmt_mxn, mo):
    _n = df.height
    _monto = df["monto_ejercido"].sum()
    _benef = df["poblacion_beneficiada"].sum()
    _alcs = df["desc_alcaldia"].n_unique()

    def _kpi(label, value, accent):
        return f"""
        <div style="
            background:white;border:1px solid #E2E8F0;border-left:4px solid {accent};
            border-radius:10px;padding:16px 20px;flex:1;min-width:160px;
            box-shadow:0 1px 3px rgba(15,23,42,0.04);
        ">
            <div style="font-size:10px;color:#64748B;letter-spacing:1.5px;text-transform:uppercase;font-weight:600;">{label}</div>
            <div style="font-size:24px;font-weight:700;color:#0F172A;margin-top:4px;letter-spacing:-0.5px;">{value}</div>
        </div>
        """

    mo.md(f"""
    <div style="display:flex;gap:12px;flex-wrap:wrap;margin:14px 0 18px;">
    {_kpi("Proyectos", fmt_int(_n), "#9F2241")}
    {_kpi("Inversión ejercida", fmt_mxn(_monto), "#00A489")}
    {_kpi("Personas beneficiadas", fmt_int(_benef), "#00B7CD")}
    {_kpi("Alcaldías con obra", fmt_int(_alcs), "#EC6730")}
    </div>
    """)
    return


@app.cell
def _(
    BUCKET_COLORS, STATUS_COLORS, alcaldia_pick, df, fmt_int, fmt_mxn,
    go, mo, pl, step,
):
    def _donut(labels, values, colors, center_text, height=260):
        _fig = go.Figure(go.Pie(
            labels=labels, values=values,
            hole=0.62,
            marker=dict(colors=colors, line=dict(color="white", width=2)),
            textinfo="percent",
            textfont=dict(size=12, color="white", family="Inter"),
            hovertemplate="<b>%{label}</b><br>%{value:,.0f} proyectos<br>%{percent}<extra></extra>",
            sort=False,
        ))
        _fig.update_layout(
            height=height,
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            annotations=[dict(text=center_text, x=0.5, y=0.5, showarrow=False, align="center")],
            font=dict(family="Inter, system-ui, sans-serif"),
        )
        return _fig

    if step.value == "① Fuente":
        _agg = (
            df.group_by("_bucket")
              .agg([
                  pl.col("monto_ejercido").sum().alias("monto"),
                  pl.len().alias("n"),
              ])
              .sort("monto", descending=True)
              .to_pandas()
        )
        _order = ["Aportaciones (municipales)", "Provisiones (estratégicas)", "Sectoriales (otros)"]
        _agg = _agg.set_index("_bucket").reindex(_order).reset_index().fillna(0)
        _total = _agg["monto"].sum() or 1

        _bullets = []
        for _, r in _agg.iterrows():
            _pct = r["monto"] / _total * 100
            _color = BUCKET_COLORS[r["_bucket"]]
            _bullets.append(f"""
            <div style="margin-bottom:14px;">
                <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px;">
                    <span style="font-size:13px;color:#0F172A;font-weight:600;">
                        <span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:{_color};margin-right:8px;vertical-align:middle;"></span>
                        {r['_bucket']}
                    </span>
                    <span style="font-size:13px;color:#475569;">{fmt_mxn(r['monto'])} · {_pct:.0f}%</span>
                </div>
                <div style="background:#F1F5F9;height:6px;border-radius:3px;overflow:hidden;">
                    <div style="background:{_color};width:{_pct}%;height:100%;"></div>
                </div>
            </div>
            """)

        panel = mo.md(f"""
        <div style="padding:22px 24px;background:white;border:1px solid #E2E8F0;border-radius:14px;">
            <div style="font-size:11px;color:#64748B;letter-spacing:1.8px;text-transform:uppercase;font-weight:600;">Fuente federal</div>
            <div style="font-size:28px;font-weight:700;color:#0F172A;margin-top:4px;line-height:1.15;letter-spacing:-0.5px;">
                Casi todo vino de 2 ramos
            </div>
            <div style="font-size:13px;color:#475569;margin:12px 0 18px;line-height:1.5;">
                <b>Aportaciones</b> (Ramo 33) son fondos federales etiquetados para infraestructura local.
                <b>Provisiones</b> (Ramo 23) son partidas estratégicas asignadas por la federación.
                Los sectoriales (Salud, Educación, SCT, etc.) aportan el resto.
            </div>
            {''.join(_bullets)}
        </div>
        """)

    elif step.value == "② Dónde":
        _alc = (
            df.group_by("desc_alcaldia")
              .agg(pl.col("monto_ejercido").sum().alias("monto"))
              .sort("monto", descending=True)
              .to_pandas()
        )
        _alc["desc_alcaldia"] = _alc["desc_alcaldia"].fillna("Sin alcaldía")
        _alc = _alc.iloc[::-1].reset_index(drop=True)
        _alc["label"] = _alc["monto"].apply(fmt_mxn)

        _selected = alcaldia_pick.value if alcaldia_pick.value != "Todas las alcaldías" else None
        _colors = ["#9F2241" if a == _selected else ("#CBD5E1" if _selected else "#9F2241")
                   for a in _alc["desc_alcaldia"]]

        _fig = go.Figure(go.Bar(
            x=_alc["monto"], y=_alc["desc_alcaldia"],
            orientation="h",
            marker=dict(color=_colors),
            text=_alc["label"],
            textposition="outside",
            textfont=dict(size=11, color="#334155"),
            hovertemplate="<b>%{y}</b><br>%{text}<extra></extra>",
            cliponaxis=False,
        ))
        _fig.update_layout(
            height=max(300, 28 * len(_alc) + 40),
            margin=dict(l=10, r=50, t=10, b=20),
            xaxis=dict(showgrid=True, gridcolor="#F1F5F9", tickformat=".2s", title=""),
            yaxis=dict(title="", tickfont=dict(size=11)),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, system-ui, sans-serif", size=12),
        )

        _header = mo.md("""
        <div style="padding:22px 24px 8px;background:white;border:1px solid #E2E8F0;
                    border-bottom:none;border-radius:14px 14px 0 0;">
            <div style="font-size:11px;color:#64748B;letter-spacing:1.8px;text-transform:uppercase;font-weight:600;">Distribución territorial</div>
            <div style="font-size:28px;font-weight:700;color:#0F172A;margin-top:4px;line-height:1.15;letter-spacing:-0.5px;">
                Dónde aterrizó el dinero
            </div>
            <div style="font-size:13px;color:#475569;margin-top:10px;line-height:1.5;">
                Elige tu alcaldía en el selector de arriba para ver solo sus proyectos.
            </div>
        </div>
        """)
        panel = mo.vstack([_header, mo.ui.plotly(_fig)])

    elif step.value == "③ Avance":
        _st = (
            df.group_by("_status")
              .agg([
                  pl.len().alias("n"),
                  pl.col("monto_ejercido").sum().alias("monto"),
              ])
              .to_pandas()
              .set_index("_status")
        )
        _order = ["Terminado", "En curso", "Rezagado", "Sin dato"]
        _order = [x for x in _order if x in _st.index]
        _st = _st.reindex(_order).fillna(0)
        _total_n = max(_st["n"].sum(), 1)
        _rezagado_n = int(_st.loc["Rezagado", "n"]) if "Rezagado" in _st.index else 0
        _rezagado_monto = _st.loc["Rezagado", "monto"] if "Rezagado" in _st.index else 0
        _ratio = _total_n / max(_rezagado_n, 1) if _rezagado_n else 0

        _donut_fig = _donut(
            list(_st.index), list(_st["n"]),
            [STATUS_COLORS[x] for x in _st.index],
            f"<b style='font-size:22px;color:#0F172A'>{int(_total_n):,}</b><br><span style='font-size:10px;color:#64748B;letter-spacing:1px'>PROYECTOS</span>",
            height=240,
        )

        _rows = []
        for _s in _order:
            _pct_n = _st.loc[_s, "n"] / _total_n * 100
            _rows.append(f"""
                <tr>
                    <td style="padding:8px 0;"><span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:{STATUS_COLORS[_s]};margin-right:8px;vertical-align:middle;"></span>{_s}</td>
                    <td style="padding:8px 0;text-align:right;font-weight:600;color:#0F172A;">{int(_st.loc[_s,'n']):,}</td>
                    <td style="padding:8px 0;text-align:right;color:#64748B;">{_pct_n:.0f}%</td>
                    <td style="padding:8px 0;text-align:right;color:#64748B;">{fmt_mxn(_st.loc[_s,'monto'])}</td>
                </tr>
            """)

        _hero_text = (
            f"<b style='color:#DC2626'>1 de cada {int(round(_ratio))}</b> proyectos quedó rezagado"
            if _rezagado_n else "Todos los proyectos con avance registrado"
        )

        panel = mo.md(f"""
        <div style="padding:22px 24px;background:white;border:1px solid #E2E8F0;border-radius:14px;">
            <div style="font-size:11px;color:#64748B;letter-spacing:1.8px;text-transform:uppercase;font-weight:600;">Ejecución física</div>
            <div style="font-size:28px;font-weight:700;color:#0F172A;margin-top:4px;line-height:1.15;letter-spacing:-0.5px;">
                ¿Se construyó?
            </div>
            <div style="font-size:15px;margin:10px 0 14px;color:#334155;">
                {_hero_text}
            </div>
            <div style="font-size:13px;color:#475569;margin-bottom:16px;line-height:1.5;">
                Rezagado = menos del 25% de avance físico. Acumulan
                <b style="color:#DC2626;">{fmt_mxn(_rezagado_monto)}</b> ejercidos.
            </div>
            <table style="width:100%;font-size:13px;border-collapse:collapse;">
                <thead>
                    <tr style="border-bottom:1px solid #E2E8F0;color:#64748B;font-size:10px;text-transform:uppercase;letter-spacing:1px;">
                        <th style="text-align:left;padding:6px 0;font-weight:600;">Estado</th>
                        <th style="text-align:right;padding:6px 0;font-weight:600;">Proy.</th>
                        <th style="text-align:right;padding:6px 0;font-weight:600;">%</th>
                        <th style="text-align:right;padding:6px 0;font-weight:600;">Ejercido</th>
                    </tr>
                </thead>
                <tbody>{''.join(_rows)}</tbody>
            </table>
        </div>
        """)

    else:
        _total_monto = df["monto_ejercido"].sum()
        _total_n = df.height

        _top_alc = (
            df.group_by("desc_alcaldia")
              .agg(pl.col("monto_ejercido").sum().alias("monto"))
              .sort("monto", descending=True)
              .head(1)
              .to_pandas()
        )
        _top_line = (
            f"<b>{_top_alc.iloc[0]['desc_alcaldia']}</b> lidera con <b>{fmt_mxn(_top_alc.iloc[0]['monto'])}</b>"
            if len(_top_alc) else "Sin datos con estos filtros"
        )

        panel = mo.md(f"""
        <div style="padding:22px 24px;background:white;border:1px solid #E2E8F0;border-radius:14px;">
            <div style="font-size:11px;color:#64748B;letter-spacing:1.8px;text-transform:uppercase;font-weight:600;">Modo exploración</div>
            <div style="font-size:28px;font-weight:700;color:#0F172A;margin-top:4px;line-height:1.15;letter-spacing:-0.5px;">
                Tu turno
            </div>
            <div style="font-size:13px;color:#475569;margin:10px 0 18px;line-height:1.5;">
                Combina los filtros de arriba (fuente · año · estatus) con el selector de alcaldía.
                El mapa y los contadores responden al instante.
            </div>
            <div style="padding:14px 16px;background:#F8FAFC;border-radius:10px;">
                <div style="font-size:11px;color:#64748B;letter-spacing:1px;text-transform:uppercase;font-weight:600;">Con los filtros actuales</div>
                <div style="font-size:20px;font-weight:700;color:#0F172A;margin-top:6px;">{fmt_mxn(_total_monto)} · {fmt_int(_total_n)} proyectos</div>
                <div style="font-size:12px;color:#475569;margin-top:6px;">{_top_line}</div>
            </div>
        </div>
        """)

    panel
    return (panel,)


@app.cell
def _(
    ALCALDIA_PALETTE, BUCKET_COLORS, STATUS_COLORS,
    alcaldia_pick, df, fmt_mxn, math, mo, pl, px, step,
):
    _pdf = df.select([
        "id", "latitud", "longitud", "_bucket", "_status",
        "desc_ramo", "desc_alcaldia", "desc_localidad",
        "monto_ejercido", "nombre_proyecto", "avance_fisico", "ciclo",
    ]).to_pandas().copy()
    _pdf["desc_alcaldia"] = _pdf["desc_alcaldia"].fillna("Sin alcaldía")
    _pdf["_name"] = _pdf["nombre_proyecto"].fillna("(sin nombre)").str.slice(0, 90)

    def _hover(row):
        _place = " · ".join([s for s in [row["desc_alcaldia"], row["desc_localidad"]] if isinstance(s, str) and s])
        _avance = f"{row['avance_fisico']:.0f}%" if row["avance_fisico"] else "—"
        return (
            f"<b>{row['_name']}</b><br>"
            f"<span style='color:#64748B'>{_place} · {int(row['ciclo'])}</span><br>"
            f"Ejercido <b>{fmt_mxn(row['monto_ejercido'])}</b> · Avance {_avance}<br>"
            f"<span style='color:#9F2241'>{row['_bucket']}</span>"
        )
    _pdf["_h"] = _pdf.apply(_hover, axis=1)
    _pdf["_size"] = _pdf["monto_ejercido"].apply(
        lambda v: max(math.sqrt(max(v, 0)) / 700, 4)
    )

    if step.value == "① Fuente" or step.value == "④ Explora":
        _color_col = "_bucket"
        _cat_order = ["Aportaciones (municipales)", "Provisiones (estratégicas)", "Sectoriales (otros)"]
        _present = [c for c in _cat_order if c in _pdf["_bucket"].unique()]
        _colors = [BUCKET_COLORS[c] for c in _present]
        _title = "Fuente federal"
    elif step.value == "② Dónde":
        _color_col = "desc_alcaldia"
        _present = sorted(_pdf["desc_alcaldia"].unique())
        _colors = [ALCALDIA_PALETTE[i % len(ALCALDIA_PALETTE)] for i in range(len(_present))]
        _title = "Alcaldía"
    else:
        _color_col = "_status"
        _cat_order = ["Terminado", "En curso", "Rezagado", "Sin dato"]
        _present = [c for c in _cat_order if c in _pdf["_status"].unique()]
        _colors = [STATUS_COLORS[c] for c in _present]
        _title = "Estatus del proyecto"

    _center = {"lat": 19.38, "lon": -99.15}
    _zoom = 9.7
    if alcaldia_pick.value and alcaldia_pick.value != "Todas las alcaldías":
        _sub = _pdf[_pdf["desc_alcaldia"] == alcaldia_pick.value]
        if len(_sub):
            _center = {"lat": float(_sub["latitud"].mean()), "lon": float(_sub["longitud"].mean())}
            _zoom = 11.5

    _fig = px.scatter_map(
        _pdf,
        lat="latitud", lon="longitud",
        color=_color_col,
        color_discrete_sequence=_colors,
        category_orders={_color_col: _present},
        size="_size",
        size_max=26,
        custom_data=["id", "_h"],
        zoom=_zoom,
        center=_center,
        map_style="carto-positron",
        opacity=0.78,
    )
    _fig.update_traces(hovertemplate="%{customdata[1]}<extra></extra>")
    _fig.update_layout(
        height=620,
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(
            orientation="v",
            yanchor="top", y=0.99,
            xanchor="left", x=0.01,
            bgcolor="rgba(255,255,255,0.94)",
            bordercolor="#E2E8F0", borderwidth=1,
            font=dict(size=11, family="Inter"),
            title=dict(text=f"<b>{_title}</b>", font=dict(size=12)),
            itemsizing="constant",
        ),
        paper_bgcolor="white",
    )

    map_widget = mo.ui.plotly(_fig)
    return (map_widget,)


@app.cell(hide_code=True)
def _(map_widget, mo, panel):
    mo.hstack([panel, map_widget], justify="start", gap=1.5, widths=[1, 2], wrap=True)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### Proyecto seleccionado
        <div style="font-size:13px;color:#64748B;margin:-4px 0 12px;">Haz clic en cualquier punto del mapa.</div>
        """
    )
    return


@app.cell
def _(df, fmt_int, fmt_mxn, map_widget, mo, pl):
    _selected_ids = []
    try:
        _points = getattr(map_widget, "value", None) or []
        if isinstance(_points, list):
            for _p in _points:
                _cd = _p.get("customdata")
                if _cd and len(_cd) > 0:
                    _selected_ids.append(_cd[0])
    except Exception:
        pass

    if not _selected_ids:
        detail = mo.md(
            """
            <div style="padding:22px;border:1.5px dashed #CBD5E1;border-radius:12px;
                        color:#64748B;text-align:center;background:#F8FAFC;">
                👆 Haz clic en un punto del mapa para ver los detalles del proyecto.
            </div>
            """
        )
    else:
        _proj = df.filter(pl.col("id") == _selected_ids[0]).to_pandas().iloc[0]

        _status_color = "#059669" if _proj["avance_fisico"] >= 95 else (
            "#D97706" if _proj["avance_fisico"] >= 25 else "#DC2626"
        )
        _status_label = "Terminado" if _proj["avance_fisico"] >= 95 else (
            "En curso" if _proj["avance_fisico"] >= 25 else "Rezagado"
        )

        _contract_link = ""
        if isinstance(_proj.get("url_contrato"), str) and _proj["url_contrato"].startswith("http"):
            _contract_link = (
                f'<a href="{_proj["url_contrato"]}" target="_blank" '
                'style="color:#9F2241;text-decoration:underline;font-weight:500;">ver contrato ↗</a>'
            )

        _justif = _proj.get("justificacion") or ""
        if isinstance(_justif, str) and _justif.strip():
            _justif_html = (
                f'<div style="margin-top:16px;padding:14px;background:#F8FAFC;'
                f'border-radius:8px;font-size:13px;color:#334155;line-height:1.55;">'
                f'<div style="font-size:10px;letter-spacing:1px;color:#64748B;'
                f'text-transform:uppercase;margin-bottom:6px;">Justificación</div>{_justif[:500]}</div>'
            )
        else:
            _justif_html = ""

        detail = mo.md(f"""
        <div style="
            border:1px solid #E2E8F0; border-radius:14px; padding:24px 28px;
            background:white; box-shadow:0 2px 8px rgba(15,23,42,0.04);
        ">
            <div style="display:flex;align-items:start;justify-content:space-between;gap:20px;">
                <div style="flex:1;">
                    <div style="font-size:20px;font-weight:700;color:#0F172A;letter-spacing:-0.3px;line-height:1.3;">
                        {_proj['nombre_proyecto'] or '(sin nombre)'}
                    </div>
                    <div style="margin-top:6px;font-size:13px;color:#64748B;">
                        {_proj.get('desc_alcaldia','')} · {_proj.get('desc_localidad','')} · {_proj.get('direccion_proyecto','') or ''}
                    </div>
                </div>
                <div style="
                    padding:6px 14px;border-radius:20px;
                    background:{_status_color}15;color:{_status_color};
                    font-weight:600;font-size:12px;letter-spacing:0.5px;text-transform:uppercase;
                    white-space:nowrap;
                ">
                    {_status_label} · {_proj['avance_fisico']:.0f}%
                </div>
            </div>

            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));
                        gap:16px;margin-top:20px;padding-top:18px;border-top:1px solid #F1F5F9;">
                <div>
                    <div style="font-size:10px;letter-spacing:1.2px;color:#64748B;text-transform:uppercase;font-weight:600;">Aprobado</div>
                    <div style="font-size:17px;font-weight:600;color:#0F172A;margin-top:3px;">{fmt_mxn(_proj['monto_aprobado'])}</div>
                </div>
                <div>
                    <div style="font-size:10px;letter-spacing:1.2px;color:#64748B;text-transform:uppercase;font-weight:600;">Ejercido</div>
                    <div style="font-size:17px;font-weight:600;color:#9F2241;margin-top:3px;">{fmt_mxn(_proj['monto_ejercido'])}</div>
                </div>
                <div>
                    <div style="font-size:10px;letter-spacing:1.2px;color:#64748B;text-transform:uppercase;font-weight:600;">Pagado</div>
                    <div style="font-size:17px;font-weight:600;color:#0F172A;margin-top:3px;">{fmt_mxn(_proj['monto_pagado'])}</div>
                </div>
                <div>
                    <div style="font-size:10px;letter-spacing:1.2px;color:#64748B;text-transform:uppercase;font-weight:600;">Beneficiarios</div>
                    <div style="font-size:17px;font-weight:600;color:#0F172A;margin-top:3px;">{fmt_int(_proj['poblacion_beneficiada'])}</div>
                </div>
                <div>
                    <div style="font-size:10px;letter-spacing:1.2px;color:#64748B;text-transform:uppercase;font-weight:600;">Fuente</div>
                    <div style="font-size:13px;font-weight:500;color:#0F172A;margin-top:3px;line-height:1.35;">{_proj.get('desc_ramo','—')}</div>
                </div>
                <div>
                    <div style="font-size:10px;letter-spacing:1.2px;color:#64748B;text-transform:uppercase;font-weight:600;">Contratista</div>
                    <div style="font-size:13px;font-weight:500;color:#0F172A;margin-top:3px;line-height:1.35;">
                        {_proj.get('contratista') or '—'}{' · ' + _contract_link if _contract_link else ''}
                    </div>
                </div>
            </div>

            {_justif_html}
        </div>
        """)

    detail
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ---
        <div style="text-align:center;color:#64748B;font-size:12px;padding:14px 0 28px;">
        Fuente: <a href="https://datos.cdmx.gob.mx/dataset/rally-como-van-las-obras-cdmx" style="color:#9F2241;">Rally ¿Cómo van las obras? · Portal de Datos Abiertos CDMX</a>
        · Construido con Marimo + Plotly · Claude Mexico City Lab 2026
        </div>
        """
    )
    return


if __name__ == "__main__":
    app.run()
