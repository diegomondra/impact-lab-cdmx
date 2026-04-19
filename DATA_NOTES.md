# DATA_NOTES — hour-0 data inventory & depth assessment

**Agent 1 — Data & Research · 2026-04-18**

Status: GREEN. All data successfully downloaded and verified. No BLOCKERS.
Level-2 "named programs" ambition confirmed achievable; alcaldía filter
confirmed achievable from the main egresos file (better than expected —
Recursos Transferidos not required for the filter).

---

## TL;DR for the human lead

1. **Data is on disk. 18 files. ~200 MB. Repro via `bash scripts/download_data.sh`.**
2. **Published-headline check: `egresos_2024_aprobado.csv` sums to
   MXN 267,965,350,437.** This matches the CDMX Decreto de Presupuesto de
   Egresos 2024 total to the peso. Mismatch = 0.00%.
3. **Level 2 is viable.** 169 programs; ~70-80% citizen-recognizable as-is;
   the rest need editorial `display_name` cleanup or roll-up into "Otros".
4. **Alcaldía filter is viable straight from the main CSV.** All 16
   alcaldías appear as `desc_unidad_responsable`, summing to MXN 49.25 B
   (18.38% of 2024 budget). Recursos Transferidos is redundant for filter
   use; keep it only as a reference dataset.
5. **Best real-ejercido corpus: `egresos_2022_cp.csv`** (Cuenta Pública
   2022). 22,261 rows, same 63-col schema, MXN 267.99 B ejercido. The
   canonical "what was actually spent" dataset. 2023 Cuenta Pública is not
   yet published; 2024 has only aprobado (no trimestres yet).
6. **Recommended lead dataset for the demo: `egresos_2024_aprobado.csv`**
   (268 B MXN, current-year "promises"), with `egresos_2022_cp.csv` as the
   honest-accountability counterpoint (closed-year "actuals").
7. **Ingresos sidebar:** `ingresos_fuentes.csv` is an 8-row pre-aggregated
   "where does the money come from" view — Recursos federales vs Ingresos
   locales vs Endeudamiento etc. — ready to render with almost no work.

---

## 1. Inventory

All datasets live under `data/` (Tier 1 — consumed by existing notebooks)
or `data/raw/` (Tier 2+). Schema dictionaries under
`data/raw/dictionaries/`. All commits go through `scripts/download_data.sh`,
re-runnable and idempotent (`dl()` helper skips existing files).

### Tier 1 — consumed directly by `notebooks/*`

| File | Size | Rows | Key note |
|---|---|---|---|
| `data/egresos_2024_aprobado.csv` | 14 MB | 19,453 | 2024 approved — PRIMARY source of truth for the demo |
| `data/egresos_2023_aprobado.csv` | 17 MB | 22,457 | 2023 approved — prior-year comparison |
| `data/egresos_2023_03_trimestre.csv` | 21 MB | 27,129 | 2023 cumulative Jan–Sep ejercido |
| `data/rally_obras.csv` | 32 MB | 23,410 | Rally "¿Cómo van las obras?" — federal georef 2013–2018 |

### Tier 2 — additional CDMX egresos (real ejercido + trend)

| File | Size | Rows | Key note |
|---|---|---|---|
| `data/raw/egresos_2022_cp.csv` | 24 MB | 22,261 | 2022 Cuenta Pública — most recent real full-year ejercido |
| `data/raw/egresos_2022_aprobado.csv` | 10 MB | 13,157 | 2022 approved — pairs with 2022 CP |
| `data/raw/egresos_2023_01_trimestre.csv` | 18 MB | — | 2023 Q1 ejercido |
| `data/raw/egresos_2023_02_trimestre.csv` | 19 MB | — | 2023 Q2 ejercido |
| `data/raw/egresos_2021_cp.csv` | 22 MB | — | 2021 Cuenta Pública (historical) |
| `data/raw/egresos_2020_cp.csv` | 26 MB | — | 2020 Cuenta Pública (historical) |

