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
            # ─── Dashboard 'La ruta de tu peso' — presupuesto CDMX ───
            types.Tool(
                name="cdmx_presupuesto_summary",
                description="Resumen del presupuesto CDMX por 16 categorías ciudadanas (Agua, Transporte, Seguridad, Salud…). Devuelve Level-1 con monto_aprobado y per_100_of_total. Fuente: data/clean/budget_tree.parquet.",
                inputSchema={
                    "type": "object",
                    "properties": {"year": {"type": "integer", "description": "2018–2024"}},
                },
            ),
            types.Tool(
                name="cdmx_presupuesto_drill",
                description="Programas Level-2 dentro de una categoría ciudadana (ej. Agua → SACMEX, Sectorización Iztapalapa…). Devuelve display_name, monto_aprobado, per_100_of_parent y rationale editorial.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "citizen_category": {"type": "string", "description": "Una de las 16: Agua, Transporte público, Calles y banquetas, Basura y limpia, Parques y espacios públicos, Seguridad, Justicia, Salud, Educación, Apoyos sociales, Cultura y deporte, Medio ambiente, Alumbrado, Gobierno y administración, Deuda, Otros"},
                        "year": {"type": "integer"},
                        "top_n": {"type": "integer", "default": 20},
                    },
                    "required": ["citizen_category"],
                },
            ),
            types.Tool(
                name="cdmx_presupuesto_named_programs",
                description="Programas emblemáticos con nombre propio (Cablebús L3, Utopías, Pilares, Mi Beca, Altépetl, Cosecha de Lluvia, Comedores…) extraídos del Paquete Económico 2024. No aparecen como desc_programa_presupuestario en la CSV oficial.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "subcadena en display_name / ente_ejecutor / section"},
                        "top_n": {"type": "integer", "default": 20},
                    },
                },
            ),
            types.Tool(
                name="cdmx_presupuesto_egresos",
                description="Agregado de egresos 2018–2024 (Cuenta Pública + trimestre + aprobado). Agrupa por función, unidad responsable o capítulo. Devuelve monto_aprobado vs monto_ejercido.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "year": {"type": "integer", "description": "2018–2024. Si se omite, agrega todos los años."},
                        "group_by": {"type": "string", "enum": ["desc_funcion", "desc_unidad_responsable", "desc_capitulo"], "default": "desc_funcion"},
                        "top_n": {"type": "integer", "default": 15},
                    },
                },
            ),
            types.Tool(
                name="cdmx_presupuesto_ingresos",
                description="Ingresos CDMX por rubro, concepto o tipo. periodo=Anual (Ley de Ingresos/planeado) o 'Cuenta Pública' (recaudado real).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "ciclo": {"type": "integer"},
                        "periodo": {"type": "string", "enum": ["Anual", "Cuenta Pública"]},
                        "group_by": {"type": "string", "enum": ["desc_rubro", "desc_concepto", "desc_tipo_recurso_clase"], "default": "desc_rubro"},
                        "top_n": {"type": "integer", "default": 20},
                    },
                },
            ),
            types.Tool(
                name="cdmx_presupuesto_rally_obras",
                description="Obras federales georreferenciadas 2013–2018 (Rally ¿Cómo van las obras?). Filtrable por alcaldía, ramo federal y ciclo. Devuelve id, nombre_proyecto, contratista, monto_ejercido, avance_fisico.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "alcaldia": {"type": "string"},
                        "ramo": {"type": "string"},
                        "ciclo_from": {"type": "integer"},
                        "ciclo_to": {"type": "integer"},
                        "top_n": {"type": "integer", "default": 15},
                    },
                },
            ),
            types.Tool(
                name="cdmx_presupuesto_crosswalk",
                description="Busca un programa presupuestario en el crosswalk editorial por subcadena en source_label o display_name. Devuelve su citizen_category asignada y el rationale.",
                inputSchema={
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"],
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

        # ─── Dashboard 'La ruta de tu peso' ───
        case "cdmx_presupuesto_summary":
            df = cdmx.presupuesto.budget_summary(year=args.get("year"))
            return {
                "year": args.get("year"),
                "source": "data/clean/budget_tree.parquet",
                "total_monto_aprobado": float(df["monto_aprobado"].sum()) if len(df) else 0,
                "records": df.to_dict(orient="records"),
            }

        case "cdmx_presupuesto_drill":
            df = cdmx.presupuesto.budget_drill(
                citizen_category=args["citizen_category"],
                year=args.get("year"),
                top_n=args.get("top_n", 20),
            )
            return {
                "citizen_category": args["citizen_category"],
                "year": args.get("year"),
                "source": "data/clean/budget_tree.parquet + crosswalk/crosswalk.csv",
                "total_monto_aprobado": float(df["monto_aprobado"].sum()) if len(df) else 0,
                "records": df.to_dict(orient="records"),
            }

        case "cdmx_presupuesto_named_programs":
            df = cdmx.presupuesto.named_programs(
                query=args.get("query"),
                top_n=args.get("top_n", 20),
            )
            return {
                "query": args.get("query"),
                "source": "crosswalk/named_programs_2024.csv (Paquete Económico 2024)",
                "total_filtered": float(df["monto_aprobado_mxn"].sum()) if len(df) else 0,
                "records": df.to_dict(orient="records"),
            }

        case "cdmx_presupuesto_egresos":
            df = cdmx.presupuesto.egresos_aggregate(
                year=args.get("year"),
                group_by=args.get("group_by", "desc_funcion"),
                top_n=args.get("top_n", 15),
            )
            return {
                "year": args.get("year"),
                "group_by": args.get("group_by", "desc_funcion"),
                "source": "data/egresos_{2018..2024}_{cp|aprobado|trimestre}.csv",
                "records": df.to_dict(orient="records"),
            }

        case "cdmx_presupuesto_ingresos":
            df = cdmx.presupuesto.ingresos(
                ciclo=args.get("ciclo"),
                periodo=args.get("periodo"),
                group_by=args.get("group_by", "desc_rubro"),
                top_n=args.get("top_n", 20),
            )
            return {
                "ciclo": args.get("ciclo"),
                "periodo": args.get("periodo"),
                "group_by": args.get("group_by", "desc_rubro"),
                "source": "data/ingresos_main.csv",
                "records": df.to_dict(orient="records"),
            }

        case "cdmx_presupuesto_rally_obras":
            df = cdmx.presupuesto.rally_obras(
                alcaldia=args.get("alcaldia"),
                ramo=args.get("ramo"),
                ciclo_from=args.get("ciclo_from"),
                ciclo_to=args.get("ciclo_to"),
                top_n=args.get("top_n", 15),
            )
            return {
                "filters": {k: args.get(k) for k in ("alcaldia", "ramo", "ciclo_from", "ciclo_to")},
                "source": "data/rally_obras.csv (Rally ¿Cómo van las obras? 2013–2018)",
                "total_filtered": float(df["monto_ejercido"].sum()) if "monto_ejercido" in df.columns and len(df) else 0,
                "records": df.to_dict(orient="records"),
            }

        case "cdmx_presupuesto_crosswalk":
            df = cdmx.presupuesto.crosswalk_lookup(query=args["query"])
            return {
                "query": args["query"],
                "source": "crosswalk/crosswalk.csv",
                "records": df.to_dict(orient="records"),
            }

        case _:
            raise ValueError(f"Tool desconocida: {name}")
