import requests


def call_api(base_url: str, endpoint: dict, user_data: dict):
    url = f"{base_url}{endpoint['url']}"
    method = endpoint["method"]
    headers = endpoint.get("headers", {})

    if method == "GET":
        response = requests.get(url, params=user_data, headers=headers)
    else:
        response = requests.post(url, json=user_data, headers=headers)

    return response.json()
