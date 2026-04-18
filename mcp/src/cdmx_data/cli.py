from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from cdmx_data import __version__

app = typer.Typer(
    name="cdmx",
    help="Hub de datos abiertos de la Ciudad de México.",
    no_args_is_help=True,
)
cache_app = typer.Typer(help="Gestión del cache local.")
app.add_typer(cache_app, name="cache")

console = Console()


def _get_cdmx():
    import atexit
    from cdmx_data import CDMX
    cdmx = CDMX()
    atexit.register(cdmx.close)
    return cdmx


@app.command()
def version() -> None:
    """Muestra la versión instalada del paquete."""
    console.print(f"cdmx-data {__version__}")


@app.command()
def search(
    query: str = typer.Argument(..., help="Texto a buscar en el portal"),
    max_results: int = typer.Option(10, "--max", "-n", help="Número máximo de resultados"),
) -> None:
    """Busca datasets en datos.cdmx.gob.mx."""
    cdmx = _get_cdmx()
    results = cdmx.search(query, max_results=max_results)
    if not results:
        console.print("[yellow]Sin resultados para esa búsqueda.[/yellow]")
        return
    table = Table("Nombre", "Título", "Organización")
    for r in results:
        table.add_row(
            r.get("name", ""),
            r.get("title", ""),
            r.get("organization", {}).get("title", "") if r.get("organization") else "",
        )
    console.print(table)


@app.command()
def fetch(
    key: str = typer.Argument(..., help="Key interna del dataset (ej. metro_afluencia_simple)"),
    limit: int = typer.Option(1000, "--limit", "-l", help="Máximo de registros"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Archivo de salida (.csv o .json)"),
) -> None:
    """Descarga un recurso del catálogo por su key interna."""
    from cdmx_data.catalog import CATALOG

    if key not in CATALOG:
        console.print(f"[red]Key '{key}' no encontrada en el catálogo.[/red]")
        console.print("Usa [bold]cdmx catalog[/bold] para ver las keys disponibles.")
        raise typer.Exit(1)

    cdmx = _get_cdmx()
    info = CATALOG[key]
    resource_id = info.resource_id

    if resource_id is None:
        pkg = cdmx.ckan.package_show(info.slug)
        for r in pkg.get("resources", []):
            if r.get("datastore_active"):
                resource_id = r["id"]
                break

    if resource_id is None:
        console.print(f"[red]No se encontró recurso activo para '{key}'.[/red]")
        raise typer.Exit(1)

    df = cdmx.fetch_resource(resource_id, max_records=limit)

    if output is None:
        console.print(df.to_string(index=False))
        return

    suffix = output.suffix.lower()
    if suffix == ".csv":
        df.to_csv(output, index=False)
        console.print(f"[green]Guardado en {output} ({len(df)} filas)[/green]")
    elif suffix == ".json":
        df.to_json(output, orient="records", force_ascii=False, indent=2)
        console.print(f"[green]Guardado en {output} ({len(df)} filas)[/green]")
    else:
        console.print(f"[red]Formato no soportado: {suffix}. Usa .csv o .json[/red]")
        raise typer.Exit(1)


@app.command()
def catalog(
    track: str | None = typer.Option(None, "--track", "-t", help="Filtrar por track"),
) -> None:
    """Lista los datasets conocidos en el catálogo."""
    cdmx = _get_cdmx()
    entries = cdmx.catalogo(track=track)
    table = Table("Key", "Track", "Slug", "Resource ID", "Notas")
    for e in entries:
        rid = e.resource_id or "[italic dim]resolver[/italic dim]"
        table.add_row(e.key, e.track, e.slug, rid, e.notes[:50])
    console.print(table)


@cache_app.command("list")
def cache_list() -> None:
    """Lista las entradas almacenadas en el cache local."""
    cdmx = _get_cdmx()
    entries = cdmx.cache.list_entries()
    if not entries:
        console.print("[dim]El cache está vacío.[/dim]")
        return
    table = Table("Resource ID", "Descargado", "Filas", "Última modificación")
    for e in entries:
        table.add_row(
            e["resource_id"],
            e["fetched_at"],
            str(e["row_count"] or ""),
            e["source_last_modified"] or "",
        )
    console.print(table)


@cache_app.command("clear")
def cache_clear(
    confirm: bool = typer.Option(False, "--yes", "-y", help="Confirmar sin prompt"),
) -> None:
    """Elimina todos los datos del cache local."""
    if not confirm:
        typer.confirm("Esto eliminará todos los datos en cache. ¿Continuar?", abort=True)
    cdmx = _get_cdmx()
    cdmx.cache.clear()
    console.print("[green]Cache eliminado correctamente.[/green]")


@app.command()
def mcp() -> None:
    """Inicia el servidor MCP en stdio (para Claude Code / Claude Desktop)."""
    try:
        from cdmx_data.mcp_server import run_server
    except ImportError:
        console.print(
            "[red]El servidor MCP no está disponible.[/red]\n"
            "Instala con: [bold]pip install cdmx-data[mcp][/bold]"
        )
        raise typer.Exit(1)
    run_server()
