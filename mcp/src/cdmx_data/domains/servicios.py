from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

from cdmx_data.domains.movilidad import _resolve
from cdmx_data.normalize import canonical_alcaldia

if TYPE_CHECKING:
    from cdmx_data.core import CDMX


class Servicios:
    """Dominio de servicios ciudadanos (*0311 / Locatel)."""

    def __init__(self, cdmx: "CDMX") -> None:
        self._cdmx = cdmx

    def locatel(
        self,
        alcaldia: str | None = None,
        desde: str | None = None,
        hasta: str | None = None,
    ) -> pd.DataFrame:
        """
        Solicitudes recibidas por Locatel (*0311) con tiempos de respuesta.

        Parámetros
        ----------
        alcaldia : str, opcional
            Filtra por alcaldía (se normaliza automáticamente)
        desde : str, opcional
            Fecha inicio YYYY-MM-DD
        hasta : str, opcional
            Fecha fin YYYY-MM-DD
        """
        resource_id = _resolve(self._cdmx, "locatel_0311")
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
        if hasta:
            col = next((c for c in df.columns if "fecha" in c.lower()), None)
            if col:
                df = df[df[col] <= hasta]

        return df.reset_index(drop=True)
