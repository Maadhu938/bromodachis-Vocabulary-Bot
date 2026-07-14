# 🐳 Docker Deployment Guide

This guide covers deploying the Japanese Learning Bot using Docker and Render.com.

## 📋 Prerequisites

- Docker installed locally (for testing)
- Docker Hub account (optional, for image hosting)
- Render.com account (for deployment)
- Telegram Bot Token (from @BotFather)

## 🏗️ Local Docker Development

### 1. Build the Docker Image

```bash
# Build the image
docker build -t japanese-learning-bot .

# Or use docker-compose
docker-compose build
```

### 2. Run Locally with Docker

```bash
# Create .env file first
cp .env.example .env
# Edit .env and add your TELEGRAM_BOT_TOKEN

# Run with docker-compose (recommended)
docker-compose up -d

# Or run directly with docker
docker run -d \
  --name japanese-bot \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  japanese-learning-bot
```

### 3. View Logs

```bash
# View logs
docker-compose logs -f

# Or for specific container
docker logs -f japanese-learning-bot
```

### 4. Stop the Container

```bash
docker-compose down

# Or
docker stop japanese-learning-bot
docker rm japanese-learning-bot
```

## 🚀 Deploy to Render.com

### Method 1: Using render.yaml (Recommended)

1. **Push code to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin your-github-repo-url
   git push -u origin main
   ```

2. **Connect to Render:**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml`

3. **Set Environment Variables:**
   - In Render dashboard, go to your service
   - Click "Environment" tab
   - Add `TELEGRAM_BOT_TOKEN` with your bot token

4. **Deploy:**
   - Render will automatically deploy
   - Monitor logs in the "Logs" tab

### Method 2: Manual Deployment

1. **Create New Service:**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Background Worker"

2. **Configure Service:**
   - **Name:** `japanese-learning-bot`
   - **Runtime:** Docker
   - **Repository:** Connect your GitHub repo
   - **Branch:** main

3. **Set Environment Variables:**
   ```
   TELEGRAM_BOT_TOKEN=your_token_here
   WORDS_PER_DAY=3
   TIMEZONE=Asia/Kolkata
   PYTHONUNBUFFERED=1
   ```

4. **Add Disk (for persistent database):**
   - Click "Disks" tab
   - Add disk:
     - **Name:** `bot-data`
     - **Mount Path:** `/app/data`
     - **Size:** 1 GB

5. **Deploy:**
   - Click "Create Background Worker"
   - Render will build and deploy automatically

## 🔧 Docker Commands Reference

```bash
# Build image
docker build -t japanese-learning-bot .

# Run container
docker run -d --name bot --env-file .env japanese-learning-bot

# View logs
docker logs -f bot

# Stop container
docker stop bot

# Remove container
docker rm bot

# Remove image
docker rmi japanese-learning-bot

# Shell into container
docker exec -it bot /bin/bash

# Check running containers
docker ps

# Check all containers (including stopped)
docker ps -a
```

## 📁 Project Structure with Docker

```
whatsapp-bot/
├── Dockerfile                   # Docker image definition
├── docker-compose.yml           # Local development
├── render.yaml                  # Render deployment config
├── scripts/
│   └── docker-entrypoint.sh     # Container startup script
├── .dockerignore                # Files to exclude from Docker
├── .env                         # Environment variables (not in git)
├── .env.example                 # Example env file
├── requirements.txt             # Python dependencies
├── run_telegram_bot.py          # Entry point
└── app/                         # Application code
```

## 🐛 Troubleshooting

### Container won't start
```bash
# Check logs
docker logs japanese-learning-bot

# Check if env vars are set
docker inspect japanese-learning-bot | grep -A 10 Env
```

### Database issues
```bash
# Shell into container
docker exec -it japanese-learning-bot /bin/bash

# Check database
ls -la /app/
cat /app/vocab.db
```

### Rebuild from scratch
```bash
# Remove everything
docker-compose down -v
docker rmi japanese-learning-bot

# Rebuild
docker-compose up --build -d
```

## 🔒 Security Best Practices

1. **Never commit `.env` file** - It's in `.gitignore`
2. **Use Render Environment Variables** - Don't hardcode tokens
3. **Keep base image updated** - Use `python:3.11-slim` or newer
4. **Scan for vulnerabilities:**
   ```bash
   docker scan japanese-learning-bot
   ```

## 📊 Monitoring

### On Render:
- View logs in Dashboard → Logs tab
- Set up alerts for service downtime
- Monitor disk usage (1GB should be plenty)

### Local:
```bash
# Resource usage
docker stats japanese-learning-bot

# Health check
docker inspect --format='{{.State.Health.Status}}' japanese-learning-bot
```

## 🔄 CI/CD Pipeline (Optional)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Render

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to Render
      uses: johnbeynon/render-deploy-action@v0.0.8
      with:
        service-id: ${{ secrets.RENDER_SERVICE_ID }}
        api-key: ${{ secrets.RENDER_API_KEY }}
```

## 💡 Tips for Job Applications

When showcasing this project:

1. **Mention Technologies:**
   - Docker containerization
   - Linux-based deployment
   - Cloud deployment (Render.com)
   - Environment variable management
   - Persistent volume management

2. **Highlight Features:**
   - Multi-stage Docker builds
   - Health checks and monitoring
   - Automated deployment pipeline
   - Production-ready configuration

3. **Show Understanding:**
   - Explain why Docker is used
   - Discuss container orchestration
   - Mention security considerations
   - Talk about scalability

---

**Good luck with your job application!** 🚀
