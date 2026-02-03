from dataclasses import dataclass
import logging
from typing import Dict, List, Optional
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright, Page

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

BASE_URL = "https://bip.zambrow.pl"
TENDERS_PATH = "/zamowienia-publiczne"
CONTENT_SELECTOR = "article#content"
ROW_SELECTOR = "table tr"


@dataclass
class TenderDTO:
    title: str
    link: str
    date: str


def parse_row_to_dto(
    title_text: str, href: Optional[str], date_text: str
) -> Optional[TenderDTO]:
    if not title_text or not date_text:
        return None

    return TenderDTO(
        title=title_text.strip(),
        link=urljoin(BASE_URL, href) if href else "",
        date=clean_date(date_text),
    )


def clean_date(raw_date: str) -> str:
    parts = raw_date.strip().split()
    return parts[0] if parts else ""


def get_tenders_from_page(page: Page) -> List[TenderDTO]:
    url = urljoin(BASE_URL, TENDERS_PATH)
    page.goto(url, wait_until="networkidle")

    content_area = page.wait_for_selector(CONTENT_SELECTOR)
    if not content_area:
        return []

    rows = content_area.query_selector_all(ROW_SELECTOR)
    results = []

    for row in rows:
        cols = row.query_selector_all("td")
        if len(cols) != 2:
            continue

        link_el = cols[0].query_selector("a")
        if not link_el:
            continue

        tender = parse_row_to_dto(
            title_text=link_el.inner_text(),
            href=link_el.get_attribute("href"),
            date_text=cols[1].inner_text(),
        )

        if tender:
            results.append(tender)

    return results


def scrape_zambrow_tenders() -> List[TenderDTO]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            data = get_tenders_from_page(page)
            logging.info(f"Successfully scraped {len(data)} tenders.")
            return data
        except Exception as e:
            logging.error(f"Scraping failed: {e}")
            return []
        finally:
            browser.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    results = scrape_zambrow_tenders()
    logging.info(f"Extracted {len(results)} advertisements.")

    for res in results[:5]:
        print(f"[{res.date}] {res.title[:70]}...")
