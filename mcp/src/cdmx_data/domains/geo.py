from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

from cdmx_data.domains.movilidad import _resolve

if TYPE_CHECKING:
    from cdmx_data.core import CDMX


class Geo:
    """Dominio geoespacial transversal de la CDMX."""

    def __init__(self, cdmx: "CDMX") -> None:
        self._cdmx = cdmx

    def colonias(self) -> pd.DataFrame:
        """Catálogo de colonias con geometrías."""
        resource_id = _resolve(self._cdmx, "colonias")
        return self._cdmx._fetch_cached(resource_id)

    def alcaldias(self) -> pd.DataFrame:
        """16 polígonos oficiales de alcaldías."""
        resource_id = _resolve(self._cdmx, "alcaldias")
        return self._cdmx._fetch_cached(resource_id)

    def agebs(self) -> pd.DataFrame:
        """Áreas Geoestadísticas Básicas del INEGI."""
        resource_id = _resolve(self._cdmx, "agebs")
        return self._cdmx._fetch_cached(resource_id)

    def cuadrantes_ssc(self) -> pd.DataFrame:
        """847 polígonos de cuadrantes de la SSC."""
        resource_id = _resolve(self._cdmx, "cuadrantes_ssc")
        return self._cdmx._fetch_cached(resource_id)

    def colonia_en_punto(self, lat: float, lon: float) -> dict | None:
        """
        Geocruce: devuelve la colonia que contiene el punto (lat, lon).

        Requiere geopandas instalado (pip install cdmx-data[geo]).
        """
        try:
            import geopandas as gpd
            from shapely.geometry import Point
        except ImportError as e:
            raise ImportError(
                "colonia_en_punto requiere geopandas. "
                "Instala con: pip install cdmx-data[geo]"
            ) from e

        df = self.colonias()
        if "geometry" not in df.columns:
            raise ValueError(
                "El dataset de colonias no contiene columna 'geometry'. "
                "Verifica que el recurso incluya geometrías."
            )
        gdf = gpd.GeoDataFrame(df, geometry="geometry")
        punto = Point(lon, lat)
        matches = gdf[gdf.geometry.contains(punto)]
        if matches.empty:
            return None
        return matches.iloc[0].to_dict()
