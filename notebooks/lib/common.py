"""Shared presentation helpers for the Marimo notebooks.

Extracted from `notebooks/budget_dashboard.py` and `notebooks/obra_map.py` so
Agent 3's `notebooks/tus_100_pesos.py` can import a single source of truth for
formatting, palette, typography, Plotly styling, KPI cards, and the guinda hero
banner. The two source notebooks still inline their own copies and are frozen
demo artifacts — this module is additive, not a refactor of those files.
"""

from __future__ import annotations

CDMX_GUINDA = "#9F2241"
CDMX_GUINDA_DARK = "#691C32"

FONT = "Inter, -apple-system, system-ui, sans-serif"

PALETTE = [
    "#9F2241",
    "#E3007E",
    "#EC6730",
    "#00A489",
    "#00B7CD",
    "#6C4A7E",
    "#D6A461",
    "#3D5A80",
    "#C14953",
    "#2A9D8F",
]

RAMO_PALETTE = {
    "Aportaciones Federales para Entidades Federativas y Municipios": "#9F2241",
    "Provisiones Salariales y Económicas": "#EC6730",
    "Comunicaciones y Transportes": "#00B7CD",
    "Medio Ambiente y Recursos Naturales": "#00A489",
    "Salud": "#E3007E",
    "Educación Pública": "#6C4A7E",
    "Gobernación": "#3D5A80",
    "Cultura": "#D6A461",
    "Desarrollo Agrario, Territorial y Urbano": "#2A9D8F",
}


def fmt_mxn(v, short: bool = True) -> str:
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


def fmt_int(v) -> str:
    if v is None or v == 0:
        return "—"
    return f"{int(v):,}"


def style_fig(fig, height: int = 480, title: str | None = None):
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
            x=0.01,
            xanchor="left",
        ) if title else None,
    )
    return fig


def kpi_card(label: str, value: str, accent: str = CDMX_GUINDA, sub: str | None = None) -> str:
    sub_html = (
        f'<div style="font-size:11px;color:#64748B;margin-top:4px;'
        f'letter-spacing:0.5px;text-transform:uppercase;">{sub}</div>'
        if sub else ""
    )
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
        {sub_html}
    </div>
    """


def hero_banner(kicker: str, title: str, subtitle: str) -> str:
    return f"""
    <div style="
        padding: 36px 40px 28px;
        background: linear-gradient(135deg, {CDMX_GUINDA} 0%, {CDMX_GUINDA_DARK} 100%);
        color: white;
        border-radius: 14px;
        margin-bottom: 8px;
        box-shadow: 0 8px 24px rgba(159, 34, 65, 0.25);
    ">
        <div style="font-size: 13px; letter-spacing: 3px; opacity: 0.85; text-transform: uppercase; font-weight: 600;">
            {kicker}
        </div>
        <div style="font-size: 38px; font-weight: 700; margin-top: 6px; letter-spacing: -0.5px;">
            {title}
        </div>
        <div style="font-size: 15px; margin-top: 10px; opacity: 0.92; max-width: 820px; line-height: 1.55;">
            {subtitle}
        </div>
    </div>
    """
