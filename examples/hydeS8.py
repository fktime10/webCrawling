import mechanicalsoup
from urllib.parse import urlparse
import json
import requests
from PyPDF2 import PdfReader
import os

# Connect to the target website
browser = mechanicalsoup.StatefulBrowser(user_agent="MechanicalSoup")
browser.open("https://freilaw.de/ausgaben/")

# Get the base URL
base_url = "https://freilaw.de/ausgaben/"

# Directory to save PDF files
pdf_directory = "C:/Users/User/Desktop/MechanicalSoup/extracted_pdfs"
os.makedirs(pdf_directory, exist_ok=True)  # Create the directory if it doesn't exist

# Adjust the extract_content function to skip URLs containing '/feed'
def extract_content(url):
    if '/feed' in url:
        return None  # Skip URLs with '/feed'
    try:
        browser.open(url)
        text_content = browser.get_current_page().text
        return text_content
    except Exception as e:
        print(f"Error accessing URL: {url}")
        print(f"Error message: {e}")
        return None  # Return None if there's an error fetching the content

# Function to download PDF files
def download_pdf(url):
    if '/feed' in url:
        return None  # Skip URLs with '/feed'
    try:
        response = requests.get(url)
        if 'Content-Type' in response.headers and 'application/pdf' in response.headers['Content-Type']:
            filename = os.path.join(pdf_directory, url.split('/')[-1])  # Generate filename
            with open(filename, 'wb') as pdf_file:
                pdf_file.write(response.content)
            return filename
        else:
            return None
    except Exception as e:
        print(f"Error downloading PDF from URL: {url}")
        print(f"Error message: {e}")
        return None

# Dictionary to store extracted content
extracted_content = []

# Counter for numerical IDs
id_counter = 1  # Start ID from 1, for example

# Extract content from links within the same domain
for link in browser.page.select('a'):
    href = link.get('href')
    if href and urlparse(href).netloc == urlparse(base_url).netloc:
        if href.endswith('.pdf'):  # Check if the link ends with .pdf
            pdf_filename = download_pdf(href)
            if pdf_filename:
                text_content = ''
                with open(pdf_filename, 'rb') as pdf_file:
                    pdf_reader = PdfReader(pdf_file)
                    num_pages = len(pdf_reader.pages)
                    for page_num in range(num_pages):
                        text_content += pdf_reader.pages[page_num].extract_text()
                extracted_content.append({"id": id_counter, "source": href, "text": text_content})
                id_counter += 1
            else:
                print(f"Failed to download or extract text from PDF at URL: {href}")
        else:
            text_content = extract_content(href)
            extracted_content.append({"id": id_counter, "source": href, "text": text_content})
            id_counter += 1

# Rest of your code for saving extracted content as JSONL remains unchanged...

# Get the source name from the base URL
source_name = urlparse(base_url).hostname.replace("www.", "")  # Extracts the domain name as the source name

# Save extracted content as JSONL with the source name in the filename
output_filename = f"extracted_content_{source_name}.jsonl"
with open(output_filename, "w", encoding="utf-8") as jsonl_file:
    for entry in extracted_content:
        # Remove newline characters from the text_content
        entry['text'] = entry['text'].replace('\n', ' ')  # Replace '\n' with a space or '' to remove it entirely
        json.dump(entry, jsonl_file, ensure_ascii=False)
        jsonl_file.write('\n')
