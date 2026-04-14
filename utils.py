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
