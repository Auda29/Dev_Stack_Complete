import os
import sys

# Abstract Interface
class LLMClient:
    def generate_text(self, prompt, system_prompt=None):
        raise NotImplementedError

# OpenAI Implementation
class OpenAIClient(LLMClient):
    def __init__(self):
        try:
            from openai import OpenAI
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            self.client = OpenAI(api_key=api_key)
            self.model = os.environ.get("OPENAI_MODEL", "gpt-4o")
        except ImportError:
            print("Error: openai package not installed. Run 'pip install openai'")
            sys.exit(1)
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

    def generate_text(self, prompt, system_prompt="You are a helpful AI assistant."):
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating text with OpenAI: {e}"

# Anthropic Implementation
class AnthropicClient(LLMClient):
    def __init__(self):
        try:
            import anthropic
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
            self.client = anthropic.Anthropic(api_key=api_key)
            self.model = os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20240620")
        except ImportError:
            print("Error: anthropic package not installed. Run 'pip install anthropic'")
            sys.exit(1)
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

    def generate_text(self, prompt, system_prompt="You are a helpful AI assistant."):
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            return f"Error generating text with Anthropic: {e}"

# Google Gemini Implementation
class GoogleClient(LLMClient):
    def __init__(self):
        try:
            import google.generativeai as genai
            api_key = os.environ.get("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found in environment variables")
            genai.configure(api_key=api_key)
            self.model_name = os.environ.get("GOOGLE_MODEL", "gemini-1.5-pro")
            self.model = genai.GenerativeModel(self.model_name)
        except ImportError:
            print("Error: google-generativeai package not installed. Run 'pip install google-generativeai'")
            sys.exit(1)
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

    def generate_text(self, prompt, system_prompt="You are a helpful AI assistant."):
        try:
            # Gemini doesn't have a separate system prompt in the same way, 
            # but we can prepend it or use system instructions if supported by the specific model version.
            # For simplicity, we'll prepend it.
            full_prompt = f"{system_prompt}\n\n{prompt}"
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"Error generating text with Google Gemini: {e}"

# Factory Function
def get_llm_client():
    provider = os.environ.get("LLM_PROVIDER", "openai").lower()
    
    if provider == "openai":
        return OpenAIClient()
    elif provider == "anthropic":
        return AnthropicClient()
    elif provider == "google":
        return GoogleClient()
    else:
        print(f"Warning: Unknown LLM_PROVIDER '{provider}'. Defaulting to OpenAI.")
        return OpenAIClient()
