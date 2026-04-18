import marimo

__generated_with = "0.23.1"
app = marimo.App(
    width="full",
    app_title="La ruta de tu peso · CDMX",
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
            Ciudad de México · finanzas públicas
        </div>
        <div style="font-size: 38px; font-weight: 700; margin-top: 6px; letter-spacing: -0.5px;">
            La ruta de tu peso
        </div>
        <div style="font-size: 15px; margin-top: 10px; opacity: 0.92; max-width: 860px; line-height: 1.55;">
            El viaje del dinero público, en tres actos.<br/>
            <b>① Entran</b> — de dónde vienen los pesos.
            <b>② Se prometen</b> — plan vs. lo ejercido.
            <b>③ Aterrizan</b> — en qué manos terminan.
        </div>
        </div>
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
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
        <b>Cobertura:</b> Ingresos y egresos 2018–2024 · Cuenta Pública oficial (cerrada) 2018–2022
        · Q3 trimestral 2023 · Aprobado 2024 (año en curso) · Contratistas Rally ¿Cómo van las obras?
        2013–2018.  Fuentes:
        <a href="https://datos.cdmx.gob.mx/dataset/ingresos" style="color:#78350F;text-decoration:underline;">Ingresos CDMX</a>
        · <a href="https://datos.cdmx.gob.mx/dataset/presupuesto-de-egresos" style="color:#78350F;text-decoration:underline;">Presupuesto de egresos</a>
        · <a href="https://datos.cdmx.gob.mx/dataset/rally-como-van-las-obras-cdmx" style="color:#78350F;text-decoration:underline;">Rally obras</a>.
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
    FONT = "Inter, -apple-system, system-ui, sans-serif"

    SOURCE_COLORS = {
        "Impuestos locales":                        "#9F2241",
        "Derechos y productos":                     "#E3007E",
        "Federal (participaciones + aportaciones)": "#EC6730",
        "Sector paraestatal":                       "#00B7CD",
        "Financiamientos (deuda)":                  "#6C4A7E",
        "Otros":                                    "#94A3B8",
    }
    SOURCE_ORDER = list(SOURCE_COLORS.keys())

    CHAPTER_PALETTE = [
        "#9F2241", "#E3007E", "#EC6730", "#00A489", "#00B7CD",
        "#6C4A7E", "#D6A461", "#3D5A80", "#C14953", "#2A9D8F",
    ]

    EGRESOS_FILE_MAP = {
        2018: ("egresos_2018_cp.csv",          "modificado", "Cuenta Pública (cerrada)"),
        2019: ("egresos_2019_cp.csv",          "modificado", "Cuenta Pública (cerrada)"),
        2020: ("egresos_2020_cp.csv",          "modificado", "Cuenta Pública (cerrada)"),
        2021: ("egresos_2021_cp.csv",          "modificado", "Cuenta Pública (cerrada)"),
        2022: ("egresos_2022_cp.csv",          "modificado", "Cuenta Pública (cerrada)"),
        2023: ("egresos_2023_03_trimestre.csv","modificado", "Q3 trimestral (parcial)"),
        2024: ("egresos_2024_aprobado.csv",    "aprobado",   "Aprobado (sin ejecución)"),
    }

    def fmt_mxn(v):
        if v is None or v == 0:
            return "—"
        v = float(v)
        if abs(v) >= 1e9:
            return f"${v/1e9:,.2f} mmdp"
        if abs(v) >= 1e6:
            return f"${v/1e6:,.1f} mdp"
        if abs(v) >= 1e3:
            return f"${v/1e3:,.0f} k"
        return f"${v:,.0f}"

    def fmt_int(v):
        if v is None:
            return "—"
        return f"{int(v):,}"

    def bucketize_ingreso(tipo_clase, rubro):
        if tipo_clase == "Ingresos locales":
            if rubro == "Impuestos":
                return "Impuestos locales"
            if rubro in ("Derechos", "Productos", "Aprovechamientos"):
                return "Derechos y productos"
            return "Otros"
        if tipo_clase == "Recursos federales":
            return "Federal (participaciones + aportaciones)"
        if tipo_clase == "Ingresos del Sector Paraestatal":
            return "Sector paraestatal"
        if tipo_clase == "Endeudamiento":
            return "Financiamientos (deuda)"
        return "Otros"

    return (
        CHAPTER_PALETTE, DATA_DIR, EGRESOS_FILE_MAP, FONT, SOURCE_COLORS,
        SOURCE_ORDER, bucketize_ingreso, fmt_int, fmt_mxn,
        go, math, mo, pl, px,
    )


@app.cell
def _(DATA_DIR, bucketize_ingreso, pl):
    ingresos_raw = pl.read_csv(
        DATA_DIR / "ingresos_main.csv",
        infer_schema_length=10_000,
        null_values=["NA", ""],
        truncate_ragged_lines=True,
        ignore_errors=True,
        encoding="utf8-lossy",
    ).with_columns([
        pl.col("monto_estimado").cast(pl.Float64, strict=False).fill_null(0),
        pl.col("monto_recaudado").cast(pl.Float64, strict=False).fill_null(0),
        pl.struct(["desc_tipo_recurso_clase", "desc_rubro"])
          .map_elements(
              lambda s: bucketize_ingreso(s["desc_tipo_recurso_clase"], s["desc_rubro"]),
              return_dtype=pl.Utf8,
          ).alias("_bucket"),
    ])
    return (ingresos_raw,)


@app.cell
def _(DATA_DIR, pl):
    rally_raw = pl.read_csv(
        DATA_DIR / "rally_obras.csv",
        infer_schema_length=10_000,
        null_values=["NA", ""],
        truncate_ragged_lines=True,
        ignore_errors=True,
    ).with_columns([
        pl.col("monto_ejercido").cast(pl.Float64, strict=False).fill_null(0),
        pl.col("rfc_contratista").str.to_uppercase().str.strip_chars().alias("rfc_contratista"),
    ])
    return (rally_raw,)


@app.cell(hide_code=True)
def _(EGRESOS_FILE_MAP, mo):
    year_pick = mo.ui.dropdown(
        options={f"{y} · {EGRESOS_FILE_MAP[y][2]}": y for y in sorted(EGRESOS_FILE_MAP.keys())},
        value=f"2018 · {EGRESOS_FILE_MAP[2018][2]}",
        label="📅 Año",
    )
    return (year_pick,)


@app.cell
def _(DATA_DIR, EGRESOS_FILE_MAP, pl, year_pick):
    _year = year_pick.value
    _file, _bcol_type, _label = EGRESOS_FILE_MAP[_year]

    egresos_df = pl.read_csv(
        DATA_DIR / _file,
        infer_schema_length=10_000,
        null_values=["NA", ""],
        truncate_ragged_lines=True,
        ignore_errors=True,
        encoding="utf8-lossy",
        schema_overrides={
            "monto_aprobado":   pl.Float64,
            "monto_modificado": pl.Float64,
            "monto_ejercido":   pl.Float64,
        },
    )

    budget_col = "monto_modificado" if _bcol_type == "modificado" else "monto_aprobado"
    has_ejercido = "monto_ejercido" in egresos_df.columns and egresos_df["monto_ejercido"].fill_null(0).sum() > 0

    egresos_df = egresos_df.with_columns([
        pl.col(budget_col).fill_null(0).alias("_budget"),
        pl.col("monto_ejercido").fill_null(0).alias("_spent") if "monto_ejercido" in egresos_df.columns
            else pl.lit(0.0).alias("_spent"),
    ])
    return budget_col, egresos_df, has_ejercido


@app.cell(hide_code=True)
def _(egresos_df, mo, pl):
    _alcs = (
        egresos_df.filter(pl.col("desc_unidad_responsable").str.starts_with("Alcaldía"))
                  .select("desc_unidad_responsable")
                  .unique()
                  .sort("desc_unidad_responsable")
                  .to_series().to_list()
    )
    alcaldia_pick = mo.ui.dropdown(
        options=["Toda la CDMX"] + _alcs,
        value="Toda la CDMX",
        label="🎯 Alcaldía",
    )
    return (alcaldia_pick,)


@app.cell(hide_code=True)
def _(alcaldia_pick, mo, year_pick):
    mo.hstack([year_pick, alcaldia_pick], justify="start", gap=2)
    return


@app.cell(hide_code=True)
def _(
    alcaldia_pick, egresos_df, fmt_mxn, has_ejercido, ingresos_raw,
    mo, pl, year_pick,
):
    _year = year_pick.value

    _ing_anual = ingresos_raw.filter(
        (pl.col("ciclo") == _year) & (pl.col("periodo") == "Anual")
    )["monto_estimado"].sum()
    _ing_actual_df = ingresos_raw.filter(
        (pl.col("ciclo") == _year) & (pl.col("periodo") == "Cuenta Pública")
    )
    _ing_actual = _ing_actual_df["monto_recaudado"].sum()

    _eg = egresos_df
    if alcaldia_pick.value != "Toda la CDMX":
        _eg = _eg.filter(pl.col("desc_unidad_responsable") == alcaldia_pick.value)
    _eg_plan = _eg["_budget"].sum()
    _eg_spent = _eg["_spent"].sum()
    _eg_pct = (_eg_spent / _eg_plan * 100) if has_ejercido and _eg_plan > 0 else None

    def _kpi(label, value, accent, sub=None):
        sub_html = f'<div style="font-size:10px;color:#64748B;margin-top:3px;letter-spacing:0.5px;">{sub}</div>' if sub else ""
        return f"""
        <div style="
            background:white;border:1px solid #E2E8F0;border-left:4px solid {accent};
            border-radius:10px;padding:16px 20px;flex:1;min-width:180px;
            box-shadow:0 1px 3px rgba(15,23,42,0.04);
        ">
            <div style="font-size:10px;color:#64748B;letter-spacing:1.5px;text-transform:uppercase;font-weight:600;">{label}</div>
            <div style="font-size:24px;font-weight:700;color:#0F172A;margin-top:4px;letter-spacing:-0.5px;">{value}</div>
            {sub_html}
        </div>
        """

    _cards = [
        _kpi("Ingresos planeados", fmt_mxn(_ing_anual), "#9F2241", sub="Ley de Ingresos"),
    ]
    if _ing_actual > 0:
        _delta = (_ing_actual / _ing_anual - 1) * 100 if _ing_anual else 0
        _cards.append(_kpi("Ingresos recaudados", fmt_mxn(_ing_actual), "#00A489",
                          sub=f"Cuenta Pública · Δ {_delta:+.1f}%"))
    else:
        _cards.append(_kpi("Ingresos recaudados", "—", "#CBD5E1", sub="año en curso"))

    _alc_suffix = "" if alcaldia_pick.value == "Toda la CDMX" else f" · {alcaldia_pick.value}"
    _cards.append(_kpi("Presupuesto de egresos", fmt_mxn(_eg_plan), "#EC6730", sub=f"aprobado{_alc_suffix}"))

    if _eg_pct is not None:
        _cards.append(_kpi("Ejecución", f"{_eg_pct:.1f}%", "#6C4A7E", sub="ejercido / modificado"))

    mo.md(f'<div style="display:flex;gap:12px;flex-wrap:wrap;margin:14px 0 20px;">{"".join(_cards)}</div>')
    return


@app.cell
def _(
    SOURCE_COLORS, SOURCE_ORDER, alcaldia_pick, fmt_mxn, go, ingresos_raw,
    mo, pl, year_pick,
):
    _year = year_pick.value
    _anual = ingresos_raw.filter((pl.col("ciclo") == _year) & (pl.col("periodo") == "Anual"))
    _cp    = ingresos_raw.filter((pl.col("ciclo") == _year) & (pl.col("periodo") == "Cuenta Pública"))

    _use = _cp if _cp.height > 0 and _cp["monto_recaudado"].sum() > 0 else _anual
    _amount_col = "monto_recaudado" if _use is _cp else "monto_estimado"
    _label = "recaudado" if _use is _cp else "planeado"

    _by_bucket = (
        _use.group_by("_bucket")
            .agg(pl.col(_amount_col).sum().alias("monto"))
            .filter(pl.col("monto") > 0)
            .to_pandas()
            .set_index("_bucket")
            .reindex(SOURCE_ORDER)
            .dropna()
            .reset_index()
    )
    _total = _by_bucket["monto"].sum() or 1

    _rows = []
    for _, _r in _by_bucket.sort_values("monto", ascending=False).iterrows():
        _pct = _r["monto"] / _total * 100
        _color = SOURCE_COLORS[_r["_bucket"]]
        _rows.append(f"""
        <div style="margin-bottom:14px;">
            <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px;">
                <span style="font-size:13px;color:#0F172A;font-weight:600;">
                    <span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:{_color};margin-right:8px;vertical-align:middle;"></span>
                    {_r['_bucket']}
                </span>
                <span style="font-size:13px;color:#475569;">{fmt_mxn(_r['monto'])} · {_pct:.0f}%</span>
            </div>
            <div style="background:#F1F5F9;height:6px;border-radius:3px;overflow:hidden;">
                <div style="background:{_color};width:{_pct}%;height:100%;"></div>
            </div>
        </div>
        """)

    _alc_caption = ""
    if alcaldia_pick.value != "Toda la CDMX":
        _alc_caption = (
            '<div style="margin:8px 0 14px;padding:8px 12px;background:#F1F5F9;border-radius:6px;'
            'font-size:11px;color:#475569;letter-spacing:0.5px;">'
            f'ℹ️ Los ingresos se recaudan para <b>toda la CDMX</b>, antes de distribuir a las alcaldías.'
            '</div>'
        )

    _left = mo.md(f"""
    <div style="padding:22px 24px;background:white;border:1px solid #E2E8F0;border-radius:14px;">
        <div style="font-size:11px;color:#64748B;letter-spacing:1.8px;text-transform:uppercase;font-weight:600;">Acto I · Entran</div>
        <div style="font-size:26px;font-weight:700;color:#0F172A;margin-top:4px;line-height:1.15;letter-spacing:-0.5px;">
            {fmt_mxn(_total)} {_label} en {_year}
        </div>
        {_alc_caption}
        <div style="font-size:13px;color:#475569;margin:8px 0 18px;line-height:1.5;">
            De cada peso público, ~9 de cada 10 vienen de impuestos locales y transferencias federales.
            Lo demás son fees, deuda y empresas paraestatales (Metro, SAPA, etc.).
        </div>
        {''.join(_rows)}
    </div>
    """)

    _fig = go.Figure(go.Pie(
        labels=_by_bucket["_bucket"],
        values=_by_bucket["monto"],
        hole=0.55,
        marker=dict(colors=[SOURCE_COLORS[b] for b in _by_bucket["_bucket"]],
                    line=dict(color="white", width=2)),
        textinfo="percent",
        textfont=dict(size=13, color="white", family="Inter"),
        hovertemplate="<b>%{label}</b><br>%{customdata}<br>%{percent}<extra></extra>",
        customdata=[fmt_mxn(v) for v in _by_bucket["monto"]],
        sort=False,
    ))
    _fig.update_layout(
        height=400,
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02,
                    font=dict(size=11)),
        paper_bgcolor="rgba(0,0,0,0)",
        annotations=[dict(
            text=f"<b style='font-size:18px;color:#0F172A'>{fmt_mxn(_total)}</b><br><span style='font-size:10px;color:#64748B;letter-spacing:1px'>TOTAL {_year}</span>",
            x=0.5, y=0.5, showarrow=False, align="center",
        )],
        font=dict(family="Inter, system-ui, sans-serif"),
    )

    _transition = mo.md(
        f'<div style="margin:18px 0 0;padding:14px 18px;background:#FEF2F2;border-left:3px solid #9F2241;border-radius:6px;font-size:13px;color:#7F1D1D;line-height:1.5;">'
        f'<b>→ Acto II.</b> De estos <b>{fmt_mxn(_total)}</b>, ¿cuánto se prometió gastar — y cuánto se ejerció realmente?'
        f'</div>'
    )

    act1_content = mo.vstack([
        mo.hstack([_left, mo.ui.plotly(_fig)], justify="start", gap=1.5, widths=[1, 1], wrap=True),
        _transition,
    ])
    return (act1_content,)


