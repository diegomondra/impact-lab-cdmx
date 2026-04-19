import marimo

__generated_with = "0.23.1"
app = marimo.App(
    width="full",
    app_title="Tus 100 pesos · Presupuesto CDMX",
)


@app.cell
def _():
    import sys
    from pathlib import Path

    _NB_DIR = Path(__file__).resolve().parent
    if str(_NB_DIR) not in sys.path:
        sys.path.insert(0, str(_NB_DIR))

    import marimo as mo
    import polars as pl
    import plotly.express as px
    import plotly.graph_objects as go

    from lib.common import (
        CDMX_GUINDA,
        CDMX_GUINDA_DARK,
        FONT,
        PALETTE,
        fmt_int,
        fmt_mxn,
        hero_banner,
        kpi_card,
        style_fig,
    )
    from lib.loaders import (
        available_years,
        load_budget_by_alcaldia,
        load_budget_tree,
        load_income_sources,
        load_source_links,
    )

    return (
        CDMX_GUINDA,
        CDMX_GUINDA_DARK,
        FONT,
        PALETTE,
        available_years,
        fmt_int,
        fmt_mxn,
        go,
        hero_banner,
        kpi_card,
        load_budget_by_alcaldia,
        load_budget_tree,
        load_income_sources,
        load_source_links,
        mo,
        pl,
        px,
        style_fig,
    )


@app.cell
def _(mo):
    _qp = mo.query_params()
    _raw = _qp.get("cat")
    selected_cat = _raw if (_raw and str(_raw).strip()) else None
    return (selected_cat,)


@app.cell(hide_code=True)
def _(hero_banner, mo):
    mo.md(
        hero_banner(
            kicker="Ciudad de México · Presupuesto ciudadano",
            title="Tus 100 pesos",
            subtitle=(
                "De cada 100 pesos que gasta tu Ciudad, así se reparten. "
                "No por clasificación funcional — por lo que tú ves al salir "
                "de tu casa. Toca una categoría para ver los programas."
            ),
        )
    )
    return


@app.cell
def _(load_budget_by_alcaldia, load_budget_tree, load_source_links, pl):
    _tree_all = load_budget_tree()
    _years = sorted(_tree_all["year"].unique().to_list())
    year_val = int(max(_years)) if _years else 2024

    tree = _tree_all.filter(pl.col("year") == year_val)

    _alc_all = load_budget_by_alcaldia()
    alc_df = (
        _alc_all.filter(pl.col("year") == year_val)
        if _alc_all is not None
        else None
    )

    source_links = load_source_links()
    city_level1 = (
        tree.filter(pl.col("level") == 1)
            .sort("monto_aprobado", descending=True)
    )
    city_total = float(city_level1["monto_aprobado"].sum())
    return alc_df, city_level1, city_total, source_links, tree, year_val


@app.cell(hide_code=True)
def _(alc_df, mo):
    if alc_df is None:
        alcaldia_dropdown = None
        _display = mo.md("")
    else:
        _alc_names = sorted(
            alc_df.select("alcaldia").unique()["alcaldia"].to_list()
        )
        alcaldia_dropdown = mo.ui.dropdown(
            options=["Toda la ciudad"] + _alc_names,
            value="Toda la ciudad",
            label="Vista por alcaldía",
            full_width=False,
        )
        _display = mo.hstack(
            [alcaldia_dropdown], justify="start", gap=1.0
        )
    _display
    return (alcaldia_dropdown,)


@app.cell(hide_code=True)
def _(city_total, fmt_mxn, mo, year_val):
    mo.md(
        f"""
        <div style="margin: 20px 0 4px;">
            <div style="font-size:11px;color:#64748B;letter-spacing:1.8px;
                        text-transform:uppercase;font-weight:600;">
                Presupuesto de egresos · {year_val}
            </div>
            <div style="font-size:56px;font-weight:700;color:#0F172A;
                        letter-spacing:-1.5px;line-height:1.05;margin-top:6px;
                        font-variant-numeric:tabular-nums;">
                {fmt_mxn(city_total, short=False)}
            </div>
            <div style="font-size:14px;color:#334155;margin-top:10px;
                        max-width:680px;line-height:1.55;">
                Así se reparten de cada 100 pesos.
            </div>
        </div>
        """
    )
    return


