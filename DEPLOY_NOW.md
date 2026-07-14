# 🚀 Deploy to Production - Exact Steps

Follow these steps in order to deploy your bot to production on Render.com.

---

## ✅ Pre-Deployment Checklist

- [ ] You have a Telegram account
- [ ] You have a GitHub account
- [ ] You have Docker installed (optional, for local testing)

---

## Step 1: Get Your Credentials (Do This First!)

### 1.1 Get Bot Token from @BotFather

1. Open **Telegram** app on your phone or desktop
2. Search for **@BotFather**
3. Click "Start" or send `/start`
4. Send `/newbot`
5. Enter a name for your bot (e.g., "Japanese Learning Bot")
6. Enter a username (must end in 'bot', e.g., "japanese_vocab_bot")
7. **Copy the token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 1.2 Get Your Telegram ID from @userinfobot

1. In Telegram, search for **@userinfobot**
2. Click "Start"
3. It will show your ID (looks like: `123456789`)
4. **Copy this number**

---

## Step 2: Update Environment Variables

Open the `.env` file and replace the placeholders:

```bash
# Open .env file
code .env
```

Replace:
```env
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
ADMIN_IDS=YOUR_TELEGRAM_ID_HERE
```

With your actual values:
```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_IDS=123456789
```

**Save the file.**

---

## Step 3: Test Locally with Docker (Optional but Recommended)

```bash
# Build the Docker image
docker build -t japanese-learning-bot:latest .

# Run the container
docker run -d \
  --name bot-test \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  japanese-learning-bot:latest

# Check if it's running
docker ps

# View logs
docker logs -f bot-test

# Stop the test container
docker stop bot-test && docker rm bot-test
```

---

## Step 4: Push to GitHub

```bash
# Check git status
git status

# Add all files
git add .

# Commit
git commit -m "Production ready with Docker and admin manager"

# Push to GitHub
git push origin main
```

---

## Step 5: Deploy on Render.com

### 5.1 Create Render Account

1. Go to [render.com](https://render.com)
2. Click "Get Started for Free"
3. Sign up with your **GitHub** account
4. Verify your email

### 5.2 Deploy Using Blueprint

1. In Render Dashboard, click **"New +"** (top right)
2. Select **"Blueprint"**
3. Find your GitHub repository and click **"Connect"**
4. Render will detect the `render.yaml` file automatically
5. Click **"Apply"**

### 5.3 Set Environment Variables

1. Click on your new service ("japanese-learning-bot")
2. Go to **"Environment"** tab on the left
3. Click **"Add Environment Variable"**
4. Add these two variables:
   - **Key:** `TELEGRAM_BOT_TOKEN` | **Value:** your bot token
   - **Key:** `ADMIN_IDS` | **Value:** your Telegram ID
5. Click **"Save Changes"**

### 5.4 Deploy

1. Render will automatically start deploying
2. Click **"Logs"** tab to watch the deployment
3. Wait for the message: "Starting Telegram bot..."
4. **Done!** 🎉

---

## Step 6: Test Your Bot

1. Open Telegram
2. Search for your bot (the username you created)
3. Click "Start" or send `/start`
4. Try these commands:
   - `/daily` - Get daily vocabulary
   - `/quiz` - Start a quiz
   - `/stats` - View your stats
   - `/adminhelp` - See admin commands (only works for you)

---

## Step 7: Add Admin Managers (Optional)

To give someone else admin access:

1. Get their Telegram ID (ask them to message @userinfobot)
2. Send this command to your bot:
   ```
   /addmanager 987654321
   ```
   (Replace with their actual ID)

3. They can now use all admin commands!

---

## 🆘 Troubleshooting

### Bot not responding?
- Check Render logs for errors
- Verify `TELEGRAM_BOT_TOKEN` is correct
- Make sure you messaged the right bot

### Admin commands not working?
- Check `ADMIN_IDS` is set correctly
- Get your ID again from @userinfobot
- Redeploy after fixing

### Deployment failed?
- Check `render.yaml` syntax
- Make sure all files are pushed to GitHub
- Check Render service logs

---

## 📊 What You Get

After deployment:
- ✅ Bot running 24/7 on Render.com (free tier)
- ✅ 1GB persistent disk for database
- ✅ Health checks monitoring
- ✅ Auto-restart on failure
- ✅ Admin manager system
- ✅ All admin commands working

---

## 🔗 Useful Links

- **Render Dashboard:** https://dashboard.render.com
- **Your Bot:** https://t.me/YOUR_BOT_USERNAME
- **BotFather:** https://t.me/BotFather
- **User Info Bot:** https://t.me/userinfobot

---

**Total Time:** ~15 minutes

**Ready to deploy!** 🚀
