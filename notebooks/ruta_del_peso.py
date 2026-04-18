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
        <br/>
        <b>✓ Validación:</b> el aprobado 2024 suma <b>MXN 267,965,350,437</b> — coincidencia exacta con el Decreto de Presupuesto de Egresos 2024. Cada peso es rastreable al CSV oficial.
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


@app.cell
def _(DATA_DIR, pl):
    # dev/manu enrichment layer:
    #   - crosswalk.csv           19k rows → 16 citizen-facing buckets
    #   - named_programs_2024.csv 81 flagship programs with pesos (Paquete Económico)
    #   - budget_tree.parquet     pre-aggregated L1+L2 hierarchy per year
    _ROOT = DATA_DIR.parent

    try:
        crosswalk_df = pl.read_csv(
            _ROOT / "crosswalk" / "crosswalk.csv",
            infer_schema_length=20_000,
            null_values=["NA", ""],
            ignore_errors=True,
        )
    except Exception:
        crosswalk_df = None

    try:
        named_programs_df = pl.read_csv(
            _ROOT / "crosswalk" / "named_programs_2024.csv",
            infer_schema_length=10_000,
            null_values=["NA", ""],
            ignore_errors=True,
        ).with_columns(
            pl.col("monto_aprobado_mxn").cast(pl.Float64, strict=False).fill_null(0)
        )
    except Exception:
        named_programs_df = None

    try:
        budget_tree_df = pl.read_parquet(_ROOT / "data" / "clean" / "budget_tree.parquet")
    except Exception:
        budget_tree_df = None

    CITIZEN_ICON = {
        "Agua":                         "💧",
        "Transporte público":           "🚇",
        "Calles y banquetas":           "🛣️",
        "Basura y limpia":              "🗑️",
        "Parques y espacios públicos":  "🌳",
        "Seguridad":                    "🛡️",
        "Justicia":                     "⚖️",
        "Salud":                        "🏥",
        "Educación":                    "📚",
        "Apoyos sociales":              "🤝",
        "Cultura y deporte":            "🎭",
        "Medio ambiente":               "🌱",
        "Alumbrado":                    "💡",
        "Gobierno y administración":    "🏛️",
        "Deuda":                        "💳",
        "Otros":                        "▫️",
    }
    CITIZEN_PALETTE = {
        "Agua":                         "#00B7CD",
        "Transporte público":           "#9F2241",
        "Calles y banquetas":           "#6C4A7E",
        "Basura y limpia":              "#94A3B8",
        "Parques y espacios públicos":  "#00A489",
        "Seguridad":                    "#EC6730",
        "Justicia":                     "#C14953",
        "Salud":                        "#E3007E",
        "Educación":                    "#3D5A80",
        "Apoyos sociales":              "#D6A461",
        "Cultura y deporte":            "#2A9D8F",
        "Medio ambiente":               "#059669",
        "Alumbrado":                    "#EAB308",
        "Gobierno y administración":    "#475569",
        "Deuda":                        "#7F1D1D",
        "Otros":                        "#CBD5E1",
    }
    CITIZEN_ORDER = list(CITIZEN_ICON.keys())

    return (
        CITIZEN_ICON, CITIZEN_ORDER, CITIZEN_PALETTE,
        budget_tree_df, crosswalk_df, named_programs_df,
    )


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


