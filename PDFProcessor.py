import re
import pymupdf
import csv
from collections import namedtuple
from typing import Dict, Pattern, Optional, Tuple
from tqdm import tqdm

class PDFProcessor:
    def __init__(self, pdf_file_path: str, csv_file_path: str = 'output.csv', regexes: Dict[str, Pattern] = None,
                 required_fields: Optional[list] = None):
        """
        Initialize the PDF processor with file paths and regular expressions.

        :param pdf_file_path: Path to the PDF file to process.
        :param csv_file_path: Path to the CSV file to write the results.
        :param regexes: Dictionary of regex patterns, where keys will be used as field names in the namedtuple.
        :param required_fields: List of fields that must be non-null for the record to be considered complete.
        """
        self.pdf_file_path = pdf_file_path
        self.csv_file_path = csv_file_path
        self.regex_mode_enabled = regexes is not None

        if self.regex_mode_enabled:
            self.initialize_regex_mode(regexes, required_fields)
        else:
            self.regexes = None
            self.Line = None
            self.empty_record = None

    def initialize_regex_mode(self, regexes: Dict[str, Pattern], required_fields: Optional[list]):
        """
        Initialize regex-related attributes, including compiling regexes, creating namedtuple fields,
        and setting required fields.

        :param regexes: Dictionary of regex patterns.
        :param required_fields: List of required fields.
        """

        self.regexes = self.compile_regexes(regexes)

        # Dynamically create the field names for namedtuple
        field_names = []
        for field, regex in self.regexes.items():
            num_groups = re.compile(regex).groups
            if num_groups == 1:
                field_names.append(field)  # Single field name
            else:
                # Create field names with suffixes for multiple groups
                field_names.extend([f"{field}_{i + 1}" for i in range(num_groups)])

        # Create the namedtuple dynamically using regex dictionary keys as field names
        self.Line = namedtuple('Line', field_names)
        self.empty_record = self.Line(*([None] * len(self.Line._fields)))
        
        # If required_fields is not provided, set it to the first field
        self.required_fields = required_fields if required_fields else [field_names[0]]

    def compile_regexes(self, regex_dict: Dict[str, str]) -> Dict[str, re.Pattern]:
        """
        Compiles a dictionary of regex strings into regex patterns.

        :param regex_dict: Dictionary where keys are field names and values are regex strings.
        :return: A dictionary with compiled regex patterns.
        """
        return {field: re.compile(pattern) for field, pattern in regex_dict.items()}

    def parse_record(self, record: namedtuple) -> namedtuple:
        """
        Normalize spaces in each field of the record by collapsing multiple spaces into one.
        """
        cleaned_values = {
            field: re.sub(r'\s+', ' ', str(getattr(record, field))).strip() if getattr(record, field) else None
            for field in record._fields}
        return record._replace(**cleaned_values)

    def process_pdf(self) -> None:
        """
        Process the PDF and write the data directly to CSV line by line.
        """
        if not self.regex_mode_enabled:
            raise RuntimeError("Cannot process PDF without regex. Use 'preview_regex_try' for manual inspection.")

        with pymupdf.open(self.pdf_file_path) as doc, open(self.csv_file_path, mode='w', newline='',
                                                        encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(self.Line._fields)
            record = self.empty_record

            for page in tqdm(doc, total=len(doc), desc="Processing PDF", unit="page"):
                text = page.get_text("text", sort=True)

                for line in text.splitlines():
                    # Process the extracted text
                    record = self.extract_data_from_line(line, record)
                    
                    # Check if the record is ready to be written (last relevant field is filled)
                    if self.is_record_complete(record):
                        record = self.parse_record(record) 
                        csv_writer.writerow(record)
                        record = self.empty_record  # Reset for the next block

            # Write any remaining record if the last page doesn't end with a complete record
            if record != self.empty_record:
                csv_writer.writerow(record)

    def is_record_complete(self, record: namedtuple) -> bool:
        """
        Check if the record is complete by verifying that all required fields are non-null.
        """
        # Check if all required fields are non-null
        return all(getattr(record, field) for field in self.required_fields)

    def extract_data_from_line(self, line: str, record: namedtuple) -> namedtuple:
        """
        Check each regex against the line and update the record accordingly.
        Handles regex with multiple groups.
        """
        for field, regex in self.regexes.items():
            if match := regex.search(line):
                groups = match.groups()
                if len(groups) == 1:
                    # Single group, map directly to the field
                    record = record._replace(**{field: groups[0]})
                else:
                    # Multiple groups, map to corresponding fields with suffixes
                    record = record._replace(**{f"{field}_{i + 1}": group for i, group in enumerate(groups)})
        return record

    def preview_regex_try(self, page_from_to: Tuple[int, int] = (0, 5), match_type: str = 'both') -> None:
        """
        Preview the output of the regex patterns on the specified pages, allowing filtering for success, failure, or both.

        :param page_from_to: A tuple indicating the range of pages to apply regex (inclusive).
        :param match_type: Specifies the type of match to display ('success', 'fail', 'both').
        """
        if match_type not in ['success', 'fail', 'both']:
            raise ValueError("The 'match_type' parameter must be 'success', 'fail', or 'both'.")

        with pymupdf.open(self.pdf_file_path) as doc:
            for page_number in range(page_from_to[0], min(page_from_to[1], len(doc))):
                page = doc.load_page(page_number)
                text = page.get_text("text", sort=True)

                print(f"\n\n--- Preview of Page {page_number + 1} ---\n")

                if not self.regex_mode_enabled:
                    # If regex is not enabled, just print the text for analysis
                    print(text)
                else:
                    # If regex is enabled, try to match and display results
                    for line in text.split('\n'):
                        for field, regex in self.regexes.items():
                            match = regex.search(line)

                            if match and match_type in ['success', 'both']:
                                groups = match.groups()  # Capture all groups
                                print(f"\nProcessing line: {line}")
                                print(f"Matched field '{field}':")
                                for i, group in enumerate(groups, 1):
                                    print(f"  Group {i}: {group}")
                            elif not match and match_type in ['fail', 'both']:
                                print(f"\nProcessing line: {line}")
                                print(f"Field '{field}' did not match.")
