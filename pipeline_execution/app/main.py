from fastapi import FastAPI

from app.api.steps_routes import router as steps_router


app = FastAPI()

app.include_router(steps_router)