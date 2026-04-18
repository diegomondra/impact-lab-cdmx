import marimo

__generated_with = "0.23.1"
app = marimo.App(
    width="full",
    app_title="Patrones extraños · auditoría forense de los datos abiertos",
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
            Auditoría forense · datos abiertos CDMX
        </div>
        <div style="font-size: 38px; font-weight: 700; margin-top: 6px; letter-spacing: -0.5px;">
            Patrones extraños.
        </div>
        <div style="font-size: 18px; margin-top: 8px; opacity: 0.85; font-weight: 400; max-width:820px; line-height:1.5;">
            Cuatro irregularidades estadísticas que aparecen cuando los datos públicos
            se examinan con herramientas forenses. <em>No son acusaciones.</em> Cada una
            tiene explicaciones inocentes plausibles — son el punto de partida para
            una pregunta, no para una sentencia.
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
        <b>Cómo leer este tablero.</b> Cada sección presenta un patrón, tres lecturas
        posibles (incluyendo las más mundanas), y la pregunta verificable que haría un reportero.
        El objetivo es localizar <em>dónde investigar</em>, no <em>concluir</em>.
        </div>
        """
    )
    return


@app.cell
def _():
    import marimo as mo
    from pathlib import Path
    from datetime import date
    import math
    from collections import Counter
    import polars as pl
    import plotly.express as px
    import plotly.graph_objects as go

    DATA_DIR = Path(__file__).parent.parent / "data"

    NAVY = "#1E3A5F"
    GOLD = "#B88A4A"
    RUST = "#9A3412"
    TEAL = "#0E7490"
    SLATE = "#475569"

    def fmt_mxn(v):
        if v is None or v == 0:
            return "—"
        v = float(v)
        if v >= 1e9: return f"${v/1e9:,.2f} mmdp"
        if v >= 1e6: return f"${v/1e6:,.1f} mdp"
        if v >= 1e3: return f"${v/1e3:,.0f} k"
        return f"${v:,.0f}"

    return Counter, DATA_DIR, GOLD, NAVY, RUST, SLATE, TEAL, date, fmt_mxn, go, math, mo, pl, px


@app.cell
def _(DATA_DIR, pl):
    raw = pl.read_csv(
        DATA_DIR / "rally_obras.csv",
        infer_schema_length=10_000,
        null_values=["NA", ""],
        truncate_ragged_lines=True,
        ignore_errors=True,
    ).with_columns([
        pl.col("latitud").cast(pl.Float64, strict=False),
        pl.col("longitud").cast(pl.Float64, strict=False),
        pl.col("monto_aprobado").fill_null(0),
        pl.col("monto_ejercido").fill_null(0),
        pl.col("inicio_proyecto").str.to_date(strict=False).alias("ini_dt"),
        pl.col("termino_proyecto").str.to_date(strict=False).alias("fin_dt"),
    ])
    return (raw,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## Patrón #1 · La distribución del primer dígito no es natural

        En datos financieros que surgen de procesos reales (costos, precios, ventas),
        la frecuencia del primer dígito tiende a seguir la **Ley de Benford** — el dígito **1**
        aparece primero ~30% de las veces, el **2** un 17%, y así hasta el **9** con ~5%.
        Los montos *aprobados* en CDMX siguen la curva casi perfectamente… **excepto en
        el 7**, que aparece casi 3 veces más de lo esperado.
        """
    )
    return


