"""Integration tests for Customer Search HTTP API."""

import time
import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


class TestCustomerSearchAPI:
    """Integration test suite for /api/v1/customers/search."""

    def test_search_success_ac01(self):
        """AC-01: GET /api/v1/customers/search?q=ana returns HTTP 200 and JSON array."""
        response = client.get("/api/v1/customers/search?q=ana")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(item["name"] == "Ana Garcia" for item in data)

    def test_search_matches_name_and_email_ac02(self):
        """AC-02: Searching with q=doe matches both customer name and email."""
        response = client.get("/api/v1/customers/search?q=doe")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
        names = [item["name"] for item in data]
        emails = [item["email"] for item in data]
        assert "John Doe" in names
        assert "jane.doe@example.com" in emails

    def test_search_case_insensitive_ac03(self):
        """AC-03: Searching with uppercase q=ALICE returns matching records."""
        response = client.get("/api/v1/customers/search?q=ALICE")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(item["name"] == "Alice Smith" for item in data)

    def test_search_item_fields_ac04(self):
        """AC-04: Every item returned includes id, name, email, and is_active."""
        response = client.get("/api/v1/customers/search?q=doe")
        assert response.status_code == 200
        data = response.json()
        for item in data:
            assert "id" in item and isinstance(item["id"], str)
            assert "name" in item and isinstance(item["name"], str)
            assert "email" in item and isinstance(item["email"], str)
            assert "is_active" in item and isinstance(item["is_active"], bool)

    @pytest.mark.parametrize(
        "invalid_q",
        [
            "",
            "   ",
            "a",
            " a ",
        ],
    )
    def test_search_short_or_blank_query_ac05(self, invalid_q):
        """AC-05: Blank, whitespace-only, or single-character q returns HTTP 400."""
        response = client.get("/api/v1/customers/search", params={"q": invalid_q})
        assert response.status_code == 400
        data = response.json()
        assert data.get("detail") == "Query string must be at least 2 characters long"

    def test_search_non_existent_returns_empty_list_ac06(self):
        """AC-06: Searching for non-existent values returns HTTP 200 and []."""
        response = client.get("/api/v1/customers/search?q=nonexistentqueryxyz")
        assert response.status_code == 200
        assert response.json() == []

    def test_search_missing_q_parameter_ts04(self):
        """TS-04: Missing query parameter q produces HTTP 422."""
        response = client.get("/api/v1/customers/search")
        assert response.status_code == 422

    def test_search_query_exceeding_max_length(self):
        """Query parameter exceeding 100 characters returns HTTP 400."""
        response = client.get("/api/v1/customers/search", params={"q": "a" * 101})
        assert response.status_code == 400
        data = response.json()
        assert data.get("detail") == "Query string must not exceed 100 characters"

    def test_search_response_latency_nfr01(self):
        """NFR-01: Search endpoint must respond in under 150ms."""
        start = time.perf_counter()
        response = client.get("/api/v1/customers/search?q=doe")
        duration_ms = (time.perf_counter() - start) * 1000
        assert response.status_code == 200
        assert duration_ms < 150, f"Response took {duration_ms:.2f}ms which exceeds 150ms limit"

    def test_search_limit_success(self):
        response = client.get("/api/v1/customers/search?q=example.com&limit=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_search_limit_invalid_values(self):
        response_zero = client.get("/api/v1/customers/search?q=doe&limit=0")
        assert response_zero.status_code == 422

        response_too_large = client.get("/api/v1/customers/search?q=doe&limit=101")
        assert response_too_large.status_code == 422

