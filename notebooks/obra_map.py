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
            ¿Qué se construyó en tu calle?
        </div>
        <div style="font-size: 15px; margin-top: 10px; opacity: 0.92; max-width: 820px; line-height: 1.55;">
            Cada punto es un proyecto pagado con dinero federal. Arrastra el mapa a tu colonia,
            haz clic en cualquier punto y verás cuánto costó, quién lo construyó y cuántas
            personas se beneficiaron.
        </div>
        </div>
@app.cell(hide_code=True)
def _(df, fmt_int, fmt_mxn, mo, pl):
    _n = df.height
    _monto = df["monto_ejercido"].sum()
    _alcs = df["desc_alcaldia"].n_unique()

    _aprobado = df.with_columns(pl.col("monto_aprobado").cast(pl.Float64, strict=False))["monto_aprobado"].drop_nulls().sum()
    _ejercido_sum = df.with_columns(pl.col("monto_ejercido").cast(pl.Float64, strict=False))["monto_ejercido"].drop_nulls().sum()
    _ejecucion = f"{_ejercido_sum / _aprobado * 100:.1f}%" if _aprobado else "—"

    _terminados = df.with_columns(pl.col("avance_fisico").cast(pl.Float64, strict=False)).filter(pl.col("avance_fisico") >= 95).height
    _pct_terminados = f"{_terminados / _n * 100:.1f}%" if _n else "—"

    def _kpi(label, value, accent="#9F2241"):
        return f"""
        <div style="
            background: white;
            border: 1px solid #E2E8F0;
            border-left: 4px solid {accent};
            border-radius: 10px;
            padding: 18px 22px;
            flex: 1;
            min-width: 180px;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        ">
            <div style="font-size:11px;color:#64748B;letter-spacing:1.5px;text-transform:uppercase;font-weight:600;">{label}</div>
            <div style="font-size:26px;font-weight:700;color:#0F172A;margin-top:6px;letter-spacing:-0.5px;">{value}</div>
        </div>
        """

    mo.md(f"""
    <div style="display:flex;gap:14px;flex-wrap:wrap;margin:16px 0 22px;">
    {_kpi("Proyectos", fmt_int(_n), "#9F2241")}
    {_kpi("Inversión ejercida", fmt_mxn(_monto), "#00A489")}
    {_kpi("Ejecución presupuestal", _ejecucion, "#00B7CD")}
    {_kpi("Proyectos terminados", _pct_terminados, "#6C4A7E")}
    {_kpi("Alcaldías con obra", fmt_int(_alcs), "#EC6730")}
    </div>
    """)
    return
        "Comunicaciones y Transportes": "#00B7CD",
        "Medio Ambiente y Recursos Naturales": "#00A489",
        "Salud": "#E3007E",
        "Educación Pública": "#6C4A7E",
        "Gobernación": "#3D5A80",
        "Cultura": "#D6A461",
        "Desarrollo Agrario, Territorial y Urbano": "#2A9D8F",
    }

    def fmt_mxn(v):
        if v is None or v == 0:
            return "—"
        v = float(v)
        if v >= 1e9:
            return f"${v / 1e9:,.2f} mmdp"
        if v >= 1e6:
            return f"${v / 1e6:,.1f} mdp"
        if v >= 1e3:
            return f"${v / 1e3:,.0f} k"
        return f"${v:,.0f}"

    def fmt_int(v):
        if v is None or v == 0:
            return "—"
        return f"{int(v):,}"

    return DATA_DIR, FONT, RAMO_PALETTE, fmt_int, fmt_mxn, go, mo, pl, px


@app.cell
def _(DATA_DIR, pl):
    raw = pl.read_csv(
        DATA_DIR / "rally_obras.csv",
        infer_schema_length=10_000,
        null_values=["NA", ""],
        truncate_ragged_lines=True,
        ignore_errors=True,
    )

    raw = raw.with_columns(
        [
            pl.col("latitud").cast(pl.Float64, strict=False),
            pl.col("longitud").cast(pl.Float64, strict=False),
            pl.col("monto_aprobado").fill_null(0),
            pl.col("monto_ejercido").fill_null(0),
            pl.col("monto_pagado").fill_null(0),
            pl.col("avance_fisico").fill_null(0),
            pl.col("poblacion_beneficiada").fill_null(0),
        ]
    ).filter(
        pl.col("latitud").is_not_null()
        & pl.col("longitud").is_not_null()
        & (pl.col("latitud").is_between(19.0, 19.7))
        & (pl.col("longitud").is_between(-99.5, -98.9))
    )
    return (raw,)


