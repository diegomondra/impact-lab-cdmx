#!/usr/bin/env bash
# Download CDMX public budget datasets.
#
# Layout:
#   data/            — kept where the existing frozen notebooks expect them
#     egresos_2024_aprobado.csv, egresos_2023_aprobado.csv,
#     egresos_2023_03_trimestre.csv, rally_obras.csv
#   data/raw/        — additional datasets discovered by Agent 1 (Ingresos,
#                       Cuenta Pública, pre-aggregated treemaps, diccionarios,
#                       recursos transferidos, older aprobados + trimestres)
#   data/raw/dictionaries/ — XLSX schema dictionaries
#
# Source portals:
#   https://datos.cdmx.gob.mx      (CKAN open-data portal)
#   https://tudinero.cdmx.gob.mx   (gov-maintained visualization portal)
#
# All URLs last verified: 2026-04-18 (fresh today).
# No 2025 aprobado, no 2024 trimestre, no 2023/2024 Cuenta Pública on
# datos.cdmx.gob.mx as of the hour-0 probe.

set -euo pipefail

cd "$(dirname "$0")/.."
mkdir -p data data/raw data/raw/dictionaries

# --- Helper -------------------------------------------------------------
dl() {
  # dl <dest_path> <url>
  local dest="$1" url="$2"
  if [[ -f "$dest" ]]; then
    echo "  skip  $dest (exists)"
    return 0
  fi
  echo "  get   $dest"
  curl -fsSL -o "$dest" "$url"
}

# ======================================================================
# Tier 1 — consumed directly by existing notebooks (keep under data/)
# ======================================================================

echo "[Tier 1] current budget CSVs consumed by notebooks/*"

dl data/egresos_2024_aprobado.csv \
  "https://datos.cdmx.gob.mx/dataset/3a6cba97-adb1-4f35-9df1-984cc3657aca/resource/7fa1da81-531c-477c-93db-7580bc1c7ad0/download/egresos_2024_aprobado.csv"

dl data/egresos_2023_aprobado.csv \
  "https://datos.cdmx.gob.mx/dataset/ea119a03-4f5a-46fa-afbe-bc32bcf79ec3/resource/5137e3db-227e-462d-8d59-1942afbc0c6a/download/egresos_2023_aprobado.csv"

dl data/egresos_2023_03_trimestre.csv \
  "https://datos.cdmx.gob.mx/dataset/ea119a03-4f5a-46fa-afbe-bc32bcf79ec3/resource/7c50218d-adc3-4c71-98ca-ea28747b49d6/download/egresos_2023_03_trimestre.csv"

dl data/rally_obras.csv \
  "https://datos.cdmx.gob.mx/dataset/c48edfeb-cde2-4030-a127-cd4c9ac2b546/resource/738424f5-20a2-4f3a-8e12-ae9d63c6ba02/download/rally-como-van-las-obras-cdmx.csv"

# ======================================================================
# Tier 2 — additional CDMX budget CSVs under data/raw/
# ======================================================================

echo "[Tier 2a] most recent full-year Cuenta Pública (real monto_ejercido)"
dl data/raw/egresos_2022_cp.csv \
  "https://datos.cdmx.gob.mx/dataset/755f47f1-b937-4131-8a7b-fbe306e747c8/resource/771247b8-3cb2-4664-ae21-d3f03aff9b2a/download/egresos_2022_cp.csv"

dl data/raw/egresos_2022_aprobado.csv \
  "https://datos.cdmx.gob.mx/dataset/755f47f1-b937-4131-8a7b-fbe306e747c8/resource/fc93c940-ad75-4e7f-afe6-c624726623a9/download/egresos_2022_aprobado.csv"

echo "[Tier 2b] complete 2023 trimestre set (Q1 + Q2 already alongside Q3)"
dl data/raw/egresos_2023_01_trimestre.csv \
  "https://datos.cdmx.gob.mx/dataset/ea119a03-4f5a-46fa-afbe-bc32bcf79ec3/resource/e707c147-e8f9-446c-94d3-81fec3a8d979/download/egresos_2023_01_trimestre.csv"

dl data/raw/egresos_2023_02_trimestre.csv \
  "https://datos.cdmx.gob.mx/dataset/ea119a03-4f5a-46fa-afbe-bc32bcf79ec3/resource/f6171417-e686-4639-8e06-27790665b9f2/download/egresos_2023_02_trimestre.csv"

echo "[Tier 2c] earlier Cuenta Pública (for long-horizon trend)"
dl data/raw/egresos_2021_cp.csv \
  "https://datos.cdmx.gob.mx/dataset/246be014-62ba-46e0-a7ce-9f37c8f01886/resource/f7c764eb-8eac-42b3-96ec-7f84f646f228/download/egresos_2021_cp.csv"

