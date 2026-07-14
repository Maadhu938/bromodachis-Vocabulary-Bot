# 🎌 Bromodachis Japanese Learning Bot (Telegram Edition)

A gamified Japanese vocabulary learning bot for Telegram with quizzes, XP system, streaks, and leaderboards!

## ✨ Features

### 🎮 Gamification
- **XP System** - Earn XP for learning words and taking quizzes
- **Level System** - 10 levels from Beginner to Grandmaster
- **Streak Tracking** - Daily login streaks with bonus XP
- **Leaderboards** - Compete with other learners globally

### 📚 Learning
- **Daily Vocabulary** - Get new JLPT N5 words every day
- **Interactive Quizzes** - Multiple choice questions with 3 question types
- **Progress Tracking** - See words learned, quiz accuracy, and more
- **Personal Stats** - Detailed statistics on your learning journey

### 🎯 Quiz Types
1. **Meaning → Japanese** - Given English meaning, select Japanese word
2. **Japanese → Meaning** - Given Japanese word, select English meaning
3. **Reading → Expression** - Given reading (hiragana), select kanji/kana

## 🚀 Setup

### 1. Create Telegram Bot
1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow instructions
3. Copy your bot token

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
copy .env.example .env
```

Edit `.env` and add your bot token:
```
TELEGRAM_BOT_TOKEN=your_token_here
WORDS_PER_DAY=3
TIMEZONE=Asia/Kolkata
```

### 4. Initialize Database
```bash
python -c "from app.database.connection import init_db; init_db()"
python -m app.utils.load_csv
```

### 5. Run the Bot
```bash
python -m app.telegram_bot
```

## 📱 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Register and start learning |
| `/daily` | Get today's vocabulary words |
| `/quiz` | Start a quiz session (5 questions) |
| `/stats` | View your stats, XP, and streak |
| `/leaderboard` | See global rankings |
| `/help` | Show help message |
| `/about` | Bot information |

## 🎮 How It Works

### Getting Started
1. Start the bot with `/start`
2. Get your first words with `/daily`
3. Take quizzes with `/quiz`
4. Check your progress with `/stats`

### Earning XP
| Action | XP Reward |
|--------|-----------|
| Daily vocabulary | 10 XP |
| Correct quiz answer | 5 XP |
| New word learned | 2 XP |
| 7-day streak bonus | 50 XP |
| 30-day streak bonus | 200 XP |

### Level Progression
| Level | Title | XP Required |
|-------|-------|-------------|
| 1 | 🔰 Beginner | 0 |
| 2 | 📚 Student | 100 |
| 3 | ✏️ Learner | 250 |
| 4 | 📝 Intermediate | 475 |
| 5 | 📖 Advanced | 812 |
| 6 | 🎓 Expert | 1,318 |
| 7 | 🏆 Master | 2,077 |
| 8 | 👑 Sensei | 3,216 |
| 9 | ⭐ Legend | 4,924 |
| 10 | 🌟 Grandmaster | 7,386 |

## 🏗️ Project Structure

```
app/
├── telegram_bot.py          # Main bot entry point
├── models/
│   ├── vocabulary.py        # Vocabulary model
│   ├── sent_words.py         # Sent words tracking
│   └── user.py              # User, UserWord, QuizResult models
├── services/
│   ├── vocabulary.py        # Vocabulary service
│   ├── user_service.py      # User management & gamification
│   └── quiz_service.py      # Quiz generation
├── keyboards/
│   └── inline_keyboards.py  # Telegram inline keyboards
├── utils/
│   ├── constants.py         # XP values, messages, etc.
│   └── load_csv.py          # CSV to DB loader
└── database/
    └── connection.py        # Database connection

data/
└── n5.csv                   # JLPT N5 vocabulary (700+ words)
```

## 🔄 Migration from WhatsApp

This bot replaces the WhatsApp version with:
- ✅ No Evolution API needed
- ✅ Direct user interaction
- ✅ Much faster response times
- ✅ Better user experience with inline keyboards
- ✅ Individual user progress tracking
- ✅ Gamification features

## 🛠️ Development

### Adding New Features
1. Add models to `app/models/`
2. Add services to `app/services/`
3. Add handlers to `app/telegram_bot.py`
4. Update keyboards in `app/keyboards/inline_keyboards.py`

### Database Migrations
If you modify models, reinitialize:
```bash
# Backup first!
copy vocab.db vocab.db.backup

# Delete old DB and reinitialize
del vocab.db
python -c "from app.database.connection import init_db; init_db()"
python -m app.utils.load_csv
```

## 📝 License

MIT License - Feel free to use and modify!

## 🙏 Credits

- Vocabulary data: JLPT N5 word list
- Built with: python-telegram-bot, SQLAlchemy
- Inspired by: Bromodachis learning community

---

**Happy Learning!** 頑張って！ (Ganbatte!) 💪🇯🇵
