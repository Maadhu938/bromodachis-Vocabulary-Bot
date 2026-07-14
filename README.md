# 🎌 Japanese Learning Bot (Telegram Edition)

[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://docker.com)
[![Python](https://img.shields.io/badge/Python-3.11-green?logo=python)](https://python.org)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-blue?logo=telegram)](https://telegram.org)

A gamified Japanese vocabulary learning bot for Telegram with quizzes, XP system, streaks, and leaderboards! Built with Python, Docker, and deployed on Render.

## ✨ Features

### 🎮 Gamification
- **XP System** - Earn XP for learning words and taking quizzes
- **10 Levels** - From Beginner (🔰) to Grandmaster (🌟)
- **Streak Tracking** - Daily login streaks with bonus XP
- **Global Leaderboards** - Compete with other learners

### 📚 Learning
- **Daily Vocabulary** - JLPT N5 words delivered daily
- **Interactive Quizzes** - 3 question types with instant feedback
- **Progress Tracking** - Personal stats and achievements
- **700+ Words** - Complete JLPT N5 vocabulary

### 🐳 DevOps
- **Docker Containerized** - Production-ready Docker setup
- **Cloud Deployed** - Ready for Render.com deployment
- **Persistent Storage** - SQLite database with volume mounting
- **Environment Config** - Easy configuration via env vars

## 🚀 Quick Start

### Prerequisites
- Python 3.11+ or Docker
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))

### Option 1: Docker (Recommended)

```bash
# Clone and setup
git clone <your-repo-url>
cd whatsapp-bot
cp .env.example .env
# Edit .env and add TELEGRAM_BOT_TOKEN

# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f
```

### Option 2: Local Python

```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env and add TELEGRAM_BOT_TOKEN

# Initialize database
python -c "from app.database.connection import init_db; init_db()"
python -m app.utils.load_csv

# Run bot
python run_telegram_bot.py
```

## 📱 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Register and start learning |
| `/daily` | Get today's vocabulary (+10 XP) |
| `/quiz` | Start quiz session (+5 XP per correct) |
| `/stats` | View your progress |
| `/leaderboard` | Global rankings |
| `/help` | Show commands |

## 🎮 How It Works

1. **Start** - Use `/start` to register
2. **Learn** - Get daily words with `/daily`
3. **Quiz** - Test knowledge with `/quiz`
4. **Earn XP** - Level up and compete!

### XP Rewards
| Action | XP |
|--------|-----|
| Daily vocabulary | 10 XP |
| Correct quiz answer | 5 XP |
| New word learned | 2 XP |
| 7-day streak | 50 XP bonus |
| 30-day streak | 200 XP bonus |

## 🐳 Docker Deployment

### Local Development
```bash
# Build
docker build -t japanese-bot .

# Run
docker run -d --env-file .env japanese-bot

# Or use docker-compose
docker-compose up -d
```

### Deploy to Render.com

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Connect to Render:**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Blueprint"
   - Connect your GitHub repo

3. **Set Environment Variables:**
   - Add `TELEGRAM_BOT_TOKEN` in Render dashboard

4. **Deploy:**
   - Render automatically deploys from `render.yaml`

See [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) for detailed instructions.

## 🏗️ Project Structure

```
whatsapp-bot/
├── app/
│   ├── telegram_bot.py          # Main bot
│   ├── database/
│   │   └── connection.py        # DB setup
│   ├── keyboards/
│   │   └── inline_keyboards.py  # Telegram buttons
│   ├── models/
│   │   ├── vocabulary.py        # Word model
│   │   └── user.py              # User models
│   ├── services/
│   │   ├── vocabulary.py        # Word service
│   │   ├── user_service.py      # XP/levels/streaks
│   │   └── quiz_service.py      # Quiz generation
│   └── utils/
│       ├── constants.py         # Config & messages
│       └── load_csv.py          # Data loader
├── data/
│   └── n5.csv                   # 700+ JLPT N5 words
├── scripts/
│   └── docker-entrypoint.sh     # Docker startup
├── Dockerfile                   # Docker image
├── docker-compose.yml           # Local dev
├── render.yaml                  # Render config
├── .dockerignore                # Docker exclusions
├── requirements.txt             # Dependencies
├── run_telegram_bot.py          # Entry point
└── README.md                    # This file
```

## 🛠️ Technologies

- **Python 3.11** - Core language
- **python-telegram-bot** - Telegram Bot API
- **SQLAlchemy** - Database ORM
- **SQLite** - Database
- **Docker** - Containerization
- **Render** - Cloud deployment

## 📊 Features for Job Applications

This project demonstrates:

✅ **Backend Development**
- Python application architecture
- Database design and ORM usage
- Service layer pattern

✅ **DevOps & Cloud**
- Docker containerization
- Docker Compose orchestration
- Cloud deployment (Render)
- Environment management
- Volume persistence

✅ **Bot Development**
- Telegram Bot API integration
- Interactive inline keyboards
- State management
- User session handling

✅ **Gamification**
- XP and leveling system
- Streak tracking
- Leaderboards
- Progress analytics

## 📝 Environment Variables

```env
TELEGRAM_BOT_TOKEN=your_token_from_botfather
WORDS_PER_DAY=3
TIMEZONE=Asia/Kolkata
```

## 🔒 Security

- Environment variables for secrets
- `.env` in `.gitignore`
- No hardcoded tokens
- Docker security best practices

## 📚 Documentation

- [README_TELEGRAM.md](README_TELEGRAM.md) - Detailed bot features
- [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) - Docker & deployment guide
- [TELEGRAM_BOT_PLAN.md](TELEGRAM_BOT_PLAN.md) - Implementation plan

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request

## 📄 License

MIT License - Feel free to use for your projects!

## 🙏 Credits

- Vocabulary data: JLPT N5 word list
- Built with: Python, Docker, Render
- Inspired by: Japanese learning community

---

**Happy Learning!** 頑張って！ (Ganbatte!) 💪🇯🇵

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)
