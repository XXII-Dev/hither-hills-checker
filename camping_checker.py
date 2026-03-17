from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import schedule
import time
from datetime import datetime
from win10toast import ToastNotifier

# Configuration
URL = "https://newyorkstateparks.reserveamerica.com/camping/hither-hills-state-park/r/campgroundDetails.do?contractCode=NY&parkId=297"
CHECK_INTERVAL_MINUTES = 5

toaster = ToastNotifier()


def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def notify_user(message):
    print(f"[{get_timestamp()}] 🎉 ALERT: {message}")
    toaster.show_toast("Campsite Availability Alert", message, duration=10)


def create_driver():
    """Create a headless Chrome browser"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run without opening browser window
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--log-level=3")  # Suppress logging
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def check_availability():
    print(f"[{get_timestamp()}] 🔍 Checking campsite availability...")

    driver = None
    try:
        driver = create_driver()
        driver.get(URL)

        print(f"[{get_timestamp()}] ⏳ Waiting for page to load...")

        # Wait for the page to load dynamic content (adjust selector as needed)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "availability"))
        )

        print(f"[{get_timestamp()}] ✅ Page loaded successfully")

        # Try multiple possible selectors for availability info
        selectors_to_try = [
            (By.CLASS_NAME, "section-status"),
            (By.CLASS_NAME, "availability"),
            (By.CLASS_NAME, "site-availability"),
            (By.CSS_SELECTOR, "[class*='avail']"),
            (By.CSS_SELECTOR, "[class*='status']"),
        ]

        page_text = driver.find_element(By.TAG_NAME, "body").text

        # Look for availability patterns in the page text
        if "site(s) available" in page_text.lower():
            # Find the line with availability info
            for line in page_text.split('\n'):
                if "site(s) available" in line.lower():
                    print(f"[{get_timestamp()}] 📋 Found: {line.strip()}")

                    # Parse number
                    parts = line.strip().split()
                    if parts[0].isdigit():
                        available = int(parts[0])
                        if available > 0:
                            notify_user(line.strip())
                        else:
                            print(f"[{get_timestamp()}] 😞 No sites available")
                    break
        elif "no sites available" in page_text.lower():
            print(f"[{get_timestamp()}] 😞 No sites available")
        else:
            print(f"[{get_timestamp()}] ❓ Could not find availability info")
            print(f"[{get_timestamp()}] 💾 Saving page source for debugging...")
            with open("debug_page.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print(f"[{get_timestamp()}] 💾 Saved to debug_page.html - check this file to find the right selector")

    except Exception as e:
        print(f"[{get_timestamp()}] ❌ Error: {e}")
    finally:
        if driver:
            driver.quit()


def main():
    print("=" * 60)
    print("🏕️  CAMPSITE AVAILABILITY CHECKER (Selenium)")
    print("📍 Hither Hills State Park")
    print(f"⏰ Checking every {CHECK_INTERVAL_MINUTES} minutes")
    print("=" * 60)
    print()

    # Run immediately on start
    check_availability()

    # Then schedule recurring checks
    schedule.every(CHECK_INTERVAL_MINUTES).minutes.do(check_availability)

    print(f"\n[{get_timestamp()}] 🔄 Scheduler running. Press Ctrl+C to stop.\n")

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()