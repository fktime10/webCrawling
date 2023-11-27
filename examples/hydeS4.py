import mechanicalsoup
from urllib.parse import urlparse
import json
import boto3

# Connect to the target website
browser = mechanicalsoup.StatefulBrowser(user_agent="MechanicalSoup")
browser.open("https://www.juraforum.de/news/")

# Get the base URL
base_url = "https://www.juraforum.de/news/"

# Create a function to extract content
def extract_content(url):
    browser.open(url)
    text_content = browser.get_current_page().text
    return text_content

# Dictionary to store extracted content
extracted_content = []


# Counter for numerical IDs
id_counter = 1  # Start ID from 1, for example

# Extract content from links within the same domain
for link in browser.page.select('a'):
    href = link.get('href')
    # Check if the link belongs to the same domain
    if href and urlparse(href).netloc == urlparse(base_url).netloc:
        # Extract content from the link
        text_content = extract_content(href)
        # Add ID, Source (URL), and content to extracted_content dictionary
        extracted_content.append({"id": id_counter, "source": href, "text": text_content})
        id_counter += 1  # Increment ID counter for the next entry


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

 
 