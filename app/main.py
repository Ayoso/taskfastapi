from fastapi import FastAPI
from . import models
from .database import engine
from .api import router as file_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Document Versioning and AI Analysis Service",
    description="Мини-сервис для хранения документов с версияцией, метаданными и базовым AI-анализом.",
    version="1.0.0"
)

app.include_router(file_router, prefix="/files", tags=["Files and Analysis"])

@app.get("/", include_in_schema=False)
def read_root():
    return {"message": "Welcome to the Document Service. Check /docs for API details."}