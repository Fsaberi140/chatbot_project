from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.db import db
import os


def answer_question(question: str):
    documents = db.documents.find()
    all_texts = [doc["content"] for doc in documents]

    if not all_texts:
        return "هیچ داکیومنتی در پایگاه داده یافت نشد."

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.create_documents(all_texts)

    if not docs:
        return "هیچ متنی برای پردازش وجود ندارد."

    try:
        embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
        vector_store = FAISS.from_documents(docs, embeddings)
        if vector_store is None:
            return "خطا در ایجاد vector store"
    except Exception as e:
        return f"خطا در ساخت embedding یا vectorstore: {str(e)}"

    try:
        retriever = vector_store.as_retriever()
        qa_chain = RetrievalQA.from_chain_type(
            llm=ChatOpenAI(model_name="gpt-4", openai_api_key=os.getenv("OPENAI_API_KEY")),
            retriever=retriever
        )
        response = qa_chain.run(question)
        return response
    except Exception as e:
        return f"خطا در اجرای مدل پرسش‌وپاسخ: {str(e)}"