### Tier 3 — CDMX Ingresos

| File | Size | Rows | Key note |
|---|---|---|---|
| `data/raw/ingresos_2018_2024.csv` | 532 KB | 2,281 | Granular estimado + recaudado 2018-2024 |
| `data/raw/ingresos_fuentes.csv` | 899 B | 8 | **Ready-to-render aggregated "de dónde viene" view** |
| `data/raw/ingresos_treemap.csv` | 334 KB | — | Treemap rollup |

### Tier 4 — CDMX's own pre-aggregated treemaps (reference material for crosswalk)

| File | Size | Note |
|---|---|---|
| `data/raw/egresos_2024_a_donde_va.csv` | 657 B | 10 sectors CDMX uses on tudinero — quick-win taxonomy cross-check |
| `data/raw/egresos_2024_treemap_unidad.csv` | 8.3 KB | Unidad responsable → presupuesto_2023 |
| `data/raw/egresos_2024_treemap_capitulo.csv` | 3.8 KB | Capítulo → concepto → presupuesto_2023 |
| `data/raw/egresos_2024_como_cambia.csv` | 507 KB | 3,239 rows stacked — trend 2019-2024 |

⚠️ Naming bug on datos.cdmx.gob.mx: these files live under the
"Presupuesto de egresos 2024" dataset but the columns inside are
"Presupuesto 2023" / `presupuesto_2023`. CDMX has not refreshed their
treemap files for 2024. Use for structure/sectors, not for 2024 amounts.

### Tier 5 — Recursos Transferidos a Alcaldías

| File | Size | Note |
|---|---|---|
| `data/raw/recursos_transferidos_alcaldias.xlsx` | 411 KB | XLSX, last refresh 2022-08. Not needed for filter (see §3). |

### Tier 5b — Federal-transferidos superset (extends Rally 2013→2022)

