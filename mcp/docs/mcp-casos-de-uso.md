# Casos de uso: cdmx-data MCP en Claude Code

El servidor MCP `cdmx-data` expone datos abiertos de la Ciudad de México directamente en conversaciones con Claude. Los ejemplos siguientes son prompts que puedes escribir tal cual.

---

## Movilidad

**¿Cuántos pasajeros usaron el Metro en enero 2026?**
> "Usando cdmx_movilidad_metro, dame la afluencia total del metro CDMX de enero 2026 (desde 2026-01-01 hasta 2026-01-31). Agrupa por línea y ordena de mayor a menor."

**Comparar líneas del Metro**
> "Con cdmx_movilidad_metro trae la afluencia del primer trimestre 2026. Dime cuál fue la línea más usada y cuál la menos usada, con sus totales."

**Tendencia semanal**
> "Obtén la afluencia diaria del Metro en febrero 2026 con cdmx_movilidad_metro. Calcula el promedio por día de la semana y dime qué día tiene más demanda."

---

## Seguridad

**Resumen de delitos por alcaldía**
> "Con cdmx_seguridad_fgj trae las carpetas FGJ del primer trimestre 2026. Cuenta cuántas carpetas hay por alcaldía y ordénalas de mayor a menor."

**Delitos específicos**
> "Usa cdmx_seguridad_fgj con delito_contiene='robo' para el período 2026-01-01 a 2026-03-31. ¿En qué alcaldía ocurrieron más robos?"

**Análisis de una alcaldía**
> "Con cdmx_seguridad_fgj filtra por alcaldia='Cuauhtémoc' en Q1 2026. Lista los 5 delitos más frecuentes con su conteo."

---

## Calidad del Aire

**Estado actual del aire**
> "Usa cdmx_aire_calidad con contaminante='PM25' y dime cuáles estaciones SIMAT registraron los niveles más altos. Indica si superan la norma de 45 µg/m³."

**Comparar contaminantes**
> "Trae datos de O3 y NO2 con cdmx_aire_calidad (una llamada por contaminante). ¿Qué zonas de la ciudad tienen peor calidad del aire en ambos indicadores?"

**Estación específica**
> "Con cdmx_aire_calidad, contaminante='CO' y estacion='MER', dame los registros disponibles y calcula el promedio."

---

## Servicios Ciudadanos

**Volumen de llamadas Locatel**
> "Usa cdmx_servicios_locatel con desde='2026-01-01' y hasta='2026-03-31'. ¿Cuántas solicitudes hubo por alcaldía? ¿Cuál generó más llamadas?"

**Tiempo de respuesta**
> "Con cdmx_servicios_locatel trae los datos de Q1 2026. Si hay columna de tiempo de atención, dime el promedio por alcaldía."

---

## Finanzas Públicas

**Quién le vende al gobierno**
> "Usa cdmx_finanzas_proveedores con nombre_contiene='construcción'. Lista los proveedores encontrados."

**Explorar el padrón**
> "Con cdmx_finanzas_proveedores trae los primeros registros. Describe las columnas disponibles y dame un conteo por tipo de persona (física vs moral)."

---

## Descubrimiento y exploración

**¿Qué datos hay disponibles?**
> "Usa cdmx_catalog con track='seguridad' y lista todos los datasets disponibles con su descripción."

**Buscar un dataset desconocido**
> "Con cdmx_search busca 'accidentes viales' en el portal de datos de CDMX. ¿Qué datasets encuentras?"

**Acceso directo por ID**
> "Usa cdmx_fetch_resource con resource_id='0e8ffe58-28bb-4dde-afcd-e5f5b4de4ccb' y max_records=50. Describe las columnas que tiene."

---

## Análisis cruzado

**Seguridad y movilidad juntos**
> "Quiero entender si los días con más afluencia en el Metro tienen más incidentes. Usa cdmx_movilidad_metro y cdmx_seguridad_fgj para febrero 2026. Cruza por fecha y dime si ves correlación."

**Mapa mental de una alcaldía**
> "Para la alcaldía Iztapalapa en Q1 2026: usa cdmx_seguridad_fgj para ver delitos y cdmx_servicios_locatel para llamadas. Resume el panorama de seguridad y servicios."

---

## Con datos locales descargados

Si ya tienes CSVs en `./data/` (descargados con `descarga_periodo.py`), el MCP los usa sin tocar la API:

**Análisis offline**
> "Tengo datos locales de Q1 2026. Con cdmx_movilidad_metro y cdmx_seguridad_fgj dame un resumen ejecutivo: top 3 líneas de metro por afluencia y top 3 alcaldías por carpetas FGJ."

**SQL directo sobre datos locales**
> "Usa cdmx_sql_remote para consultar: SELECT linea, SUM(afluencia) FROM \"<resource_id>\" GROUP BY linea ORDER BY 2 DESC"

---

## Tips

- Los tools devuelven máximo **100 filas** por llamada; pide a Claude que agrupe o filtre antes si el dataset es grande.
- Combina múltiples tools en un mismo prompt para análisis cruzados.
- Si no sabes el `resource_id`, usa primero `cdmx_catalog` o `cdmx_search`.
- El MCP detecta automáticamente `./data/` — si ejecutas Claude Code desde el directorio de tu proyecto, usa los CSVs locales sin configuración extra.
