# 🐳 Docker Deployment on Render.com

This guide showcases Docker and Linux skills by deploying a production-ready Telegram bot using Docker on Render.com.

## 🏗️ Docker Architecture

### Multi-Stage Build (Production-Optimized)

```
┌─────────────────────────────────────────────────────────┐
│  Stage 1: Builder                                       │
│  ├─ Python 3.11-slim                                   │
│  ├─ Build dependencies (gcc, libsqlite3-dev)          │
│  ├─ Virtual environment creation                        │
│  └─ pip install requirements                            │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  Stage 2: Production                                    │
│  ├─ Python 3.11-slim (smaller, no build tools)         │
│  ├─ Runtime dependencies only                         │
│  ├─ Copy venv from builder                              │
│  ├─ Non-root user (security)                            │
│  ├─ Health checks                                       │
│  └─ Entrypoint script                                   │
└─────────────────────────────────────────────────────────┘
```

### Security Features

| Feature | Implementation | Purpose |
|---------|---------------|---------|
| Multi-stage build | Builder + Production stages | Smaller image size |
| Non-root user | `botuser` | Prevents privilege escalation |
| Minimal dependencies | Only runtime libs | Reduced attack surface |
| Health checks | curl to Telegram API | Container monitoring |
| Layer caching | Optimized COPY order | Faster builds |

---

## 📋 Prerequisites

- Docker installed locally
- Render.com account
- GitHub repository
- Telegram Bot Token
- Your Telegram ID

---

## 🚀 Deployment Steps

### Step 1: Build Docker Image Locally (Test First)

```bash
# Build the image
docker build -t japanese-learning-bot:latest .

# Check image size (should be ~150MB with multi-stage)
docker images japanese-learning-bot:latest

# Run locally to test
docker run -d \
  --name bot-test \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  japanese-learning-bot:latest

# View logs
docker logs -f bot-test

# Stop and remove
docker stop bot-test && docker rm bot-test
```

### Step 2: Push to Docker Hub (Optional but Recommended)

```bash
# Login to Docker Hub
docker login

# Tag image
docker tag japanese-learning-bot:latest YOUR_USERNAME/japanese-learning-bot:latest

# Push to Docker Hub
docker push YOUR_USERNAME/japanese-learning-bot:latest
```

### Step 3: Deploy on Render.com Using Docker

#### Option A: Using render.yaml (Blueprint)

Your `render.yaml` is already configured:

```yaml
services:
  - type: worker
    name: japanese-learning-bot
    runtime: docker
    dockerfilePath: ./Dockerfile
    envVars:
      - key: TELEGRAM_BOT_TOKEN
        sync: false
      - key: ADMIN_IDS
        sync: false
    disk:
      name: bot-data
      mountPath: /app/data
      sizeGB: 1
```

**Deploy:**
1. Push code to GitHub
2. Go to Render Dashboard → "New +" → "Blueprint"
3. Connect your repo
4. Set environment variables
5. Deploy!

#### Option B: Manual Docker Deployment

