from sqlalchemy.orm import Session
from .models import Tender


class TenderRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_link(self, link: str) -> Tender | None:
        return self.db.query(Tender).filter(Tender.link == link).first()

    def add(self, tender: Tender) -> None:
        self.db.add(tender)

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()    
