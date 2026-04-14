import PyPDF2
import re

def extract_text_from_pdf(pdf_file):
    """
    Extracts text from an uploaded PDF file using PyPDF2.
    
    Args:
        pdf_file: Uploaded file object (from Streamlit)
        
    Returns:
        str: Extracted text from all pages
    """
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        # Iterate through all the pages and append their text
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text() + " "
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""
    
    return text

def clean_text(text):
    """
    Performs basic text cleaning.
    Removes special characters, converts to lowercase, and normalizes space.
    
    Args:
        text (str): Raw extracted text
        
    Returns:
        str: Cleaned text
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove special characters and punctuation (keep alphanumeric and spaces)
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

from fpdf import FPDF
import os

def generate_pdf_report(score, present_skills, missing_skills, target_role, suggestions):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="AI Resume ATS Analysis Report", ln=1, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=f"Target Role: {target_role}", ln=1)
    pdf.cell(200, 10, txt=f"ATS Score: {score}%", ln=1)
    pdf.ln(10)
    
    pdf.cell(200, 10, txt="Identified Skills:", ln=1)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 8, txt=", ".join(present_skills).title() if present_skills else "None")
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Missing Critical Skills:", ln=1)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 8, txt=", ".join(missing_skills).title() if missing_skills else "None")
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Improvement Suggestions:", ln=1)
    pdf.set_font("Arial", size=10)
    for i, sug in enumerate(suggestions, 1):
        safe_sug = sug.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 8, txt=f"{i}. {safe_sug}")
        
    report_path = "ATS_Report.pdf"
    pdf.output(report_path)
    return report_path
