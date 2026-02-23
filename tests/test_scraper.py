import pytest
from unittest.mock import MagicMock, patch

from app.scraper import (
    scrape_zambrow_tenders,
    TenderDTO,
    clean_date,
    parse_row_to_dto,
)
from app.service import TenderService


@pytest.fixture
def mock_page():
    page = MagicMock()
    page.goto = MagicMock()
    page.wait_for_selector = MagicMock()
    page.query_selector = MagicMock()
    return page


@pytest.fixture
def mock_browser(mock_page):
    browser = MagicMock()
    browser.new_page.return_value = mock_page
    return browser


@pytest.fixture
def mock_content():
    content = MagicMock()
    content.query_selector_all.return_value = []
    return content


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.commit = MagicMock()
    db.rollback = MagicMock()
    return db


@pytest.fixture
def mock_repo(mock_db):
    repo = MagicMock()
    repo.db = mock_db
    repo.get_by_link = MagicMock()
    repo.add = MagicMock()
    return repo


@pytest.fixture
def service(mock_db, mock_repo):
    service = TenderService(mock_db)
    service.repo = mock_repo
    return service


def test_scraper_returns_list():
    results = scrape_zambrow_tenders()
    assert isinstance(results, list)


def test_clean_date_normal_case():
    assert clean_date("2026-02-19 15:30:00") == "2026-02-19"
    assert clean_date("2026-02-19") == "2026-02-19"


def test_clean_date_empty_or_invalid():
    assert clean_date("") == ""
    assert clean_date("abc") == ""
    assert clean_date("2026-02") == ""
    assert clean_date("Termin: 2026-02-19") == ""
    assert clean_date("2026-13-01") == ""


def test_parse_row_to_dto_valid_data():
    dto = parse_row_to_dto(
        title_text="ZP.271.1.2026 Przetarg na paliwo",
        href="/zamowienie/zp-271-1-2026",
        date_text="2026-02-19 09:00:00",
    )
    assert dto is not None
    assert dto.title == "ZP.271.1.2026 Przetarg na paliwo"
    assert dto.link.endswith("/zamowienie/zp-271-1-2026")
    assert dto.date == "2026-02-19"


def test_parse_row_to_dto_missing_data():
    assert parse_row_to_dto("", None, "") is None
    assert parse_row_to_dto("tytuł", "/link", "") is None


def test_sync_tenders_adds_new_items(service, mock_repo):
    mock_scraped = [
        TenderDTO(title="Test A", link="https://link1", date="2026-02-20"),
        TenderDTO(title="Test B", link="https://link2", date="2026-02-19"),
    ]

    mock_repo.get_by_link.return_value = None

    with patch("app.service.scrape_zambrow_tenders", return_value=mock_scraped):
        added = service.sync_tenders()

    assert added == 2
    assert mock_repo.add.call_count == 2
    mock_repo.db.commit.assert_called_once()


def test_sync_tenders_skips_existing(service, mock_repo):
    mock_scraped = [
        TenderDTO(title="Istniejący", link="https://link1", date="2026-02-20"),
        TenderDTO(title="Nowy", link="https://link2", date="2026-02-19"),
    ]

    mock_repo.get_by_link.side_effect = [MagicMock(), None]

    with patch("app.service.scrape_zambrow_tenders", return_value=mock_scraped):
        added = service.sync_tenders()

    assert added == 1
    mock_repo.add.assert_called_once()
    mock_repo.db.commit.assert_called_once()


def test_sync_tenders_no_new_items_no_commit(service, mock_repo):
    mock_scraped = [
        TenderDTO(title="Duplikat", link="https://link1", date="2026-02-20"),
    ]

    mock_repo.get_by_link.return_value = MagicMock()

    with patch("app.service.scrape_zambrow_tenders", return_value=mock_scraped):
        added = service.sync_tenders()

    assert added == 0
    mock_repo.add.assert_not_called()
    mock_repo.db.commit.assert_not_called()


def test_sync_tenders_handles_empty_scrape(service, mock_repo):
    with patch("app.service.scrape_zambrow_tenders", return_value=[]):
        added = service.sync_tenders()

    assert added == 0
    mock_repo.add.assert_not_called()
    mock_repo.db.commit.assert_not_called()
