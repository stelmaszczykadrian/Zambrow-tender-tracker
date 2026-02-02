from playwright.sync_api import sync_playwright

def test_connection():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://bip.zambrow.pl/zamowienia-publiczne")
        print(f"Tytuł strony: {page.title()}")
        browser.close()

if __name__ == "__main__":
    test_connection()