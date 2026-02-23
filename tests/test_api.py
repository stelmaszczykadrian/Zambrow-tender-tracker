import datetime

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.api import app
from app.models import Tender
from app.service import TenderService
from app.database import db_manager

client = TestClient(app)


@pytest.fixture
def mock_db_session():
    session = MagicMock()
    session.query.return_value = MagicMock()
    session.add = MagicMock()
    session.commit = MagicMock()
    session.rollback = MagicMock()
    session.close = MagicMock()
    return session


@pytest.fixture(autouse=True)
def mock_get_session(mock_db_session, monkeypatch):
    monkeypatch.setattr(db_manager, "get_session", lambda: mock_db_session)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch("app.api.TenderService")
def test_sync_endpoint_success(mock_service_class):
    mock_service_instance = mock_service_class.return_value
    mock_service_instance.sync_tenders.return_value = 7

    response = client.post("/sync")

    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "added": 7,
        "message": "7 new tenders added",
    }
    mock_service_instance.sync_tenders.assert_called_once()


@patch("app.api.TenderService")
def test_sync_endpoint_failure(mock_service_class):
    mock_service_instance = mock_service_class.return_value
    mock_service_instance.sync_tenders.side_effect = Exception("Database error")

    response = client.post("/sync")

    assert response.status_code == 500
    assert "Synchronization error" in response.json()["detail"]


def test_tenders_endpoint_empty_db(mock_db_session):
    mock_query = MagicMock()
    mock_query.count.return_value = 0
    mock_query.all.return_value = []

    mock_query.order_by.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query

    mock_db_session.query.return_value = mock_query

    response = client.get("/tenders?limit=10")

    assert response.status_code == 200
    data = response.json()
    assert data["total_in_database"] == 0
    assert data["returned"] == 0
    assert data["limit"] == 10
    assert data["offset"] == 0
    assert data["data"] == []


def test_tenders_endpoint_with_data(mock_db_session):
    mock_tender1 = Tender(
        id=1,
        title="Test 1",
        link="https://link1",
        date=datetime.datetime(2026, 2, 20),
        scraped_at=datetime.datetime(2026, 2, 21),
    )

    mock_tender2 = Tender(
        id=2,
        title="Test 2",
        link="https://link2",
        date=datetime.datetime(2026, 2, 19),
        scraped_at=datetime.datetime(2026, 2, 20),
    )

    mock_query_chain = MagicMock()
    mock_query_chain.count.return_value = 2
    mock_query_chain.all.return_value = [mock_tender1, mock_tender2]

    mock_query_chain.order_by.return_value = mock_query_chain
    mock_query_chain.offset.return_value = mock_query_chain
    mock_query_chain.limit.return_value = mock_query_chain

    mock_db_session.query.return_value = mock_query_chain

    response = client.get("/tenders?limit=10")

    assert response.status_code == 200
    data = response.json()
    assert data["total_in_database"] == 2
    assert data["returned"] == 2
    assert len(data["data"]) == 2
    assert data["data"][0]["title"] == "Test 1"
    assert "date" in data["data"][0]
