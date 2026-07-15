"""
FastAPI Web Server for Telegram Bot Webhook
Deploy this on Render as a Web Service (FREE tier - no credit card needed!)
"""
import os
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import asyncio

from app.webhook_bot import setup_application, process_update
from app.database.connection import init_db
from app.utils.load_csv import load_csv_to_db

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global bot application
bot_app = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    global bot_app
    
    # Startup
    logger.info("🎌 Starting Japanese Learning Bot...")
    
    # Initialize database
    logger.info("📊 Initializing database...")
    init_db()
    
    # Load vocabulary data
    logger.info("📚 Loading vocabulary data...")
    load_csv_to_db("data/n5.csv")
    
    # Setup bot application
    logger.info("🤖 Setting up Telegram bot...")
    bot_app = await setup_application()
    
    # Set webhook
    webhook_url = os.getenv("WEBHOOK_URL")
    if webhook_url:
        logger.info(f"🔗 Setting webhook to: {webhook_url}")
        await bot_app.bot.set_webhook(url=webhook_url)
        logger.info("✅ Webhook set successfully!")
    else:
        logger.warning("⚠️ WEBHOOK_URL not set. Please set it in environment variables.")
    
    logger.info("🚀 Bot is ready!")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down bot...")
    if bot_app:
        await bot_app.stop()


# Create FastAPI app
app = FastAPI(
    title="Japanese Learning Bot",
    description="Telegram Bot for Japanese Vocabulary Learning",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "status": "✅ Bot is running!",
        "bot": "Japanese Learning Bot 🎌",
        "webhook": "Active" if bot_app else "Not initialized"
    }


@app.get("/health")
@app.post("/health")
@app.head("/health")
async def health_check(request: Request = None):
    """Health check endpoint - supports GET, POST, and HEAD for UptimeRobot compatibility"""
    return {
        "status": "healthy",
        "bot_initialized": bot_app is not None,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/webhook")
async def webhook(request: Request):
    """Receive webhook updates from Telegram"""
    try:
        # Get JSON data from request
        update_data = await request.json()
        logger.debug(f"Received update: {update_data}")
        
        # Process the update
        await process_update(update_data)
        
        return Response(status_code=200)
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.get("/webhook-info")
async def webhook_info():
    """Get current webhook info (admin only)"""
    if not bot_app:
        return {"error": "Bot not initialized"}
    
    try:
        info = await bot_app.bot.get_webhook_info()
        return {
            "url": info.url,
            "has_custom_certificate": info.has_custom_certificate,
            "pending_update_count": info.pending_update_count,
            "ip_address": info.ip_address,
            "last_error_date": info.last_error_date,
            "last_error_message": info.last_error_message,
            "max_connections": info.max_connections,
            "allowed_updates": info.allowed_updates
        }
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment variable (Render sets this)
    port = int(os.getenv("PORT", 8000))
    
    logger.info(f"Starting server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
