from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.db import db
import os
import asyncio

# مقداردهی اولیه (بارگذاری فقط یک‌بار)
vector_store = None


async def initialize_vector_store():
    """ایجاد و ذخیره FAISS در صورت عدم وجود"""
    global vector_store
    documents = await db.documents.find().to_list(length=None)  # دریافت اسناد به‌صورت async
    all_texts = [doc["content"] for doc in documents]

    if not all_texts:
        return None

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.create_documents(all_texts)

    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
    vector_store = FAISS.from_documents(docs, embeddings)

    # ذخیره FAISS در دیسک برای جلوگیری از پردازش مجدد
    vector_store.save_local("faiss_index")
    return vector_store


async def load_vector_store():
    """لود FAISS از دیسک، در صورت نبود ایجاد مجدد"""
    global vector_store
    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

    try:
        vector_store = FAISS.load_local("faiss_index", embeddings)
    except FileNotFoundError:
        vector_store = await initialize_vector_store()
    except Exception as e:
        print(f"خطا در لود FAISS: {e}")
        vector_store = None


async def answer_question(question: str):
    """پاسخ‌دهی به سوالات کاربران از روی داکیومنت‌های پردازش‌شده"""
    global vector_store
    if vector_store is None:
        await load_vector_store()

    # چک کردن دوباره بعد از لود کردن
    if vector_store is None:
        return "خطا: سیستم پردازش اسناد آماده نیست. لطفاً بعداً تلاش کنید."

    try:
        retriever = vector_store.as_retriever()
        qa_chain = RetrievalQA.from_chain_type(
            llm=ChatOpenAI(model_name="gpt-4", openai_api_key=os.getenv("OPENAI_API_KEY")),
            retriever=retriever
        )
        return await asyncio.to_thread(qa_chain.run, question)
    except Exception as e:
        return f"خطا در پردازش سوال: {str(e)}"