@app.cell(hide_code=True)
def _(CDMX_GUINDA, alc_df, alcaldia_dropdown, city_total, fmt_mxn, mo, pl):
    _alc_name = (
        alcaldia_dropdown.value
        if alcaldia_dropdown is not None
        else "Toda la ciudad"
    )
    _scoped = _alc_name != "Toda la ciudad" and alc_df is not None

    if _scoped:
        _alc_total = float(
            alc_df.filter(
                (pl.col("level") == 1) & (pl.col("alcaldia") == _alc_name)
            )["monto_aprobado"].sum()
        )
        _pct = (_alc_total / city_total * 100) if city_total else 0.0
        mo.md(
            f"""
            <div style="margin:18px 0 6px;padding:16px 20px;
                        background:#FDF2F4;border-left:4px solid {CDMX_GUINDA};
                        border-radius:10px;line-height:1.55;">
                <div style="font-size:11px;color:{CDMX_GUINDA};
                            letter-spacing:1.5px;text-transform:uppercase;
                            font-weight:700;">
                    Filtrado · {_alc_name}
                </div>
                <div style="font-size:14px;color:#334155;margin-top:6px;
                            max-width:780px;">
                    De esos <b style="font-variant-numeric:tabular-nums;">
                    {fmt_mxn(city_total)}</b>, unos
                    <b style="font-variant-numeric:tabular-nums;color:#0F172A;">
                    {fmt_mxn(_alc_total)}</b>
                    (<b style="font-variant-numeric:tabular-nums;">{_pct:.1f}%</b>)
                    se atribuyen a programas que tocan {_alc_name}. Abajo: cómo
                    se reparten esos pesos dentro de la alcaldía.
                </div>
            </div>
            """
        )
    else:
        mo.md("")
    return


@app.cell
def _(alc_df, alcaldia_dropdown, city_level1, pl):
    _alc_name = (
        alcaldia_dropdown.value
        if alcaldia_dropdown is not None
        else "Toda la ciudad"
    )
    _scoped = _alc_name != "Toda la ciudad" and alc_df is not None
    _city_lookup = {r["source_id"]: r for r in city_level1.to_dicts()}

    if not _scoped:
        display_rows = [
            {
                "source_id": r["source_id"],
                "display_name": r["display_name"],
                "citizen_category": r["citizen_category"],
                "icon": r.get("icon"),
                "rationale": r.get("rationale"),
                "monto_aprobado": r["monto_aprobado"],
                "primary_pct": r.get("per_100_of_total"),
                "secondary_pct": None,
            }
            for r in city_level1.to_dicts()
        ]
        scope_label = None
    else:
        _alc_l1 = (
            alc_df.filter(
                (pl.col("level") == 1) & (pl.col("alcaldia") == _alc_name)
            )
            .sort("monto_aprobado", descending=True)
            .to_dicts()
        )
        display_rows = []
        for _r in _alc_l1:
            _base = _city_lookup.get(_r["source_id"], {})
            display_rows.append({
                "source_id": _r["source_id"],
                "display_name": _r["display_name"],
                "citizen_category": _r["citizen_category"],
                "icon": _base.get("icon"),
                "rationale": _base.get("rationale"),
                "monto_aprobado": _r["monto_aprobado"],
                "primary_pct": _r.get("per_100_of_alcaldia_total"),
                "secondary_pct": _base.get("per_100_of_total"),
            })
        scope_label = _alc_name

    return display_rows, scope_label


