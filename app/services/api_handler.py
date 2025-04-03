import requests
from fastapi import HTTPException

async def process_api_request(endpoint: dict, user_data: dict):
    """
    پردازش و ارسال درخواست به یک API مشخص
    :param endpoint: اطلاعات مربوط به API هدف
    :param user_data: داده‌های ورودی که کاربر ارائه کرده است
    :return: پاسخ API
    """
    url = endpoint.get("full_url") or f"{endpoint['base_url']}{endpoint['url']}"
    method = endpoint["method"].upper()
    headers = endpoint.get("headers", {})

    # بررسی توکن احراز هویت (در صورت وجود)
    if "Authorization" in endpoint:
        headers["Authorization"] = endpoint["Authorization"]

    try:
        # ارسال درخواست به API با توجه به متد
        if method == "GET":
            response = requests.get(url, params=user_data, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=user_data, headers=headers, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json=user_data, headers=headers, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        else:
            raise HTTPException(status_code=400, detail="متد نامعتبر است.")

        # مدیریت ارورهای HTTP
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.json())

        return response.json()

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"خطا در ارتباط با API: {str(e)}")
