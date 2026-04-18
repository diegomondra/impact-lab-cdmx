# Metodología — Tus 100 pesos

**Autoría:** Agent 1 — Datos e investigación · **Fecha:** 2026-04-18

Este documento explica cómo se reorganiza el presupuesto oficial de la
Ciudad de México en las **15 categorías ciudadanas + Otros** que la
aplicación muestra, qué elecciones editoriales se tomaron y qué límites
tiene la información.

## 1. El objetivo del reordenamiento

El presupuesto de la CDMX ya es público. Lo publica la Secretaría de
Administración y Finanzas en `datos.cdmx.gob.mx` y se visualiza de forma
oficial en `tudinero.cdmx.gob.mx`. Su estructura, sin embargo, responde
a tres lógicas contables — funcional, administrativa y programática —
que tienen sentido para una persona que lleva la contabilidad
gubernamental, pero no para una vecina que quiere entender en qué se
gastan sus impuestos.

El trabajo aquí es un **reordenamiento editorial**, no una investigación
nueva. Cada peso mostrado en la app se puede rastrear a una fila
específica del CSV oficial. El valor agregado está en la clasificación.

## 2. Las 15 categorías ciudadanas (Nivel 1)

La taxonomía ciudadana es:

> Agua · Transporte público · Calles y banquetas · Basura y limpia ·
> Parques y espacios públicos · Seguridad · Justicia · Salud · Educación ·
> Apoyos sociales · Cultura y deporte · Medio ambiente · Alumbrado ·
> Gobierno y administración · Deuda · Otros

Se eligieron aplicando la regla: **"si alguien que camina por la ciudad
puede señalar algo y decir 'eso es' (el agua de la llave, el camión que
pasa, el parque donde juegan mis hijos), es categoría. Si no, se agrupa
en Gobierno y administración o en Otros."**

El orden de la cuadrícula principal sigue esa misma lista: las primeras
categorías son las que una persona ve todos los días al salir de casa;
las últimas corresponden a funciones que, aunque importantes, son
internas a la administración pública.

## 3. El mapeo — cómo llega cada peso a su categoría

El CSV de egresos trae 63 columnas por fila. Usamos tres campos para
clasificar:

1. **`programa_presupuestario`** (código estable: `E169`, `S227`, etc.)
2. **`desc_programa_presupuestario`** (nombre del programa)
3. **`desc_funcion`** (clasificación COFOG funcional)

La regla, en orden de precedencia:

1. **Mapeo explícito por código de programa** (≈168 códigos). Los
   programas grandes y reconocibles se clasifican a mano, con una
   justificación por escrito en `crosswalk/crosswalk.csv`. Este grupo
   cubre más del 95 % del gasto total.
2. **Coincidencia por palabra clave** sobre el nombre del programa
   (`Agua`, `Metro`, `Alumbrado`, etc.). Atrapa la cola larga de
   programas pequeños.
3. **Fallback por `desc_funcion`**. La clasificación COFOG asegura que
   cualquier fila sin mapeo explícito ni palabra clave aterrice en una
   categoría razonable.
4. **Si todo falla → "Otros"**, con rationale explícita.

Todo el código vive en `data/scripts/build_crosswalk_and_parquets.py`.
No hay hojas de cálculo ocultas. Cada decisión es reproducible.

## 4. Decisiones editoriales que merecen escrutinio

Transparencia sobre las llamadas de juicio:

- **Pensiones y Jubilaciones (`J001`, `E195`)** → *Gobierno y
  administración*. Son pagos a ex-trabajadores del propio gobierno, no
  transferencias sociales a la ciudadanía. Mezclarlas con `Mi Beca` o
  `Pensión Adultos Mayores` daría una falsa sensación de volumen social.
- **Ministración a Órganos Autónomos y de Gobierno (`R003`, ≈23 mil mdp)**
  → *Gobierno y administración*. Cubre el Congreso, Tribunal Superior,
  IECM, InfoCDMX y otros entes autónomos. No es gasto ciudadano directo.
- **Gobierno y seguridad en alcaldías (`E200`, ≈10 mil mdp)** →
  *Gobierno y administración*. Es el gasto de autogobierno de las
  alcaldías. Una versión futura podría dividir la fracción de seguridad
  hacia la categoría *Seguridad*.
- **Infraestructura Urbana (`K023`, ≈12.6 mil mdp)** → *Calles y
  banquetas*. Es el programa más amplio de SOBSE; mezcla vialidad,
  banquetas, alumbrado y mobiliario. Se deja entero para no inventar
  precisión que la fuente no ofrece.
- **Vivienda (`S061`, `S027`, `S047`, `S053`, INVI)** → *Apoyos
  sociales*. La taxonomía oficial no incluye una categoría "Vivienda"
  porque el tamaño individual es modesto y encaja mejor como apoyo
  social.

## 5. "Gobierno y administración" no es donde escondemos el dinero

El riesgo de una taxonomía como ésta es convertir "Gobierno y
administración" en un vertedero donde van a morir todos los rubros
difíciles de explicar. Para evitarlo:

- El rationale de cada programa en `Gobierno y administración` está
  escrito explícitamente en `crosswalk.csv`.
- En la app, esta categoría expone sus sub-programas de Nivel 2 igual
  que cualquier otra — no se oculta detrás de un total agregado.
- El monto total de la categoría se compara contra la suma del decreto
  publicado en la Gaceta Oficial para verificar que no hay "fugas"
  hacia allá.

