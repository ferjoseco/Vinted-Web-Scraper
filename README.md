## Vinted UK Price Scraper

Scrapes product listings from Vinted UK and suggests a resale price (average of discovered prices) based on a brand, product description, and a selected condition level.

### Features
- Numeric menu to pick product condition (1–5) with input validation
- Headless Chrome via Selenium + webdriver-manager (no manual ChromeDriver installs)
- Extracts prices from search results and computes an average
- Simple, clear console output with a resale price suggestion

### Requirements
- Python 3.9+
- Google Chrome installed

### Install
```bash
cd /Users/fernandojosecabrera/scraper
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run
```bash
python vinted_scraper.py
```

You will be prompted for:
1) Brand (e.g., Nike, Zara)
2) Detailed description (e.g., White Air Force 1 sneakers)
3) Condition (numeric menu 1–5):
   - 1 = New With Tags
   - 2 = New Without Tags
   - 3 = Very Good
   - 4 = Good
   - 5 = Satisfactory

The script will open a headless browser, gather prices, and print an average as a “RESALE PRICE SUGGESTION”.

### File Structure
```
/Users/fernandojosecabrera/scraper/
  ├─ README.md
  ├─ requirements.txt
  └─ vinted_scraper.py
```

### Troubleshooting
- “No prices found”:
  - Check spelling of brand/description
  - Try different condition
- “Check your internet connection and try again.”
  - Ensure you’re online and retry
- Chrome issues
  - Make sure Google Chrome is installed and up to date

### Notes
- The search URL is built from your brand, description and condition; results depend on Vinted’s current structure.
- Headless mode is enabled by default. If you want to view the browser, set `headless=False` in `setup_driver()`.
