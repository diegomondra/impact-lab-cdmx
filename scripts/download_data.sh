#!/usr/bin/env bash
# Download CDMX public budget datasets into data/
# Source: https://datos.cdmx.gob.mx

set -euo pipefail

cd "$(dirname "$0")/.."
mkdir -p data
cd data

echo "═══ Ingresos CDMX (2018–2024) ═══"
curl -sSL -o ingresos_main.csv \
  "https://datos.cdmx.gob.mx/dataset/f04b7092-782d-4206-9590-ac8b577891dc/resource/77c2e268-f5b4-4cdf-a705-13a73a9608b3/download/ingresos_2024_01.csv"

echo "═══ Egresos: Cuenta Pública 2018–2022 (final closed-books) ═══"
curl -sSL -o egresos_2018_cp.csv \
  "https://datos.cdmx.gob.mx/dataset/7a8820f2-3bea-4c69-8b20-1d01b1a99a6a/resource/1ea90350-d41d-48ae-b848-613490d6e16c/download/egresos_2018_cp.csv"
curl -sSL -o egresos_2019_cp.csv \
  "https://datos.cdmx.gob.mx/dataset/8dc52617-63f6-4bfd-9fae-54239675c6d0/resource/e4f62593-a5e3-447b-a3ff-0a3203f7b5db/download/egresos_2019_cp.csv"
curl -sSL -o egresos_2020_cp.csv \
  "https://datos.cdmx.gob.mx/dataset/2bb4de63-8212-4d2a-a377-98b10f8384c6/resource/8581fb25-3ab4-4022-bc4f-423eda5b4013/download/egresos_2020_cp.csv"
curl -sSL -o egresos_2021_cp.csv \
  "https://datos.cdmx.gob.mx/dataset/246be014-62ba-46e0-a7ce-9f37c8f01886/resource/f7c764eb-8eac-42b3-96ec-7f84f646f228/download/egresos_2021_cp.csv"
curl -sSL -o egresos_2022_cp.csv \
  "https://datos.cdmx.gob.mx/dataset/755f47f1-b937-4131-8a7b-fbe306e747c8/resource/771247b8-3cb2-4664-ae21-d3f03aff9b2a/download/egresos_2022_cp.csv"

echo "═══ Egresos 2023 (Q3 trimestral — latest with ejercido) ═══"
curl -sSL -o egresos_2023_03_trimestre.csv \
  "https://datos.cdmx.gob.mx/dataset/ea119a03-4f5a-46fa-afbe-bc32bcf79ec3/resource/7c50218d-adc3-4c71-98ca-ea28747b49d6/download/egresos_2023_03_trimestre.csv"
curl -sSL -o egresos_2023_aprobado.csv \
  "https://datos.cdmx.gob.mx/dataset/ea119a03-4f5a-46fa-afbe-bc32bcf79ec3/resource/5137e3db-227e-462d-8d59-1942afbc0c6a/download/egresos_2023_aprobado.csv"

echo "═══ Egresos 2024 (aprobado — año en curso) ═══"
curl -sSL -o egresos_2024_aprobado.csv \
  "https://datos.cdmx.gob.mx/dataset/3a6cba97-adb1-4f35-9df1-984cc3657aca/resource/7fa1da81-531c-477c-93db-7580bc1c7ad0/download/egresos_2024_aprobado.csv"

echo "═══ Rally ¿Cómo van las obras? (proyectos federales 2013–2018 georreferenciados) ═══"
curl -sSL -o rally_obras.csv \
  "https://datos.cdmx.gob.mx/dataset/c48edfeb-cde2-4030-a127-cd4c9ac2b546/resource/738424f5-20a2-4f3a-8e12-ae9d63c6ba02/download/rally-como-van-las-obras-cdmx.csv"

echo ""
echo "Listo. Archivos descargados:"
ls -lh ingresos_*.csv egresos_*.csv rally_obras.csv
