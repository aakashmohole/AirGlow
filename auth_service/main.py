from fastapi import FastAPI
from routers import router
from database import engine,Base
import models 
from starlette.middleware.sessions import SessionMiddleware
import os


Base.metadata.create_all(bind=engine)


app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY")
)

app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)