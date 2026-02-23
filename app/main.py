import argparse
import logging

from app.config import LOG_FORMAT
from app.database import db_manager
from app.service import TenderService

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


def run_sync():
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


def run_api():
    """Starts the FastAPI server (Swagger at http://127.0.0.1:8000/docs)"""
    import uvicorn

    uvicorn.run(
        "app.api:app", host="127.0.0.1", port=8000, reload=True, log_level="info"
    )


def main():
    parser = argparse.ArgumentParser(description="Zambrow Tenders Monitor")
    parser.add_argument(
        "mode",
        nargs="?",
        default="sync",
        choices=["sync", "api"],
        help="sync = CLI synchronization (default), api = FastAPI server",
    )

    args = parser.parse_args()

    if args.mode == "sync":
        run_sync()
    elif args.mode == "api":
        run_api()


if __name__ == "__main__":
    main()
