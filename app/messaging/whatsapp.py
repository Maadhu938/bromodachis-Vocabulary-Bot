import requests
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class WhatsAppMessagingService:
    """
    Sends messages to a WhatsApp group via the Evolution API (self-hosted Docker container).
    Docs: https://doc.evolution-api.com
    """

    def __init__(self):
        self.base_url = os.getenv("EVOLUTION_API_URL", "http://localhost:8080")
        self.api_key = os.getenv("EVOLUTION_API_KEY", "")
        self.instance_name = os.getenv("EVOLUTION_INSTANCE_NAME", "bromodachis")
        self.group_id = os.getenv("WHATSAPP_GROUP_ID", "")

    def send_message(self, message: str) -> bool:
        url = f"{self.base_url}/message/sendText/{self.instance_name}"
        headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "number": self.group_id,
            "text": message
        }

        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Sending WhatsApp message (attempt {attempt}/{max_retries})...")
                response = requests.post(url, json=payload, headers=headers, timeout=15)
                response.raise_for_status()
                logger.info("Message sent successfully!")
                return True
            except requests.exceptions.ConnectionError:
                logger.error(f"Attempt {attempt}: Cannot connect to Evolution API at {self.base_url}. Is Docker running?")
            except requests.exceptions.Timeout:
                logger.error(f"Attempt {attempt}: Request timed out.")
            except requests.exceptions.HTTPError as e:
                logger.error(f"Attempt {attempt}: HTTP error: {e.response.status_code} - {e.response.text}")
                break  # Don't retry on HTTP errors (e.g., 401 bad API key)
            except Exception as e:
                logger.error(f"Attempt {attempt}: Unexpected error: {e}")

        logger.error("All retry attempts failed. Message was NOT sent.")
        return False
