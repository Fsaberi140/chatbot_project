from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import api_parser, doc_reader, chat
import os

# ایجاد نمونه‌ای از FastAPI
app = FastAPI(
    title="Smart ChatBot API",
    description="یک چت‌بات هوشمند که APIهای Swagger و اسناد را پردازش می‌کند.",
    version="1.0.0"
)

# تنظیم CORS برای دسترسی کلاینت‌های مختلف
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # در محیط تولید باید فقط به دامنه‌های مشخصی اجازه دهید.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# اضافه کردن مسیرهای مختلف
app.include_router(api_parser.router, prefix="/api", tags=["API Processing"])
app.include_router(doc_reader.router, prefix="/docs", tags=["Document Processing"])
app.include_router(chat.router, prefix="/chat", tags=["Chatbot"])

# مسیر اصلی برای نمایش پیام خوش‌آمدگویی
@app.get("/")
def read_root():
    return {"message": "Welcome to Smart ChatBot API 🚀"}

# راه‌اندازی سرور (اگر مستقیم اجرا شود)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
