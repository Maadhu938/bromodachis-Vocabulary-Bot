"""Admin service for managing the bot"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models.user import User, UserWord, QuizResult
from app.models.vocabulary import Vocabulary


class AdminService:
    """Admin management service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def is_admin(self, telegram_id: int, admin_ids: List[int]) -> bool:
        """Check if user is admin"""
        return telegram_id in admin_ids
    
    def get_all_users(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get all registered users"""
        users = self.db.query(User).order_by(desc(User.created_at)).limit(limit).offset(offset).all()
        
        result = []
        for user in users:
            result.append({
                "id": user.id,
                "telegram_id": user.telegram_id,
                "username": user.username,
                "first_name": user.first_name,
                "level": user.level,
                "xp": user.xp,
                "current_streak": user.current_streak,
                "total_words_learned": user.total_words_learned,
                "created_at": user.created_at,
                "last_active_date": user.last_active_date
            })
        return result
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by database ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID"""
        return self.db.query(User).filter(User.telegram_id == telegram_id).first()
    
    def get_bot_statistics(self) -> Dict:
        """Get overall bot statistics"""
        # User stats
        total_users = self.db.query(User).count()
        active_today = self.db.query(User).filter(
            User.last_active_date == datetime.now().date()
        ).count()
        active_this_week = self.db.query(User).filter(
            User.last_active_date >= (datetime.now().date() - timedelta(days=7))
        ).count()
        
        # Learning stats
        total_words_learned = self.db.query(func.sum(User.total_words_learned)).scalar() or 0
        total_quizzes_taken = self.db.query(func.sum(User.total_quizzes_taken)).scalar() or 0
        
        # Quiz accuracy
        total_quiz_answers = self.db.query(QuizResult).count()
        correct_answers = self.db.query(QuizResult).filter(QuizResult.correct == True).count()
        overall_accuracy = round((correct_answers / total_quiz_answers) * 100, 1) if total_quiz_answers > 0 else 0
        
        # Top users
        top_users = self.db.query(User).order_by(desc(User.xp)).limit(5).all()
        
        # Level distribution
        level_distribution = {}
        for level in range(1, 11):
            count = self.db.query(User).filter(User.level == level).count()
            if count > 0:
                level_distribution[level] = count
        
        return {
            "users": {
                "total": total_users,
                "active_today": active_today,
                "active_this_week": active_this_week
            },
            "learning": {
                "total_words_learned": total_words_learned,
                "total_quizzes_taken": total_quizzes_taken,
                "overall_accuracy": overall_accuracy
            },
            "top_users": [
                {
                    "telegram_id": u.telegram_id,
                    "username": u.username or u.first_name,
                    "xp": u.xp,
                    "level": u.level
                } for u in top_users
            ],
            "level_distribution": level_distribution
        }
    
    def broadcast_message(self, message: str, admin_id: int) -> Dict:
        """Broadcast message to all users"""
        users = self.db.query(User).all()
        
        successful = 0
        failed = 0
        failed_users = []
        
        # Note: Actual sending happens in the bot handler
        # This just prepares the list
        return {
            "total_users": len(users),
            "message": message,
            "admin_id": admin_id,
            "user_ids": [u.telegram_id for u in users]
        }
    
    def get_user_details(self, user_id: int) -> Optional[Dict]:
        """Get detailed info about a specific user"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        # Get learned words
        learned_words = self.db.query(Vocabulary).join(
            UserWord, Vocabulary.id == UserWord.vocabulary_id
        ).filter(UserWord.user_id == user.id).all()
        
        # Get quiz stats
        quiz_stats = self.db.query(
            func.count(QuizResult.id).label('total'),
            func.sum(QuizResult.correct.cast()).label('correct')
        ).filter(QuizResult.user_id == user.id).first()
        
        return {
            "user_info": {
                "id": user.id,
                "telegram_id": user.telegram_id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "created_at": user.created_at,
                "last_active": user.last_active_date
            },
            "gamification": {
                "level": user.level,
                "level_title": user.get_level_title(),
                "xp": user.xp,
                "current_streak": user.current_streak,
                "longest_streak": user.longest_streak
            },
            "learning": {
                "words_learned": user.total_words_learned,
                "quizzes_taken": user.total_quizzes_taken,
                "quiz_accuracy": round((quiz_stats.correct / quiz_stats.total) * 100, 1) if quiz_stats.total else 0
            },
            "recent_words": [
                {"expression": w.expression, "reading": w.reading, "meaning": w.meaning}
                for w in learned_words[-10:]  # Last 10 words
            ]
        }
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user and all their data"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        # Delete related data
        self.db.query(UserWord).filter(UserWord.user_id == user.id).delete()
        self.db.query(QuizResult).filter(QuizResult.user_id == user.id).delete()
        
        # Delete user
        self.db.delete(user)
        self.db.commit()
        return True
    
    def add_xp_to_user(self, user_id: int, xp_amount: int, reason: str = "") -> bool:
        """Add XP to a specific user (admin reward)"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        from app.utils.constants import LEVEL_THRESHOLDS
        
        old_level = user.level
        user.xp += xp_amount
        
        # Check for level up
        for level, threshold in sorted(LEVEL_THRESHOLDS.items()):
            if user.xp >= threshold and level > user.level:
                user.level = level
        
        self.db.commit()
        
        return {
            "success": True,
            "xp_added": xp_amount,
            "new_total_xp": user.xp,
            "old_level": old_level,
            "new_level": user.level,
            "leveled_up": user.level > old_level
        }
    
    def get_inactive_users(self, days: int = 7) -> List[Dict]:
        """Get users who haven't been active for X days"""
        cutoff_date = datetime.now().date() - timedelta(days=days)
        
        inactive_users = self.db.query(User).filter(
            (User.last_active_date < cutoff_date) | (User.last_active_date.is_(None))
        ).all()
        
        return [
            {
                "telegram_id": u.telegram_id,
                "username": u.username,
                "first_name": u.first_name,
                "last_active": u.last_active_date,
                "days_inactive": (datetime.now().date() - (u.last_active_date or u.created_at.date())).days
            }
            for u in inactive_users
        ]
    
    def reset_user_progress(self, user_id: int) -> bool:
        """Reset a user's learning progress"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        # Reset stats
        user.xp = 0
        user.level = 1
        user.current_streak = 0
        user.total_words_learned = 0
        user.total_quizzes_taken = 0
        user.correct_answers = 0
        
        # Delete learning data
        self.db.query(UserWord).filter(UserWord.user_id == user.id).delete()
        self.db.query(QuizResult).filter(QuizResult.user_id == user.id).delete()
        
        self.db.commit()
        return True
