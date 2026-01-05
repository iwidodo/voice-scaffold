"""
OpenAI client wrapper for LLM integration.
"""
import os
import logging
from typing import List, Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class LLMClient:
    """Wrapper for OpenAI API with function calling support."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize LLM client.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model to use for completions
        """
        logger.info(f"[client.py.LLMClient.__init__] Initializing LLM client with model: {model}")
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.error("[client.py.LLMClient.__init__] OpenAI API key not found")
            raise ValueError("OpenAI API key required")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        logger.info("[client.py.LLMClient.__init__] LLM client initialized successfully")
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict]] = None,
        tool_choice: Optional[str] = None
    ) -> Dict:
        """
        Get a chat completion from the LLM.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            tools: Optional list of function tools for function calling
            tool_choice: Optional tool choice ("auto", "none", or specific function)
            
        Returns:
            Response dictionary from OpenAI API
        """
        logger.debug(f"[client.py.LLMClient.chat_completion] Requesting chat completion with {len(messages)} messages")
        if tools:
            logger.debug(f"[client.py.LLMClient.chat_completion] Using {len(tools)} tools")
        
        kwargs = {
            "model": self.model,
            "messages": messages
        }
        
        if tools:
            kwargs["tools"] = tools
            if tool_choice:
                kwargs["tool_choice"] = tool_choice
        
        try:
            response = self.client.chat.completions.create(**kwargs)
            logger.debug("[client.py.LLMClient.chat_completion] Chat completion successful")
            return response
        except Exception as e:
            logger.error(f"[client.py.LLMClient.chat_completion] Error during chat completion: {e}")
            raise
    
    def extract_message_content(self, response) -> str:
        """
        Extract message content from response.
        
        Args:
            response: OpenAI API response
            
        Returns:
            Message content as string
        """
        content = response.choices[0].message.content or ""
        logger.debug(f"[client.py.LLMClient.extract_message_content] Extracted message content (length: {len(content)})")
        return content
    
    def extract_tool_calls(self, response) -> List[Dict]:
        """
        Extract tool calls from response.
        
        Args:
            response: OpenAI API response
            
        Returns:
            List of tool call dictionaries
        """
        message = response.choices[0].message
        if hasattr(message, 'tool_calls') and message.tool_calls:
            tool_calls = [
                {
                    "id": tc.id,
                    "function": tc.function.name,
                    "arguments": tc.function.arguments
                }
                for tc in message.tool_calls
            ]
            logger.debug(f"[client.py.LLMClient.extract_tool_calls] Extracted {len(tool_calls)} tool calls")
            return tool_calls
        logger.debug("[client.py.LLMClient.extract_tool_calls] No tool calls in response")
        return []
