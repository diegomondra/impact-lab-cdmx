#!/usr/bin/env bash
# Download CDMX public budget datasets into data/
# Source: https://datos.cdmx.gob.mx

set -euo pipefail

cd "$(dirname "$0")/.."
mkdir -p data
cd data

echo "Downloading 2018 approved budget..."
curl -sSL -o egresos_2018_aprobado.csv \
  "https://datos.cdmx.gob.mx/dataset/7a8820f2-3bea-4c69-8b20-1d01b1a99a6a/resource/5b20655c-072f-4347-baee-ab93d930b27b/download/egresos_2018_aprobado.csv"

echo "Downloading 2018 public account (actual spending)..."
curl -sSL -o egresos_2018_cp.csv \
  "https://datos.cdmx.gob.mx/dataset/7a8820f2-3bea-4c69-8b20-1d01b1a99a6a/resource/1ea90350-d41d-48ae-b848-613490d6e16c/download/egresos_2018_cp.csv"

echo "Downloading 2019 approved budget..."
curl -sSL -o egresos_2019_aprobado.csv \
  "https://datos.cdmx.gob.mx/dataset/8dc52617-63f6-4bfd-9fae-54239675c6d0/resource/9a6f53d7-1751-4ae4-8bd8-d31807be7789/download/egresos_2019_aprobado.csv"

echo "Downloading 2019 Q1 actual spending..."
curl -sSL -o egresos_2019_01_trimestre.csv \
  "https://datos.cdmx.gob.mx/dataset/8dc52617-63f6-4bfd-9fae-54239675c6d0/resource/7212363b-c655-4ff6-9207-3cac5a2d8236/download/egresos_2019_01_trimestre.csv"

echo "Downloading 2019 Q2 actual spending..."
curl -sSL -o egresos_2019_02_trimestre.csv \
  "https://datos.cdmx.gob.mx/dataset/8dc52617-63f6-4bfd-9fae-54239675c6d0/resource/58dbd930-63b8-497c-9770-76e2ebf38bc3/download/egresos_2019_02_trimestre.csv"

echo "Downloading 2019 Q3 actual spending..."
curl -sSL -o egresos_2019_03_trimestre.csv \
  "https://datos.cdmx.gob.mx/dataset/8dc52617-63f6-4bfd-9fae-54239675c6d0/resource/53ab63bd-728a-4ebe-8c92-d64f66514e27/download/egresos_2019_03_trimestre.csv"

echo "Downloading 2024 approved budget..."
curl -sSL -o egresos_2024_aprobado.csv \
  "https://datos.cdmx.gob.mx/dataset/3a6cba97-adb1-4f35-9df1-984cc3657aca/resource/7fa1da81-531c-477c-93db-7580bc1c7ad0/download/egresos_2024_aprobado.csv"

echo "Downloading 2023 approved budget..."
curl -sSL -o egresos_2023_aprobado.csv \
  "https://datos.cdmx.gob.mx/dataset/ea119a03-4f5a-46fa-afbe-bc32bcf79ec3/resource/5137e3db-227e-462d-8d59-1942afbc0c6a/download/egresos_2023_aprobado.csv"

echo "Downloading 2023 Q3 actual spending..."
curl -sSL -o egresos_2023_03_trimestre.csv \
  "https://datos.cdmx.gob.mx/dataset/ea119a03-4f5a-46fa-afbe-bc32bcf79ec3/resource/7c50218d-adc3-4c71-98ca-ea28747b49d6/download/egresos_2023_03_trimestre.csv"

echo "Downloading Rally ¿Cómo van las obras? (georeferenced federal projects 2013-2018)..."
curl -sSL -o rally_obras.csv \
  "https://datos.cdmx.gob.mx/dataset/c48edfeb-cde2-4030-a127-cd4c9ac2b546/resource/738424f5-20a2-4f3a-8e12-ae9d63c6ba02/download/rally-como-van-las-obras-cdmx.csv"

echo "Done. Files:"
ls -lh egresos_*.csv rally_obras.csv
