import os
import json

pdf_directory = "C:/Users/User/Desktop/MechanicalSoup/extracted_pdfs_freilaw.de"
output_filename = "extracted_data_freilaw.jsonl"

# Function to extract text and title from PDFs
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
                    from PyPDF2 import PdfReader

                    pdf_reader = PdfReader(pdf_file)
                    num_pages = len(pdf_reader.pages)

                    # Extract text from each page and concatenate into a single string
                    pdf_text = ''
                    for page_num in range(num_pages):
                        pdf_text += pdf_reader.pages[page_num].extract_text()

                    # Extract title (using the filename)
                    title = filename.replace('.pdf', '')

                    # Append extracted text and title to the list
                    extracted_content.append({"title": title, "text": pdf_text})
                except Exception as e:
                    print(f"Error processing file: {filename}")
                    print(f"Error message: {e}")

    return extracted_content

# Extract text and titles from PDFs in the specified directory
extracted_data = extract_text_and_title_from_pdfs(pdf_directory)

# Save extracted content as JSONL
with open(output_filename, "w", encoding="utf-8") as jsonl_file:
    for entry in extracted_data:
        json.dump(entry, jsonl_file, ensure_ascii=False)
        jsonl_file.write('\n')