@app.cell(hide_code=True)
def _(CDMX_GUINDA, display_rows, fmt_mxn, mo, scope_label):
    _CANONICAL_ORDER = [
        "Agua",
        "Transporte público",
        "Calles y banquetas",
        "Basura y limpia",
        "Parques y espacios públicos",
        "Seguridad",
        "Justicia",
        "Salud",
        "Educación",
        "Apoyos sociales",
        "Cultura y deporte",
        "Medio ambiente",
        "Alumbrado",
        "Gobierno y administración",
        "Deuda",
        "Otros",
    ]
    _order_idx = {c: i for i, c in enumerate(_CANONICAL_ORDER)}

    _rows = list(display_rows)
    _rows.sort(
        key=lambda r: (
            _order_idx.get(r.get("citizen_category"), 999),
            -(r.get("monto_aprobado") or 0),
        )
    )

    def _fmt_pct(p):
        if p is None:
            return "—"
        return f"{p:.0f}" if p >= 1 else f"{p:.1f}"

    def _card_html(row):
        _pct = float(row.get("primary_pct") or 0.0)
        _pct_label = _fmt_pct(_pct)
        _bar_width = max(min(_pct, 100.0), 1.0) if _pct > 0 else 0
        _icon = row.get("icon") or "•"
        _pesos = row.get("monto_aprobado") or 0
        _sid = row["source_id"]
        _name = row["display_name"]
        _secondary = row.get("secondary_pct")
        _empty = (not _pesos) or _pesos <= 0

        if _empty:
            _value_html = (
                '<div style="font-size:13px;color:#94A3B8;font-style:italic;">'
                "Datos en consolidación.</div>"
            )
        else:
            _primary_line = (
                f"{_pct_label} de cada 100 pesos"
                if _secondary is None
                else f"{_pct_label} de cada 100 pesos en esta alcaldía"
            )
            if _secondary is not None:
                _city_line = (
                    f'<div style="font-size:11px;color:#94A3B8;margin-top:2px;'
                    f'font-variant-numeric:tabular-nums;">'
                    f"{_secondary:.2f}% del gasto total de la ciudad</div>"
                )
            else:
                _city_line = ""
            _value_html = (
                f'<div style="font-size:22px;font-weight:700;color:#0F172A;'
                f'letter-spacing:-0.3px;font-variant-numeric:tabular-nums;">'
                f"{fmt_mxn(_pesos)}</div>"
                f'<div style="font-size:12px;color:#64748B;">'
                f"{_primary_line}</div>"
                f"{_city_line}"
            )

        return f"""
        <a class="tcp-card" href="?cat={_sid}">
            <div style="display:flex;align-items:center;justify-content:space-between;">
                <div style="font-size:22px;line-height:1;">{_icon}</div>
                <div style="font-size:11px;color:{CDMX_GUINDA};font-weight:700;
                            letter-spacing:0.5px;
                            font-variant-numeric:tabular-nums;">{_pct_label}%</div>
            </div>
            <div style="font-size:13px;color:#334155;font-weight:600;
                        letter-spacing:0.2px;line-height:1.35;
                        min-height:34px;">{_name}</div>
            {_value_html}
            <div style="height:4px;background:#F1F5F9;border-radius:2px;
                        overflow:hidden;margin-top:auto;">
                <div style="height:100%;width:{_bar_width}%;
                            background:{CDMX_GUINDA};border-radius:2px;"></div>
            </div>
        </a>
        """

    _cards_html = "".join(_card_html(r) for r in _rows)
    _subtitle = (
        "Las categorías que tu Ciudad gasta"
        if scope_label is None
        else f"Lo que tu Ciudad gasta en {scope_label}"
    )

    if not _rows:
        _grid_block = (
            '<div style="padding:24px;border:1.5px dashed #CBD5E1;'
            "border-radius:12px;color:#64748B;text-align:center;"
            'background:#F8FAFC;margin-top:12px;">'
            "Datos en consolidación para esta alcaldía."
            "</div>"
        )
    else:
        _grid_block = f"""
        <div style="
            display:grid;
            grid-template-columns: repeat(auto-fill, minmax(232px, 1fr));
            gap: 12px;
            margin-top: 4px;
        ">{_cards_html}</div>
        """

    mo.md(
        f"""
        <style>
        a.tcp-card {{
            text-decoration: none;
            color: inherit;
            display: flex;
            flex-direction: column;
            gap: 10px;
            background: white;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 20px 22px 18px;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
            min-height: 178px;
            box-sizing: border-box;
            transition: transform 120ms ease-out,
                        box-shadow 120ms ease-out,
                        border-color 120ms ease-out;
        }}
        a.tcp-card:hover {{
            border-color: {CDMX_GUINDA};
            transform: translateY(-1px);
            box-shadow: 0 6px 14px rgba(159, 34, 65, 0.10);
        }}
        a.tcp-card:focus-visible {{
            outline: 2px solid {CDMX_GUINDA};
            outline-offset: 2px;
        }}
        </style>
        <div style="margin:28px 0 10px;font-size:11px;color:#64748B;
                    letter-spacing:1.8px;text-transform:uppercase;
                    font-weight:600;">
            {_subtitle}
        </div>
        {_grid_block}
        """
    )
    return


