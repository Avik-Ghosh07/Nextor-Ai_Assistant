"""
LLM Manager - Multi-provider AI integration with automatic fallback
Supports: OpenAI, Anthropic Claude, Google Gemini, and Groq
"""

import logging
import os
from typing import Dict, List, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers in order of preference"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    GEMINI = "gemini"


class LLMManager:
    """
    Manages multiple LLM providers with automatic fallback support.
    Tries providers in order of preference until one succeeds.
    """
    
    def __init__(self):
        """Initialize all available LLM providers based on API keys"""
        self.providers = {}
        self.provider_order = []
        
        # Get preferred provider from environment (default: auto-detect)
        preferred = os.getenv('LLM_PROVIDER', 'auto').lower()
        
        # Initialize providers based on available API keys
        self._init_openai()
        self._init_anthropic()
        self._init_groq()
        self._init_gemini()
        
        # Set provider order based on preference
        if preferred != 'auto' and preferred in [p.value for p in LLMProvider]:
            # Put preferred provider first
            preferred_enum = LLMProvider(preferred)
            if preferred_enum in self.providers:
                self.provider_order = [preferred_enum] + [
                    p for p in self.providers.keys() if p != preferred_enum
                ]
            else:
                logger.warning(f"⚠️ Preferred provider '{preferred}' not available, using auto-detect")
                self.provider_order = list(self.providers.keys())
        else:
            # Default order: OpenAI > Anthropic > Groq > Gemini
            default_order = [
                LLMProvider.OPENAI,
                LLMProvider.ANTHROPIC,
                LLMProvider.GROQ,
                LLMProvider.GEMINI
            ]
            self.provider_order = [p for p in default_order if p in self.providers]
        
        if self.provider_order:
            logger.info(f"✅ LLM Manager initialized with providers: {[p.value for p in self.provider_order]}")
        else:
            logger.warning("⚠️ No LLM providers available - will use built-in responses")
    
    def _init_openai(self):
        """Initialize OpenAI GPT models"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return
        
        try:
            import openai
            self.providers[LLMProvider.OPENAI] = {
                'client': openai.OpenAI(api_key=api_key),
                'model': os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),  # Cost-effective default
                'available': True
            }
            logger.info(f"✅ OpenAI initialized (model: {self.providers[LLMProvider.OPENAI]['model']})")
        except ImportError:
            logger.warning("⚠️ openai package not installed")
        except Exception as e:
            logger.error(f"❌ OpenAI initialization failed: {e}")
    
    def _init_anthropic(self):
        """Initialize Anthropic Claude models"""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            return
        
        try:
            import anthropic
            self.providers[LLMProvider.ANTHROPIC] = {
                'client': anthropic.Anthropic(api_key=api_key),
                'model': os.getenv('ANTHROPIC_MODEL', 'claude-3-5-haiku-20241022'),  # Fast and cost-effective
                'available': True
            }
            logger.info(f"✅ Anthropic initialized (model: {self.providers[LLMProvider.ANTHROPIC]['model']})")
        except ImportError:
            logger.warning("⚠️ anthropic package not installed")
        except Exception as e:
            logger.error(f"❌ Anthropic initialization failed: {e}")
    
    def _init_groq(self):
        """Initialize Groq (ultra-fast inference)"""
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            return
        
        try:
            from groq import Groq
            self.providers[LLMProvider.GROQ] = {
                'client': Groq(api_key=api_key),
                'model': os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile'),  # Fast and powerful
                'available': True
            }
            logger.info(f"✅ Groq initialized (model: {self.providers[LLMProvider.GROQ]['model']})")
        except ImportError:
            logger.warning("⚠️ groq package not installed")
        except Exception as e:
            logger.error(f"❌ Groq initialization failed: {e}")
    
    def _init_gemini(self):
        """Initialize Google Gemini"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.providers[LLMProvider.GEMINI] = {
                'client': genai.GenerativeModel(
                    os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')
                ),
                'model': os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp'),
                'available': True
            }
            logger.info(f"✅ Gemini initialized (model: {self.providers[LLMProvider.GEMINI]['model']})")
        except ImportError:
            logger.warning("⚠️ google-generativeai package not installed")
        except Exception as e:
            logger.error(f"❌ Gemini initialization failed: {e}")
    

    
    def _call_openai(self, message: str, history: List[Dict[str, str]], provider_info: dict) -> Optional[str]:
        """Call OpenAI API"""
        try:
            client = provider_info['client']
            model = provider_info['model']
            
            # Build messages array
            messages = [
                {"role": "system", "content": "You are Nextor, a helpful AI voice assistant. Answer concisely in under 100 words. Be direct and accurate."}
            ]
            
            # Add conversation history (last 4 messages for context)
            for msg in history[-4:]:
                messages.append({
                    "role": "user" if msg["role"] == "user" else "assistant",
                    "content": msg["text"]
                })
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Call API
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=200,
                temperature=0.7,
                timeout=8
            )
            
            if response.choices:
                reply = response.choices[0].message.content.strip()
                logger.info(f"✅ OpenAI ({model}) responded successfully")
                return reply
            
            return None
            
        except Exception as e:
            error_msg = str(e)
            if '429' in error_msg or 'quota' in error_msg.lower():
                logger.warning(f"⚠️ OpenAI quota exceeded")
                provider_info['available'] = False
            elif 'timeout' in error_msg.lower():
                logger.warning(f"⚠️ OpenAI timeout")
            else:
                logger.warning(f"⚠️ OpenAI error: {error_msg}")
            return None
    
    def _call_anthropic(self, message: str, history: List[Dict[str, str]], provider_info: dict) -> Optional[str]:
        """Call Anthropic Claude API"""
        try:
            client = provider_info['client']
            model = provider_info['model']
            
            # Build messages array
            messages = []
            
            # Add conversation history (last 4 messages)
            for msg in history[-4:]:
                messages.append({
                    "role": "user" if msg["role"] == "user" else "assistant",
                    "content": msg["text"]
                })
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Call API
            response = client.messages.create(
                model=model,
                max_tokens=200,
                temperature=0.7,
                system="You are Nextor, a helpful AI voice assistant. Answer concisely in under 100 words. Be direct and accurate.",
                messages=messages,
                timeout=8
            )
            
            if response.content:
                reply = response.content[0].text.strip()
                logger.info(f"✅ Anthropic ({model}) responded successfully")
                return reply
            
            return None
            
        except Exception as e:
            error_msg = str(e)
            if '429' in error_msg or 'quota' in error_msg.lower() or 'rate_limit' in error_msg.lower():
                logger.warning(f"⚠️ Anthropic quota/rate limit exceeded")
                provider_info['available'] = False
            elif 'timeout' in error_msg.lower():
                logger.warning(f"⚠️ Anthropic timeout")
            else:
                logger.warning(f"⚠️ Anthropic error: {error_msg}")
            return None
    
    def _call_groq(self, message: str, history: List[Dict[str, str]], provider_info: dict) -> Optional[str]:
        """Call Groq API (ultra-fast inference)"""
        try:
            client = provider_info['client']
            model = provider_info['model']
            
            # Build messages array
            messages = [
                {"role": "system", "content": "You are Nextor, a helpful AI voice assistant. Answer concisely in under 100 words. Be direct and accurate."}
            ]
            
            # Add conversation history (last 4 messages)
            for msg in history[-4:]:
                messages.append({
                    "role": "user" if msg["role"] == "user" else "assistant",
                    "content": msg["text"]
                })
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Call API
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=200,
                temperature=0.7,
                timeout=8
            )
            
            if response.choices:
                reply = response.choices[0].message.content.strip()
                logger.info(f"✅ Groq ({model}) responded successfully")
                return reply
            
            return None
            
        except Exception as e:
            error_msg = str(e)
            if '429' in error_msg or 'quota' in error_msg.lower() or 'rate_limit' in error_msg.lower():
                logger.warning(f"⚠️ Groq quota/rate limit exceeded")
                provider_info['available'] = False
            elif 'timeout' in error_msg.lower():
                logger.warning(f"⚠️ Groq timeout")
            else:
                logger.warning(f"⚠️ Groq error: {error_msg}")
            return None
    
    def _call_gemini(self, message: str, history: List[Dict[str, str]], provider_info: dict) -> Optional[str]:
        """Call Google Gemini API"""
        try:
            model = provider_info['client']
            
            # Build context
            context = "You are Nextor, an AI assistant. Answer directly and concisely in under 100 words. Be helpful and accurate.\n\n"
            
            # Add conversation history (last 2 messages for speed)
            for msg in history[-2:]:
                role = "User" if msg["role"] == "user" else "Assistant"
                context += f"{role}: {msg['text']}\n"
            
            context += f"User: {message}\nAssistant:"
            
            # Call API
            generation_config = {
                "temperature": 0.7,
                "max_output_tokens": 200,
                "top_p": 0.95,
                "top_k": 40
            }
            
            response = model.generate_content(
                context,
                generation_config=generation_config,
                request_options={"timeout": 8}
            )
            
            if response and response.text:
                reply = response.text.strip()
                # Remove any "Nextor:" or "Assistant:" prefix
                if reply.lower().startswith('nextor:'):
                    reply = reply[7:].strip()
                elif reply.lower().startswith('assistant:'):
                    reply = reply[10:].strip()
                logger.info(f"✅ Gemini ({provider_info['model']}) responded successfully")
                return reply
            
            return None
            
        except Exception as e:
            error_msg = str(e)
            if '429' in error_msg or 'quota' in error_msg.lower():
                logger.warning(f"⚠️ Gemini quota exceeded")
                provider_info['available'] = False
            elif 'timeout' in error_msg.lower():
                logger.warning(f"⚠️ Gemini timeout")
            else:
                logger.warning(f"⚠️ Gemini error: {error_msg}")
            return None
    

    
    def get_response(self, message: str, history: List[Dict[str, str]] = None) -> Tuple[Optional[str], Optional[str]]:
        """
        Get AI response from available providers with automatic fallback.
        
        Args:
            message: User's message
            history: Conversation history (list of dicts with 'role' and 'text')
        
        Returns:
            Tuple of (response_text, provider_used)
        """
        if history is None:
            history = []
        
        # Try each provider in order
        for provider in self.provider_order:
            provider_info = self.providers[provider]
            
            # Skip if provider is marked as unavailable
            if not provider_info.get('available', True):
                continue
            
            logger.info(f"🔄 Trying {provider.value}...")
            
            try:
                # Call the appropriate provider
                if provider == LLMProvider.OPENAI:
                    response = self._call_openai(message, history, provider_info)
                elif provider == LLMProvider.ANTHROPIC:
                    response = self._call_anthropic(message, history, provider_info)
                elif provider == LLMProvider.GROQ:
                    response = self._call_groq(message, history, provider_info)
                elif provider == LLMProvider.GEMINI:
                    response = self._call_gemini(message, history, provider_info)
                else:
                    continue
                
                # If successful, return the response
                if response:
                    return response, provider.value
                
            except Exception as e:
                logger.error(f"❌ Unexpected error with {provider.value}: {e}")
                continue
        
        # No provider succeeded
        logger.warning("⚠️ All LLM providers failed or unavailable")
        return None, None
    
    def get_available_providers(self) -> List[str]:
        """Get list of currently available providers"""
        return [p.value for p in self.provider_order if self.providers[p].get('available', True)]
    
    def reset_availability(self):
        """Reset all providers to available (useful after quota resets)"""
        for provider_info in self.providers.values():
            provider_info['available'] = True
        logger.info("🔄 Reset all providers to available")
