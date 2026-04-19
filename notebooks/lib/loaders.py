"""Data loaders for the Marimo notebooks.

Every loader reads from `data/clean/` (Agent 1's output) if the file exists,
and otherwise returns a small inline fixture so Agent 3 can build the UI from
minute zero. A fallback emits a loud warning to stderr so no one demos on
fixtures by accident.

Contract: `data/clean/SCHEMAS.md`. Column names and dtypes here must match.
"""

from __future__ import annotations

import sys
from pathlib import Path

import polars as pl

DATA_CLEAN = Path(__file__).resolve().parent.parent.parent / "data" / "clean"

_FIXTURE_YEAR = 2024


def _warn_fixture(name: str, path: Path) -> None:
    print(
        f"[notebooks/lib/loaders.py] WARNING: {name} falling back to inline "
        f"fixture — expected file not found at {path}. "
        f"Do NOT demo on this data.",
        file=sys.stderr,
        flush=True,
    )


# ---------------------------------------------------------------------------
# budget_tree
# ---------------------------------------------------------------------------

_BUDGET_TREE_FIXTURE_ROWS: list[dict] = [
    # --- Level 1 ---
    {"source_id": "L1-transporte",   "level": 1, "citizen_category": "Transporte público",        "display_name": "Transporte público",        "parent_id": None, "icon": "🚌", "monto_aprobado": 42_000_000_000.0, "monto_ejercido": None, "per_100_of_total": 14.7, "per_100_of_parent": None, "rationale": "Metro, Metrobús, RTP, Cablebús y trolebuses — la red que mueve a la ciudad.",                                    "year": _FIXTURE_YEAR},
    {"source_id": "L1-agua",         "level": 1, "citizen_category": "Agua",                      "display_name": "Agua",                      "parent_id": None, "icon": "💧", "monto_aprobado": 18_500_000_000.0, "monto_ejercido": None, "per_100_of_total": 6.5,  "per_100_of_parent": None, "rationale": "Operación, potabilización, drenaje y sectorización a cargo de SACMEX.",                                       "year": _FIXTURE_YEAR},
    {"source_id": "L1-seguridad",    "level": 1, "citizen_category": "Seguridad",                 "display_name": "Seguridad",                 "parent_id": None, "icon": "🛡️", "monto_aprobado": 28_200_000_000.0, "monto_ejercido": None, "per_100_of_total": 9.9,  "per_100_of_parent": None, "rationale": "Policía preventiva, C5, bomberos y protección civil.",                                                         "year": _FIXTURE_YEAR},
    {"source_id": "L1-salud",        "level": 1, "citizen_category": "Salud",                     "display_name": "Salud",                     "parent_id": None, "icon": "🏥", "monto_aprobado": 22_800_000_000.0, "monto_ejercido": None, "per_100_of_total": 8.0,  "per_100_of_parent": None, "rationale": "Hospitales, centros de salud, medicamentos y atención a poblaciones prioritarias.",                            "year": _FIXTURE_YEAR},
    {"source_id": "L1-educacion",    "level": 1, "citizen_category": "Educación",                 "display_name": "Educación",                 "parent_id": None, "icon": "📚", "monto_aprobado": 14_700_000_000.0, "monto_ejercido": None, "per_100_of_total": 5.2,  "per_100_of_parent": None, "rationale": "Escuelas, becas y programas de aprendizaje a lo largo de la vida.",                                             "year": _FIXTURE_YEAR},
    {"source_id": "L1-apoyos",       "level": 1, "citizen_category": "Apoyos sociales",           "display_name": "Apoyos sociales",           "parent_id": None, "icon": "🤝", "monto_aprobado": 35_400_000_000.0, "monto_ejercido": None, "per_100_of_total": 12.4, "per_100_of_parent": None, "rationale": "Transferencias directas: pensiones, becas y apoyos a personas adultas mayores y jóvenes.",                     "year": _FIXTURE_YEAR},
    {"source_id": "L1-calles",       "level": 1, "citizen_category": "Calles y banquetas",        "display_name": "Calles y banquetas",        "parent_id": None, "icon": "🛣️", "monto_aprobado": 9_800_000_000.0,  "monto_ejercido": None, "per_100_of_total": 3.4,  "per_100_of_parent": None, "rationale": "Pavimentación, bacheo, banquetas y señalización vial.",                                                         "year": _FIXTURE_YEAR},
    {"source_id": "L1-basura",       "level": 1, "citizen_category": "Basura y limpia",           "display_name": "Basura y limpia",           "parent_id": None, "icon": "🗑️", "monto_aprobado": 6_200_000_000.0,  "monto_ejercido": None, "per_100_of_total": 2.2,  "per_100_of_parent": None, "rationale": "Recolección, transferencia y tratamiento de residuos sólidos.",                                                 "year": _FIXTURE_YEAR},
    {"source_id": "L1-parques",      "level": 1, "citizen_category": "Parques y espacios públicos", "display_name": "Parques y espacios públicos", "parent_id": None, "icon": "🌳", "monto_aprobado": 4_800_000_000.0,  "monto_ejercido": None, "per_100_of_total": 1.7,  "per_100_of_parent": None, "rationale": "Mantenimiento y creación de parques, plazas y arbolado urbano.",                                              "year": _FIXTURE_YEAR},
    {"source_id": "L1-gobierno",     "level": 1, "citizen_category": "Gobierno y administración", "display_name": "Gobierno y administración", "parent_id": None, "icon": "🏛️", "monto_aprobado": 38_500_000_000.0, "monto_ejercido": None, "per_100_of_total": 13.5, "per_100_of_parent": None, "rationale": "Funciones administrativas, recaudación, planeación y operación interna del gobierno.",                         "year": _FIXTURE_YEAR},
    {"source_id": "L1-deuda",        "level": 1, "citizen_category": "Deuda",                     "display_name": "Deuda",                     "parent_id": None, "icon": "💰", "monto_aprobado": 8_900_000_000.0,  "monto_ejercido": None, "per_100_of_total": 3.1,  "per_100_of_parent": None, "rationale": "Pago de intereses y amortización de deuda pública.",                                                            "year": _FIXTURE_YEAR},
    {"source_id": "L1-otros",        "level": 1, "citizen_category": "Otros",                     "display_name": "Otros",                     "parent_id": None, "icon": "•",   "monto_aprobado": 55_000_000_000.0, "monto_ejercido": None, "per_100_of_total": 19.3, "per_100_of_parent": None, "rationale": "Categorías adicionales y rubros menores. Se detallan en la metodología.",                                     "year": _FIXTURE_YEAR},

    # --- Level 2 ---
    {"source_id": "L2-metro-mant",    "level": 2, "citizen_category": "Transporte público", "display_name": "Metro · mantenimiento y operación", "parent_id": "L1-transporte", "icon": None, "monto_aprobado": 17_500_000_000.0, "monto_ejercido": None, "per_100_of_total": 6.1, "per_100_of_parent": 41.7, "rationale": "Sistema de Transporte Colectivo Metro — la mayor partida de transporte.",                                    "year": _FIXTURE_YEAR},
    {"source_id": "L2-metrobus",      "level": 2, "citizen_category": "Transporte público", "display_name": "Metrobús",                        "parent_id": "L1-transporte", "icon": None, "monto_aprobado": 4_200_000_000.0,  "monto_ejercido": None, "per_100_of_total": 1.5, "per_100_of_parent": 10.0, "rationale": "Operación y mantenimiento del sistema Metrobús en sus siete líneas.",                                        "year": _FIXTURE_YEAR},
    {"source_id": "L2-cablebus-l3",   "level": 2, "citizen_category": "Transporte público", "display_name": "Cablebús Línea 3",                "parent_id": "L1-transporte", "icon": None, "monto_aprobado": 3_100_000_000.0,  "monto_ejercido": None, "per_100_of_total": 1.1, "per_100_of_parent": 7.4,  "rationale": "Construcción de la Línea 3 del Cablebús (Chapultepec – Los Pinos – Vasco de Quiroga).",                      "year": _FIXTURE_YEAR},
    {"source_id": "L2-rtp",           "level": 2, "citizen_category": "Transporte público", "display_name": "RTP · Red de Transporte de Pasajeros","parent_id": "L1-transporte", "icon": None, "monto_aprobado": 2_400_000_000.0,  "monto_ejercido": None, "per_100_of_total": 0.8, "per_100_of_parent": 5.7,  "rationale": "Operación de la flota RTP y renovación de autobuses.",                                                       "year": _FIXTURE_YEAR},

    {"source_id": "L2-sacmex-op",     "level": 2, "citizen_category": "Agua",              "display_name": "SACMEX · Operación hidráulica",    "parent_id": "L1-agua",       "icon": None, "monto_aprobado": 11_200_000_000.0, "monto_ejercido": None, "per_100_of_total": 3.9, "per_100_of_parent": 60.5, "rationale": "Operación cotidiana del sistema de agua potable y drenaje.",                                                 "year": _FIXTURE_YEAR},
    {"source_id": "L2-sectorizacion", "level": 2, "citizen_category": "Agua",              "display_name": "Sectorización Iztapalapa",         "parent_id": "L1-agua",       "icon": None, "monto_aprobado": 2_600_000_000.0,  "monto_ejercido": None, "per_100_of_total": 0.9, "per_100_of_parent": 14.1, "rationale": "Obra mayor para garantizar abasto continuo en alcaldías del oriente.",                                        "year": _FIXTURE_YEAR},

    {"source_id": "L2-policia-pr",    "level": 2, "citizen_category": "Seguridad",         "display_name": "Policía preventiva",               "parent_id": "L1-seguridad",  "icon": None, "monto_aprobado": 18_900_000_000.0, "monto_ejercido": None, "per_100_of_total": 6.6, "per_100_of_parent": 67.0, "rationale": "Sueldos, equipamiento y operación de la policía preventiva de la SSC.",                                       "year": _FIXTURE_YEAR},
    {"source_id": "L2-c5",            "level": 2, "citizen_category": "Seguridad",         "display_name": "C5 · videovigilancia y 9-1-1",     "parent_id": "L1-seguridad",  "icon": None, "monto_aprobado": 3_400_000_000.0,  "monto_ejercido": None, "per_100_of_total": 1.2, "per_100_of_parent": 12.1, "rationale": "Centro de Comando, Control, Cómputo, Comunicaciones y Contacto Ciudadano.",                                   "year": _FIXTURE_YEAR},

    {"source_id": "L2-pilares",       "level": 2, "citizen_category": "Apoyos sociales",   "display_name": "Pilares",                         "parent_id": "L1-apoyos",     "icon": None, "monto_aprobado": 2_900_000_000.0,  "monto_ejercido": None, "per_100_of_total": 1.0, "per_100_of_parent": 8.2,  "rationale": "Puntos de Innovación, Libertad, Arte, Educación y Saberes — red de centros comunitarios.",                    "year": _FIXTURE_YEAR},
    {"source_id": "L2-mi-beca",       "level": 2, "citizen_category": "Apoyos sociales",   "display_name": "Mi Beca para Empezar",            "parent_id": "L1-apoyos",     "icon": None, "monto_aprobado": 4_100_000_000.0,  "monto_ejercido": None, "per_100_of_total": 1.4, "per_100_of_parent": 11.6, "rationale": "Apoyo universal a estudiantes de escuelas públicas de educación básica.",                                     "year": _FIXTURE_YEAR},
    {"source_id": "L2-pens-am",       "level": 2, "citizen_category": "Apoyos sociales",   "display_name": "Pensión adultos mayores",         "parent_id": "L1-apoyos",     "icon": None, "monto_aprobado": 12_800_000_000.0, "monto_ejercido": None, "per_100_of_total": 4.5, "per_100_of_parent": 36.2, "rationale": "Transferencia directa a personas adultas mayores residentes en la CDMX.",                                     "year": _FIXTURE_YEAR},

    {"source_id": "L2-hospitales",    "level": 2, "citizen_category": "Salud",             "display_name": "Hospitales y centros de salud",    "parent_id": "L1-salud",      "icon": None, "monto_aprobado": 15_300_000_000.0, "monto_ejercido": None, "per_100_of_total": 5.4, "per_100_of_parent": 67.1, "rationale": "Operación de la red hospitalaria y centros de salud de la Secretaría de Salud CDMX.",                         "year": _FIXTURE_YEAR},

    {"source_id": "L2-escuelas",      "level": 2, "citizen_category": "Educación",         "display_name": "Escuelas · mantenimiento y operación","parent_id": "L1-educacion",  "icon": None, "monto_aprobado": 8_200_000_000.0,  "monto_ejercido": None, "per_100_of_total": 2.9, "per_100_of_parent": 55.8, "rationale": "Operación de planteles educativos bajo tutela local.",                                                        "year": _FIXTURE_YEAR},
]

