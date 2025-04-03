from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.doc_handler import answer_question
from app.services.api_handler import process_api_request
from app.db import db
import asyncio

router = APIRouter()


# مدل درخواست برای دریافت سوال کاربر
class ChatRequest(BaseModel):
    question: str
    params: dict = None  # در صورتی که سوال نیاز به پارامترهای اضافی داشته باشد


async def fetch_api_data(question: str):
    """بررسی اینکه آیا سوال به APIهای موجود مرتبط است یا نه"""
    api_docs = await db.api.find().to_list(length=None)  # دریافت تمام APIها
    for api_doc in api_docs:
        for endpoint in api_doc["endpoints"]:
            if endpoint["url"].lower() in question:
                return endpoint  # اگر API مرتبط پیدا شد، آن را برگردان
    return None


@router.post("/")
async def chat(request: ChatRequest):
    question = request.question.strip().lower()

    # موازی‌سازی پردازش API و جستجو در اسناد
    api_task = fetch_api_data(question)
    doc_task = asyncio.create_task(answer_question(question))

    api_endpoint = await api_task

    # اگر سوال به API مربوط باشد
    if api_endpoint:
        if not request.params:
            return {"message": "لطفاً پارامترهای موردنیاز را ارسال کنید.", "required_params": api_endpoint["params"]}

        response = await process_api_request(api_endpoint, request.params)
        return {"answer": response}

    # اگر سوال مربوط به اسناد باشد
    response = await doc_task
    if not response:
        raise HTTPException(status_code=404, detail="متاسفم، پاسخی پیدا نشد.")

    return {"answer": response}
