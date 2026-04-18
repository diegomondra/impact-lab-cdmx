# `cdmx-data` · Project Brief

Contexto completo del paquete a construir. Este documento es la fuente única de verdad técnica — consúltalo antes de cada decisión de diseño.

---

## Contexto del producto

**Qué es:** Librería Python + servidor MCP + CLI para consumir los datos abiertos de la Ciudad de México (`datos.cdmx.gob.mx`).

**Para quién:** equipos del **Claude Impact Lab CDMX** (sábado 18 abril 2026) — 5 horas de build time, necesitan arrancar rápido sin escribir boilerplate de CKAN.

**Objetivo:** ser *el hub* por el que pasan todas las consultas a datos abiertos de CDMX. Un dev escribe `cdmx.movilidad.metro.afluencia(desde="2024-01-01")` y obtiene un DataFrame limpio, sin pelearse con paginación, tildes inconsistentes, o resource_ids cambiantes.

**Tres superficies, un solo core:**
1. **Librería Python** — import directo para notebooks, Streamlit, FastAPI
2. **Servidor MCP** — `uvx cdmx-data mcp` lo expone como tools para Claude Code, Claude Desktop, Cursor
3. **CLI** — `cdmx fetch metro` para exploración rápida desde terminal

---

## El portal `datos.cdmx.gob.mx`

### Arquitectura
Corre sobre **CKAN** (plataforma open source). Jerarquía:

```
Dataset (conjunto)          →  "Afluencia diaria del Metro CDMX"
  └─ Resource (recurso)     →  "Afluencia Diaria del Metro (Simple)"
      └─ resource_id (UUID) →  0e8ffe58-28bb-4dde-afcd-e5f5b4de4ccb
```

Un dataset puede tener varios recursos. Tú consumes **un recurso a la vez** por su `resource_id`.

### Endpoints CKAN (sin auth, sin API key)

Base: `https://datos.cdmx.gob.mx/api/3/action/`

| Acción | Uso |
|---|---|
| `package_search?q=metro&rows=10` | Buscar datasets por texto |
| `package_show?id=<slug>` | Metadata de un dataset con todos sus recursos |
| `resource_show?id=<uuid>` | Metadata de un recurso (incluye last_modified) |
| `datastore_search?resource_id=<uuid>&limit=100&offset=0` | Leer registros tabulares |
| `datastore_search_sql?sql=SELECT ...` | SQL read-only. Tabla = `"<resource_id>"` con comillas |

**Respuesta estándar CKAN:**
```json
{
  "help": "...",
  "success": true,
  "result": {
    "total": 1234567,
    "records": [ { ... } ],
    "fields": [ { "id": "alcaldia", "type": "text" } ],
    "_links": { "next": "...", "start": "..." }
  }
}
```

### Gotchas confirmados del portal

1. **Cap de ~32,000 registros por request**, aunque pidas más. Paginar con `offset` o descargar CSV.
2. **Tildes y mayúsculas inconsistentes:** "Cuauhtémoc" / "Cuauhtemoc" / "CUAUHTÉMOC" conviven en los mismos datasets.
3. **Coordenadas con coma decimal en algunos recursos:** `"19,4326"` en vez de `19.4326`.
4. **Carpetas FGJ tiene DOS columnas de alcaldía:**
   - `alcaldia_hecho` — como la reportó FGJ (sucia)
   - `alcaldia_catalogo` — después de geocruce oficial (usar ESTA)
5. **El parámetro `filters` debe ser JSON urlencoded**, no dict plano.
6. **Resource_ids rotan** cuando publican versión nueva. Nunca hardcodear en producción sin fallback a `package_show`.
7. **Zona horaria:** fechas sin TZ. Asumir `America/Mexico_City`.
8. **Licencia:** Libre Uso MX (≈ CC-BY 4.0). Atribuir ADIP.

---

## Datasets del catálogo inicial

Resource IDs validados al 2026-04-18. Si alguno devuelve 404, resolver con `package_show` usando el slug.

### 🚇 Movilidad

