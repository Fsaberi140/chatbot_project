from pydantic import BaseModel
from typing import List


class Document(BaseModel):
    name: str
    content: str  # محتوای داکیومنت
    embeddings: List[float]  # برای جستجو در متن
