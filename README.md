<p align="center">
  
<img width="300" height="300" alt="Gemini_Generated_Image_iv0f6piv0f6piv0f" src="https://github.com/user-attachments/assets/26755cf8-754e-4e13-933d-eb19dd81829b" />

## 📖 Description

**Zambrow Tender Tracker** A simple application for monitoring tender announcements (public procurement) from the Public Information Bulletin in Zambrów.

- Scraping the tender list from https://bip.zambrow.pl/zamowienia-publiczne
- Saving new tenders to the database (avoiding duplicates via links)
- API endpoints:
- GET `/health` – checking server status
- GET `/scrape` – raw data from the scraper
- POST `/sync` – starting synchronization and saving new tenders
- GET `/tenders` – a list of tenders from the database (with limit/offset pagination)
<br>

## :star: Technologies
- Python 3.11+
- FastAPI (REST API + interactive Swagger documentation)
- Playwright (BIP page scraping)
- SQLAlchemy + SQLite (database)
- Pytest + unittest.mock (unit and integration tests)
<br>

## How to start

1. **Clone the repository**

```
   git clone https://github.com/stelmaszczykadrian/Zambrow-tender-tracker.git
```

2. **Create & activate virtual environment**
   
  ```
  python -m venv venv
  ```

* **Windows (PowerShell / CMD):**

```
venv\Scripts\activate
```

* **Linux / macOS:**

```
source venv/bin/activate
```

3. **Install dependencies**
   
  ```
  pip install -r requirements.txt
  ```
4. **Run the application (single entry point)**
- One-time synchronization (CLI)
```
python -m app.main
python -m app.main sync
```

- Start FastAPI server + Swagger UI

```
python -m app.main api
```
After starting, open in your browser:
```
http://127.0.0.1:8000/docs
```

You will see all available endpoints:
- GET /health – check if the server is alive
- GET /scrape – get raw scraped data
- POST /sync – trigger synchronization and see how many new tenders were added
- GET /tenders – view paginated list of tenders from the database (try ?limit=10)

5. **Run tests**

```
pytest -v
```



Quick test flow:
1.  Run python -m app.main sync → synchronize once
2.  Run python -m app.main api → start server
3.  Go to http://127.0.0.1:8000/docs
4. Try POST /sync → see how many new tenders were added
5. Try GET /tenders?limit=10 → see list from database


## Future ideas:
- Automatic sync every hour (APScheduler)
- Multiple BIP sources (Łomża, Białystok etc.)
- Simple frontend (HTML + JS)
- Deployment (Render / Railway / Docker)


## 🖼️ Screenshots
<img width="1820" height="693" alt="{C65A8F1F-DB0A-476B-BCD3-3E1491276909}" src="https://github.com/user-attachments/assets/7150c1ef-08b5-4083-8d30-5ffeb2b0c628" />


