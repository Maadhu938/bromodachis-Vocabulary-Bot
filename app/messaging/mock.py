import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

class MockMessagingService:
    """
    A mock service that logs the message instead of sending it.
    Can be replaced with Telegram/WhatsApp API later.
    """
    
    def send_message(self, message: str) -> bool:
        logger.info("\n--- MOCK MESSAGE START ---\n%s\n--- MOCK MESSAGE END ---", message)
        return True
