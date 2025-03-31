from pydantic import BaseModel
from typing import List, Dict, Any

class APIEndpoint(BaseModel):
    method: str  # مثل GET، POST
    url: str  # مثل /app/createUser/
    parameters: Dict[str, Any]  # پارامترهای مورد نیاز
    headers: Dict[str, str] = {}  # هدرها

class APIDocument(BaseModel):
    name: str
    base_url: str
    endpoints: List[APIEndpoint]