| File | Size | Rows | Note |
|---|---|---|---|
| `data/raw/proyectos_federales_transferidos_2013_2022t1.csv` | 112 MB | 115,075 | Same SRFT universe as `rally_obras.csv` (federal $$ in CDMX) but extended from 2013-2018 (23,410 rows) to 2013-2022 (~60k NEW georef'd projects in 2019-2022 across Ramo 23 / Ramo 9 / Ramo 12 / FORTAMUN / FAIS etc.). 83 cols. Feeds the `obra_map.py` sibling view with much richer geographic coverage — 2019-2022 gives citizens obras they can actually remember (Cablebús L1/L2, Utopías construction phase, etc.). Source: `datos.cdmx.gob.mx/dataset/recursos-federales-transferidos`. Updated 2022-06. |

⚠️ **Rally vs superset overlap:** 2013-2018 is duplicate between
`rally_obras.csv` (23,410 rows, 73 cols) and this file
(first ~54,400 rows of 115,075). The frozen `obra_map.py` notebook
points at `rally_obras.csv`; Agent 2 should decide whether to swap the
loader or keep both. Minimum change: `obra_map.py` frozen, use Rally
for the existing sibling view, use the superset only if Agent 3 wants
to extend coverage to 2019-2022.

### Tier 5c — Entes Públicos catalog

| File | Size | Note |
|---|---|---|
| `data/raw/entes_publicos_cdmx_2024.xlsx` | 13 KB | Catalog of all dependencias / órganos desconcentrados / entidades / alcaldías registered as receiving budget in 2024. Useful cross-reference to validate `desc_unidad_responsable` values in the crosswalk. |

### Tier 6 — Data dictionaries

| File | Size | Note |
|---|---|---|
| `data/raw/dictionaries/diccionario_presupuesto_egresos.xlsx` | 82 KB | Egresos schema reference |
| `data/raw/dictionaries/diccionario_ingresos.xlsx` | 42 KB | Ingresos schema reference |
| `data/raw/dictionaries/diccionario_recursosalasalcaldias.xlsx` | 61 KB | Recursos Transferidos schema reference |
| `data/raw/dictionaries/diccionario_recursos_federales.xlsx` | 19 KB | SRFT 83-column schema for Tier 5b superset |
| `data/raw/dictionaries/nota_aclaratoria_transferencias_federales.pdf` | 57 KB | SRFT methodology notes from CDMX |

---

## 2. Published-headline check (BLOCKER gate)

Per the Agent 1 brief, a >1 % mismatch vs CDMX's published headline is a
BLOCKER. This check passes.

| Dataset | Our sum | Published headline | Δ |
|---|---|---|---|
| `egresos_2024_aprobado.csv` · `monto_aprobado` | **267,965,350,437** | 267,965.35 M MXN (Decreto de Presupuesto de Egresos 2024, Gaceta Oficial CDMX) | **0.00 %** ✓ |
| `egresos_2023_aprobado.csv` · `monto_aprobado` | 248,415,083,383 | ≈ 248 B (Decreto 2023) | consistent with rounded headline |
| `egresos_2022_cp.csv` · `monto_ejercido` | 267,985,965,289 | ≈ 267.99 B (Cuenta Pública 2022 anexo) | consistent |
| `egresos_2022_cp.csv` · `monto_aprobado` | 234,000,875,723 | ≈ 234 B (Decreto 2022) | consistent |

Gate: **PASS**. No blocker.

---

## 3. Depth assessment (the hour-0 question)

### Level 1 — Citizen categories — **ACHIEVABLE**

`desc_funcion` gives 21 raw buckets (COFOG-style functional classification).
Our editorial crosswalk will collapse these into ~12-15 citizen-facing
categories using `desc_funcion` + `desc_unidad_responsable` + (where
necessary) `desc_programa_presupuestario`.

Raw distribution, 2024 aprobado (top contributors):

| Share | Amount (MXN) | `desc_funcion` |
|---|---|---|
| 21.72 % | 58.21 B | Vivienda y Servicios a la Comunidad |
| 16.70 % | 44.76 B | Asuntos de Orden Público y de Seguridad Interior |
| 12.19 % | 32.66 B | Transporte |
|  8.71 % | 23.35 B | Justicia |
|  7.91 % | 21.21 B | Salud |
|  7.18 % | 19.25 B | Protección Social |
|  5.09 % | 13.63 B | Educación |
|  3.55 % |  9.52 B | Protección Ambiental |
|  3.48 % |  9.32 B | Transacciones de la Deuda Pública |
|  3.35 % |  8.97 B | Minería, Manufacturas y Construcción |
|  3.06 % |  8.19 B | Asuntos Financieros y Hacendarios |
|  1.98 % |  5.30 B | Coordinación de la Política de Gobierno |
|  1.70 % |  4.55 B | Recreación, Cultura y Otras Manifestaciones Sociales |
|  1.15 % |  3.07 B | Asuntos Económicos, Comerciales y Laborales |
|  0.79 % |  2.11 B | Legislación |
|  0.53 % |  1.43 B | Otros Servicios Generales |
|  0.48 % |  1.29 B | Otros Asuntos Sociales |
|  0.22 % |  0.58 B | Otras Industrias y Otros Asuntos Económicos |
|  0.12 % |  0.33 B | Ciencia, Tecnología e Innovación |
|  0.09 % |  0.23 B | Turismo |
|  0.00 % |  0.00 B | Agropecuaria, Silvicultura, Pesca y Caza |

CDMX's own editorial slicing (from `egresos_2024_a_donde_va.csv`, 10
sectors): Seguridad Ciudadana / Transportes y Vialidad / Salud / Medio
Ambiente / Obras y Servicios / Educación / Deuda Pública / Desarrollo
Social / Desarrollo Urbano y Vivienda / Desarrollo Económico. Useful
sanity cross-reference for the taxonomy.

