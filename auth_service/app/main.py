from fastapi import FastAPI
from app.api.routes import router
from app.db.database import engine, Base
import app.models.user as models
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
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)