Actualmente representa alrededor del 25-30 % del presupuesto. Ese
porcentaje **refleja realidad administrativa** (pagos a órganos
autónomos, pensiones del gobierno, overhead de las alcaldías, política
fiscal, etc.), no una cobertura de vacíos del análisis.

## 6. Atribución a alcaldías

El CSV principal **no trae una columna de alcaldía territorial**.
Solo distingue la unidad responsable del ejercicio del gasto. Por eso
el filtro de alcaldía es **heurístico**:

- Se incluye únicamente el gasto cuya `desc_unidad_responsable` coincide
  con una de las 16 alcaldías (`Alcaldía Iztapalapa`, `Alcaldía
  Cuauhtémoc`, etc.).
- El `attribution_method` queda registrado como
  `"heuristic_unidad_responsable"` en `data/clean/budget_by_alcaldia.parquet`.
- Esto representa **~18.4 % del presupuesto total** (≈49 mil mdp en
  2024). El 81.6 % restante se ejerce desde dependencias centrales
  (SSC, SACMEX, SOBSE, etc.) y órganos autónomos que atienden a toda
  la ciudad.

**Lo que el filtro NO dice:** no dice cuánto se gastó *físicamente
dentro* de una alcaldía. Una obra del Metro en Iztapalapa, por ejemplo,
se ejerce desde el STC Metro (dependencia central), no desde la
alcaldía. Para ese tipo de análisis se requiere el SRFT u otras fuentes
que todavía no se integran.

## 7. Lo que no se incluye (Nivel 3 no se intenta)

Por debajo del `desc_programa_presupuestario` el CSV solo tiene
`desc_partida_especifica` — rubros contables como "material de oficina"
o "servicios de energía eléctrica". Exponerlos al usuario final
degradaría la experiencia sin agregar información útil.

Las obras específicas (Cablebús L3, Utopías Iztapalapa, Sectorización
Iztapalapa, etc.) **viven en documentos narrativos del Paquete
Económico**, no en el CSV. Se documentan como:

- Menciones editoriales en el Nivel 2 (ej. "Construcción de
  Infraestructura de Transporte Público — incluye Cablebús L3,
  ampliación Trolebús, modernización L1 Metro").
- Cuando hay montos verificados en fuentes oficiales, se listan en
  `data/raw/narrative_sources/named_programs_2024.csv`.

La vista de obra específica se complementa con el mapa
`notebooks/obra_map.py`, que usa el padrón de Recursos Federales
Transferidos (23 mil obras con coordenadas 2013-2018, extendibles hasta
2022 con `data/raw/proyectos_federales_transferidos_2013_2022t1.csv`).

## 8. Años incluidos

La app despliega dos años:

- **2024 aprobado** (`egresos_2024_aprobado.csv`) — "lo que el gobierno
  prometió gastar este año".
- **2022 Cuenta Pública** (`egresos_2022_cp.csv`) — "lo que efectivamente
  se ejerció" el último año cerrado con información publicada.

El 2023 aún no tiene Cuenta Pública publicada y 2024 no tiene reportes
trimestrales. Estos huecos son del portal, no nuestros.

## 9. Validación cruzada contra el total publicado

La app expone una **invariante dura**: la suma de los Niveles 1 por año
debe coincidir con la cifra publicada en el Decreto de Presupuesto de
Egresos correspondiente, dentro de un margen del 0.5 %.

Resultado al cierre de esta versión:

| Año | Suma Nivel 1 (MXN) | Decreto publicado | Δ |
|-----|---|---|---|
| 2024 | 267,965,350,437 | 267,965,350,437 | **0.000 %** |
| 2022 | 234,000,875,723 | 234,005,875,723 | **0.002 %** |

Si en algún momento la invariante se rompe, la app lo grita en consola
antes de servir.

## 10. Limitaciones conocidas

- **No hay desagregación por obra** en el CSV principal; se suple con el
  suplemento narrativo descrito en §7.
- **No hay trimestres 2024** publicados al momento de escribir esto; el
  año corriente solo se muestra con montos aprobados, no ejercidos.
- **Cuenta Pública 2023** no publicada; los montos ejercidos más
  recientes corresponden a 2022.
- **2025 aprobado** aún no publicado en `datos.cdmx.gob.mx` (aunque el
  Congreso lo aprobó en diciembre 2024).
- **La atribución a alcaldías es heurística** (§6) — no es geográfica.
- **`Otros`** es una categoría honesta, no un basurero: contiene rubros
  no clasificables (turismo, marca ciudad, programas muy pequeños). Se
  declara explícitamente cuánto vale.

## 11. Fuentes

- **Datos de egresos:** Secretaría de Administración y Finanzas de la
  CDMX → `datos.cdmx.gob.mx/dataset/presupuesto-de-egresos`.
- **Decreto de Presupuesto de Egresos 2024:** Gaceta Oficial de la
  Ciudad de México, 26 de diciembre de 2023.
- **Proyecto de Presupuesto de Egresos 2024 (exposición de motivos):**
  finanzas.cdmx.gob.mx → Paquete Económico 2024 Tomo I.
- **Datos de ingresos:** `datos.cdmx.gob.mx/dataset/ingresos`.
- **Obras con georreferencia:**
  `datos.cdmx.gob.mx/dataset/recursos-federales-transferidos`.

Todos los URLs resolverables están en `data/clean/source_links.csv`,
ligados fila por fila a las vistas de la app.