_BUDGET_TREE_SCHEMA = {
    "source_id":         pl.Utf8,
    "level":             pl.Int32,
    "citizen_category":  pl.Utf8,
    "display_name":      pl.Utf8,
    "parent_id":         pl.Utf8,
    "icon":              pl.Utf8,
    "monto_aprobado":    pl.Float64,
    "monto_ejercido":    pl.Float64,
    "per_100_of_total":  pl.Float64,
    "per_100_of_parent": pl.Float64,
    "rationale":         pl.Utf8,
    "year":              pl.Int32,
}


def _budget_tree_fixture() -> pl.DataFrame:
    return pl.DataFrame(_BUDGET_TREE_FIXTURE_ROWS, schema=_BUDGET_TREE_SCHEMA)


def load_budget_tree(year: int | None = None) -> pl.DataFrame:
    """Return the Level-1+2 citizen-category budget tree.

    Filters to `year` if provided; otherwise returns all years in the file.
    Falls back to a hardcoded fixture (year=2024) if the file is missing.
    """
    path = DATA_CLEAN / "budget_tree.parquet"
    if path.exists():
        df = pl.read_parquet(path)
    else:
        _warn_fixture("load_budget_tree", path)
        df = _budget_tree_fixture()

    if year is not None:
        df = df.filter(pl.col("year") == year)
    return df


