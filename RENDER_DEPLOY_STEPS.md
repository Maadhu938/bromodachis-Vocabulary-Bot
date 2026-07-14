# 🚀 Render.com Deployment Steps

## Step 1: Get Your Credentials (Do This First!)

### Get Bot Token from @BotFather
1. Open Telegram app
2. Search for **@BotFather**
3. Click "Start" or send `/start`
4. Send `/newbot`
5. Follow instructions:
   - Enter bot name (e.g., "Japanese Learning Bot")
   - Enter username (must end in 'bot', e.g., "japanese_learning_bot")
6. **Copy the token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Get Your Telegram ID from @userinfobot
1. Search for **@userinfobot**
2. Click "Start"
3. It will show your ID (looks like: `123456789`)
4. **Copy this number**

---

## Step 2: Update .env File

Open `.env` file and replace the placeholders:

```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_IDS=123456789
```

(Use your actual values, not these examples!)

---

## Step 3: Push to GitHub

```bash
# Initialize git (if not done)
git init

# Add all files
git add .

# Commit
git commit -m "Production ready with admin manager"

# Add your GitHub repo (replace with your actual repo URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push to GitHub
git push -u origin main
```

---

## Step 4: Deploy on Render.com

### 4.1 Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Verify your email

### 4.2 Deploy Using Blueprint
1. In Render Dashboard, click **"New +"**
2. Select **"Blueprint"**
3. Connect your GitHub repository
4. Render will detect `render.yaml` automatically
5. Click **"Apply"**

### 4.3 Set Environment Variables
1. In Render Dashboard, click your new service
2. Go to **"Environment"** tab
3. Add these variables:
   - `TELEGRAM_BOT_TOKEN` = your bot token
   - `ADMIN_IDS` = your Telegram ID
4. Click **"Save Changes"**

### 4.4 Deploy
1. Render will automatically deploy
2. Watch the logs in the **"Logs"** tab
3. Wait for "Starting Telegram bot..." message
4. **Done!** 🎉

---

## Step 5: Test Your Bot

1. Open Telegram
2. Find your bot (search for the username you created)
3. Send `/start`
4. Send `/adminhelp` to see admin commands
5. Try `/addmanager <friend_telegram_id>` to add another admin

---

## Troubleshooting

### Bot not responding?
- Check Render logs for errors
- Verify TELEGRAM_BOT_TOKEN is correct
- Make sure you messaged the correct bot

### Admin commands not working?
- Check ADMIN_IDS is set correctly
- Get your ID again from @userinfobot
- Redeploy after fixing

### Deployment failed?
- Check `render.yaml` syntax
- Ensure all files are pushed to GitHub
- Check Render service logs

---

## Useful Render Commands

```bash
# View logs in dashboard
# Just go to: Dashboard → Your Service → Logs

# Restart service
# Dashboard → Your Service → Manual Deploy → Deploy Latest Commit

# Update environment variables
# Dashboard → Your Service → Environment → Edit
```

---

## Free Tier Limits (Render)
- **Uptime**: 24/7 (never sleeps!)
- **Disk**: 1GB (included in config)
- **Bandwidth**: 100GB/month
- **Build time**: 500 minutes/month

Perfect for a Telegram bot! ✨

---

**Need help?** Check the logs in Render Dashboard first - they show exactly what's happening!
