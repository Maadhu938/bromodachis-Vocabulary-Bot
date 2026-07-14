import os
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.models.vocabulary import Vocabulary


class VocabularyService:
    def __init__(self, db: Session):
        self.db = db

    def get_next_words_for_user(self, learned_ids: List[int], limit: int = None) -> List[Vocabulary]:
        """Get next words for a specific user (excluding already learned)"""
        if limit is None:
            limit = int(os.getenv("WORDS_PER_DAY", 10))
        
        query = self.db.query(Vocabulary)
        
        if learned_ids:
            query = query.filter(~Vocabulary.id.in_(learned_ids))
        
        next_words = (
            query.order_by(Vocabulary.id)
            .limit(limit)
            .all()
        )
        return next_words

    def get_random_words(self, limit: int = 10, exclude_ids: List[int] = None) -> List[Vocabulary]:
        """Get random words for quiz generation"""
        query = self.db.query(Vocabulary)
        
        if exclude_ids:
            query = query.filter(~Vocabulary.id.in_(exclude_ids))
        
        return query.order_by(func.random()).limit(limit).all()

    def get_word_by_id(self, word_id: int) -> Vocabulary:
        """Get a specific word by ID"""
        return self.db.query(Vocabulary).filter(Vocabulary.id == word_id).first()

    def get_daily_words(self, telegram_id: int, limit: int = 10) -> List[Vocabulary]:
        """Get daily words for a user (alias for get_next_words_for_user)"""
        from app.models.user import User
        from app.services.user_service import UserService
        
        user_service = UserService(self.db)
        user = user_service.get_user_by_telegram_id(telegram_id)
        
        if not user:
            return []
        
        learned_ids = user_service.get_learned_word_ids(user)
        return self.get_next_words_for_user(learned_ids, limit=limit)
