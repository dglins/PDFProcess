---

# PDF to CSV Processor

This project provides a tool to extract information from PDF files using regular expressions and export the extracted data to a CSV file. It is useful for automating the extraction of specific fields from PDF documents and generating structured CSV output.

## Features

- **PDF Processing**: Parses the content of PDF files and extracts information based on patterns defined by regular expressions.
- **Regular Expression Preview**: Tests the regular expressions on specific pages of the PDF to verify their effectiveness before full processing.
- **CSV Export**: Generates a CSV file containing the extracted data.

## How to Use

### 1. Define the file paths

```python
# Define file paths for the input PDF and the output CSV
pdf_file_path = r'C:\Users\x\inputfile.pdf'
csv_file_path = r'C:\Users\x\outputfile.csv'
```

### 2. Define the regular expressions

Create a dictionary with the regular expressions you want to use to extract fields from the PDF:

```python
# Define regular expressions for the fields
regexes = {
    'process': r'\s+(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})'
}
```

### 3. Initialize the `PDFProcessor`

```python
# Initialize the PDFProcessor with the file paths, regexes, and a delimiter field
# Note that you only need the pdf_file_path to initialize the preview_regex_try()
processor = PDFProcessor(
    pdf_file_path=pdf_file_path,
    csv_file_path=csv_file_path,
    regexes=regexes,
    delimiter_field='process'
)
```

### 4. Test the regular expressions

Test your regular expressions on specific pages of the PDF to ensure they work as expected:

```python
# Preview regex matches on specific pages (from page 0 to page 5, in this case)
# match_type can be set as: success, fail and both
processor.preview_regex_try(page_from_to=(0, 5), match_type='both')
```

### 5. Process the PDF and generate the CSV output

After confirming that the regular expressions are working, process the entire PDF and export the extracted data to a CSV file:

```python
# Process the PDF and generate the CSV
processor.process_pdf()
```

## Requirements

- Python 3.x
- Libraries: `pymupdf`, `re` (regular expressions), `csv`, 'tqdm' (show the progress)

## Installation

Install the necessary libraries using `pip`:

```bash
pip install pymupdf tqdm
```

---

This `README.md` provides instructions for setting up and using your PDF-to-CSV processor tool. You can modify it as needed for your specific project.
