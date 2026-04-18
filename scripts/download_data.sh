#!/usr/bin/env bash
# Download CDMX public budget datasets into data/
# Source: https://datos.cdmx.gob.mx

set -euo pipefail

cd "$(dirname "$0")/.."
mkdir -p data
cd data

echo "Downloading 2024 approved budget..."
curl -sSL -o egresos_2024_aprobado.csv \
  "https://datos.cdmx.gob.mx/dataset/3a6cba97-adb1-4f35-9df1-984cc3657aca/resource/7fa1da81-531c-477c-93db-7580bc1c7ad0/download/egresos_2024_aprobado.csv"

echo "Downloading 2023 approved budget..."
curl -sSL -o egresos_2023_aprobado.csv \
  "https://datos.cdmx.gob.mx/dataset/ea119a03-4f5a-46fa-afbe-bc32bcf79ec3/resource/5137e3db-227e-462d-8d59-1942afbc0c6a/download/egresos_2023_aprobado.csv"

echo "Downloading 2023 Q3 actual spending..."
curl -sSL -o egresos_2023_03_trimestre.csv \
  "https://datos.cdmx.gob.mx/dataset/ea119a03-4f5a-46fa-afbe-bc32bcf79ec3/resource/7c50218d-adc3-4c71-98ca-ea28747b49d6/download/egresos_2023_03_trimestre.csv"

echo "Done. Files:"
ls -lh egresos_*.csv
