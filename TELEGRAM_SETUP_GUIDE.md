# 📱 Complete Telegram Bot Setup Guide

Step-by-step guide to create your Telegram bot and connect it to this application.

---

## Step 1: Create Your Telegram Bot

### 1.1 Open Telegram and Find BotFather

1. **Open Telegram** on your phone or desktop
2. **Search for "@BotFather"** in the search bar
3. **Click on BotFather** (the one with the blue checkmark ✅)

### 1.2 Create a New Bot

1. **Send this command:**
   ```
   /newbot
   ```

2. **Choose a name for your bot:**
   - This is the display name users will see
   - Example: `Japanese Learning Bot`
   - Send it to BotFather

3. **Choose a username for your bot:**
   - Must end in "bot" (e.g., `myjapanesebot` or `my_japanese_bot`)
   - Must be unique (no spaces, lowercase only)
   - Example: `bromodachis_jp_bot`
   - Send it to BotFather

### 1.3 Get Your Bot Token

After you choose a username, BotFather will send you a message like this:

```
Done! Congratulations on your new bot. You will find it at t.me/bromodachis_jp_bot.

Use this token to access the HTTP API:
123456789:ABCdefGHIjklMNOpqrSTUvwxyz1234567890

Keep your token secure and store it safely, it can be used by anyone to control your bot.
```

**⚠️ IMPORTANT:**
- Copy the token (the long string with numbers and letters)
- **Keep it secret!** Anyone with this token can control your bot
- Save it somewhere safe - you'll need it in the next step

---

## Step 2: Configure Your Bot

### 2.1 Set Up Environment Variables

1. **Open your project folder** in VS Code or terminal

2. **Create the .env file:**
   ```bash
   # Windows
   copy .env.example .env
   
   # Mac/Linux
   cp .env.example .env
   ```

3. **Edit the .env file** and add your bot token:
   ```env
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxyz1234567890
   WORDS_PER_DAY=10
   TIMEZONE=Asia/Kolkata
   ```
   
   Replace `123456789:ABCdefGHIjklMNOpqrSTUvwxyz1234567890` with your actual token!

---

## Step 3: Run Your Bot

### Option A: Run with Docker (Recommended)

1. **Make sure Docker is running**

2. **Build and start the bot:**
   ```bash
   docker-compose up -d
   ```

3. **Check if it's running:**
   ```bash
   docker-compose logs -f
   ```
   
   You should see: "🎌 Starting Japanese Learning Bot..."

### Option B: Run with Python

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize the database:**
   ```bash
   python -c "from app.database.connection import init_db; init_db()"
   python -m app.utils.load_csv
   ```

3. **Run the bot:**
   ```bash
   python run_telegram_bot.py
   ```
   
   You should see: "🎌 Starting Bromodachis Japanese Learning Bot..."

---

## Step 4: Test Your Bot

### 4.1 Find Your Bot on Telegram

1. **Search for your bot's username** in Telegram
   - Example: `@bromodachis_jp_bot`

2. **Click "Start"** or send `/start`

3. **You should see a welcome message:**
   ```
   🎌 Welcome, [Your Name]! 🇯🇵
   
   I'm here to help you learn Japanese vocabulary...
   ```

### 4.2 Try the Commands

Send these commands to test:

- `/start` - Welcome message
- `/daily` - Get 10 vocabulary words
- `/quiz` - Start a quiz
- `/stats` - View your progress
- `/leaderboard` - See rankings
- `/help` - Show all commands

---

## Step 5: Deploy to Render (Optional)

### 5.1 Push to GitHub

1. **Create a GitHub repository** (if not done)

2. **Push your code:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

### 5.2 Deploy on Render

1. **Go to [render.com](https://render.com)** and sign up/login

2. **Click "New +"** → **"Blueprint"**

3. **Connect your GitHub repository**

4. **Set Environment Variable:**
   - Click on your service
   - Go to "Environment" tab
   - Add: `TELEGRAM_BOT_TOKEN` = your token

5. **Deploy!**
   - Render will automatically build and deploy
   - Check logs in the "Logs" tab

---

## 🔧 Troubleshooting

### Bot not responding?

1. **Check if bot is running:**
   ```bash
   docker-compose ps
   # or
   docker ps
   ```

2. **Check logs:**
   ```bash
   docker-compose logs -f
   ```

3. **Common issues:**
   - **"No module named 'telegram'"** → Run `pip install -r requirements.txt`
   - **"TELEGRAM_BOT_TOKEN not set"** → Check your .env file
   - **"Database error"** → Run the database initialization commands

### Token not working?

1. **Get a new token from BotFather:**
   - Message BotFather: `/revoke`
   - Select your bot
   - BotFather will give you a new token
   - Update your .env file with the new token

2. **Restart the bot:**
   ```bash
   docker-compose restart
   # or stop and start again
   docker-compose down
   docker-compose up -d
   ```

---

## 📋 BotFather Commands Reference

Useful commands when managing your bot:

| Command | Description |
|---------|-------------|
| `/newbot` | Create a new bot |
| `/token` | Get your bot's token |
| `/revoke` | Revoke and get new token |
| `/setname` | Change bot name |
| `/setdescription` | Change description |
| `/setabouttext` | Change about text |
| `/setuserpic` | Set bot profile picture |
| `/setcommands` | Set command list |
| `/deletebot` | Delete your bot |

---

## 🎉 You're Done!

Your Telegram bot is now:
- ✅ Created with BotFather
- ✅ Connected to your application
- ✅ Running locally or on Render
- ✅ Ready for users!

**Share your bot:** Send your bot's username (e.g., `@bromodachis_jp_bot`) to friends so they can learn Japanese too!

---

## 💡 Tips

1. **Keep your token secret** - Never share it or commit it to GitHub
2. **Use the .env file** - It's already in .gitignore so it won't be committed
3. **Monitor logs** - Check logs regularly to see if everything is working
4. **Test before deploying** - Always test locally before deploying to Render

**Happy bot building!** 🤖🇯🇵
