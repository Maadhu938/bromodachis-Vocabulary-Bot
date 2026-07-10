from sqlalchemy import Column, Integer, String, Date, ForeignKey
from app.database.connection import Base

class SentWords(Base):
    __tablename__ = "sent_words"

    id = Column(Integer, primary_key=True, index=True)
    vocabulary_id = Column(Integer, ForeignKey("vocabulary.id"))
    sent_date = Column(Date, index=True)
    batch_number = Column(Integer)
