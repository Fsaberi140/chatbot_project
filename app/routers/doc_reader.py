from fastapi import APIRouter, UploadFile
from app.db import db
from PyPDF2 import PdfReader
import docx

router = APIRouter()

def extract_text_from_pdf(file):
    reader = PdfReader(file)
    return "\n".join(page.extract_text() for page in reader.pages)

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join(para.text for para in doc.paragraphs)

@router.post("/upload-doc/")
async def upload_document(file: UploadFile):
    if file.filename.endswith(".pdf"):
        content = extract_text_from_pdf(file.file)
    elif file.filename.endswith(".docx"):
        content = extract_text_from_docx(file.file)
    else:
        return {"error": "Unsupported file format"}

    db.documents.insert_one({"name": file.filename, "content": content})

    return {"message": "Document uploaded successfully"}
