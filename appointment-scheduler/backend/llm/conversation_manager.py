"""
Conversation state management for multi-turn conversations.
"""
import uuid
from typing import Dict, List, Optional, Any, Union
from backend.models.schemas import ConversationMessage, Provider, ProviderMatch
from backend.models.constants import ConversationState


class ConversationManager:
    """
    Manages conversation state and history for appointment scheduling.
    """
    
    def __init__(self):
        """Initialize conversation manager."""
        self.conversations: Dict[str, Dict] = {}
    
    def create_conversation(self) -> str:
        """
        Create a new conversation.
        
        Returns:
            Conversation ID
        """
        conversation_id = str(uuid.uuid4())
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
            raise ValueError(f"Conversation {conversation_id} not found")
        
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
            return []
        return self.conversations[conversation_id]["messages"]
    
    def get_state(self, conversation_id: str) -> str:
        """
        Get the current state of a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Current state
        """
        if conversation_id not in self.conversations:
            return ConversationState.INITIAL
        return self.conversations[conversation_id]["state"]
    
    def set_state(self, conversation_id: str, state: ConversationState):
        """
        Set the state of a conversation.
        
        Args:
            conversation_id: Conversation ID
            state: New state
        """
        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation {conversation_id} not found")
        self.conversations[conversation_id]["state"] = state
    
    def update_context(self, conversation_id: str, key: str, value: Any):
        """
        Update conversation context with a key-value pair.
        
        Args:
            conversation_id: Conversation ID
            key: Context key
            value: Context value
        """
        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation {conversation_id} not found")
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
            return None
        
        context = self.conversations[conversation_id]["context"]
        if key:
            return context.get(key)
        return context
    
    def get_system_prompt(self, conversation_id: str) -> str:
        """
        Generate system prompt based on conversation state.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            System prompt string
        """
        state = self.get_state(conversation_id)
        
        base_prompt = """You are a helpful medical appointment scheduling assistant.
Your role is to:
1. Understand the patient's health issue
2. Match them with the appropriate healthcare provider
3. Help them find a suitable appointment time
4. Confirm the appointment details

Be empathetic, clear, and efficient. Ask clarifying questions when needed.
Use the provided functions to:
- identify_provider: Find the right doctor for their issue
- check_availability: Look up available appointment times
- create_appointment: Book the appointment once all details are confirmed

Always confirm key details before creating an appointment."""
        
        if state == ConversationState.INITIAL:
            return base_prompt + "\n\nThe conversation is just starting. Greet the patient and ask how you can help."
        
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
