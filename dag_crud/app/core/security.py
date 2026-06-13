from dotenv import load_dotenv
import os
from jose import JWTError, jwt


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

def verify_token(token :str):
    try:
        payload = jwt.decode(
            token,SECRET_KEY,algorithms=[ALGORITHM]
        )
        return payload
    except JWTError:
        return None