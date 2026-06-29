import requests

def send_webhook(
        url,
        payload
):
    requests.post(
        url=url,
        json=payload,
        timeout=5
    )