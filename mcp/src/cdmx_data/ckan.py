import json
from collections.abc import Iterator

import httpx

_BASE_URL = "https://datos.cdmx.gob.mx/api/3/action/"


class CKANError(Exception):
    """Error retornado por el portal CKAN."""


class CKANClient:
    """Cliente HTTP para la API CKAN de datos.cdmx.gob.mx."""

    def __init__(self, base_url: str = _BASE_URL, timeout: int = 30) -> None:
        self.base_url = base_url
        self._client = httpx.Client(timeout=timeout)

    def _get(self, action: str, params: dict) -> dict:
        url = self.base_url + action
        resp = self._client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        if not data.get("success"):
            msg = data.get("error", {}).get("message", "Error desconocido del portal")
            raise CKANError(msg)
        return data["result"]

    def datastore_search(
        self,
        resource_id: str,
        limit: int = 100,
        offset: int = 0,
        filters: dict | None = None,
    ) -> dict:
        """Busca registros tabulares en un recurso CKAN."""
        params: dict = {"resource_id": resource_id, "limit": limit, "offset": offset}
        if filters:
            params["filters"] = json.dumps(filters)
        return self._get("datastore_search", params)

    def package_search(self, query: str, rows: int = 10) -> dict:
        """Busca datasets por texto libre."""
        return self._get("package_search", {"q": query, "rows": rows})

    def package_show(self, id: str) -> dict:
        """Obtiene metadata de un dataset (incluye lista de recursos)."""
        return self._get("package_show", {"id": id})

    def resource_show(self, id: str) -> dict:
        """Obtiene metadata de un recurso individual."""
        return self._get("resource_show", {"id": id})

    def datastore_search_sql(self, sql: str) -> dict:
        """Ejecuta SQL read-only en el servidor CKAN."""
        return self._get("datastore_search_sql", {"sql": sql})

    def iter_records(
        self,
        resource_id: str,
        page_size: int = 10_000,
        filters: dict | None = None,
    ) -> Iterator[dict]:
        """Pagina todos los registros de un recurso, respetando el cap de ~32k por request."""
        offset = 0
        while True:
            result = self.datastore_search(
                resource_id, limit=page_size, offset=offset, filters=filters
            )
            records: list[dict] = result.get("records", [])
            if not records:
                break
            yield from records
            if len(records) < page_size:
                break
            offset += len(records)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "CKANClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