# ---------------------------------------------------------------------------
# budget_by_alcaldia
# ---------------------------------------------------------------------------

_ALCALDIA_FIXTURE_ROWS: list[dict] = [
    {"source_id": "L1-transporte", "level": 1, "alcaldia": "Iztapalapa",  "citizen_category": "Transporte público", "display_name": "Transporte público", "monto_aprobado": 6_400_000_000.0, "monto_ejercido": None, "per_100_of_alcaldia_total": 18.2, "attribution_method": "heuristic_unidad_responsable", "year": _FIXTURE_YEAR},
    {"source_id": "L1-agua",       "level": 1, "alcaldia": "Iztapalapa",  "citizen_category": "Agua",               "display_name": "Agua",               "monto_aprobado": 4_800_000_000.0, "monto_ejercido": None, "per_100_of_alcaldia_total": 13.6, "attribution_method": "recursos_transferidos",         "year": _FIXTURE_YEAR},
    {"source_id": "L1-apoyos",     "level": 1, "alcaldia": "Iztapalapa",  "citizen_category": "Apoyos sociales",    "display_name": "Apoyos sociales",    "monto_aprobado": 7_200_000_000.0, "monto_ejercido": None, "per_100_of_alcaldia_total": 20.4, "attribution_method": "modeled",                       "year": _FIXTURE_YEAR},
    {"source_id": "L1-transporte", "level": 1, "alcaldia": "Cuauhtémoc",  "citizen_category": "Transporte público", "display_name": "Transporte público", "monto_aprobado": 5_100_000_000.0, "monto_ejercido": None, "per_100_of_alcaldia_total": 22.1, "attribution_method": "heuristic_unidad_responsable", "year": _FIXTURE_YEAR},
    {"source_id": "L1-seguridad",  "level": 1, "alcaldia": "Cuauhtémoc",  "citizen_category": "Seguridad",          "display_name": "Seguridad",          "monto_aprobado": 3_900_000_000.0, "monto_ejercido": None, "per_100_of_alcaldia_total": 16.9, "attribution_method": "heuristic_unidad_responsable", "year": _FIXTURE_YEAR},
    {"source_id": "L1-agua",       "level": 1, "alcaldia": "Álvaro Obregón","citizen_category": "Agua",             "display_name": "Agua",               "monto_aprobado": 1_900_000_000.0, "monto_ejercido": None, "per_100_of_alcaldia_total": 11.2, "attribution_method": "recursos_transferidos",         "year": _FIXTURE_YEAR},
    {"source_id": "L2-cablebus-l3","level": 2, "alcaldia": "Álvaro Obregón","citizen_category": "Transporte público","display_name": "Cablebús Línea 3",   "monto_aprobado": 1_400_000_000.0, "monto_ejercido": None, "per_100_of_alcaldia_total": 8.3,  "attribution_method": "modeled",                       "year": _FIXTURE_YEAR},
    {"source_id": "L2-sectorizacion","level": 2, "alcaldia": "Iztapalapa","citizen_category": "Agua",               "display_name": "Sectorización Iztapalapa", "monto_aprobado": 2_600_000_000.0, "monto_ejercido": None, "per_100_of_alcaldia_total": 7.4, "attribution_method": "modeled",                       "year": _FIXTURE_YEAR},
]