dl data/raw/egresos_2020_cp.csv \
  "https://datos.cdmx.gob.mx/dataset/2bb4de63-8212-4d2a-a377-98b10f8384c6/resource/8581fb25-3ab4-4022-bc4f-423eda5b4013/download/egresos_2020_cp.csv"

# ======================================================================
# Tier 3 — Ingresos (where the money comes from)
# ======================================================================

echo "[Tier 3] Ingresos 2018-2024"
dl data/raw/ingresos_2018_2024.csv \
  "https://datos.cdmx.gob.mx/dataset/f04b7092-782d-4206-9590-ac8b577891dc/resource/77c2e268-f5b4-4cdf-a705-13a73a9608b3/download/ingresos_2024_01.csv"

# Pre-aggregated citizen-facing view — "¿De dónde viene el presupuesto?"
dl data/raw/ingresos_fuentes.csv \
  "https://datos.cdmx.gob.mx/dataset/f04b7092-782d-4206-9590-ac8b577891dc/resource/17b86228-055d-4d70-9565-9de41cf073ef/download/tabla1_fuentes_ingreso.csv"

dl data/raw/ingresos_treemap.csv \
  "https://datos.cdmx.gob.mx/dataset/f04b7092-782d-4206-9590-ac8b577891dc/resource/6c42b597-40be-406d-8bed-953b3d74395b/download/treemap_ingresos.csv"

# ======================================================================
# Tier 4 — CDMX's own citizen-facing pre-aggregations (treemaps used on
# tudinero.cdmx.gob.mx). These inform the editorial crosswalk.
# ======================================================================

echo "[Tier 4] tudinero treemap + '¿a dónde va?' aggregates for 2024"
dl data/raw/egresos_2024_a_donde_va.csv \
  "https://datos.cdmx.gob.mx/dataset/3a6cba97-adb1-4f35-9df1-984cc3657aca/resource/8aa3e0aa-4962-47b7-b77f-4abee7d46931/download/tabla1_a_donde_va.csv"

dl data/raw/egresos_2024_treemap_unidad.csv \
  "https://datos.cdmx.gob.mx/dataset/3a6cba97-adb1-4f35-9df1-984cc3657aca/resource/164a56f9-de2b-4cfa-8d26-436e62249a05/download/treemap1_a_donde_va.csv"

dl data/raw/egresos_2024_treemap_capitulo.csv \
  "https://datos.cdmx.gob.mx/dataset/3a6cba97-adb1-4f35-9df1-984cc3657aca/resource/093b4f35-e0d6-4b95-b84a-f5e5b99c3f88/download/treemap2_a_donde_va.csv"

dl data/raw/egresos_2024_como_cambia.csv \
  "https://datos.cdmx.gob.mx/dataset/3a6cba97-adb1-4f35-9df1-984cc3657aca/resource/61b6c48b-f9d6-41cd-ae6b-ab591bc9d195/download/grafica1_como_cambia_v2.csv"

# ======================================================================
# Tier 5 — Recursos Transferidos a Alcaldías
# (stale: latest resource dated 2022/2023, XLSX only — keep for reference)
# ======================================================================

echo "[Tier 5] Recursos Transferidos a Alcaldías (reference, XLSX)"
dl data/raw/recursos_transferidos_alcaldias.xlsx \
  "https://datos.cdmx.gob.mx/dataset/3ab834ad-89ab-477b-8698-a71987ea4c39/resource/3516a236-cc06-4c2f-8752-2ef9343dd2e0/download/recursos_transferidos_alcaldias_202200.xlsx"

# ======================================================================
# Tier 5b — Proyectos Financiados con Recursos Federales Transferidos
# Superset of rally_obras.csv. Same SRFT universe (federal $$ in CDMX)
# but extended from 2013-2018 (rally) to 2013-2022 (this file).
# Adds ~60k new georef'd projects across 2019-2022 (Ramo 23 / Ramo 9 /
# Ramo 12, FORTAMUN, FAIS, etc.). Feeds the `obra_map.py` sibling view.
# ======================================================================

echo "[Tier 5b] Federal-transferidos superset 2013-2022 + dictionary"
dl data/raw/proyectos_federales_transferidos_2013_2022t1.csv \
  "https://datos.cdmx.gob.mx/dataset/fef171a3-3f29-4b99-9f42-1e3ff9e46b05/resource/fdc16ff5-be42-47d0-b717-c8e81fed1a32/download/proyectos_financiados_recursos_federales_2022t1.csv"

dl data/raw/dictionaries/diccionario_recursos_federales.xlsx \
  "https://datos.cdmx.gob.mx/dataset/fef171a3-3f29-4b99-9f42-1e3ff9e46b05/resource/8e843d08-835e-460b-be7e-b23123fcdc9b/download/diccionario_recursos_federales.xlsx"

