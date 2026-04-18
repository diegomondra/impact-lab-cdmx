import time
import pytest
import pandas as pd
from cdmx_data.cache import Cache


@pytest.fixture
def cache():
    c = Cache(db_path=":memory:", ttl_hours=1)
    yield c
    c.close()


@pytest.fixture
def sample_df():
    return pd.DataFrame({"id": [1, 2, 3], "valor": ["a", "b", "c"]})


class TestIsFrequency:
    def test_new_resource_not_fresh(self, cache):
        assert cache.is_fresh("abc-123") is False

    def test_fresh_after_put(self, cache, sample_df):
        cache.put("abc-123", sample_df)
        assert cache.is_fresh("abc-123") is True

    def test_stale_after_ttl(self, sample_df):
        # TTL de 0 horas = siempre stale
        c = Cache(db_path=":memory:", ttl_hours=0)
        c.put("abc-123", sample_df)
        assert c.is_fresh("abc-123") is False
        c.close()


class TestPutGet:
    def test_get_returns_dataframe(self, cache, sample_df):
        cache.put("abc-123", sample_df)
        result = cache.get("abc-123")
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3

    def test_get_preserves_columns(self, cache, sample_df):
        cache.put("abc-123", sample_df)
        result = cache.get("abc-123")
        assert list(result.columns) == ["id", "valor"]

    def test_get_missing_returns_none(self, cache):
        assert cache.get("00000000-0000-0000-0000-000000000000") is None

    def test_put_replaces_existing(self, cache):
        df1 = pd.DataFrame({"x": [1, 2]})
        df2 = pd.DataFrame({"x": [10, 20, 30]})
        cache.put("abc-123", df1)
        cache.put("abc-123", df2)
        result = cache.get("abc-123")
        assert len(result) == 3


class TestInvalidate:
    def test_invalidate_removes_data(self, cache, sample_df):
        cache.put("abc-123", sample_df)
        cache.invalidate("abc-123")
        assert cache.get("abc-123") is None
        assert cache.is_fresh("abc-123") is False

    def test_invalidate_nonexistent_ok(self, cache):
        cache.invalidate("00000000-0000-0000-0000-000000000000")  # no debe lanzar


class TestListAndClear:
    def test_list_returns_entries(self, cache, sample_df):
        cache.put("abc-123", sample_df)
        cache.put("def-456", sample_df)
        entries = cache.list_entries()
        assert len(entries) == 2
        ids = {e["resource_id"] for e in entries}
        assert ids == {"abc-123", "def-456"}

    def test_list_includes_row_count(self, cache, sample_df):
        cache.put("abc-123", sample_df)
        entries = cache.list_entries()
        assert entries[0]["row_count"] == 3

    def test_clear_removes_all(self, cache, sample_df):
        cache.put("abc-123", sample_df)
        cache.put("def-456", sample_df)
        cache.clear()
        assert cache.list_entries() == []


class TestTableName:
    def test_hyphens_become_underscores(self, cache):
        assert cache._table_name("0e8ffe58-28bb-4dde") == "r_0e8ffe58_28bb_4dde"


class TestSQLQuery:
    def test_sql_on_cached_data(self, cache, sample_df):
        cache.put("abc-123", sample_df)
        table = cache._table_name("abc-123")
        result = cache.sql(f'SELECT * FROM "{table}" WHERE id = 1')
        assert len(result) == 1
        assert result.iloc[0]["valor"] == "a"