| Key interna | Slug | Resource ID | Notas |
|---|---|---|---|
| `metro_afluencia_simple` | `afluencia-diaria-del-metro-cdmx` | `0e8ffe58-28bb-4dde-afcd-e5f5b4de4ccb` | Enero 2010 → presente, por línea y estación |
| `metro_afluencia_desglosada` | `afluencia-diaria-del-metro-cdmx` | `cce544e1-dc6b-42b4-bc27-0d8e6eb3ed72` | Desglosada por TMI/boleto/gratuidad |
| `metrobus_afluencia` | `afluencia-diaria-de-metrobus-cdmx` | `d122639e-a56a-4f26-a8b7-983464d11aaa` | Desde julio 2005 |
| `rtp_afluencia` | `afluencia-diaria-de-la-red-de-transporte-de-pasajeros` | — resolver con search | Desde enero 2022 |
| `ste_afluencia` | `afluencia-diaria-ste` | — resolver | Cablebús + Tren Ligero + Trolebús |
| `ecobici_viajes` | `viajes-ecobici` | — resolver | Viajes procesados de usuarios |
| `ciclovias` | `infraestructura-vial-ciclista` | — resolver | 651 tramos (v11, marzo 2025) |
| `gtfs` | `gtfs-estatico-transporte-publico-cdmx` | — resolver | Estándar GTFS, ZIP |

### 🔒 Seguridad

| Key interna | Slug | Resource ID | Notas |
|---|---|---|---|
| `carpetas_fgj` | `carpetas-de-investigacion-fgj-de-la-ciudad-de-mexico` | — múltiples por año, resolver con search | Enero 2016 → presente |
| `victimas_fgj` | `victimas-en-carpetas-de-investigacion-fgj` | `d543a7b1-f8cb-439f-8a5c-e56c5479eeb5` | Acumulado 2019 → presente |
| `hechos_transito` | `hechos-de-transito-ssc` | — resolver | Desde 2018 |
| `fotocivicas` | `fotocivicas` | — resolver | Cumplimiento reglamento vehicular |
| `incidentes_c5` | `incidentes-viales-c5` | — resolver | Reportes ciudadanos C5 |

### 🌬 Aire

| Key interna | Slug | Notas |
|---|---|---|
| `calidad_aire` | `calidad-del-aire` | PM2.5, O3, NO2, CO por estación SIMAT. Resolver resource_ids por contaminante. |
| `estaciones_simat` | `estaciones-simat` | Georreferenciadas |
| `meteorologia_simat` | `meteorologia-simat` | Temperatura, humedad, viento |

### 📋 Servicios (*0311)

| Key interna | Slug | Notas |
|---|---|---|
| `locatel_0311` | `solicitudes-locatel` | Tiempos de respuesta por alcaldía |

### 💰 Finanzas

| Key interna | Slug | Notas |
|---|---|---|
| `proveedores` | `padron-de-proveedores` | Personas físicas y morales vigentes |
| `deuda_publica` | `deuda-publica` | Por acreedor, tipo, intereses |
| `transparencia_presupuestaria` | `transparencia-presupuestaria` | Gasto público |
| `ley_ingresos` | `ley-de-ingresos` | Ingresos estimados |

### 🗺 Geo (transversal, usada por TODOS los tracks)

| Key interna | Slug | Notas |
|---|---|---|
| `colonias` | `catalogo-de-colonias-datos-abiertos` | GeoJSON + Shapefile. Base de cualquier mapa. |
| `alcaldias` | `alcaldias-cdmx` | 16 polígonos oficiales |
| `agebs` | `agebs-cdmx` | Áreas Geoestadísticas Básicas (unidad INEGI) |
| `cuadrantes_ssc` | `cuadrantes-de-seguridad` | 847 polígonos de SSC |

### 📦 Meta

| Key interna | Slug | Notas |
|---|---|---|
| `catalogo_completo` | `domaindatasets` | Meta-dataset: lista TODOS los datasets. Ideal para descubrimiento dinámico vía MCP. |

---

## Diseño del paquete

### Árbol de archivos objetivo

