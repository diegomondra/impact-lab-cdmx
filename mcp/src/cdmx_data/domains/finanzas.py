from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

from cdmx_data.catalog import CATALOG
from cdmx_data.domains.movilidad import _resolve

if TYPE_CHECKING:
    from cdmx_data.core import CDMX


class Finanzas:
    """Dominio de finanzas públicas de la CDMX."""

    def __init__(self, cdmx: "CDMX") -> None:
        self._cdmx = cdmx

    def proveedores(self, nombre_contiene: str | None = None) -> pd.DataFrame:
        """Padrón de proveedores del gobierno de la CDMX."""
        df = self._cdmx._load_local("proveedores")
        if df is None:
            info = CATALOG["proveedores"]
            pkg = self._cdmx.ckan.package_show(info.slug)
            resources = pkg.get("resources", [])
            active = [r for r in resources if r.get("datastore_active")]
            if active:
                df = self._cdmx._fetch_cached(active[0]["id"])
            else:
                csv_r = next((r for r in resources if r.get("format", "").upper() == "CSV"), None)
                if not csv_r:
                    raise ValueError("No se encontró recurso descargable para 'proveedores'")
                df = pd.read_csv(csv_r["url"])
        if nombre_contiene:
            col = next((c for c in df.columns if "nombre" in c.lower()), None)
            if col:
                df = df[df[col].str.contains(nombre_contiene, case=False, na=False)]
        return df.reset_index(drop=True)

    def deuda_publica(self) -> pd.DataFrame:
        """Deuda pública de la CDMX por acreedor y tipo."""
        resource_id = _resolve(self._cdmx, "deuda_publica")
        return self._cdmx._fetch_cached(resource_id)

    def transparencia_presupuestaria(self) -> pd.DataFrame:
        """Gasto público de la CDMX."""
        resource_id = _resolve(self._cdmx, "transparencia_presupuestaria")
        return self._cdmx._fetch_cached(resource_id)

    def ley_ingresos(self) -> pd.DataFrame:
        """Ingresos estimados de la CDMX."""
        resource_id = _resolve(self._cdmx, "ley_ingresos")
        return self._cdmx._fetch_cached(resource_id)
