from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from app.db.database import SessionLocal
from jose import JWTError, jwt
from fastapi.responses import RedirectResponse
import app.schemas.user as schema
import app.models.user as models
from app.core.security import hash_password, verify_password, create_access_token
from dotenv import load_dotenv
from app.core.security import oauth
import os

router=APIRouter()
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=schema.UserResponse)
async def register(user:schema.UserCreate,db=Depends(get_db)):
    new_user=models.User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


#authentication
@router.post("/login")
async def login(user:schema.UserCreate, db=Depends(get_db)):
    db_user=db.query(models.User).filter(models.User.username==user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    
    token=create_access_token(data={"sub":db_user.username})
    return {"access_token":token}
    
    
#authorization
oauth2_scheme=OAuth2PasswordBearer(tokenUrl="login")
async def get_current_user(token:str=Depends(oauth2_scheme)):
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=ALGORITHM)
        username:str=payload.get("sub")
        if username is None:    
            raise HTTPException(status_code=401, detail="Invalid Credentials")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid Credentials")



@router.get("/auth/google")
async def auth_google(request : Request):
    token= await oauth.google.authorize_access_token(request)
    user_info=token.get("userinfo")
    jwt_token=create_access_token(data={"sub":user_info.get("email")})
    return {
        "provider":"Google",
        "user":user_info,
        "access_token":jwt_token
    }

@router.get("/login/google")
async def login_google(request : Request):
    redirect_uri=request.url_for("auth_google")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/auth/github")
async def auth_github(request:Request):
    token=await oauth.github.authorize_access_token(request)
    resp = await oauth.github.get("user", token=token)
    user_info = resp.json()
    jwt_token=create_access_token(data={"sub":user_info.get("email") or user_info.get("login")})
    return {
        "provider":"Github",
        "user":user_info,
        "access_token":jwt_token
    }

@router.get("/login/github")
async def login_github(request:Request):
    redirect_uri=request.url_for("auth_github")
    return await oauth.github.authorize_redirect(request, redirect_uri)