_ALCALDIA_SCHEMA = {
    "source_id":                 pl.Utf8,
    "level":                     pl.Int32,
    "alcaldia":                  pl.Utf8,
    "citizen_category":          pl.Utf8,
    "display_name":              pl.Utf8,
    "monto_aprobado":            pl.Float64,
    "monto_ejercido":            pl.Float64,
    "per_100_of_alcaldia_total": pl.Float64,
    "attribution_method":        pl.Utf8,
    "year":                      pl.Int32,
}


def _alcaldia_fixture() -> pl.DataFrame:
    return pl.DataFrame(_ALCALDIA_FIXTURE_ROWS, schema=_ALCALDIA_SCHEMA)


def load_budget_by_alcaldia() -> pl.DataFrame | None:
    """Return alcaldía-sliced budget tree, or None if unavailable.

    Agent 1 may conclude alcaldía-level data is not viable; in that case the
    file never appears and the loader returns None. Agent 3 should hide the
    alcaldía filter when None is returned.

    When the file is missing *and* no decision has been recorded, returns the
    fixture with a stderr warning so Agent 3 can still build the UI branch.
    """
    path = DATA_CLEAN / "budget_by_alcaldia.parquet"
    if path.exists():
        return pl.read_parquet(path)

    sentinel = DATA_CLEAN / "budget_by_alcaldia.SKIP"
    if sentinel.exists():
        return None

    _warn_fixture("load_budget_by_alcaldia", path)
    return _alcaldia_fixture()