@app.cell
def _(Counter, GOLD, NAVY, RUST, go, math, raw):
    _amts = raw.filter(raw["monto_aprobado"] > 100)["monto_aprobado"].to_list()
    _first = Counter(str(int(a))[0] for a in _amts if a > 0)
    _total = sum(_first.values())
    _digits = list("123456789")
    _obs = [_first.get(d, 0) / _total * 100 for d in _digits]
    _exp = [math.log10(1 + 1 / int(d)) * 100 for d in _digits]
    _delta = [o - e for o, e in zip(_obs, _exp)]
    _colors = [RUST if abs(d) > 3 else NAVY for d in _delta]

    _fig = go.Figure()
    _fig.add_trace(go.Bar(
        x=_digits, y=_obs,
        name="Observado", marker=dict(color=_colors),
        hovertemplate="Dígito %{x}<br>Observado: %{y:.2f}%<extra></extra>",
        text=[f"{v:.1f}%" for v in _obs], textposition="outside",
        textfont=dict(size=11, color="#0F172A"),
    ))
    _fig.add_trace(go.Scatter(
        x=_digits, y=_exp,
        name="Esperado (Benford)", mode="lines+markers",
        line=dict(color=GOLD, width=3, dash="dash"),
        marker=dict(size=9, color=GOLD),
        hovertemplate="Dígito %{x}<br>Esperado: %{y:.2f}%<extra></extra>",
    ))
    _fig.update_layout(
        height=420,
        xaxis=dict(title="Primer dígito del monto aprobado", showgrid=False),
        yaxis=dict(title="% de los montos", showgrid=True, gridcolor="#F1F5F9", ticksuffix="%"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif"),
        margin=dict(l=50, r=30, t=40, b=40),
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
          <li>Montos estándar de programas federales centrados en $7M, $70k, $700 (productos catalogados).</li>
          <li>Techos presupuestales que se redondean repetidamente hacia rangos que empiezan con 7.</li>
          <li>Copiar-pegar de partidas plantilla donde el primer dígito se arrastra entre proyectos.</li>
        </ul>
        </div>
        <div style="padding:16px 20px;background:#FEF2F2;border-left:4px solid #9A3412;border-radius:8px;">
        <div style="font-size:11px;letter-spacing:1.5px;color:#9A3412;text-transform:uppercase;font-weight:600;">Lo que verificaría un periodista</div>
        <ul style="margin:8px 0 0 16px;padding:0;font-size:13px;color:#7F1D1D;line-height:1.6;">
          <li>Filtrar los montos que empiezan con 7 — ¿son casi todos iguales (ej. $7,500,000)?</li>
          <li>¿Pertenecen a una misma unidad responsable o programa presupuestario?</li>
          <li>¿Hay un catálogo público de precios unitarios que explique la concentración?</li>
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
        ## Patrón #2 · Demasiados números redondos

        En un catálogo de costos reales (insumos, horas-hombre, kilómetros de pavimento),
        la probabilidad de que un monto termine en seis ceros exactos es &lt;0.1%. Sin embargo,
        **el 12.6% de los montos aprobados mayores a $100k son exactamente divisibles entre
        un millón de pesos**, y el 28.6% entre cien mil.
        """
    )
    return


@app.cell
def _(GOLD, NAVY, go, pl, raw):
    _big = raw.filter(pl.col("monto_aprobado") >= 100_000)
    _levels = [
        ("Exactamente / $1,000,000", 1_000_000),
        ("/ $500,000", 500_000),
        ("/ $100,000", 100_000),
        ("/ $10,000", 10_000),
        ("/ $1,000", 1_000),
    ]
    _rows = []
    for _lbl, _div in _levels:
        _n = _big.filter((pl.col("monto_aprobado") % _div) == 0).height
        _rows.append({"lbl": _lbl, "pct": _n / _big.height * 100, "n": _n})

    _fig = go.Figure(go.Bar(
        x=[r["pct"] for r in _rows],
        y=[r["lbl"] for r in _rows],
        orientation="h",
        marker=dict(color=[NAVY, NAVY, NAVY, GOLD, GOLD]),
        text=[f"{r['pct']:.1f}% · {r['n']:,} proyectos" for r in _rows],
        textposition="outside", textfont=dict(size=12, color="#0F172A"),
        hovertemplate="<b>%{y}</b><br>%{text}<extra></extra>",
        cliponaxis=False,
    ))
    _fig.update_layout(
        height=320,
        xaxis=dict(title="% del universo de proyectos >$100k", ticksuffix="%", showgrid=True, gridcolor="#F1F5F9", range=[0, 55]),
        yaxis=dict(title="", tickfont=dict(size=12, color="#0F172A")),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif"),
        margin=dict(l=10, r=180, t=10, b=40),
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
          <li>Techos presupuestales fijados por decreto (p.ej. "cada alcaldía recibe $1M para X").</li>
          <li>Fórmulas de distribución que generan sumas redondas por construcción.</li>
          <li>Asignaciones iniciales que se definen primero y costean después.</li>
        </ul>
        </div>
        <div style="padding:16px 20px;background:#FEF2F2;border-left:4px solid #9A3412;border-radius:8px;">
        <div style="font-size:11px;letter-spacing:1.5px;color:#9A3412;text-transform:uppercase;font-weight:600;">Lo que verificaría un periodista</div>
        <ul style="margin:8px 0 0 16px;padding:0;font-size:13px;color:#7F1D1D;line-height:1.6;">
          <li>¿Existe un expediente técnico detallado para cada monto redondo, o son asignaciones forfaitarias?</li>
          <li>¿Cómo cambia <code>monto_modificado</code> respecto al <code>aprobado</code> redondo? (indicador de costeo real posterior).</li>
          <li>Cruzar con el <em>Anexo 20</em> del PEF para confirmar si son techos federales vs. asignaciones locales.</li>
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
        ## Patrón #3 · Coordenadas que acumulan muchos proyectos distintos

        Hay **49 pares de coordenadas exactas** donde aparecen **3 o más proyectos con nombres
        diferentes**. Entre ellos concentran **$61.5 mmdp** — casi todo el dinero ejercido.
        Las coordenadas más repetidas son la puerta del palacio de cada alcaldía: direcciones
        genéricas usadas como punto de reporte cuando el proyecto real está disperso.
        """
    )
    return


@app.cell
def _(fmt_mxn, go, pl, raw):
    _dup = (
        raw.filter(pl.col("latitud").is_not_null())
           .group_by(["latitud", "longitud"])
           .agg([
               pl.col("nombre_proyecto").n_unique().alias("distinct_names"),
               pl.len().alias("n_rows"),
               pl.col("monto_ejercido").sum().alias("monto"),
               pl.col("desc_alcaldia").first().alias("alcaldia"),
               pl.col("direccion_proyecto").first().alias("direccion"),
           ])
           .filter(pl.col("distinct_names") >= 3)
           .sort("n_rows", descending=True)
           .head(15)
           .to_pandas()
    )
    _dup["label"] = _dup["alcaldia"].fillna("—") + " · " + _dup["direccion"].fillna("—").str.slice(0, 45)
    _dup = _dup.iloc[::-1].reset_index(drop=True)

    _fig = go.Figure(go.Bar(
        x=_dup["n_rows"], y=_dup["label"],
        orientation="h",
        marker=dict(color=_dup["monto"], colorscale=[[0, "#CBD5E1"], [1, "#1E3A5F"]], showscale=False),
        text=[f"{n:,} proyectos · {fmt_mxn(m)}" for n, m in zip(_dup["n_rows"], _dup["monto"])],
        textposition="outside",
        textfont=dict(size=11, color="#0F172A"),
        hovertemplate="<b>%{y}</b><br>%{text}<extra></extra>",
        cliponaxis=False,
    ))
    _fig.update_layout(
        height=560,
        margin=dict(l=10, r=200, t=10, b=30),
        xaxis=dict(title="Número de proyectos reportados en la misma coordenada exacta",
                   showgrid=True, gridcolor="#F1F5F9"),
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
          <li>Captura por defecto: el sistema exige lat/long y usan la dirección de la oficina.</li>
          <li>Programas transversales (mantenimiento vial, alumbrado) que se ejecutan en toda la alcaldía pero se reportan al domicilio administrativo.</li>
          <li>Proyectos auténticamente ubicados en un mismo complejo (plaza principal, deportivo).</li>
        </ul>
        </div>
        <div style="padding:16px 20px;background:#FEF2F2;border-left:4px solid #9A3412;border-radius:8px;">
        <div style="font-size:11px;letter-spacing:1.5px;color:#9A3412;text-transform:uppercase;font-weight:600;">Lo que verificaría un periodista</div>
        <ul style="margin:8px 0 0 16px;padding:0;font-size:13px;color:#7F1D1D;line-height:1.6;">
          <li>Pedir las direcciones reales o polígonos de ejecución por oficio de transparencia.</li>
          <li>Para un proyecto específico: visitar la dirección. ¿Es una oficina o es la obra?</li>
          <li>¿Cómo se hace la auditoría física si el punto georreferenciado no es el sitio real?</li>
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
        ## Patrón #4 · Fechas imposibles

        Entre los proyectos con fechas de inicio y término registradas,
        **3,195 tienen término anterior al inicio** (~14%). Otros 32 duran cero días.
        Seis proyectos reportan duraciones mayores a 10 años.
        """
    )
    return


@app.cell
def _(NAVY, RUST, SLATE, go, pl, raw):
    _both = raw.filter(pl.col("ini_dt").is_not_null() & pl.col("fin_dt").is_not_null())
    _back = _both.filter(pl.col("fin_dt") < pl.col("ini_dt")).height
    _same = _both.filter(pl.col("fin_dt") == pl.col("ini_dt")).height
    _long = _both.with_columns((pl.col("fin_dt") - pl.col("ini_dt")).dt.total_days().alias("d")).filter(pl.col("d") > 3650).height
    _normal = _both.height - _back - _same - _long

    _cats = ["OK (rango válido)", "Término = Inicio (0 días)", "Duración > 10 años", "Término ANTES del inicio"]
    _vals = [_normal, _same, _long, _back]
    _cols = [SLATE, NAVY, NAVY, RUST]

    _fig = go.Figure(go.Bar(
        x=_cats, y=_vals,
        marker=dict(color=_cols),
        text=[f"{v:,}" for v in _vals], textposition="outside",
        textfont=dict(size=13, color="#0F172A"),
        hovertemplate="<b>%{x}</b><br>%{y:,} proyectos<extra></extra>",
    ))
    _fig.update_layout(
        height=380,
        xaxis=dict(title=""),
        yaxis=dict(title="Proyectos", showgrid=True, gridcolor="#F1F5F9", type="log"),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif"),
        margin=dict(l=60, r=30, t=40, b=60),
        annotations=[dict(
            text="(escala logarítmica)", x=1, y=-0.2, xref="paper", yref="paper",
            showarrow=False, font=dict(size=10, color="#94A3B8"),
        )],
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
          <li>Errores de captura — meses intercambiados, formatos invertidos entre DD-MM y MM-DD.</li>
          <li>Convenciones administrativas: "inicio" registrado como fecha de firma, "término" como fecha del acta.</li>
          <li>Proyectos plurianuales cuyo registro captura sólo la ventana fiscal de un año.</li>
        </ul>
        </div>
        <div style="padding:16px 20px;background:#FEF2F2;border-left:4px solid #9A3412;border-radius:8px;">
        <div style="font-size:11px;letter-spacing:1.5px;color:#9A3412;text-transform:uppercase;font-weight:600;">Lo que verificaría un periodista</div>
        <ul style="margin:8px 0 0 16px;padding:0;font-size:13px;color:#7F1D1D;line-height:1.6;">
          <li>¿Existe validación de rango en el sistema de captura? ¿Por qué permite fin &lt; inicio?</li>
          <li>¿Los mismos registros tienen el resto de sus campos bien capturados?</li>
          <li>Pedir el acta o contrato en esos 3,195 casos — las fechas ahí deberían ser consistentes.</li>
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
        <b>Sobre lo que este tablero es — y lo que no es.</b>
        <ul style="margin:10px 0 0 20px;padding:0;">
          <li>Es una <b>auditoría de consistencia interna del dataset público</b>. No usamos fuentes externas; sólo el archivo que la CDMX publica.</li>
          <li>Las irregularidades pueden tener explicaciones legítimas. Las secciones <em>"lecturas plausibles"</em> muestran las más mundanas.</li>
          <li>Un patrón extraño no es evidencia — es <b>una señal de dónde vale la pena preguntar más</b>.</li>
          <li>Los criterios numéricos exactos están en el código. El notebook es reproducible: <code>uv run marimo edit notebooks/patrones.py</code>.</li>
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
