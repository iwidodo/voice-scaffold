"""
Conversation state management for multi-turn conversations.
"""
import uuid
import logging
from typing import Dict, List, Optional, Any, Union
from backend.models.schemas import ConversationMessage, Provider, ProviderMatch
from backend.models.constants import ConversationState

logger = logging.getLogger(__name__)


class ConversationManager:
    """
    Manages conversation state and history for appointment scheduling.
    """
    
    def __init__(self):
        """Initialize conversation manager."""
        logger.info("[conversation_manager.py.ConversationManager.__init__] Initializing conversation manager")
        self.conversations: Dict[str, Dict] = {}
    
    def create_conversation(self) -> str:
        """
        Create a new conversation.
        
        Returns:
            Conversation ID
        """
        conversation_id = str(uuid.uuid4())
        logger.info(f"[conversation_manager.py.ConversationManager.create_conversation] Creating new conversation: {conversation_id}")
        
        self.conversations[conversation_id] = {
            "id": conversation_id,
            "state": ConversationState.INITIAL,
            "messages": [],
            "context": {}
        }
        return conversation_id
    
    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str
    ):
        """
        Add a message to the conversation history.
        
        Args:
            conversation_id: Conversation ID
            role: Message role ("user", "assistant", "system")
            content: Message content
        """
        if conversation_id not in self.conversations:
            logger.error(f"[conversation_manager.py.ConversationManager.add_message] Conversation not found: {conversation_id}")
            raise ValueError(f"Conversation {conversation_id} not found")
        
        logger.debug(f"[conversation_manager.py.ConversationManager.add_message] Adding {role} message to conversation: {conversation_id}")
        
        self.conversations[conversation_id]["messages"].append({
            "role": role,
            "content": content
        })
    
    def get_messages(self, conversation_id: str) -> List[Dict]:
        """
        Get all messages in a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            List of message dictionaries
        """
        if conversation_id not in self.conversations:
            logger.warning(f"[conversation_manager.py.ConversationManager.get_messages] Conversation not found: {conversation_id}")
            return []
        
        messages = self.conversations[conversation_id]["messages"]
        logger.debug(f"[conversation_manager.py.ConversationManager.get_messages] Retrieved {len(messages)} messages for conversation: {conversation_id}")
        return messages
    
    def get_state(self, conversation_id: str) -> str:
        """
        Get the current state of a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Current state
        """
        if conversation_id not in self.conversations:
            logger.warning(f"[conversation_manager.py.ConversationManager.get_state] Conversation not found: {conversation_id}, returning INITIAL state")
            return ConversationState.INITIAL
        
        state = self.conversations[conversation_id]["state"]
        logger.debug(f"[conversation_manager.py.ConversationManager.get_state] State for conversation {conversation_id}: {state}")
        return state
    
    def set_state(self, conversation_id: str, state: ConversationState):
        """
        Set the state of a conversation.
        
        Args:
            conversation_id: Conversation ID
            state: New state
        """
        if conversation_id not in self.conversations:
            logger.error(f"[conversation_manager.py.ConversationManager.set_state] Conversation not found: {conversation_id}")
            raise ValueError(f"Conversation {conversation_id} not found")
        
        old_state = self.conversations[conversation_id]["state"]
        self.conversations[conversation_id]["state"] = state
        logger.info(f"[conversation_manager.py.ConversationManager.set_state] Conversation {conversation_id} state changed: {old_state} -> {state}")
    
    def update_context(self, conversation_id: str, key: str, value: Any):
        """
        Update conversation context with a key-value pair.
        
        Args:
            conversation_id: Conversation ID
            key: Context key
            value: Context value
        """
        if conversation_id not in self.conversations:
            logger.error(f"[conversation_manager.py.ConversationManager.update_context] Conversation not found: {conversation_id}")
            raise ValueError(f"Conversation {conversation_id} not found")
        
        logger.debug(f"[conversation_manager.py.ConversationManager.update_context] Updating context for conversation {conversation_id}: {key}={value}")
        self.conversations[conversation_id]["context"][key] = value
    
    def get_context(self, conversation_id: str, key: Optional[str] = None) -> Optional[Union[str, Dict, Any]]:
        """
        Get conversation context.
        
        Args:
            conversation_id: Conversation ID
            key: Optional specific key to retrieve
            
        Returns:
            Context value or entire context dict
        """
        if conversation_id not in self.conversations:
            logger.warning(f"[conversation_manager.py.ConversationManager.get_context] Conversation not found: {conversation_id}")
            return None
        
        context = self.conversations[conversation_id]["context"]
        if key:
            value = context.get(key)
            logger.debug(f"[conversation_manager.py.ConversationManager.get_context] Retrieved context key '{key}' for conversation {conversation_id}: {value}")
            return value
        
        logger.debug(f"[conversation_manager.py.ConversationManager.get_context] Retrieved full context for conversation {conversation_id}")
        return context
    
    def get_system_prompt(self, conversation_id: str) -> str:
        """
        Generate system prompt based on conversation state.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            System prompt string
        """
        from datetime import datetime
        
        state = self.get_state(conversation_id)
        logger.debug(f"[conversation_manager.py.ConversationManager.get_system_prompt] Generating system prompt for conversation {conversation_id} in state: {state}")
        
        # Get current date and time
        now = datetime.now()
        current_date = now.strftime("%A, %B %d, %Y")  # e.g., "Monday, January 06, 2026"
        current_time = now.strftime("%I:%M %p")  # e.g., "02:30 PM"
        
        base_prompt = f"""You are a helpful medical appointment scheduling assistant.

CURRENT DATE AND TIME: {current_date} at {current_time}

Your role is to:
1. Understand the patient's health issue
2. Match them with the appropriate healthcare provider
3. Help them find a suitable appointment time
4. Confirm the appointment details

VOICE OUTPUT FORMATTING:
- Keep responses concise and conversational for spoken output
- Avoid parentheses - integrate information naturally into sentences
- Use "also known as" or "or" instead of parentheses
- Format times and dates in a natural speaking style
- Instead of "(Dentist)", say "who is a dentist" or "dentist at..."
- Skip technical state information like "(State: provider_matched)"

Be empathetic, clear, and efficient. Ask clarifying questions when needed.
Use the provided functions to:
- identify_provider: Find the right doctor for their issue
- check_availability: Look up available appointment times
- create_appointment: Book the appointment once all details are confirmed

IMPORTANT: 
- Use the CURRENT DATE AND TIME above to understand relative dates like "tomorrow", "next week", "Wednesday", etc.
- When checking availability, call check_availability with num_days parameter to look ahead the appropriate number of days.
- If a function returns an error (like no providers available or no time slots), you MUST communicate this clearly to the user.
- Never stay silent when a function call fails or returns no results.
- If no providers are available for a specialty, apologize and suggest alternatives (like seeing a General Practitioner).
- If no time slots are available, offer to check other dates or suggest contacting the office directly.
- Always provide helpful next steps when something isn't available.

Always confirm key details before creating an appointment."""
        
        if state == ConversationState.INITIAL:
            return base_prompt + "\n\nThe conversation is just starting. Introduce yourself as an AI booking assistant from Hippocratic AI, then ask how you can help with scheduling their appointment."
        
        elif state == ConversationState.ISSUE_IDENTIFIED:
            return base_prompt + "\n\nYou've identified the patient's health issue. Use identify_provider to find the right doctor."
        
        elif state == ConversationState.PROVIDER_MATCHED:
            context = self.get_context(conversation_id)
            provider_name = context.get("provider_name", "the provider")
            return base_prompt + f"\n\nYou've matched the patient with {provider_name}. Use check_availability to show available times."
        
        elif state == ConversationState.AVAILABILITY_CHECKED:
            return base_prompt + "\n\nYou've shown available times. Help the patient choose and confirm the appointment details."
        
        elif state == ConversationState.APPOINTMENT_CONFIRMED:
            return base_prompt + "\n\nThe appointment has been confirmed. Provide the details and ask if they need anything else."
        
        return base_prompt
