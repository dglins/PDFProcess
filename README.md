Exemple of how to use:

# Define the file paths
pdf_file_path = r'C:\Users\x\inputfile.pdf'
csv_file_path = r'C:\Users\x\outputfile.csv'

# Define the regular expressions for the fields
regexes = {
    'process': r'\s+(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})'
}

# Initialize the PDFProcessor
processor = PDFProcessor(pdf_file_path=pdf_file_path,
                         csv_file_path=csv_file_path,
                         regexes=regexes,
                         delimiter_field='process'
                           )

# Test the regexes on specific pages
processor.preview_regex_try(page_from_to=(0, 5), match_type='both')

# Process the PDF and generate the CSV output
processor.process_pdf()
