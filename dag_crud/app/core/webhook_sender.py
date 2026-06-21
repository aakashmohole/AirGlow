import requests

def send_webhook(
        url,
        payload
):
    requests.post(
        url,
        json=payload
    )