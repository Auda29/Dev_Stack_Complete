"""
Enhanced LLM Client with RAG Integration, Token Counting, and Retry Logic

This module provides a robust interface to multiple LLM providers with:
- RAG-based code context injection
- Token counting and budget management
- Automatic retry with exponential backoff
- Conversation history management
- Streaming support (where available)
"""

import os
import sys
from typing import List, Dict, Optional, Callable
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


# Abstract Interface
class LLMClient:
    """Base class for all LLM clients."""
    
    def __init__(self):
        self.last_token_count = 0
        self.total_tokens_used = 0
        self.rag_client = None
        
    def generate_text(self, prompt, system_prompt=None, **kwargs):
        """Generate text from prompt. Must be implemented by subclasses."""
        raise NotImplementedError
    
    def generate_with_messages(self, messages: List[Dict], **kwargs):
        """Generate text from a list of messages. Must be implemented by subclasses."""
        raise NotImplementedError
    
    def get_token_count(self, text: str) -> int:
        """
        Estimate token count for text.
        Override in subclasses for accurate counting.
        Default: rough estimate of ~4 chars per token
        """
        return len(text) // 4
    
    def generate_with_context(self,
                             prompt: str,
                             system_prompt: Optional[str] = None,
                             search_query: Optional[str] = None,
                             max_context_chunks: int = 5,
                             **kwargs) -> str:
        """
        Generate text with RAG context automatically included.
        
        Args:
            prompt: User prompt
            system_prompt: System instruction
            search_query: Query for RAG search (defaults to prompt if None)
            max_context_chunks: Maximum code chunks to include
            **kwargs: Additional arguments for generate_text
            
        Returns:
            Generated text
        """
        # Lazy load RAG client
        if self.rag_client is None:
            try:
                from rag_client import RAGClient
                self.rag_client = RAGClient()
            except Exception as e:
                print(f"Warning: RAG client unavailable: {e}")
                # Continue without RAG
                return self.generate_text(prompt, system_prompt, **kwargs)
        
        # Query RAG for relevant code
        query = search_query or prompt
        rag_results = self.rag_client.query(query, n_results=max_context_chunks)
        
        # Format context
        if rag_results:
            code_context = self.rag_client.format_for_llm(rag_results)
            enhanced_prompt = f"{code_context}\n\n---\n\n{prompt}"
        else:
            enhanced_prompt = prompt
        
        return self.generate_text(enhanced_prompt, system_prompt, **kwargs)


# OpenAI Implementation
class OpenAIClient(LLMClient):
    def __init__(self):
        super().__init__()
        try:
            from openai import OpenAI
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            self.client = OpenAI(api_key=api_key)
            self.model = os.environ.get("OPENAI_MODEL", "gpt-5.1")
            
            # Try to import tiktoken for accurate token counting
            try:
                import tiktoken
                self.encoding = tiktoken.encoding_for_model(self.model)
                self.has_tiktoken = True
            except:
                self.has_tiktoken = False
                print("Warning: tiktoken not available, using approximate token counting")
                
        except ImportError:
            print("Error: openai package not installed. Run 'pip install openai'")
            sys.exit(1)
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

    def get_token_count(self, text: str) -> int:
        """Get accurate token count for OpenAI models."""
        if self.has_tiktoken:
            return len(self.encoding.encode(text))
        return super().get_token_count(text)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    def generate_text(self, 
                     prompt: str, 
                     system_prompt: str = "You are a helpful AI assistant.",
                     temperature: float = 0.7,
                     max_tokens: Optional[int] = None,
                     **kwargs) -> str:
        """
        Generate text using OpenAI API with retry logic.
        
        Args:
            prompt: User prompt
            system_prompt: System instruction
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional OpenAI API parameters
            
        Returns:
            Generated text
        """
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
            }
            
            if max_tokens:
                params["max_tokens"] = max_tokens
            
            # Add any additional parameters
            params.update(kwargs)
            
            response = self.client.chat.completions.create(**params)
            
            # Track token usage
            if hasattr(response, 'usage'):
                self.last_token_count = response.usage.total_tokens
                self.total_tokens_used += response.usage.total_tokens
            
            return response.choices[0].message.content
            
        except Exception as e:
            error_msg = f"Error generating text with OpenAI: {e}"
            print(error_msg)
            raise  # Re-raise for retry logic

    def generate_with_messages(self, 
                               messages: List[Dict],
                               temperature: float = 0.7,
                               max_tokens: Optional[int] = None,
                               **kwargs) -> str:
        """
        Generate text from a conversation history.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            Generated text
        """
        try:
            params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
            }
            
            if max_tokens:
                params["max_tokens"] = max_tokens
            
            params.update(kwargs)
            
            response = self.client.chat.completions.create(**params)
            
            if hasattr(response, 'usage'):
                self.last_token_count = response.usage.total_tokens
                self.total_tokens_used += response.usage.total_tokens
            
            return response.choices[0].message.content
            
        except Exception as e:
            error_msg = f"Error generating text with OpenAI: {e}"
            print(error_msg)
            raise


