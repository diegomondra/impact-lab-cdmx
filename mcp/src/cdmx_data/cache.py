import re as _re
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pandas as pd

_DEFAULT_TTL_HOURS = 6

_RESOURCE_ID_RE = _re.compile(r'^[0-9a-f\-]+$')


class Cache:
    """Cache SQLite con TTL para respuestas del portal CKAN."""

    def __init__(
        self,
        db_path: str | Path = "~/.cdmx_data/cache.db",
        ttl_hours: int = _DEFAULT_TTL_HOURS,
    ) -> None:
        self.ttl = timedelta(hours=ttl_hours)
        if str(db_path) == ":memory:":
            self.conn = sqlite3.connect(":memory:")
        else:
            path = Path(db_path).expanduser()
            path.parent.mkdir(parents=True, exist_ok=True)
            self.conn = sqlite3.connect(str(path))
        self._init_meta()

    def _init_meta(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS _cache_meta (
                resource_id          TEXT PRIMARY KEY,
                fetched_at           TEXT NOT NULL,
                row_count            INTEGER,
                source_last_modified TEXT
            )
            """
        )
        self.conn.commit()

    def _table_name(self, resource_id: str) -> str:
        if not _RESOURCE_ID_RE.match(resource_id):
            raise ValueError(f"resource_id inválido: '{resource_id}'")
        return "r_" + resource_id.replace("-", "_")

    def is_fresh(self, resource_id: str) -> bool:
        """True si hay datos y el TTL no ha expirado."""
        row = self.conn.execute(
            "SELECT fetched_at FROM _cache_meta WHERE resource_id = ?",
            (resource_id,),
        ).fetchone()
        if not row:
            return False
        fetched_at = datetime.fromisoformat(row[0])
        return datetime.now(UTC) - fetched_at < self.ttl

    def put(
        self,
        resource_id: str,
        df: pd.DataFrame,
        source_last_modified: str | None = None,
    ) -> None:
        """Guarda un DataFrame en SQLite y actualiza la metadata."""
        table = self._table_name(resource_id)
        df.to_sql(table, self.conn, if_exists="replace", index=False)
        self.conn.execute(
            """
            INSERT OR REPLACE INTO _cache_meta
                (resource_id, fetched_at, row_count, source_last_modified)
            VALUES (?, ?, ?, ?)
            """,
            (resource_id, datetime.now(UTC).isoformat(), len(df), source_last_modified),
        )
        self.conn.commit()

    def get(self, resource_id: str) -> pd.DataFrame | None:
        """Lee un DataFrame del cache, o None si no existe."""
        import pandas.io.sql as _psql
        table = self._table_name(resource_id)
        try:
            return pd.read_sql(f'SELECT * FROM "{table}"', self.conn)
        except (_psql.DatabaseError, sqlite3.OperationalError):
            return None

    def invalidate(self, resource_id: str) -> None:
        """Elimina datos y metadata de un resource_id."""
        table = self._table_name(resource_id)
        self.conn.execute(f'DROP TABLE IF EXISTS "{table}"')
        self.conn.execute(
            "DELETE FROM _cache_meta WHERE resource_id = ?", (resource_id,)
        )
        self.conn.commit()

    def list_entries(self) -> list[dict]:
        """Devuelve la lista de entradas en cache con metadata."""
        rows = self.conn.execute(
            "SELECT resource_id, fetched_at, row_count, source_last_modified FROM _cache_meta"
        ).fetchall()
        return [
            {
                "resource_id": r[0],
                "fetched_at": r[1],
                "row_count": r[2],
                "source_last_modified": r[3],
            }
            for r in rows
        ]

    def clear(self) -> None:
        """Elimina todas las entradas del cache."""
        for entry in self.list_entries():
            self.invalidate(entry["resource_id"])

    def sql(self, query: str) -> pd.DataFrame:
        """Ejecuta SQL directamente contra la base SQLite del cache."""
        return pd.read_sql(query, self.conn)

    def close(self) -> None:
        self.conn.close()

    def __enter__(self) -> "Cache":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
