from fastapi import Header , HTTPException, Depends
from app.core.security import verify_token
from jose import jwt, JWTError
from dotenv import load_dotenv
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    print("TOKEN:", token)

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        print("PAYLOAD:", payload)
        return payload

    except Exception as e:
        print(credentials)
        print("JWT ERROR:", e)
        raise HTTPException(
            status_code=401,
            detail=str(e)
        )