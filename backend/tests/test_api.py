"""
FastAPI integration tests for all API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.api.search import init_search_engines


@pytest.fixture(scope="module", autouse=True)
def setup_engines():
    init_search_engines()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_health_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["database_connected"] is True
    assert data["indexed_documents"] > 0
    assert data["indexes"]["tfidf"] is True
    assert data["indexes"]["bm25"] is True
    assert data["indexes"]["dense"] is True


def test_stats_and_config_endpoints(client):
    res = client.get("/api/stats")
    assert res.status_code == 200
    assert res.json()["total_documents"] > 0

    res_cfg = client.get("/api/config")
    assert res_cfg.status_code == 200
    assert "rrf_k" in res_cfg.json()


def test_search_endpoint_methods(client):
    for method in ["tfidf", "bm25", "dense", "rrf"]:
        payload = {
            "query": "California power crisis",
            "method": method,
            "top_k": 5
        }
        res = client.post("/api/search", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["method"] == method
        assert len(data["results"]) > 0
        assert data["results"][0]["rank"] == 1


def test_search_compare_endpoint(client):
    payload = {
        "query": "energy trading regulations",
        "method": "rrf",
        "top_k": 5
    }
    res = client.post("/api/search/compare", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "tfidf" in data
    assert "bm25" in data
    assert "dense" in data
    assert "rrf" in data
    assert len(data["tfidf"]) > 0
    assert len(data["rrf"]) > 0


def test_email_detail_and_thread_endpoint(client):
    # Search first to get a valid document_id
    search_res = client.post("/api/search", json={"query": "FERC", "top_k": 1})
    results = search_res.json()["results"]
    assert len(results) > 0

    doc_id = results[0]["document_id"]
    res = client.get(f"/api/email/{doc_id}")
    assert res.status_code == 200
    email_data = res.json()
    assert email_data["document_id"] == doc_id
    assert "body" in email_data

    # Test thread endpoint if thread_id is available
    t_id = email_data.get("thread_id")
    if t_id:
        t_res = client.get(f"/api/thread/{t_id}")
        assert t_res.status_code == 200
        t_data = t_res.json()
        assert t_data["thread_id"] == t_id
        assert len(t_data["messages"]) > 0


def test_evaluation_endpoints(client):
    summary_res = client.get("/api/evaluation/summary")
    assert summary_res.status_code == 200
    summary_data = summary_res.json()
    assert "metrics" in summary_data
    assert "bm25" in summary_data["metrics"]

    pr_res = client.get("/api/evaluation/precision-recall")
    assert pr_res.status_code == 200
    assert "points" in pr_res.json()
    assert len(pr_res.json()["points"]) == 11


def test_analytics_endpoint(client):
    res = client.get("/api/analytics/overview")
    assert res.status_code == 200
    data = res.json()
    assert data["total_emails"] > 0
    assert data["unique_senders"] > 0
    assert len(data["top_senders"]) > 0