1. Go to [render.com](https://render.com)
2. Click "New +" → "Background Worker"
3. Configure:
   - **Name:** `japanese-learning-bot`
   - **Runtime:** Docker
   - **Repository:** Your GitHub repo
4. Set Environment Variables:
   ```
   TELEGRAM_BOT_TOKEN=your_token
   ADMIN_IDS=your_id
   ```
5. Add Disk:
   - **Name:** `bot-data`
   - **Mount Path:** `/app/data`
   - **Size:** 1 GB
6. Click "Create Background Worker"

---

## 🔧 Docker Commands Reference

### Build & Run

```bash
# Build image
docker build -t japanese-learning-bot:latest .

# Build with no cache (clean build)
docker build --no-cache -t japanese-learning-bot:latest .

# Run container
docker run -d \
  --name japanese-bot \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  --restart unless-stopped \
  japanese-learning-bot:latest

# Run with custom name
docker run -d --name my-bot japanese-learning-bot:latest
```

### Monitoring & Debugging

```bash
# View logs
docker logs japanese-bot
docker logs -f japanese-bot  # Follow mode

# View last 100 lines
docker logs --tail 100 japanese-bot

# Check container status
docker ps
docker ps -a  # Include stopped

# Container stats (CPU, Memory)
docker stats japanese-bot

# Execute commands inside container
docker exec -it japanese-bot /bin/bash

# Check health status
docker inspect --format='{{.State.Health.Status}}' japanese-bot
```

### Management

```bash
# Stop container
docker stop japanese-bot

# Start container
docker start japanese-bot

# Restart container
docker restart japanese-bot

# Remove container
docker rm japanese-bot

# Remove image
docker rmi japanese-learning-bot:latest

# Prune unused images
docker image prune -a

# View image layers
docker history japanese-learning-bot:latest
```

---

## 🐧 Linux Commands Inside Container

Once inside the container (`docker exec -it japanese-bot /bin/bash`):

```bash
# Check processes
ps aux

# Check disk usage
df -h

# Check memory
free -m

# View environment variables
env | grep -E 'TELEGRAM|ADMIN|PYTHON'

# Check file permissions
ls -la /app/

# View running user
whoami
id

# Check network connectivity
curl -I https://api.telegram.org

# View database
ls -la /app/data/
```

---

## 📊 Image Optimization Results

### Before (Single Stage)
- Size: ~400MB
- Includes build tools
- Security: Root user

### After (Multi-Stage)
- Size: ~150MB
- Only runtime dependencies
- Security: Non-root user
- **62% size reduction!**

---

## 🔒 Security Best Practices Implemented

1. **Non-root user**: Container runs as `botuser`, not root
2. **Minimal attack surface**: Only required packages installed
3. **No build tools in production**: gcc removed in final stage
4. **Health checks**: Container monitored for failures
5. **Layer caching**: Efficient build process
6. **Virtual environment**: Isolated Python packages

---

## 🐳 Docker Compose (Local Development)

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Scale (if needed)
docker-compose up -d --scale telegram-bot=2

# Stop
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Rebuild
docker-compose up -d --build
```

---

## 🎯 Showcase Skills

When presenting this project, highlight:

### Docker Skills
- ✅ Multi-stage builds for optimization
- ✅ Security hardening (non-root user)
- ✅ Health checks and monitoring
- ✅ Layer caching strategies
- ✅ Image size optimization (62% reduction)
- ✅ Docker Compose for orchestration

### Linux Skills
- ✅ Shell scripting (entrypoint)
- ✅ File permissions and user management
- ✅ Process management
- ✅ Network troubleshooting
- ✅ System monitoring

### DevOps Skills
- ✅ CI/CD ready configuration
- ✅ Environment variable management
- ✅ Persistent volume handling
- ✅ Cloud deployment (Render.com)
- ✅ Container orchestration

---

## 📈 Production Checklist

- [ ] Environment variables set in Render dashboard
- [ ] Disk mounted at `/app/data`
- [ ] Health checks passing
- [ ] Logs showing "Starting Telegram bot..."
- [ ] Bot responding to `/start` command
- [ ] Admin commands working (`/adminhelp`)

---

## 🆘 Troubleshooting

### Container won't start
```bash
# Check logs
docker logs japanese-bot

# Check environment variables
docker inspect japanese-bot | grep -A 20 Env

# Test locally first
docker run --rm -it --env-file .env japanese-learning-bot:latest
```

### Permission denied errors
```bash
# Check file ownership inside container
docker exec japanese-bot ls -la /app/

# Should show botuser:botuser
```

### Database not persisting
```bash
# Check volume mount
docker inspect japanese-bot | grep -A 10 Mounts

# Verify data directory
ls -la data/
```

---

## 📚 Additional Resources

- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Render Docker Deployments](https://render.com/docs/docker)
- [Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Container Security](https://docs.docker.com/engine/security/)

---

**Ready to deploy!** 🚀
