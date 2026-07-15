# UptimeRobot Setup Guide for Bromodachis Bot

## 🌐 Your Render URL
**URL:** https://bromodachis-vocabulary-bot.onrender.com

## 📋 UptimeRobot Configuration

### Step 1: Sign Up/Login
1. Go to https://uptimerobot.com/
2. Sign up for a free account (or login if you have one)

### Step 2: Add New Monitor
1. Click **"Add New Monitor"**
2. Configure as follows:

| Setting | Value |
|---------|-------|
| **Monitor Type** | HTTP(s) |
| **Friendly Name** | Bromodachis Vocabulary Bot |
| **URL** | `https://bromodachis-vocabulary-bot.onrender.com/health` |
| **Monitoring Interval** | 5 minutes (free tier) |
| **Monitor Timeout** | 30 seconds |

### Step 3: Alert Settings (Optional)
- Add your email for notifications
- You can also add Telegram, Discord, Slack webhooks

### Step 4: Save Monitor
Click "Create Monitor"

## ✅ Health Check Endpoints Available

Your bot has these endpoints for monitoring:

1. **Root Endpoint**
   - URL: `https://bromodachis-vocabulary-bot.onrender.com/`
   - Returns: Bot status and webhook info

2. **Health Check** (Recommended for UptimeRobot)
   - URL: `https://bromodachis-vocabulary-bot.onrender.com/health`
   - Returns: `{"status": "healthy", "bot_initialized": true/false}`

3. **Webhook Info**
   - URL: `https://bromodachis-vocabulary-bot.onrender.com/webhook-info`
   - Returns: Detailed webhook configuration

## 🔧 Why Use UptimeRobot?

Render free tier spins down after 15 minutes of inactivity. UptimeRobot will:
- Ping your bot every 5 minutes to keep it awake
- Send you alerts if the bot goes down
- Track uptime statistics

## 📱 Mobile App

Download the UptimeRobot mobile app:
- iOS: https://apps.apple.com/app/uptimerobot/id1101683093
- Android: https://play.google.com/store/apps/details?id=com.uptimerobot.app

## 📝 Notes

- Free tier allows 50 monitors
- 5-minute monitoring interval on free tier
- Email notifications are free
- SMS notifications require paid plan

---

**Your bot is ready for 24/7 monitoring! 🎌**
