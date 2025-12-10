import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, func
from .database import Base

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    
    original_name = Column(String, index=True, nullable=False) 
    
    file_name_on_disk = Column(String, unique=True, nullable=False)
    
    version = Column(Integer, default=1, nullable=False)
    path = Column(String, nullable=False) 
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
    uploaded_by = Column(Integer, default=1) 
    file_size_bytes = Column(Integer)
    
    analysis_result = Column(Text, nullable=True)
    analysis_updated_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<File(id={self.id}, original_name='{self.original_name}', version={self.version})>"