# ---------------------------------------------------------------------------
# income_sources
# ---------------------------------------------------------------------------

_INCOME_FIXTURE_ROWS: list[dict] = [
    {"source_id": "ING-participaciones", "display_name": "Participaciones federales",             "category": "federal_participaciones", "monto": 95_000_000_000.0, "per_100_of_total": 33.3, "year": _FIXTURE_YEAR},
    {"source_id": "ING-aportaciones",    "display_name": "Aportaciones federales (FAIS, FASSA, …)","category": "federal_aportaciones",    "monto": 28_000_000_000.0, "per_100_of_total": 9.8,  "year": _FIXTURE_YEAR},
    {"source_id": "ING-predial",         "display_name": "Impuesto predial",                      "category": "impuestos_locales",       "monto": 22_000_000_000.0, "per_100_of_total": 7.7,  "year": _FIXTURE_YEAR},
    {"source_id": "ING-tenencia",        "display_name": "Tenencia vehicular y otros impuestos",  "category": "impuestos_locales",       "monto": 18_000_000_000.0, "per_100_of_total": 6.3,  "year": _FIXTURE_YEAR},
    {"source_id": "ING-derechos-agua",   "display_name": "Derechos por suministro de agua",       "category": "derechos",                "monto": 9_000_000_000.0,  "per_100_of_total": 3.2,  "year": _FIXTURE_YEAR},
    {"source_id": "ING-otros-derechos",  "display_name": "Otros derechos y aprovechamientos",     "category": "aprovechamientos",        "monto": 14_000_000_000.0, "per_100_of_total": 4.9,  "year": _FIXTURE_YEAR},
    {"source_id": "ING-financiamiento",  "display_name": "Financiamiento (deuda neta)",           "category": "financiamiento",          "monto": 7_000_000_000.0,  "per_100_of_total": 2.5,  "year": _FIXTURE_YEAR},
    {"source_id": "ING-otros",           "display_name": "Otros ingresos",                        "category": "otros",                   "monto": 91_800_000_000.0, "per_100_of_total": 32.3, "year": _FIXTURE_YEAR},
]

