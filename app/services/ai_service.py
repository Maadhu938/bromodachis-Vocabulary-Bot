"""AI Service using Groq API for Japanese learning assistance"""
import os
from typing import Optional, List, Dict
from groq import Groq

class AIService:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "openai/gpt-oss-120b"  # Fast and good for chat
        
    def ask(self, question: str, user_context: Optional[Dict] = None) -> str:
        """Ask AI anything about Japanese"""
        system_prompt = """You are a helpful Japanese language tutor. You help students learn Japanese by:
- Explaining grammar clearly with examples
- Answering vocabulary questions
- Providing cultural context
- Giving study tips

Keep responses concise but informative. Use romaji readings for Japanese words."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1024
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def explain_grammar(self, grammar_point: str) -> str:
        """Explain a Japanese grammar point"""
        prompt = f"""Explain this Japanese grammar point in detail:
{grammar_point}

Include:
1. Basic meaning/usage
2. Formation rules
3. 3 example sentences with English translations
4. Common mistakes to avoid"""
        
        return self.ask(prompt)
    
    def explain_vocabulary(self, word: str, context: Optional[str] = None) -> str:
        """Explain vocabulary word with usage"""
        prompt = f"""Explain this Japanese word: {word}

Include:
1. Meaning and reading (romaji)
2. Part of speech
3. Usage examples (3 sentences)
4. Related words or synonyms
5. Common collocations"""
        
        if context:
            prompt += f"\n\nContext: {context}"
        
        return self.ask(prompt)
    
    def translate(self, text: str, to_japanese: bool = True) -> str:
        """Translate text between English and Japanese"""
        if to_japanese:
            prompt = f"""Translate this English text to Japanese:
{text}

Provide:
1. Natural Japanese translation
2. Romaji reading
3. Literal translation (if different from natural)
4. Notes on formality level"""
        else:
            prompt = f"""Translate this Japanese text to English:
{text}

Provide:
1. Natural English translation
2. Word-by-word breakdown
3. Grammar notes"""
        
        return self.ask(prompt)
    
    def practice_conversation(self, topic: str, user_level: str = "beginner") -> str:
        """Generate conversation practice for a topic"""
        prompt = f"""Create a Japanese conversation practice scenario.

Topic: {topic}
User Level: {user_level}

Provide:
1. Scenario setup (in English)
2. Key vocabulary list (Japanese - Romaji - English)
3. Useful phrases for this situation
4. A sample dialogue (Japanese with English translation)
5. Practice prompts for the user to respond"""
        
        return self.ask(prompt)
    
    def get_study_tips(self, weak_areas: Optional[List[str]] = None) -> str:
        """Get personalized study tips"""
        prompt = """Give 5 practical tips for learning Japanese effectively.

Focus on:
- Daily study habits
- Memorization techniques
- Practice methods
- Common pitfalls to avoid
- Resources to use"""
        
        if weak_areas:
            prompt += f"\n\nUser needs help with: {', '.join(weak_areas)}"
        
        return self.ask(prompt)
    
    def check_answer(self, user_answer: str, correct_answer: str, question_context: str) -> str:
        """Check user's answer and provide feedback"""
        prompt = f"""Check this Japanese answer and provide feedback.

Question: {question_context}
User's Answer: {user_answer}
Correct Answer: {correct_answer}

Provide:
1. Is it correct? (Yes/Partially/No)
2. What was good about the answer
3. What needs improvement
4. Correct explanation
5. Encouragement for the student"""
        
        return self.ask(prompt)
    
    def generate_quiz_explanation(self, question: str, correct_answer: str, user_answer: str) -> str:
        """Generate explanation for quiz answers"""
        prompt = f"""Explain this quiz question and answer.

Question: {question}
Correct Answer: {correct_answer}
User Selected: {user_answer}

Explain:
1. Why the correct answer is right
2. Why the user's answer was wrong (if incorrect)
3. Additional context to help them remember
4. Similar examples"""
        
        return self.ask(prompt)

# Global AI service instance
ai_service = AIService()