@app.cell(hide_code=True)
def _(mo, raw):
    _alcaldias = sorted(raw["desc_alcaldia"].drop_nulls().unique().to_list())
    _ramos = sorted(raw["desc_ramo"].drop_nulls().unique().to_list())
    _ciclos = sorted(raw["ciclo"].drop_nulls().unique().to_list())

    alcaldia_filter = mo.ui.multiselect(
        options=_alcaldias,
        value=[],
        label="Alcaldía",
    )
    ramo_filter = mo.ui.multiselect(
        options=_ramos,
        value=[],
        label="Ramo federal",
    )
    ciclo_filter = mo.ui.range_slider(
        start=min(_ciclos),
        stop=max(_ciclos),
        value=(min(_ciclos), max(_ciclos)),
        step=1,
        label="Año",
        show_value=True,
        full_width=False,
    )
    status_filter = mo.ui.dropdown(
        options={
            "Todos los estados": "all",
            "Terminados (≥95% avance)": "done",
            "En curso (25–95%)": "in_progress",
            "Rezagados (<25%)": "stalled",
        },
        value="Todos los estados",
        label="Estatus",
    )

    mo.hstack(
        [alcaldia_filter, ramo_filter, ciclo_filter, status_filter],
        justify="start",
        gap=1.5,
        wrap=True,
    )
    return alcaldia_filter, ciclo_filter, ramo_filter, status_filter


@app.cell
def _(alcaldia_filter, ciclo_filter, pl, ramo_filter, raw, status_filter):
    df = raw
    if alcaldia_filter.value:
        df = df.filter(pl.col("desc_alcaldia").is_in(alcaldia_filter.value))
    if ramo_filter.value:
        df = df.filter(pl.col("desc_ramo").is_in(ramo_filter.value))
    df = df.filter(pl.col("ciclo").is_between(*ciclo_filter.value))

    _status = status_filter.value
    if _status == "done":
        df = df.filter(pl.col("avance_fisico") >= 95)
    elif _status == "in_progress":
        df = df.filter(pl.col("avance_fisico").is_between(25, 95, closed="left"))
    elif _status == "stalled":
        df = df.filter(pl.col("avance_fisico") < 25)
    return (df,)


@app.cell(hide_code=True)
def _(df, fmt_int, fmt_mxn, mo):
    _n = df.height
    _monto = df["monto_ejercido"].sum()
    _contratistas = df["contratista"].drop_nulls().n_unique()
    _alcs = df["desc_alcaldia"].n_unique()

    def _kpi(label, value, accent="#9F2241"):
        return f"""
        <div style="
            background: white;
            border: 1px solid #E2E8F0;
            border-left: 4px solid {accent};
            border-radius: 10px;
            padding: 18px 22px;
            flex: 1;
            min-width: 180px;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        ">
            <div style="font-size:11px;color:#64748B;letter-spacing:1.5px;text-transform:uppercase;font-weight:600;">{label}</div>
            <div style="font-size:26px;font-weight:700;color:#0F172A;margin-top:6px;letter-spacing:-0.5px;">{value}</div>
        </div>
        """

    mo.md(f"""
    <div style="display:flex;gap:14px;flex-wrap:wrap;margin:16px 0 22px;">
    {_kpi("Proyectos", fmt_int(_n), "#9F2241")}
    {_kpi("Inversión ejercida", fmt_mxn(_monto), "#00A489")}
    {_kpi("Contratistas únicos", fmt_int(_contratistas), "#00B7CD")}
    {_kpi("Alcaldías con obra", fmt_int(_alcs), "#EC6730")}
    </div>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### El mapa · explora proyecto por proyecto

        Cada punto es un proyecto. **El tamaño** indica el monto ejercido y **el color** la fuente federal.
        Haz clic en un punto para ver los detalles completos abajo.
        """
    )
    return


