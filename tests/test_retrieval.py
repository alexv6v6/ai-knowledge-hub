"""
test_retrieval.py — Unit tests for SQL connector.
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.retrieval.sql_connector import SQLConnector


@pytest.fixture
def connector():
    return SQLConnector(db_url="sqlite:///data/processed/test_knowledge.db")


class TestSQLConnector:
    def test_schema_contains_tables(self, connector):
        schema = connector.get_schema()
        assert "products" in schema
        assert "sales" in schema
        assert "customers" in schema

    def test_execute_simple_query(self, connector):
        results = connector.execute_query("SELECT COUNT(*) as total FROM products")
        assert len(results) == 1
        assert "total" in results[0]

    def test_execute_select_all(self, connector):
        results = connector.execute_query("SELECT * FROM products")
        assert len(results) > 0
        assert "name" in results[0]

    def test_execute_join_query(self, connector):
        results = connector.execute_query("""
            SELECT p.name, SUM(s.total) as revenue
            FROM sales s JOIN products p ON s.product_id = p.id
            GROUP BY p.name ORDER BY revenue DESC
        """)
        assert len(results) > 0
        assert "revenue" in results[0]

    def test_invalid_query_raises(self, connector):
        with pytest.raises(ValueError):
            connector.execute_query("SELECT * FROM nonexistent_table_xyz")
