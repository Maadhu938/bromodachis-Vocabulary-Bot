"""User service for managing gamification features"""
from datetime import date, datetime, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.user import User, UserWord, QuizResult
from app.models.vocabulary import Vocabulary
from app.utils.constants import (
    XP_DAILY_VOCABULARY,
    XP_CORRECT_QUIZ_ANSWER,
    XP_STREAK_BONUS_7_DAYS,
    XP_STREAK_BONUS_30_DAYS,
    XP_NEW_WORD_LEARNED,
    LEVEL_THRESHOLDS
)


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_user(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> User:
        """Get existing user or create new one"""
        user = self.db.query(User).filter(User.telegram_id == telegram_id).first()
        
        if not user:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        
        return user

    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID"""
        return self.db.query(User).filter(User.telegram_id == telegram_id).first()

    def update_user_activity(self, user: User) -> dict:
        """Update user activity and check streak"""
        today = date.today()
        streak_bonus = 0
        messages = []
        
        if user.last_active_date:
            days_diff = (today - user.last_active_date).days
            
            if days_diff == 0:
                # Already active today
                pass
            elif days_diff == 1:
                # Consecutive day - increase streak
                user.current_streak += 1
                messages.append(f"🔥 Streak continued! {user.current_streak} days!")
                
                # Check streak bonuses
                if user.current_streak == 7:
                    streak_bonus = XP_STREAK_BONUS_7_DAYS
                    messages.append(f"🎉 7-day streak bonus! +{streak_bonus} XP!")
                elif user.current_streak == 30:
                    streak_bonus = XP_STREAK_BONUS_30_DAYS
                    messages.append(f"🎉 30-day streak bonus! +{streak_bonus} XP!")
                    
            elif days_diff <= 2:
                # Within grace period - keep streak
                user.current_streak += 1
                messages.append(f"🔥 Streak saved! {user.current_streak} days!")
            else:
                # Streak broken
                if user.current_streak > 0:
                    messages.append(f"❄️ Streak reset! You had {user.current_streak} days.")
                user.current_streak = 1
                messages.append("🔥 New streak started!")
        else:
            # First activity
            user.current_streak = 1
            messages.append("🔥 Streak started!")
        
        # Update longest streak
        if user.current_streak > user.longest_streak:
            user.longest_streak = user.current_streak
        
        user.last_active_date = today
        
        # Add streak bonus XP if applicable
        if streak_bonus > 0:
            self.add_xp(user, streak_bonus, "streak_bonus")
        
        self.db.commit()
        
        return {
            "streak": user.current_streak,
            "bonus_xp": streak_bonus,
            "messages": messages
        }

    def add_xp(self, user: User, amount: int, source: str = "") -> dict:
        """Add XP to user and check for level up"""
        old_level = user.level
        user.xp += amount
        
        # Check for level up
        level_up = False
        new_level = old_level
        
        for level, threshold in sorted(LEVEL_THRESHOLDS.items()):
            if user.xp >= threshold and level > new_level:
                new_level = level
        
        if new_level > old_level:
            user.level = new_level
            level_up = True
        
        self.db.commit()
        
        return {
            "xp_gained": amount,
            "total_xp": user.xp,
            "level_up": level_up,
            "old_level": old_level,
            "new_level": new_level
        }

    def award_daily_vocab_xp(self, user: User) -> dict:
        """Award XP for daily vocabulary"""
        today = date.today()
        
        # Check if already claimed today
        if user.last_daily_vocab_date == today:
            return {"already_claimed": True, "xp_gained": 0}
        
        # Update activity and streak
        activity_result = self.update_user_activity(user)
        
        # Award XP
        xp_result = self.add_xp(user, XP_DAILY_VOCABULARY, "daily_vocabulary")
        user.last_daily_vocab_date = today
        
        self.db.commit()
        
        return {
            "already_claimed": False,
            "xp_gained": XP_DAILY_VOCABULARY + activity_result["bonus_xp"],
            "streak": user.current_streak,
            "level_up": xp_result["level_up"],
            "messages": activity_result["messages"]
        }

    def award_quiz_xp(self, user: User, correct: bool) -> dict:
        """Award XP for quiz answer"""
        user.total_quizzes_taken += 1
        
        if correct:
            user.correct_answers += 1
            xp_result = self.add_xp(user, XP_CORRECT_QUIZ_ANSWER, "correct_quiz")
            return {
                "correct": True,
                "xp_gained": XP_CORRECT_QUIZ_ANSWER,
                "level_up": xp_result["level_up"]
            }
        
        self.db.commit()
        return {"correct": False, "xp_gained": 0, "level_up": False}

    def mark_word_as_learned(self, user: User, vocabulary_id: int) -> bool:
        """Mark a vocabulary word as learned by user"""
        # Check if already learned
        existing = self.db.query(UserWord).filter(
            UserWord.user_id == user.id,
            UserWord.vocabulary_id == vocabulary_id
        ).first()
        
        if existing:
            # Update review count
            existing.review_count += 1
            existing.last_reviewed = datetime.now()
        else:
            # Add new learned word
            user_word = UserWord(
                user_id=user.id,
                vocabulary_id=vocabulary_id
            )
            self.db.add(user_word)
            user.total_words_learned += 1
            
            # Award XP for new word
            self.add_xp(user, XP_NEW_WORD_LEARNED, "new_word")
        
        self.db.commit()
        return True

    def get_learned_word_ids(self, user: User) -> List[int]:
        """Get list of vocabulary IDs learned by user"""
        results = self.db.query(UserWord.vocabulary_id).filter(
            UserWord.user_id == user.id
        ).all()
        return [r[0] for r in results]

    def get_user_stats(self, user: User) -> dict:
        """Get comprehensive user stats"""
        next_level_xp = user.get_next_level_xp()
        prev_level_xp = LEVEL_THRESHOLDS.get(user.level, 0)
        xp_in_current_level = user.xp - prev_level_xp
        xp_needed = next_level_xp - prev_level_xp
        progress_pct = user.get_progress_percentage()
        
        # Calculate accuracy
        accuracy = 0
        if user.total_quizzes_taken > 0:
            accuracy = int((user.correct_answers / user.total_quizzes_taken) * 100)
        
        return {
            "telegram_id": user.telegram_id,
            "username": user.username,
            "first_name": user.first_name,
            "level": user.level,
            "level_title": user.get_level_title(),
            "xp": user.xp,
            "next_level_xp": next_level_xp,
            "xp_in_level": xp_in_current_level,
            "xp_needed": xp_needed,
            "progress_percentage": progress_pct,
            "current_streak": user.current_streak,
            "longest_streak": user.longest_streak,
            "total_words_learned": user.total_words_learned,
            "total_quizzes_taken": user.total_quizzes_taken,
            "correct_answers": user.correct_answers,
            "accuracy": accuracy,
            "joined_at": user.created_at
        }

    def get_leaderboard(self, limit: int = 10) -> List[dict]:
        """Get top users by XP"""
        users = self.db.query(User).order_by(User.xp.desc()).limit(limit).all()
        
        leaderboard = []
        for rank, user in enumerate(users, 1):
            leaderboard.append({
                "rank": rank,
                "telegram_id": user.telegram_id,
                "username": user.username or user.first_name or "Anonymous",
                "xp": user.xp,
                "level": user.level,
                "level_title": user.get_level_title(),
                "current_streak": user.current_streak
            })
        
        return leaderboard

    def get_user_rank(self, user: User) -> int:
        """Get user's global rank"""
        rank = self.db.query(func.count(User.id)).filter(User.xp > user.xp).scalar()
        return rank + 1
