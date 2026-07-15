# 🚀 Deploy on Render (FREE - No Credit Card!)

This guide shows you how to deploy your Japanese Learning Bot on Render's **FREE Web Service** tier. No credit card required!

## ✅ What's Different?

- **Before**: Background Worker (requires credit card)
- **Now**: Web Service with Webhooks (FREE!)

**Trade-off**: Free web services spin down after 15 minutes of inactivity. First message after inactivity has ~30 second delay (bot needs to wake up).

---

## 📋 Prerequisites

1. **GitHub account** (free)
2. **Render account** (free - sign up with GitHub)
3. **Telegram Bot Token** (from @BotFather)
4. **Your Telegram ID** (from @userinfobot)

---

## 🚀 Deployment Steps

### Step 1: Push to GitHub

```bash
# Add all new files
git add .

# Commit
git commit -m "Add webhook support for Render free tier"

# Push
git push origin main
```

---

### Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Click **"Get Started for Free"**
3. Sign up with your **GitHub account**
4. Verify your email

---

### Step 3: Create New Web Service

1. In Render Dashboard, click **"New +"**
2. Select **"Web Service"**
3. Connect your **GitHub repository**
4. Click **"Connect"**

---

### Step 4: Configure Service

Fill in these details:

| Field | Value |
|-------|-------|
| **Name** | `japanese-learning-bot` (or your choice) |
| **Region** | Choose closest to you |
| **Branch** | `main` (or your default branch) |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Plan** | `Free` |

Click **"Create Web Service"**

---

### Step 5: Set Environment Variables

1. In your service dashboard, go to **"Environment"** tab
2. Click **"Add Environment Variable"** for each:

| Variable | Value | How to Get |
|----------|-------|------------|
| `TELEGRAM_BOT_TOKEN` | Your bot token | @BotFather on Telegram |
| `ADMIN_IDS` | Your Telegram ID | @userinfobot on Telegram |
| `WEBHOOK_URL` | `https://your-service-name.onrender.com/webhook` | Replace with your actual URL |

**How to find your WEBHOOK_URL:**
- After creating the service, Render gives you a URL like: `https://japanese-learning-bot-xxx.onrender.com`
- Your webhook URL is: `https://japanese-learning-bot-xxx.onrender.com/webhook`

3. Click **"Save Changes"**

---

### Step 6: Deploy!

1. Render will automatically build and deploy
2. Watch the logs in the **"Logs"** tab
3. Wait for: `🚀 Bot is ready!` message
4. **Done!** 🎉

---

## 🧪 Test Your Bot

1. Open Telegram
2. Find your bot (search for the username you created)
3. Send `/start`
4. Try `/daily` to get vocabulary
5. Try `/quiz` for a quiz

---

## 📊 Free Tier Limits

| Feature | Limit |
|---------|-------|
| **Cost** | FREE |
| **Uptime** | Spins down after 15 min inactivity |
| **Wake-up time** | ~30 seconds |
| **Disk** | 1GB |
| **Bandwidth** | 100GB/month |
| **Build minutes** | 500/month |

**Note**: The bot will sleep after 15 minutes of no activity. First message will wake it up (takes ~30 seconds). After that, it responds instantly!

---

## 🔧 Troubleshooting

### Bot not responding?

1. Check Render logs for errors
2. Verify `TELEGRAM_BOT_TOKEN` is correct
3. Verify `WEBHOOK_URL` is correct (must end with `/webhook`)
4. Make sure you messaged the correct bot

### Webhook not working?

Check webhook info:
```
Visit: https://your-service.onrender.com/webhook-info
```

### Bot sleeping?

This is normal on free tier! First message after inactivity wakes it up.

To keep it awake (optional):
- Use a service like UptimeRobot to ping your bot every 10 minutes
- Or just accept the 30-second wake-up delay

---

## 🔄 Updating Your Bot

Just push to GitHub:
```bash
git add .
git commit -m "Your changes"
git push origin main
```

Render will automatically redeploy!

---

## 📁 Files Changed

- `main.py` - New FastAPI web server
- `app/webhook_bot.py` - Webhook-compatible bot logic
- `render.yaml` - Updated for Web Service

---

## 🆘 Need Help?

1. Check Render logs first (Dashboard → Your Service → Logs)
2. Verify all environment variables are set
3. Make sure your bot token is correct

**Enjoy your FREE Japanese Learning Bot!** 🎌