### Level 2 — Named programs — **ACHIEVABLE**

`desc_programa_presupuestario`: 169 unique values in the 2024 aprobado
CSV. Citizen-legibility spot-check below.

**20-row sample across `desc_funcion` (raw, no editorial cleanup):**

| `desc_funcion` | `desc_programa_presupuestario` |
|---|---|
| Vivienda y Servicios a la Comunidad | Infraestructura Urbana |
| Vivienda y Servicios a la Comunidad | Vivienda en Conjunto |
| Asuntos de Orden Público | Acciones de Búsqueda, Localización e Identificación de Personas |
| Asuntos de Orden Público | Cumplimiento de los Programas de Protección Civil |
| Transporte | Provisiones para Contingencias |
| Transporte | Construcción, Ampliación y Mejoramiento de Infraestructura de Transporte Público |
| Justicia | Atención Prioritaria a Personas Egresadas del Sistema de Justicia Penal |
| Justicia | Apoyo para el Desarrollo Integral de la Mujer |
| Salud | Prevención de Enfermedades y Promoción a la Salud para el Bienestar |
| Salud | Provisiones para Contingencias |
| Protección Social | Desarrollo de Los Pueblos y Barrios Originarios y Comunidades Indígenas Residentes |
| Protección Social | Fomento, Constitución y Fortalecimiento de las Empresas Sociales y Solidarias (FOCOFESS) |
| Educación | Rehabilitación, Equipamiento y Construcción de Infraestructura Educativa |
| Educación | Fortalecimiento a la Educación Media Superior |
| Protección Ambiental | Conducción de la Política Del Medio Ambiente |
| Protección Ambiental | Acceso a la Justicia Ambiental, Urbana y de Protección y Bienestar Animal |
| Deuda Pública | Servicio de la Deuda |
| Deuda Pública | Devolución de Ingresos Percibidos Indebidamente |
| Minería, Manufacturas y Construcción | Producción y Comercialización de Mezclas Asfálticas |
| Minería, Manufacturas y Construcción | Actividades de Apoyo Administrativo |

