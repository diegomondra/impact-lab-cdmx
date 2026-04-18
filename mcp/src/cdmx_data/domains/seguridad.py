from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import pandas as pd

from cdmx_data.catalog import CATALOG
from cdmx_data.domains.movilidad import _resolve
from cdmx_data.normalize import canonical_alcaldia

if TYPE_CHECKING:
    from cdmx_data.core import CDMX


class Seguridad:
    """Dominio de seguridad pública de la CDMX."""

    def __init__(self, cdmx: "CDMX") -> None:
        self._cdmx = cdmx

    def carpetas_fgj(
        self,
        alcaldia: str | None = None,
        delito_contiene: str | None = None,
        desde: str | None = None,
        hasta: str | None = None,
    ) -> pd.DataFrame:
        """
        Carpetas de investigación de la FGJ.

        Carga el recurso más reciente disponible por defecto.
        Si desde/hasta cruzan años, carga los recursos de cada año.

        Parámetros
        ----------
        alcaldia : str, opcional
            Nombre de alcaldía (se normaliza automáticamente)
        delito_contiene : str, opcional
            Filtro de texto sobre la columna 'delito' (case-insensitive)
        desde : str, opcional
            Fecha inicio YYYY-MM-DD
        hasta : str, opcional
            Fecha fin YYYY-MM-DD
        """
        df = self._cdmx._load_local("carpetas_fgj")
        if df is None:
            resource_ids = self._resolve_carpetas(desde, hasta)
            frames = [self._cdmx._fetch_cached(rid) for rid in resource_ids]
            df = pd.concat(frames, ignore_index=True) if len(frames) > 1 else frames[0]

        if alcaldia:
            canon = canonical_alcaldia(alcaldia)
            target = canon if canon else alcaldia
            col = "alcaldia_catalogo" if "alcaldia_catalogo" in df.columns else "alcaldia_hecho"
            df = df[df[col].apply(lambda v: canonical_alcaldia(str(v)) == target)]

        if delito_contiene:
            df = df[df["delito"].str.contains(delito_contiene, case=False, na=False)]

        if desde and "fecha_inicio" in df.columns:
            df = df[df["fecha_inicio"] >= desde]
        if hasta and "fecha_inicio" in df.columns:
            df = df[df["fecha_inicio"] <= hasta]

        return df.reset_index(drop=True)

    def _resolve_carpetas(self, desde: str | None, hasta: str | None) -> list[str]:
        """Busca los recursos de carpetas FGJ por año vía package_show."""
        info = CATALOG["carpetas_fgj"]
        pkg = self._cdmx.ckan.package_show(info.slug)
        resources = [r for r in pkg.get("resources", []) if r.get("datastore_active")]

        if not resources:
            raise ValueError("No se encontraron recursos activos para carpetas_fgj")

        current_year = datetime.date.today().year
        desde_year = int(desde[:4]) if desde else current_year
        hasta_year = int(hasta[:4]) if hasta else current_year

        selected = []
        for r in resources:
            name = r.get("name", "") + r.get("description", "")
            for year in range(desde_year, hasta_year + 1):
                if str(year) in name:
                    selected.append(r["id"])
                    break

        if not selected:
            selected = [resources[0]["id"]]

        return selected

    def victimas_fgj(
        self,
        alcaldia: str | None = None,
        desde: str | None = None,
        hasta: str | None = None,
    ) -> pd.DataFrame:
        """Víctimas en carpetas de investigación FGJ (2019 → presente)."""
        resource_id = _resolve(self._cdmx, "victimas_fgj")
        df = self._cdmx._fetch_cached(resource_id)
        if alcaldia:
            canon = canonical_alcaldia(alcaldia)
            target = canon if canon else alcaldia
            col = "alcaldia_catalogo" if "alcaldia_catalogo" in df.columns else "alcaldia"
            df = df[df[col].apply(lambda v: canonical_alcaldia(str(v)) == target)]
        if desde and "ao_hechos" in df.columns:
            df = df[df["ao_hechos"].astype(str) >= desde[:4]]
        if hasta and "ao_hechos" in df.columns:
            df = df[df["ao_hechos"].astype(str) <= hasta[:4]]
        return df.reset_index(drop=True)

    def hechos_transito(
        self, desde: str | None = None, hasta: str | None = None
    ) -> pd.DataFrame:
        """Hechos de tránsito registrados por la SSC."""
        resource_id = _resolve(self._cdmx, "hechos_transito")
        df = self._cdmx._fetch_cached(resource_id)
        date_col = next((c for c in df.columns if "fecha" in c.lower()), None)
        if date_col:
            if desde:
                df = df[df[date_col] >= desde]
            if hasta:
                df = df[df[date_col] <= hasta]
        return df.reset_index(drop=True)

    def fotocivicas(self) -> pd.DataFrame:
        """Infracciones al reglamento vehicular registradas por fotocívicas."""
        resource_id = _resolve(self._cdmx, "fotocivicas")
        return self._cdmx._fetch_cached(resource_id)

    def incidentes_c5(
        self, alcaldia: str | None = None, desde: str | None = None
    ) -> pd.DataFrame:
        """Incidentes viales reportados al C5."""
        resource_id = _resolve(self._cdmx, "incidentes_c5")
        df = self._cdmx._fetch_cached(resource_id)
        if alcaldia:
            canon = canonical_alcaldia(alcaldia)
            target = canon if canon else alcaldia
            col = next((c for c in df.columns if "alcaldia" in c.lower()), None)
            if col:
                df = df[df[col].apply(lambda v: canonical_alcaldia(str(v)) == target)]
        if desde:
            col = next((c for c in df.columns if "fecha" in c.lower()), None)
            if col:
                df = df[df[col] >= desde]
        return df.reset_index(drop=True)
