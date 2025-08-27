import spacy
import re
from docx import Document
from io import BytesIO

nlp = spacy.load("en_core_web_sm")

SSN_PATTERN = r"\b\d{3}-\d{2}-\d{4}\b"
CREDIT_CARD_PATTERN = r"\b(?:\d[ -]*?){13,16}\b"
BANK_ACCOUNT_PATTERN = r"\b\d{6,12}\b"
PHONE_PATTERN = r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"

def redact_text(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "GPE", "ORG", "DATE", "MONEY"]:
            text = text.replace(ent.text, "[REDACTED]")
    text = re.sub(SSN_PATTERN, "[REDACTED]", text)
    text = re.sub(CREDIT_CARD_PATTERN, "[REDACTED]", text)
    text = re.sub(BANK_ACCOUNT_PATTERN, "[REDACTED]", text)
    text = re.sub(PHONE_PATTERN, "[REDACTED]", text)
    return text

def redact_docx(file_stream):
    doc = Document(file_stream)
    for para in doc.paragraphs:
        para.text = redact_text(para.text)
    out_stream = BytesIO()
    doc.save(out_stream)
    out_stream.seek(0)
    return out_stream

def redact_pdf(file_stream):
    import pdfplumber
    redacted_text = ""
    with pdfplumber.open(file_stream) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            redacted_text += redact_text(text) + "\n"
    return redacted_text