# Anthropic Implementation
class AnthropicClient(LLMClient):
    def __init__(self):
        super().__init__()
        try:
            import anthropic
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
            self.client = anthropic.Anthropic(api_key=api_key)
            self.model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5")
        except ImportError:
            print("Error: anthropic package not installed. Run 'pip install anthropic'")
            sys.exit(1)
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    def generate_text(self, 
                     prompt: str, 
                     system_prompt: str = "You are a helpful AI assistant.",
                     temperature: float = 0.7,
                     max_tokens: int = 4096,
                     **kwargs) -> str:
        """Generate text using Anthropic API with retry logic."""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                **kwargs
            )
            
            # Track token usage
            if hasattr(message, 'usage'):
                self.last_token_count = message.usage.input_tokens + message.usage.output_tokens
                self.total_tokens_used += self.last_token_count
            
            return message.content[0].text
            
        except Exception as e:
            error_msg = f"Error generating text with Anthropic: {e}"
            print(error_msg)
            raise

    def generate_with_messages(self, 
                               messages: List[Dict],
                               temperature: float = 0.7,
                               max_tokens: int = 4096,
                               **kwargs) -> str:
        """Generate text from conversation history."""
        try:
            # Anthropic requires system prompt separate
            system_prompt = "You are a helpful AI assistant."
            filtered_messages = []
            
            for msg in messages:
                if msg['role'] == 'system':
                    system_prompt = msg['content']
                else:
                    filtered_messages.append(msg)
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                temperature=temperature,
                messages=filtered_messages,
                **kwargs
            )
            
            if hasattr(message, 'usage'):
                self.last_token_count = message.usage.input_tokens + message.usage.output_tokens
                self.total_tokens_used += self.last_token_count
            
            return message.content[0].text
            
        except Exception as e:
            error_msg = f"Error generating text with Anthropic: {e}"
            print(error_msg)
            raise


# Google Gemini Implementation
class GoogleClient(LLMClient):
    def __init__(self):
        super().__init__()
        try:
            import google.generativeai as genai
            api_key = os.environ.get("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found in environment variables")
            genai.configure(api_key=api_key)
            self.model_name = os.environ.get("GOOGLE_MODEL", "gemini-1.5-pro")
            self.model = genai.GenerativeModel(self.model_name)
            self.genai = genai
        except ImportError:
            print("Error: google-generativeai package not installed. Run 'pip install google-generativeai'")
            sys.exit(1)
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    def generate_text(self, 
                     prompt: str, 
                     system_prompt: str = "You are a helpful AI assistant.",
                     temperature: float = 0.7,
                     max_tokens: Optional[int] = None,
                     **kwargs) -> str:
        """Generate text using Google Gemini API with retry logic."""
        try:
            # Gemini handles system instructions differently
            full_prompt = f"{system_prompt}\n\n{prompt}"
            
            generation_config = {
                "temperature": temperature,
            }
            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            # Google's token counting
            try:
                self.last_token_count = self.model.count_tokens(full_prompt).total_tokens
                self.total_tokens_used += self.last_token_count
            except:
                pass
            
            return response.text
            
        except Exception as e:
            error_msg = f"Error generating text with Google Gemini: {e}"
            print(error_msg)
            raise

    def generate_with_messages(self, 
                               messages: List[Dict],
                               temperature: float = 0.7,
                               max_tokens: Optional[int] = None,
                               **kwargs) -> str:
        """Generate text from conversation history."""
        try:
            # Convert messages to Gemini format
            chat = self.model.start_chat(history=[])
            
            # Build prompt from messages
            combined_prompt = ""
            for msg in messages:
                role_label = msg['role'].upper()
                combined_prompt += f"[{role_label}]: {msg['content']}\n\n"
            
            generation_config = {"temperature": temperature}
            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens
            
            response = chat.send_message(
                combined_prompt,
                generation_config=generation_config
            )
            
            return response.text
            
        except Exception as e:
            error_msg = f"Error generating text with Google Gemini: {e}"
            print(error_msg)
            raise


# Factory Function
def get_llm_client(**kwargs) -> LLMClient:
    """
    Get an LLM client based on environment configuration.
    
    Args:
        **kwargs: Additional configuration parameters
        
    Returns:
        LLMClient instance
    """
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


if __name__ == "__main__":
    # Test the enhanced LLM client
    print("Testing Enhanced LLM Client...")
    
    client = get_llm_client()
    
    # Test basic generation
    response = client.generate_text(
        "Write a Python function to calculate fibonacci numbers",
        temperature=0.3
    )
    
    print("\nGenerated Response:")
    print(response)
    print(f"\nTokens used: {client.last_token_count}")
    print(f"Total tokens: {client.total_tokens_used}")
    
    # Test with RAG context
    print("\n\nTesting with RAG context...")
    try:
        response_with_context = client.generate_with_context(
            prompt="How does the task manager work?",
            search_query="task manager python",
            max_context_chunks=3
        )
        print(response_with_context[:500] + "...")
    except Exception as e:
        print(f"RAG test skipped: {e}")
