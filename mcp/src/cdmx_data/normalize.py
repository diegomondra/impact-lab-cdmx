import re
import unicodedata
from datetime import date, datetime

from dateutil import parser as _dateutil_parser

__all__ = ["normalize_text", "canonical_alcaldia", "parse_date", "parse_coord"]

_ALCALDIAS_CANONICAL: list[str] = [
    "Álvaro Obregón",
    "Azcapotzalco",
    "Benito Juárez",
    "Coyoacán",
    "Cuajimalpa de Morelos",
    "Cuauhtémoc",
    "Gustavo A. Madero",
    "Iztacalco",
    "Iztapalapa",
    "La Magdalena Contreras",
    "Miguel Hidalgo",
    "Milpa Alta",
    "Tláhuac",
    "Tlalpan",
    "Venustiano Carranza",
    "Xochimilco",
]


def normalize_text(s: str) -> str:
    """Convierte a minúsculas, elimina tildes y colapsa espacios."""
    if not isinstance(s, str):
        raise TypeError(f"Se esperaba str, se recibió {type(s).__name__}")
    s = s.strip().lower()
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", s)


_ALCALDIAS_MAP: dict[str, str] = {normalize_text(a): a for a in _ALCALDIAS_CANONICAL}


def canonical_alcaldia(raw: str) -> str | None:
    """Devuelve la alcaldía canónica (con acento) o None si no coincide."""
    return _ALCALDIAS_MAP.get(normalize_text(raw))


def parse_date(s: str) -> date:
    """Acepta YYYY-MM-DD, DD/MM/YYYY (orden DD primero), ISO con T, y otros formatos via dateutil.

    El formato de barra se interpreta como DD/MM/YYYY, no MM/DD/YYYY.
    Raises: ValueError si el string no puede interpretarse como fecha.
    """
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return _dateutil_parser.parse(s).date()


def parse_coord(value: str | float | int) -> float:
    """Normaliza coordenadas con coma decimal (gotcha del portal CDMX).

    Acepta un solo separador decimal (coma o punto). No maneja separadores
    de miles — '1,234.56' lanzará ValueError.
    """
    if isinstance(value, (int, float)):
        return float(value)
    return float(str(value).replace(",", "."))
