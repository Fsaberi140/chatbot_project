from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.db import db
import os



def answer_question(question: str):
    # دریافت داکیومنت‌های ذخیره شده از دیتابیس
    documents = db.documents.find()
    all_texts = [doc["content"] for doc in documents]

    if not all_texts:
        return "هیچ داکیومنتی در پایگاه داده یافت نشد."

    # تقسیم‌بندی متن برای جلوگیری از محدودیت طول ورودی مدل
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.create_documents(all_texts)

    # تبدیل متن به بردارهای عددی با استفاده از OpenAI
    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
    vector_store = FAISS.from_documents(docs, embeddings)

    # ایجاد مدل پرسش و پاسخ
    retriever = vector_store.as_retriever()
    qa_chain = RetrievalQA.from_chain_type(llm=ChatOpenAI(model_name="gpt-4", openai_api_key=os.getenv("OPENAI_API_KEY")),
                                           retriever=retriever)

    # پاسخ دادن به سوال کاربر
    response = qa_chain.run(question)
    return response
