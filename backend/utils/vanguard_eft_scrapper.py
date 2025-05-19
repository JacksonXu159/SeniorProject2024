import csv
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup

# Setup headless Firefox
options = webdriver.FirefoxOptions()

driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)

url = "https://investor.vanguard.com/investment-products/list/all?filters=open"
driver.get(url)

output_csv = "vanguard_funds.csv"
all_data = []
headers = []
previous_first_row = None

while True:
    time.sleep(3)  # Wait for the page to load

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")

    if table is None:
        print("No table found on the page. Exiting.")
        break

    rows = table.find_all("tr")

    if not headers and len(rows) > 1:
        first_row = rows[1]
        headers = [cell.get_text(strip=True) for cell in first_row.find_all(["td", "th"])]

    current_page_data = []
    for row in rows[2:]:
        cells = row.find_all(["td", "th"])
        row_data = [cell.get_text(strip=True) for cell in cells]
        if row_data:
            all_data.append(row_data)
            current_page_data.append(row_data)

    # Check if the first row is same as the previous page (indicates last page)
    if previous_first_row == current_page_data[0] if current_page_data else None:
        print("Detected same first row on next page. Assuming last page reached.")
        break

    previous_first_row = current_page_data[0] if current_page_data else None

    # Try to go to next page
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="next page"]'))
        )
        next_button = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="next page"]')
        driver.execute_script("arguments[0].click();", next_button)
    except Exception as e:
        print("Next button not found or not clickable. Ending pagination.")
        break

# Save to CSV
with open(output_csv, mode="w", newline='', encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(headers)
    writer.writerows(all_data)

print(f"Scraping complete! Data saved to '{output_csv}'.")

driver.quit()
