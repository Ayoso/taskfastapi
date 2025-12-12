from pydantic import BaseModel
from datetime import datetime


class FileUploadResponse(BaseModel):
    id: int
    original_name: str
    version: int
    size_bytes: int
    message: str


class FileListElement(BaseModel):
    id: int
    file_name: str  
    version: int    
    upload_date: datetime 
    size_bytes: int 

# Схема для ответа анализа
class FileAnalysisResponse(BaseModel):
    file_id: int
    original_name: str
    version: int
    status: str
    ai_comment: str | None = None
    analysis_updated_at: datetime | None = None


    class Config:
        from_attributes = True