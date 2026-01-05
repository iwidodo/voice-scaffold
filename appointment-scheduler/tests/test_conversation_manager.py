"""
Tests for conversation manager.
"""
import pytest
from backend.llm.conversation_manager import ConversationManager
from backend.models.constants import ConversationState


def test_create_conversation():
    """Test creating a new conversation."""
    manager = ConversationManager()
    conv_id = manager.create_conversation()
    assert conv_id is not None
    assert manager.get_state(conv_id) == ConversationState.INITIAL


def test_add_and_get_messages():
    """Test adding and retrieving messages."""
    manager = ConversationManager()
    conv_id = manager.create_conversation()
    
    manager.add_message(conv_id, "user", "Hello")
    manager.add_message(conv_id, "assistant", "Hi there!")
    
    messages = manager.get_messages(conv_id)
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Hello"
    assert messages[1]["role"] == "assistant"


def test_update_state():
    """Test updating conversation state."""
    manager = ConversationManager()
    conv_id = manager.create_conversation()
    
    manager.set_state(conv_id, ConversationState.PROVIDER_MATCHED)
    assert manager.get_state(conv_id) == ConversationState.PROVIDER_MATCHED


def test_context_management():
    """Test conversation context management."""
    manager = ConversationManager()
    conv_id = manager.create_conversation()
    
    manager.update_context(conv_id, "provider_id", "p001")
    manager.update_context(conv_id, "patient_name", "John Doe")
    
    assert manager.get_context(conv_id, "provider_id") == "p001"
    assert manager.get_context(conv_id, "patient_name") == "John Doe"
    
    full_context = manager.get_context(conv_id)
    assert "provider_id" in full_context
    assert "patient_name" in full_context


def test_system_prompt_generation():
    """Test system prompt generation for different states."""
    manager = ConversationManager()
    conv_id = manager.create_conversation()
    
    # Test initial state prompt
    prompt = manager.get_system_prompt(conv_id)
    assert "scheduling assistant" in prompt.lower()
    
    # Test provider matched state
    manager.set_state(conv_id, ConversationState.PROVIDER_MATCHED)
    manager.update_context(conv_id, "provider_name", "Dr. Smith")
    prompt = manager.get_system_prompt(conv_id)
    assert "Dr. Smith" in prompt


def test_nonexistent_conversation():
    """Test handling of nonexistent conversation."""
    manager = ConversationManager()
    
    messages = manager.get_messages("nonexistent")
    assert messages == []
    
    state = manager.get_state("nonexistent")
    assert state == ConversationState.INITIAL
    
    context = manager.get_context("nonexistent")
    assert context is None


def test_invalid_conversation_operations():
    """Test error handling for invalid operations."""
    manager = ConversationManager()
    
    with pytest.raises(ValueError):
        manager.add_message("nonexistent", "user", "Hello")
    
    with pytest.raises(ValueError):
        manager.set_state("nonexistent", ConversationState.PROVIDER_MATCHED)
    
    with pytest.raises(ValueError):
        manager.update_context("nonexistent", "key", "value")
