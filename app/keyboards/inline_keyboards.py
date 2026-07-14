"""Inline keyboard layouts for the Telegram bot"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List

from app.services.quiz_service import QuizQuestion


def get_quiz_keyboard(question: QuizQuestion, question_number: int, total_questions: int) -> InlineKeyboardMarkup:
    """Create keyboard for quiz question"""
    buttons = []
    
    # Add option buttons (2 per row)
    for i in range(0, len(question.options), 2):
        row = []
        for j in range(i, min(i + 2, len(question.options))):
            # Callback data: quiz_answer:question_number:option_index
            callback_data = f"quiz_answer:{question_number}:{j}:{question.vocabulary_id}:{question.question_type}"
            row.append(InlineKeyboardButton(
                f"{chr(65 + j)}. {question.options[j][:20]}",  # A, B, C, D labels
                callback_data=callback_data
            ))
        buttons.append(row)
    
    # Add navigation row
    nav_row = []
    if question_number > 1:
        nav_row.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"quiz_nav:{question_number - 1}"))
    nav_row.append(InlineKeyboardButton(f"{question_number}/{total_questions}", callback_data="quiz_info"))
    if question_number < total_questions:
        nav_row.append(InlineKeyboardButton("Next ➡️", callback_data=f"quiz_nav:{question_number + 1}"))
    buttons.append(nav_row)
    
    # Add cancel button
    buttons.append([InlineKeyboardButton("❌ End Quiz", callback_data="quiz_end")])
    
    return InlineKeyboardMarkup(buttons)


def get_answer_feedback_keyboard(is_correct: bool, question_number: int, total_questions: int) -> InlineKeyboardMarkup:
    """Keyboard shown after answering"""
    buttons = []
    
    if is_correct:
        emoji = "✅"
        text = "Correct!"
    else:
        emoji = "❌"
        text = "Incorrect"
    
    # Show result
    buttons.append([InlineKeyboardButton(f"{emoji} {text}", callback_data="answer_result")])
    
    # Navigation
    nav_row = []
    if question_number < total_questions:
        nav_row.append(InlineKeyboardButton("Next Question ➡️", callback_data=f"quiz_nav:{question_number + 1}"))
    else:
        nav_row.append(InlineKeyboardButton("🎉 Finish Quiz", callback_data="quiz_finish"))
    buttons.append(nav_row)
    
    return InlineKeyboardMarkup(buttons)


def get_daily_vocab_keyboard(word_id: int) -> InlineKeyboardMarkup:
    """Keyboard for daily vocabulary word"""
    buttons = [
        [
            InlineKeyboardButton("✅ Mark as Learned", callback_data=f"learn_word:{word_id}"),
            InlineKeyboardButton("🎯 Quiz Me", callback_data="start_quiz")
        ],
        [
            InlineKeyboardButton("📊 My Stats", callback_data="show_stats"),
            InlineKeyboardButton("🏆 Leaderboard", callback_data="show_leaderboard")
        ]
    ]
    return InlineKeyboardMarkup(buttons)


def get_stats_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for stats page"""
    buttons = [
        [
            InlineKeyboardButton("🎯 Take Quiz", callback_data="start_quiz"),
            InlineKeyboardButton("📚 Daily Words", callback_data="show_daily")
        ],
        [
            InlineKeyboardButton("🏆 Leaderboard", callback_data="show_leaderboard"),
            InlineKeyboardButton("❓ Help", callback_data="show_help")
        ]
    ]
    return InlineKeyboardMarkup(buttons)


def get_leaderboard_keyboard(page: int = 1, has_more: bool = False) -> InlineKeyboardMarkup:
    """Keyboard for leaderboard"""
    buttons = []
    
    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"lb_page:{page - 1}"))
    nav_row.append(InlineKeyboardButton(f"Page {page}", callback_data="lb_info"))
    if has_more:
        nav_row.append(InlineKeyboardButton("Next ➡️", callback_data=f"lb_page:{page + 1}"))
    buttons.append(nav_row)
    
    buttons.append([
        InlineKeyboardButton("📊 My Stats", callback_data="show_stats"),
        InlineKeyboardButton("🎯 Quiz", callback_data="start_quiz")
    ])
    
    return InlineKeyboardMarkup(buttons)


def get_help_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for help page"""
    buttons = [
        [
            InlineKeyboardButton("📚 Daily Vocab", callback_data="show_daily"),
            InlineKeyboardButton("🎯 Take Quiz", callback_data="start_quiz")
        ],
        [
            InlineKeyboardButton("📊 My Stats", callback_data="show_stats"),
            InlineKeyboardButton("🏆 Leaderboard", callback_data="show_leaderboard")
        ]
    ]
    return InlineKeyboardMarkup(buttons)


def get_start_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for start command"""
    buttons = [
        [
            InlineKeyboardButton("📚 Get Daily Words", callback_data="show_daily"),
            InlineKeyboardButton("🎯 Start Quiz", callback_data="start_quiz")
        ],
        [
            InlineKeyboardButton("📊 View Stats", callback_data="show_stats"),
            InlineKeyboardButton("❓ Help", callback_data="show_help")
        ]
    ]
    return InlineKeyboardMarkup(buttons)


def get_quiz_result_keyboard(score: int, total: int) -> InlineKeyboardMarkup:
    """Keyboard shown at end of quiz"""
    percentage = (score / total) * 100 if total > 0 else 0
    
    buttons = [
        [InlineKeyboardButton(f"🎯 Score: {score}/{total} ({percentage:.0f}%)", callback_data="quiz_score")]
    ]
    
    if percentage >= 80:
        buttons.append([InlineKeyboardButton("🌟 Excellent! Play Again?", callback_data="start_quiz")])
    elif percentage >= 60:
        buttons.append([InlineKeyboardButton("👍 Good Job! Try Again?", callback_data="start_quiz")])
    else:
        buttons.append([InlineKeyboardButton("💪 Keep Practicing! Try Again?", callback_data="start_quiz")])
    
    buttons.append([
        InlineKeyboardButton("📊 My Stats", callback_data="show_stats"),
        InlineKeyboardButton("🏆 Leaderboard", callback_data="show_leaderboard")
    ])
    
    return InlineKeyboardMarkup(buttons)


def get_confirmation_keyboard(confirm_callback: str, cancel_callback: str) -> InlineKeyboardMarkup:
    """Generic confirmation keyboard"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Yes", callback_data=confirm_callback),
            InlineKeyboardButton("❌ No", callback_data=cancel_callback)
        ]
    ])