@app.cell
def _(RAMO_PALETTE, df, fmt_int, fmt_mxn, go, mo, pl, px):
    import math

    _pdf = (
        df.select(
            [
                "id",
                "latitud",
                "longitud",
                "desc_ramo",
                "monto_ejercido",
                "nombre_proyecto",
                "desc_alcaldia",
                "desc_localidad",
                "poblacion_beneficiada",
                "avance_fisico",
                "ciclo",
            ]
        )
        .to_pandas()
        .copy()
    )

    _pdf["desc_ramo"] = _pdf["desc_ramo"].fillna("Sin clasificar")
    _pdf["_name"] = _pdf["nombre_proyecto"].fillna("(sin nombre)").str.slice(0, 90)

    def _hover(row):
        _place = " · ".join(
            [
                s
                for s in [row["desc_alcaldia"], row["desc_localidad"]]
                if isinstance(s, str) and s
            ]
        )
        _monto = fmt_mxn(row["monto_ejercido"])
        _avance = f"{row['avance_fisico']:.0f}%" if row["avance_fisico"] else "—"
        _benef = fmt_int(row["poblacion_beneficiada"])
        return (
            f"<b>{row['_name']}</b><br>"
            f"<span style='color:#64748B'>{_place} · {int(row['ciclo'])}</span><br>"
            f"Ejercido <b>{_monto}</b> · Avance {_avance}<br>"
            f"Beneficiarios {_benef}<br>"
            f"<span style='color:#9F2241'>{row['desc_ramo']}</span>"
        )

    _pdf["_h"] = _pdf.apply(_hover, axis=1)
    _pdf["_size"] = _pdf["monto_ejercido"].apply(
        lambda v: max(math.sqrt(max(v, 0)) / 700, 4)
    )

    _ramos_present = sorted(_pdf["desc_ramo"].unique())
    _color_seq = [RAMO_PALETTE.get(r, "#94A3B8") for r in _ramos_present]

    _fig = px.scatter_map(
        _pdf,
        lat="latitud",
        lon="longitud",
        color="desc_ramo",
        color_discrete_sequence=_color_seq,
        size="_size",
        size_max=26,
        custom_data=["id", "_h"],
        zoom=9.7,
        center={"lat": 19.38, "lon": -99.15},
        map_style="carto-positron",
        opacity=0.75,
    )
    _fig.update_traces(
        hovertemplate="%{customdata[1]}<extra></extra>",
    )
    _fig.update_layout(
        height=620,
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255,255,255,0.92)",
            bordercolor="#E2E8F0",
            borderwidth=1,
            font=dict(size=11, family="Inter"),
            title=dict(text="<b>Ramo federal</b>", font=dict(size=12)),
            itemsizing="constant",
        ),
        paper_bgcolor="white",
    )

    map_widget = mo.ui.plotly(_fig)
    map_widget
    return (map_widget,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("### Proyecto seleccionado")
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
        mo.md(
            """
            <div style="padding:24px;border:1.5px dashed #CBD5E1;border-radius:12px;
                        color:#64748B;text-align:center;background:#F8FAFC;">
                👆 Haz clic en un punto del mapa para ver los detalles del proyecto.
            </div>
            """
        )
    else:
        _proj = df.filter(pl.col("id") == _selected_ids[0]).to_pandas().iloc[0]

        _status_color = (
            "#059669"
            if _proj["avance_fisico"] >= 95
            else ("#D97706" if _proj["avance_fisico"] >= 25 else "#DC2626")
        )
        _status_label = (
            "Terminado"
            if _proj["avance_fisico"] >= 95
            else ("En curso" if _proj["avance_fisico"] >= 25 else "Rezagado")
        )

        _contract_link = ""
        if isinstance(_proj.get("url_contrato"), str) and _proj[
            "url_contrato"
        ].startswith("http"):
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

        mo.md(f"""
        <div style="
            border:1px solid #E2E8F0; border-radius:14px; padding:24px 28px;
            background:white; box-shadow:0 2px 8px rgba(15,23,42,0.04);
        ">
            <div style="display:flex;align-items:start;justify-content:space-between;gap:20px;">
                <div style="flex:1;">
                    <div style="font-size:20px;font-weight:700;color:#0F172A;letter-spacing:-0.3px;line-height:1.3;">
                        {_proj["nombre_proyecto"] or "(sin nombre)"}
                    </div>
                    <div style="margin-top:6px;font-size:13px;color:#64748B;">
                        {_proj.get("desc_alcaldia", "")} · {_proj.get("desc_localidad", "")} · {_proj.get("direccion_proyecto", "") or ""}
                    </div>
                </div>
                <div style="
                    padding:6px 14px;border-radius:20px;
                    background:{_status_color}15;color:{_status_color};
                    font-weight:600;font-size:12px;letter-spacing:0.5px;text-transform:uppercase;
                    white-space:nowrap;
                ">
                    {_status_label} · {_proj["avance_fisico"]:.0f}%
                </div>
            </div>

            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));
                        gap:16px;margin-top:20px;padding-top:18px;border-top:1px solid #F1F5F9;">
                <div>
                    <div style="font-size:10px;letter-spacing:1.2px;color:#64748B;text-transform:uppercase;font-weight:600;">Aprobado</div>
                    <div style="font-size:17px;font-weight:600;color:#0F172A;margin-top:3px;">{fmt_mxn(_proj["monto_aprobado"])}</div>
                </div>
                <div>
                    <div style="font-size:10px;letter-spacing:1.2px;color:#64748B;text-transform:uppercase;font-weight:600;">Ejercido</div>
                    <div style="font-size:17px;font-weight:600;color:#9F2241;margin-top:3px;">{fmt_mxn(_proj["monto_ejercido"])}</div>
                </div>
                <div>
                    <div style="font-size:10px;letter-spacing:1.2px;color:#64748B;text-transform:uppercase;font-weight:600;">Pagado</div>
                    <div style="font-size:17px;font-weight:600;color:#0F172A;margin-top:3px;">{fmt_mxn(_proj["monto_pagado"])}</div>
                </div>
                <div>
                    <div style="font-size:10px;letter-spacing:1.2px;color:#64748B;text-transform:uppercase;font-weight:600;">Beneficiarios</div>
                    <div style="font-size:17px;font-weight:600;color:#0F172A;margin-top:3px;">{fmt_int(_proj["poblacion_beneficiada"])}</div>
                </div>
                <div>
                    <div style="font-size:10px;letter-spacing:1.2px;color:#64748B;text-transform:uppercase;font-weight:600;">Fuente</div>
                    <div style="font-size:13px;font-weight:500;color:#0F172A;margin-top:3px;line-height:1.35;">{_proj.get("desc_ramo", "—")}</div>
                </div>
                <div>
                    <div style="font-size:10px;letter-spacing:1.2px;color:#64748B;text-transform:uppercase;font-weight:600;">Contratista</div>
                    <div style="font-size:13px;font-weight:500;color:#0F172A;margin-top:3px;line-height:1.35;">
                        {_proj.get("contratista") or "—"}{" · " + _contract_link if _contract_link else ""}
                    </div>
                </div>
            </div>

            {_justif_html}
        </div>
        """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("### ¿Cómo se reparte la inversión entre alcaldías?")
    return


@app.cell
def _(alcaldia_filter, df, fmt_mxn, go, pl):
    _alc = (
        df.group_by("desc_alcaldia")
        .agg(
            [
                pl.col("monto_ejercido").sum().alias("monto"),
                pl.len().alias("proyectos"),
            ]
        )
        .sort("monto", descending=True)
        .to_pandas()
    )
    _alc["desc_alcaldia"] = _alc["desc_alcaldia"].fillna("Sin alcaldía")
    _alc = _alc.iloc[::-1].reset_index(drop=True)
    _alc["label"] = _alc["monto"].apply(fmt_mxn)

    _selected = set(alcaldia_filter.value or [])
    _colors = [
        "#9F2241" if a in _selected else "#E2E8F0" for a in _alc["desc_alcaldia"]
    ]
    if not _selected:
        _colors = ["#9F2241"] * len(_alc)

    _fig = go.Figure(
        go.Bar(
            x=_alc["monto"],
            y=_alc["desc_alcaldia"],
            orientation="h",
            marker=dict(color=_colors),
            text=_alc["label"],
            textposition="outside",
            textfont=dict(size=11, color="#334155"),
            hovertemplate="<b>%{y}</b><br>%{text} · %{customdata} proyectos<extra></extra>",
            customdata=_alc["proyectos"],
            cliponaxis=False,
        )
    )
    _fig.update_layout(
        height=max(300, 28 * len(_alc) + 40),
        margin=dict(l=10, r=60, t=10, b=30),
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9", tickformat=".2s", title=""),
        yaxis=dict(title="", tickfont=dict(size=12)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif", size=12, color="#1E293B"),
    )
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("### Hallazgos")
    return


@app.cell
def _(df, fmt_int, fmt_mxn, mo, pl):
    if df.height == 0:
        mo.md("*Sin datos con los filtros actuales.*")
    else:
        _total = df["monto_ejercido"].sum()
        _stalled = df.filter(pl.col("avance_fisico") < 25)
        _stalled_n = _stalled.height
        _stalled_monto = _stalled["monto_ejercido"].sum()

        _done_n = df.filter(pl.col("avance_fisico") >= 95).height

        _top_ramo = (
            df.group_by("desc_ramo")
            .agg(pl.col("monto_ejercido").sum())
            .sort("monto_ejercido", descending=True)
            .head(1)
            .to_pandas()
        )

        _top_alc = (
            df.group_by("desc_alcaldia")
            .agg(pl.col("monto_ejercido").sum())
            .sort("monto_ejercido", descending=True)
            .head(1)
            .to_pandas()
        )

        def _card(emoji, title, body, tone="#0F172A"):
            return f"""
            <div style="background:white;border:1px solid #E2E8F0;border-radius:12px;padding:18px 20px;flex:1;min-width:240px;">
                <div style="font-size:22px;">{emoji}</div>
                <div style="font-size:11px;letter-spacing:1.2px;color:#64748B;text-transform:uppercase;font-weight:600;margin-top:6px;">{title}</div>
                <div style="font-size:14px;color:{tone};margin-top:6px;line-height:1.45;">{body}</div>
            </div>
            """

        _cards = []
        _pct_done = (_done_n / df.height * 100) if df.height else 0
        _cards.append(
            _card(
                "✅",
                "Tasa de terminación",
                f"<b>{_pct_done:.0f}%</b> de {fmt_int(df.height)} proyectos llegaron a ≥95% de avance físico.",
            )
        )

        if _stalled_n:
            _cards.append(
                _card(
                    "⚠️",
                    "Proyectos rezagados",
                    f"<b>{fmt_int(_stalled_n)}</b> proyectos con menos de 25% de avance acumulan "
                    f"<b>{fmt_mxn(_stalled_monto)}</b> ejercidos.",
                    tone="#B91C1C",
                )
            )

        if len(_top_ramo):
            _tr = _top_ramo.iloc[0]
            _cards.append(
                _card(
                    "🏦",
                    "Principal fuente federal",
                    f"<b>{_tr['desc_ramo']}</b> concentra <b>{fmt_mxn(_tr['monto_ejercido'])}</b> "
                    f"({_tr['monto_ejercido'] / _total * 100:.0f}% del total).",
                )
            )

        if len(_top_alc):
            _ta = _top_alc.iloc[0]
            _cards.append(
                _card(
                    "📍",
                    "Alcaldía con mayor inversión",
                    f"<b>{_ta['desc_alcaldia']}</b> recibió <b>{fmt_mxn(_ta['monto_ejercido'])}</b>.",
                )
            )

        mo.md(
            f'<div style="display:flex;gap:14px;flex-wrap:wrap;margin:8px 0 24px;">{"".join(_cards)}</div>'
        )
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
