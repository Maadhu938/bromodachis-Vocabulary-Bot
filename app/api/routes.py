from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database.connection import get_db
from app.services.vocabulary import VocabularyService
from app.services.formatter import MessageFormatter
from app.messaging.whatsapp import WhatsAppMessagingService

router = APIRouter()
messaging_service = WhatsAppMessagingService()

@router.get("/today")
def get_today_words(db: Session = Depends(get_db)):
    vocab_service = VocabularyService(db)
    words = vocab_service.get_next_words()
    return {"words": words}

@router.post("/send")
def send_daily_vocabulary(db: Session = Depends(get_db)):
    vocab_service = VocabularyService(db)
    
    # 1. Get words
    words = vocab_service.get_next_words()
    if not words:
        return {"status": "error", "message": "No more words to send!"}
        
    # 2. Mark as sent to get batch number
    word_ids = [w.id for w in words]
    batch_number = vocab_service.mark_as_sent(word_ids)
    
    # 3. Format message
    message = MessageFormatter.format_daily_message(batch_number, words)
    
    # 4. Send message
    messaging_service.send_message(message)
    
    return {"status": "success", "batch_number": batch_number, "sent_count": len(words)}

@router.post("/reset")
def reset_progress(db: Session = Depends(get_db)):
    vocab_service = VocabularyService(db)
    vocab_service.reset_progress()
    return {"status": "success", "message": "Progress reset to beginning."}

@router.get("/progress")
def get_progress(db: Session = Depends(get_db)):
    vocab_service = VocabularyService(db)
    return vocab_service.get_progress_stats()
