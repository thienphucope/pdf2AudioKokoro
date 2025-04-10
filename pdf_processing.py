import fitz  # PyMuPDF
import os
import re

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file using PyMuPDF."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def standardize_text(text):
    """Standardizes text by cleaning and normalizing it."""
    # Remove non-standard characters
    text = re.sub(r'[^\w\s.,!?\'"-]', '', text)
    # Normalize whitespace
    text = " ".join(text.split())
    # Join broken lines
    lines = text.splitlines()
    standardized_lines = []
    for line in lines:
        line = line.strip()
        if line:
            if not line.endswith(('.', '!', '?')) and standardized_lines:
                standardized_lines[-1] += " " + line
            else:
                standardized_lines.append(line)
    return " ".join(standardized_lines)

def save_text(text, output_path):
    """Saves text to a file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(text)

def process_pdf(input_path, output_path):
    """Processes a PDF and saves standardized text."""
    raw_text = extract_text_from_pdf(input_path)
    standardized = standardize_text(raw_text)
    save_text(standardized, output_path)
    return standardized