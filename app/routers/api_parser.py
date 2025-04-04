import json
from typing import List
from fastapi import APIRouter, UploadFile, HTTPException
from app.db import db
from app.models.api import APIDocument, APIEndpoint

router = APIRouter()


@router.post("/upload-api/")
async def upload_api(file: UploadFile):
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="فقط فایل‌های JSON مجاز هستند.")

    content = await file.read()

    try:
        api_data = json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="فرمت JSON معتبر نیست.")

    base_url = api_data.get("servers", [{}])[0].get("url", "")
    paths = api_data.get("paths", {})

    endpoints: List[APIEndpoint] = []

    for path, methods in paths.items():
        for method, details in methods.items():
            parameters = details.get("parameters", [])
            headers = {}

            # اگر هدرها در پارامترها بودند
            for param in parameters:
                if param.get("in") == "header":
                    headers[param["name"]] = param.get("default", "")

            endpoint = APIEndpoint(
                method=method.upper(),
                url=path,
                parameters=parameters,
                headers=headers
            )
            endpoints.append(endpoint)

    api_doc = APIDocument(
        name=file.filename,
        base_url=base_url,
        endpoints=endpoints
    )

    await db.api.insert_one(api_doc.model_dump())

    return {"message": "API document uploaded successfully"}
