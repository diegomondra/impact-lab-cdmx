"""
Smoke test manual — pega contra el portal real.
Correr con: python examples/smoke_test.py

NO incluir en CI. Solo para validación manual.
"""
import sys

from cdmx_data import CDMX


def main() -> None:
    print("Iniciando smoke test contra datos.cdmx.gob.mx ...")

    cdmx = CDMX(cache_path=":memory:")

    # Test 1: metro_afluencia_simple — resource_id conocido
    print("\n[1/3] metro_afluencia_simple (resource_id hardcoded) ...")
    result = cdmx.ckan.datastore_search(
        "0e8ffe58-28bb-4dde-afcd-e5f5b4de4ccb", limit=5
    )
    records = result.get("records", [])
    assert len(records) > 0, "Sin registros en metro_afluencia_simple"
    print(f"    OK — {len(records)} registros de muestra. Columnas: {list(records[0].keys())}")

    # Test 2: package_search
    print("\n[2/3] package_search 'metro' ...")
    result = cdmx.search("metro", max_results=3)
    assert len(result) > 0, "Sin resultados para 'metro'"
    print(f"    OK — {len(result)} datasets encontrados: {[r['name'] for r in result]}")

    # Test 3: normalize — confirmar que canonical_alcaldia funciona
    print("\n[3/3] Normalización de alcaldías ...")
    from cdmx_data.normalize import canonical_alcaldia
    assert canonical_alcaldia("COYOACÁN") == "Coyoacán"
    assert canonical_alcaldia("cuauhtemoc") == "Cuauhtémoc"
    print("    OK")

    print("\nSmoke test completado exitosamente.")


if __name__ == "__main__":
    main()
