from fastapi import APIRouter, UploadFile, File as FFile, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pathlib import Path
from datetime import datetime
import os
import shutil
   
from fastapi.responses import FileResponse 
from .database import get_db
from .models import File
from .crud import (
    get_latest_file_version, 
    create_file, 
    get_file_by_id, 
    update_file
)
from .ai_mock import analyze_document_mock

router = APIRouter()

STORAGE_DIR = Path("./storage")
STORAGE_DIR.mkdir(exist_ok=True)


from fastapi import APIRouter, UploadFile, File as FFile, Depends, HTTPException, status


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = FFile(..., description="PDF / DOCX / PNG - любой формат файла"),
    db: Session = Depends(get_db)
):
    
    original_name = file.filename
    if not original_name:
        raise HTTPException(status_code=400, detail="Filename is required")

    latest_version_entry = get_latest_file_version(db, original_name)
    new_version = (latest_version_entry.version + 1) if latest_version_entry else 1

    extension = original_name.split(".")[-1] if "." in original_name else "dat"
   
    base_name = original_name.rsplit(".", 1)[0]
    unique_filename = f"{base_name}_v{new_version}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{extension}"
    file_path = STORAGE_DIR / unique_filename

    try:
        file.file.seek(0, os.SEEK_END)
        file_size_bytes = file.file.tell() 
        file.file.seek(0) 
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
    except Exception as e:
        print(f"File saving error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file to disk: {e}"
        )

    db_file = create_file(db, {
        "original_name": original_name,
        "file_name_on_disk": unique_filename,
        "version": new_version,
        "path": str(file_path),
        "uploaded_by": 1,
        "file_size_bytes": file_size_bytes
    })

    return {
        "id": db_file.id,
        "original_name": db_file.original_name,
        "version": db_file.version,
        "size_bytes": db_file.file_size_bytes,
        "message": f"File uploaded and saved as version {new_version}"
    }

@router.get("/", response_model=list)
def list_files(db: Session = Depends(get_db)):
  
    from sqlalchemy import func, desc
    
    subquery = db.query(
        File.original_name,
        func.max(File.version).label('max_version')
    ).group_by(File.original_name).subquery()

    latest_files = db.query(File).join(
        subquery,
        (File.original_name == subquery.c.original_name) &
        (File.version == subquery.c.max_version)
    ).order_by(
        desc(File.uploaded_at)
    ).all()

    result = [
        {
            "id": f.id,
            "имя_файла": f.original_name,
            "версия": f.version,
            "дата_загрузки": f.uploaded_at.isoformat(),
            "размер_байты": f.file_size_bytes,
        }
        for f in latest_files
    ]
    return result

@router.post("/{file_id}/analyze")
def analyze_file(file_id: int, db: Session = Depends(get_db)):
    db_file = get_file_by_id(db, file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail=f"File with id {file_id} not found")

    metadata = {
        "original_name": db_file.original_name,
        "file_size_bytes": db_file.file_size_bytes,
        "version": db_file.version,
        "uploaded_at": db_file.uploaded_at.isoformat(),
    }

    ai_comment = analyze_document_mock(metadata)

    db_file = update_file(db, db_file, {
        "analysis_result": ai_comment,
        "analysis_updated_at": datetime.utcnow()
    })

    return {
        "file_id": db_file.id,
        "original_name": db_file.original_name,
        "version": db_file.version,
        "status": "Analysis complete and result saved",
        "ai_comment": ai_comment
    }

@router.get("/{file_id}/analysis")
def get_file_analysis(file_id: int, db: Session = Depends(get_db)):
    db_file = get_file_by_id(db, file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail=f"File with id {file_id} not found")

    if not db_file.analysis_result:
        return {
            "file_id": file_id,
            "original_name": db_file.original_name,
            "version": db_file.version,
            "status": "Analysis not performed yet or result is empty",
            "result": None
        }

    return {
        "file_id": db_file.id,
        "original_name": db_file.original_name,
        "version": db_file.version,
        "analysis_updated_at": db_file.analysis_updated_at.isoformat() if db_file.analysis_updated_at else None,
        "result": db_file.analysis_result
    }

@router.get("/{file_id}/download")
def download_file(file_id: int, db: Session = Depends(get_db)):
    db_file = get_file_by_id(db, file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail=f"File with id {file_id} not found")
    
    file_path = Path(db_file.path)
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File content not found on disk")
    
    return FileResponse(
        path=file_path, 
        filename=db_file.original_name, 
        media_type='application/octet-stream'
    )