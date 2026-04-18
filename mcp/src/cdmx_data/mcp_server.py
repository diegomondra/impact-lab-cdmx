"""
Servidor MCP para cdmx-data.

Requiere: pip install cdmx-data[mcp]
Arrancar:  cdmx mcp   ó   uvx cdmx-data mcp
"""
from __future__ import annotations

_MAX_ROWS = 100


def run_server() -> None:
    """Punto de entrada del servidor MCP en modo stdio."""
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp import types

    from cdmx_data import CDMX

    server = Server("cdmx-data")
    cdmx = CDMX()  # auto-detecta ./data/ si existe

    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="cdmx_search",
                description="Busca datasets en el portal datos.cdmx.gob.mx",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Texto de búsqueda"},
                        "max_results": {"type": "integer", "default": 10},
                    },
                    "required": ["query"],
                },
            ),
            types.Tool(
                name="cdmx_catalog",
                description="Lista los datasets conocidos en el catálogo interno",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "track": {
                            "type": "string",
                            "description": "Filtrar por track: movilidad, seguridad, aire, servicios, finanzas, geo",
                        }
                    },
                },
            ),
            types.Tool(
                name="cdmx_fetch_resource",
                description="Descarga registros de un recurso CKAN por su resource_id UUID",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "resource_id": {"type": "string"},
                        "max_records": {"type": "integer", "default": 100},
                    },
                    "required": ["resource_id"],
                },
            ),
            types.Tool(
                name="cdmx_movilidad_metro",
                description="Afluencia diaria del Metro CDMX por línea y estación",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "desde": {"type": "string", "description": "Fecha inicio YYYY-MM-DD"},
                        "hasta": {"type": "string", "description": "Fecha fin YYYY-MM-DD"},
                        "linea": {"type": "string", "description": "Número de línea (ej. '1', 'A')"},
                    },
                },
            ),
            types.Tool(
                name="cdmx_seguridad_fgj",
                description="Carpetas de investigación de la FGJ CDMX",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "alcaldia": {"type": "string"},
                        "delito_contiene": {"type": "string"},
                        "desde": {"type": "string"},
                        "hasta": {"type": "string"},
                    },
                },
            ),
            types.Tool(
                name="cdmx_aire_calidad",
                description="Calidad del aire por estación SIMAT",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "contaminante": {
                            "type": "string",
                            "description": "PM25, PM10, O3, NO2, CO, SO2",
                        },
                        "estacion": {"type": "string", "description": "Clave SIMAT (ej. 'MER')"},
                    },
                },
            ),
            types.Tool(
                name="cdmx_servicios_locatel",
                description="Solicitudes recibidas por Locatel (*0311)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "alcaldia": {"type": "string"},
                        "desde": {"type": "string"},
                        "hasta": {"type": "string"},
                    },
                },
            ),
            types.Tool(
                name="cdmx_finanzas_proveedores",
                description="Padrón de proveedores del gobierno de la CDMX",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "nombre_contiene": {"type": "string"},
                    },
                },
            ),
            types.Tool(
                name="cdmx_geo_colonia_en_punto",
                description="Geocruce: devuelve la colonia que contiene el punto lat/lon",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "lat": {"type": "number"},
                        "lon": {"type": "number"},
                    },
                    "required": ["lat", "lon"],
                },
            ),
            types.Tool(
                name="cdmx_sql_remote",
                description='Ejecuta SQL read-only directamente en el servidor CKAN. Tabla = \'\"<resource_id>\"\'',
                inputSchema={
                    "type": "object",
                    "properties": {
                        "sql": {"type": "string"},
                    },
                    "required": ["sql"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
        import json

        try:
            result = _dispatch(cdmx, name, arguments)
        except Exception as e:
            result = {"error": str(e)}

        return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, default=str))]

    import asyncio

    asyncio.run(stdio_server(server).run())


def _dispatch(cdmx, name: str, args: dict) -> object:
    """Despachador de tools MCP → métodos de CDMX."""
    match name:
        case "cdmx_search":
            results = cdmx.search(args["query"], max_results=args.get("max_results", 10))
            return [{"name": r.get("name"), "title": r.get("title")} for r in results]

        case "cdmx_catalog":
            entries = cdmx.catalogo(track=args.get("track"))
            return [
                {"key": e.key, "track": e.track, "slug": e.slug, "notes": e.notes}
                for e in entries
            ]

        case "cdmx_fetch_resource":
            max_r = args.get("max_records", _MAX_ROWS)
            df = cdmx.fetch_resource(args["resource_id"], max_records=max_r)
            total = len(df)
            records = df.head(_MAX_ROWS).to_dict(orient="records")
            return {"total": total, "returned": len(records), "records": records}

        case "cdmx_movilidad_metro":
            df = cdmx.movilidad.metro.afluencia(
                desde=args.get("desde"),
                hasta=args.get("hasta"),
                linea=args.get("linea"),
            )
            total = len(df)
            return {"total": total, "returned": min(total, _MAX_ROWS), "records": df.head(_MAX_ROWS).to_dict(orient="records")}

        case "cdmx_seguridad_fgj":
            df = cdmx.seguridad.carpetas_fgj(
                alcaldia=args.get("alcaldia"),
                delito_contiene=args.get("delito_contiene"),
                desde=args.get("desde"),
                hasta=args.get("hasta"),
            )
            total = len(df)
            return {"total": total, "returned": min(total, _MAX_ROWS), "records": df.head(_MAX_ROWS).to_dict(orient="records")}

        case "cdmx_aire_calidad":
            df = cdmx.aire.calidad(
                contaminante=args.get("contaminante"),
                estacion=args.get("estacion"),
            )
            total = len(df)
            return {"total": total, "returned": min(total, _MAX_ROWS), "records": df.head(_MAX_ROWS).to_dict(orient="records")}

        case "cdmx_servicios_locatel":
            df = cdmx.servicios.locatel(
                alcaldia=args.get("alcaldia"),
                desde=args.get("desde"),
                hasta=args.get("hasta"),
            )
            total = len(df)
            return {"total": total, "returned": min(total, _MAX_ROWS), "records": df.head(_MAX_ROWS).to_dict(orient="records")}

        case "cdmx_finanzas_proveedores":
            df = cdmx.finanzas.proveedores(nombre_contiene=args.get("nombre_contiene"))
            total = len(df)
            return {"total": total, "returned": min(total, _MAX_ROWS), "records": df.head(_MAX_ROWS).to_dict(orient="records")}

        case "cdmx_geo_colonia_en_punto":
            result = cdmx.geo.colonia_en_punto(lat=args["lat"], lon=args["lon"])
            return result or {"error": "No se encontró colonia para ese punto"}

        case "cdmx_sql_remote":
            df = cdmx.sql_remote(args["sql"])
            total = len(df)
            return {"total": total, "returned": min(total, _MAX_ROWS), "records": df.head(_MAX_ROWS).to_dict(orient="records")}

        case _:
            raise ValueError(f"Tool desconocida: {name}")
