import logging
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.database.connection import SessionLocal
from app.services.vocabulary import VocabularyService
from app.services.formatter import MessageFormatter
from app.messaging.whatsapp import WhatsAppMessagingService

logger = logging.getLogger(__name__)

def daily_vocabulary_job():
    logger.info("Starting daily vocabulary job...")
    db = SessionLocal()
    try:
        vocab_service = VocabularyService(db)
        messaging_service = WhatsAppMessagingService()
        
        words = vocab_service.get_next_words()
        if not words:
            logger.info("No more words available in database.")
            return
            
        word_ids = [w.id for w in words]
        batch_number = vocab_service.mark_as_sent(word_ids)
        
        message = MessageFormatter.format_daily_message(batch_number, words)
        messaging_service.send_message(message)
        
        logger.info(f"Successfully sent batch {batch_number} with {len(words)} words.")
    except Exception as e:
        logger.error(f"Error in daily vocabulary job: {e}")
    finally:
        db.close()

def setup_scheduler():
    scheduler = BackgroundScheduler(timezone=os.getenv("TIMEZONE", "UTC"))
    # Schedule to run every day at 08:00 in the configured timezone
    trigger = CronTrigger(hour=8, minute=0)
    scheduler.add_job(daily_vocabulary_job, trigger=trigger)
    scheduler.start()
    logger.info("Scheduler started. Daily job scheduled at 08:00 %s.", os.getenv("TIMEZONE", "UTC"))
    return scheduler
