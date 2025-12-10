from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Dict, Any

from .models import File

def get_latest_file_version(db: Session, original_name: str) -> File | None:
    return db.query(File).filter(
        File.original_name == original_name
    ).order_by(
        desc(File.version)
    ).first()

def create_file(db: Session, file_data: Dict[str, Any]) -> File:
    db_file = File(**file_data)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

def get_file_by_id(db: Session, file_id: int) -> File | None:
    return db.query(File).filter(File.id == file_id).first()

def update_file(db: Session, db_file: File, update_data: Dict[str, Any]) -> File:
    for key, value in update_data.items():
        setattr(db_file, key, value)
    db.commit()
    db.refresh(db_file)
    return db_file