@app.cell
def _(alcaldia_pick, egresos_df, fmt_mxn, go, has_ejercido, mo, pl, year_pick):
    _year = year_pick.value
    _eg = egresos_df
    if alcaldia_pick.value != "Toda la CDMX":
        _eg = _eg.filter(pl.col("desc_unidad_responsable") == alcaldia_pick.value)

    _top = (
        _eg.with_columns(pl.col("desc_capitulo").fill_null("Sin clasificar"))
            .group_by("desc_capitulo")
            .agg([
                pl.col("_budget").sum().alias("budget"),
                pl.col("_spent").sum().alias("spent"),
            ])
            .filter(pl.col("budget") > 0)
            .sort("budget", descending=True)
            .head(12)
            .to_pandas()
            .iloc[::-1]
            .reset_index(drop=True)
    )
    _top["exec_pct"] = (_top["spent"] / _top["budget"].where(_top["budget"] > 0, 1) * 100).fillna(0)

    def _exec_color(pct):
        if pct >= 85: return "#059669"
        if pct >= 60: return "#D97706"
        return "#DC2626"

    _fig = go.Figure()
    _fig.add_trace(go.Bar(
        y=_top["desc_capitulo"], x=_top["budget"], orientation="h",
        marker=dict(color="#E2E8F0"), width=0.78,
        name="Aprobado / Modificado",
        hovertemplate="<b>%{y}</b><br>Plan: %{customdata}<extra></extra>",
        customdata=[fmt_mxn(v) for v in _top["budget"]],
    ))
    if has_ejercido:
        _fig.add_trace(go.Bar(
            y=_top["desc_capitulo"], x=_top["spent"], orientation="h",
            marker=dict(color=[_exec_color(p) for p in _top["exec_pct"]]),
            width=0.42, name="Ejercido",
            hovertemplate="<b>%{y}</b><br>Ejercido: %{customdata}<extra></extra>",
            customdata=[fmt_mxn(v) for v in _top["spent"]],
        ))
        _fig.add_trace(go.Scatter(
            y=_top["desc_capitulo"], x=_top["budget"],
            mode="text",
            text=[f"  {p:.0f}%" for p in _top["exec_pct"]],
            textposition="middle right",
            textfont=dict(size=11, family="Inter",
                          color=[_exec_color(p) for p in _top["exec_pct"]]),
            showlegend=False, hoverinfo="skip", cliponaxis=False,
        ))

    _max_x = float(_top["budget"].max()) if len(_top) else 1
    _fig.update_layout(
        barmode="overlay", bargap=0.35,
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9", tickformat=".2s", title="",
                   range=[0, _max_x * 1.14]),
        yaxis=dict(title="", tickfont=dict(size=11), automargin=True),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, xanchor="left",
                    bgcolor="rgba(0,0,0,0)"),
        height=520, margin=dict(l=10, r=40, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif", size=12),
    )

    _total_budget = _top["budget"].sum()
    _total_spent = _top["spent"].sum()
    _global_pct = (_total_spent / _total_budget * 100) if _total_budget and has_ejercido else 0

    if has_ejercido:
        _subejerc = _top[_top["exec_pct"] < 90].sort_values("exec_pct").head(3)
        _sub_rows = "".join([
            f'<li style="margin-bottom:6px;"><b>{_r["desc_capitulo"]}</b> — {_r["exec_pct"]:.0f}% · {fmt_mxn(_r["spent"])} de {fmt_mxn(_r["budget"])}</li>'
            for _, _r in _subejerc.iterrows()
        ]) or '<li style="color:#64748B;">Ningún capítulo con subejercicio notable.</li>'
        _hero_stat = f"<b>{_global_pct:.0f}%</b> del presupuesto se ejerció"
        _extra = f"""
        <div style="margin-top:16px;font-size:12px;color:#475569;">
            <div style="font-size:11px;color:#64748B;letter-spacing:1.2px;text-transform:uppercase;font-weight:600;margin-bottom:8px;">Top 3 capítulos con menor ejecución</div>
            <ul style="margin:0;padding-left:16px;line-height:1.5;">{_sub_rows}</ul>
        </div>
        """
    else:
        _hero_stat = f"<b>{fmt_mxn(_total_budget)}</b> presupuestados"
        _extra = '<div style="margin-top:16px;font-size:12px;color:#64748B;">Año en curso — aún no hay datos de ejecución.</div>'

    _alc_scope = (" para toda la CDMX" if alcaldia_pick.value == "Toda la CDMX"
                  else f" en {alcaldia_pick.value}")

    _left = mo.md(f"""
    <div style="padding:22px 24px;background:white;border:1px solid #E2E8F0;border-radius:14px;">
        <div style="font-size:11px;color:#64748B;letter-spacing:1.8px;text-transform:uppercase;font-weight:600;">Acto II · Se prometen</div>
        <div style="font-size:26px;font-weight:700;color:#0F172A;margin-top:4px;line-height:1.15;letter-spacing:-0.5px;">
            {_hero_stat} en {_year}{_alc_scope}
        </div>
        <div style="font-size:13px;color:#475569;margin:10px 0 0;line-height:1.5;">
            Cada barra es un capítulo del gasto: servicios personales (nómina), obra pública,
            materiales, transferencias, etc. <b>Gris</b> es lo programado;
            <b style="color:#9F2241">guinda</b> lo ejercido.
            <span style="color:#059669">Verde</span> ≥ 85%,
            <span style="color:#D97706">ámbar</span> 60–85%,
            <span style="color:#DC2626">rojo</span> &lt; 60%.
        </div>
        {_extra}
    </div>
    """)

    if has_ejercido:
        _next = f"De los <b>{fmt_mxn(_total_spent)}</b> ejercidos, ¿quiénes los recibieron como contratos?"
    else:
        _next = "Cuando haya datos de ejecución, veremos quién recibió ese gasto como contratos."

    _transition = mo.md(
        f'<div style="margin:18px 0 0;padding:14px 18px;background:#FEF2F2;border-left:3px solid #9F2241;border-radius:6px;font-size:13px;color:#7F1D1D;line-height:1.5;">'
        f'<b>→ Acto III.</b> {_next}'
        f'</div>'
    )

    act2_content = mo.vstack([
        mo.hstack([_left, mo.ui.plotly(_fig)], justify="start", gap=1.5, widths=[1, 2], wrap=True),
        _transition,
    ])
    return (act2_content,)


