import os

DATABASE_URL = "sqlite:///./tenders.db"

DB_TYPE = os.getenv("DB_TYPE", "sqlite")

BASE_URL = "https://bip.zambrow.pl"
TENDERS_PATH = "/zamowienia-publiczne"

LOG_FORMAT = "%(levelname)s: %(message)s"

if DB_TYPE == "sqlite":
    DATABASE_URL = "sqlite:///./tenders.db"
    ENGINE_KWARGS = {"connect_args": {"check_same_thread": False}}
else:
    # An example for another database in the future
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")
    ENGINE_KWARGS = {}