from fastapi import FastAPI
from routers import router
from database import engine,Base
import models 



Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)