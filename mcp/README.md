# cdmx-data

> Hub de datos abiertos de la Ciudad de México — librería Python, servidor MCP y CLI.
>
> Construido para el Claude Impact Lab CDMX

---

## Quick Start

**Librería Python:**

```python
from cdmx_data import CDMX

cdmx = CDMX()

# Afluencia del Metro en 2024
df = cdmx.movilidad.metro.afluencia(desde="2024-01-01", linea="1")
print(df.head())

# Carpetas FGJ por alcaldía
robos = cdmx.seguridad.carpetas_fgj(
    alcaldia="Benito Juárez",
    delito_contiene="robo",
    desde="2024-01-01"
)

# Calidad del aire
pm25 = cdmx.aire.calidad(contaminante="PM25", estacion="MER")
```

**CLI:**

```bash
cdmx search "calidad del aire"
cdmx fetch metro_afluencia_simple --limit 1000 --output metro.csv
cdmx catalog --track movilidad
cdmx cache list
```

**MCP (Claude Code / Claude Desktop):**

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

---

## Instalación

```bash
pip install cdmx-data

# Con soporte geoespacial (geopandas)
pip install "cdmx-data[geo]"

# Con servidor MCP
pip install "cdmx-data[mcp]"

# Todo incluido
pip install "cdmx-data[geo,mcp]"
```

**Requisitos:** Python >= 3.10

---

## Ejemplos por track

### Movilidad

```python
cdmx = CDMX()
# Top 10 estaciones más concurridas
top = (
    cdmx.movilidad.metro.afluencia()
    .groupby("estacion")["afluencia"]
    .sum()
    .nlargest(10)
)
```

### Seguridad

```python
# Robos en Iztapalapa en 2024
robos = cdmx.seguridad.carpetas_fgj(
    alcaldia="Iztapalapa",
    delito_contiene="robo",
    desde="2024-01-01",
    hasta="2024-12-31",
)
```

### Aire

```python
# PM2.5 en estación Merced
pm25 = cdmx.aire.calidad(contaminante="PM25", estacion="MER")
```

### Servicios

```python
# Solicitudes a Locatel en Tlalpan
df = cdmx.servicios.locatel(alcaldia="Tlalpan")
```

### Finanzas

```python
# Proveedores vigentes
df = cdmx.finanzas.proveedores()
```

### Geo

```python
# Requiere pip install cdmx-data[geo]
colonia = cdmx.geo.colonia_en_punto(lat=19.42, lon=-99.16)
print(colonia["nombre"])
```

---

## Conectar a Claude Code

1. Instala: `pip install "cdmx-data[mcp]"`
2. Agrega a `.mcp.json` en tu proyecto:

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

3. Reinicia Claude Code. Las tools `cdmx_*` estarán disponibles.

Ver `examples/claude_code_mcp.md` para opciones con `uvx`.

---

## Arquitectura interna

```
datos.cdmx.gob.mx (CKAN API)
        |
        v
   ckan.py          <- cliente httpx, paginación automática
        |
        v
   cache.py         <- SQLite, TTL 6h, tabla por resource_id
        |
        +-- domains/movilidad.py  -+
        +-- domains/seguridad.py   |  Normalizan tildes/coords,
        +-- domains/aire.py        |  resuelven resource_ids,
        +-- domains/servicios.py   |  filtran DataFrames
        +-- domains/finanzas.py    |
        +-- domains/geo.py        -+
                |
                v
           core.py (CDMX)
          /          \
      cli.py       mcp_server.py
```

---

## Agregar un dataset nuevo

1. Añade una entrada a `src/cdmx_data/catalog.py`:

```python
"mi_dataset": DatasetInfo(
    key="mi_dataset",
    slug="slug-en-el-portal",
    resource_id=None,        # o el UUID si lo conoces
    track="movilidad",
    notes="Descripción breve",
),
```

2. Si necesitas filtros específicos, agrégalos en el dominio correspondiente en `domains/`.

3. Abre un PR con el nuevo dataset y un test en `tests/test_domains.py`.

---

## Licencia y atribución

MIT License. Ver [LICENSE](LICENSE).

Datos provistos por la **ADIP** (Agencia Digital de Innovación Pública de la CDMX)
bajo la [Licencia Libre Uso MX](https://datos.gob.mx/libreusomx) (≈ CC-BY 4.0).

Al usar `cdmx-data` en tu proyecto, atribuye la fuente:
> Datos: Portal de Datos Abiertos CDMX (datos.cdmx.gob.mx) — ADIP
