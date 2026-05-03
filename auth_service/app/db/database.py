from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from fastapi import Request

load_dotenv()

DATABASE_URL=os.getenv("DATABASE_URL")

if DATABASE_URL.startswith("sqlite"):
    engine=create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine=create_engine(DATABASE_URL)

SessionLocal=sessionmaker(autocommit=False, autoflush=False, bind=engine)
async def login_google(request : Request):
    redirect_uri=request.url_for("auth_google")
    return await oauth.google.authorize_redirect(request, redirect_uri)

Base=declarative_base()