dl data/raw/dictionaries/nota_aclaratoria_transferencias_federales.pdf \
  "https://datos.cdmx.gob.mx/dataset/fef171a3-3f29-4b99-9f42-1e3ff9e46b05/resource/197ba698-7404-41fe-bd09-1c084c47f610/download/nota-aclaratoria-transferencias-federales.pdf"

# ======================================================================
# Tier 5c — Entes Públicos CDMX catalog (unidad-responsable taxonomy)
# ======================================================================

echo "[Tier 5c] Entes Públicos CDMX 2024 (catalog)"
dl data/raw/entes_publicos_cdmx_2024.xlsx \
  "https://datos.cdmx.gob.mx/dataset/b31708a9-0936-4e26-b24b-4531d99b4d65/resource/5724acc4-64aa-42ee-9646-19d6f80b466d/download/entes-publicos-gobcdmx-2024.xlsx"

# ======================================================================
# Tier 6 — Data dictionaries (XLSX)
# ======================================================================

echo "[Tier 6] Data dictionaries"
dl data/raw/dictionaries/diccionario_presupuesto_egresos.xlsx \
  "https://datos.cdmx.gob.mx/dataset/3a6cba97-adb1-4f35-9df1-984cc3657aca/resource/ec240fe9-41e0-4db0-8413-cd5c698cec33/download/diccionario_presupuesto_egresos.xlsx"

dl data/raw/dictionaries/diccionario_ingresos.xlsx \
  "https://datos.cdmx.gob.mx/dataset/f04b7092-782d-4206-9590-ac8b577891dc/resource/a6d3270a-ad7e-49e1-82fd-ddd8aaae03b2/download/diccionario_ingresos.xlsx"

dl data/raw/dictionaries/diccionario_recursosalasalcaldias.xlsx \
  "https://datos.cdmx.gob.mx/dataset/3ab834ad-89ab-477b-8698-a71987ea4c39/resource/e82636f8-1da8-44cf-973b-1e86c8fff4f5/download/diccionario_recursosalasalcaldias.xlsx"

# ======================================================================
# Tier 7 — Narrative sources for named-obra coverage
# These PDFs inform the editorial crosswalk (Cablebús, Utopías, Pilares,
# Mi Beca, Altépetl, etc.) that are NOT exposed at the row level of the
# main CSV. Extracted tabular data lives in data/raw/narrative_sources/
# named_programs_2024.csv (hand-curated by Agent 1).
# ======================================================================

mkdir -p data/raw/narrative_sources

echo "[Tier 7] Paquete Económico 2024 narrative PDFs"

dl data/raw/narrative_sources/proyecto_egresos_2024_tomo1.pdf \
  "https://cdmxassets.s3.amazonaws.com/media/files-pdf/paquete_economico_2024/TOMO_I/PROYECTO_PRESUPUESTO_EGRESOS_2024_TOMO_I.pdf"

dl data/raw/narrative_sources/decreto_egresos_2024.pdf \
  "https://www.poderjudicialcdmx.gob.mx/transparencia_cj/PDF/121/01/Leyes/DecPresEgre_2024.pdf"

dl data/raw/narrative_sources/tomoII_A_analisis_programatico_2024.pdf \
  "https://cdmxassets.s3.amazonaws.com/media/files-pdf/paquete_economico_2024/TOMO_II/A_ANALISIS_PRO.pdf"

dl data/raw/narrative_sources/tomoII_D_principales_proyectos_2024.pdf \
  "https://cdmxassets.s3.amazonaws.com/media/files-pdf/paquete_economico_2024/TOMO_II/D_PRINCIPALES_PROYECTOS.pdf"

dl data/raw/narrative_sources/tomoII_E_prioridades_gasto_2024.pdf \
  "https://cdmxassets.s3.amazonaws.com/media/files-pdf/paquete_economico_2024/TOMO_II/E_PRIORIDADESGASTO.pdf"

dl data/raw/narrative_sources/anexo_III_F_programas_proyectos_2024.pdf \
  "https://cdmxassets.s3.amazonaws.com/media/files-pdf/paquete_economico_2024/ANEXO_III/III.F_PROGRAMAS_PROYECTOS.pdf"

dl data/raw/narrative_sources/anexo_VI_F_programas_proyectos_2024.pdf \
  "https://cdmxassets.s3.amazonaws.com/media/files-pdf/paquete_economico_2024/ANEXO_VI/VI.F_PROGRAMAS_PROYECTOS.pdf"

# ----------------------------------------------------------------------
echo ""
echo "Done. Summary:"
echo ""
echo "data/*.csv (Tier 1, consumed by notebooks):"
ls -lh data/*.csv 2>/dev/null || true
echo ""
echo "data/raw/ (Tiers 2-5):"
ls -lh data/raw/*.csv data/raw/*.xlsx 2>/dev/null || true
echo ""
echo "data/raw/dictionaries/:"
ls -lh data/raw/dictionaries/*.xlsx 2>/dev/null || true
