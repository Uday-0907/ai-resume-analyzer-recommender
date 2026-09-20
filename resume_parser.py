import io
from pypdf import PdfReader
from docx import Document

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extracts text page by page from a PDF file."""
    reader = PdfReader(io.BytesIO(file_bytes))
    extracted_text = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            extracted_text.append(text)
    return " ".join(extracted_text)

def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extracts text paragraph by paragraph from a DOCX file."""
    doc = Document(io.BytesIO(file_bytes))
    extracted_text = [p.text for p in doc.paragraphs if p.text.strip()]
    return " ".join(extracted_text)

def parse_resume(uploaded_file) -> str:
    """Routes uploaded file to correct parser based on extension."""
    file_bytes = uploaded_file.read()
    if uploaded_file.name.endswith('.pdf'):
        return extract_text_from_pdf(file_bytes)
    elif uploaded_file.name.endswith('.docx'):
        return extract_text_from_docx(file_bytes)
    else:
        raise ValueError("Unsupported file format. Please upload PDF or DOCX.")