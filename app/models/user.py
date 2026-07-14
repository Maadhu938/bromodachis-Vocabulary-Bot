from sqlalchemy import Column, Integer, String, DateTime, Date, BigInteger, Boolean
from sqlalchemy.sql import func
from app.database.connection import Base


class User(Base):
    """Telegram user with gamification stats"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    
    # Gamification stats
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_active_date = Column(Date, nullable=True)
    
    # Daily vocabulary tracking
    last_daily_vocab_date = Column(Date, nullable=True)
    total_words_learned = Column(Integer, default=0)
    
    # Quiz stats
    total_quizzes_taken = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def get_level_title(self) -> str:
        """Get title based on level"""
        titles = {
            1: "🔰 Beginner",
            2: "📚 Student",
            3: "✏️ Learner",
            4: "📝 Intermediate",
            5: "📖 Advanced",
            6: "🎓 Expert",
            7: "🏆 Master",
            8: "👑 Sensei",
            9: "⭐ Legend",
            10: "🌟 Grandmaster"
        }
        return titles.get(self.level, f"Level {self.level}")

    def get_next_level_xp(self) -> int:
        """Calculate XP needed for next level (exponential growth)"""
        return int(100 * (1.5 ** (self.level - 1)))

    def get_progress_percentage(self) -> int:
        """Get progress to next level as percentage"""
        next_level_xp = self.get_next_level_xp()
        prev_level_xp = int(100 * (1.5 ** (self.level - 2))) if self.level > 1 else 0
        current_level_xp = self.xp - prev_level_xp
        needed_xp = next_level_xp - prev_level_xp
        return min(100, int((current_level_xp / needed_xp) * 100))


class UserWord(Base):
    """Track which words each user has learned"""
    __tablename__ = "user_words"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    vocabulary_id = Column(Integer, nullable=False, index=True)
    learned_at = Column(DateTime, server_default=func.now())
    review_count = Column(Integer, default=0)
    last_reviewed = Column(DateTime, nullable=True)


class QuizResult(Base):
    """Track quiz attempts"""
    __tablename__ = "quiz_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    vocabulary_id = Column(Integer, nullable=False)
    question_type = Column(String, nullable=False)  # 'meaning_to_jp', 'jp_to_meaning', 'reading_to_expression'
    correct = Column(Boolean, nullable=False)
    answered_at = Column(DateTime, server_default=func.now())
