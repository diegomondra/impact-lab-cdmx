import json
from unittest.mock import patch, MagicMock
import pytest
import httpx

from cdmx_data.ckan import CKANClient, CKANError
from tests.conftest import make_ckan_response, make_package_response

BASE = "https://datos.cdmx.gob.mx/api/3/action/"


class TestDatastoreSearch:
    def test_builds_correct_url(self):
        mock_resp = make_ckan_response([{"id": 1}])
        with patch.object(httpx.Client, "get", return_value=mock_resp) as mock_get:
            client = CKANClient()
            result = client.datastore_search("abc-123", limit=50, offset=0)
            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args
            assert "datastore_search" in call_kwargs.args[0]
            assert result["records"] == [{"id": 1}]

    def test_passes_filters_as_json(self):
        mock_resp = make_ckan_response([])
        with patch.object(httpx.Client, "get", return_value=mock_resp) as mock_get:
            client = CKANClient()
            client.datastore_search("abc-123", filters={"alcaldia": "Coyoacán"})
            call_kwargs = mock_get.call_args
            params = call_kwargs.kwargs.get("params", {})
            assert "filters" in params
            assert json.loads(params["filters"]) == {"alcaldia": "Coyoacán"}

    def test_raises_ckan_error_on_failure(self):
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {
            "success": False,
            "error": {"message": "Recurso no encontrado"},
        }
        with patch.object(httpx.Client, "get", return_value=mock_resp):
            client = CKANClient()
            with pytest.raises(CKANError, match="Recurso no encontrado"):
                client.datastore_search("bad-id")


class TestPackageSearch:
    def test_returns_results(self):
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {
            "success": True,
            "result": {"results": [{"name": "metro"}], "count": 1},
        }
        with patch.object(httpx.Client, "get", return_value=mock_resp):
            client = CKANClient()
            result = client.package_search("metro", rows=5)
            assert result["results"][0]["name"] == "metro"


class TestPackageShow:
    def test_returns_resources(self):
        mock_resp = make_package_response([{"id": "res-1", "datastore_active": True}])
        with patch.object(httpx.Client, "get", return_value=mock_resp):
            client = CKANClient()
            result = client.package_show("test-slug")
            assert result["resources"][0]["id"] == "res-1"


class TestIterRecords:
    def test_paginates_until_empty(self):
        page1 = make_ckan_response([{"n": i} for i in range(3)], total=6)
        page2 = make_ckan_response([{"n": i} for i in range(3, 6)], total=6)
        page3 = make_ckan_response([], total=6)

        call_count = 0

        def side_effect(url, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return page1
            if call_count == 2:
                return page2
            return page3

        with patch.object(httpx.Client, "get", side_effect=side_effect):
            client = CKANClient()
            records = list(client.iter_records("abc-123", page_size=3))
            assert len(records) == 6

    def test_stops_when_page_smaller_than_page_size(self):
        mock_resp = make_ckan_response([{"n": 1}, {"n": 2}])
        with patch.object(httpx.Client, "get", return_value=mock_resp):
            client = CKANClient()
            records = list(client.iter_records("abc-123", page_size=100))
            assert len(records) == 2


class TestDatastoreSearchSQL:
    def test_passes_sql_param(self):
        mock_resp = make_ckan_response([{"count": 42}])
        with patch.object(httpx.Client, "get", return_value=mock_resp) as mock_get:
            client = CKANClient()
            sql = 'SELECT COUNT(*) FROM "abc-123"'
            result = client.datastore_search_sql(sql)
            call_kwargs = mock_get.call_args
            params = call_kwargs.kwargs.get("params", {})
            assert params.get("sql") == sql
            assert result["records"] == [{"count": 42}]
