import openai
import logging
import os
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LLMInterface:
    
    def __init__(self, model: str = None, api_key: str = None):
        self.model = model or os.getenv('OPENAI_MODEL', 'gpt-4')
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable.")
        
        # Set up OpenAI client
        openai.api_key = self.api_key
        self.client = openai.OpenAI(api_key=self.api_key)
        
        self.logger = logging.getLogger(__name__)
        
        # Conversation history for context
        self.conversation_history = []

    def prompt_llm(self, user_prompt: str, system_prompt: str) -> str:
        try:

            
            # Build messages with proper history management
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add recent conversation history (keep last N exchanges)
            if self.conversation_history:
                # Keep last 8 messages (4 exchanges) to stay within context limits
                recent_history = self.conversation_history[-8:]
                messages.extend(recent_history)
            
            # Add current user message
            messages.append({"role": "user", "content": user_prompt})
            
            # Calculate approximate token count to stay within limits
            total_chars = sum(len(msg["content"]) for msg in messages)
            if total_chars > 12000:  # Rough estimate for token limit
                # Trim history more aggressively if approaching limits
                messages = [messages[0]]  # Keep system prompt
                # Keep only last 4 messages (2 exchanges)
                messages.extend(self.conversation_history[-4:])
                messages.append({"role": "user", "content": user_prompt})
            
            
            response = self.client.responses.create(
                model=self.model,
                input=messages,
                temperature=0.3,
            )
            
            response_content = response.output_text
            
            # Add to conversation history
            self.conversation_history.extend([
                {"role": "user", "content": user_prompt},
                {"role": "assistant", "content": response_content}
            ])
            
            # Keep history manageable
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            self.logger.info(f"Received LLM response ({len(response_content)} characters)")
            return response_content
            
        except openai.RateLimitError:
            self.logger.error("OpenAI API rate limit exceeded")
            return "Rate limit exceeded. Please wait and try again."
        except openai.AuthenticationError:
            self.logger.error("OpenAI API authentication failed")
            return "Authentication failed. Check your API key."
        except Exception as e:
            self.logger.error(f"LLM API error: {e}")
            return f"Error communicating with LLM: {str(e)}"
    
