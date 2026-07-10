import os
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from typing import List

from app.models.vocabulary import Vocabulary
from app.models.sent_words import SentWords

class VocabularyService:
    def __init__(self, db: Session):
        self.db = db

    def get_next_words(self, limit: int = None) -> List[Vocabulary]:
        if limit is None:
            limit = int(os.getenv("WORDS_PER_DAY", 5))
        sent_query = self.db.query(SentWords.vocabulary_id)
        next_words = (
            self.db.query(Vocabulary)
            .filter(~Vocabulary.id.in_(sent_query))
            .order_by(Vocabulary.id)
            .limit(limit)
            .all()
        )
        return next_words

    def mark_as_sent(self, vocab_ids: List[int]) -> int:
        if not vocab_ids:
            return 0
            
        max_batch = self.db.query(func.max(SentWords.batch_number)).scalar()
        next_batch = (max_batch or 0) + 1
        today = date.today()
        
        for v_id in vocab_ids:
            sent_word = SentWords(
                vocabulary_id=v_id,
                sent_date=today,
                batch_number=next_batch
            )
            self.db.add(sent_word)
            
        self.db.commit()
        return next_batch

    def reset_progress(self):
        self.db.query(SentWords).delete()
        self.db.commit()
        
    def get_progress_stats(self) -> dict:
        total_words = self.db.query(Vocabulary).count()
        sent_words = self.db.query(func.count(func.distinct(SentWords.vocabulary_id))).scalar()
        
        return {
            "total_words": total_words,
            "sent_words": sent_words,
            "remaining_words": total_words - sent_words
        }
