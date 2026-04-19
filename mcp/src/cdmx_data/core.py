from __future__ import annotations

from pathlib import Path

import pandas as pd

from cdmx_data.ckan import CKANClient
from cdmx_data.cache import Cache
from cdmx_data.catalog import CATALOG, DatasetInfo
from cdmx_data.domains.movilidad import Movilidad
from cdmx_data.domains.seguridad import Seguridad
from cdmx_data.domains.aire import Aire
from cdmx_data.domains.servicios import Servicios
from cdmx_data.domains.finanzas import Finanzas
from cdmx_data.domains.geo import Geo
from cdmx_data.domains.presupuesto import Presupuesto

_LOCAL_PREFIX = "local:"


class CDMX:
    """
    Hub principal para los datos abiertos de la Ciudad de México.

    Uso:
        from cdmx_data import CDMX
        cdmx = CDMX()
        df = cdmx.movilidad.metro.afluencia(desde="2024-01-01")
    """

    def __init__(
        self,
        cache_path: str = "~/.cdmx_data/cache.db",
        ttl_hours: int = 6,
        offline: bool = False,
        data_dir: Path | str | None = Path("data"),
    ) -> None:
        self.ckan = CKANClient()
        self.cache = Cache(cache_path, ttl_hours)
        self.offline = offline
        _dd = Path(data_dir) if data_dir is not None else None
        self.data_dir: Path | None = _dd if (_dd is not None and _dd.is_dir()) else None
        self.movilidad = Movilidad(self)
        self.seguridad = Seguridad(self)
        self.aire = Aire(self)
        self.servicios = Servicios(self)
        self.finanzas = Finanzas(self)
        self.geo = Geo(self)
        self.presupuesto = Presupuesto(self)

    def _load_local(self, key: str) -> pd.DataFrame | None:
        """Carga CSVs locales que coincidan con *_{key}_*.csv en data_dir."""
        if self.data_dir is None:
            return None
        files = sorted(self.data_dir.glob(f"*_{key}_*.csv"))
        if not files:
            return None
        frames = [pd.read_csv(f) for f in files]
        return pd.concat(frames, ignore_index=True) if len(frames) > 1 else frames[0]

    def _fetch_cached(self, resource_id: str) -> pd.DataFrame:
        """Flujo canónico: local → cache fresco → descargar y cachear."""
        if resource_id.startswith(_LOCAL_PREFIX):
            key = resource_id[len(_LOCAL_PREFIX):]
            df = self._load_local(key)
            if df is None:
                raise FileNotFoundError(f"No hay datos locales para '{key}' en {self.data_dir}")
            return df

        if self.cache.is_fresh(resource_id):
            df = self.cache.get(resource_id)
            if df is not None:
                return df

        if self.offline:
            df = self.cache.get(resource_id)
            if df is None:
                raise RuntimeError(
                    f"Sin datos en cache para '{resource_id}' y offline=True. "
                    "Ejecuta primero con acceso a internet para poblar el cache."
                )
            return df

        records = list(self.ckan.iter_records(resource_id))
        df = pd.DataFrame(records)
        self.cache.put(resource_id, df)
        return df

    def fetch_resource(
        self, resource_id: str, max_records: int | None = None
    ) -> pd.DataFrame:
        """Escape hatch: descarga un recurso por ID directamente."""
        if max_records is not None:
            result = self.ckan.datastore_search(resource_id, limit=max_records)
            return pd.DataFrame(result["records"])
        return self._fetch_cached(resource_id)

    def search(self, query: str, max_results: int = 10) -> list[dict]:
        """Busca datasets en el portal por texto libre."""
        result = self.ckan.package_search(query, rows=max_results)
        return result.get("results", [])

    def catalogo(self, track: str | None = None) -> list[DatasetInfo]:
        """Lista los datasets conocidos, opcionalmente filtrados por track."""
        entries = list(CATALOG.values())
        if track:
            entries = [e for e in entries if e.track == track]
        return entries

    def sql_remote(self, sql: str) -> pd.DataFrame:
        """Ejecuta SQL read-only directamente en el servidor CKAN."""
        result = self.ckan.datastore_search_sql(sql)
        return pd.DataFrame(result["records"])

    def sql(self, query: str) -> pd.DataFrame:
        """Ejecuta SQL en el cache SQLite local."""
        return self.cache.sql(query)

    def close(self) -> None:
        self.cache.close()
        self.ckan.close()

    def __enter__(self) -> "CDMX":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
