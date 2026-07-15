"""Telegram Bot for Japanese Vocabulary Learning with Gamification"""
import os
import logging
from datetime import date, datetime
from typing import Dict, List

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
from dotenv import load_dotenv

from app.database.connection import SessionLocal
from app.services.user_service import UserService
from app.services.quiz_service import QuizService, QuizQuestion
from app.services.vocabulary import VocabularyService
from app.services.formatter import MessageFormatter
from app.services.admin_service import AdminService
from app.services.ai_service import ai_service
from app.utils.constants import (
    WELCOME_MESSAGE,
    HELP_MESSAGE,
    ABOUT_MESSAGE,
    WORDS_PER_DAY_DEFAULT,
    get_streak_emoji
)
from app.keyboards.inline_keyboards import (
    get_start_keyboard,
    get_quiz_keyboard,
    get_answer_feedback_keyboard,
    get_quiz_result_keyboard,
    get_stats_keyboard,
    get_leaderboard_keyboard,
    get_help_keyboard,
    get_daily_vocab_keyboard
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Store quiz sessions in memory (user_id -> quiz data)
quiz_sessions: Dict[int, Dict] = {}

# Admin configuration - Add your Telegram ID here
# Get your ID by messaging @userinfobot on Telegram
ADMIN_IDS = [int(id.strip()) for id in os.getenv("ADMIN_IDS", "").split(",") if id.strip()]

# In-memory admin manager storage (for runtime admin management)
# Format: {manager_telegram_id: {"added_at": datetime, "added_by": admin_id}}
ADMIN_MANAGERS = {}


def is_admin(telegram_id: int) -> bool:
    """Check if user is admin"""
    return telegram_id in ADMIN_IDS


def is_admin_manager(telegram_id: int) -> bool:
    """Check if user is an admin manager"""
    return telegram_id in ADMIN_MANAGERS or telegram_id in ADMIN_IDS


def add_admin_manager(manager_id: int, added_by: int) -> bool:
    """Add a new admin manager"""
    if manager_id in ADMIN_IDS or manager_id in ADMIN_MANAGERS:
        return False
    ADMIN_MANAGERS[manager_id] = {
        "added_at": datetime.now(),
        "added_by": added_by
    }
    return True


def remove_admin_manager(manager_id: int) -> bool:
    """Remove an admin manager"""
    if manager_id in ADMIN_MANAGERS:
        del ADMIN_MANAGERS[manager_id]
        return True
    return False


def get_admin_managers() -> list:
    """Get list of all admin managers"""
    return list(ADMIN_MANAGERS.keys())


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise


# ============== COMMAND HANDLERS ==============

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    db = get_db()
    
    try:
        user_service = UserService(db)
        db_user = user_service.get_or_create_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        # Update activity
        activity = user_service.update_user_activity(db_user)
        
        welcome_text = f"""
🎌 <b>Welcome, {user.first_name or 'Learner'}!</b> 🇯🇵

{WELCOME_MESSAGE}

{chr(10).join(activity['messages']) if activity['messages'] else ''}
        """.strip()
        
        await update.message.reply_html(
            welcome_text,
            reply_markup=get_start_keyboard()
        )
    finally:
        db.close()


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    await update.message.reply_html(
        HELP_MESSAGE,
        reply_markup=get_help_keyboard()
    )


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /about command"""
    await update.message.reply_html(ABOUT_MESSAGE)


async def daily_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /daily command - send daily vocabulary"""
    user = update.effective_user
    db = get_db()
    
    try:
        user_service = UserService(db)
        vocab_service = VocabularyService(db)
        
        db_user = user_service.get_user_by_telegram_id(user.id)
        if not db_user:
            await update.message.reply_text("Please use /start first!")
            return
        
        # Award XP for daily vocab
        xp_result = user_service.award_daily_vocab_xp(db_user)
        
        if xp_result.get("already_claimed"):
            await update.message.reply_text(
                "You've already claimed today's vocabulary! Come back tomorrow. 🌅"
            )
            return
        
        # Get words for user (not yet learned)
        learned_ids = user_service.get_learned_word_ids(db_user)
        
        # Get next words
        words = vocab_service.get_next_words_for_user(learned_ids, limit=WORDS_PER_DAY_DEFAULT)
        
        if not words:
            await update.message.reply_text(
                "🎉 Congratulations! You've learned all available words!\n"
                "Use /quiz to practice what you've learned."
            )
            return
        
        # Send vocabulary message
        batch_number = len(learned_ids) // WORDS_PER_DAY_DEFAULT + 1
        message = MessageFormatter.format_daily_message(batch_number, words)
        
        # Add XP info
        xp_info = f"\n\n✨ +{xp_result['xp_gained']} XP"
        if xp_result.get("level_up"):
            xp_info += f"\n🎉 LEVEL UP! You are now {db_user.get_level_title()}!"
        message += xp_info
        
        await update.message.reply_html(message)
        
        # Mark words as learned and send individual word cards
        for word in words:
            user_service.mark_word_as_learned(db_user, word.id)
            
            word_card = f"""
<b>{word.expression}</b>
📖 Reading: {word.reading}
📝 Meaning: {word.meaning}
            """.strip()
            
            await update.message.reply_html(
                word_card,
                reply_markup=get_daily_vocab_keyboard(word.id)
            )
        
        # Show streak info
        streak_emoji = get_streak_emoji(db_user.current_streak)
        await update.message.reply_html(
            f"{streak_emoji} <b>Current Streak: {db_user.current_streak} days!</b>\n"
            f"Keep it up! 🔥"
        )
        
    finally:
        db.close()


async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /quiz command - start a quiz session"""
    user = update.effective_user
    db = get_db()
    
    try:
        user_service = UserService(db)
        quiz_service = QuizService(db)
        
        db_user = user_service.get_user_by_telegram_id(user.id)
        if not db_user:
            await update.message.reply_text("Please use /start first!")
            return
        
        # Generate quiz questions
        questions = quiz_service.generate_quiz_session(db_user)
        
        if not questions:
            await update.message.reply_text(
                "Not enough words to create a quiz yet. Use /daily to learn some words first! 📚"
            )
            return
        
        # Store quiz session
        quiz_sessions[user.id] = {
            "questions": questions,
            "current_question": 0,
            "score": 0,
            "answers": {}
        }
        
        # Send first question
        await send_quiz_question(update, context, user.id)
        
    finally:
        db.close()


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command - show user statistics"""
    user = update.effective_user
    db = get_db()
    
    try:
        user_service = UserService(db)
        quiz_service = QuizService(db)
        
        db_user = user_service.get_user_by_telegram_id(user.id)
        if not db_user:
            await update.message.reply_text("Please use /start first!")
            return
        
        stats = user_service.get_user_stats(db_user)
        quiz_stats = quiz_service.get_user_quiz_stats(db_user)
        rank = user_service.get_user_rank(db_user)
        
        # Build progress bar
        progress_bar = "▓" * (stats["progress_percentage"] // 10) + "░" * (10 - stats["progress_percentage"] // 10)
        
        streak_emoji = get_streak_emoji(stats["current_streak"])
        
        message = f"""
<b>📊 Your Learning Stats</b>

<b>{stats['level_title']}</b>
Level {stats['level']} | Rank #{rank}

<b>XP Progress:</b>
{progress_bar} {stats['progress_percentage']}%
{stats['xp_in_level']}/{stats['xp_needed']} XP to next level
Total: {stats['xp']} XP

<b>🔥 Streak:</b>
Current: {streak_emoji} {stats['current_streak']} days
Longest: {stats['longest_streak']} days

<b>📚 Learning:</b>
Words Learned: {stats['total_words_learned']}

<b>🎯 Quiz Performance:</b>
Questions: {quiz_stats['total_questions']}
Correct: {quiz_stats['correct_answers']}
Accuracy: {quiz_stats['accuracy']}%
        """.strip()
        
        await update.message.reply_html(message, reply_markup=get_stats_keyboard())
        
    finally:
        db.close()


async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /leaderboard command"""
    db = get_db()
    
    try:
        user_service = UserService(db)
        leaderboard = user_service.get_leaderboard(limit=10)
        
        message = "<b>🏆 Global Leaderboard - Top Learners</b>\n\n"
        
        medals = {1: "🥇", 2: "🥈", 3: "🥉"}
        
        for entry in leaderboard:
            rank = entry["rank"]
            medal = medals.get(rank, f"{rank}.")
            streak = get_streak_emoji(entry["current_streak"])
            
            message += (
                f"{medal} <b>{entry['username'][:15]}</b>\n"
                f"   {entry['level_title']} | {entry['xp']} XP {streak}{entry['current_streak']}\n\n"
            )
        
        await update.message.reply_html(
            message,
            reply_markup=get_leaderboard_keyboard(page=1, has_more=False)
        )
        
    finally:
        db.close()


async def learned_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /learned command - show words user has learned"""
    user = update.effective_user
    db = get_db()
    
    try:
        user_service = UserService(db)
        vocab_service = VocabularyService(db)
        
        db_user = user_service.get_user_by_telegram_id(user.id)
        if not db_user:
            await update.message.reply_text("Please use /start first!")
            return
        
        # Get learned word IDs
        learned_ids = user_service.get_learned_word_ids(db_user)
        
        if not learned_ids:
            await update.message.reply_text(
                "📚 You haven't learned any words yet!\n\n"
                "Use /daily to start learning vocabulary."
            )
            return
        
        # Get the actual words
        learned_words = []
        for word_id in learned_ids[-20:]:  # Show last 20 words
            word = vocab_service.get_word_by_id(word_id)
            if word:
                learned_words.append(word)
        
        # Build message
        message = f"<b>📚 Words You've Learned</b>\n"
        message += f"<b>Total:</b> {len(learned_ids)} words\n\n"
        
        for i, word in enumerate(reversed(learned_words), 1):
            message += f"{i}. <b>{word.expression}</b>\n"
            message += f"   📖 {word.reading}\n"
            message += f"   📝 {word.meaning}\n\n"
        
        await update.message.reply_html(message)
        
    finally:
        db.close()


# ============== QUIZ FUNCTIONS ==============

async def send_quiz_question(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Send a quiz question to user"""
    session = quiz_sessions.get(user_id)
    if not session:
        return
    
    current_idx = session["current_question"]
    questions = session["questions"]
    
    if current_idx >= len(questions):
        # Quiz finished
        await finish_quiz(update, context, user_id)
        return
    
    question = questions[current_idx]
    
    message = f"""
<b>🎯 Question {current_idx + 1}/{len(questions)}</b>

{question.question_text}
    """.strip()
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            message,
            reply_markup=get_quiz_keyboard(question, current_idx + 1, len(questions)),
            parse_mode="HTML"
        )
    else:
        await update.message.reply_html(
            message,
            reply_markup=get_quiz_keyboard(question, current_idx + 1, len(questions))
        )


async def handle_quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle quiz answer callback"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    user_id = user.id
    
    # Parse callback data: quiz_answer:question_number:option_index:vocab_id:question_type
    data = query.data.split(":")
    if len(data) != 5:
        return
    
    _, question_num, option_idx, vocab_id, question_type = data
    question_num = int(question_num)
    option_idx = int(option_idx)
    vocab_id = int(vocab_id)
    
    session = quiz_sessions.get(user_id)
    if not session or question_num - 1 != session["current_question"]:
        await query.edit_message_text("This quiz session has expired. Start a new one with /quiz")
        return
    
    question = session["questions"][session["current_question"]]
    selected_answer = question.options[option_idx]
    is_correct = selected_answer == question.correct_answer
    
    # Record answer in database
    db = get_db()
    try:
        user_service = UserService(db)
        quiz_service = QuizService(db)
        
        db_user = user_service.get_user_by_telegram_id(user_id)
        if db_user:
            # Record the answer
            quiz_service.record_answer(db_user, vocab_id, question_type, is_correct)
            
            # Award XP
            xp_result = user_service.award_quiz_xp(db_user, is_correct)
            
            # Update session
            session["answers"][question_num] = is_correct
            if is_correct:
                session["score"] += 1
            
            # Show feedback
            feedback = "✅ Correct!" if is_correct else f"❌ Wrong! The answer was: {question.correct_answer}"
            if xp_result.get("level_up"):
                feedback += f"\n\n🎉 LEVEL UP! You are now {db_user.get_level_title()}!"
            elif is_correct:
                feedback += f"\n+{xp_result['xp_gained']} XP"
            
            await query.edit_message_text(
                f"<b>🎯 Question {question_num}/{len(session['questions'])}</b>\n\n"
                f"{question.question_text}\n\n"
                f"{feedback}",
                reply_markup=get_answer_feedback_keyboard(is_correct, question_num, len(session["questions"])),
                parse_mode="HTML"
            )
    finally:
        db.close()


async def handle_quiz_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle quiz navigation (next/prev/end)"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    data = query.data.split(":")
    
    if data[0] == "quiz_nav":
        # Navigate to question
        target_question = int(data[1]) - 1
        session = quiz_sessions.get(user_id)
        if session:
            session["current_question"] = target_question
            await send_quiz_question(update, context, user_id)
    
    elif data[0] == "quiz_finish":
        await finish_quiz(update, context, user_id)
    
    elif data[0] == "quiz_end":
        # End quiz immediately
        quiz_sessions.pop(user_id, None)
        await query.edit_message_text(
            "❌ Quiz ended. Use /quiz to start a new one!",
            reply_markup=get_start_keyboard()
        )


async def finish_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Finish quiz and show results"""
    session = quiz_sessions.pop(user_id, None)
    if not session:
        return
    
    score = session["score"]
    total = len(session["questions"])
    percentage = (score / total) * 100 if total > 0 else 0
    
    # Determine message based on score
    if percentage >= 80:
        title = "🌟 Excellent!"
        message = "Amazing job! You're mastering these words!"
    elif percentage >= 60:
        title = "👍 Good Job!"
        message = "Nice work! Keep practicing to improve."
    else:
        title = "💪 Keep Going!"
        message = "Practice makes perfect! Try again."
    
    result_text = f"""
<b>{title}</b>

{message}

<b>📊 Quiz Results:</b>
Score: {score}/{total} ({percentage:.0f}%)
    """.strip()
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            result_text,
            reply_markup=get_quiz_result_keyboard(score, total),
            parse_mode="HTML"
        )
    else:
        await update.message.reply_html(
            result_text,
            reply_markup=get_quiz_result_keyboard(score, total)
        )


# ============== CALLBACK HANDLERS ==============

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user = update.effective_user
    
    # Check if user exists in database
    db = get_db()
    try:
        user_service = UserService(db)
        db_user = user_service.get_user_by_telegram_id(user.id)
        
        if not db_user:
            await query.edit_message_text(
                "👋 Welcome! Please use /start first to register!",
                reply_markup=get_start_keyboard()
            )
            return
    finally:
        db.close()
    
    if data == "show_daily":
        # Get daily vocab for callback
        vocab_service = VocabularyService(db)
        words = vocab_service.get_daily_words(user.id, limit=WORDS_PER_DAY_DEFAULT)
        
        if not words:
            await query.edit_message_text(
                "🎉 You've learned all available words! Great job!",
                reply_markup=get_start_keyboard()
            )
            return
        
        message = f"📚 <b>Your Daily Vocabulary ({len(words)} words)</b>\n\n"
        for i, word in enumerate(words, 1):
            message += f"{i}. <b>{word.expression}</b>\n"
            message += f"   Reading: {word.reading}\n"
            message += f"   Meaning: {word.meaning}\n\n"
        
        await query.edit_message_text(
            message, 
            reply_markup=get_start_keyboard(),
            parse_mode="HTML"
        )
    
    elif data == "start_quiz":
        # Start quiz from callback
        user = update.effective_user
        db = get_db()
        
        try:
            user_service = UserService(db)
            quiz_service = QuizService(db)
            
            db_user = user_service.get_user_by_telegram_id(user.id)
            if not db_user:
                await query.edit_message_text(
                    "👋 Welcome! Please use /start first to register!",
                    reply_markup=get_start_keyboard()
                )
                return
            
            # Generate quiz questions
            questions = quiz_service.generate_quiz_session(db_user)
            
            if not questions:
                await query.edit_message_text(
                    "Not enough words to create a quiz yet. Use /daily to learn some words first! 📚",
                    reply_markup=get_start_keyboard()
                )
                return
            
            # Store quiz session
            quiz_sessions[user.id] = {
                "questions": questions,
                "current_question": 0,
                "score": 0,
                "answers": {}
            }
            
            # Send first question
            await send_quiz_question(update, context, user.id)
            
        finally:
            db.close()
    
    elif data == "show_stats":
        # Get stats for callback
        user_service = UserService(db)
        quiz_service = QuizService(db)
        stats = user_service.get_user_stats(db_user)
        quiz_stats = quiz_service.get_user_quiz_stats(db_user)
        rank = user_service.get_user_rank(db_user)
        
        progress_bar = "▓" * (stats["progress_percentage"] // 10) + "░" * (10 - stats["progress_percentage"] // 10)
        streak_emoji = get_streak_emoji(stats["current_streak"])
        
        message = f"""📊 <b>Your Learning Stats</b>

👤 <b>{user.first_name or 'Learner'}</b>
🏆 Rank: #{rank}
⭐ Level: {stats['level']} ({stats['level_title']})

📈 Progress:
{progress_bar} {stats['progress_percentage']}%
🔥 Current Streak: {stats['current_streak']} days {streak_emoji}
🏅 Longest Streak: {stats['longest_streak']} days

        📚 Learning:
• Words Learned: {stats['total_words_learned']}
• Total XP: {stats['xp']}
• Quizzes Taken: {quiz_stats['total_questions']}
• Accuracy: {quiz_stats['accuracy']}%

💡 Keep learning to improve your rank!"""
        
        await query.edit_message_text(message, reply_markup=get_start_keyboard(), parse_mode="HTML")
    
    elif data == "show_leaderboard":
        # Get leaderboard for callback
        user_service = UserService(db)
        leaderboard = user_service.get_leaderboard(limit=10)
        
        message = "🏆 <b>Leaderboard - Top Learners</b>\n\n"
        
        for i, user_data in enumerate(leaderboard, 1):
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, "📌")
            name = user_data.get('first_name') or user_data.get('username') or 'Anonymous'
            message += f"{medal} #{i} <b>{name}</b>\n"
            message += f"    Level {user_data['level']} | {user_data['xp']} XP | 🔥 {user_data['current_streak']} days\n\n"
        
        await query.edit_message_text(message, reply_markup=get_start_keyboard(), parse_mode="HTML")
    
    elif data == "show_help":
        await query.edit_message_text(HELP_MESSAGE, reply_markup=get_help_keyboard(), parse_mode="HTML")
    
    elif data == "show_ai_help":
        ai_help_text = """
🤖 <b>AI Assistant</b>

I can help you with Japanese using AI!

<b>Available Commands:</b>
/ask <question> - Ask anything about Japanese
/grammar <point> - Get grammar explanations
/translate <text> - Translate EN↔JP
/practice [topic] - Conversation practice
/tips - Get study tips

<b>Examples:</b>
/ask How do I use the particle は?
/grammar て-form
/translate Hello, how are you?
/practice ordering at a restaurant

Try it now! 💡
        """.strip()
        await query.edit_message_text(ai_help_text, reply_markup=get_start_keyboard(), parse_mode="HTML")
    
    elif data.startswith("learn_word:"):
        word_id = int(data.split(":")[1])
        await query.edit_message_text(f"✅ Word marked as learned! Keep it up!")
    
    elif data == "quiz_end":
        quiz_sessions.pop(user.id, None)
        await query.edit_message_text("Quiz ended. Use /quiz to start a new one!")


# ============== ADMIN COMMAND HANDLERS ==============

async def admin_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: Get bot statistics"""
    user = update.effective_user
    
    if not is_admin(user.id):
        await update.message.reply_text("⛔ This command is only for admins!")
        return
    
    db = get_db()
    try:
        admin_service = AdminService(db)
        stats = admin_service.get_bot_statistics()
        
        message = f"""
<b>📊 Bot Statistics (Admin)</b>

<b>👥 Users:</b>
• Total Users: {stats['users']['total']}
• Active Today: {stats['users']['active_today']}
• Active This Week: {stats['users']['active_this_week']}

<b>📚 Learning:</b>
• Total Words Learned: {stats['learning']['total_words_learned']}
• Total Quizzes Taken: {stats['learning']['total_quizzes_taken']}
• Overall Accuracy: {stats['learning']['overall_accuracy']}%

<b>🏆 Top Users:</b>
"""
        for i, u in enumerate(stats['top_users'], 1):
            message += f"{i}. {u['username'][:15]} - Level {u['level']} ({u['xp']} XP)\n"
        
        if stats['level_distribution']:
            message += "\n<b>📊 Level Distribution:</b>\n"
            for level, count in sorted(stats['level_distribution'].items()):
                message += f"• Level {level}: {count} users\n"
        
        await update.message.reply_html(message)
    finally:
        db.close()


async def admin_broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: Broadcast message to all users"""
    user = update.effective_user
    
    if not is_admin(user.id):
        await update.message.reply_text("⛔ This command is only for admins!")
        return
    
    if not context.args:
        await update.message.reply_text(
            "Usage: /broadcast Your message here\n"
            "Example: /broadcast 🎉 New feature released!"
        )
        return
    
    message = " ".join(context.args)
    db = get_db()
    
    try:
        admin_service = AdminService(db)
        users = admin_service.get_all_users(limit=1000)
        
        sent = 0
        failed = 0
        
        for user_data in users:
            try:
                await context.bot.send_message(
                    chat_id=user_data['telegram_id'],
                    text=f"<b>📢 Message from Admin:</b>\n\n{message}",
                    parse_mode="HTML"
                )
                sent += 1
            except Exception as e:
                logger.error(f"Failed to send to {user_data['telegram_id']}: {e}")
                failed += 1
        
        await update.message.reply_text(
            f"✅ Broadcast complete!\n"
            f"📤 Sent: {sent}\n"
            f"❌ Failed: {failed}"
        )
    finally:
        db.close()


async def admin_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: List all users"""
    user = update.effective_user
    
    if not is_admin(user.id):
        await update.message.reply_text("⛔ This command is only for admins!")
        return
    
    db = get_db()
    try:
        admin_service = AdminService(db)
        users = admin_service.get_all_users(limit=20)
        
        message = "<b>👥 Registered Users (Last 20)</b>\n\n"
        
        for u in users:
            name = u['username'] or u['first_name'] or "Unknown"
            message += (
                f"🆔 {u['id']} | {name[:15]}\n"
                f"   Level {u['level']} | {u['xp']} XP | "
                f"🔥 {u['current_streak']} days\n\n"
            )
        
        await update.message.reply_html(message)
    finally:
        db.close()


async def admin_userinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: Get detailed info about a user"""
    user = update.effective_user
    
    if not is_admin(user.id):
        await update.message.reply_text("⛔ This command is only for admins!")
        return
    
    if not context.args:
        await update.message.reply_text(
            "Usage: /userinfo <user_id>\n"
            "Example: /userinfo 42"
        )
        return
    
    try:
        user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ User ID must be a number!")
        return
    
    db = get_db()
    try:
        admin_service = AdminService(db)
        user_details = admin_service.get_user_details(user_id)
        
        if not user_details:
            await update.message.reply_text("❌ User not found!")
            return
        
        info = user_details['user_info']
        gamification = user_details['gamification']
        learning = user_details['learning']
        
        message = f"""
<b>👤 User Details (ID: {info['id']})</b>

<b>Info:</b>
• Telegram ID: {info['telegram_id']}
• Username: @{info['username'] or 'N/A'}
• Name: {info['first_name'] or ''} {info['last_name'] or ''}
• Joined: {info['created_at'].strftime('%Y-%m-%d')}
• Last Active: {info['last_active'].strftime('%Y-%m-%d') if info['last_active'] else 'Never'}

<b>Gamification:</b>
• Level: {gamification['level']} ({gamification['level_title']})
• XP: {gamification['xp']}
• Streak: {gamification['current_streak']} days (Longest: {gamification['longest_streak']})

<b>Learning:</b>
• Words Learned: {learning['words_learned']}
• Quizzes Taken: {learning['quizzes_taken']}
• Quiz Accuracy: {learning['quiz_accuracy']}%
"""
        await update.message.reply_html(message)
    finally:
        db.close()


async def admin_addxp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: Add XP to a user"""
    user = update.effective_user
    
    if not is_admin(user.id):
        await update.message.reply_text("⛔ This command is only for admins!")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "Usage: /addxp <user_id> <amount>\n"
            "Example: /addxp 42 100"
        )
        return
    
    try:
        user_id = int(context.args[0])
        xp_amount = int(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ User ID and XP amount must be numbers!")
        return
    
    db = get_db()
    try:
        admin_service = AdminService(db)
        result = admin_service.add_xp_to_user(user_id, xp_amount)
        
        if not result:
            await update.message.reply_text("❌ User not found!")
            return
        
        message = f"""
✅ XP Added Successfully!

• User ID: {user_id}
• XP Added: {result['xp_added']}
• New Total XP: {result['new_total_xp']}
"""
        if result['leveled_up']:
            message += f"\n🎉 User leveled up! {result['old_level']} → {result['new_level']}"
        
        await update.message.reply_text(message)
    finally:
        db.close()


async def admin_inactive_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: Get inactive users"""
    user = update.effective_user
    
    if not is_admin(user.id):
        await update.message.reply_text("⛔ This command is only for admins!")
        return
    
    days = 7
    if context.args:
        try:
            days = int(context.args[0])
        except ValueError:
            pass
    
    db = get_db()
    try:
        admin_service = AdminService(db)
        inactive_users = admin_service.get_inactive_users(days)
        
        if not inactive_users:
            await update.message.reply_text(f"✅ No users inactive for {days}+ days!")
            return
        
        message = f"<b>😴 Inactive Users ({days}+ days)</b>\n\n"
        
        for u in inactive_users[:20]:  # Show first 20
            name = u['username'] or u['first_name'] or "Unknown"
            message += (
                f"👤 {name[:15]}\n"
                f"   ID: {u['telegram_id']} | "
                f"Inactive: {u['days_inactive']} days\n\n"
            )
        
        await update.message.reply_html(message)
    finally:
        db.close()


async def admin_help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: Show admin commands"""
    user = update.effective_user
    
    if not is_admin(user.id):
        await update.message.reply_text("⛔ This command is only for admins!")
        return
    
    message = """
<b>🔧 Admin Commands</b>

<b>Statistics:</b>
/adminstats - Bot statistics
/adminusers - List all users

<b>User Management:</b>
/userinfo <user_id> - Get user details
/addxp <user_id> <amount> - Add XP to user
/inactive [days] - List inactive users

<b>Broadcast:</b>
/broadcast <message> - Send to all users

<b>Admin Manager:</b>
/addmanager <telegram_id> - Add admin manager
/removemanager <telegram_id> - Remove admin manager
/listmanagers - List all admin managers

<b>Your Admin ID:</b> {}
""".format(user.id)
    
    await update.message.reply_html(message)


async def admin_add_manager_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: Add an admin manager"""
    user = update.effective_user
    
    if not is_admin(user.id):
        await update.message.reply_text("⛔ This command is only for super admins!")
        return
    
    if not context.args:
        await update.message.reply_text(
            "Usage: /addmanager <telegram_id>\n"
            "Example: /addmanager 123456789\n\n"
            "Get Telegram ID by messaging @userinfobot"
        )
        return
    
    try:
        manager_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Telegram ID must be a number!")
        return
    
    if add_admin_manager(manager_id, user.id):
        await update.message.reply_text(
            f"✅ Admin manager added successfully!\n\n"
            f"🆔 Manager ID: {manager_id}\n"
            f"👤 Added by: {user.id}"
        )
    else:
        await update.message.reply_text(
            "❌ Failed to add manager. They may already be an admin or manager."
        )


async def admin_remove_manager_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: Remove an admin manager"""
    user = update.effective_user
    
    if not is_admin(user.id):
        await update.message.reply_text("⛔ This command is only for super admins!")
        return
    
    if not context.args:
        await update.message.reply_text(
            "Usage: /removemanager <telegram_id>\n"
            "Example: /removemanager 123456789"
        )
        return
    
    try:
        manager_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Telegram ID must be a number!")
        return
    
    if remove_admin_manager(manager_id):
        await update.message.reply_text(
            f"✅ Admin manager removed successfully!\n\n"
            f"🆔 Manager ID: {manager_id}"
        )
    else:
        await update.message.reply_text(
            "❌ Manager not found or cannot be removed."
        )


async def admin_list_managers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: List all admin managers"""
    user = update.effective_user
    
    if not is_admin(user.id):
        await update.message.reply_text("⛔ This command is only for admins!")
        return
    
    managers = get_admin_managers()
    
    if not managers:
        await update.message.reply_text(
            "📋 No admin managers configured.\n\n"
            f"<b>Super Admins (from env):</b> {', '.join(map(str, ADMIN_IDS))}"
        )
        return
    
    message = "<b>👥 Admin Managers</b>\n\n"
    
    for manager_id in managers:
        info = ADMIN_MANAGERS.get(manager_id, {})
        added_at = info.get("added_at", "Unknown")
        added_by = info.get("added_by", "Unknown")
        if isinstance(added_at, datetime):
            added_at = added_at.strftime("%Y-%m-%d %H:%M")
        message += (
            f"🆔 {manager_id}\n"
            f"   Added: {added_at}\n"
            f"   By: {added_by}\n\n"
        )
    
    message += f"\n<b>Super Admins (from env):</b> {', '.join(map(str, ADMIN_IDS))}"
    
    await update.message.reply_html(message)


# ============== AI COMMAND HANDLERS ==============

async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ask AI anything about Japanese"""
    if not context.args:
        await update.message.reply_html(
            "🤖 <b>Ask AI</b>\n\n"
            "Ask me anything about Japanese!\n\n"
            "<b>Examples:</b>\n"
            "/ask How do I use the particle は?\n"
            "/ask What's the difference between です and ます?\n"
            "/ask Explain te-form conjugation"
        )
        return
    
    question = " ".join(context.args)
    
    # Show typing indicator
    await update.message.chat.send_action(action="typing")
    
    try:
        response = ai_service.ask(question)
        await update.message.reply_html(f"🤖 <b>AI Response:</b>\n\n{response}")
    except Exception as e:
        logger.error(f"AI ask error: {e}")
        await update.message.reply_text("❌ Sorry, I couldn't process your question. Please try again!")


async def grammar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get AI explanation for a grammar point"""
    if not context.args:
        await update.message.reply_html(
            "📚 <b>Grammar Explainer</b>\n\n"
            "Get detailed explanations of Japanese grammar points!\n\n"
            "<b>Examples:</b>\n"
            "/grammar て-form\n"
            "/grammar passive voice\n"
            "/grammar たら vs ば"
        )
        return
    
    grammar_point = " ".join(context.args)
    
    # Show typing indicator
    await update.message.chat.send_action(action="typing")
    
    try:
        response = ai_service.explain_grammar(grammar_point)
        await update.message.reply_html(f"📚 <b>Grammar: {grammar_point}</b>\n\n{response}")
    except Exception as e:
        logger.error(f"AI grammar error: {e}")
        await update.message.reply_text("❌ Sorry, I couldn't explain that grammar point. Please try again!")


async def translate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Translate between English and Japanese"""
    if not context.args:
        await update.message.reply_html(
            "🌐 <b>Translator</b>\n\n"
            "Translate between English and Japanese!\n\n"
            "<b>Usage:</b>\n"
            "/translate <text> - Auto-detects language\n\n"
            "<b>Examples:</b>\n"
            "/translate Hello, how are you?\n"
            "/translate おはようございます"
        )
        return
    
    text = " ".join(context.args)
    
    # Detect if text is Japanese
    is_japanese = any('\u3040' <= char <= '\u309f' or '\u30a0' <= char <= '\u30ff' or '\u4e00' <= char <= '\u9fff' for char in text)
    
    # Show typing indicator
    await update.message.chat.send_action(action="typing")
    
    try:
        response = ai_service.translate(text, to_japanese=not is_japanese)
        await update.message.reply_html(f"🌐 <b>Translation:</b>\n\n{response}")
    except Exception as e:
        logger.error(f"AI translate error: {e}")
        await update.message.reply_text("❌ Sorry, I couldn't translate that. Please try again!")


async def practice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get AI-generated conversation practice"""
    user = update.effective_user
    db = get_db()
    
    try:
        user_service = UserService(db)
        db_user = user_service.get_user_by_telegram_id(user.id)
        
        # Determine user level
        if db_user:
            level = db_user.level
            if level <= 3:
                user_level = "beginner"
            elif level <= 6:
                user_level = "intermediate"
            else:
                user_level = "advanced"
        else:
            user_level = "beginner"
        
        # Get topic from args or use default
        if context.args:
            topic = " ".join(context.args)
        else:
            topic = "daily conversation"
        
        # Show typing indicator
        await update.message.chat.send_action(action="typing")
        
        try:
            response = ai_service.practice_conversation(topic, user_level)
            await update.message.reply_html(f"🗣️ <b>Conversation Practice: {topic}</b>\n\n{response}")
        except Exception as e:
            logger.error(f"AI practice error: {e}")
            await update.message.reply_text("❌ Sorry, I couldn't generate practice. Please try again!")
    finally:
        db.close()


async def tips_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get AI study tips"""
    # Show typing indicator
    await update.message.chat.send_action(action="typing")
    
    try:
        response = ai_service.get_study_tips()
        await update.message.reply_html(f"💡 <b>Study Tips</b>\n\n{response}")
    except Exception as e:
        logger.error(f"AI tips error: {e}")
        await update.message.reply_text("❌ Sorry, I couldn't get study tips. Please try again!")


# ============== MAIN FUNCTION ==============

def main():
    """Start the bot"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not set!")
        return
    
    # Create application
    application = Application.builder().token(token).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("daily", daily_command))
    application.add_handler(CommandHandler("quiz", quiz_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("leaderboard", leaderboard_command))
    application.add_handler(CommandHandler("learned", learned_command))
    
    # Add AI command handlers
    application.add_handler(CommandHandler("ask", ask_command))
    application.add_handler(CommandHandler("grammar", grammar_command))
    application.add_handler(CommandHandler("translate", translate_command))
    application.add_handler(CommandHandler("practice", practice_command))
    application.add_handler(CommandHandler("tips", tips_command))
    
    # Add admin command handlers
    application.add_handler(CommandHandler("adminstats", admin_stats_command))
    application.add_handler(CommandHandler("adminusers", admin_users_command))
    application.add_handler(CommandHandler("userinfo", admin_userinfo_command))
    application.add_handler(CommandHandler("addxp", admin_addxp_command))
    application.add_handler(CommandHandler("inactive", admin_inactive_command))
    application.add_handler(CommandHandler("broadcast", admin_broadcast_command))
    application.add_handler(CommandHandler("adminhelp", admin_help_command))
    application.add_handler(CommandHandler("addmanager", admin_add_manager_command))
    application.add_handler(CommandHandler("removemanager", admin_remove_manager_command))
    application.add_handler(CommandHandler("listmanagers", admin_list_managers_command))
    
    # Add callback handlers
    application.add_handler(CallbackQueryHandler(handle_quiz_answer, pattern="^quiz_answer:"))
    application.add_handler(CallbackQueryHandler(handle_quiz_navigation, pattern="^quiz_"))
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    # Start the bot
    logger.info("Starting Telegram bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
