# Citizen categories — Tus 100 pesos

**Agent 1 · 2026-04-18**

This is the canonical Level-1 taxonomy used everywhere in the app. The
ordering below is the display order on the hero grid (also enforced in
`data/clean/SCHEMAS.md`).

Each category is a **citizen experience**, not a bureaucratic classification.
The rule: if a resident of CDMX can point at it (el agua que sale de la
llave, el camión que pasa, la luminaria que prende, la cuadra que se
repavimenta), it goes here. If they can't, it rolls up into "Gobierno y
administración" or "Otros."

## `source_id` convention

- Level-1 rows: `L1-<slug>` where slug is the kebab-case ASCII of the
  category (e.g. `L1-agua`, `L1-transporte`, `L1-apoyos-sociales`).
- Level-2 rows: `L2-<programa_code>` where the code is the lower-cased
  `programa_presupuestario` value from the source CSV (e.g. `L2-e169`
  for "Prevención del Delito y Seguridad Ciudadana"). This preserves
  direct traceability back to `data/egresos_<year>_aprobado.csv`.

## The 16 categories

| # | `citizen_category` | icon | Descripción ciudadana (ES) |
|---|---|---|---|
| 1 | Agua | 💧 | El agua que llega a tu llave, el drenaje que se lleva la lluvia, la planta que la potabiliza. SACMEX y sus obras. |
| 2 | Transporte público | 🚇 | El Metro, el Metrobús, el Cablebús, el trolebús, el tren ligero y la RTP. El dinero que mueve a la ciudad. |
| 3 | Calles y banquetas | 🛣️ | El pavimento, el bacheo, las banquetas, las señales viales y el mantenimiento del Circuito Interior. |
| 4 | Basura y limpia | 🗑️ | Recolección, transferencia, separación y tratamiento de residuos sólidos. |
| 5 | Parques y espacios públicos | 🌳 | Parques, plazas, arbolado urbano, rehabilitación de espacios comunitarios. |
| 6 | Seguridad | 🛡️ | Policía preventiva, C5, bomberos y gestión de riesgos. |
| 7 | Justicia | ⚖️ | Fiscalía, defensoría, sistema penitenciario y búsqueda de personas. |
| 8 | Salud | 🏥 | Hospitales, centros de salud, medicamentos y prevención. |
| 9 | Educación | 📚 | Escuelas públicas, becas, infraestructura educativa, ciencia y tecnología. |
| 10 | Apoyos sociales | 🤝 | Transferencias directas: Mi Beca, Pensión adultos mayores, Pilares, Comedores, vivienda social. |
| 11 | Cultura y deporte | 🎭 | Fomento cultural, museos, festivales, deporte comunitario (Ponte Pila), promoción cultural. |
| 12 | Medio ambiente | 🌱 | Suelo de conservación, bosques, calidad del aire, Altépetl, Cosecha de Lluvia. |
| 13 | Alumbrado | 💡 | Luminarias, ampliación y mantenimiento del alumbrado público. |
| 14 | Gobierno y administración | 🏛️ | Recaudación, planeación, funciones administrativas internas, pensiones a trabajadores, órganos autónomos. |
| 15 | Deuda | 💳 | Pago de intereses y amortización de la deuda pública. |
| 16 | Otros | ▫️ | Rubros no clasificables (turismo, materias primas, apoyos económicos menores). Se declara en la metodología. |

## Mapping strategy (how each CSV row finds its bucket)

Precedence, highest first:

1. **Explicit program-code mapping** — the top ~60 `programa_presupuestario`
   codes are mapped by hand based on editorial judgment. Covers >95 % of
   the budget.
2. **Keyword match on `desc_programa_presupuestario`** — e.g. "Agua" /
   "Drenaje" → Agua; "Alumbrado" → Alumbrado. Catches long-tail programs.
3. **Fallback on `desc_funcion`** — the COFOG-style functional
   classification ("Transporte", "Salud", etc.). Guarantees every row
   lands somewhere.
4. **If still unmapped** → Otros, with a rationale recording the fallback.

All three tiers and their assignments live in
`data/scripts/build_crosswalk_and_parquets.py` — not in a spreadsheet,
so the choices are reviewable and diffable.

## Known controversial mappings (disclose in METHODOLOGY.md)

- **Pensiones y Jubilaciones (J001, E195)** → Gobierno y administración,
  not Apoyos sociales. These are pensions to ex-employees of the
  gobierno de la ciudad, not social transfers to citizens.
- **"Ministración para Órganos Autónomos y de Gobierno" (R003, 23 B)**
  → Gobierno y administración. Covers Congreso, Tribunal, IECM,
  InfoCDMX, etc. — autonomous bodies, not citizen-facing services.
- **"Gobierno y seguridad en alcaldías" (E200, 10 B)** → Gobierno y
  administración. This is alcaldías' own-government overhead. A future
  version could split out the "seguridad" share into Seguridad.
- **"Infraestructura Urbana" (K023, 12.6 B)** → Calles y banquetas.
  Broadest programmatic bucket for SOBSE physical works; label covers
  vialidades + banquetas + alumbrado + parques mixing. Kept whole to
  avoid false precision.
- **"Servicios Públicos" (E187, 12.2 B)** → Calles y banquetas. Similar
  catch-all; dominant content is urban maintenance.
- **Vivienda programs (S061, S027, S047, S053, INVI)** → Apoyos
  sociales. The SCHEMAS list has no Vivienda bucket; these fit
  citizens' experience of housing support better than a standalone
  category given the size of each.
