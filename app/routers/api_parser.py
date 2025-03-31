from fastapi import APIRouter, UploadFile
import json
from app.models.api import APIDocument, APIEndpoint
from app.db import db

router = APIRouter()

@router.post("/upload-api/")
async def upload_api(file: UploadFile):
    content = await file.read()
    api_data = json.loads(content)

    base_url = api_data.get("servers", [{}])[0].get("url", "")
    endpoints = []

    for path, methods in api_data.get("paths", {}).items():
        for method, details in methods.items():
            endpoints.append(APIEndpoint(
                method=method.upper(),
                url=path,
                parameters=details.get("parameters", []),
                headers={}
            ))

    api_doc = APIDocument(name=file.filename, base_url=base_url, endpoints=endpoints)
    db.api.insert_one(api_doc.model_dump())

    return {"message": "API document uploaded successfully"}
