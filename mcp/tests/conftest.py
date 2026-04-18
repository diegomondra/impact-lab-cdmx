from unittest.mock import MagicMock


def make_ckan_response(records: list[dict], total: int | None = None) -> MagicMock:
    """Construye un mock de respuesta CKAN válida."""
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {
        "success": True,
        "result": {
            "records": records,
            "total": total if total is not None else len(records),
            "fields": [],
        },
    }
    return mock_resp


def make_package_response(resources: list[dict]) -> MagicMock:
    """Construye un mock de respuesta package_show."""
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {
        "success": True,
        "result": {
            "id": "test-pkg",
            "name": "test-slug",
            "resources": resources,
        },
    }
    return mock_resp
