# Conectar cdmx-data a Claude Code via MCP

## Instalación

```bash
pip install "cdmx-data[mcp]"
```

## Configuración

Agrega esto a tu `.mcp.json` en la raíz del proyecto:

```json
{
  "mcpServers": {
    "cdmx-data": {
      "command": "uvx",
      "args": ["cdmx-data", "mcp"]
    }
  }
}
```

O si instalaste localmente:

```json
{
  "mcpServers": {
    "cdmx-data": {
      "command": "cdmx",
      "args": ["mcp"]
    }
  }
}
```

## Tools disponibles

Una vez configurado, Claude Code puede usar:

- `cdmx_search` — buscar datasets por texto
- `cdmx_catalog` — listar datasets conocidos
- `cdmx_fetch_resource` — descargar por resource_id
- `cdmx_movilidad_metro` — afluencia del Metro CDMX
- `cdmx_seguridad_fgj` — carpetas de investigación FGJ
- `cdmx_aire_calidad` — calidad del aire SIMAT
- `cdmx_servicios_locatel` — solicitudes Locatel *0311
- `cdmx_finanzas_proveedores` — padrón de proveedores
- `cdmx_geo_colonia_en_punto` — geocruce lat/lon → colonia
- `cdmx_sql_remote` — SQL directo al portal CKAN