**Citizen-legibility verdict:** roughly 70-80% of the 20 are legible as-is
or with light editorial cleanup ("Infraestructura Urbana," "Servicio de la
Deuda," "Vivienda en Conjunto," "Servicio de Agua Potable"). The remaining
~20-30% are bureaucratic labels ("Actividades de Apoyo Administrativo,"
"Provisiones para Contingencias," "Ministración para Órganos Autónomos")
that must either get a cleaned-up `display_name` in the crosswalk or roll
up to "Otros" within their citizen_category. No row reveals raw partida
codes like 3411 — that level is `desc_partida_especifica`, which we will
not expose.

**Top-20 programs by 2024 `monto_aprobado` (citizen-recognizable bolded):**

| Code | MXN | Program |
|---|---|---|
| E169 | 38.3 B | **Prevención del Delito y Seguridad Ciudadana** |
| E042 | 27.1 B | **Operación y Mantenimiento del Transporte Público Masivo** |
| R003 | 23.1 B | Ministración para Órganos Autónomos y de Gobierno |
| M001 | 15.1 B | Actividades de Apoyo Administrativo |
| K023 | 12.6 B | **Infraestructura Urbana** |
| E187 | 12.2 B | **Servicios Públicos** |
| E172 | 11.7 B | **Atención Médica de Segundo Nivel** |
| J001 | 11.5 B | **Pago de Pensiones y Jubilaciones** |
| E200 | 10.0 B | **Gobierno y seguridad en alcaldías** |
| D001 |  9.1 B | **Servicio de la Deuda** |
| K020 |  7.0 B | **Construcción de Infraestructura Urbana** |
| S227 |  6.9 B | **Mi Beca para Empezar** |
| E066 |  6.7 B | **Servicios de Salud del Primer Nivel** |
| E160 |  5.3 B | **Servicio de Agua Potable** |
| E168 |  5.0 B | **Sistema Penitenciario** |
| U009 |  4.2 B | Otros Subsidios |
| E188 |  3.1 B | **Educación, Cultura, Deporte y Recreación** |
| S061 |  2.5 B | **Vivienda en Conjunto** |
| E093 |  2.2 B | **Manejo Integral de Residuos Sólidos Urbanos** |
| E184 |  2.1 B | **Drenaje, Alcantarillado y Saneamiento** |

Named programs from the PRD's wish-list that DO exist in the data:
Programa Pilares (E116, 736M), Beca Pilares Bienestar (S224, 107M),
Mi Beca para Empezar (S227, 6.87B), Atención Integral Adultos Mayores
(E162+E086 variants), Programa Altépetl (S036, 1.1B), Programa
uniformes y útiles escolares (S210, 1.28B), Comedores para el Bienestar
(S221, 535M), La Escuela Es Nuestra-Mejor Escuela (S225, 352M),
Ponte Pila (E197, 184M), Presupuesto Participativo (R002, 1.97B).

Named programs NOT found under `desc_programa_presupuestario`:
"Cablebús L3", "Utopías", "Sembrando Parques", "RTP renovación de flota",
"SACMEX – Sectorización Iztapalapa". These are specific obras, not
budget programs — they live one level below (partida especifica or
proyecto_inv) and are not citizen-legible from the data. The pitch should
pivot: Cablebús rolls under "Construcción, Ampliación y Mejoramiento de
Infraestructura de Transporte Público" (K022, 1.14B). We can disclose
"Cablebús está incluido aquí" in methodology, not expose it as its own row.

### Level 3 — Specific obras — **NOT ATTEMPTED** (per GO_NO_GO)

The next column below `desc_programa_presupuestario` is `desc_partida_especifica`
(accounting partidas like "Material de oficina", "Servicios de energía
eléctrica"). There is a `desc_proy_inv` column that sometimes carries
project-level names, but spot-checks are inconsistent.

Substitute (per GO_NO_GO):
- **Alcaldía filter** on Level 1 + 2 — viable, see §4
- **Sibling `obra_map.py`** view of `rally_obras.csv` — 23,410 georef'd
  federal projects 2013-2018, fully operational

---

## 4. Alcaldía availability

**Better than expected.** The main egresos CSV already carries alcaldía
identity via `desc_unidad_responsable`. No need to pull in Recursos
Transferidos for the filter.

All 16 alcaldías appear as unidades responsables. 2024 `monto_aprobado`
per alcaldía:

| Alcaldía | MXN | % of its tier |
|---|---|---|
| Iztapalapa | 6,646,602,610 | largest |
| Gustavo A. Madero | 5,420,675,812 | |
| Cuauhtémoc | 3,816,669,577 | |
| Álvaro Obregón | 3,630,859,853 | |
| Coyoacán | 3,216,678,984 | |
| Venustiano Carranza | 3,175,521,699 | |
| Tlalpan | 3,114,028,349 | |
| Miguel Hidalgo | 2,759,466,602 | |
| Benito Juárez | 2,559,288,954 | |
| Xochimilco | 2,404,458,646 | |
| Iztacalco | 2,375,342,474 | |
| Azcapotzalco | 2,259,351,289 | |
| Tláhuac | 2,068,095,210 | |
| Cuajimalpa | 2,042,980,975 | |
| Magdalena Contreras | 1,998,743,675 | |
| Milpa Alta | 1,763,275,815 | smallest |
| **TOTAL 16 alcaldías** | **49,252,040,524** | **18.38 %** of 2024 budget |

The remaining 81.62 % sits under centralized dependencies (SSC, SACMEX,
SOBSE, etc.) and autonomous entities. Alcaldía filter must therefore be
framed in the UI as "spending whose unidad responsable is the alcaldía
itself" — not "all spending in the geographic territory of the alcaldía,"
which is not derivable from this dataset.

Methodology note for `crosswalk/METHODOLOGY.md`: the alcaldía filter is
**own-budget** (gasto propio ejercido por la alcaldía), not
**territorial**. This distinction is important and must be disclosed.

---

## 5. Column schema (confirmed from live data)

All 2024 aprobado + 2023 aprobado + 2023 trimestres + 2022 aprobado + 2022
CP + 2021 CP + 2020 CP share the **same 63-column schema**. This is a
huge win — one loader, one crosswalk, seven years.

Columns (63):
```
clave_presupuestaria, ciclo, periodo,
gobierno_general, desc_gobierno_general,
sector, desc_sector, subsector, desc_subsector,
unidad_responsable, desc_unidad_responsable,
finalidad, desc_finalidad,
funcion, desc_funcion,
subfuncion, desc_subfuncion,
area_funcional, desc_area_funcional,
modalidad, desc_modalidad,
programa_presupuestario, desc_programa_presupuestario,
eje, desc_eje,
objetivo_desarrollo_sostenible, desc_objetivo_desarrollo_sostenible,
tipo_recurso, desc_tipo_recurso,
fuente_financiamiento, desc_fuente_financiamiento,
fuente_generica, desc_fuente_generica,
fuente_especifica, desc_fuente_especifica,
ciclo_original, origen_recurso, desc_origen_recurso,
fondo, desc_fondo,
gasto_programable, desc_gasto_programable,
tipo_gasto, desc_tipo_gasto,
capitulo, desc_capitulo,
concepto, desc_concepto,
partida_generica, desc_partida_generica,
partida_especifica, desc_partida_especifica,
consolidado, desc_consolidado, detalle_consolidado, desc_detalle_consolidado,
proyecto_inv, desc_proy_inv, tipo_proyecto, desc_tipo_proyecto,
monto_aprobado, monto_modificado, monto_ejercido
```

Rally obras CSV keeps its own 73-column schema (see `prd/AUDIT.md` §
"Rally obras CSV schema"). It is a separate universe (federal money,
georeferenced, 2013-2018) and joins to the main egresos only through the
sibling-view narrative, not through any key.

### Known data quirks

- **`egresos_2023_03_trimestre.csv`**: `monto_aprobado` column is String
  (blank values), not Float64. Use `monto_modificado` + `monto_ejercido`
  as the truth columns for Q3 data. Pre-emptive cast to `Float64` is
  already in Agent 1's loader plans.
- **`egresos_2024_aprobado.csv`**: `monto_modificado` and `monto_ejercido`
  are all zero (aprobado-only snapshot, no execution recorded). Expected.
- **Tier 4 treemap files** (`egresos_2024_*.csv` under `data/raw/`):
  columns inside are dated 2022/2023, even though the files live on the
  "Presupuesto 2024" dataset page. CDMX did not refresh them. Use for
  sector/unidad reference structure only.

---

## 6. What is NOT available (transparent gaps)

Gaps that shape the pitch:

- **No 2024 trimestre / monto_ejercido.** As of 2026-04-18,
  datos.cdmx.gob.mx shows only the 2024 aprobado CSV. The Q1-2024
  report (typically published April-May following year) has not
  appeared. The closest real-ejercido analog for a current-ish
  conversation is `egresos_2023_03_trimestre.csv` (Jan-Sep 2023) or
  `egresos_2022_cp.csv` (full-year 2022).
- **No 2024 Cuenta Pública.** Cuenta Pública is normally published
  ~8-12 months after year end; the 2024 CP would be expected around
  mid-to-late 2025 and is not yet on the portal.
- **No 2023 Cuenta Pública.** Present for 2018-2022 only. The 2023
  closed-year audit has not yet been published — consistent with ASCM's
  normal cadence.
- **No 2025 aprobado.** Congress approved 291.5 B MXN in Dec 2024 (per
  press), but no CSV has landed on datos.cdmx.gob.mx yet. The
  `presupuesto-de-egresos` slug still points to the 2024 dataset.
- **No obra-level names/locations inside the egresos CSVs.** See §3
  Level-3 analysis.

These gaps are the reason the GO_NO_GO reshape (Level 3 → alcaldía filter
+ Rally sibling view) is the right call, not a concession.

---

## 7. Narrative sources (addendum, 2026-04-18, +30 min budget)

Purpose: patch the Level-2 gap — Cablebús, Utopías, Sembrando Parques,
SACMEX Sectorización Iztapalapa do **not** appear as
`desc_programa_presupuestario` values. These named obras live only in
narrative PDFs. See `data/raw/narrative_sources/README.md` for the
ledger and `data/raw/narrative_sources/named_programs_2024.csv` for the
structured extract (81 rows).

### PDFs downloaded

| File | Size | Verdict |
|---|---|---|
| `proyecto_egresos_2024_tomo1.pdf` | 11 MB | ⭐ Richest — 50 named programs **with** peso amounts in the Política Social table |
| `decreto_egresos_2024.pdf` | 5.6 MB | ⭐ Unidad-level allocations (Art 5 / Art 6 / Art 7 tables — SACMEX, Metro, STE, Metrobús, RTP, Fideicomiso Bienestar Educativo) |
| `tomoII_D_principales_proyectos_2024.pdf` | 190 KB | Multi-year obras list — names only, **no peso column** in the public PDF |
| `anexo_III_F_programas_proyectos_2024.pdf` | 290 KB | Obras list (incl. UTOPÍAS Iztapalapa, Ampliación L1 Trolebús) — no pesos |
| `anexo_VI_F_programas_proyectos_2024.pdf` | 293 KB | Mirror of III.F |
| `tomoII_E_prioridades_gasto_2024.pdf` | 244 KB | Extract was near-empty — just category headers. Skipped. |

**SOBSE 2024 obras anexo:** not found as a standalone published file
within the 30-min window. SOBSE obras are already covered by Anexo III.F
/ VI.F (above) and by `rally_obras.csv` for 2013-2018 federal money.
Skipped per the 5-min-per-source rule.

### Named-obras coverage

| Target name | Peso amount in 2024? | Pitch-ready? |
|---|---|---|
| Pilares (+ 5 sub-programs) | ✓ MXN 1,028 M Subsistema + 687 M sub-programs | Yes — primary citizen-legible exemplar |
| Mi Beca para Empezar | ✓ MXN 6,820,960,250 | Yes — flagship |
| Altépetl Bienestar | ✓ MXN 1,100,000,000 | Yes |
| Cosecha de Lluvia | ✓ MXN 500 M (200 regular + 300 escuelas) | Yes |
| Ponte Pila | ✓ MXN 187,000,000 | Yes |
| La Escuela Es Nuestra | ✓ MXN 350,000,000 | Yes |
| Beca Leona Vicario | ✓ MXN 241,164,650 | Yes |
| Comedores para el Bienestar | ✓ MXN 474 M (SIBISO + DIF) | Yes |
| Memorial New's Divine | ✓ MXN 1,500,000 | Yes (story row) |
| **Utopías (Iztapalapa)** | ✗ obra name only (no peso) | Narrative callout under Alcaldía Iztapalapa 6.65 B |
| **Cablebús Línea 3** | ✗ obra name only in Tomo I narrative | Callout under STE 1.90 B; web research: MXN ~2.34 B obra total multianual |
| **SACMEX Sectorización Iztapalapa** | ✗ narrative reference only | Callout under Sistema de Aguas 13.27 B |
| **Sembrando Parques** | ✗ NOT in 2024 budget | Document as "concluido 2019-2023, MXN 1,576 M ejercidos acumulados" |

### How this plugs into the crosswalk

- Main crosswalk still uses `desc_programa_presupuestario` (169 values)
  as the Level-2 spine because those values sum to the published
  headline.
- `named_programs_2024.csv` is an **editorial supplement**, not a
  replacement. It provides citizen-friendly `display_name` strings and
  proper pesos for the famous programs that the CSV labels with
  bureaucratic names.
- For obras with no peso (Cablebús L3, Utopías, Sectorización), Agent 3
  treats them as narrative sub-callouts under their parent unidad — not
  as numbered rows. This keeps the editorial cleanliness while letting
  the pitch mention the famous names.

---

## 8. BLOCKERS

None. Greenlit to proceed with Level 1 + 2 crosswalk work and parquet
emission.

---

## 9. Open follow-ups (non-blocking)

- ~~Decide with Agent 2 whether to carve a `data/clean/` exception in
  `.gitignore`~~ — **RESOLVED.** Agent 2 accepted Option 2 in
  `HANDOFFS.md`; `data/clean/**` is now tracked by git.
- Watch for a Q1-2024 trimestre drop during the hackathon — if it
  lands on Saturday, it's the freshest real-ejercido signal for the
  demo.
- Revisit `rally_obras.csv` for any schema drift before hour 3 —
  `obra_map.py` depends on it.
- If time permits, probe SOBSE's SIPOT portal for a 2024 obras-level
  CSV — out of scope for hour-0.

## 10. Coverage audit — what's intentionally NOT downloaded

This section exists so nothing surprises the lead later. Every gap
below is a deliberate skip, not a miss.

### Skipped — forensic narrative only

These surface repeatedly in our memory pointers (see
`dev/forensic-analysis` context) but they serve cross-source coherence
analysis, not the descriptive "Tus 100 pesos" pitch:

- **`proyectos_fed_2022t3.csv`** (the mid-year SRFT schema break file).
  Useful to a forensic investigator who wants to prove a methodology
  change happened. Not useful to a citizen drill-down.
- **SHCP participaciones PDFs 2018-2024** (federal-side paid totals to
  CDMX). Needed only for macro reconciliation (CDMX-side vs SHCP-side).
  Our Ingresos dataset already has the CDMX-side view, which is what
  the footer needs.
- **`reconciliation_federal_transfers.csv`** (derived forensic output).
  Not a raw source.

### Skipped — redundant with what we have

- **2018 + 2019 aprobados + trimestres + CPs** — we have five closed-
  year CPs (2020, 2021, 2022) plus current-year aprobados (2022, 2023,
  2024). Adding 2018-2019 buys a longer trend line but costs ~150 MB.
  Pitch doesn't need it.
- **2020 + 2021 + 2022 aprobados beyond what we grabbed** — we have
  2022 aprobado; 2020 / 2021 aprobado would only matter for an
  aprobado-vs-ejercido gap analysis, which the CPs already cover.
- **2020 / 2021 / 2022 trimestres Q1-Q3** — these are intermediate
  snapshots superseded by each year's Cuenta Pública.
- **Tomo II J / K / N apartados** (Clasificación URG, Anexos
  Transversales) — covered conceptually by Tomo I narrative. The
  named-obra content we needed is in Tomo II A + D and in Anexos III.F
  / VI.F, which we did grab.

### Not available today (portal gaps)

- **2023 Cuenta Pública** — not yet published (ASCM publishes ~12-18 mo
  after year end).
- **2024 Cuenta Pública** — not yet published.
- **2024 trimestres** (Q1-Q4) — none published on datos.cdmx as of the
  hour-0 probe.
- **2025 aprobado CSV** — Congress approved MXN 291.5 B in Dec 2024
  (press), but no CSV on datos.cdmx yet.
- **SOBSE 2024 standalone obras anexo** — not published as a separate
  file. Obra-level data exists inside Anexo III.F / VI.F (grabbed) and
  via SIPOT transparencia queries (out of scope).

If any of the above publishes during the hackathon, Agent 1 grabs it
via a re-run of `scripts/download_data.sh` (new URL appended).
