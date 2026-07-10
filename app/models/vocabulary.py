from sqlalchemy import Column, Integer, String
from app.database.connection import Base

class Vocabulary(Base):
    __tablename__ = "vocabulary"

    id = Column(Integer, primary_key=True, index=True)
    expression = Column(String, index=True)
    reading = Column(String)
    meaning = Column(String)
    tags = Column(String)
