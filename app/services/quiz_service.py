"""Quiz service for generating questions"""
import random
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.vocabulary import Vocabulary
from app.models.user import User, QuizResult
from app.utils.constants import QUIZ_OPTIONS_COUNT, QUIZ_QUESTIONS_PER_SESSION


class QuizQuestion:
    """Represents a single quiz question"""
    def __init__(
        self,
        question_type: str,
        question_text: str,
        correct_answer: str,
        options: List[str],
        vocabulary_id: int,
        expression: str,
        reading: str,
        meaning: str
    ):
        self.question_type = question_type
        self.question_text = question_text
        self.correct_answer = correct_answer
        self.options = options
        self.vocabulary_id = vocabulary_id
        self.expression = expression
        self.reading = reading
        self.meaning = meaning
        try:
            self.correct_index = options.index(correct_answer)
        except ValueError:
            # Fallback if correct answer not in options (shouldn't happen)
            self.correct_index = 0


class QuizService:
    def __init__(self, db: Session):
        self.db = db

    def generate_question(
        self,
        user: User,
        question_type: Optional[str] = None
    ) -> Optional[QuizQuestion]:
        """Generate a single quiz question"""
        
        # Get words the user has learned
        learned_ids = self.db.query(QuizResult.vocabulary_id).filter(
            QuizResult.user_id == user.id
        ).distinct().all()
        learned_ids = [id[0] for id in learned_ids]
        
        # If user hasn't learned many words, use any words
        if len(learned_ids) < 10:
            # Get random words from database
            words = self.db.query(Vocabulary).order_by(func.random()).limit(20).all()
        else:
            # Use learned words + some new ones
            words = self.db.query(Vocabulary).filter(
                Vocabulary.id.in_(learned_ids)
            ).order_by(func.random()).limit(15).all()
            
            # Add some new words
            new_words = self.db.query(Vocabulary).filter(
                ~Vocabulary.id.in_(learned_ids)
            ).order_by(func.random()).limit(5).all()
            words.extend(new_words)
            random.shuffle(words)
        
        if not words:
            return None
        
        # Select question type if not specified
        if question_type is None:
            question_type = random.choice([
                "meaning_to_jp",
                "jp_to_meaning",
                "reading_to_expression"
            ])
        
        # Select correct answer word
        correct_word = random.choice(words)
        
        # Get distractors (wrong answers)
        distractors = [w for w in words if w.id != correct_word.id]
        if len(distractors) < QUIZ_OPTIONS_COUNT - 1:
            # Not enough words, get more from database
            additional = self.db.query(Vocabulary).filter(
                Vocabulary.id != correct_word.id
            ).order_by(func.random()).limit(QUIZ_OPTIONS_COUNT * 2).all()
            distractors.extend(additional)
        
        # Select random distractors
        wrong_options = random.sample(distractors, min(QUIZ_OPTIONS_COUNT - 1, len(distractors)))
        
        # Build question based on type
        if question_type == "meaning_to_jp":
            question_text = f"What is the Japanese word for:\n\n<b>{correct_word.meaning}</b>?"
            correct_answer = correct_word.expression
            options = [correct_answer] + [w.expression for w in wrong_options]
            
        elif question_type == "jp_to_meaning":
            question_text = f"What does <b>{correct_word.expression}</b> mean?\n\nReading: ({correct_word.reading})"
            correct_answer = correct_word.meaning
            options = [correct_answer] + [w.meaning for w in wrong_options]
            
        elif question_type == "reading_to_expression":
            question_text = f"Which word is read as:\n\n<b>{correct_word.reading}</b>?"
            correct_answer = correct_word.expression
            options = [correct_answer] + [w.expression for w in wrong_options]
        else:
            return None
        
        # Shuffle options
        random.shuffle(options)
        
        return QuizQuestion(
            question_type=question_type,
            question_text=question_text,
            correct_answer=correct_answer,
            options=options,
            vocabulary_id=correct_word.id,
            expression=correct_word.expression,
            reading=correct_word.reading,
            meaning=correct_word.meaning
        )

    def generate_quiz_session(
        self,
        user: User,
        num_questions: int = QUIZ_QUESTIONS_PER_SESSION
    ) -> List[QuizQuestion]:
        """Generate a full quiz session"""
        questions = []
        attempts = 0
        max_attempts = num_questions * 3
        
        while len(questions) < num_questions and attempts < max_attempts:
            question = self.generate_question(user)
            if question:
                # Avoid duplicate questions in same session
                if not any(q.vocabulary_id == question.vocabulary_id for q in questions):
                    questions.append(question)
            attempts += 1
        
        return questions

    def record_answer(
        self,
        user: User,
        vocabulary_id: int,
        question_type: str,
        correct: bool
    ) -> None:
        """Record a quiz answer"""
        result = QuizResult(
            user_id=user.id,
            vocabulary_id=vocabulary_id,
            question_type=question_type,
            correct=correct
        )
        self.db.add(result)
        self.db.commit()

    def get_user_quiz_stats(self, user: User) -> Dict:
        """Get user's quiz statistics"""
        total = self.db.query(QuizResult).filter(
            QuizResult.user_id == user.id
        ).count()
        
        correct = self.db.query(QuizResult).filter(
            QuizResult.user_id == user.id,
            QuizResult.correct == True
        ).count()
        
        accuracy = round((correct / total) * 100, 1) if total > 0 else 0
        
        # Get stats by question type
        type_stats = {}
        for q_type in ["meaning_to_jp", "jp_to_meaning", "reading_to_expression"]:
            type_total = self.db.query(QuizResult).filter(
                QuizResult.user_id == user.id,
                QuizResult.question_type == q_type
            ).count()
            type_correct = self.db.query(QuizResult).filter(
                QuizResult.user_id == user.id,
                QuizResult.question_type == q_type,
                QuizResult.correct == True
            ).count()
            type_stats[q_type] = {
                "total": type_total,
                "correct": type_correct,
                "accuracy": round((type_correct / type_total) * 100, 1) if type_total > 0 else 0
            }
        
        return {
            "total_questions": total,
            "correct_answers": correct,
            "accuracy": accuracy,
            "by_type": type_stats
        }

    def get_weak_areas(self, user: User, limit: int = 5) -> List[Dict]:
        """Get words the user struggles with"""
        from sqlalchemy import desc
        
        # Get words with low accuracy
        weak_words = self.db.query(
            Vocabulary,
            func.count(QuizResult.id).label('total'),
            func.sum(QuizResult.correct.cast()).label('correct_count')
        ).join(
            QuizResult, Vocabulary.id == QuizResult.vocabulary_id
        ).filter(
            QuizResult.user_id == user.id
        ).group_by(
            Vocabulary.id
        ).having(
            func.count(QuizResult.id) >= 2  # At least 2 attempts
        ).order_by(
            (func.sum(QuizResult.correct.cast()) / func.count(QuizResult.id))
        ).limit(limit).all()
        
        result = []
        for vocab, total, correct in weak_words:
            accuracy = round((correct / total) * 100, 1) if total > 0 else 0
            result.append({
                "word": vocab,
                "total_attempts": total,
                "correct": correct,
                "accuracy": accuracy
            })
        
        return result
