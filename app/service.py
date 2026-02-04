import logging
from .repository import TenderRepository
from .scraper import scrape_zambrow_tenders


class TenderService:
    def __init__(self, db_session):
        self.repo = TenderRepository(db_session)

    def sync_tenders(self) -> int:
        logging.info("I'm launching the scraper...")
        scraped_data = scrape_zambrow_tenders()
        new_count = 0

        for dto in scraped_data:
            if not self.repo.get_by_link(dto.link):
                new_tender = dto.to_model()
                self.repo.add(new_tender)
                new_count += 1

        if new_count > 0:
            self.repo.db.commit()
        return new_count
