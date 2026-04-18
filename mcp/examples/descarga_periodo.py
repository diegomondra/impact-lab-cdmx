"""
Descarga datos de todos los tracks para un rango de fechas.

Uso:
    python examples/descarga_periodo.py --desde 2024-01-01 --hasta 2024-12-31
    python examples/descarga_periodo.py --desde 2024-01-01 --hasta 2024-12-31 --track movilidad
    python examples/descarga_periodo.py --desde 2024-01-01 --hasta 2024-12-31 --salida ./datos

Los archivos se guardan en el directorio de salida como:
    <track>_<key>_<desde>_<hasta>.csv

Datasets disponibles por track:
    movilidad  — metro, metrobús, RTP, STE, Ecobici
    seguridad  — carpetas FGJ, víctimas, hechos de tránsito
    aire       — calidad del aire (PM25, O3, NO2, CO)
    servicios  — solicitudes Locatel *0311
    finanzas   — proveedores, deuda pública, presupuesto

Nota: La primera descarga tarda varios minutos por recurso.
      Las siguientes ejecuciones del mismo día usan el cache local (6h TTL).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from cdmx_data import CDMX


# Mapeo de track → función descargadora
# Cada entrada: (key_catalogo, callable que recibe (cdmx, desde, hasta))
_DESCARGAS: dict[str, list[tuple[str, callable]]] = {
    "movilidad": [
        ("metro_afluencia_simple",
         lambda c, d, h: c.movilidad.metro.afluencia(desde=d, hasta=h)),
        ("metrobus_afluencia",
         lambda c, d, h: c.movilidad.metrobus(desde=d, hasta=h)),
        ("rtp_afluencia",
         lambda c, d, h: c.movilidad.rtp(desde=d, hasta=h)),
        ("ste_afluencia",
         lambda c, d, h: c.movilidad.ste(desde=d, hasta=h)),
        ("ecobici_viajes",
         lambda c, d, h: c.movilidad.ecobici()),
    ],
    "seguridad": [
        ("carpetas_fgj",
         lambda c, d, h: c.seguridad.carpetas_fgj(desde=d, hasta=h)),
        ("victimas_fgj",
         lambda c, d, h: c.seguridad.victimas_fgj(desde=d, hasta=h)),
        ("hechos_transito",
         lambda c, d, h: c.seguridad.hechos_transito(desde=d, hasta=h)),
    ],
    "aire": [
        ("calidad_aire_pm25",
         lambda c, d, h: c.aire.calidad(contaminante="PM25")),
        ("calidad_aire_o3",
         lambda c, d, h: c.aire.calidad(contaminante="O3")),
        ("calidad_aire_no2",
         lambda c, d, h: c.aire.calidad(contaminante="NO2")),
        ("calidad_aire_co",
         lambda c, d, h: c.aire.calidad(contaminante="CO")),
    ],
    "servicios": [
        ("locatel_0311",
         lambda c, d, h: c.servicios.locatel(desde=d, hasta=h)),
    ],
    "finanzas": [
        ("proveedores",
         lambda c, d, h: c.finanzas.proveedores()),
        ("deuda_publica",
         lambda c, d, h: c.finanzas.deuda_publica()),
        ("transparencia_presupuestaria",
         lambda c, d, h: c.finanzas.transparencia_presupuestaria()),
    ],
}


def descargar_periodo(
    desde: str,
    hasta: str,
    tracks: list[str] | None = None,
    salida: Path = Path("data"),
    verbose: bool = True,
) -> dict[str, Path]:
    """
    Descarga datos para todos los datasets en el rango [desde, hasta].

    Parámetros
    ----------
    desde : str
        Fecha inicio YYYY-MM-DD
    hasta : str
        Fecha fin YYYY-MM-DD
    tracks : list[str], opcional
        Tracks a descargar. Si es None, descarga todos.
    salida : Path
        Directorio donde guardar los CSV
    verbose : bool
        Imprimir progreso

    Retorna
    -------
    dict[str, Path]
        Mapa de key → ruta del archivo guardado (solo los exitosos)
    """
    salida.mkdir(parents=True, exist_ok=True)
    cdmx = CDMX()

    targets = {k: v for k, v in _DESCARGAS.items() if tracks is None or k in tracks}
    resultados: dict[str, Path] = {}
    errores: list[tuple[str, str]] = []

    total = sum(len(v) for v in targets.values())
    contador = 0

    for track, datasets in targets.items():
        for key, fn in datasets:
            contador += 1
            nombre_archivo = f"{track}_{key}_{desde}_{hasta}.csv"
            ruta = salida / nombre_archivo

            if verbose:
                print(f"[{contador}/{total}] {track}/{key} ...", end=" ", flush=True)

            try:
                df: pd.DataFrame = fn(cdmx, desde, hasta)

                if df.empty:
                    if verbose:
                        print(f"sin datos para el periodo")
                    continue

                df.to_csv(ruta, index=False)
                resultados[key] = ruta

                if verbose:
                    print(f"{len(df):,} filas → {ruta.name}")

            except Exception as exc:
                errores.append((key, str(exc)))
                if verbose:
                    print(f"ERROR: {exc}")

    if verbose:
        print(f"\nDescarga completada: {len(resultados)} datasets, {len(errores)} errores")
        if errores:
            print("\nDatasets con error:")
            for key, msg in errores:
                print(f"  - {key}: {msg}")

    return resultados


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Descarga datos de la CDMX para un rango de fechas.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--desde", required=True, help="Fecha inicio YYYY-MM-DD")
    parser.add_argument("--hasta", required=True, help="Fecha fin YYYY-MM-DD")
    parser.add_argument(
        "--track",
        choices=list(_DESCARGAS.keys()),
        default=None,
        help="Descargar solo un track (por defecto: todos)",
    )
    parser.add_argument(
        "--salida",
        type=Path,
        default=Path("data"),
        help="Directorio de salida (por defecto: ./data)",
    )
    parser.add_argument(
        "--silencioso",
        action="store_true",
        help="No imprimir progreso",
    )
    args = parser.parse_args()

    tracks = [args.track] if args.track else None

    resultados = descargar_periodo(
        desde=args.desde,
        hasta=args.hasta,
        tracks=tracks,
        salida=args.salida,
        verbose=not args.silencioso,
    )

    if not resultados:
        sys.exit(1)


if __name__ == "__main__":
    main()
