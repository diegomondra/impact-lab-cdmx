from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

from cdmx_data.catalog import CATALOG

if TYPE_CHECKING:
    from cdmx_data.core import CDMX

_resolved_ids: dict[str, str] = {}


class Metro:
    """Datos del Sistema de Transporte Colectivo Metro CDMX."""

    def __init__(self, cdmx: "CDMX") -> None:
        self._cdmx = cdmx
        self._resolved: dict[str, str] = {}

    def _resource_id(self, key: str) -> str:
        if key in self._resolved:
            return self._resolved[key]
        if self._cdmx.data_dir is not None and list(self._cdmx.data_dir.glob(f"*_{key}_*.csv")):
            return f"local:{key}"
        info = CATALOG[key]
        if info.resource_id:
            self._resolved[key] = info.resource_id
            return info.resource_id
        pkg = self._cdmx.ckan.package_show(info.slug)
        for r in pkg.get("resources", []):
            if r.get("datastore_active"):
                self._resolved[key] = r["id"]
                return r["id"]
        raise ValueError(f"No se encontró recurso activo para '{key}' (slug: {info.slug})")

    def afluencia(
        self,
        desde: str | None = None,
        hasta: str | None = None,
        linea: str | None = None,
        desglosada: bool = False,
    ) -> pd.DataFrame:
        """
        Afluencia diaria del Metro por estación y línea.

        Parámetros
        ----------
        desde : str, opcional
            Fecha inicio en formato YYYY-MM-DD
        hasta : str, opcional
            Fecha fin en formato YYYY-MM-DD
        linea : str, opcional
            Número de línea (ej. "1", "2", "A")
        desglosada : bool
            Si True, usa el recurso con desglose por tipo de tarifa
        """
        key = "metro_afluencia_desglosada" if desglosada else "metro_afluencia_simple"
        resource_id = self._resource_id(key)
        df = self._cdmx._fetch_cached(resource_id)
        if desde:
            df = df[df["fecha"] >= desde]
        if hasta:
            df = df[df["fecha"] <= hasta]
        if linea:
            df = df[df["linea"].str.upper() == linea.upper()]
        return df.reset_index(drop=True)


class Movilidad:
    """Dominio de movilidad urbana de la CDMX."""

    def __init__(self, cdmx: "CDMX") -> None:
        self._cdmx = cdmx
        self.metro = Metro(cdmx)

    def metrobus(
        self,
        desde: str | None = None,
        hasta: str | None = None,
    ) -> pd.DataFrame:
        """Afluencia diaria de Metrobús por estación."""
        resource_id = _resolve(self._cdmx, "metrobus_afluencia")
        df = self._cdmx._fetch_cached(resource_id)
        if desde:
            df = df[df["fecha"] >= desde]
        if hasta:
            df = df[df["fecha"] <= hasta]
        return df.reset_index(drop=True)

    def rtp(self, desde: str | None = None, hasta: str | None = None) -> pd.DataFrame:
        """Afluencia diaria de la Red de Transporte de Pasajeros."""
        resource_id = _resolve(self._cdmx, "rtp_afluencia")
        df = self._cdmx._fetch_cached(resource_id)
        if desde:
            df = df[df["fecha"] >= desde]
        if hasta:
            df = df[df["fecha"] <= hasta]
        return df.reset_index(drop=True)

    def ste(self, desde: str | None = None, hasta: str | None = None) -> pd.DataFrame:
        """Afluencia del STE: Cablebús, Tren Ligero, Trolebús."""
        resource_id = _resolve(self._cdmx, "ste_afluencia")
        df = self._cdmx._fetch_cached(resource_id)
        if desde:
            df = df[df["fecha"] >= desde]
        if hasta:
            df = df[df["fecha"] <= hasta]
        return df.reset_index(drop=True)

    def ecobici(self) -> pd.DataFrame:
        """Viajes procesados de usuarios de Ecobici."""
        resource_id = _resolve(self._cdmx, "ecobici_viajes")
        return self._cdmx._fetch_cached(resource_id)

    def ciclovias(self) -> pd.DataFrame:
        """Infraestructura vial ciclista (651 tramos)."""
        resource_id = _resolve(self._cdmx, "ciclovias")
        return self._cdmx._fetch_cached(resource_id)


def _resolve(cdmx: "CDMX", key: str) -> str:
    """Resuelve resource_id desde catálogo o package_show, con caché en memoria."""
    if key in _resolved_ids:
        return _resolved_ids[key]
    if cdmx.data_dir is not None and list(cdmx.data_dir.glob(f"*_{key}_*.csv")):
        return f"local:{key}"
    info = CATALOG[key]
    if info.resource_id:
        _resolved_ids[key] = info.resource_id
        return info.resource_id
    pkg = cdmx.ckan.package_show(info.slug)
    for r in pkg.get("resources", []):
        if r.get("datastore_active"):
            _resolved_ids[key] = r["id"]
            return r["id"]
    raise ValueError(f"No se encontró recurso activo para '{key}' (slug: {info.slug})")
