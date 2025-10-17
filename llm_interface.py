import openai
import logging
import os
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv
import tiktoken


# Load environment variables
load_dotenv()

class LLMInterface:
    
    def __init__(self, model: str = None, api_key: str = None):
        self.model = model or os.getenv('OPENAI_MODEL', 'gpt-4')
        print(f">>> Using LLM model: {self.model} <<<")
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable.")
        
        # Set up OpenAI client
        openai.api_key = self.api_key
        self.client = openai.OpenAI(api_key=self.api_key)
        
        self.logger = logging.getLogger(__name__)
        

    def prompt_llm(self, user_prompt, system_prompt) -> str:
        try:
            messages = [system_prompt, user_prompt]
            
            # Calculate approximate token count to stay within limits
            total_tokens = sum(self.num_tokens_from_string(msg["content"]) for msg in messages)
            print(f"Estimated total tokens: {total_tokens}")
            # TODO: Implement token limit checks and trimming if necessary
            
            
            # Print messages being sent to LLM for monitoring
            print("\n" + "="*80)
            print(">>> SENDING TO LLM <<<")
            print("="*80)
            for i, msg in enumerate(messages):
                role_label = msg["role"].upper()
                print(f"\n[{i+1}] {role_label}:")
                print(f"{msg['content']}")
            print("\n" + "="*80 + "\n")
            
            # Call OpenAI API
            response = self.client.responses.create(
                model=self.model,
                input=messages,
            )
            response_content = response.output_text

            print("\n" + "="*80)
            print("🤖 LLM RESPONSE 🤖")
            print("="*80)
            print(f"\n{response_content}\n")
            print("="*80)
            print(f"✅ Response received successfully!")
            print("="*80 + "\n")
            
            print(f"LLM response tokens: {self.num_tokens_from_string(response_content)}")
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
    

    def num_tokens_from_string(self, string: str) -> int:
        encoding = tiktoken.encoding_for_model(self.model)
        num_tokens = len(encoding.encode(string))
        return num_tokens