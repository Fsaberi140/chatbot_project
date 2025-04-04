from fastapi import APIRouter, UploadFile, HTTPException
from app.db import db
from PyPDF2 import PdfReader
import docx
import tempfile
import os

router = APIRouter()

async def extract_text_from_pdf(file_path: str) -> str:
    try:
        reader = PdfReader(file_path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"خطا در خواندن PDF: {str(e)}")

async def extract_text_from_docx(file_path: str) -> str:
    try:
        doc = docx.Document(file_path)
        return "\n".join(para.text for para in doc.paragraphs)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"خطا در خواندن Word: {str(e)}")

@router.post("/upload-doc/")
async def upload_document(file: UploadFile):
    if not file.filename.endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="فقط فایل‌های PDF و DOCX مجاز هستند.")

    # ذخیره فایل موقتی برای استفاده توسط کتابخانه‌ها
    suffix = ".pdf" if file.filename.endswith(".pdf") else ".docx"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        temp_path = tmp.name
        content = await file.read()
        tmp.write(content)

    try:
        if file.filename.endswith(".pdf"):
            extracted_text = await extract_text_from_pdf(temp_path)
        else:
            extracted_text = await extract_text_from_docx(temp_path)
    finally:
        os.remove(temp_path)  # پاک کردن فایل موقتی

    if not extracted_text.strip():
        raise HTTPException(status_code=400, detail="محتوایی در فایل یافت نشد.")

    await db.documents.insert_one({
        "name": file.filename,
        "content": extracted_text
    })

    return {"message": "فایل با موفقیت آپلود و ذخیره شد"}