@app.cell
def _(alcaldia_pick, fmt_int, fmt_mxn, go, mo, pl, rally_raw, year_pick):
    _year = year_pick.value

    _rally = rally_raw.filter(
        pl.col("ciclo").is_between(2013, 2017)
        & pl.col("rfc_contratista").is_not_null()
        & (pl.col("rfc_contratista") != "")
        & ~pl.col("rfc_contratista").str.to_lowercase().str.contains("no reportó")
        & (pl.col("monto_ejercido") > 0)
    )

    if alcaldia_pick.value != "Toda la CDMX":
        _bare = alcaldia_pick.value.replace("Alcaldía ", "").strip()
        _rally = _rally.filter(
            pl.col("desc_alcaldia").str.contains(_bare, literal=True)
        )

    _agg = (
        _rally.group_by(["rfc_contratista"])
              .agg([
                  pl.col("monto_ejercido").sum().alias("monto"),
                  pl.len().alias("proyectos"),
                  pl.col("contratista").mode().first().alias("nombre"),
                  pl.col("desc_unidad_responsable").n_unique().alias("agencias"),
              ])
              .sort("monto", descending=True)
              .to_pandas()
    )

    if _agg.empty:
        act3_content = mo.md(f"""
        <div style="padding:30px 32px;background:#F8FAFC;border:1.5px dashed #CBD5E1;border-radius:14px;text-align:center;">
            <div style="font-size:34px;margin-bottom:8px;">🚧</div>
            <div style="font-size:18px;font-weight:700;color:#0F172A;">Sin contratos con esta alcaldía</div>
            <div style="font-size:13px;color:#64748B;margin-top:8px;line-height:1.55;">
                {alcaldia_pick.value} no aparece en el Rally 2013–2017, o sus filas no tienen RFC.
            </div>
        </div>
        """)
    else:
        _total_monto = _agg["monto"].sum()
        _top10 = _agg.head(10)
        _top10_monto = _top10["monto"].sum()
        _top10_pct = (_top10_monto / _total_monto * 100) if _total_monto else 0

        _rows = []
        for _i, _r in _top10.iterrows():
            _share = _r["monto"] / _total_monto * 100 if _total_monto else 0
            _name = str(_r["nombre"] or "(nombre no reportado)").strip()[:48]
            _rows.append(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid #F1F5F9;">
                <div style="flex:1;min-width:0;">
                    <div style="font-size:12px;color:#9F2241;font-weight:600;letter-spacing:0.5px;">#{_i+1}</div>
                    <div style="font-size:13px;font-weight:600;color:#0F172A;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" title="{_name}">{_name}</div>
                    <div style="font-size:11px;color:#64748B;">{fmt_int(_r['proyectos'])} obras · {fmt_int(_r['agencias'])} agencias</div>
                </div>
                <div style="text-align:right;padding-left:12px;">
                    <div style="font-size:13px;font-weight:700;color:#0F172A;">{fmt_mxn(_r['monto'])}</div>
                    <div style="font-size:11px;color:#9F2241;">{_share:.1f}%</div>
                </div>
            </div>
            """)

        _alc_scope = (" en toda la CDMX" if alcaldia_pick.value == "Toda la CDMX"
                      else f" en {alcaldia_pick.value}")

        _scope_note = (
            f'<div style="margin:8px 0 14px;padding:8px 12px;background:#F1F5F9;border-radius:6px;font-size:11px;color:#475569;letter-spacing:0.5px;">'
            f'ℹ️ Datos agregados <b>2013–2017</b> · el Rally 2018 dejó de reportar RFCs. Esta vista no cambia con el año.'
            f'</div>'
        )

        _left = mo.md(f"""
        <div style="padding:22px 24px;background:white;border:1px solid #E2E8F0;border-radius:14px;">
            <div style="font-size:11px;color:#64748B;letter-spacing:1.8px;text-transform:uppercase;font-weight:600;">Acto III · Aterrizan</div>
            <div style="font-size:26px;font-weight:700;color:#0F172A;margin-top:4px;line-height:1.15;letter-spacing:-0.5px;">
                Las 10 empresas top concentraron <span style="color:#9F2241">{_top10_pct:.0f}%</span>
            </div>
            <div style="font-size:13px;color:#475569;margin:10px 0 14px;line-height:1.5;">
                De <b>{fmt_mxn(_total_monto)}</b> en contratos georreferenciados{_alc_scope}
                · <b>{fmt_int(_agg.shape[0])}</b> contratistas únicos.
            </div>
            {_scope_note}
            {''.join(_rows)}
        </div>
        """)

        _tm = _agg.head(30).copy()
        _tm["label"] = _tm.apply(
            lambda _row: f"{str(_row['nombre'] or 'N/A')[:32]}<br><b>{fmt_mxn(_row['monto'])}</b>", axis=1,
        )

        _colors = [
            f"rgba(159,34,65,{0.35 + 0.55 * (1 - _i/len(_tm))})"
            for _i in range(len(_tm))
        ]

        _fig = go.Figure(go.Treemap(
            labels=_tm["label"],
            parents=[""] * len(_tm),
            values=_tm["monto"],
            marker=dict(colors=_colors, line=dict(color="white", width=2)),
            textinfo="label",
            textfont=dict(size=11, family="Inter", color="white"),
            hovertemplate="<b>%{label}</b><br>%{customdata} contratos<extra></extra>",
            customdata=_tm["proyectos"],
            branchvalues="total",
        ))
        _fig.update_layout(
            height=560,
            margin=dict(l=6, r=6, t=6, b=6),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, system-ui, sans-serif"),
        )

        act3_content = mo.vstack([
            mo.hstack([_left, mo.ui.plotly(_fig)], justify="start", gap=1.5, widths=[1, 1], wrap=True),
        ])
    return (act3_content,)


@app.cell
def _(
    alcaldia_pick, egresos_df, fmt_mxn, has_ejercido, ingresos_raw, mo, pl,
    year_pick,
):
    _year = year_pick.value

    _ing = ingresos_raw.filter(
        (pl.col("ciclo") == _year) & (pl.col("periodo").is_in(["Anual", "Cuenta Pública"]))
    )
    _eg = egresos_df
    if alcaldia_pick.value != "Toda la CDMX":
        _eg = _eg.filter(pl.col("desc_unidad_responsable") == alcaldia_pick.value)

    _ing_total = (
        _ing.filter(pl.col("periodo") == "Cuenta Pública")["monto_recaudado"].sum()
        or _ing.filter(pl.col("periodo") == "Anual")["monto_estimado"].sum()
    )
    _eg_plan = _eg["_budget"].sum()
    _eg_spent = _eg["_spent"].sum()
    _pct_spent = (_eg_spent / _ing_total * 100) if _ing_total and has_ejercido else 0

    act4_content = mo.md(f"""
    <div style="padding:28px 32px;background:white;border:1px solid #E2E8F0;border-radius:14px;">
        <div style="font-size:11px;color:#64748B;letter-spacing:1.8px;text-transform:uppercase;font-weight:600;">Acto IV · Explora</div>
        <div style="font-size:26px;font-weight:700;color:#0F172A;margin-top:4px;line-height:1.15;letter-spacing:-0.5px;">
            {_year} · {alcaldia_pick.value}
        </div>
        <div style="font-size:13px;color:#475569;margin:12px 0 22px;line-height:1.55;">
            Combina el selector de <b>Año</b> y <b>Alcaldía</b> de arriba. Los 3 actos anteriores
            (Entran · Se prometen · Aterrizan) responden instantáneamente.
        </div>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;">
            <div style="padding:16px;background:#FEF2F2;border-radius:10px;border-left:3px solid #9F2241;">
                <div style="font-size:10px;letter-spacing:1.5px;color:#7F1D1D;text-transform:uppercase;font-weight:600;">① Ingresos</div>
                <div style="font-size:22px;font-weight:700;color:#0F172A;margin-top:4px;">{fmt_mxn(_ing_total)}</div>
                <div style="font-size:11px;color:#475569;">Ingresos CDMX totales</div>
            </div>
            <div style="padding:16px;background:#FEF3C7;border-radius:10px;border-left:3px solid #D97706;">
                <div style="font-size:10px;letter-spacing:1.5px;color:#78350F;text-transform:uppercase;font-weight:600;">② Egresos planeados</div>
                <div style="font-size:22px;font-weight:700;color:#0F172A;margin-top:4px;">{fmt_mxn(_eg_plan)}</div>
                <div style="font-size:11px;color:#475569;">Presupuesto {alcaldia_pick.value}</div>
            </div>
            <div style="padding:16px;background:#F0FDF4;border-radius:10px;border-left:3px solid #059669;">
                <div style="font-size:10px;letter-spacing:1.5px;color:#14532D;text-transform:uppercase;font-weight:600;">Ejercido</div>
                <div style="font-size:22px;font-weight:700;color:#0F172A;margin-top:4px;">{fmt_mxn(_eg_spent) if has_ejercido else '—'}</div>
                <div style="font-size:11px;color:#475569;">{_pct_spent:.1f}% del ingreso total</div>
            </div>
        </div>
        <div style="margin-top:20px;font-size:13px;color:#475569;line-height:1.55;">
            💡 <b>Tip:</b> compara años recientes (2022–2023) con años más antiguos (2018–2019)
            para ver cómo ha crecido el presupuesto. Cambia de alcaldía para ver la distribución
            territorial.
        </div>
    </div>
    """)
    return (act4_content,)


@app.cell(hide_code=True)
def _(act1_content, act2_content, act3_content, act4_content, mo):
    mo.ui.tabs(
        {
            "① Entran":       act1_content,
            "② Se prometen":  act2_content,
            "③ Aterrizan":    act3_content,
            "④ Explora":      act4_content,
        },
        value="① Entran",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ---
        <div style="text-align:center;color:#64748B;font-size:12px;padding:14px 0 28px;line-height:1.6;">
        <b>La ruta de tu peso</b> · construido en Claude Mexico City Lab 2026<br/>
        Datos: <a href="https://datos.cdmx.gob.mx" style="color:#9F2241;">Portal de Datos Abiertos CDMX</a>
        · Marimo + Polars + Plotly
        </div>
        """
    )
    return


if __name__ == "__main__":
    app.run()
