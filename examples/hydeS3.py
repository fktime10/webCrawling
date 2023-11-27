import mechanicalsoup
from urllib.parse import urlparse
import os
from openpyxl import Workbook
import json

# Connect to the target website
browser = mechanicalsoup.StatefulBrowser(user_agent="MechanicalSoup")
browser.open("https://www.itm.nrw/publikationen/")

# Get the base URL
base_url = "https://www.itm.nrw/publikationen/"

# Create an Excel workbook
workbook = Workbook()
sheet = workbook.active

# Dictionary to store extracted content
extracted_content = []

# Define headers for Excel
sheet.append(["URL", "Content"])

for link in browser.page.select('a'):
    href = link.get('href')
    if href and urlparse(href).netloc == urlparse(base_url).netloc:
        browser.open(href)
        current_page = browser.get_current_page()
        if current_page:
            text_content = current_page.text if hasattr(current_page, 'text') else ""
            sheet.append([href, text_content])
            extracted_content.append({"URL": href, "Content": text_content})
        browser.open(base_url)


# # Save the Excel file
# workbook.save("extracted_content3.xlsx")

# # Save extracted content as JSON
# with open("extracted_content3.json", "w", encoding="utf-8") as json_file:
#     json.dump(extracted_content, json_file, ensure_ascii=False, indent=4)
