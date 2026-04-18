from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

from cdmx_data.catalog import CATALOG
from cdmx_data.domains.movilidad import _resolve

if TYPE_CHECKING:
    from cdmx_data.core import CDMX

_CONTAMINANTE_KEYWORDS: dict[str, str] = {
    "PM25": "pm2",
    "PM10": "pm10",
    "O3":   "o3",
    "NO2":  "no2",
    "CO":   "co",
    "SO2":  "so2",
}


class Aire:
    """Dominio de calidad del aire (SIMAT) de la CDMX."""

    def __init__(self, cdmx: "CDMX") -> None:
        self._cdmx = cdmx
        self._contaminante_ids: dict[str, str] = {}

    def calidad(
        self,
        contaminante: str | None = None,
        estacion: str | None = None,
    ) -> pd.DataFrame:
        """
        Calidad del aire por estación SIMAT.

        Parámetros
        ----------
        contaminante : str, opcional
            Código del contaminante: PM25, PM10, O3, NO2, CO, SO2
        estacion : str, opcional
            Clave de la estación SIMAT (ej. "MER", "XAL")
        """
        local_key = f"calidad_aire_{contaminante.lower()}" if contaminante else "calidad_aire"
        df = self._cdmx._load_local(local_key)
        if df is None:
            resource_id = self._resolve_contaminante(contaminante)
            df = self._cdmx._fetch_cached(resource_id)
        if estacion:
            col = next((c for c in df.columns if "estacion" in c.lower()), None)
            if col:
                df = df[df[col].str.upper() == estacion.upper()]
        return df.reset_index(drop=True)

    def _resolve_contaminante(self, contaminante: str | None) -> str:
        if contaminante and contaminante in self._contaminante_ids:
            return self._contaminante_ids[contaminante]

        info = CATALOG["calidad_aire"]
        pkg = self._cdmx.ckan.package_show(info.slug)
        resources = [r for r in pkg.get("resources", []) if r.get("datastore_active")]

        if not resources:
            raise ValueError("No se encontraron recursos activos para calidad_aire")

        if not contaminante:
            return resources[0]["id"]

        keyword = _CONTAMINANTE_KEYWORDS.get(contaminante.upper(), contaminante.lower())
        for r in resources:
            name = (r.get("name", "") + r.get("description", "")).lower()
            if keyword in name:
                self._contaminante_ids[contaminante] = r["id"]
                return r["id"]

        return resources[0]["id"]

    def estaciones(self) -> pd.DataFrame:
        """Estaciones SIMAT georreferenciadas."""
        resource_id = _resolve(self._cdmx, "estaciones_simat")
        return self._cdmx._fetch_cached(resource_id)

    def meteorologia(self) -> pd.DataFrame:
        """Datos meteorológicos: temperatura, humedad, viento."""
        resource_id = _resolve(self._cdmx, "meteorologia_simat")
        return self._cdmx._fetch_cached(resource_id)