@app.cell
def _(
    CDMX_GUINDA,
    alc_df,
    alcaldia_dropdown,
    fmt_mxn,
    mo,
    pl,
    selected_cat,
    source_links,
    tree,
):
    _sid = selected_cat
    _alc_name = (
        alcaldia_dropdown.value
        if alcaldia_dropdown is not None
        else "Toda la ciudad"
    )
    _scoped = _alc_name != "Toda la ciudad" and alc_df is not None

    def _escape(s):
        if not s:
            return ""
        return (
            str(s)
            .replace("&", "&amp;")
            .replace('"', "&quot;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

    if _sid is None:
        _panel = mo.md(
            """
            <div style="margin:28px 0 8px;padding:18px 22px;
                        border:1.5px dashed #CBD5E1;border-radius:12px;
                        background:#F8FAFC;color:#64748B;font-size:13px;
                        line-height:1.55;">
                👆 Toca una categoría arriba para ver los programas nombrados
                que componen ese gasto.
            </div>
            """
        )
    else:
        _parent = None
        _category = None
        _city_base = tree.filter(
            (pl.col("level") == 1) & (pl.col("source_id") == _sid)
        ).to_dicts()

        if _scoped:
            _p_df = alc_df.filter(
                (pl.col("level") == 1)
                & (pl.col("source_id") == _sid)
                & (pl.col("alcaldia") == _alc_name)
            )
            if _p_df.height > 0:
                _p = _p_df.to_dicts()[0]
                if _city_base:
                    _p["icon"] = _city_base[0].get("icon")
                    _p["rationale"] = _city_base[0].get("rationale")
                _parent = _p
                _category = _p["citizen_category"]
        else:
            if _city_base:
                _parent = _city_base[0]
                _category = _parent["citizen_category"]

        if _parent is None:
            _panel = mo.md(
                f"""
                <div style="margin:28px 0 8px;padding:18px 22px;
                            border:1.5px dashed #CBD5E1;border-radius:12px;
                            background:#F8FAFC;color:#64748B;font-size:13px;
                            line-height:1.55;">
                    Datos en consolidación para esta categoría en
                    {_escape(_alc_name)}. Prueba con "Toda la ciudad" o
                    selecciona otra categoría.
                    <a href="?cat=" style="color:{CDMX_GUINDA};
                                            margin-left:8px;
                                            text-decoration:none;">
                        ← Volver a categorías
                    </a>
                </div>
                """
            )
        else:
            _parent_monto = float(_parent.get("monto_aprobado") or 0)
            _rationale_lookup = {
                r["source_id"]: r.get("rationale", "")
                for r in tree.filter(pl.col("level") == 2).to_dicts()
            }

            if _scoped:
                _children = (
                    alc_df.filter(
                        (pl.col("level") == 2)
                        & (pl.col("citizen_category") == _category)
                        & (pl.col("alcaldia") == _alc_name)
                    )
                    .sort("monto_aprobado", descending=True)
                    .to_dicts()
                )
                for _c in _children:
                    _cm = float(_c.get("monto_aprobado") or 0)
                    _c["per_100_of_parent"] = (
                        _cm / _parent_monto * 100 if _parent_monto else 0
                    )
                    _c["rationale"] = _rationale_lookup.get(
                        _c["source_id"], ""
                    )
            else:
                _children = (
                    tree.filter(
                        (pl.col("level") == 2)
                        & (pl.col("parent_id") == _sid)
                    )
                    .sort("monto_aprobado", descending=True)
                    .to_dicts()
                )

            _children_monto = sum(
                float(c.get("monto_aprobado") or 0) for c in _children
            )
            _remainder = max(_parent_monto - _children_monto, 0.0)

            def _row_html(c):
                _pct = c.get("per_100_of_parent") or 0.0
                _pct_label = (
                    f"{_pct:.1f}" if _pct < 10 else f"{_pct:.0f}"
                )
                _bar_width = max(min(float(_pct), 100.0), 1.0)
                _rationale = _escape(c.get("rationale") or "")
                _url = source_links.get(
                    c["source_id"], "https://datos.cdmx.gob.mx"
                )
                return f"""
                <div style="display:flex;align-items:center;gap:20px;
                            padding:14px 4px;
                            border-bottom:1px solid #F1F5F9;"
                     title="{_rationale}">
                    <div style="flex:1;min-width:0;">
                        <div style="font-size:15px;font-weight:600;
                                    color:#0F172A;line-height:1.35;">
                            {_escape(c['display_name'])}
                        </div>
                        <div style="margin-top:5px;">
                            <a href="{_url}" target="_blank" rel="noopener"
                               style="font-size:11px;color:{CDMX_GUINDA};
                                      text-decoration:none;
                                      letter-spacing:0.3px;font-weight:500;">
                                Ver en datos oficiales ↗
                            </a>
                        </div>
                    </div>
                    <div style="min-width:160px;display:flex;
                                flex-direction:column;align-items:flex-end;">
                        <div style="font-size:16px;font-weight:700;
                                    color:#0F172A;
                                    font-variant-numeric:tabular-nums;
                                    letter-spacing:-0.2px;">
                            {fmt_mxn(c['monto_aprobado'])}
                        </div>
                        <div style="font-size:11px;color:#64748B;
                                    font-variant-numeric:tabular-nums;">
                            {_pct_label}% de esta categoría
                        </div>
                    </div>
                    <div style="width:140px;flex-shrink:0;">
                        <div style="height:4px;background:#F1F5F9;
                                    border-radius:2px;overflow:hidden;">
                            <div style="height:100%;width:{_bar_width}%;
                                        background:{CDMX_GUINDA};
                                        border-radius:2px;"></div>
                        </div>
                    </div>
                </div>
                """

            if _children:
                _rows_html = "".join(_row_html(c) for c in _children)
            else:
                _rows_html = """
                <div style="padding:32px;text-align:center;color:#64748B;
                            font-size:13px;">
                    Datos en consolidación para esta categoría.
                </div>
                """

            if _remainder > 0 and _children:
                _pct_rem = (
                    _remainder / _parent_monto * 100
                    if _parent_monto
                    else 0
                )
                _disclosure = f"""
                <div style="margin-top:14px;padding:12px 16px;
                            background:#F8FAFC;border-radius:8px;
                            font-size:12px;color:#64748B;line-height:1.55;">
                    Otros rubros no destacados en esta categoría suman
                    <b style="color:#334155;
                              font-variant-numeric:tabular-nums;">
                    {fmt_mxn(_remainder)}</b>
                    ({_pct_rem:.0f}% de la categoría). Se consolidan como
                    "Otros" en la metodología.
                </div>
                """
            else:
                _disclosure = ""

            _sibling_cta = f"""
            <a href="obra_map.py" target="_blank"
               style="display:block;margin-top:22px;
                      text-decoration:none;color:inherit;">
                <div style="padding:20px 24px;border:1px solid #E2E8F0;
                            border-left:4px solid {CDMX_GUINDA};
                            border-radius:10px;background:white;
                            box-shadow:0 1px 3px rgba(15,23,42,0.04);">
                    <div style="font-size:11px;color:{CDMX_GUINDA};
                                letter-spacing:1.5px;
                                text-transform:uppercase;font-weight:600;">
                        Siguiente paso
                    </div>
                    <div style="font-size:17px;font-weight:700;
                                color:#0F172A;margin-top:6px;
                                letter-spacing:-0.3px;">
                        ¿Y qué se construyó en tu calle? →
                    </div>
                    <div style="font-size:13px;color:#64748B;
                                margin-top:6px;line-height:1.55;
                                max-width:680px;">
                        Cada proyecto pagado con dinero federal entre 2013
                        y 2018, ubicado en el mapa de la Ciudad. Abre el
                        mapa interactivo para ver qué se construyó cerca
                        de tu casa.
                    </div>
                </div>
            </a>
            """

            _scope_suffix = (
                "" if not _scoped else f" · en {_escape(_alc_name)}"
            )
            _header_html = f"""
            <style>
            @keyframes fadeInUp {{
                from {{ opacity: 0; transform: translateY(4px); }}
                to   {{ opacity: 1; transform: translateY(0); }}
            }}
            a.tcp-back {{
                display: inline-flex;
                align-items: center;
                gap: 6px;
                font-size: 13px;
                color: {CDMX_GUINDA};
                font-weight: 600;
                text-decoration: none;
                padding: 8px 14px;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                background: white;
                transition: border-color 120ms, background 120ms;
            }}
            a.tcp-back:hover {{
                border-color: {CDMX_GUINDA};
                background: #FDF2F4;
            }}
            </style>
            <div style="margin:32px 0 4px;
                        animation:fadeInUp 180ms ease-out;">
                <div style="font-size:11px;color:#64748B;letter-spacing:1.8px;
                            text-transform:uppercase;font-weight:600;">
                    {_parent.get("icon") or "•"} ·
                    {_escape(_parent["display_name"])}
                    · {fmt_mxn(_parent_monto)}{_scope_suffix}
                </div>
                <div style="font-size:22px;font-weight:700;color:#0F172A;
                            margin-top:4px;letter-spacing:-0.3px;">
                    Programas en esta categoría
                </div>
                <div style="font-size:13px;color:#64748B;margin-top:6px;
                            max-width:680px;line-height:1.55;">
                    {_escape(_parent.get("rationale") or "")}
                </div>
                <div style="margin-top:14px;">
                    <a class="tcp-back" href="?cat=">← Volver a categorías</a>
                </div>
            </div>
            """

            _list_html = f"""
            <div style="border:1px solid #E2E8F0;border-radius:12px;
                        padding:6px 18px 18px;background:white;
                        margin-top:10px;
                        animation:fadeInUp 220ms ease-out;">
                {_rows_html}
                {_disclosure}
            </div>
            {_sibling_cta}
            """

            _panel = mo.md(_header_html + _list_html)

    _panel
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ---
        <div style="text-align:center;color:#64748B;font-size:12px;padding:14px 0 28px;">
        Fuente: <a href="https://datos.cdmx.gob.mx" style="color:#9F2241;">Portal de Datos Abiertos de la Ciudad de México</a>
        · Construido con Marimo + Plotly · Claude Mexico City Lab 2026
        </div>
        """
    )
    return


if __name__ == "__main__":
    app.run()
