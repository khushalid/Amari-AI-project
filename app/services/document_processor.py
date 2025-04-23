import os
import re
import pandas as pd
import PyPDF2
import json
from app.services.llm_service import extract_fields_from_document  # Note plural "fields"
import pdfplumber
from pdf2image import convert_from_path
import pytesseract
import os
from PyPDF2 import PdfReader

class DocumentProcessor:
    """
    Service to process uploaded customs documents and extract relevant information.
    """
    
    def process_documents(self, bol_path, invoice_path):
        """
        Process the bill of lading and commercial invoice documents.
        
        Args:
            bol_path: Path to the bill of lading PDF file
            invoice_path: Path to the commercial invoice Excel file
            
        Returns:
            dict: Extracted data for form filling
        """
        # Extract data from bill of lading
        bol_data = self.extract_from_bol(bol_path)
        
        # Extract data from commercial invoice
        invoice_data = self.extract_from_invoice(invoice_path)
        print(f"Invoice Data: {invoice_data}")
        
        # Combine extracted data
        combined_data = {**bol_data, **invoice_data}
        
        return combined_data


    def extract_from_bol(pdf_path):

        # Step 2: Extract text with PyPDF2 for digital PDFs
        with open(pdf_path, "r") as f:
            reader = PdfReader(f)
            pdf_text = "\n".join([page.extract_text() or "" for page in reader.pages])
        print("text: ", pdf_text)
        try:
            print(f"Converting PDF to images...")
            images = convert_from_path(pdf_path)

            print(f"Number of pages: {len(images)}")
            full_text = ''
            for i, img in enumerate(images):
                page_text = pytesseract.image_to_string(img)
                print(f"\n--- Page {i+1} Preview ---\n{page_text[:500]}")
                full_text += page_text + '\n'

            if not full_text.strip():
                raise ValueError("OCR failed to extract text from all pages.")

            # Define fields to extract
            keys_to_extract = [
                "Bill of lading number",
                "Consignee name", 
                "Consignee address",
                "Date"
            ]

            # Call your LLM or pattern-based field extractor
            extracted_data = extract_fields_from_document(full_text, keys_to_extract)

            print("LLM extraction results:")
            print(json.dumps(extracted_data, indent=2))

            return extracted_data

        except Exception as e:
            print(f"Error processing {pdf_path}: {str(e)}")
            return None

    
    def extract_from_invoice(self, excel_path):
        """
        Extract data from commercial invoice and packing list Excel.
        
        Based on the sample invoice, we need to extract:
        - Container number
        - Line items count
        - Average gross weight
        - Average price
        """
        try:
            print(f"Converting PDF to images...")
            images = convert_from_path(excel_path)

            print(f"Number of pages: {len(images)}")
            full_text = ''
            for i, img in enumerate(images):
                page_text = pytesseract.image_to_string(img)
                print(f"\n--- Page {i+1} Preview ---\n{page_text[:500]}")
                full_text += page_text + '\n'

            if not full_text.strip():
                raise ValueError("OCR failed to extract text from all pages.")

            # Define fields to extract
            keys_to_extract = [
                "Container number",
                "Line items count",
                "Average gross weight",
                "Average price"
            ]

            # Call your LLM or pattern-based field extractor
            extracted_data = extract_fields_from_document(full_text, keys_to_extract)

            print("LLM extraction results:")
            print(json.dumps(extracted_data, indent=2))

            return extracted_data

        except Exception as e:
            print(f"Error processing {excel_path}: {str(e)}")
            return None
