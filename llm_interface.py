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

    # Known Claude model prefixes
    CLAUDE_MODELS = ['claude-3', 'claude-sonnet', 'claude-opus', 'claude-haiku']

    def __init__(self, model: str = None, api_key: str = None):
        self.model = model or os.getenv('AI_MODEL')
        if not self.model:
            raise ValueError("Model not provided. Set AI_MODEL environment variable.")
        print(f">>> Using LLM model: {self.model} <<<")

        # Detect if this is a Claude model
        self.is_claude = any(self.model.startswith(prefix) for prefix in self.CLAUDE_MODELS) if self.model else False

        if self.is_claude:
            # Use Claude API
            self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
            if not self.api_key:
                raise ValueError("Anthropic API key not provided. Set ANTHROPIC_API_KEY environment variable.")
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url='https://api.anthropic.com/v1/'
            )
            print(f">>> Using Claude API <<<")
        else:
            # Use OpenAI API
            self.api_key = api_key or os.getenv('OPENAI_API_KEY')
            if not self.api_key:
                raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable.")
            openai.api_key = self.api_key
            self.client = openai.OpenAI(api_key=self.api_key)
            print(f">>> Using OpenAI API <<<")

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

            if self.is_claude:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    extra_body={
                        "thinking": {"type": "enabled", "budget_tokens": 2000}
                    }
                )
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages
                )
            response_content = response.choices[0].message.content

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
        # tiktoken only works for OpenAI models, use gpt-5 encoding for Claude
        model_for_encoding = "gpt-5" if self.is_claude else self.model
        encoding = tiktoken.encoding_for_model(model_for_encoding)
        num_tokens = len(encoding.encode(string))
        return num_tokens