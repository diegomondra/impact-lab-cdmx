import marimo

__generated_with = "0.23.1"
app = marimo.App(
    width="full",
    app_title="Proveedores y asignación directa · lo que el dato deja ver",
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        <div style="
            padding: 36px 40px 28px;
            background: linear-gradient(135deg, #1E3A5F 0%, #0F2744 100%);
            color: white;
            border-radius: 14px;
            margin-bottom: 8px;
            box-shadow: 0 8px 24px rgba(15, 39, 68, 0.3);
            border-left: 5px solid #B88A4A;
        ">
        <div style="font-size: 13px; letter-spacing: 3px; opacity: 0.75; text-transform: uppercase; font-weight: 600; color:#F5D48A;">
            Auditoría forense · proveedores y modalidades de contratación
        </div>
        <div style="font-size: 38px; font-weight: 700; margin-top: 6px; letter-spacing: -0.5px;">
            ¿Quién cobra y cómo lo contratan?
        </div>
        <div style="font-size: 18px; margin-top: 8px; opacity: 0.85; font-weight: 400; max-width:820px; line-height:1.5;">
            De 23,410 proyectos con recursos federales en CDMX, sólo el 6% publicó
            <b>ambos</b> datos necesarios para auditar: modalidad de contratación
            <em>y</em> nombre del proveedor. Este tablero explora qué se ve — y qué
            se sugiere — dentro de ese 6%.
        </div>
        </div>
        <div style="
            margin: 8px 0 20px;
            padding: 14px 20px;
            background: #FEF6E1;
            border-left: 4px solid #B88A4A;
            border-radius: 8px;
            color: #6B4D1F;
            font-size: 13px;
            line-height: 1.55;
        ">
        <b>Cómo leerlo.</b> Cada sección presenta un patrón, sus lecturas inocentes
        y la pregunta que haría un reportero. <em>No son acusaciones</em>. Concentraciones y
        asignaciones directas son legales y a veces necesarias — pero los patrones
        merecen explicación pública.
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

    NAVY = "#1E3A5F"
    GOLD = "#B88A4A"
    TEAL = "#0E7490"
    RUST = "#9A3412"
    SLATE = "#475569"
    SLATE_LIGHT = "#CBD5E1"

    def fmt_mxn(v):
        if v is None or v == 0: return "—"
        v = float(v)
        if v >= 1e9: return f"${v/1e9:,.2f} mmdp"
        if v >= 1e6: return f"${v/1e6:,.1f} mdp"
        if v >= 1e3: return f"${v/1e3:,.0f} k"
        return f"${v:,.0f}"

    def bucket(s):
        if s is None: return None
        s = s.lower()
        if "adjudic" in s and "direct" in s: return "Adjudicación directa"
        if "invitación" in s or "invitacion" in s: return "Invitación a 3"
        if "licitación" in s or "licitacion" in s: return "Licitación pública"
        return None

    return DATA_DIR, GOLD, NAVY, RUST, SLATE, SLATE_LIGHT, TEAL, bucket, fmt_mxn, go, mo, pl, px


@app.cell
def _(DATA_DIR, bucket, pl):
    raw = pl.read_csv(
        DATA_DIR / "rally_obras.csv",
        infer_schema_length=10_000,
        null_values=["NA", ""],
        truncate_ragged_lines=True,
        ignore_errors=True,
    ).with_columns([
        pl.col("monto_ejercido").fill_null(0),
        pl.col("monto_aprobado").fill_null(0),
    ])

    NO_REPORT = "La Unidad Responsable no reportó información"
    disc = raw.filter(
        pl.col("desc_modalidad_contratacion").is_not_null()
        & (pl.col("desc_modalidad_contratacion") != NO_REPORT)
        & pl.col("contratista").is_not_null()
        & (pl.col("contratista") != NO_REPORT)
    ).with_columns(
        pl.col("desc_modalidad_contratacion").map_elements(bucket, return_dtype=pl.Utf8).alias("mod")
    ).filter(pl.col("mod").is_not_null())

    return disc, raw


@app.cell(hide_code=True)
def _(disc, fmt_mxn, mo, raw):
    _total_n = raw.height
    _total_monto = raw["monto_ejercido"].sum()
    _disc_n = disc.height
    _disc_monto = disc["monto_ejercido"].sum()

    def _card(number, label, caption, tone="#1E3A5F", big=False):
        size = "42px" if big else "30px"
        return f"""
        <div style="
            background: white;
            border: 1px solid #E2E8F0;
            border-left: 5px solid {tone};
            border-radius: 12px;
            padding: 22px 26px;
            flex: 1;
            min-width: 260px;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        ">
            <div style="font-size:{size};font-weight:800;color:{tone};letter-spacing:-0.5px;line-height:1;">{number}</div>
            <div style="font-size:12px;letter-spacing:1.2px;color:#0F172A;text-transform:uppercase;font-weight:700;margin-top:12px;line-height:1.4;">{label}</div>
            <div style="font-size:13px;color:#475569;margin-top:8px;line-height:1.55;">{caption}</div>
        </div>
        """

    mo.md(f"""
    <div style="display:flex;gap:16px;flex-wrap:wrap;margin:18px 0 24px;">
    {_card(f"{_disc_n/_total_n*100:.1f}%",
            "Universo auditable",
            f"Sólo <b>{_disc_n:,} de {_total_n:,}</b> proyectos publicaron modalidad de contratación <em>y</em> nombre de contratista. Ese 6% es lo único que permite una revisión pública desde afuera del gobierno.",
            tone="#1E3A5F", big=True)}
    {_card(fmt_mxn(_disc_monto),
            "Monto ejercido auditable",
            f"Los <b>{fmt_mxn(_disc_monto)}</b> que sí se pueden revisar representan el <b>{_disc_monto/_total_monto*100:.1f}%</b> del total federal en CDMX. El resto carece de datos públicos mínimos para fiscalizar.",
            tone="#B88A4A")}
    </div>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## Patrón #1 · Cómo se asignan los contratos que sí declaran modalidad

        Dentro del 6% auditable, los contratos se reparten entre **licitación pública** (proceso competido),
        **adjudicación directa** (un solo proveedor sin competencia) e **invitación a cuando menos tres**
        (competencia restringida a invitados). La ley permite las tres — pero solo la primera es abierta.
        """
    )
    return


@app.cell
def _(GOLD, NAVY, RUST, disc, fmt_mxn, go, pl):
    _by_mod = disc.group_by("mod").agg([
        pl.len().alias("n"),
        pl.col("monto_ejercido").sum().alias("monto"),
        pl.col("contratista").n_unique().alias("proveedores"),
    ]).sort("monto", descending=True).to_pandas()
    _total_n = _by_mod["n"].sum()
    _total_m = _by_mod["monto"].sum()
    _by_mod["pct_n"] = _by_mod["n"] / _total_n * 100
    _by_mod["pct_m"] = _by_mod["monto"] / _total_m * 100

    _color_map = {"Licitación pública": NAVY, "Adjudicación directa": RUST, "Invitación a 3": GOLD}
    _colors = [_color_map[m] for m in _by_mod["mod"]]

    _fig = go.Figure()
    _fig.add_trace(go.Bar(
        x=_by_mod["mod"], y=_by_mod["pct_n"],
        name="% de contratos", marker=dict(color=_colors),
        text=[f"{r['pct_n']:.1f}%<br>({r['n']:,} contratos · {r['proveedores']} proveedores)"
              for _, r in _by_mod.iterrows()],
        textposition="outside", textfont=dict(size=12, color="#0F172A"),
        hovertemplate="<b>%{x}</b><br>%{text}<extra></extra>",
        cliponaxis=False,
    ))
    _fig.update_layout(
        height=400,
        yaxis=dict(title="% de contratos auditables", ticksuffix="%", showgrid=True, gridcolor="#F1F5F9", range=[0,70]),
        xaxis=dict(title="", tickfont=dict(size=13, color="#0F172A")),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif"),
        margin=dict(l=50, r=30, t=60, b=40),
        showlegend=False,
    )
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin:12px 0 24px;">
        <div style="padding:16px 20px;background:#F8FAFC;border-left:4px solid #475569;border-radius:8px;">
        <div style="font-size:11px;letter-spacing:1.5px;color:#475569;text-transform:uppercase;font-weight:600;">Lecturas plausibles</div>
        <ul style="margin:8px 0 0 16px;padding:0;font-size:13px;color:#334155;line-height:1.6;">
          <li>32% en AD es legalmente permisible para montos menores (obra pública regida por LOPSRM) y urgencias.</li>
          <li>La mezcla refleja la composición real del gasto: muchos contratos pequeños bajo umbral + grandes obras licitadas.</li>
          <li>IR3 es el canal estándar para montos intermedios que no ameritan licitación completa.</li>
        </ul>
        </div>
        <div style="padding:16px 20px;background:#FEF2F2;border-left:4px solid #9A3412;border-radius:8px;">
        <div style="font-size:11px;letter-spacing:1.5px;color:#9A3412;text-transform:uppercase;font-weight:600;">Lo que verificaría un periodista</div>
        <ul style="margin:8px 0 0 16px;padding:0;font-size:13px;color:#7F1D1D;line-height:1.6;">
          <li>¿Los montos de adjudicación directa se mantienen por debajo de los topes legales (ej. LOPSRM art. 42)?</li>
          <li>¿Qué justificación técnica o de excepción se documentó? (pedir el dictamen fundado)</li>
          <li>¿Cómo cambió esta mezcla año con año? ¿Está aumentando la adjudicación directa?</li>
        </ul>
        </div>
        </div>
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## Patrón #2 · Las invitaciones restringidas son un club pequeño

        En **invitación a cuando menos tres personas**, solo participan 12 proveedores distintos — los 5
        más frecuentes recibieron el **98.4%** del dinero. La modalidad IR3 está diseñada para ser
        selectiva; el grado de concentración, sin embargo, merece explicación.
        """
    )
    return


@app.cell
def _(GOLD, NAVY, RUST, disc, fmt_mxn, go, pl):
    _rows = []
    for _m, _tone in [
        ("Licitación pública", NAVY),
        ("Adjudicación directa", RUST),
        ("Invitación a 3", GOLD),
    ]:
        _sub = disc.filter(pl.col("mod") == _m)
        if _sub.height == 0: continue
        _tot = _sub["monto_ejercido"].sum()
        _top = _sub.group_by("contratista").agg(pl.col("monto_ejercido").sum().alias("t")).sort("t", descending=True)
        _top5 = _top.head(5)["t"].sum() / _tot * 100
        _top10 = _top.head(10)["t"].sum() / _tot * 100
        _rows.append({
            "mod": _m, "tone": _tone,
            "proveedores": _top.height,
            "top5": _top5, "top10": _top10,
        })

    def _hex_to_rgba(h, a):
        h = h.lstrip("#")
        return f"rgba({int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)},{a})"

    _fig = go.Figure()
    for _r in _rows:
        _fig.add_trace(go.Bar(
            x=[_r["top5"]],
            y=[_r["mod"]],
            orientation="h",
            marker=dict(color=_r["tone"]),
            text=[f"top-5 = {_r['top5']:.1f}%"],
            textposition="inside", textfont=dict(size=11, color="white"),
            hoverinfo="skip",
            showlegend=False,
            name=f"top5_{_r['mod']}",
        ))
        _fig.add_trace(go.Bar(
            x=[_r["top10"] - _r["top5"]],
            y=[_r["mod"]],
            orientation="h",
            marker=dict(color=_hex_to_rgba(_r["tone"], 0.45)),
            text=[f"top-10 = {_r['top10']:.1f}%"],
            textposition="inside", textfont=dict(size=11, color="#0F172A"),
            hoverinfo="skip",
            showlegend=False,
            name=f"top10_{_r['mod']}",
        ))

    _fig.update_layout(
        height=320,
        barmode="stack",
        xaxis=dict(title="% del monto que captura el top de proveedores", ticksuffix="%",
                   showgrid=True, gridcolor="#F1F5F9", range=[0,105]),
        yaxis=dict(title="", tickfont=dict(size=13, color="#0F172A")),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif"),
        margin=dict(l=30, r=30, t=30, b=40),
        annotations=[
            dict(x=105, y=r["mod"], text=f"({r['proveedores']} proveedores únicos)",
                 showarrow=False, xanchor="left", font=dict(size=11, color="#64748B"))
            for r in _rows
        ],
    )
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin:12px 0 24px;">
        <div style="padding:16px 20px;background:#F8FAFC;border-left:4px solid #475569;border-radius:8px;">
        <div style="font-size:11px;letter-spacing:1.5px;color:#475569;text-transform:uppercase;font-weight:600;">Lecturas plausibles</div>
        <ul style="margin:8px 0 0 16px;padding:0;font-size:13px;color:#334155;line-height:1.6;">
          <li>Pocos proveedores están precalificados para el tipo técnico específico de obra.</li>
          <li>La modalidad IR3 se aplicó en un tipo de trabajo nicho (p.ej. especialidad eléctrica).</li>
          <li>El universo es pequeño (170 contratos) y puede estar sesgado por reporte parcial.</li>
        </ul>
        </div>
        <div style="padding:16px 20px;background:#FEF2F2;border-left:4px solid #9A3412;border-radius:8px;">
        <div style="font-size:11px;letter-spacing:1.5px;color:#9A3412;text-transform:uppercase;font-weight:600;">Lo que verificaría un periodista</div>
        <ul style="margin:8px 0 0 16px;padding:0;font-size:13px;color:#7F1D1D;line-height:1.6;">
          <li>¿Quiénes son los 3 invitados en cada IR3? ¿Son los mismos siempre?</li>
          <li>¿Cómo se integra la lista de proveedores precalificados? ¿Hay criterios públicos?</li>
          <li>Revisar actas de presentación de propuestas: ¿los "no ganadores" presentaron propuestas competitivas?</li>
        </ul>
        </div>
        </div>
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## Patrón #3 · Convocantes con un proveedor dominante

        Entre las unidades que publicaron al menos 3 contratos con proveedor identificado,
        estas son las que **concentraron ≥50% de su gasto en un solo proveedor**. Ordenadas
        por monto concentrado.
        """
    )
    return


@app.cell
def _(NAVY, RUST, disc, fmt_mxn, go, pl):
    _pairs = disc.group_by(["convocante", "contratista"]).agg(pl.col("monto_ejercido").sum().alias("mt"))
    _tot = disc.group_by("convocante").agg([
        pl.col("monto_ejercido").sum().alias("total"),
        pl.len().alias("n_total"),
    ])
    _hits = (
        _pairs.join(_tot, on="convocante")
              .with_columns((pl.col("mt") / pl.col("total") * 100).alias("pct"))
              .filter((pl.col("pct") >= 50) & (pl.col("n_total") >= 3))
              .sort("mt", descending=True)
              .head(12)
              .to_pandas()
              .iloc[::-1]
              .reset_index(drop=True)
    )
    _hits["label_y"] = _hits["convocante"].str.slice(0, 40) + " →<br>" + _hits["contratista"].str.slice(0, 40)
    _hits["text"] = [
        f"  {p:.0f}% · {fmt_mxn(m)} en {int(n)} contratos"
        for p, m, n in zip(_hits["pct"], _hits["mt"], _hits["n_total"])
    ]

    _fig = go.Figure(go.Bar(
        x=_hits["pct"], y=_hits["label_y"],
        orientation="h",
        marker=dict(color=_hits["pct"], colorscale=[[0, "#CBD5E1"], [1, RUST]], showscale=False),
        text=_hits["text"],
        textposition="outside", textfont=dict(size=11, color="#0F172A"),
        hovertemplate="<b>%{y}</b><br>%{text}<extra></extra>",
        cliponaxis=False,
    ))
    _fig.update_layout(
        height=max(400, 42 * len(_hits) + 80),
        xaxis=dict(title="% del gasto del convocante concentrado en el proveedor",
                   ticksuffix="%", showgrid=True, gridcolor="#F1F5F9", range=[0, 130]),
        yaxis=dict(title="", tickfont=dict(size=11, color="#0F172A")),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif"),
        margin=dict(l=10, r=260, t=20, b=40),
    )
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin:12px 0 24px;">
        <div style="padding:16px 20px;background:#F8FAFC;border-left:4px solid #475569;border-radius:8px;">
        <div style="font-size:11px;letter-spacing:1.5px;color:#475569;text-transform:uppercase;font-weight:600;">Lecturas plausibles</div>
        <ul style="margin:8px 0 0 16px;padding:0;font-size:13px;color:#334155;line-height:1.6;">
          <li>El proveedor es único especialista en un trabajo (p.ej. equipamiento patentado).</li>
          <li>Universo pequeño de contratos reportados por ese convocante — el denominador es frágil.</li>
          <li>Sucesiones de obra donde un proveedor ejecuta etapas continuas del mismo proyecto.</li>
        </ul>
        </div>
        <div style="padding:16px 20px;background:#FEF2F2;border-left:4px solid #9A3412;border-radius:8px;">
        <div style="font-size:11px;letter-spacing:1.5px;color:#9A3412;text-transform:uppercase;font-weight:600;">Lo que verificaría un periodista</div>
        <ul style="margin:8px 0 0 16px;padding:0;font-size:13px;color:#7F1D1D;line-height:1.6;">
          <li>Cruzar con CompraNet / ComprasMX: ¿el proveedor gana también en otros convocantes?</li>
          <li>Revisar padrones de precalificación: ¿cuántos proveedores había elegibles para esa licitación?</li>
          <li>Historial de parentescos o conflictos de interés entre funcionarios del convocante y representantes legales del proveedor.</li>
        </ul>
        </div>
        </div>
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## Patrón #4 · Los 15 proveedores más beneficiados por adjudicación directa

        Entre los **472 contratos adjudicados directamente** con proveedor identificado,
        estos son los 15 que más dinero recibieron. El tamaño y repetición no son por sí mismos
        evidencia de irregularidad — pero son la lista natural donde empezar una auditoría.
        """
    )
    return


@app.cell
def _(RUST, disc, fmt_mxn, go, pl):
    _ad = (
        disc.filter(pl.col("mod") == "Adjudicación directa")
            .group_by("contratista")
            .agg([
                pl.col("monto_ejercido").sum().alias("monto"),
                pl.len().alias("n"),
                pl.col("convocante").n_unique().alias("convocantes_distintos"),
            ])
            .sort("monto", descending=True)
            .head(15)
            .to_pandas()
            .iloc[::-1]
            .reset_index(drop=True)
    )
    _ad["label"] = [
        f"  {fmt_mxn(m)} · {int(n)} contratos · {int(c)} convocantes"
        for m, n, c in zip(_ad["monto"], _ad["n"], _ad["convocantes_distintos"])
    ]
    _ad["short"] = _ad["contratista"].str.slice(0, 55)

    _fig = go.Figure(go.Bar(
        x=_ad["monto"], y=_ad["short"],
        orientation="h",
        marker=dict(color=_ad["monto"], colorscale=[[0, "#FCA5A5"], [1, RUST]], showscale=False),
        text=_ad["label"], textposition="outside",
        textfont=dict(size=11, color="#334155"),
        hovertemplate="<b>%{customdata}</b><br>%{text}<extra></extra>",
        customdata=_ad["contratista"],
        cliponaxis=False,
    ))
    _fig.update_layout(
        height=560,
        margin=dict(l=10, r=240, t=10, b=30),
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9", tickformat=".2s", title="Monto ejercido en adjudicación directa"),
        yaxis=dict(title="", tickfont=dict(size=11, color="#0F172A")),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif"),
    )
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin:12px 0 24px;">
        <div style="padding:16px 20px;background:#F8FAFC;border-left:4px solid #475569;border-radius:8px;">
        <div style="font-size:11px;letter-spacing:1.5px;color:#475569;text-transform:uppercase;font-weight:600;">Lecturas plausibles</div>
        <ul style="margin:8px 0 0 16px;padding:0;font-size:13px;color:#334155;line-height:1.6;">
          <li>Especialización técnica: proveedores que dominan un nicho (áreas verdes, semaforización).</li>
          <li>Montos individuales dentro de topes legales para adjudicación directa.</li>
          <li>Continuidad operativa: contratos chicos recurrentes para mantenimiento rutinario.</li>
        </ul>
        </div>
        <div style="padding:16px 20px;background:#FEF2F2;border-left:4px solid #9A3412;border-radius:8px;">
        <div style="font-size:11px;letter-spacing:1.5px;color:#9A3412;text-transform:uppercase;font-weight:600;">Lo que verificaría un periodista</div>
        <ul style="margin:8px 0 0 16px;padding:0;font-size:13px;color:#7F1D1D;line-height:1.6;">
          <li>¿Cuántos proveedores similares existen en el mercado? (diagnosticar si la AD era inevitable)</li>
          <li>Sumar los contratos individuales del mismo proveedor con el mismo convocante: ¿rebasa el tope legal agregado?</li>
          <li>Verificar dictámenes de excepción fundada que deben acompañar cada AD.</li>
          <li>Revisar sanciones, inhabilitaciones o litigios del proveedor en CompraNet.</li>
        </ul>
        </div>
        </div>
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## Nota de método

        <div style="background:#F1F5F9;border-left:4px solid #1E3A5F;border-radius:10px;padding:18px 24px;font-size:13px;line-height:1.7;color:#1E293B;">
        <b>Qué incluye el universo auditable.</b>
        <ul style="margin:10px 0 0 20px;padding:0;">
          <li>Sólo <b>1,455 de 23,410 proyectos</b> (6.2%) con <code>desc_modalidad_contratacion</code> <em>y</em> <code>contratista</code> ambos publicados y distintos de la leyenda <em>"no reportó información"</em>.</li>
          <li>El resto (94%) simplemente no puede analizarse bajo esta lente — no por decisión nuestra, sino por ausencia del dato.</li>
          <li>Los umbrales legales de adjudicación directa varían por año y por fuente federal; aquí no aplicamos cortes — sólo reportamos agrupamientos.</li>
          <li>Un patrón extraño <b>no es evidencia de irregularidad</b>. Los umbrales aquí son estadísticos, no jurídicos.</li>
        </ul>
        </div>

        <div style="text-align:center;color:#64748B;font-size:12px;padding:20px 0 28px;">
        Fuente: <a href="https://datos.cdmx.gob.mx/dataset/rally-como-van-las-obras-cdmx" style="color:#1E3A5F;">Rally ¿Cómo van las obras? · Portal de Datos Abiertos CDMX</a>
        · Claude Mexico City Lab 2026 · Branch <code>red-team-accountability</code>
        </div>
        """
    )
    return


if __name__ == "__main__":
    app.run()
