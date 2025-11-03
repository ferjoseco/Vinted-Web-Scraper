"""
Vinted UK Web Scraper
Scrapes product listings from Vinted UK to calculate average prices
for items matching user-specified brand, description, and condition.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import re
import time


def get_user_input():
    """
    Prompt user for product information.
    Returns tuple of (brand, description, condition).
    """
    print("=" * 60)
    print("Vinted UK Price Scraper")
    print("=" * 60)
    brand = input("Enter brand (e.g., Nike, Zara): ").strip()
    description = input("Enter a detailed description of the product (e.g., White Air Force 1 sneakers): ").strip()

    # Product condition menu
    condition_menu = {
        "1": "New With Tags",
        "2": "New Without Tags",
        "3": "Very Good",
        "4": "Good",
        "5": "Satisfactory",
    }

    print("\nSelect condition:")
    print("  1 = New With Tags")
    print("  2 = New Without Tags")
    print("  3 = Very Good")
    print("  4 = Good")
    print("  5 = Satisfactory")

    # Input loop with validation
    condition = None
    while condition is None:
        choice = input("Enter a number (1-5): ").strip()
        if choice in condition_menu:
            condition = condition_menu[choice]
        else:
            print("Invalid input. Please enter a number from 1 to 5.")
    return brand, description, condition


def construct_search_url(brand, description, condition):
    """
    Construct the Vinted UK search URL from brand and description.
    Replaces spaces with + for URL encoding.
    """
    # Format intputs: replace spaces with "+"
    search_terms = f"{brand} {description} {condition}".strip()
    search_text = search_terms.replace(" ", "+")
    
    # Construct URL
    base_url = "https://www.vinted.co.uk/catalog"
    url = f"{base_url}?search_text={search_text}"
    
    return url


def setup_driver(headless=True):
    """
    Setup and configure Chrome driver with Selenium.
    Uses webdriver_manager to automatically handle driver installation.
    
    Args:
        headless: If True, runs browser in headless mode (no GUI)
    
    Returns:
        Configured WebDriver instance
    """
    # Configure Chrome options
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Use webdriver_manager to handle driver setup
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver


def scrape_vinted_prices(driver, url):
    """
    Navigate to Vinted URL, wait for content to load, and extract prices.
    
    Args:
        driver: Selenium WebDriver instance
        url: Vinted search URL
    
    Returns:
        List of price values (floats)
    """
    print(f"\nLoading page: {url}")
    driver.get(url)
    
    
    # Wait up to 15 seconds for product prices to appear
    # Search for elements that contain "price" or  "£"
    try:

        print("\nCalculating a price for your product...")
        wait = WebDriverWait(driver, 15)
        
        
        price_selectors = [
            (By.CSS_SELECTOR, "[class*='price']"),
            (By.CSS_SELECTOR, "[data-testid*='price']"),
            (By.XPATH, "//*[contains(text(), '£')]"),
            (By.CSS_SELECTOR, ".new-item-box__price"),
        ]
        
        price_element_found = False
        for by, selector in price_selectors:
            try:
                wait.until(EC.presence_of_element_located((by, selector)))
                price_element_found = True
                break
            except:
                continue
        
        if not price_element_found:
            # Wait for any content that might contain products
            print("Loading...")
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(3)  # Give extra time for JS to render
        
        # Additional wait to ensure all content is loaded
        time.sleep(2)
        
    except Exception as e:
        print(f"Check your internet connection and try again.")
        return []
    
    # Extract prices from the page
    prices = []
    
    price_patterns = [
        "[class*='price']",
        "[data-testid*='price']",
        ".new-item-box__price",
        ".feed-grid__item [class*='price']",
        "[class*='Price']",
        "[class*='item-price']",
    ]
    
    for pattern in price_patterns:
        try:
            price_elements = driver.find_elements(By.CSS_SELECTOR, pattern)
            if price_elements:
                for element in price_elements:
                    price_text = element.text.strip()
                    if price_text:
                        prices.append(price_text)
                break
        except:
            continue
    
    #Find all elements containing "£" symbol
    if not prices:
        try:
            all_text = driver.find_elements(By.XPATH, "//*[contains(text(), '£')]")
            for element in all_text:
                text = element.text.strip()
                if text and "£" in text:
                    prices.append(text)
        except Exception as e:
            print(f"Please try again later. Error: {e}")
    
    print(f"Extracted {len(prices)} product prices")
    
    return prices


#Clean price string and convert to float
def clean_price(price_string):
    """
    Clean price string and convert to float.
    
    Examples:
        "£12.50" -> 12.50
        "£ 15.99" -> 15.99
        "Price: £20" -> 20.0
    
    Args:
        price_string: Raw price string from webpage
    
    Returns:
        Float value of price, or None if parsing fails
    """
    if not price_string:
        return None
    
    # Remove £ symbol and any whitespace
    cleaned = price_string.replace("£", "").strip()
    
    # Extract first number (in case there are multiple prices or text)
    # Standard price format
    match = re.search(r'(\d+\.?\d*)', cleaned)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    
    return None



def calculate_average_price(prices):
    """
    Calculate average price from list of prices.
    
    Args:
        prices: List of float prices
    
    Returns:
        Average price as float, or None if list is empty
    """
    if not prices:
        return None
    
    return sum(prices) / len(prices)


def main():
    """
    Main function to orchestrate the scraping process.
    """
    # Get user input
    brand, description, condition = get_user_input()
    
    # Construct search URL
    url = construct_search_url(brand, description, condition)
    
    # Setup driver
    driver = None
    try:
        driver = setup_driver(headless=True)
        
        # Scrape prices
        price_strings = scrape_vinted_prices(driver, url)
        
        if not price_strings:
            print("\n⚠️  No prices found on the page.")
            print("  - No results matched your search")
            print("Please check your spelling and try again.")
            return
        
        # Clean prices
        cleaned_prices = []
        for price_str in price_strings:
            price_float = clean_price(price_str)
            if price_float is not None:
                cleaned_prices.append(price_float)
        
        if not cleaned_prices:
            print("\n⚠️  Could not retrieve any prices from the page.")
            return
        
        # Use cleaned prices directly since filtering was removed
        filtered_prices = cleaned_prices
        
        # Calculate average
        avg_price = calculate_average_price(filtered_prices)
        
        # Display results
        print("\n" + "=" * 60)
        print("RESULTS")
        print("=" * 60)
        print(f"Search terms: {brand} {description}")
        print(f"Condition filter: {condition}")
        
        if avg_price is not None:
            print(f"Average price: £{avg_price:.2f}")
            print("\n" + "=" * 60)
            print(f"RESALE PRICE SUGGESTION: £{avg_price:.2f}")
            print("=" * 60)
        else:
            print("Could not calculate average price.")
        
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Close the browser and thank the user
        if driver:
            print("\nThanks for using Vinted UK Price Scraper!") 
            print("See you next time!")
            driver.quit()


if __name__ == "__main__":
    main()