```
cdmx-data/
├── pyproject.toml
├── README.md
├── LICENSE (MIT)
├── src/
│   └── cdmx_data/
│       ├── __init__.py          # exporta CDMX, versión
│       ├── core.py              # clase CDMX (hub principal)
│       ├── ckan.py              # cliente CKAN genérico
│       ├── cache.py             # cache SQLite
│       ├── catalog.py           # registro central de datasets conocidos
│       ├── normalize.py         # tildes, alcaldías, fechas, coords
│       ├── cli.py               # Typer app — `cdmx ...`
│       ├── mcp_server.py        # servidor MCP que expone la lib como tools
│       └── domains/
│           ├── __init__.py
│           ├── movilidad.py
│           ├── seguridad.py
│           ├── aire.py
│           ├── servicios.py
│           ├── finanzas.py
│           └── geo.py
├── tests/
│   ├── test_ckan.py
│   ├── test_cache.py
│   ├── test_normalize.py
│   └── test_domains.py
└── examples/
    ├── notebook_movilidad.ipynb
    ├── streamlit_seguridad.py
    └── claude_code_mcp.md       # cómo configurar MCP en Claude Code
```

### DX objetivo

**Librería:**
```python
from cdmx_data import CDMX

cdmx = CDMX()  # cache automático, no api key

# Movilidad
df = cdmx.movilidad.metro.afluencia(desde="2024-01-01", linea="1")
top = cdmx.movilidad.metro.afluencia().groupby("estacion")["afluencia"].sum().nlargest(10)

# Seguridad — DEBE normalizar alcaldia automáticamente
robos = cdmx.seguridad.carpetas_fgj(
    alcaldia="Benito Juárez",
    delito_contiene="robo",
    desde="2024-01-01"
)

# Aire
df = cdmx.aire.calidad(contaminante="PM25", estacion="MER")

# Servicios
df = cdmx.servicios.locatel(alcaldia="Coyoacán")

# Finanzas
df = cdmx.finanzas.proveedores()

# Geo (requiere extras [geo])
gdf = cdmx.geo.colonias()  # GeoDataFrame
colonia = cdmx.geo.colonia_en_punto(lat=19.42, lon=-99.16)

# Descubrimiento (para track "Abierto")
results = cdmx.search("fotocívicas")
all_datasets = cdmx.catalogo()

# Escape hatches
df = cdmx.fetch_resource("abc-123")  # resource_id directo
df = cdmx.sql_remote('SELECT COUNT(*) FROM "abc-123"')  # SQL en el server
df = cdmx.sql("SELECT * FROM r_abc_123 LIMIT 10")  # SQL en cache local
```

**CLI:**
```bash
cdmx search "fotocívicas"
cdmx fetch metro-afluencia-simple --limit 1000 --output metro.csv
cdmx catalog --track movilidad
cdmx cache list
cdmx cache clear
cdmx mcp  # arranca el servidor MCP en stdio
```

**MCP (en `.mcp.json` de Claude Code):**
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

## Decisiones de diseño (ya tomadas — respetar)

1. **Python ≥ 3.10** (sintaxis `X | None`, `match`)
2. **HTTP client: httpx** (no requests) — soporte async futuro sin refactor
3. **Cache: SQLite** — cero dependencias extra, portable, reutilizable
4. **DataFrames: pandas** — estándar para el público del Lab
5. **geopandas es opcional** (`pip install cdmx-data[geo]`) — no todos van a hacer mapas
6. **MCP es opcional** (`pip install cdmx-data[mcp]`) — para que la lib pura sea liviana
7. **CLI con Typer + Rich** — experiencia bonita out of the box
8. **Licencia: MIT** — el Lab exige open source
9. **Sin emojis en el código.** Sí en docstrings de usuario y README.
10. **No async en v1.** Keep it simple. Async server MCP cuando sea necesario.

---

## Patrón de cacheo (crítico)

Cada método de dominio sigue este flujo:

```
1. Resolver resource_id (del catalog o con package_show si hace falta)
2. ¿Hay cache fresco (< TTL)? → leer de SQLite, filtrar, devolver
3. ¿No hay cache o está stale? → paginar desde CKAN, guardar en SQLite, devolver
4. ¿offline=True y no hay cache? → error claro
```

**TTL default: 6 horas.** Los datasets del portal se actualizan mensualmente, pero 6h da margen para re-runs durante un día de hackathon sin saturar al gobierno.

**Nombre de tabla:** `r_<resource_id_con_guiones_bajos>`. Una tabla `_cache_meta` tracea `fetched_at`, `row_count`, `source_last_modified`.