_INCOME_SCHEMA = {
    "source_id":        pl.Utf8,
    "display_name":     pl.Utf8,
    "category":         pl.Utf8,
    "monto":            pl.Float64,
    "per_100_of_total": pl.Float64,
    "year":             pl.Int32,
}


def _income_fixture() -> pl.DataFrame:
    return pl.DataFrame(_INCOME_FIXTURE_ROWS, schema=_INCOME_SCHEMA)


def load_income_sources() -> pl.DataFrame:
    """Return the ingresos breakdown, one row per aggregated category per year."""
    path = DATA_CLEAN / "income_sources.parquet"
    if path.exists():
        return pl.read_parquet(path)
    _warn_fixture("load_income_sources", path)
    return _income_fixture()


# ---------------------------------------------------------------------------
# source_links
# ---------------------------------------------------------------------------

_SOURCE_LINKS_FIXTURE: dict[str, str] = {
    "L1-transporte":     "https://datos.cdmx.gob.mx/dataset/presupuesto-de-egresos",
    "L1-agua":           "https://datos.cdmx.gob.mx/dataset/presupuesto-de-egresos",
    "L1-seguridad":      "https://datos.cdmx.gob.mx/dataset/presupuesto-de-egresos",
    "L1-salud":          "https://datos.cdmx.gob.mx/dataset/presupuesto-de-egresos",
    "L1-educacion":      "https://datos.cdmx.gob.mx/dataset/presupuesto-de-egresos",
    "L1-apoyos":         "https://datos.cdmx.gob.mx/dataset/presupuesto-de-egresos",
    "L1-calles":         "https://datos.cdmx.gob.mx/dataset/presupuesto-de-egresos",
    "L1-basura":         "https://datos.cdmx.gob.mx/dataset/presupuesto-de-egresos",
    "L1-parques":        "https://datos.cdmx.gob.mx/dataset/presupuesto-de-egresos",
    "L1-gobierno":       "https://datos.cdmx.gob.mx/dataset/presupuesto-de-egresos",
    "L1-deuda":          "https://datos.cdmx.gob.mx/dataset/presupuesto-de-egresos",
    "L1-otros":          "https://datos.cdmx.gob.mx/dataset/presupuesto-de-egresos",
    "L2-metro-mant":     "https://tudinero.cdmx.gob.mx",
    "L2-metrobus":       "https://tudinero.cdmx.gob.mx",
    "L2-cablebus-l3":    "https://tudinero.cdmx.gob.mx",
    "L2-rtp":            "https://tudinero.cdmx.gob.mx",
    "L2-sacmex-op":      "https://tudinero.cdmx.gob.mx",
    "L2-sectorizacion":  "https://tudinero.cdmx.gob.mx",
    "L2-policia-pr":     "https://tudinero.cdmx.gob.mx",
    "L2-c5":             "https://tudinero.cdmx.gob.mx",
    "L2-pilares":        "https://tudinero.cdmx.gob.mx",
    "L2-mi-beca":        "https://tudinero.cdmx.gob.mx",
    "L2-pens-am":        "https://tudinero.cdmx.gob.mx",
    "L2-hospitales":     "https://tudinero.cdmx.gob.mx",
    "L2-escuelas":       "https://tudinero.cdmx.gob.mx",
}


def load_source_links() -> dict[str, str]:
    """Return a `source_id -> url` dict for "Ver en datos oficiales" links."""
    path = DATA_CLEAN / "source_links.csv"
    if path.exists():
        df = pl.read_csv(path)
        return dict(zip(df["source_id"].to_list(), df["url"].to_list()))
    _warn_fixture("load_source_links", path)
    return dict(_SOURCE_LINKS_FIXTURE)


# ---------------------------------------------------------------------------
# available_years
# ---------------------------------------------------------------------------

def available_years() -> list[int]:
    """Return sorted list of fiscal years present in budget_tree.parquet."""
    path = DATA_CLEAN / "budget_tree.parquet"
    if path.exists():
        df = pl.read_parquet(path, columns=["year"])
        return sorted({int(y) for y in df["year"].unique().to_list()})
    _warn_fixture("available_years", path)
    return [_FIXTURE_YEAR]
