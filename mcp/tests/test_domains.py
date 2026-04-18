from unittest.mock import MagicMock, patch
import pandas as pd
import pytest

from cdmx_data.ckan import CKANClient
from cdmx_data.catalog import CATALOG


def make_cdmx_mock(df: pd.DataFrame) -> MagicMock:
    """Crea un mock de la clase CDMX cuyo _fetch_cached devuelve df."""
    cdmx = MagicMock()
    cdmx._fetch_cached.return_value = df.copy()
    cdmx.ckan = MagicMock(spec=CKANClient)
    return cdmx


class TestMetroAfluencia:
    def test_returns_dataframe(self):
        df = pd.DataFrame({"fecha": ["2024-01-01", "2024-01-02"], "linea": ["1", "2"], "estacion": ["A", "B"], "afluencia": [100, 200]})
        cdmx = make_cdmx_mock(df)
        from cdmx_data.domains.movilidad import Metro
        metro = Metro(cdmx)
        result = metro.afluencia()
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2

    def test_filters_by_linea(self):
        df = pd.DataFrame({"fecha": ["2024-01-01", "2024-01-01"], "linea": ["1", "2"], "estacion": ["A", "B"], "afluencia": [100, 200]})
        cdmx = make_cdmx_mock(df)
        from cdmx_data.domains.movilidad import Metro
        metro = Metro(cdmx)
        result = metro.afluencia(linea="1")
        assert len(result) == 1
        assert result.iloc[0]["linea"] == "1"

    def test_filters_by_desde(self):
        df = pd.DataFrame({"fecha": ["2024-01-01", "2024-06-01"], "linea": ["1", "1"], "estacion": ["A", "A"], "afluencia": [100, 200]})
        cdmx = make_cdmx_mock(df)
        from cdmx_data.domains.movilidad import Metro
        metro = Metro(cdmx)
        result = metro.afluencia(desde="2024-04-01")
        assert len(result) == 1
        assert result.iloc[0]["fecha"] == "2024-06-01"

    def test_uses_known_resource_id_from_catalog(self):
        df = pd.DataFrame({"fecha": [], "linea": [], "estacion": [], "afluencia": []})
        cdmx = make_cdmx_mock(df)
        from cdmx_data.domains.movilidad import Metro
        metro = Metro(cdmx)
        metro.afluencia()
        expected_id = CATALOG["metro_afluencia_simple"].resource_id
        cdmx._fetch_cached.assert_called_once_with(expected_id)

    def test_resolves_unknown_resource_id_via_package_show(self):
        df = pd.DataFrame({"fecha": [], "linea": [], "estacion": [], "afluencia": []})
        cdmx = make_cdmx_mock(df)
        cdmx.ckan.package_show.return_value = {
            "resources": [{"id": "resolved-id", "datastore_active": True}]
        }
        from cdmx_data.domains.movilidad import Metro
        from cdmx_data.catalog import DatasetInfo, CATALOG
        CATALOG["_test_key_domains"] = DatasetInfo(key="_test_key_domains", slug="test-slug", resource_id=None, track="movilidad")
        metro = Metro(cdmx)
        result_id = metro._resource_id("_test_key_domains")
        assert result_id == "resolved-id"
        del CATALOG["_test_key_domains"]


class TestSeguridadCarpetas:
    def test_filters_by_alcaldia(self):
        df = pd.DataFrame({
            "fecha_inicio": ["2024-01-01", "2024-01-02"],
            "alcaldia_catalogo": ["Coyoacán", "CUAUHTÉMOC"],
            "delito": ["robo a transeúnte", "lesiones"],
        })
        cdmx = make_cdmx_mock(df)
        cdmx.ckan.package_show.return_value = {
            "resources": [{"id": "res-1", "datastore_active": True, "name": "2024", "description": ""}]
        }
        from cdmx_data.domains.seguridad import Seguridad
        seg = Seguridad(cdmx)
        result = seg.carpetas_fgj(alcaldia="coyoacan")
        assert len(result) == 1
        assert result.iloc[0]["delito"] == "robo a transeúnte"

    def test_filters_by_delito_contiene(self):
        df = pd.DataFrame({
            "fecha_inicio": ["2024-01-01", "2024-01-02"],
            "alcaldia_catalogo": ["Coyoacán", "Coyoacán"],
            "delito": ["robo a transeúnte", "lesiones dolosas"],
        })
        cdmx = make_cdmx_mock(df)
        cdmx.ckan.package_show.return_value = {
            "resources": [{"id": "res-1", "datastore_active": True, "name": "2024", "description": ""}]
        }
        from cdmx_data.domains.seguridad import Seguridad
        seg = Seguridad(cdmx)
        result = seg.carpetas_fgj(delito_contiene="robo")
        assert len(result) == 1
        assert "robo" in result.iloc[0]["delito"]


class TestAireCalidad:
    def test_returns_dataframe(self):
        df = pd.DataFrame({"estacion": ["MER", "XAL"], "valor": [35.2, 28.1]})
        cdmx = make_cdmx_mock(df)
        cdmx.ckan.package_show.return_value = {
            "resources": [{"id": "pm25-res", "datastore_active": True, "name": "pm25", "description": ""}]
        }
        from cdmx_data.domains.aire import Aire
        aire = Aire(cdmx)
        result = aire.calidad(contaminante="PM25")
        assert isinstance(result, pd.DataFrame)

    def test_filters_by_estacion(self):
        df = pd.DataFrame({"estacion": ["MER", "XAL"], "valor": [35.2, 28.1]})
        cdmx = make_cdmx_mock(df)
        cdmx.ckan.package_show.return_value = {
            "resources": [{"id": "pm25-res", "datastore_active": True, "name": "pm25", "description": ""}]
        }
        from cdmx_data.domains.aire import Aire
        aire = Aire(cdmx)
        result = aire.calidad(contaminante="PM25", estacion="MER")
        assert len(result) == 1
        assert result.iloc[0]["estacion"] == "MER"


class TestServiciosLocatel:
    def test_filters_by_alcaldia(self):
        df = pd.DataFrame({
            "fecha": ["2024-01-01", "2024-01-02"],
            "alcaldia": ["Coyoacán", "Tlalpan"],
            "tipo": ["consulta", "queja"],
        })
        cdmx = make_cdmx_mock(df)
        cdmx.ckan.package_show.return_value = {
            "resources": [{"id": "loc-res", "datastore_active": True}]
        }
        from cdmx_data.domains.servicios import Servicios
        svc = Servicios(cdmx)
        result = svc.locatel(alcaldia="Coyoacán")
        assert len(result) == 1


class TestFinanzasProveedores:
    def test_filters_by_nombre(self):
        df = pd.DataFrame({
            "nombre": ["Empresa ABC", "Constructora XYZ", "Servicios ABC"],
        })
        cdmx = make_cdmx_mock(df)
        cdmx.ckan.package_show.return_value = {
            "resources": [{"id": "prov-res", "datastore_active": True}]
        }
        from cdmx_data.domains.finanzas import Finanzas
        fin = Finanzas(cdmx)
        result = fin.proveedores(nombre_contiene="ABC")
        assert len(result) == 2
