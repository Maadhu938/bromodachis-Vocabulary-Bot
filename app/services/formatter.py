from datetime import date
from typing import List
from app.models.vocabulary import Vocabulary

class MessageFormatter:
    @staticmethod
    def format_daily_message(batch_number: int, words: List[Vocabulary]) -> str:
        if not words:
            return "No words available to send today."
            
        today_str = date.today().strftime("%d %B %Y")
        
        message = [
            f"🇯🇵 Bromodachis Daily Vocabulary #{batch_number}",
            "",
            f"📅 {today_str}",
            "",
            "━━━━━━━━━━━━━━",
            ""
        ]
        
        number_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        
        for idx, word in enumerate(words):
            emoji = number_emojis[idx] if idx < len(number_emojis) else f"{idx+1}."
            
            message.append(f"{emoji} {word.expression}")
            message.append(f"({word.reading})")
            message.append("")
            message.append("Meaning")
            message.append(f"{word.meaning}")
            message.append("")
            
            message.append("━━━━━━━━━━━━━━")
            message.append("")
            
        message.append("🎯 Challenge")
        message.append("")
        message.append("Translate")
        message.append("")
        message.append('"I want to master Japanese."') 
        message.append("")
        message.append("Reply below 👇")
        message.append("")
        message.append("頑張って！")
        
        return "\n".join(message)