---

## Normalizaciones obligatorias

El módulo `normalize.py` debe exportar como mínimo:

- `normalize_text(s)` — lowercase + sin tildes + whitespace colapsado
- `canonical_alcaldia(raw)` — devuelve una de las 16 alcaldías canónicas o None
- `parse_date(s)` — acepta formatos `YYYY-MM-DD`, `DD/MM/YYYY`, ISO con T, etc.
- `parse_coord(value)` — maneja coma decimal

**Las 16 alcaldías canónicas (con acentos correctos):**
```
Álvaro Obregón, Azcapotzalco, Benito Juárez, Coyoacán,
Cuajimalpa de Morelos, Cuauhtémoc, Gustavo A. Madero, Iztacalco,
Iztapalapa, La Magdalena Contreras, Miguel Hidalgo, Milpa Alta,
Tláhuac, Tlalpan, Venustiano Carranza, Xochimilco
```

---

## MCP server — tools a exponer

El servidor MCP debe exponer (como mínimo) estas tools:

| Tool | Descripción | Parámetros |
|---|---|---|
| `cdmx_search` | Busca datasets en el portal | `query: str`, `max_results: int = 10` |
| `cdmx_catalog` | Lista datasets conocidos | `track: str = None` |
| `cdmx_fetch_resource` | Baja un recurso por ID | `resource_id: str`, `max_records: int = None` |
| `cdmx_movilidad_metro` | Afluencia del Metro | `desde: str = None`, `hasta: str = None`, `linea: str = None` |
| `cdmx_seguridad_fgj` | Carpetas FGJ | `alcaldia: str`, `delito_contiene: str`, `desde`, `hasta` |
| `cdmx_aire_calidad` | Calidad del aire | `contaminante: str`, `estacion: str = None` |
| `cdmx_servicios_locatel` | Solicitudes *0311 | `alcaldia: str = None` |
| `cdmx_finanzas_proveedores` | Padrón de proveedores | filtros básicos |
| `cdmx_geo_colonia_en_punto` | Geocruce por lat/lon | `lat: float`, `lon: float` |
| `cdmx_sql_remote` | SQL directo al servidor CKAN | `sql: str` |

Cada tool devuelve JSON serializable (no DataFrames). Para responses grandes, truncar a N filas y mencionar el total.

---

## Testing

**Lo mínimo aceptable:**
- `test_normalize.py` — tests unitarios de alcaldías, tildes, fechas. Sin red.
- `test_cache.py` — put/get/ttl/invalidate con SQLite en memoria.
- `test_ckan.py` — mock de httpx, verifica construcción correcta de URLs/params.
- `test_domains.py` — mock del cliente CKAN, verifica que cada método construye la query esperada.

**No hacer tests contra el portal real en CI.** Mocks siempre. Un script `examples/smoke_test.py` que sí pega al portal, para correrlo manualmente.

---

## README — secciones obligatorias

1. **Logo/título** con link al Claude Impact Lab CDMX
2. **Quick start** (3 snippets: librería / CLI / MCP)
3. **Instalación** (`pip install cdmx-data`, extras `[geo]` `[mcp]`)
4. **Ejemplos por track** (6 snippets, uno por cada challenge)
5. **Cómo conectarlo a Claude Code** (bloque MCP)
6. **Arquitectura interna** (diagrama breve: CKAN → Cache → Dominios → UI)
7. **Contributing** — cómo agregar un dataset nuevo al catálogo
8. **Licencia y atribución a ADIP**

---

## Lo que NO se construye en v1

- Async/await (posible v2)
- Web UI (los equipos la construyen encima, ese es el punto)
- Auth / multi-usuario (el portal es público)
- Scheduling/cron de refresh (que lo haga el usuario)
- Visualizaciones (responsabilidad de los equipos)
- Export a formatos exóticos (CSV y JSON basta)

---

## Referencias

- Portal: https://datos.cdmx.gob.mx/
- Docs CKAN: https://docs.ckan.org/en/latest/api/
- MCP spec: https://modelcontextprotocol.io/
- Impact Lab brief: `./Claude_Impact_Lab_CDMX.pdf`
