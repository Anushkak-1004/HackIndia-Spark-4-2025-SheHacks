import os
import PyPDF2
import pytesseract
from pdf2image import convert_from_path
import pdfplumber
import pandas as pd
from openpyxl import Workbook
from docx import Document

# Set Tesseract OCR path (for Windows users)
pytesseract.pytesseract.tesseract_cmd = r"D:\Excelmate AI\tesseract.exe"

def extract_text_pypdf2(pdf_path):
    """Extract text from a text-based PDF."""
    text = ""
    with open(pdf_path, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"
    return text.strip() if text else None  # Return None if empty

def extract_text_tesseract(pdf_path):
    """Extract text from scanned PDFs using OCR."""
    images = convert_from_path(pdf_path)
    extracted_text = ""
    for img in images:
        extracted_text += pytesseract.image_to_string(img) + "\n"
    return extracted_text.strip()

def extract_text_pdf(pdf_path):
    """Detect and extract text from a PDF (text-based or scanned)."""
    text = extract_text_pypdf2(pdf_path)
    if text is None:  # If no text, use OCR
        print("No text found with PyPDF2, using OCR...")
        text = extract_text_tesseract(pdf_path)
    return text

def extract_tables_pdf(pdf_path):
    """Extract tables from a PDF using pdfplumber."""
    tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_tables = page.extract_tables()
            for table in extracted_tables:
                df = pd.DataFrame(table)  # Convert table into DataFrame
                tables.append(df)
    return tables

def extract_text_csv(csv_path):
    """Extract data from CSV files."""
    return pd.read_csv(csv_path)

def extract_text_txt(txt_path):
    """Extract text from TXT files."""
    with open(txt_path, "r", encoding="utf-8") as file:
        return file.read()

def extract_text_docx(docx_path):
    """Extract text from Word (DOCX) files."""
    doc = Document(docx_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def save_to_excel(text, tables, excel_path):
    """Save extracted text and tables to an Excel file."""
    with pd.ExcelWriter(excel_path) as writer:
        if isinstance(text, pd.DataFrame):  # If it's a CSV
            text.to_excel(writer, sheet_name="Extracted Data", index=False)
        else:
            text_df = pd.DataFrame({"Extracted Text": [text]})
            text_df.to_excel(writer, sheet_name="Extracted Text", index=False)
        
        for i, df in enumerate(tables):
            df.to_excel(writer, sheet_name=f"Table_{i+1}", index=False, header=False)
    print(f"✅ Extraction complete! Data saved to {excel_path}")

def extract_and_save(file_path, excel_path):
    """Extract text and tables from various file formats and save to Excel."""
    file_extension = os.path.splitext(file_path)[1].lower()
    extracted_text = ""
    extracted_tables = []

    if file_extension == ".pdf":
        extracted_text = extract_text_pdf(file_path)
        extracted_tables = extract_tables_pdf(file_path)
    elif file_extension == ".csv":
        extracted_text = extract_text_csv(file_path)
    elif file_extension == ".txt":
        extracted_text = extract_text_txt(file_path)
    elif file_extension == ".docx":
        extracted_text = extract_text_docx(file_path)
    else:
        print("❌ Unsupported file format.")
        return
    
    if (isinstance(extracted_text, pd.DataFrame) and not extracted_text.empty) or \
   (isinstance(extracted_text, str) and extracted_text.strip()) or \
   extracted_tables:

        save_to_excel(extracted_text, extracted_tables, excel_path)
    else:
        print("No text or tables extracted from the file.")

# Example Usage
file_path = r"D:\Excelmate AI\dataset\Student_performance_data _.csv"  # Change to your file
excel_path = r"D:\Excelmate AI\output.xlsx"
extract_and_save(file_path, excel_path)
