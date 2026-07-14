# Telegram Bot Conversion Plan - Gamification Edition 🎮

## Features to Implement

### 1. Core Conversion
- Replace WhatsApp/Evolution API with python-telegram-bot
- Keep existing vocabulary database (SQLite)
- Add user management system

### 2. Quiz System 🎯
- Multiple choice quizzes (4 options)
- Question types: Meaning → Japanese, Japanese → Meaning, Reading → Expression
- Immediate feedback with explanations
- Difficulty levels based on JLPT

### 3. XP & Level System 📈
- XP for: daily vocabulary, correct quiz answers, streaks
- Levels: Beginner → Intermediate → Advanced → Master
- XP calculation:
  - Daily vocab: 10 XP
  - Correct quiz answer: 5 XP
  - 7-day streak bonus: 50 XP
  - 30-day streak bonus: 200 XP

### 4. Leaderboards 🏆
- Global leaderboard (all users)
- Weekly leaderboard
- Personal rank display
- Top 10 display with medals 🥇🥈🥉

### 5. Streak Tracking 🔥
- Daily login tracking
- Streak display with fire emoji
- Streak loss warning
- Streak recovery (1 day grace period)

### 6. Commands
- `/start` - Welcome + user registration
- `/daily` - Get today's vocabulary
- `/quiz` - Start a quiz session
- `/stats` - Personal stats (XP, level, streak)
- `/leaderboard` - Show rankings
- `/help` - Command list

## Database Schema Additions

### users table
- user_id (Telegram ID)
- username
- xp
- level
- current_streak
- longest_streak
- last_active_date
- created_at

### quiz_results table
- id
- user_id
- vocabulary_id
- correct
- answered_at

### user_words table (for tracking learned words)
- user_id
- vocabulary_id
- learned_at
- review_count

## File Structure
```
app/
├── main.py                    # Telegram bot entry point
├── config.py                  # Bot configuration
├── database/
│   ├── connection.py          # Existing (modified)
│   └── models.py              # All models combined
├── handlers/
│   ├── __init__.py
│   ├── start.py               # /start command
│   ├── daily.py               # /daily command
│   ├── quiz.py                # /quiz command
│   ├── stats.py               # /stats command
│   ├── leaderboard.py         # /leaderboard command
│   └── help.py                # /help command
├── services/
│   ├── vocabulary.py          # Existing (modified)
│   ├── user_service.py        # User management
│   ├── quiz_service.py        # Quiz generation
│   ├── xp_service.py          # XP/Level calculations
│   └── leaderboard_service.py # Leaderboard logic
├── keyboards/
│   └── inline_keyboards.py    # Button layouts
└── utils/
    ├── constants.py           # XP values, level thresholds
    └── helpers.py             # Utility functions
```

## Implementation Steps
1. Set up python-telegram-bot dependencies
2. Create user models and migration
3. Implement core bot handlers
4. Add quiz system with inline keyboards
5. Implement XP/level tracking
6. Add leaderboard functionality
7. Add streak tracking
8. Test and polish
