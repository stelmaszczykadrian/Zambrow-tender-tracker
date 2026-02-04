import logging

from app.config import LOG_FORMAT
from app.database import db_manager
from app.models import Tender
from app.repository import TenderRepository
from app.scraper import scrape_zambrow_tenders
from app.service import TenderService

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


def main():
    db_manager.init_db()
    db = db_manager.get_session()

    try:
        service = TenderService(db)
        added = service.sync_tenders()

        logging.info(f"Done. Added {added} new items.")
    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
