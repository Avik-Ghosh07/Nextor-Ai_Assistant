"""
Chat Service - Handles chat logic and AI interactions
"""

import logging
import datetime as dt
import random
import re
from typing import Dict, List, Optional

from llm_manager import LLMManager
from app.services.web_search_service import search_web

logger = logging.getLogger(__name__)

# Initialize LLM Manager
llm_manager = LLMManager()
logger.info(f"🤖 Available LLM providers: {llm_manager.get_available_providers()}")


def get_ai_reply(message: str, history: List[Dict[str, str]]) -> Optional[str]:
    """
    Get AI response using LLM Manager (supports multiple providers with automatic fallback).
    Returns None if all providers fail or are unavailable.
    """
    try:
        logger.info(f"🤖 Requesting AI response for: {message[:100]}...")
        response, provider_used = llm_manager.get_response(message, history)
        
        if response:
            logger.info(f"✅ AI response received from {provider_used}")
            return response
        else:
            logger.warning("⚠️ All AI providers failed - will use fallback methods")
            return None
        
    except Exception as e:
        logger.error(f"❌ AI response error: {e}")
        return None


def get_builtin_knowledge(query: str) -> Optional[str]:
    """Return built-in knowledge for common technical topics."""
    from app.models.knowledge_base import KNOWLEDGE_BASE
    
    query_lower = query.lower()
    
    # Try to match exact phrases
    for keyword, answer in KNOWLEDGE_BASE.items():
        if ' ' in keyword:
            # Multi-word phrase - exact match
            if keyword in query_lower:
                logger.info(f"✅ Using built-in knowledge for: {keyword}")
                return answer
        else:
            # Single word - use word boundaries
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, query_lower):
                logger.info(f"✅ Using built-in knowledge for: {keyword}")
                return answer
    
    return None


def generate_response(message: str, history: List[Dict[str, str]]) -> str:
    """
    Generate reply using AI, web search, or fallback to pattern matching.
    
    Priority order:
    1. Math calculations
    2. Built-in knowledge base
    3. Pattern-based responses (productivity tips, motivation, etc.)
    4. AI response (via LLM Manager)
    5. Web search
    6. Fallback response
    """
    
    lowered = message.lower()
    
    # 1. Check for simple math calculations first
    from app.utils.helpers import calculate_simple_math
    math_result = calculate_simple_math(message)
    if math_result:
        logger.info(f"✅ Calculated math: {message}")
        return math_result
    
    # 2. Check for questions that might be in built-in knowledge
    is_question = any(lowered.startswith(q) for q in 
        ['what is', 'what are', 'who is', 'who are', 'when was', 'where is', 
         'how does', 'why does', 'define', 'explain', 'tell me about', 'what was'])
    
    # Try built-in knowledge for questions
    if is_question:
        builtin_answer = get_builtin_knowledge(message)
        if builtin_answer:
            logger.info(f"✅ Using built-in knowledge base for: {message[:50]}")
            return builtin_answer
    
    # 3. Check for pattern-based commands (productivity, motivation, etc.)
    pattern_response = _check_patterns(lowered, is_question)
    if pattern_response:
        logger.info(f"✅ Using pattern-based response")
        return pattern_response
    
    # 4. Try AI response (this is the primary response method)
    ai_reply = get_ai_reply(message, history)
    if ai_reply:
        return ai_reply
    
    # 5. Try web search for unanswered questions
    if is_question:
        web_answer = search_web(message)
        if web_answer:
            logger.info(f"✅ Using web search answer")
            return web_answer
    
    # 6. Final fallback
    return _get_fallback_response(message, lowered, is_question)
    if web_answer:
        logger.info(f"✅ Using web search answer")
        return web_answer
    
    # Final fallback
    return _get_fallback_response(message, lowered, is_question)


def _check_patterns(lowered: str, is_question: bool) -> Optional[str]:
    """Check for built-in command patterns"""
    
    # Productivity tips
    if any(keyword in lowered for keyword in 
           ['productivity tip', 'productivity', 'productive', 'give me a tip']) and not is_question:
        tips = [
            "Try the Pomodoro Technique: 25 minutes of deep focused work, then a 5-minute break.",
            "Start your day by identifying your top 3 priorities. Focus on completing these first.",
            "Eliminate distractions: turn off notifications, close unnecessary tabs, put your phone on silent.",
            "Use the 2-minute rule: if a task takes less than 2 minutes, do it immediately.",
            "Batch similar tasks together to reduce context switching.",
            "Take regular breaks - your brain needs rest to maintain peak performance.",
        ]
        return random.choice(tips)
    
    # Motivation
    if any(keyword in lowered for keyword in 
           ['motivate me', 'motivation', 'inspire', 'quote']) and not is_question:
        quotes = [
            "You've got this! Break the task into one focused step and get started.",
            "Your future self will thank you for getting started today.",
            "Progress, not perfection. Focus on doing one thing well right now.",
            "The best time to start was yesterday, the second best time is now.",
            "Success is the sum of small efforts repeated day in and day out.",
            "Don't wait for motivation - start anyway. Action creates momentum.",
        ]
        return random.choice(quotes)
    
    return None


def _get_fallback_response(message: str, lowered: str, is_question: bool) -> str:
    """Generate fallback response when all other methods fail"""
    
    logger.warning(f"⚠️ AI and web search unavailable, using fallback for: {message}")
    now = dt.datetime.now()
    greeting = f"Good {('morning' if now.hour < 12 else 'afternoon' if now.hour < 18 else 'evening')}!"
    
    # Greetings
    greeting_words = [r"\bhi\b", r"\bhello\b", r"\bhey\b"]
    if any(re.search(pattern, lowered) for pattern in greeting_words) and len(lowered.split()) <= 3:
        return f"{greeting} I'm Nextor, your AI voice assistant. What can I do for you today?"
    
    if "how are you" in lowered:
        return "I'm functioning perfectly and ready to help you achieve great things today!"
    
    # Creator/origin questions
    if any(keyword in lowered for keyword in ['who created you', 'who made you', 'who built you', 'who is your creator', 'your creator']):
        return "I was created by Mister Avik Ghosh."
    
    # Music
    if "play" in lowered and ("song" in lowered or "music" in lowered):
        return "I can play Hindi, Bengali, or English songs for you! Just specify the language."
    
    # Stress/wellness
    if "stress" in lowered or "overwhelm" in lowered or "anxious" in lowered:
        return "Take 3 deep breaths. Focus on your top 2 priorities. You've got this!"
    
    # Gratitude
    if "thank" in lowered or "thanks" in lowered:
        return "You're welcome! Happy to help. What else can I do for you?"
    
    # Weather
    if "weather" in lowered:
        return "I can fetch live weather for your location! Grant location permission when asked."
    
    # Jokes
    if "joke" in lowered or "funny" in lowered:
        jokes = [
            "Why don't programmers trust stairs? Because they're always up to something!",
            "Why do Java developers wear glasses? Because they can't C sharp!",
            "A SQL query walks into a bar and asks: 'Can I join you?'",
        ]
        return random.choice(jokes)
    
    # Questions that failed
    if is_question:
        return (
            f"I apologize, but I couldn't find information about '{message}'. "
            "Try rephrasing your question or ask about: productivity, tech, famous people/places, weather, music, etc."
        )
    
    # General helpful response
    return "I'm Nextor, your AI productivity assistant! I can help with time management, motivation, planning, playing music, answering questions, and staying organized. How can I assist you today?"
