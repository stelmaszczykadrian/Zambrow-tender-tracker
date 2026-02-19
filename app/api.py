import logging
from fastapi import Depends, FastAPI, HTTPException, Query
from pytest import Session
from app.models import Tender
from app.scraper import scrape_zambrow_tenders
from app.database import db_manager
from app.service import TenderService

app = FastAPI(
    title="Zambrow Tenders API",
    description="Simple API for scraping the Zambrów Public Information Bulletin",
    version="0.1.0",
)


@app.on_event("startup")
def startup_event():
    db_manager.init_db()
    logging.info("Database initialized (tables created if missing)")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/scrape")
def scrape_raw():
    """
    Returns raw scraped data from BIP Zambrów (for debugging).
    """
    results = scrape_zambrow_tenders()
    return {"count": len(results), "data": results}


@app.post("/sync")
def sync_tenders(db: Session = Depends(lambda: db_manager.get_session())) -> dict:
    """
    Runs synchronization process:
    - scrapes current tenders from BIP Zambrow
    - saves only new entries (based on unique link)
    - returns number of newly added records
    """
    try:
        service = TenderService(db)
        added = service.sync_tenders()
        return {
            "status": "success",
            "added": added,
            "message": f"{added} new tenders added",
        }
    except Exception as e:
        logging.exception("Synchronization failed")
        raise HTTPException(status_code=500, detail=f"Synchronization error: {str(e)}")


@app.get("/tenders")
def get_tenders(
    limit: int = Query(20, ge=1, le=100, description="Number of tenders to return"),
    offset: int = Query(0, ge=0, description="Skip this many records (pagination)"),
    db: Session = Depends(lambda: db_manager.get_session()),
):
    """
    Returns recent tenders from the database, sorted by publication date (newest first).
    """
    query = db.query(Tender).order_by(Tender.date.desc())

    total = query.count()
    tenders = query.offset(offset).limit(limit).all()

    return {
        "total_in_database": total,
        "returned": len(tenders),
        "limit": limit,
        "offset": offset,
        "data": [
            {
                "id": t.id,
                "title": t.title,
                "link": t.link,
                "date": t.date.isoformat() if t.date else None,
                "scraped_at": t.scraped_at.isoformat() if t.scraped_at else None,
            }
            for t in tenders
        ],
    }
