import requests

def send_webhook(
        callback_url:str,
        payload:dict
):
    try:
        response= requests.post(
            callback_url,
            json=payload,
            timeout=10
        )
        response.raise_for_status()

        return True
    
    except requests.RequestException as e:
        print("Webhook Error : ",e)
        return False