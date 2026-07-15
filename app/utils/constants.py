"""Constants for the Telegram Japanese Learning Bot"""
from datetime import time

# XP Rewards
XP_DAILY_VOCABULARY = 10
XP_CORRECT_QUIZ_ANSWER = 5
XP_STREAK_BONUS_7_DAYS = 50
XP_STREAK_BONUS_30_DAYS = 200
XP_NEW_WORD_LEARNED = 2

# Level thresholds (cumulative XP needed)
# Formula: 100 * (1.5 ^ (level - 1))
LEVEL_THRESHOLDS = {
    1: 0,      # Beginner
    2: 100,    # Student
    3: 250,    # Learner
    4: 475,    # Intermediate
    5: 812,    # Advanced
    6: 1318,   # Expert
    7: 2077,   # Master
    8: 3216,   # Sensei
    9: 4924,   # Legend
    10: 7386,  # Grandmaster
}

# Level titles
LEVEL_TITLES = {
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

# Quiz settings
QUIZ_OPTIONS_COUNT = 4
QUIZ_QUESTIONS_PER_SESSION = 5

# Daily vocabulary settings
WORDS_PER_DAY_DEFAULT = 10
DAILY_VOCAB_TIME = time(8, 0)  # 8:00 AM

# Streak settings
STREAK_GRACE_PERIOD_HOURS = 48  # Allow recovery within 48 hours

# Messages
WELCOME_MESSAGE = """
🎌 Welcome to <b>Bromodachis Japanese Bot</b>! 🇯🇵

I'm here to help you learn Japanese vocabulary and track your progress!

<b>What I can do:</b>
📚 Send daily vocabulary words
🎯 Quiz you on words you've learned
🤖 Answer your Japanese questions with Maddy AI
📊 Track your learning streak
🏆 Compete on leaderboards

<b>Commands:</b>
/daily - Get today's vocabulary
/quiz - Test your knowledge
/ask - Ask Maddy AI anything about Japanese
/stats - View your progress
/leaderboard - See top learners
/help - Show all commands

Let's start your Japanese learning journey! 頑張って！💪
"""

HELP_MESSAGE = """
<b>🎌 Bromodachis Japanese Bot Commands</b>

<b>Learning:</b>
/daily - Get today's vocabulary words
/quiz - Take a quiz (5 questions)
/learned - View words you've learned

<b>🤖 Maddy AI:</b>
/ask <question> - Ask Maddy AI anything about Japanese
/grammar <point> - Get grammar explanations
/translate <text> - Translate EN↔JP
/practice [topic] - Conversation practice
/tips - Get study tips

<b>Progress:</b>
/stats - Your stats, XP, level, and streak
/leaderboard - Global rankings

<b>Other:</b>
/help - Show this message
/about - Bot information

<b>Gamification:</b>
• Earn XP by studying daily and taking quizzes
• Maintain your streak for bonus XP
• Level up to unlock new titles
• Compete with other learners!

頑張って！ (Ganbatte!) 💪
"""

ABOUT_MESSAGE = """
<b>🎌 About Bromodachis Japanese Bot</b>

A gamified Japanese vocabulary learning bot with:
• JLPT N5 vocabulary (700+ words)
• Daily learning reminders
• Interactive quizzes
• XP and leveling system
• Leaderboards

<b>Version:</b> 2.0.0 (Telegram Edition)
<b>Data:</b> JLPT N5 Vocabulary

Made with ❤️ for Japanese learners!
"""

# Quiz question templates
QUIZ_TEMPLATES = {
    "meaning_to_jp": "What is the Japanese word for:\n\n<b>{meaning}</b>?",
    "jp_to_meaning": "What does <b>{expression}</b> mean?\n\nReading: ({reading})",
    "reading_to_expression": "Which word is read as:\n\n<b>{reading}</b>?"
}

# Streak emojis
STREAK_EMOJIS = {
    0: "❄️",
    1: "🔥",
    7: "🔥🔥",
    30: "🔥🔥🔥",
    100: "🔥🔥🔥🔥"
}

def get_streak_emoji(streak: int) -> str:
    """Get appropriate streak emoji"""
    if streak >= 100:
        return STREAK_EMOJIS[100]
    elif streak >= 30:
        return STREAK_EMOJIS[30]
    elif streak >= 7:
        return STREAK_EMOJIS[7]
    elif streak >= 1:
        return STREAK_EMOJIS[1]
    return STREAK_EMOJIS[0]
