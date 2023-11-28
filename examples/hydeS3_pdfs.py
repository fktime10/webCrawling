import os
import json
from PyPDF2 import PdfReader

pdf_directory = r"C:\Users\User\webCrawling\extracted_pdfs_itm.nrw"
output_filename = "extracted_data_itm.nrw.jsonl"

def extract_text_and_title_from_pdfs(directory):
    if not os.path.exists(directory):
        print(f"The directory '{directory}' does not exist.")
        return []

    extracted_content = []

    for filename in os.listdir(directory):
        if filename.endswith('.pdf'):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'rb') as pdf_file:
                try:
                    pdf_reader = PdfReader(pdf_file)
                    num_pages = len(pdf_reader.pages)

                    pdf_text = ''
                    for page_num in range(num_pages):
                        pdf_text += pdf_reader.pages[page_num].extract_text()

                    title = filename.replace('.pdf', '')

                    if pdf_text.strip():
                        extracted_content.append({"title": title, "text": pdf_text})
                except Exception as e:
                    print(f"Error processing file: {filename}")
                    print(f"Error message: {e}")

    return extracted_content

extracted_data = extract_text_and_title_from_pdfs(pdf_directory)

with open(output_filename, "w", encoding="utf-8") as jsonl_file:
    for entry in extracted_data:
        json.dump(entry, jsonl_file, ensure_ascii=False)
        jsonl_file.write('\n')
