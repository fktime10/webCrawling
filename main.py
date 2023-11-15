import concurrent.futures
import metadata_parser
import pandas as pd
import logging
import os
import sys

 
sys.stdout.reconfigure(encoding='utf-8')

def extract_metadata(url):
    try:
        page = metadata_parser.MetadataParser(url)
        return page.metadata
    except Exception as e:
        logging.error(f"Error extracting metadata for {url}: {e}")
        return None

def extract_custom_fields(metadata, url):
    if metadata:
        # Extract desired fields (replace with actual field names)
        return {
            'URL': url,
            'Type': metadata.get('og', {}).get('type', ''),
            'Title': metadata.get('og', {}).get('title', ''),
            'SiteName': metadata.get('og', {}).get('site_name', ''),
            'Locale': metadata.get('og', {}).get('locale', ''),
            'ID': metadata.get('id_field', ''),  # Replace with the actual field name
            'Source': metadata.get('source_field', ''),  # Replace with the actual field name
            'Text': metadata.get('text_field', ''),  # Replace with the actual field name
        }
    return None

# List of URLs to extract metadata from
urls = ['https://wistev.de/journal/',
        'https://de.wikibooks.org/wiki/Verwaltungsrecht_in_der_Klausur/_Das_Lehrbuch',
        'https://www.itm.nrw/publikationen/',
        'https://www.juraforum.de/news/',
        'https://www.komnet.nrw.de/_sitetools/komnetrecherche/index.html?cat=&q=&date-from=&date-until=&sort=',
        'https://www.zvr-online.com/archiv',
        'https://www.rechtslupe.de/',
        'https://freilaw.de/ausgaben/'
        ]  # Add more URLs as needed

# Initialize an empty list to store metadata
metadata_list = []

# Extract metadata for each URL concurrently
with concurrent.futures.ThreadPoolExecutor() as executor:
    results = list(executor.map(extract_metadata, urls))

# Extract custom fields from metadata for each URL
for url, metadata in zip(urls, results):
    custom_fields = extract_custom_fields(metadata, url)
    if custom_fields:
        metadata_list.append(custom_fields)

# Convert the list of dictionaries to a pandas DataFrame
df = pd.DataFrame(metadata_list)

# Specify the directory path for saving the Excel file
output_directory = r'C:\Users\User\Desktop\hydeAi'
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Save the DataFrame to an Excel file
excel_file_path = os.path.join(output_directory, 'metaData.xlsx')
df.to_excel(excel_file_path, index=False)

print(f"Metadata has been saved to {excel_file_path}")
