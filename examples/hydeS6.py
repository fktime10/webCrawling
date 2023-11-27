from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import json

# Set up Selenium Chrome driver
chrome_path = "path/to/chromedriver"  # Replace with your chromedriver path
service = Service(chrome_path)
driver = webdriver.Chrome(service=service)

# URL to scrape
url = "https://www.zvr-online.com/archiv"
driver.get(url)

# Extract content
extracted_content = []

links = driver.find_elements(By.XPATH, "//a[contains(@href, 'https://www.zvr-online.com')]")

for link in links:
    href = link.get_attribute("href")
    text_content = link.text.strip()
    if href and text_content:
        extracted_content.append({"source": href, "text": text_content})

# Save extracted content as JSONL
output_filename = "extracted_content_zvr-online.jsonl"
with open(output_filename, "w", encoding="utf-8") as jsonl_file:
    for entry in extracted_content:
        json.dump(entry, jsonl_file, ensure_ascii=False)
        jsonl_file.write('\n')

# Close the Selenium driver
driver.quit()
