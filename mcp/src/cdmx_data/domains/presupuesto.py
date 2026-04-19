"""Dominio del presupuesto CDMX — datos del dashboard 'La ruta de tu peso'.

Expone los 7 agregados que alimentan las pestañas del notebook como
métodos Python + tools MCP. Así el mismo conocimiento (crosswalk editorial,
programas emblemáticos, budget_tree, egresos multi-año, Rally obras) está
disponible para Claude Desktop / Claude Code.

Rutas esperadas (cdmx.data_dir apunta a data/ por defecto; repo root = su parent):
    data/egresos_{2018..2024}_{cp|aprobado|trimestre}.csv
    data/ingresos_main.csv
    data/rally_obras.csv
    data/clean/budget_tree.parquet
    crosswalk/crosswalk.csv
    crosswalk/named_programs_2024.csv
"""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from cdmx_data.core import CDMX


_EGRESOS_FILES = {
    2018: "egresos_2018_cp.csv",
    2019: "egresos_2019_cp.csv",
    2020: "egresos_2020_cp.csv",
    2021: "egresos_2021_cp.csv",
    2022: "egresos_2022_cp.csv",
    2023: "egresos_2023_03_trimestre.csv",
    2024: "egresos_2024_aprobado.csv",
}


class Presupuesto:
    """Datos canónicos del dashboard 'La ruta de tu peso'."""

    def __init__(self, cdmx: "CDMX") -> None:
        self._cdmx = cdmx

    def _repo_root(self) -> Path | None:
        if self._cdmx.data_dir is None:
            return None
        return self._cdmx.data_dir.parent

    def _data_path(self, name: str) -> Path | None:
        return None if self._cdmx.data_dir is None else self._cdmx.data_dir / name

    def _clean_path(self, name: str) -> Path | None:
        return None if self._cdmx.data_dir is None else self._cdmx.data_dir / "clean" / name

    def _crosswalk_path(self, name: str) -> Path | None:
        root = self._repo_root()
        return None if root is None else root / "crosswalk" / name

    def budget_summary(self, year: int | None = None) -> pd.DataFrame:
        """Level-1 por 16 categorías ciudadanas (pestaña ⑥ Ciudadano).

        Columnas: citizen_category, monto_aprobado, per_100_of_total, year.
        Fuente: data/clean/budget_tree.parquet.
        """
        p = self._clean_path("budget_tree.parquet")
        if p is None or not p.exists():
            raise FileNotFoundError(
                "data/clean/budget_tree.parquet no encontrado. "
                "Ejecuta `bash scripts/download_data.sh` y regenera los parquets."
            )
        df = pd.read_parquet(p)
        df = df[df["level"] == 1]
        if year is not None:
            df = df[df["year"] == int(year)]
        df = df.sort_values("monto_aprobado", ascending=False).reset_index(drop=True)
        return df[["citizen_category", "monto_aprobado", "per_100_of_total", "year"]]

    def budget_drill(
        self,
        citizen_category: str,
        year: int | None = None,
        top_n: int = 20,
    ) -> pd.DataFrame:
        """Programas Level-2 dentro de una categoría ciudadana.

        Columnas: display_name, monto_aprobado, per_100_of_parent, rationale.
        """
        p = self._clean_path("budget_tree.parquet")
        if p is None or not p.exists():
            raise FileNotFoundError("data/clean/budget_tree.parquet no encontrado")
        df = pd.read_parquet(p)
        df = df[(df["level"] == 2) & (df["citizen_category"] == citizen_category)]
        if year is not None:
            df = df[df["year"] == int(year)]
        df = df.sort_values("monto_aprobado", ascending=False).head(top_n).reset_index(drop=True)
        return df[["display_name", "monto_aprobado", "per_100_of_parent", "rationale"]]

    def named_programs(self, query: str | None = None, top_n: int = 20) -> pd.DataFrame:
        """Programas emblemáticos con nombre propio (Cablebús, Pilares, Mi Beca, Altépetl…).

        Fuente: crosswalk/named_programs_2024.csv (extraído de los PDFs del
        Paquete Económico 2024). Filtra por subcadena en display_name,
        ente_ejecutor o section.
        """
        p = self._crosswalk_path("named_programs_2024.csv")
        if p is None or not p.exists():
            raise FileNotFoundError("crosswalk/named_programs_2024.csv no encontrado")
        df = pd.read_csv(p)
        df["monto_aprobado_mxn"] = pd.to_numeric(df["monto_aprobado_mxn"], errors="coerce").fillna(0)
        df = df[df["monto_aprobado_mxn"] > 0]
        if query:
            q = query.lower()
            mask = (
                df["display_name"].fillna("").str.lower().str.contains(q, na=False)
                | df["ente_ejecutor"].fillna("").str.lower().str.contains(q, na=False)
                | df["section"].fillna("").str.lower().str.contains(q, na=False)
            )
            df = df[mask]
        return df.sort_values("monto_aprobado_mxn", ascending=False).head(top_n).reset_index(drop=True)

    def egresos_aggregate(
        self,
        year: int | None = None,
        group_by: str = "desc_funcion",
        top_n: int = 15,
    ) -> pd.DataFrame:
        """Egresos agrupados (pestañas ① Flujo / ③ Se prometen / ⑤ Explora).

        group_by ∈ {desc_funcion, desc_unidad_responsable, desc_capitulo}.
        Fuente: data/egresos_{2018..2024}_{cp|aprobado|trimestre}.csv.
        Si year es None, concatena los 7 años disponibles.
        """
        valid = {"desc_funcion", "desc_unidad_responsable", "desc_capitulo"}
        if group_by not in valid:
            raise ValueError(f"group_by inválido. Usa uno de {sorted(valid)}")
        years = [int(year)] if year is not None else list(_EGRESOS_FILES.keys())
        parts = []
        for y in years:
            fn = _EGRESOS_FILES.get(y)
            if not fn:
                continue
            p = self._data_path(fn)
            if p is None or not p.exists():
                continue
            _df = pd.read_csv(p, low_memory=False)
            if "monto_modificado" in _df.columns and pd.to_numeric(_df["monto_modificado"], errors="coerce").fillna(0).sum() > 0:
                _bcol = "monto_modificado"
            else:
                _bcol = "monto_aprobado"
            _df["_budget"] = pd.to_numeric(_df[_bcol], errors="coerce").fillna(0)
            _df["_spent"] = pd.to_numeric(_df.get("monto_ejercido", 0), errors="coerce").fillna(0)
            _df["_year"] = y
            parts.append(_df[[group_by, "_budget", "_spent", "_year"]])
        if not parts:
            raise FileNotFoundError(f"No se encontraron CSVs de egresos para year={year}")
        df = pd.concat(parts, ignore_index=True)
        agg = (
            df.groupby(group_by, dropna=False)
              .agg(monto_aprobado=("_budget", "sum"),
                   monto_ejercido=("_spent", "sum"))
              .reset_index()
              .sort_values("monto_aprobado", ascending=False)
              .head(top_n)
              .reset_index(drop=True)
        )
        return agg

    def ingresos(
        self,
        ciclo: int | None = None,
        periodo: str | None = None,
        group_by: str = "desc_rubro",
        top_n: int = 20,
    ) -> pd.DataFrame:
        """Ingresos CDMX (pestaña ② Entran).

        periodo ∈ {Anual, 'Cuenta Pública'}. Anual = planeado (Ley de
        Ingresos). Cuenta Pública = recaudado real.
        group_by ∈ {desc_rubro, desc_concepto, desc_tipo_recurso_clase}.
        Fuente: data/ingresos_main.csv.
        """
        valid = {"desc_rubro", "desc_concepto", "desc_tipo_recurso_clase"}
        if group_by not in valid:
            raise ValueError(f"group_by inválido. Usa uno de {sorted(valid)}")
        p = self._data_path("ingresos_main.csv")
        if p is None or not p.exists():
            raise FileNotFoundError("data/ingresos_main.csv no encontrado")
        df = pd.read_csv(p, low_memory=False)
        if ciclo is not None:
            df = df[df["ciclo"] == int(ciclo)]
        if periodo:
            df = df[df["periodo"] == periodo]
        amt = "monto_recaudado" if periodo == "Cuenta Pública" else "monto_estimado"
        df[amt] = pd.to_numeric(df[amt], errors="coerce").fillna(0)
        agg = (
            df.groupby(group_by, dropna=False)[amt].sum()
              .reset_index(name="monto")
              .query("monto > 0")
              .sort_values("monto", ascending=False)
              .head(top_n)
              .reset_index(drop=True)
        )
        return agg

    def rally_obras(
        self,
        alcaldia: str | None = None,
        ramo: str | None = None,
        ciclo_from: int | None = None,
        ciclo_to: int | None = None,
        top_n: int = 15,
    ) -> pd.DataFrame:
        """Obras federales georreferenciadas 2013–2018 (pestaña ④ Aterrizan).

        Columnas: id, nombre_proyecto, desc_ramo, desc_alcaldia, contratista,
        monto_ejercido, ciclo, avance_fisico. Fuente: data/rally_obras.csv.
        """
        p = self._data_path("rally_obras.csv")
        if p is None or not p.exists():
            raise FileNotFoundError("data/rally_obras.csv no encontrado")
        df = pd.read_csv(p, low_memory=False)
        df["monto_ejercido"] = pd.to_numeric(df["monto_ejercido"], errors="coerce").fillna(0)
        df = df[df["monto_ejercido"] > 0]
        if alcaldia:
            df = df[df["desc_alcaldia"].fillna("").str.contains(alcaldia, case=False, na=False)]
        if ramo:
            df = df[df["desc_ramo"].fillna("").str.contains(ramo, case=False, na=False)]
        if ciclo_from is not None:
            df = df[df["ciclo"] >= int(ciclo_from)]
        if ciclo_to is not None:
            df = df[df["ciclo"] <= int(ciclo_to)]
        df = df.sort_values("monto_ejercido", ascending=False).head(top_n).reset_index(drop=True)
        cols = [
            "id", "nombre_proyecto", "desc_ramo", "desc_alcaldia",
            "contratista", "monto_ejercido", "ciclo", "avance_fisico",
        ]
        have = [c for c in cols if c in df.columns]
        return df[have]

    def crosswalk_lookup(self, query: str) -> pd.DataFrame:
        """Busca un programa en el crosswalk editorial.

        Devuelve su citizen_category asignada y el rationale editorial.
        Fuente: crosswalk/crosswalk.csv (19k filas, 16 categorías).
        """
        p = self._crosswalk_path("crosswalk.csv")
        if p is None or not p.exists():
            raise FileNotFoundError("crosswalk/crosswalk.csv no encontrado")
        if not (query or "").strip():
            raise ValueError("query no puede estar vacío")
        df = pd.read_csv(p, low_memory=False)
        q = query.lower()
        mask = (
            df["source_label"].fillna("").str.lower().str.contains(q, na=False)
            | df["display_name"].fillna("").str.lower().str.contains(q, na=False)
        )
        return df[mask].head(20).reset_index(drop=True)