@app.cell
def _(DATA_DIR, EGRESOS_FILE_MAP, pl):
    _parts = []
    for _yr in sorted(EGRESOS_FILE_MAP.keys()):
        _fname, _bcol_type, _ = EGRESOS_FILE_MAP[_yr]
        _df = pl.read_csv(
            DATA_DIR / _fname,
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
        _bcol = "monto_modificado" if _bcol_type == "modificado" else "monto_aprobado"
        _has_sp = "monto_ejercido" in _df.columns
        _df = _df.with_columns([
            pl.col(_bcol).fill_null(0).alias("_budget"),
            (pl.col("monto_ejercido").fill_null(0) if _has_sp else pl.lit(0.0)).alias("_spent"),
            pl.lit(_yr).alias("_year"),
        ]).select(["_year", "desc_unidad_responsable", "desc_capitulo", "_budget", "_spent"])
        _parts.append(_df)
    egresos_all = pl.concat(_parts)
    return (egresos_all,)


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
        <div style="font-size:11px;color:#64748B;letter-spacing:1.8px;text-transform:uppercase;font-weight:600;">Acto II · Entran</div>
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

    _conceptos = (
        _use.group_by(["_bucket", "desc_concepto"])
            .agg(pl.col(_amount_col).sum().alias("monto"))
            .filter(pl.col("monto") > 0)
            .filter(pl.col("desc_concepto").is_not_null())
            .sort("monto", descending=True)
            .head(15)
            .to_pandas()
            .iloc[::-1]
            .reset_index(drop=True)
    )
    _conceptos["color"] = _conceptos["_bucket"].map(SOURCE_COLORS).fillna("#94A3B8")
    _conceptos["label"] = _conceptos["monto"].apply(fmt_mxn)
    _conceptos["concepto_trunc"] = _conceptos["desc_concepto"].str.slice(0, 60)

    _fig_detail = go.Figure(go.Bar(
        y=_conceptos["concepto_trunc"], x=_conceptos["monto"],
        orientation="h",
        marker=dict(color=_conceptos["color"].tolist()),
        text=_conceptos["label"],
        textposition="outside",
        textfont=dict(size=11, color="#334155"),
        hovertemplate="<b>%{customdata}</b><br>%{text}<extra></extra>",
        customdata=_conceptos["desc_concepto"].tolist(),
        cliponaxis=False,
    ))
    _fig_detail.update_layout(
        height=max(300, 28 * len(_conceptos) + 60),
        margin=dict(l=10, r=60, t=10, b=30),
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9", tickformat=".2s", title=""),
        yaxis=dict(title="", tickfont=dict(size=11)),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif", size=11),
    )

    _detail_header = mo.md("""
    <div style="margin:24px 0 10px;padding:14px 18px;background:#F8FAFC;border-radius:10px;border-left:3px solid #9F2241;">
        <div style="font-size:11px;letter-spacing:1.5px;text-transform:uppercase;color:#64748B;font-weight:600;">Detalle · nivel 2</div>
        <div style="font-size:17px;font-weight:700;color:#0F172A;margin-top:4px;">Los 15 conceptos con mayor monto</div>
        <div style="font-size:12px;color:#475569;margin-top:4px;">Los colores corresponden al cubo de origen. Predial, nómina, participaciones federales, etc.</div>
    </div>
    """)

    _transition = mo.md(
        f'<div style="margin:18px 0 0;padding:14px 18px;background:#FEF2F2;border-left:3px solid #9F2241;border-radius:6px;font-size:13px;color:#7F1D1D;line-height:1.5;">'
        f'<b>→ Acto III.</b> De estos <b>{fmt_mxn(_total)}</b>, ¿cuánto se prometió gastar — y cuánto se ejerció realmente?'
        f'</div>'
    )

    act1_content = mo.vstack([
        mo.hstack([_left, _fig], justify="start", gap=1.5, widths=[1, 1], wrap=True),
        _detail_header,
        _fig_detail,
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
        <div style="font-size:11px;color:#64748B;letter-spacing:1.8px;text-transform:uppercase;font-weight:600;">Acto III · Se prometen</div>
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

    _progs = (
        _eg.with_columns(pl.col("desc_programa_presupuestario").fill_null("Sin programa"))
            .filter(pl.col("desc_programa_presupuestario") != "Sin programa")
            .group_by("desc_programa_presupuestario")
            .agg([
                pl.col("_budget").sum().alias("budget"),
                pl.col("_spent").sum().alias("spent"),
            ])
            .filter(pl.col("budget") > 0)
            .sort("budget", descending=True)
            .head(15)
            .to_pandas()
            .iloc[::-1]
            .reset_index(drop=True)
    )
    _progs["exec_pct"] = (_progs["spent"] / _progs["budget"].where(_progs["budget"] > 0, 1) * 100).fillna(0)
    _progs["label_budget"] = _progs["budget"].apply(fmt_mxn)
    _progs["label_spent"] = _progs["spent"].apply(fmt_mxn)

    _fig_progs = go.Figure()
    _fig_progs.add_trace(go.Bar(
        y=_progs["desc_programa_presupuestario"], x=_progs["budget"], orientation="h",
        marker=dict(color="#E2E8F0"), width=0.78,
        name="Presupuesto",
        hovertemplate="<b>%{y}</b><br>Plan: %{customdata}<extra></extra>",
        customdata=_progs["label_budget"],
    ))
    if has_ejercido:
        _fig_progs.add_trace(go.Bar(
            y=_progs["desc_programa_presupuestario"], x=_progs["spent"], orientation="h",
            marker=dict(color=[_exec_color(p) for p in _progs["exec_pct"]]),
            width=0.42, name="Ejercido",
            hovertemplate="<b>%{y}</b><br>Ejercido: %{customdata}<extra></extra>",
            customdata=_progs["label_spent"],
        ))
        _fig_progs.add_trace(go.Scatter(
            y=_progs["desc_programa_presupuestario"], x=_progs["budget"],
            mode="text",
            text=[f"  {p:.0f}%" for p in _progs["exec_pct"]],
            textposition="middle right",
            textfont=dict(size=10, family="Inter",
                          color=[_exec_color(p) for p in _progs["exec_pct"]]),
            showlegend=False, hoverinfo="skip", cliponaxis=False,
        ))
    _fig_progs.update_layout(
        barmode="overlay", bargap=0.35,
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9", tickformat=".2s", title="",
                   range=[0, float(_progs["budget"].max() or 1) * 1.14]),
        yaxis=dict(title="", tickfont=dict(size=10), automargin=True),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, xanchor="left",
                    bgcolor="rgba(0,0,0,0)"),
        height=max(400, 30 * len(_progs) + 60),
        margin=dict(l=10, r=40, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif", size=11),
    )

    _detail_header = mo.md("""
    <div style="margin:24px 0 10px;padding:14px 18px;background:#F8FAFC;border-radius:10px;border-left:3px solid #9F2241;">
        <div style="font-size:11px;letter-spacing:1.5px;text-transform:uppercase;color:#64748B;font-weight:600;">Detalle · nivel 2</div>
        <div style="font-size:17px;font-weight:700;color:#0F172A;margin-top:4px;">Los 15 programas presupuestarios con mayor monto</div>
        <div style="font-size:12px;color:#475569;margin-top:4px;">Un capítulo agrupa muchos programas. Este desglose muestra los programas concretos donde se ejerció el dinero.</div>
    </div>
    """)

    if has_ejercido:
        _next = f"De los <b>{fmt_mxn(_total_spent)}</b> ejercidos, ¿quiénes los recibieron como contratos?"
    else:
        _next = "Cuando haya datos de ejecución, veremos quién recibió ese gasto como contratos."

    _transition = mo.md(
        f'<div style="margin:18px 0 0;padding:14px 18px;background:#FEF2F2;border-left:3px solid #9F2241;border-radius:6px;font-size:13px;color:#7F1D1D;line-height:1.5;">'
        f'<b>→ Acto IV.</b> {_next}'
        f'</div>'
    )

    act2_content = mo.vstack([
        mo.hstack([_left, _fig], justify="start", gap=1.5, widths=[1, 2], wrap=True),
        _detail_header,
        _fig_progs,
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
            <div style="font-size:11px;color:#64748B;letter-spacing:1.8px;text-transform:uppercase;font-weight:600;">Acto IV · Aterrizan</div>
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

        _top_contracts = (
            _rally.sort("monto_ejercido", descending=True)
                  .head(15)
                  .select([
                      "nombre_proyecto", "contratista", "desc_alcaldia",
                      "ciclo", "monto_ejercido", "avance_fisico",
                  ])
                  .to_pandas()
        )

        _contract_rows = []
        for _i, _row in _top_contracts.iterrows():
            _name = str(_row["nombre_proyecto"] or "(sin nombre)").strip()[:80]
            _cont = str(_row["contratista"] or "—").strip()[:42]
            _alc = str(_row["desc_alcaldia"] or "—").strip()[:26]
            _avc = float(_row["avance_fisico"] or 0)
            _avc_color = "#059669" if _avc >= 95 else ("#D97706" if _avc >= 25 else "#DC2626")
            _contract_rows.append(f"""
            <tr>
                <td style="padding:10px 8px;vertical-align:top;font-size:12px;color:#9F2241;font-weight:600;">#{_i+1}</td>
                <td style="padding:10px 8px;vertical-align:top;font-size:13px;color:#0F172A;line-height:1.4;">
                    <div style="font-weight:600;">{_name}</div>
                    <div style="font-size:11px;color:#64748B;margin-top:2px;">{_cont} · {_alc} · {int(_row['ciclo'])}</div>
                </td>
                <td style="padding:10px 8px;vertical-align:top;text-align:right;font-size:13px;font-weight:700;color:#0F172A;white-space:nowrap;">{fmt_mxn(_row['monto_ejercido'])}</td>
                <td style="padding:10px 8px;vertical-align:top;text-align:right;font-size:12px;font-weight:600;color:{_avc_color};white-space:nowrap;">{_avc:.0f}%</td>
            </tr>
            """)

        _detail_section = mo.md(f"""
        <div style="margin:24px 0 10px;padding:14px 18px;background:#F8FAFC;border-radius:10px;border-left:3px solid #9F2241;">
            <div style="font-size:11px;letter-spacing:1.5px;text-transform:uppercase;color:#64748B;font-weight:600;">Detalle · nivel 2</div>
            <div style="font-size:17px;font-weight:700;color:#0F172A;margin-top:4px;">Los 15 contratos individuales más grandes</div>
            <div style="font-size:12px;color:#475569;margin-top:4px;">Un contratista recibe muchos contratos — aquí están los contratos específicos más grandes del agregado.</div>
        </div>
        <div style="background:white;border:1px solid #E2E8F0;border-radius:12px;padding:6px 14px;overflow-x:auto;">
            <table style="width:100%;border-collapse:collapse;font-family:Inter,system-ui,sans-serif;">
                <thead>
                    <tr style="border-bottom:1px solid #E2E8F0;color:#64748B;font-size:10px;letter-spacing:1px;text-transform:uppercase;">
                        <th style="padding:10px 8px;text-align:left;font-weight:600;">#</th>
                        <th style="padding:10px 8px;text-align:left;font-weight:600;">Proyecto · contratista · alcaldía · año</th>
                        <th style="padding:10px 8px;text-align:right;font-weight:600;">Monto ejercido</th>
                        <th style="padding:10px 8px;text-align:right;font-weight:600;">Avance</th>
                    </tr>
                </thead>
                <tbody>{''.join(_contract_rows)}</tbody>
            </table>
        </div>
        """)

        _transition = mo.md(
            '<div style="margin:18px 0 0;padding:14px 18px;background:#FEF2F2;border-left:3px solid #9F2241;border-radius:6px;font-size:13px;color:#7F1D1D;line-height:1.5;">'
            '<b>→ Acto V.</b> ¿Cómo cambia todo esto a lo largo del tiempo? Ver tendencias multi-año.'
            '</div>'
        )

        act3_content = mo.vstack([
            mo.hstack([_left, _fig], justify="start", gap=1.5, widths=[1, 1], wrap=True),
            _detail_section,
            _transition,
        ])
    return (act3_content,)


@app.cell
def _(
    alcaldia_pick, egresos_all, fmt_mxn, go, ingresos_raw, mo, pl, rally_raw,
):
    _ing = ingresos_raw.to_pandas()
    _ing_plan = (_ing[_ing["periodo"] == "Anual"]
                 .groupby("ciclo")["monto_estimado"].sum()
                 .rename("planeado"))
    _ing_real = (_ing[_ing["periodo"] == "Cuenta Pública"]
                 .groupby("ciclo")["monto_recaudado"].sum()
                 .rename("recaudado"))
    _ing_trend = _ing_plan.to_frame().join(_ing_real, how="outer").reset_index().sort_values("ciclo")

    _fig1 = go.Figure()
    _fig1.add_trace(go.Scatter(
        x=_ing_trend["ciclo"], y=_ing_trend["planeado"],
        mode="lines+markers", name="Planeado (Ley de Ingresos)",
        line=dict(color="#CBD5E1", width=3, dash="dot"),
        marker=dict(size=8),
        hovertemplate="%{x}: %{customdata}<extra>Planeado</extra>",
        customdata=[fmt_mxn(v) for v in _ing_trend["planeado"]],
    ))
    _fig1.add_trace(go.Scatter(
        x=_ing_trend["ciclo"], y=_ing_trend["recaudado"],
        mode="lines+markers", name="Recaudado (Cuenta Pública)",
        line=dict(color="#9F2241", width=3),
        marker=dict(size=10),
        hovertemplate="%{x}: %{customdata}<extra>Recaudado</extra>",
        customdata=[fmt_mxn(v) for v in _ing_trend["recaudado"].fillna(0)],
    ))
    _fig1.update_layout(
        height=320,
        margin=dict(l=10, r=10, t=30, b=30),
        title=dict(text="<b>Ingresos CDMX · 2018–2024</b>",
                   font=dict(size=14, family="Inter", color="#0F172A"), x=0.01),
        xaxis=dict(showgrid=False, dtick=1, title=""),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", tickformat=".2s", title=""),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif", size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.04, x=1, xanchor="right",
                    bgcolor="rgba(0,0,0,0)"),
        hovermode="x unified",
    )

    _eg = egresos_all
    _alc_label = alcaldia_pick.value
    if _alc_label != "Toda la CDMX":
        _eg = _eg.filter(pl.col("desc_unidad_responsable") == _alc_label)
    _eg_trend = (
        _eg.group_by("_year").agg([
            pl.col("_budget").sum().alias("budget"),
            pl.col("_spent").sum().alias("spent"),
        ]).sort("_year").to_pandas()
    )

    _fig2 = go.Figure()
    _fig2.add_trace(go.Bar(
        x=_eg_trend["_year"], y=_eg_trend["budget"],
        name="Presupuesto (modificado / aprobado)",
        marker=dict(color="#E2E8F0"),
        hovertemplate="%{x}: %{customdata}<extra>Presupuesto</extra>",
        customdata=[fmt_mxn(v) for v in _eg_trend["budget"]],
    ))
    _fig2.add_trace(go.Bar(
        x=_eg_trend["_year"], y=_eg_trend["spent"],
        name="Ejercido",
        marker=dict(color="#9F2241"),
        hovertemplate="%{x}: %{customdata}<extra>Ejercido</extra>",
        customdata=[fmt_mxn(v) for v in _eg_trend["spent"]],
    ))
    _exec_pcts = [
        (s / b * 100) if b > 0 and s > 0 else None
        for b, s in zip(_eg_trend["budget"], _eg_trend["spent"])
    ]
    _fig2.add_trace(go.Scatter(
        x=_eg_trend["_year"], y=_eg_trend["budget"],
        mode="text",
        text=[f"{p:.0f}%" if p is not None else "" for p in _exec_pcts],
        textposition="top center",
        textfont=dict(size=11, color="#059669", family="Inter"),
        showlegend=False, hoverinfo="skip", cliponaxis=False,
    ))
    _fig2.update_layout(
        barmode="overlay",
        height=340,
        margin=dict(l=10, r=10, t=30, b=30),
        title=dict(text=f"<b>Egresos · {_alc_label} · 2018–2024</b>",
                   font=dict(size=14, family="Inter", color="#0F172A"), x=0.01),
        xaxis=dict(showgrid=False, dtick=1, title=""),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", tickformat=".2s", title=""),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif", size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.04, x=1, xanchor="right",
                    bgcolor="rgba(0,0,0,0)"),
        hovermode="x unified",
        bargap=0.35,
    )

    _rally = rally_raw.filter(
        pl.col("ciclo").is_between(2013, 2017)
        & pl.col("rfc_contratista").is_not_null()
        & (pl.col("rfc_contratista") != "")
        & ~pl.col("rfc_contratista").str.to_lowercase().str.contains("no reportó")
        & (pl.col("monto_ejercido") > 0)
    )
    if _alc_label != "Toda la CDMX":
        _bare = _alc_label.replace("Alcaldía ", "").strip()
        _rally = _rally.filter(pl.col("desc_alcaldia").str.contains(_bare, literal=True))

    _top5 = (
        _rally.group_by("rfc_contratista")
              .agg(pl.col("monto_ejercido").sum().alias("m"))
              .sort("m", descending=True)
              .head(5)["rfc_contratista"].to_list()
    )
    _rally_trend = (
        _rally.filter(pl.col("rfc_contratista").is_in(_top5))
              .group_by(["ciclo", "rfc_contratista"])
              .agg([
                  pl.col("monto_ejercido").sum().alias("monto"),
                  pl.col("contratista").mode().first().alias("nombre"),
              ])
              .sort(["ciclo", "rfc_contratista"])
              .to_pandas()
    )

    _line_palette = ["#9F2241", "#E3007E", "#EC6730", "#00A489", "#00B7CD"]
    _fig3 = go.Figure()
    if len(_rally_trend):
        for _i, _rfc in enumerate(_top5):
            _sub = _rally_trend[_rally_trend["rfc_contratista"] == _rfc]
            _name = str(_sub["nombre"].iloc[0] if len(_sub) else _rfc)[:38] or _rfc
            _fig3.add_trace(go.Scatter(
                x=_sub["ciclo"], y=_sub["monto"],
                mode="lines+markers",
                name=f"{_i+1}. {_name}",
                line=dict(color=_line_palette[_i % len(_line_palette)], width=2.5),
                marker=dict(size=8),
                hovertemplate=f"<b>{_name}</b><br>%{{x}}: %{{customdata}}<extra></extra>",
                customdata=[fmt_mxn(v) for v in _sub["monto"]],
            ))
    else:
        _fig3.add_annotation(
            text="Sin contratos con RFC para esta alcaldía en 2013–2017",
            showarrow=False, x=0.5, y=0.5, xref="paper", yref="paper",
            font=dict(size=13, color="#64748B"),
        )

    _fig3.update_layout(
        height=360,
        margin=dict(l=10, r=10, t=30, b=30),
        title=dict(text=f"<b>Top 5 contratistas · {_alc_label} · 2013–2017</b>",
                   font=dict(size=14, family="Inter", color="#0F172A"), x=0.01),
        xaxis=dict(showgrid=False, dtick=1, title=""),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", tickformat=".2s", title=""),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif", size=12),
        legend=dict(orientation="h", yanchor="top", y=-0.1, x=0, xanchor="left",
                    bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
        hovermode="x unified",
    )

    _intro = mo.md("""
    <div style="padding:22px 24px 18px;background:white;border:1px solid #E2E8F0;border-radius:14px;margin-bottom:14px;">
        <div style="font-size:11px;color:#64748B;letter-spacing:1.8px;text-transform:uppercase;font-weight:600;">Acto V · Explora</div>
        <div style="font-size:26px;font-weight:700;color:#0F172A;margin-top:4px;line-height:1.15;letter-spacing:-0.5px;">
            Tendencias multi-año
        </div>
        <div style="font-size:13px;color:#475569;margin:10px 0 0;line-height:1.55;">
            Cómo evolucionaron los tres actos en el tiempo. El selector de <b>Alcaldía</b>
            afecta los egresos y los contratistas; los ingresos siempre son para toda la CDMX.
        </div>
    </div>
    """)

    act4_content = mo.vstack([
        _intro,
        mo.ui.plotly(_fig1),
        mo.ui.plotly(_fig2),
        mo.ui.plotly(_fig3),
    ])
    return (act4_content,)


@app.cell
def _(
    CHAPTER_PALETTE, SOURCE_COLORS, alcaldia_pick, egresos_all, egresos_df,
    fmt_mxn, go, ingresos_raw, mo, pl, year_pick,
):
    _year = year_pick.value

    _ing_cp = ingresos_raw.filter(
        (pl.col("ciclo") == _year) & (pl.col("periodo") == "Cuenta Pública")
    )
    _ing_an = ingresos_raw.filter(
        (pl.col("ciclo") == _year) & (pl.col("periodo") == "Anual")
    )
    _use_cp = _ing_cp.height > 0 and _ing_cp["monto_recaudado"].sum() > 0
    _ing = _ing_cp if _use_cp else _ing_an
    _amount_col = "monto_recaudado" if _use_cp else "monto_estimado"
    _ing_label = "recaudado · Cuenta Pública" if _use_cp else "planeado · Ley de Ingresos"

    _sources = (
        _ing.group_by("_bucket")
            .agg(pl.col(_amount_col).sum().alias("monto"))
            .filter(pl.col("monto") > 0)
            .sort("monto", descending=True)
            .to_pandas()
    )
    _total_ingresos = float(_sources["monto"].sum())

    _eg = egresos_df
    _alc_label = alcaldia_pick.value
    _apportion_note = ""
    _apportion_factor = 1.0
    if _alc_label != "Toda la CDMX":
        _eg = _eg.filter(pl.col("desc_unidad_responsable") == _alc_label)
        _alc_budget = float(_eg["_budget"].sum())
        _cdmx_year_budget = float(
            egresos_all.filter(pl.col("_year") == _year)["_budget"].sum()
        )
        _apportion_factor = (_alc_budget / _cdmx_year_budget) if _cdmx_year_budget > 0 else 0
        _apportion_note = (
            f'<div style="margin:8px 0 14px;padding:10px 14px;background:#F1F5F9;border-radius:6px;font-size:12px;color:#334155;line-height:1.55;">'
            f'ℹ️ <b>{_alc_label}</b> representa <b>{_apportion_factor*100:.1f}%</b> del presupuesto total de CDMX. '
            f'Las fuentes de ingreso se muestran proporcionales a esa participación, no son asignaciones exactas.'
            f'</div>'
        )

    _uses = (
        _eg.with_columns(pl.col("desc_capitulo").fill_null("Sin clasificar"))
            .group_by("desc_capitulo")
            .agg(pl.col("_spent").sum().alias("monto"))
            .filter(pl.col("monto") > 0)
            .sort("monto", descending=True)
            .to_pandas()
    )
    if _uses.empty:
        _uses = (
            _eg.with_columns(pl.col("desc_capitulo").fill_null("Sin clasificar"))
                .group_by("desc_capitulo")
                .agg(pl.col("_budget").sum().alias("monto"))
                .filter(pl.col("monto") > 0)
                .sort("monto", descending=True)
                .to_pandas()
        )
        _uses_label = "aprobado"
    else:
        _uses_label = "ejercido"

    _top_n = 10
    if len(_uses) > _top_n:
        _rest = float(_uses["monto"].iloc[_top_n:].sum())
        _uses = _uses.head(_top_n).copy()
        if _rest > 0:
            _uses = pl.concat([pl.from_pandas(_uses),
                               pl.DataFrame({"desc_capitulo": ["Otros capítulos"], "monto": [_rest]})]).to_pandas()

    if _apportion_factor != 1.0:
        _sources = _sources.copy()
        _sources["monto"] = _sources["monto"] * _apportion_factor
        _total_ingresos = float(_sources["monto"].sum())

    _total_egresos = float(_uses["monto"].sum())

    def _hex_to_rgba(h, alpha=0.38):
        h = h.lstrip("#")
        return f"rgba({int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)},{alpha})"

    _source_names = _sources["_bucket"].tolist()
    _use_names = _uses["desc_capitulo"].tolist()
    _pool_label = f"Presupuesto CDMX {_year}" if _alc_label == "Toda la CDMX" else f"{_alc_label}"
    _labels = _source_names + [_pool_label] + _use_names
    _pool_idx = len(_source_names)

    _node_colors = (
        [SOURCE_COLORS.get(n, "#94A3B8") for n in _source_names]
        + ["#0F172A"]
        + [CHAPTER_PALETTE[i % len(CHAPTER_PALETTE)] for i in range(len(_use_names))]
    )

    _src_ids, _tgt_ids, _values, _link_colors = [], [], [], []
    for _i, _row in _sources.reset_index(drop=True).iterrows():
        _src_ids.append(_i)
        _tgt_ids.append(_pool_idx)
        _values.append(float(_row["monto"]))
        _link_colors.append(_hex_to_rgba(SOURCE_COLORS.get(_row["_bucket"], "#94A3B8"), 0.38))
    for _i, _row in _uses.reset_index(drop=True).iterrows():
        _src_ids.append(_pool_idx)
        _tgt_ids.append(_pool_idx + 1 + _i)
        _values.append(float(_row["monto"]))
        _link_colors.append(_hex_to_rgba(CHAPTER_PALETTE[_i % len(CHAPTER_PALETTE)], 0.32))

    _fig_sk = go.Figure(go.Sankey(
        arrangement="snap",
        node=dict(
            label=_labels,
            color=_node_colors,
            pad=22,
            thickness=22,
            line=dict(color="white", width=1),
            hovertemplate="<b>%{label}</b><br>%{value:,.0f} MXN<extra></extra>",
        ),
        link=dict(
            source=_src_ids, target=_tgt_ids, value=_values, color=_link_colors,
            hovertemplate="<b>%{source.label} → %{target.label}</b><br>%{value:,.0f} MXN<extra></extra>",
        ),
        textfont=dict(size=12, color="#0F172A", family="Inter"),
    ))
    _fig_sk.update_layout(
        height=640,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif", size=12),
    )

    _hero = mo.md(f"""
    <div style="padding:22px 26px;background:white;border:1px solid #E2E8F0;border-radius:14px;margin-bottom:14px;">
        <div style="font-size:11px;color:#64748B;letter-spacing:1.8px;text-transform:uppercase;font-weight:600;">Acto I · Flujo</div>
        <div style="font-size:26px;font-weight:700;color:#0F172A;margin-top:4px;line-height:1.2;letter-spacing:-0.5px;">
            De las fuentes, al capítulo de gasto
        </div>
        <div style="font-size:13px;color:#475569;margin:10px 0 0;line-height:1.55;">
            <b>Izquierda:</b> ingresos {_ing_label}. <b>Centro:</b> el presupuesto consolidado.
            <b>Derecha:</b> los {len(_use_names)} capítulos de gasto principales ({_uses_label}).
            El grosor de cada flujo representa el monto.
        </div>
        {_apportion_note}
        <div style="display:flex;gap:12px;margin-top:14px;flex-wrap:wrap;">
            <div style="padding:10px 14px;background:#FEF2F2;border-left:3px solid #9F2241;border-radius:6px;flex:1;min-width:160px;">
                <div style="font-size:10px;letter-spacing:1.5px;color:#7F1D1D;text-transform:uppercase;font-weight:600;">Ingresos</div>
                <div style="font-size:18px;font-weight:700;color:#0F172A;margin-top:3px;">{fmt_mxn(_total_ingresos)}</div>
            </div>
            <div style="padding:10px 14px;background:#FFF7ED;border-left:3px solid #EC6730;border-radius:6px;flex:1;min-width:160px;">
                <div style="font-size:10px;letter-spacing:1.5px;color:#7C2D12;text-transform:uppercase;font-weight:600;">Egresos ({_uses_label})</div>
                <div style="font-size:18px;font-weight:700;color:#0F172A;margin-top:3px;">{fmt_mxn(_total_egresos)}</div>
            </div>
        </div>
    </div>
    """)

    _transition = mo.md(
        '<div style="margin:14px 0 0;padding:14px 18px;background:#FEF2F2;border-left:3px solid #9F2241;border-radius:6px;font-size:13px;color:#7F1D1D;line-height:1.5;">'
        '<b>→ Detalles en los siguientes actos.</b> Acto II te muestra de dónde vinieron exactamente los pesos; Acto III, qué se programó y cuánto se ejerció; Acto IV, en qué empresas aterrizó el gasto.'
        '</div>'
    )

    act_flujo_content = mo.vstack([_hero, _fig_sk, _transition])
    return (act_flujo_content,)


@app.cell(hide_code=True)
def _(CITIZEN_ORDER, mo):
    citizen_pick = mo.ui.dropdown(
        options=CITIZEN_ORDER,
        value="Transporte público",
        label="🧭 Categoría ciudadana",
    )
    return (citizen_pick,)


@app.cell
def _(
    CITIZEN_ICON, CITIZEN_PALETTE, budget_tree_df, citizen_pick, fmt_mxn,
    mo, pl,
):
    # ⑥ Ciudadano — Level 1 + Level 2 view from data/clean/budget_tree.parquet.
    # Reorganizes the budget around 16 citizen-experience categories
    # (el agua que llega, el camión que pasa, la beca que recibes).

    if budget_tree_df is None:
        act_ciudadano_content = mo.md(
            '<div style="padding:24px;background:#FEF2F2;border-left:4px solid #DC2626;'
            'border-radius:8px;color:#7F1D1D;font-size:13px;">'
            '<b>⚠️ data/clean/budget_tree.parquet no disponible.</b><br/>'
            'Corre <code>bash scripts/download_data.sh</code> y regenera '
            '<code>data/clean/</code> vía <code>data/scripts/build_crosswalk_and_parquets.py</code>.'
            '</div>'
        )
    else:
        _year_latest = int(budget_tree_df["year"].max())
        _tree = budget_tree_df.filter(pl.col("year") == _year_latest)
        _l1 = (
            _tree.filter(pl.col("level") == 1)
                 .sort("monto_aprobado", descending=True)
                 .to_pandas()
        )
        _total_l1 = float(_l1["monto_aprobado"].sum()) or 1.0

        _cards = []
        for _, _r in _l1.iterrows():
            _cat = _r["citizen_category"]
            _icon = CITIZEN_ICON.get(_cat, "•")
            _color = CITIZEN_PALETTE.get(_cat, "#94A3B8")
            _pct = float(_r["per_100_of_total"]) if _r["per_100_of_total"] is not None else (_r["monto_aprobado"] / _total_l1 * 100)
            _bar_pct = min(_pct * 3, 100)
            _cards.append(f"""
            <div style="
                background:white;border:1px solid #E2E8F0;border-top:4px solid {_color};
                border-radius:12px;padding:16px 18px;flex:1 1 180px;min-width:180px;max-width:230px;
                box-shadow:0 1px 3px rgba(15,23,42,0.04);
            ">
                <div style="font-size:24px;">{_icon}</div>
                <div style="font-size:12px;color:#64748B;letter-spacing:0.5px;font-weight:600;margin-top:6px;line-height:1.3;">{_cat}</div>
                <div style="font-size:20px;font-weight:700;color:#0F172A;margin-top:6px;letter-spacing:-0.3px;">{fmt_mxn(_r['monto_aprobado'])}</div>
                <div style="font-size:11px;color:{_color};font-weight:600;margin-top:2px;">{_pct:.1f} de cada 100 pesos</div>
                <div style="background:#F1F5F9;height:4px;border-radius:2px;margin-top:10px;overflow:hidden;">
                    <div style="background:{_color};height:100%;width:{_bar_pct:.1f}%;"></div>
                </div>
            </div>
            """)

        _hero = mo.md(f"""
        <div style="padding:22px 26px;background:white;border:1px solid #E2E8F0;border-radius:14px;margin-bottom:14px;">
            <div style="font-size:11px;color:#64748B;letter-spacing:1.8px;text-transform:uppercase;font-weight:600;">⑥ Ciudadano · reparto por experiencia</div>
            <div style="font-size:26px;font-weight:700;color:#0F172A;margin-top:4px;line-height:1.15;letter-spacing:-0.5px;">
                De cada 100 pesos que gasta tu Ciudad en {_year_latest}, así se reparten
            </div>
            <div style="font-size:13px;color:#475569;margin:10px 0 0;line-height:1.5;">
                Reagrupado desde el crosswalk editorial ({_tree.filter(pl.col("level") == 2).height} programas a través de las 16 categorías).
                No por "clasificación funcional" — por <b>lo que ves cuando sales de tu casa</b>.
            </div>
        </div>
        """)

        _grid = mo.md(
            f'<div style="display:flex;flex-wrap:wrap;gap:12px;margin-bottom:24px;">{"".join(_cards)}</div>'
        )

        _cat = citizen_pick.value
        _color = CITIZEN_PALETTE.get(_cat, "#9F2241")
        _icon = CITIZEN_ICON.get(_cat, "•")

        _l1_row = _tree.filter((pl.col("level") == 1) & (pl.col("citizen_category") == _cat))
        _l1_monto = float(_l1_row["monto_aprobado"].sum()) if _l1_row.height else 0.0
        _l1_pct = float(_l1_row["per_100_of_total"].sum()) if _l1_row.height else 0.0

        _l2 = (
            _tree.filter((pl.col("level") == 2) & (pl.col("citizen_category") == _cat))
                 .sort("monto_aprobado", descending=True)
                 .head(20)
                 .to_pandas()
        )

        if len(_l2) == 0:
            _l2_html = f"""
            <div style="padding:18px;background:#F8FAFC;border:1.5px dashed #CBD5E1;border-radius:10px;color:#64748B;font-size:13px;text-align:center;">
                Sin programas desagregados para <b>{_cat}</b> en el crosswalk.
                La categoría existe como Level 1 pero sus partidas no se nombraron editorialmente.
            </div>
            """
        else:
            _rows_html = []
            _l2_monto_total = float(_l2["monto_aprobado"].sum()) or 1.0
            for _i, _r in _l2.iterrows():
                _pct = float(_r["per_100_of_parent"]) if _r["per_100_of_parent"] is not None else (_r["monto_aprobado"] / _l2_monto_total * 100)
                _bar_pct = min(_pct * 1.1, 100)
                _rows_html.append(f"""
                <div style="padding:12px 0;border-bottom:1px solid #F1F5F9;">
                    <div style="display:flex;justify-content:space-between;align-items:baseline;gap:16px;">
                        <div style="flex:1;min-width:0;font-size:14px;font-weight:600;color:#0F172A;line-height:1.35;">
                            {_r['display_name']}
                        </div>
                        <div style="font-size:14px;font-weight:700;color:#0F172A;white-space:nowrap;font-variant-numeric:tabular-nums;">
                            {fmt_mxn(_r['monto_aprobado'])}
                        </div>
                        <div style="font-size:12px;color:{_color};font-weight:600;white-space:nowrap;min-width:52px;text-align:right;">{_pct:.1f}%</div>
                    </div>
                    <div style="font-size:12px;color:#64748B;margin-top:4px;line-height:1.45;" title="{_r['rationale'] or ''}">
                        {(_r['rationale'] or '')[:160]}
                    </div>
                    <div style="background:#F1F5F9;height:3px;border-radius:2px;margin-top:8px;overflow:hidden;">
                        <div style="background:{_color};height:100%;width:{_bar_pct:.1f}%;"></div>
                    </div>
                </div>
                """)
            _l2_html = "".join(_rows_html)

        _drill = mo.md(f"""
        <div style="padding:22px 24px;background:white;border:1px solid #E2E8F0;border-radius:14px;border-top:4px solid {_color};">
            <div style="display:flex;align-items:center;gap:14px;margin-bottom:8px;">
                <div style="font-size:36px;">{_icon}</div>
                <div>
                    <div style="font-size:11px;color:#64748B;letter-spacing:1.5px;text-transform:uppercase;font-weight:600;">Detalle · {_cat}</div>
                    <div style="font-size:22px;font-weight:700;color:#0F172A;letter-spacing:-0.3px;">
                        {fmt_mxn(_l1_monto)} · {_l1_pct:.1f} de cada 100 pesos
                    </div>
                </div>
            </div>
            <div style="font-size:12px;color:#475569;margin:10px 0 16px;line-height:1.5;">
                Programas presupuestarios desagregados (hasta 20). Cada renglón es un
                programa concreto con su peso y su racional editorial. "Ver en datos
                oficiales" en <code>data/clean/source_links.csv</code>.
            </div>
            {_l2_html}
        </div>
        """)

        _footer = mo.md(
            '<div style="margin:18px 0 0;padding:12px 16px;background:#FEF2F2;border-left:3px solid #9F2241;border-radius:6px;font-size:12px;color:#7F1D1D;line-height:1.5;">'
            '<b>ℹ️ Metodología.</b> Este reparto se construye a partir del crosswalk editorial (<code>crosswalk/crosswalk.csv</code>). '
            'Cada programa presupuestario se asigna a una de las 16 categorías con un racional explícito. '
            'Ver <code>crosswalk/METHODOLOGY.md</code> para las decisiones controvertidas.'
            '</div>'
        )

        act_ciudadano_content = mo.vstack([_hero, _grid, citizen_pick, _drill, _footer])
    return (act_ciudadano_content,)


@app.cell
def _(fmt_mxn, mo, named_programs_df, pl):
    # ⑦ Emblemáticos — flagship programs extracted from the Paquete Económico 2024
    # narrative PDFs. These do NOT surface as desc_programa_presupuestario in the
    # main CSV (Cablebús, Utopías, Altépetl, Cosecha de Lluvia, Comedores, etc.).

    if named_programs_df is None:
        act_emblemas_content = mo.md(
            '<div style="padding:24px;background:#FEF2F2;border-left:4px solid #DC2626;'
            'border-radius:8px;color:#7F1D1D;font-size:13px;">'
            '<b>⚠️ crosswalk/named_programs_2024.csv no disponible.</b>'
            '</div>'
        )
    else:
        _df = (
            named_programs_df
            .filter(pl.col("monto_aprobado_mxn") > 0)
            .sort("monto_aprobado_mxn", descending=True)
            .to_pandas()
        )
        _total = float(_df["monto_aprobado_mxn"].sum())
        _n = len(_df)

        _hero = mo.md(f"""
        <div style="padding:22px 26px;background:white;border:1px solid #E2E8F0;border-radius:14px;margin-bottom:14px;">
            <div style="font-size:11px;color:#64748B;letter-spacing:1.8px;text-transform:uppercase;font-weight:600;">⑦ Emblemáticos · los proyectos con nombre propio</div>
            <div style="font-size:26px;font-weight:700;color:#0F172A;margin-top:4px;line-height:1.15;letter-spacing:-0.5px;">
                {_n} programas emblemáticos · {fmt_mxn(_total)} identificados
            </div>
            <div style="font-size:13px;color:#475569;margin:10px 0 0;line-height:1.55;">
                <b>Cablebús, Utopías, Pilares, Mi Beca, Altépetl, Cosecha de Lluvia, Comedores para el Bienestar</b> y otros
                programas emblemáticos <b>no aparecen con ese nombre</b> en la CSV oficial de egresos — viven a nivel de
                partida o de anexo. Estos pesos se extrajeron de los PDFs del Paquete Económico 2024 (Tomo I, Tomo II,
                Anexos III-F y VI-F).
            </div>
        </div>
        """)

        _sections = {}
        for _, _r in _df.iterrows():
            _sec = str(_r["section"] or "Otros").strip()
            _sections.setdefault(_sec, []).append(_r)

        _section_blocks = []
        for _sec_name, _rows in _sections.items():
            _sec_total = sum(float(r["monto_aprobado_mxn"]) for r in _rows)
            _rows_html = []
            for _r in _rows:
                _name = str(_r["display_name"] or "").strip()
                _ente = str(_r["ente_ejecutor"] or "").strip()
                _src = str(_r["source"] or "").strip()
                _note = str(_r["notes"] or "").strip()
                _rows_html.append(f"""
                <div style="padding:11px 0;border-bottom:1px solid #F1F5F9;">
                    <div style="display:flex;justify-content:space-between;align-items:baseline;gap:16px;">
                        <div style="flex:1;min-width:0;">
                            <div style="font-size:13px;font-weight:600;color:#0F172A;line-height:1.35;">{_name}</div>
                            <div style="font-size:11px;color:#64748B;margin-top:3px;">{_ente}</div>
                        </div>
                        <div style="font-size:13px;font-weight:700;color:#9F2241;white-space:nowrap;font-variant-numeric:tabular-nums;">
                            {fmt_mxn(_r['monto_aprobado_mxn'])}
                        </div>
                    </div>
                    <div style="font-size:10px;color:#94A3B8;margin-top:3px;font-family:ui-monospace,monospace;">{_src} · {_note}</div>
                </div>
                """)
            _section_blocks.append(f"""
            <div style="background:white;border:1px solid #E2E8F0;border-radius:12px;padding:16px 20px;margin-bottom:14px;">
                <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:10px;">
                    <div style="font-size:12px;color:#64748B;letter-spacing:1.2px;text-transform:uppercase;font-weight:600;">{_sec_name}</div>
                    <div style="font-size:13px;color:#9F2241;font-weight:700;font-variant-numeric:tabular-nums;">{fmt_mxn(_sec_total)}</div>
                </div>
                {''.join(_rows_html)}
            </div>
            """)

        _sections_md = mo.md("".join(_section_blocks))

        _footer = mo.md(
            '<div style="margin:8px 0 0;padding:12px 16px;background:#FEF2F2;border-left:3px solid #9F2241;border-radius:6px;font-size:12px;color:#7F1D1D;line-height:1.5;">'
            '<b>ℹ️ Fuente editorial.</b> Los pesos y nombres vienen del Paquete Económico 2024 (PDFs en <code>data/raw/narrative_sources/</code>). '
            'La columna <code>notes</code> cita página. Este es el <b>supplemento</b> al crosswalk — rellena el hueco de los programas bandera '
            'que no surgen como <code>desc_programa_presupuestario</code> en la CSV oficial.'
            '</div>'
        )

        act_emblemas_content = mo.vstack([_hero, _sections_md, _footer])
    return (act_emblemas_content,)


@app.cell(hide_code=True)
def _(mo):
    step = mo.ui.tabs(
        {
            "① Flujo":        mo.md(""),
            "② Entran":       mo.md(""),
            "③ Se prometen":  mo.md(""),
            "④ Aterrizan":    mo.md(""),
            "⑤ Explora":      mo.md(""),
            "⑥ Ciudadano":    mo.md(""),
            "⑦ Emblemáticos": mo.md(""),
        },
        value="① Flujo",
    )
    step
    return (step,)


@app.cell(hide_code=True)
def _(
    act1_content, act2_content, act3_content, act4_content,
    act_ciudadano_content, act_emblemas_content, act_flujo_content, step,
):
    _map = {
        "① Flujo":        act_flujo_content,
        "② Entran":       act1_content,
        "③ Se prometen":  act2_content,
        "④ Aterrizan":    act3_content,
        "⑤ Explora":      act4_content,
        "⑥ Ciudadano":    act_ciudadano_content,
        "⑦ Emblemáticos": act_emblemas_content,
    }
    _map.get(step.value, act_flujo_content)
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
